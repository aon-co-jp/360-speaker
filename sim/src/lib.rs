//! 360-speaker simulator core. Dependency-free, exported as raw WASM functions.
//!
//! Model (approximate, for design exploration, not a substitute for measurement):
//! - each WAY is a ring of `n` identical pistons on a cylinder of radius `ring_r`
//! - piston directivity 2*J1(x)/x, x = k*a*sin(alpha)
//! - baffle shadow: blends from omni (kR << 1) to a raised-cosine lobe (kR >> 1)
//! - crossovers: Linkwitz-Riley 4th order, complex summation (phase-correct)
//! - far field, horizontal plane only (vertical lobing is not modelled)

mod enclosure;

use std::f64::consts::PI;

pub const MAX_WAYS: usize = 5;
const CFG: usize = 4; // per way: ring_count, piston_radius_m, ring_radius_m, gain_db
const XO: usize = MAX_WAYS - 1;

static mut IN: [f64; MAX_WAYS * CFG + XO] = [0.0; MAX_WAYS * CFG + XO];
static mut OUT: Vec<f64> = Vec::new();

#[derive(Clone, Copy)]
struct C(f64, f64);
impl C {
    fn mul(self, o: C) -> C { C(self.0 * o.0 - self.1 * o.1, self.0 * o.1 + self.1 * o.0) }
    fn add(self, o: C) -> C { C(self.0 + o.0, self.1 + o.1) }
    fn div(self, o: C) -> C {
        let d = o.0 * o.0 + o.1 * o.1;
        C((self.0 * o.0 + self.1 * o.1) / d, (self.1 * o.0 - self.0 * o.1) / d)
    }
    fn scale(self, s: f64) -> C { C(self.0 * s, self.1 * s) }
    fn abs(self) -> f64 { self.0.hypot(self.1) }
}

/// Bessel J1 (Abramowitz & Stegun 9.4.4 / 9.4.6).
pub fn j1(x: f64) -> f64 {
    let ax = x.abs();
    let r = if ax < 8.0 {
        let y = x * x;
        let n = x * (72362614232.0 + y * (-7895059235.0 + y * (242396853.1 + y * (-2972611.439 + y * (15704.4826 + y * -30.16036606)))));
        let d = 144725228442.0 + y * (2300535178.0 + y * (18583304.74 + y * (99447.43394 + y * (376.9991397 + y))));
        n / d
    } else {
        let z = 8.0 / ax;
        let y = z * z;
        let xx = ax - 2.356194491;
        let p1 = 1.0 + y * (0.183105e-2 + y * (-0.3516396496e-4 + y * (0.2457520174e-5 + y * -0.240337019e-6)));
        let p2 = 0.04687499995 + y * (-0.2002690873e-3 + y * (0.8449199096e-5 + y * (-0.88228987e-6 + y * 0.105787412e-6)));
        let a = (0.636619772 / ax).sqrt() * (xx.cos() * p1 - z * xx.sin() * p2);
        if x < 0.0 { -a } else { a }
    };
    r
}

fn piston(x: f64) -> f64 { if x.abs() < 1e-6 { 1.0 } else { 2.0 * j1(x) / x } }

/// Butterworth 2nd-order LP at normalised s = j f/fc.
fn b2_lp(f: f64, fc: f64) -> C {
    let s = C(0.0, f / fc);
    let den = s.mul(s).add(s.scale(std::f64::consts::SQRT_2)).add(C(1.0, 0.0));
    C(1.0, 0.0).div(den)
}
fn b2_hp(f: f64, fc: f64) -> C {
    let s = C(0.0, f / fc);
    let s2 = s.mul(s);
    s2.div(s2.add(s.scale(std::f64::consts::SQRT_2)).add(C(1.0, 0.0)))
}
fn lr4_lp(f: f64, fc: f64) -> C { let b = b2_lp(f, fc); b.mul(b) }
fn lr4_hp(f: f64, fc: f64) -> C { let b = b2_hp(f, fc); b.mul(b) }

#[no_mangle]
pub extern "C" fn in_ptr() -> *mut f64 { std::ptr::addr_of_mut!(IN) as *mut f64 }
#[no_mangle]
pub extern "C" fn out_ptr() -> *const f64 { unsafe { (*std::ptr::addr_of!(OUT)).as_ptr() } }
#[no_mangle]
pub extern "C" fn max_ways() -> usize { MAX_WAYS }

/// Input layout: `[ring_count, piston_r, ring_r, gain_db] * MAX_WAYS` then `XO` crossover Hz.
/// Output: `n_freq * n_ang` dB values (re 1.0), freq-major, log spaced `f_lo..f_hi`, angle 0..360.
/// Returns number of f64 written.
#[no_mangle]
pub extern "C" fn compute(ways: usize, n_freq: usize, n_ang: usize, f_lo: f64, f_hi: f64) -> usize {
    let ways = ways.clamp(1, MAX_WAYS);
    let cfg = unsafe { *std::ptr::addr_of!(IN) };
    let out = unsafe { &mut *std::ptr::addr_of_mut!(OUT) };
    out.clear();
    out.reserve(n_freq * n_ang);
    let c0 = 343.0;
    for fi in 0..n_freq {
        let t = fi as f64 / (n_freq.max(2) - 1) as f64;
        let f = f_lo * (f_hi / f_lo).powf(t);
        let k = 2.0 * PI * f / c0;
        // band filter per way
        let mut band = [C(1.0, 0.0); MAX_WAYS];
        for w in 0..ways {
            let mut h = C(1.0, 0.0);
            if w > 0 { h = h.mul(lr4_hp(f, cfg[MAX_WAYS * CFG + w - 1])); }
            if w + 1 < ways { h = h.mul(lr4_lp(f, cfg[MAX_WAYS * CFG + w])); }
            band[w] = h.scale(10f64.powf(cfg[w * CFG + 3] / 20.0));
        }
        for ai in 0..n_ang {
            let th = 2.0 * PI * ai as f64 / n_ang as f64;
            let mut sum = C(0.0, 0.0);
            for w in 0..ways {
                let n = cfg[w * CFG].round().max(1.0) as usize;
                let a = cfg[w * CFG + 1];
                let r = cfg[w * CFG + 2];
                let shadow_w = 1.0 / (1.0 + 1.0 / (k * r).powi(2).max(1e-9));
                let mut acc = C(0.0, 0.0);
                for d in 0..n {
                    let phi = 2.0 * PI * d as f64 / n as f64;
                    let al = th - phi;
                    let dir = piston(k * a * al.sin());
                    let lobe = if al.cos() > 0.0 { 1.0 } else { 0.5 + 0.5 * al.cos() };
                    let lobe = (1.0 - shadow_w) + shadow_w * lobe * lobe;
                    let ph = k * r * al.cos();
                    acc = acc.add(C(ph.cos(), ph.sin()).scale(dir * lobe));
                }
                // normalise so every way has equal 1-driver-equivalent power
                sum = sum.add(band[w].mul(acc).scale(1.0 / (n as f64).sqrt()));
            }
            out.push(20.0 * sum.abs().max(1e-9).log10());
        }
    }
    out.len()
}

// ---- 垂直面(仰角)の指向性: 縦に積んだ各WAYの開口 ----
// per way: z_m, aperture_h_m, emission_elev_deg, gain_db ; crossovers reuse IN tail
static mut VIN: [f64; MAX_WAYS * 4] = [0.0; MAX_WAYS * 4];
static mut VOUT: Vec<f64> = Vec::new();
#[no_mangle]
pub extern "C" fn v_in_ptr() -> *mut f64 { std::ptr::addr_of_mut!(VIN) as *mut f64 }
#[no_mangle]
pub extern "C" fn v_out_ptr() -> *const f64 { unsafe { (*std::ptr::addr_of!(VOUT)).as_ptr() } }

/// Output: n_freq * n_el dB, elevation -90..+90 deg. Each way is a uniform line aperture of height H
/// radiating toward `emission_elev`; positions add the stacking phase.
#[no_mangle]
pub extern "C" fn vertical(ways: usize, n_freq: usize, n_el: usize, f_lo: f64, f_hi: f64) -> usize {
    let ways = ways.clamp(1, MAX_WAYS);
    let cfg = unsafe { *std::ptr::addr_of!(IN) };
    let v = unsafe { *std::ptr::addr_of!(VIN) };
    let out = unsafe { &mut *std::ptr::addr_of_mut!(VOUT) };
    out.clear();
    for fi in 0..n_freq {
        let t = fi as f64 / (n_freq.max(2) - 1) as f64;
        let f = f_lo * (f_hi / f_lo).powf(t);
        let k = 2.0 * PI * f / 343.0;
        let mut band = [C(1.0, 0.0); MAX_WAYS];
        for w in 0..ways {
            let mut h = C(1.0, 0.0);
            if w > 0 { h = h.mul(lr4_hp(f, cfg[MAX_WAYS * CFG + w - 1])); }
            if w + 1 < ways { h = h.mul(lr4_lp(f, cfg[MAX_WAYS * CFG + w])); }
            band[w] = h.scale(10f64.powf(v[w * 4 + 3] / 20.0));
        }
        for ei in 0..n_el {
            let el = (-90.0 + 180.0 * ei as f64 / (n_el - 1) as f64).to_radians();
            let mut sum = C(0.0, 0.0);
            for w in 0..ways {
                let (z, hh, phi0) = (v[w * 4], v[w * 4 + 1], v[w * 4 + 2].to_radians());
                let x = k * hh / 2.0 * (el.sin() - phi0.sin());
                let d = if x.abs() < 1e-6 { 1.0 } else { x.sin() / x };
                let ph = k * z * el.sin();
                sum = sum.add(band[w].mul(C(ph.cos(), ph.sin())).scale(d));
            }
            out.push(20.0 * sum.abs().max(1e-9).log10());
        }
    }
    out.len()
}
