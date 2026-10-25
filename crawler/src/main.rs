//! 毎朝実行して、スピーカー振動板の新素材の候補(論文・記事)を集める。
//! 出典: arXiv API / Crossref API(いずれも公開API・キー不要)。
//! 取り込み方針: 候補は「未検証」として data/materials-candidates.json に溜めるだけ。
//! 本文(要旨)から ヤング率[GPa]・密度 が機械的に読めたものだけ、画面で「試算に使う」ボタンが出る。
//! 自動で既存の材質表(web/materials.json)は書き換えない(誤抽出で設計が汚れるのを防ぐ)。

use serde::{Deserialize, Serialize};
use std::io::Read;

const MAX_BODY: u64 = 2_000_000;
const KEEP: usize = 300;
const UA: &str = "360-speaker-materials-crawler (https://github.com/aon-co-jp/360-speaker)";

const QUERIES: &[&str] = &[
    "cellulose nanofiber loudspeaker diaphragm",
    "beryllium diaphragm tweeter",
    "carbon fiber composite loudspeaker diaphragm",
    "lightweight high stiffness diaphragm acoustic transducer",
    "graphene diaphragm loudspeaker",
    "titanium diaphragm super tweeter",
    "diamond coated diaphragm loudspeaker",
    "boron nitride speaker diaphragm",
    "bio-based composite speaker cone",
    "hybrid laminate dome tweeter diaphragm",
];

#[derive(Serialize, Deserialize, Clone, Debug)]
struct Item {
    id: String,
    title: String,
    url: String,
    source: String,
    published: String,
    first_seen: String,
    query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(rename = "E")]
    e: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    rho: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    snippet: Option<String>,
}

#[derive(Serialize, Deserialize, Default)]
struct Store {
    updated: String,
    items: Vec<Item>,
}

fn get(url: &str) -> Result<String, String> {
    let resp = ureq::get(url).set("User-Agent", UA).timeout(std::time::Duration::from_secs(30)).call().map_err(|e| e.to_string())?;
    let mut s = String::new();
    resp.into_reader().take(MAX_BODY).read_to_string(&mut s).map_err(|e| e.to_string())?;
    Ok(s)
}

fn enc(q: &str) -> String {
    q.bytes().map(|b| if b.is_ascii_alphanumeric() { (b as char).to_string() } else { format!("%{:02X}", b) }).collect()
}

/// `<tag>...</tag>` の最初の中身
fn tag<'a>(s: &'a str, name: &str) -> Option<&'a str> {
    let a = s.find(&format!("<{name}"))?;
    let a = a + s[a..].find('>')? + 1;
    let b = a + s[a..].find(&format!("</{name}>"))?;
    Some(s[a..b].trim())
}

fn strip_tags(s: &str) -> String {
    let mut out = String::new();
    let mut inside = false;
    for c in s.chars() {
        match c {
            '<' => inside = true,
            '>' => inside = false,
            _ if !inside => out.push(c),
            _ => {}
        }
    }
    out.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// 直前にある数値(例 "70 GPa" の 70)
fn number_before(s: &str, end: usize) -> Option<f64> {
    let head = s[..end].trim_end();
    let start = head.rfind(|c: char| !(c.is_ascii_digit() || c == '.' || c == '-')).map(|i| i + 1).unwrap_or(0);
    head[start..].parse::<f64>().ok().filter(|v| v.is_finite() && *v > 0.0)
}

fn floor_boundary(s: &str, mut i: usize) -> usize {
    while i > 0 && !s.is_char_boundary(i) { i -= 1; }
    i
}

/// 要旨から (E[GPa], rho[kg/m3]) を機械的に抽出。見つからなければ None。
fn extract(text: &str) -> (Option<f64>, Option<f64>) {
    let low = text.to_lowercase();
    let mut e = None;
    for (i, _) in low.match_indices("gpa") {
        let w0 = floor_boundary(&low, i.saturating_sub(80));
        if low[w0..i].contains("modulus") {
            if let Some(v) = number_before(&low, i) {
                if (0.1..2000.0).contains(&v) {
                    e = Some(v);
                    break;
                }
            }
        }
    }
    let mut rho = None;
    for unit in ["g/cm", "kg/m"] {
        for (i, _) in low.match_indices(unit) {
            let w0 = floor_boundary(&low, i.saturating_sub(80));
            if low[w0..i].contains("density") {
                if let Some(v) = number_before(&low, i) {
                    let r = if unit == "g/cm" { v * 1000.0 } else { v };
                    if (100.0..25000.0).contains(&r) {
                        rho = Some(r);
                        break;
                    }
                }
            }
        }
        if rho.is_some() { break; }
    }
    (e, rho)
}

/// 無関係な結果(日付順の検索で紛れ込む)を落とすための語句と、未来日付の除外
fn relevant(title: &str, body: &str, published: &str, now: &str) -> bool {
    let t = format!("{} {}", title, body).to_lowercase();
    let audio = ["loudspeaker", "tweeter", "woofer", "speaker cone", "speaker diaphragm", "voice coil", "electroacoustic", "acoustic transducer", "audio transducer", "headphone", "micro-speaker", "microspeaker"];
    let material = ["diaphragm", "cone", "dome", "membrane", "composite", "fiber", "fibre", "nanofiber", "laminate", "stiffness"];
    let topical = audio.iter().any(|w| t.contains(w)) && material.iter().any(|w| t.contains(w));
    let y_now: i64 = now.get(..4).and_then(|x| x.parse().ok()).unwrap_or(0);
    let y_pub: i64 = published.get(..4).and_then(|x| x.parse().ok()).unwrap_or(0);
    topical && y_pub <= y_now
}

fn today() -> String {
    // 依存なしのUTC日付(unix秒→年月日)
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

fn arxiv(q: &str, now: &str, out: &mut Vec<Item>) {
    let url = format!("http://export.arxiv.org/api/query?search_query=all:{}&sortBy=submittedDate&sortOrder=descending&max_results=8", enc(&format!("\"{q}\"")));
    match get(&url) {
        Ok(body) => {
            for ent in body.split("<entry>").skip(1) {
                let (Some(id), Some(title)) = (tag(ent, "id"), tag(ent, "title")) else { continue };
                let summary = tag(ent, "summary").map(strip_tags).unwrap_or_default();
                let (e, rho) = extract(&summary);
                let published: String = tag(ent, "published").unwrap_or("").chars().take(10).collect();
                if !relevant(title, &summary, &published, now) { continue; }
                out.push(Item {
                    id: format!("arxiv:{}", id.rsplit('/').next().unwrap_or(id)),
                    title: strip_tags(title),
                    url: id.to_string(),
                    source: "arXiv".into(),
                    published,
                    first_seen: now.into(),
                    query: q.into(),
                    e,
                    rho,
                    snippet: (e.is_some() || rho.is_some()).then(|| summary.chars().take(240).collect()),
                });
            }
        }
        Err(err) => eprintln!("arXiv {q}: {err}"),
    }
}

fn crossref(q: &str, now: &str, out: &mut Vec<Item>) {
    let url = format!("https://api.crossref.org/works?query.bibliographic={}&rows=15&filter=from-pub-date:2023-01-01&select=DOI,title,abstract,issued,URL", enc(q));
    match get(&url) {
        Ok(body) => {
            let Ok(v) = serde_json::from_str::<serde_json::Value>(&body) else { return };
            let Some(items) = v["message"]["items"].as_array() else { return };
            for it in items {
                let (Some(doi), Some(title)) = (it["DOI"].as_str(), it["title"][0].as_str()) else { continue };
                let abs = it["abstract"].as_str().map(strip_tags).unwrap_or_default();
                let (e, rho) = extract(&abs);
                let date = it["issued"]["date-parts"][0]
                    .as_array()
                    .map(|a| a.iter().filter_map(|x| x.as_i64()).map(|x| x.to_string()).collect::<Vec<_>>().join("-"))
                    .unwrap_or_default();
                if !relevant(title, &abs, &date, now) { continue; }
                out.push(Item {
                    id: format!("doi:{doi}"),
                    title: strip_tags(title),
                    url: it["URL"].as_str().map(String::from).unwrap_or_else(|| format!("https://doi.org/{doi}")),
                    source: "Crossref".into(),
                    published: date,
                    first_seen: now.into(),
                    query: q.into(),
                    e,
                    rho,
                    snippet: (e.is_some() || rho.is_some()).then(|| abs.chars().take(240).collect()),
                });
            }
        }
        Err(err) => eprintln!("Crossref {q}: {err}"),
    }
}

fn main() {
    let out_path = std::env::args().nth(1).unwrap_or_else(|| "data/materials-candidates.json".into());
    let now = today();
    let mut store: Store = std::fs::read(&out_path).ok().and_then(|b| serde_json::from_slice(&b).ok()).unwrap_or_default();
    let mut found = Vec::new();
    for q in QUERIES {
        arxiv(q, &now, &mut found);
        std::thread::sleep(std::time::Duration::from_secs(3)); // APIへの配慮
        crossref(q, &now, &mut found);
        std::thread::sleep(std::time::Duration::from_secs(1));
    }
    let mut added = 0;
    for it in found {
        if !store.items.iter().any(|x| x.id == it.id) {
            store.items.insert(0, it);
            added += 1;
        }
    }
    store.items.truncate(KEEP);
    store.updated = now;
    if let Some(dir) = std::path::Path::new(&out_path).parent() { let _ = std::fs::create_dir_all(dir); }
    std::fs::write(&out_path, serde_json::to_vec_pretty(&store).unwrap()).expect("write output");
    println!("materials-crawler: +{added} new, {} total -> {out_path}", store.items.len());
}
