//! 同軸化・4WAY化の比較(ユニット中心を揃える構成)。
//! cargo test --release --test coax -- --nocapture
use speaker360_sim::*;

const NF: usize = 100;
const NE: usize = 121; // -90..90 deg, 1.5 deg step
const FLO: f64 = 100.0;
const FHI: f64 = 12000.0;

#[derive(Clone)]
struct Way { z: f64, h: f64 } // mm

/// P90-P10 within +-30deg, worst over 100Hz..12kHz  (order: 1=LR2 2=LR4)
fn eval(ways: &[Way], xo: &[f64], order: f64) -> (f64, f64) {
    unsafe {
        let m = std::slice::from_raw_parts_mut(in_ptr(), 24);
        for i in 0..4 { m[20 + i] = if i < xo.len() { xo[i] } else { 1e5 }; }
        let v = std::slice::from_raw_parts_mut(v2_in_ptr(), 44);
        for (w, a) in ways.iter().enumerate() {
            v[w * 8] = a.z / 1000.0; v[w * 8 + 1] = a.h / 1000.0;
            v[w * 8 + 2] = 0.0; v[w * 8 + 3] = 0.0; v[w * 8 + 4] = 0.0; v[w * 8 + 5] = 0.0;
        }
        v[40] = order; v[41] = 9.0;
        let n = vertical2(ways.len(), NF, NE, FLO, FHI);
        let d = std::slice::from_raw_parts(v2_out_ptr(), n);
        let (mut worst, mut wf) = (0.0f64, 0.0f64);
        for f in 0..NF {
            let mut s: Vec<f64> = (0..NE).filter(|e| (-90.0 + 1.5 * *e as f64).abs() <= 30.0).map(|e| d[f * NE + e]).collect();
            s.sort_by(|a, b| a.partial_cmp(b).unwrap());
            let len = s.len();
            let dev = s[(len as f64 * 0.9) as usize % len] - s[(len as f64 * 0.1) as usize];
            let fr = FLO * (FHI / FLO).powf(f as f64 / (NF - 1) as f64);
            if dev > worst { worst = dev; wf = fr; }
        }
        (worst, wf)
    }
}

fn optimise(ways: &[Way], mut xo: Vec<f64>, order: f64, iters: usize, seed: u64) -> (Vec<f64>, (f64, f64)) {
    let mut rng = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
    let mut next = || { rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407); ((rng >> 33) as f64) / ((1u64 << 31) as f64) };
    let mut best = eval(ways, &xo, order);
    for _ in 0..iters {
        let mut x = xo.clone();
        let k = (next() * x.len() as f64) as usize % x.len();
        x[k] *= ((next() - 0.5) * 0.5).exp();
        if x[0] < 40.0 || *x.last().unwrap() > 20000.0 { continue; }
        if (1..x.len()).any(|i| x[i] < x[i - 1] * 2.0) { continue; }
        let r = eval(ways, &x, order);
        if r.0 < best.0 { best = r; xo = x; }
    }
    (xo, best)
}

fn show(tag: &str, ways: &[Way], xo0: Vec<f64>) {
    let (xo, r) = optimise(ways, xo0, 2.0, 400, 7);
    let zs: Vec<String> = ways.iter().map(|w| format!("{:.0}", w.z)).collect();
    println!("{tag:<38} P90-P10(±30°)={:5.1}dB @{:5.0}Hz  z=[{}] xo={:?}", r.0, r.1, zs.join(","), xo.iter().map(|x| x.round() as i64).collect::<Vec<_>>());
}

#[test]
fn coax() {
    let s1 = Way { z: 260.0, h: 30.0 };
    let s2 = Way { z: 606.0, h: 18.0 };
    let mid = |z: f64| Way { z, h: 33.0 };
    let tw = |z: f64| Way { z, h: 22.5 };
    let sup = |z: f64| Way { z, h: 15.5 };
    println!("== 5WAY(WAY3-5の配置を変える, LR4)");
    show("5WAY 基準(間隔170/85)", &[s1.clone(), s2.clone(), mid(850.0), tw(1020.0), sup(1105.0)], vec![150.0, 580.0, 4400.0, 14500.0]);
    show("5WAY 中音+高音を同軸(間隔0/85)", &[s1.clone(), s2.clone(), mid(850.0), tw(850.0), sup(935.0)], vec![150.0, 580.0, 4400.0, 14500.0]);
    show("5WAY 高音+超高音を同軸(170/0)", &[s1.clone(), s2.clone(), mid(850.0), tw(1020.0), sup(1020.0)], vec![150.0, 580.0, 4400.0, 14500.0]);
    show("5WAY 3つとも同軸(0/0)", &[s1.clone(), s2.clone(), mid(850.0), tw(850.0), sup(850.0)], vec![150.0, 580.0, 4400.0, 14500.0]);
    println!("== 4WAY(高音ユニットを廃止し、中音を広帯域化)");
    show("4WAY 中音+超高音(間隔255)", &[s1.clone(), s2.clone(), mid(850.0), sup(1105.0)], vec![150.0, 580.0, 6000.0]);
    show("4WAY 中音+超高音(間隔130に近接)", &[s1.clone(), s2.clone(), mid(850.0), sup(980.0)], vec![150.0, 580.0, 6000.0]);
    show("4WAY 中音+超高音を同軸(間隔0)", &[s1.clone(), s2.clone(), mid(850.0), sup(850.0)], vec![150.0, 580.0, 6000.0]);
    println!("== 3WAY(上は広帯域1本+同軸超高音)");
    show("3WAY 低音+同軸(中+超高音)", &[s1.clone(), mid(850.0), sup(850.0)], vec![150.0, 4000.0]);
    println!("== 下側の分割(WAY1-2-3)の影響: 低音と中音の間隔");
    show("5WAY 低音を中音に近接(間隔120)", &[s1.clone(), Way { z: 730.0, h: 18.0 }, mid(850.0), tw(1020.0), sup(1105.0)], vec![150.0, 580.0, 4400.0, 14500.0]);
}
