//! 毎朝実行: ユニットの通販サイトを、柔軟に確認して「確認できたものだけ」記録する。
//!
//! 柔軟さの仕組み:
//!  1. 検索URLの自動発見: トップページの検索フォーム(action/入力名)と、よくある形(?q= など)を総当たりし、
//!     「実在の語では結果が増え、でたらめな語では増えない」ものだけを有効な検索URLとして data/shops-learned.json に記憶する。
//!     翌日に動かなくなっていたら、自動で見つけ直す(自動修正)。
//!  2. JavaScript描画のサイト: 通常取得でリンクが少なければ、ヘッドレスChromium(--dump-dom)で描画してから判定する。
//!  3. 誤検出対策: メニューに常に並ぶブランド名を数えないよう、「ブランド検索の結果」と「でたらめ語の結果」の差
//!     (ブランド名を含む商品リンクの増え方)で判定する。
//!  4. open-cuda(aruaru-llm の /v1/rerank、BERT文埋め込み)で、ページの文面が「スピーカーユニット販売」に近いかを採点し、補助判定にする。
//!  5. 結果から README の自動更新ブロックを書き換え、SHOPS_GIT_PUSH=1 なら commit・push する。
//! 使い方: shops <seed.json> <out.json> [repo_root]

use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::io::Read;
use std::process::{Command, Stdio};

const UA: &str = "360-speaker-shops-crawler (https://github.com/aon-co-jp/360-speaker)";
const MAX_BODY: u64 = 2_500_000;
const CONTROL: &str = "zqxvkjw";
const GENERIC: &[&str] = &[
    "/search?q={q}", "/?s={q}", "/?q={q}", "/search?keyword={q}", "/?keyword={q}", "/?word={q}", "/search.php?q={q}",
    "/catalogsearch/result/?q={q}", "/search?type=product&q={q}", "/view/search?search%5Bkeyword%5D={q}", "/shop/shopsearch.aspx?q={q}",
    "/?searchTerm={q}", "/search/?q={q}", "/index.php?route=product/search&search={q}", "/?s={q}&post_type=product", "/products/search?q={q}",
];

#[derive(Deserialize)]
struct Seed {
    brands: Vec<String>,
    shops: Vec<Shop>,
}
#[derive(Deserialize, Clone)]
struct Shop {
    name: String,
    region: String,
    url: String,
    #[serde(default)]
    search: String,
}
#[derive(Serialize, Deserialize, Clone, Default)]
struct Learned {
    pattern: String,
    browser: bool,
    verified: String,
}
#[derive(Serialize, Deserialize, Default)]
struct Out {
    updated: String,
    shops: Vec<ShopOut>,
}
#[derive(Serialize, Deserialize)]
struct ShopOut {
    name: String,
    region: String,
    url: String,
    status: String,
    pattern: String,
    browser: bool,
    brands: BTreeMap<String, Evidence>,
}
#[derive(Serialize, Deserialize)]
struct Evidence {
    checked: String,
    url: String,
    links: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    ai_score: Option<f64>,
}

fn enc(q: &str) -> String {
    q.bytes().map(|b| if b.is_ascii_alphanumeric() || b == b'-' { (b as char).to_string() } else { format!("%{:02X}", b) }).collect()
}

fn browser_path() -> Option<String> {
    for p in [std::env::var("SHOPS_BROWSER").unwrap_or_default(), "/usr/bin/chromium-browser".into(), "/usr/bin/chromium".into(),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe".into(), r"C:\Program Files\Google\Chrome\Application\chrome.exe".into()] {
        if !p.is_empty() && std::path::Path::new(&p).exists() { return Some(p); }
    }
    None
}

fn fetch_http(url: &str) -> Option<String> {
    let resp = ureq::get(url).set("User-Agent", UA).timeout(std::time::Duration::from_secs(25)).call().ok()?;
    let mut s = String::new();
    resp.into_reader().take(MAX_BODY).read_to_string(&mut s).ok()?;
    Some(s)
}

fn fetch_browser(url: &str) -> Option<String> {
    let b = browser_path()?;
    let tmp = std::env::temp_dir().join(format!("shops-profile-{}", std::process::id()));
    let args = ["--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--hide-scrollbars", "--virtual-time-budget=9000", "--dump-dom"];
    let mut cmd = if cfg!(unix) { let mut c = Command::new("timeout"); c.arg("60").arg(&b); c } else { Command::new(&b) };
    cmd.args(args).arg(format!("--user-data-dir={}", tmp.display())).arg(format!("--user-agent={UA}")).arg(url).stdout(Stdio::piped()).stderr(Stdio::null());
    let out = cmd.output().ok()?;
    let _ = std::fs::remove_dir_all(&tmp);
    let s = String::from_utf8_lossy(&out.stdout).to_string();
    (s.len() > 500).then_some(s)
}

fn get(url: &str, browser: bool) -> Option<String> { if browser { fetch_browser(url) } else { fetch_http(url) } }

/// (href, 表示テキスト)
fn anchors(html: &str) -> Vec<(String, String)> {
    let mut v = Vec::new();
    let low = html.to_lowercase();
    let mut i = 0;
    while let Some(p) = low[i..].find("<a ") {
        let s = i + p;
        let Some(e) = low[s..].find("</a>") else { break };
        let seg = &html[s..s + e];
        let href = seg.split("href=").nth(1).and_then(|r| {
            let q = r.chars().next()?;
            if q == '"' || q == '\'' { r[1..].split(q).next().map(String::from) } else { r.split(|c: char| c.is_whitespace() || c == '>').next().map(String::from) }
        });
        let text = {
            let mut t = String::new();
            let mut inside = false;
            for c in seg.chars() { match c { '<' => inside = true, '>' if inside => inside = false, _ if !inside => t.push(c), _ => {} } }
            t.split_whitespace().collect::<Vec<_>>().join(" ")
        };
        if let Some(h) = href { v.push((h, text)); }
        i = s + e + 4;
    }
    v
}

fn distinct_hrefs(a: &[(String, String)]) -> usize { a.iter().map(|x| x.0.as_str()).collect::<BTreeSet<_>>().len() }

/// ブランド名を含む「別々の商品リンク」の数
fn brand_links(a: &[(String, String)], brand: &str) -> usize {
    let b = brand.to_lowercase();
    a.iter().filter(|(h, t)| h.to_lowercase().contains(&b) || t.to_lowercase().contains(&b)).map(|x| x.0.as_str()).collect::<BTreeSet<_>>().len()
}

fn join_url(base: &str, rel: &str) -> String {
    if rel.starts_with("http") { return rel.to_string(); }
    let origin = base.splitn(4, '/').take(3).collect::<Vec<_>>().join("/");
    if rel.starts_with('/') { format!("{origin}{rel}") } else { format!("{}/{}", base.trim_end_matches('/'), rel) }
}

/// トップページの検索フォームから候補パターンを作る
fn form_patterns(html: &str, base: &str) -> Vec<String> {
    let mut out = Vec::new();
    let low = html.to_lowercase();
    let mut i = 0;
    while let Some(p) = low[i..].find("<form") {
        let s = i + p;
        let e = low[s..].find("</form>").map(|x| s + x).unwrap_or(low.len());
        let form = &html[s..e];
        let fl = form.to_lowercase();
        let action = fl.find("action=").and_then(|a| { let r = &form[a + 7..]; let q = r.chars().next()?; if q == '"' || q == '\'' { r[1..].split(q).next().map(String::from) } else { None } }).unwrap_or_default();
        for inp in fl.split("<input").skip(1) {
            let tag = inp.split('>').next().unwrap_or("");
            let name = tag.split("name=").nth(1).and_then(|r| { let q = r.chars().next()?; r[1..].split(q).next().map(String::from) });
            let is_search = tag.contains("type=\"search\"") || tag.contains("type='search'") || tag.contains("type=\"text\"");
            if let (Some(n), true) = (name, is_search) {
                if ["q", "s", "keyword", "word", "searchterm", "query", "search", "k", "kw", "freeword"].contains(&n.as_str()) {
                    let target = if action.is_empty() { base.to_string() } else { join_url(base, &action) };
                    out.push(format!("{target}{}{n}={{q}}", if target.contains('?') { "&" } else { "?" }));
                }
            }
        }
        i = e;
    }
    out
}

fn ai_score(text: &str) -> Option<f64> {
    // open-cuda(BERT文埋め込み, CPU)を載せた aruaru-llm の /v1/rerank で「ユニット販売ページらしさ」を採点
    let base = std::env::var("ARUARU_LLM_URL").unwrap_or_else(|_| "http://127.0.0.1:4600".into());
    let snippet: String = text.chars().take(600).collect();
    let body = serde_json::json!({"query": "スピーカーユニット(ウーファー・ツィーター)を販売する通販ページ", "documents": [snippet]});
    let resp = ureq::post(&format!("{base}/v1/rerank")).timeout(std::time::Duration::from_secs(20)).send_json(body).ok()?;
    let v: serde_json::Value = resp.into_json().ok()?;
    v["scores"][0].as_f64()
}

fn visible_text(html: &str) -> String {
    let mut t = String::new();
    let mut inside = false;
    for c in html.chars() { match c { '<' => inside = true, '>' => inside = false, _ if !inside => t.push(c), _ => {} } }
    t.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// 検索が機能しているか: 実在の語で結果リンクが増え、でたらめ語とは別ページになる
fn search_works(pattern: &str, browser: bool) -> Option<(Vec<(String, String)>, Vec<(String, String)>)> {
    let c = get(&pattern.replace("{q}", CONTROL), browser)?;
    let s = get(&pattern.replace("{q}", "speaker"), browser)?;
    let (ac, as_) = (anchors(&c), anchors(&s));
    (c != s && distinct_hrefs(&as_) >= distinct_hrefs(&ac) + 3).then_some((ac, as_))
}

fn today() -> String {
    let secs = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0) as i64;
    let (mut y, mut d) = (1970i64, secs / 86400);
    loop {
        let len = if (y % 4 == 0 && y % 100 != 0) || y % 400 == 0 { 366 } else { 365 };
        if d < len { break; }
        d -= len;
        y += 1;
    }
    let leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
    let ml = [31, if leap { 29 } else { 28 }, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let mut m = 0;
    while d >= ml[m] { d -= ml[m]; m += 1; }
    format!("{y:04}-{:02}-{:02}", m + 1, d + 1)
}

fn find_pattern(shop: &Shop, learned: &mut BTreeMap<String, Learned>, now: &str) -> Option<(String, bool)> {
    // 1) 記憶済み → 2) 既定 → 3) フォーム発見 → 4) よくある形。HTTPで駄目ならブラウザ描画で再試行(自動修正)
    let mut cands: Vec<String> = Vec::new();
    if let Some(l) = learned.get(&shop.url) { cands.push(l.pattern.clone()); }
    if !shop.search.is_empty() { cands.push(shop.search.clone()); }
    if let Some(home) = fetch_http(&shop.url) { cands.extend(form_patterns(&home, &shop.url)); }
    for g in GENERIC { cands.push(join_url(&shop.url, g)); }
    let mut seen = BTreeSet::new();
    cands.retain(|c| seen.insert(c.clone()));
    for browser in [false, true] {
        if browser && browser_path().is_none() { break; }
        for p in &cands {
            if search_works(p, browser).is_some() {
                learned.insert(shop.url.clone(), Learned { pattern: p.clone(), browser, verified: now.into() });
                return Some((p.clone(), browser));
            }
            std::thread::sleep(std::time::Duration::from_millis(700));
        }
    }
    None
}

fn update_readme(root: &str, out: &Out) -> bool {
    let path = format!("{root}/README.md");
    let Ok(text) = std::fs::read_to_string(&path) else { return false };
    let (a, b) = ("<!-- SHOPS:START -->", "<!-- SHOPS:END -->");
    let mut md = format!("{a}\n**毎朝の自動確認(最終 {}、サイト内検索で確認できたものだけ・自動更新)**\n\n| サイト | 確認できたブランド |\n|---|---|\n", out.updated);
    let mut any = false;
    for s in out.shops.iter().filter(|s| !s.brands.is_empty()) {
        any = true;
        let links = s.brands.iter().map(|(n, e)| format!("[{n}]({})", e.url)).collect::<Vec<_>>().join(" ・ ");
        md.push_str(&format!("| [{}]({}) ({}) | {} |\n", s.name, s.url, s.region, links));
    }
    if !any { md.push_str("| (確認できたものはまだありません) | |\n"); }
    let nf: Vec<_> = out.shops.iter().filter(|s| s.brands.is_empty()).map(|s| format!("{}({})", s.name, s.status)).collect();
    if !nf.is_empty() { md.push_str(&format!("\n確認できなかったサイト: {}\n", nf.join("、"))); }
    md.push_str(&format!("{b}"));
    let new = match (text.find(a), text.find(b)) {
        (Some(i), Some(j)) if j > i => format!("{}{}{}", &text[..i], md, &text[j + b.len()..]),
        _ => format!("{text}\n{md}\n"),
    };
    if new == text { return false; }
    std::fs::write(&path, new).is_ok()
}

fn git_push(root: &str) {
    let run = |args: &[&str]| Command::new("git").arg("-C").arg(root).args(args).output().map(|o| o.status.success()).unwrap_or(false);
    if !run(&["add", "README.md"]) { return; }
    if run(&["diff", "--cached", "--quiet"]) { return; } // 変更なし
    if run(&["commit", "-q", "-m", "chore: 毎朝の通販サイト自動確認を更新(自動)"]) {
        let _ = run(&["pull", "-q", "--rebase"]);
        if !run(&["push", "-q"]) { eprintln!("git push に失敗(認証・衝突を確認してください)"); }
    }
}

fn main() {
    let mut args = std::env::args().skip(1);
    let seed_path = args.next().unwrap_or_else(|| "shops-seed.json".into());
    let out_path = args.next().unwrap_or_else(|| "data/shops-confirmed.json".into());
    let repo = args.next();
    let seed: Seed = serde_json::from_slice(&std::fs::read(&seed_path).expect("read seed")).expect("parse seed");
    let learned_path = std::path::Path::new(&out_path).with_file_name("shops-learned.json");
    let mut learned: BTreeMap<String, Learned> = std::fs::read(&learned_path).ok().and_then(|b| serde_json::from_slice(&b).ok()).unwrap_or_default();
    let now = today();
    let mut out = Out { updated: now.clone(), shops: Vec::new() };
    eprintln!("browser: {:?}", browser_path());
    for shop in &seed.shops {
        let mut so = ShopOut { name: shop.name.clone(), region: shop.region.clone(), url: shop.url.clone(), status: String::new(), pattern: String::new(), browser: false, brands: BTreeMap::new() };
        match find_pattern(shop, &mut learned, &now) {
            None => so.status = if fetch_http(&shop.url).is_none() { "接続できない".into() } else { "検索の仕組みを自動で見つけられない".into() },
            Some((pattern, browser)) => {
                so.status = "検索を確認".into();
                so.pattern = pattern.clone();
                so.browser = browser;
                let control = get(&pattern.replace("{q}", CONTROL), browser).unwrap_or_default();
                let ctl = anchors(&control);
                for brand in &seed.brands {
                    let url = pattern.replace("{q}", &enc(brand));
                    if let Some(body) = get(&url, browser) {
                        let a = anchors(&body);
                        let (n, base) = (brand_links(&a, brand), brand_links(&ctl, brand));
                        if n >= base + 3 {
                            let score = ai_score(&visible_text(&body));
                            // open-cuda(BERT)の採点が取れた場合は、極端に低いものを除外する
                            if score.map(|s| s >= 0.5).unwrap_or(true) {
                                so.brands.insert(brand.clone(), Evidence { checked: now.clone(), url, links: n - base, ai_score: score });
                            }
                        }
                    }
                    std::thread::sleep(std::time::Duration::from_millis(1500));
                }
            }
        }
        eprintln!("{} [{}]: {} brand(s)", shop.name, so.status, so.brands.len());
        out.shops.push(so);
    }
    if let Some(dir) = std::path::Path::new(&out_path).parent() { let _ = std::fs::create_dir_all(dir); }
    std::fs::write(&out_path, serde_json::to_vec_pretty(&out).unwrap()).expect("write");
    std::fs::write(&learned_path, serde_json::to_vec_pretty(&learned).unwrap()).expect("write learned");
    if let Some(root) = repo {
        if update_readme(&root, &out) && std::env::var("SHOPS_GIT_PUSH").ok().as_deref() == Some("1") { git_push(&root); }
    }
    println!("shops-crawler: {} shops -> {out_path}", out.shops.len());
}
