//! 垂直指向性の条件比較(分割次数・ユニット間隔・開口高さ・反射円錐の形状)。
//! cargo test --release --test sweep -- --nocapture
use speaker360_sim::*;

const NF: usize = 100;
const NE: usize = 121; // -90..90 deg, 1.5 deg step
const FLO: f64 = 100.0;
const FHI: f64 = 12000.0;

#[derive(Clone)]
struct Cfg {
    order: f64,   // 1=LR2 2=LR4 3=LR6 4=LR8
    s34: f64,     // WAY3->4 spacing mm
    s45: f64,     // WAY4->5 spacing mm
    hscale: f64,  // reflector aperture scale
    spread: f64,  // curved-cone emission spread (deg)
    taper: f64,
    xo: [f64; 4],
}

fn base() -> Cfg {
    Cfg { order: 1.0, s34: 170.0, s45: 85.0, hscale: 1.0, spread: 0.0, taper: 0.0, xo: [60.0, 600.0, 4200.0, 13200.0] }
}

/// returns (worst deviation within +-30 deg, within +-15 deg, worst freq)
fn eval(c: &Cfg) -> (f64, f64, f64) {
    unsafe {
        let m = std::slice::from_raw_parts_mut(in_ptr(), 24);
        for i in 0..4 { m[20 + i] = c.xo[i]; }
        let v = std::slice::from_raw_parts_mut(v2_in_ptr(), 44);
        let z3 = 850.0;
        let z = [260.0, 606.0, z3, z3 + c.s34, z3 + c.s34 + c.s45];
        let h = [30.0, 18.0, 33.0 * c.hscale, 22.5 * c.hscale, 15.5 * c.hscale];
        for w in 0..5 {
            v[w * 8] = z[w] / 1000.0;
            v[w * 8 + 1] = h[w] / 1000.0;
            v[w * 8 + 2] = 0.0;
            v[w * 8 + 3] = 0.0;
            v[w * 8 + 4] = if w >= 2 { c.spread } else { 0.0 };
            v[w * 8 + 5] = if w >= 2 { c.taper } else { 0.0 };
        }
        v[40] = c.order;
        v[41] = 9.0;
        let n = vertical2(5, NF, NE, FLO, FHI);
        let d = std::slice::from_raw_parts(v2_out_ptr(), n);
        // 評価: 仰角±30°(41点)の P90-P10 幅(狭いノッチに引きずられない)。w15は±15°
        let (mut w30, mut w15, mut wf) = (0.0f64, 0.0f64, 0.0f64);
        let pc = |v: &mut Vec<f64>| -> f64 {
            v.sort_by(|a, b| a.partial_cmp(b).unwrap());
            let n = v.len();
            v[(n as f64 * 0.9) as usize % n] - v[(n as f64 * 0.1) as usize]
        };
        for f in 0..NF {
            let (mut s30, mut s15) = (Vec::new(), Vec::new());
            for e in 0..NE {
                let el = -90.0 + 1.5 * e as f64;
                let val = d[f * NE + e];
                if el.abs() <= 30.0 { s30.push(val); }
                if el.abs() <= 15.0 { s15.push(val); }
            }
            let fr = FLO * (FHI / FLO).powf(f as f64 / (NF - 1) as f64);
            let a = pc(&mut s30);
            if a > w30 { w30 = a; wf = fr; }
            w15 = w15.max(pc(&mut s15));
        }
        (w30, w15, wf)
    }
}

/// random coordinate search over crossover frequencies
fn optimise(mut c: Cfg, iters: usize, seed: u64) -> (Cfg, (f64, f64, f64)) {
    let mut rng = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
    let mut next = || { rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407); ((rng >> 33) as f64) / ((1u64 << 31) as f64) };
    let ratio = if c.order <= 1.0 { 3.0 } else { 2.0 };
    let mut best = eval(&c);
    for _ in 0..iters {
        let mut x = c.xo;
        let k = (next() * 4.0) as usize % 4;
        x[k] *= ((next() - 0.5) * 0.5).exp();
        if x[0] < 40.0 || x[3] > 20000.0 { continue; }
        if (1..4).any(|i| x[i] < x[i - 1] * ratio) { continue; }
        let mut t = c.clone();
        t.xo = x;
        let r = eval(&t);
        if r.0 < best.0 { best = r; c = t; }
    }
    (c, best)
}

fn line(tag: &str, c: &Cfg, r: (f64, f64, f64)) {
    println!("{tag:<34} P90-P10(±30°)={:5.1}dB  ±15°={:5.1}dB  @{:5.0}Hz  xo=[{:.0},{:.0},{:.0},{:.0}]", r.0, r.1, r.2, c.xo[0], c.xo[1], c.xo[2], c.xo[3]);
}

#[test]
fn sweep() {
    println!("== 0. baseline (LR2 passive, as drawn)");
    let b = base();
    line("baseline LR2", &b, eval(&b));
    println!("== 1. 分割次数 (xo optimised)");
    for (m, nm) in [(1.0, "LR2 12dB"), (2.0, "LR4 24dB"), (3.0, "LR6 36dB"), (4.0, "LR8 48dB")] {
        let mut c = base(); c.order = m;
        let (c, r) = optimise(c, 400, 1);
        line(nm, &c, r);
    }
    println!("== 2. WAY3-5間隔の縮小 (LR4, xo optimised)");
    for s in [1.0, 0.7, 0.5] {
        let mut c = base(); c.order = 2.0; c.s34 *= s; c.s45 *= s;
        let (c, r) = optimise(c, 400, 2);
        line(&format!("spacing x{s}"), &c, r);
    }
    println!("== 3. 反射円錐の開口高さ(円錐半径に比例) (LR4)");
    for hs in [0.5, 1.0, 2.0, 3.0] {
        let mut c = base(); c.order = 2.0; c.hscale = hs;
        let (c, r) = optimise(c, 400, 3);
        line(&format!("aperture x{hs}"), &c, r);
    }
    println!("== 4. 曲面円錐(放射角の広がり)と開口の重み (LR4)");
    for (sp, tp, nm) in [(0.0, 0.0, "直線円錐"), (20.0, 0.0, "凸(拡散)±20°"), (40.0, 0.0, "凸(拡散)±40°"), (-20.0, 0.0, "凹(収束)±20°"), (0.0, 1.0, "直線+周辺漸減(Hann)"), (20.0, 1.0, "凸±20°+Hann")] {
        let mut c = base(); c.order = 2.0; c.spread = sp; c.taper = tp;
        let (c, r) = optimise(c, 400, 4);
        line(nm, &c, r);
    }
    println!("== 5. 組合せ(LR4/LR6, 間隔x0.6, 開口x2, 凸±20°+Hann)");
    for (m, nm) in [(2.0, "LR4"), (3.0, "LR6")] {
        let mut c = base(); c.order = m; c.s34 *= 0.6; c.s45 *= 0.6; c.hscale = 2.0; c.spread = 20.0; c.taper = 1.0;
        let (c, r) = optimise(c, 1200, 5);
        line(&format!("combo {nm}"), &c, r);
    }
}
