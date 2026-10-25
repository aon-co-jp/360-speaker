//! 毎朝実行: ユニットの通販サイトを、サイト内検索にブランド名で問い合わせて確認する。
//! 「結果ページにブランド名とユニット関連語が出た」ものだけを確認済みとして
//! data/shops-confirmed.json に書く(確認できなかったものは載せない)。
//! 使い方: shops <seed.json> <out.json>

use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::io::Read;

const UA: &str = "360-speaker-shops-crawler (https://github.com/aon-co-jp/360-speaker)";
const MAX_BODY: u64 = 1_500_000;
const KEYWORDS: &[&str] = &["tweeter", "woofer", "driver", "speaker", "loudspeaker", "midrange", "ユニット", "スピーカー", "ツィーター", "ウーファー", "haut-parleur", "lautsprecher", "chassis"];

#[derive(Deserialize)]
struct Seed {
    brands: Vec<String>,
    shops: Vec<Shop>,
}
#[derive(Deserialize)]
struct Shop {
    name: String,
    region: String,
    url: String,
    search: String,
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
    brands: BTreeMap<String, Evidence>,
}
#[derive(Serialize, Deserialize)]
struct Evidence {
    checked: String,
    url: String,
}

fn enc(q: &str) -> String {
    q.bytes().map(|b| if b.is_ascii_alphanumeric() || b == b'-' { (b as char).to_string() } else { format!("%{:02X}", b) }).collect()
}

fn fetch(url: &str) -> Option<String> {
    let resp = ureq::get(url).set("User-Agent", UA).timeout(std::time::Duration::from_secs(25)).call().ok()?;
    let mut s = String::new();
    resp.into_reader().take(MAX_BODY).read_to_string(&mut s).ok()?;
    Some(s)
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

fn main() {
    let mut args = std::env::args().skip(1);
    let seed_path = args.next().unwrap_or_else(|| "shops-seed.json".into());
    let out_path = args.next().unwrap_or_else(|| "data/shops-confirmed.json".into());
    let seed: Seed = serde_json::from_slice(&std::fs::read(&seed_path).expect("read seed")).expect("parse seed");
    let now = today();
    let mut out = Out { updated: now.clone(), shops: Vec::new() };
    for shop in &seed.shops {
        let mut so = ShopOut { name: shop.name.clone(), region: shop.region.clone(), url: shop.url.clone(), brands: BTreeMap::new() };
        for brand in &seed.brands {
            let url = shop.search.replace("{q}", &enc(brand));
            if let Some(body) = fetch(&url) {
                let low = body.to_lowercase();
                // 検索語のエコー(数回)では通らないよう、ブランド名が12回以上出て、ユニット関連語も含む場合のみ確認済み
                let hits = low.matches(&brand.to_lowercase()).count();
                if hits >= 12 && KEYWORDS.iter().any(|k| low.contains(k)) {
                    so.brands.insert(brand.clone(), Evidence { checked: now.clone(), url });
                }
            }
            std::thread::sleep(std::time::Duration::from_secs(2));
        }
        eprintln!("{}: {} brand(s) confirmed", shop.name, so.brands.len());
        out.shops.push(so);
    }
    if let Some(dir) = std::path::Path::new(&out_path).parent() { let _ = std::fs::create_dir_all(dir); }
    std::fs::write(&out_path, serde_json::to_vec_pretty(&out).unwrap()).expect("write");
    println!("shops-crawler: {} shops -> {out_path}", out.shops.len());
}
