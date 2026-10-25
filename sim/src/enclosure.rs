//! Enclosure model: Thiele-Small sealed / vented alignment, port sizing, wall stiffness.
//! Lossy 4th-order vented transfer function after Small (1973); sealed 2nd order.
//! Several identical drivers in one chamber are modelled as one driver with n*Sd and n*Vas.

use std::f64::consts::PI;

const C0: f64 = 343.0;
const RHO: f64 = 1.2;

// in: fs qts vas_L sd_cm2 xmax_mm n vb_L kind(0 sealed,1 vented) port_d_mm fb(0=auto) ql
static mut EIN: [f64; 11] = [0.0; 11];
// out scalars: f3 f_c_or_b qtc port_len_mm port_vel port_area_cm2 peak_db alpha spl_max_at_f3 vb_qb3_L fb_used
static mut EOUT: [f64; 12] = [0.0; 12];
pub const NPTS: usize = 160;
static mut ECURVE: [f64; NPTS] = [0.0; NPTS];

#[derive(Clone, Copy)]
struct C(f64, f64);
impl C {
    fn mul(self, o: C) -> C { C(self.0 * o.0 - self.1 * o.1, self.0 * o.1 + self.1 * o.0) }
    fn add(self, o: C) -> C { C(self.0 + o.0, self.1 + o.1) }
    fn scale(self, s: f64) -> C { C(self.0 * s, self.1 * s) }
    fn div(self, o: C) -> C {
        let d = o.0 * o.0 + o.1 * o.1;
        C((self.0 * o.0 + self.1 * o.1) / d, (self.1 * o.0 - self.0 * o.1) / d)
    }
    fn abs(self) -> f64 { self.0.hypot(self.1) }
}

#[no_mangle]
pub extern "C" fn enc_in_ptr() -> *mut f64 { std::ptr::addr_of_mut!(EIN) as *mut f64 }
#[no_mangle]
pub extern "C" fn enc_out_ptr() -> *const f64 { std::ptr::addr_of!(EOUT) as *const f64 }
#[no_mangle]
pub extern "C" fn enc_curve_ptr() -> *const f64 { std::ptr::addr_of!(ECURVE) as *const f64 }

/// Frequency of curve point `i` (log spaced 15 Hz .. 3 kHz).
pub fn curve_freq(i: usize) -> f64 { 15.0 * (3000.0f64 / 15.0).powf(i as f64 / (NPTS - 1) as f64) }

fn response(f: f64, fs: f64, qts: f64, alpha: f64, vented: bool, fb: f64, ql: f64) -> f64 {
    let s = C(0.0, f / fs); // normalised to fs
    let s2 = s.mul(s);
    if !vented {
        // sealed: fc = fs*sqrt(1+alpha), qtc = qts*sqrt(1+alpha)
        let k = (1.0 + alpha).sqrt();
        let (fc, qtc) = (fs * k, qts * k);
        let sc = C(0.0, f / fc);
        let n = sc.mul(sc);
        let d = n.add(sc.scale(1.0 / qtc)).add(C(1.0, 0.0));
        return 20.0 * n.div(d).abs().max(1e-9).log10();
    }
    let ts = 1.0; // time constants in units of 1/ws
    let tb = fs / fb;
    let s3 = s2.mul(s);
    let s4 = s2.mul(s2);
    let num = s4.scale(tb * tb * ts * ts);
    let den = s4
        .scale(tb * tb * ts * ts)
        .add(s3.scale(tb * tb * ts / qts + tb * ts * ts / ql))
        .add(s2.scale((alpha + 1.0) * tb * tb + tb * ts / (ql * qts) + ts * ts))
        .add(s.scale(tb / ql + ts / qts))
        .add(C(1.0, 0.0));
    20.0 * num.div(den).abs().max(1e-9).log10()
}

/// Reads EIN, writes ECURVE (dB, NPTS points) and EOUT. Returns 1 on success.
#[no_mangle]
pub extern "C" fn enclosure() -> usize {
    let i = unsafe { *std::ptr::addr_of!(EIN) };
    let out = unsafe { &mut *std::ptr::addr_of_mut!(EOUT) };
    let curve = unsafe { &mut *std::ptr::addr_of_mut!(ECURVE) };
    let (fs, qts, vas_l, sd_cm2, xmax_mm, n, vb_l, kind, port_d_mm, fb_in, ql) =
        (i[0], i[1], i[2], i[3], i[4], i[5].max(1.0), i[6].max(0.1), i[7], i[8], i[9], if i[10] > 0.0 { i[10] } else { 7.0 });
    let vas = vas_l * n; // n drivers share the chamber
    let alpha = vas / vb_l;
    let vented = kind >= 0.5;
    let fb = if vented { if fb_in > 0.0 { fb_in } else { fs * alpha.powf(0.31) } } else { 0.0 };
    for k in 0..NPTS {
        curve[k] = response(curve_freq(k), fs, qts, alpha, vented, fb, ql);
    }
    // F3 relative to the high-frequency level (0 dB); peak = max boost
    let mut f3 = curve_freq(NPTS - 1);
    let mut peak = f64::MIN;
    let mut found = false;
    for k in (0..NPTS).rev() {
        peak = peak.max(curve[k]);
        if !found && curve[k] < -3.0 { f3 = curve_freq(k + 1); found = true; }
    }
    let kk = (1.0 + alpha).sqrt();
    out[0] = f3;
    out[1] = if vented { fb } else { fs * kk };
    out[2] = if vented { qts } else { qts * kk };
    // port
    let (mut plen, mut pvel, mut parea) = (0.0, 0.0, 0.0);
    if vented && port_d_mm > 0.0 {
        let d = port_d_mm / 1000.0;
        let sp = PI * d * d / 4.0;
        let vb = vb_l / 1000.0;
        let leff = C0 * C0 * sp / (4.0 * PI * PI * fb * fb * vb);
        plen = (leff - 0.73 * d) * 1000.0;
        let vd = n * sd_cm2 * 1e-4 * xmax_mm * 1e-3; // peak displaced volume
        pvel = vd * 2.0 * PI * fb / sp;
        parea = sp * 1e4;
    }
    out[3] = plen;
    out[4] = pvel;
    out[5] = parea;
    out[6] = peak;
    out[7] = alpha;
    // max SPL at F3 from Xmax-limited displacement (free-space 4*pi, 1 m, rms)
    let vd = n * sd_cm2 * 1e-4 * xmax_mm * 1e-3;
    let w = 2.0 * PI * f3;
    let p = RHO * w * w * vd / (4.0 * PI) / 2f64.sqrt();
    out[8] = 20.0 * (p / 2e-5).log10();
    out[9] = 15.0 * qts.powf(2.87) * vas_l * n; // QB3 volume (L) for reference
    out[10] = fb;
    1
}

/// Wall check for a cylindrical shell of inner radius `r_m`, thickness `t_m`.
/// in: E[Pa] rho[kg/m3] eta r_m t_m height_m nu   out: ring_freq, compliance_ratio, mass_kg, coincidence-ish note value (c_L)
#[no_mangle]
pub extern "C" fn wall(e: f64, rho: f64, r_m: f64, t_m: f64, h_m: f64, nu: f64, which: usize) -> f64 {
    let cl = (e / (rho * (1.0 - nu * nu))).sqrt();
    match which {
        0 => cl / (2.0 * PI * r_m),                                  // ring (breathing) mode, Hz
        1 => 2.0 * 1.4 * 101_325.0 * r_m / (e * t_m),                 // wall volume compliance / air compliance
        2 => 2.0 * PI * r_m * h_m * t_m * rho,                        // shell mass
        _ => cl,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    // fs qts vas sd xmax n vb kind port fb ql
    fn run(v: [f64; 11]) -> ([f64; 12], f64) {
        unsafe { *std::ptr::addr_of_mut!(EIN) = v; }
        enclosure();
        unsafe { (*std::ptr::addr_of!(EOUT), (*std::ptr::addr_of!(ECURVE))[NPTS - 1]) }
    }
    #[test]
    fn sim_runs() {
        let cases: [(&str, [f64; 11]); 6] = [
            ("WAY1 8in x2 sealed 33L", [28.0, 0.42, 60.0, 220.0, 10.0, 2.0, 33.0, 0.0, 0.0, 0.0, 7.0]),
            ("WAY1 8in x2 vented 60L d60", [28.0, 0.42, 60.0, 220.0, 10.0, 2.0, 60.0, 1.0, 60.0, 0.0, 7.0]),
            ("WAY2 5in x2 sealed 9L", [55.0, 0.45, 12.0, 85.0, 5.0, 2.0, 9.0, 0.0, 0.0, 0.0, 7.0]),
            ("WAY2 5in x2 vented 9L d35", [55.0, 0.45, 12.0, 85.0, 5.0, 2.0, 9.0, 1.0, 35.0, 0.0, 7.0]),
            ("WAY3 3in x2 sealed 1.5L", [120.0, 0.6, 1.5, 28.0, 2.0, 2.0, 1.5, 0.0, 0.0, 0.0, 7.0]),
            ("sanity: sealed qtc .707 box", [30.0, 0.35, 100.0, 200.0, 8.0, 1.0, 100.0 / (((0.707f64 / 0.35).powi(2)) - 1.0), 0.0, 0.0, 0.0, 7.0]),
        ];
        for (n, v) in cases {
            let (o, hf) = run(v);
            println!("{n}: F3={:.1}Hz f_c/b={:.1} Q={:.2} portL={:.0}mm vel={:.1}m/s peak={:.1}dB alpha={:.2} SPLmax@F3={:.0}dB hf={:.2}", o[0], o[1], o[2], o[3], o[4], o[6], o[7], o[8], hf);
            assert!(hf.abs() < 0.5);
        }
    }
}

// ---- 対向ユニットの隙間(環状スリット) ----
// in: n_drivers sd_cm2 xmax_mm r_throat_mm gap_mm r_mouth_mm gap_mouth_mm f_low_hz u_lim
// out: s_throat_cm2 compression_ratio u_at_xmax s_mouth_cm2 f_res spl_limit_slot spl_limit_xmax slot_limited(0/1)
static mut SIN: [f64; 9] = [0.0; 9];
static mut SOUT: [f64; 8] = [0.0; 8];
#[no_mangle]
pub extern "C" fn slot_in_ptr() -> *mut f64 { std::ptr::addr_of_mut!(SIN) as *mut f64 }
#[no_mangle]
pub extern "C" fn slot_out_ptr() -> *const f64 { std::ptr::addr_of!(SOUT) as *const f64 }

fn spl_from_vd(vd: f64, f: f64) -> f64 {
    let w = 2.0 * PI * f;
    20.0 * (RHO * w * w * vd / (4.0 * PI) / 2f64.sqrt() / 2e-5).log10()
}

#[no_mangle]
pub extern "C" fn slot() -> usize {
    let i = unsafe { *std::ptr::addr_of!(SIN) };
    let o = unsafe { &mut *std::ptr::addr_of_mut!(SOUT) };
    let (n, sd, xm, rt, g0, rm, g1, f, ulim) = (i[0], i[1] * 1e-4, i[2] * 1e-3, i[3] * 1e-3, i[4] * 1e-3, i[5] * 1e-3, i[6] * 1e-3, i[7], if i[8] > 0.0 { i[8] } else { 20.0 });
    let sd_tot = n * sd; // push-pull: both cones move in together
    let s_th = 2.0 * PI * rt * g0;
    let s_mo = 2.0 * PI * rm * g1;
    let vd = sd_tot * xm;
    let u = 2.0 * PI * f * vd / s_th;
    // radial duct of constant gap: acoustic mass M = rho/(2 pi g) ln(rm/rt); cavity between cones
    let gm = (g0 * g1).sqrt();
    let m = RHO / (2.0 * PI * gm) * (rm / rt).ln();
    let vf = PI * rt * rt * g0;
    let c = vf / (RHO * C0 * C0);
    let fres = 1.0 / (2.0 * PI * (m * c).sqrt());
    let vd_slot = ulim * s_th / (2.0 * PI * f);
    o[0] = s_th * 1e4;
    o[1] = sd_tot / s_th;
    o[2] = u;
    o[3] = s_mo * 1e4;
    o[4] = fres;
    o[5] = spl_from_vd(vd_slot.min(vd), f);
    o[6] = spl_from_vd(vd, f);
    o[7] = if vd_slot < vd { 1.0 } else { 0.0 };
    1
}

// ---- 吊り下げ反射円錐(上向きユニットの上) ----
// in: r_driver_mm sd_cm2 xmax_mm alpha_deg rim_gap_mm cone_r_mm f_low_hz u_lim
// out: elevation_deg area_exit_cm2 compression u_at_xmax aperture_h_mm cone_height_mm f_ctrl spl_limit
static mut RIN: [f64; 8] = [0.0; 8];
static mut ROUT: [f64; 8] = [0.0; 8];
#[no_mangle]
pub extern "C" fn refl_in_ptr() -> *mut f64 { std::ptr::addr_of_mut!(RIN) as *mut f64 }
#[no_mangle]
pub extern "C" fn refl_out_ptr() -> *const f64 { std::ptr::addr_of!(ROUT) as *const f64 }

#[no_mangle]
pub extern "C" fn reflector() -> usize {
    let i = unsafe { *std::ptr::addr_of!(RIN) };
    let o = unsafe { &mut *std::ptr::addr_of_mut!(ROUT) };
    let (a, sd, xm, al, gap, rc, f, ulim) = (i[0] * 1e-3, i[1] * 1e-4, i[2] * 1e-3, i[3].to_radians(), i[4] * 1e-3, i[5] * 1e-3, i[6], if i[7] > 0.0 { i[7] } else { 20.0 });
    // reflected ray leaves at 2*alpha from the (upward) axis => elevation above horizontal = 90 - 2*alpha
    o[0] = 90.0 - 2.0 * i[3];
    let a_exit = 2.0 * PI * a * gap;
    o[1] = a_exit * 1e4;
    o[2] = sd / a_exit;
    let vd = sd * xm;
    o[3] = 2.0 * PI * f * vd / a_exit;
    o[4] = ((rc - a).max(0.0) / al.tan()) * 1e3;
    o[5] = rc / al.tan() * 1e3;
    o[6] = C0 / (2.0 * PI * rc);
    let vd_lim = (ulim * a_exit / (2.0 * PI * f)).min(vd);
    o[7] = spl_from_vd(vd_lim, f);
    1
}

#[cfg(test)]
mod tests2 {
    use super::*;
    #[test]
    fn slot_and_reflector() {
        // sub: 2 x 8in (Sd 220), Xmax 10, throat r 80, gap 10 / 20, mouth r 190
        for g in [6.0, 10.0, 20.0, 40.0] {
            unsafe { *std::ptr::addr_of_mut!(SIN) = [2.0, 220.0, 10.0, 80.0, g, 190.0, g * 1.5, 40.0, 20.0]; }
            slot();
            let o = unsafe { *std::ptr::addr_of!(SOUT) };
            println!("slot gap {g}mm: S_th={:.0}cm2 CR={:.1} u={:.1}m/s fres={:.0}Hz SPLslot={:.0} SPLxmax={:.0} limited={}", o[0], o[1], o[2], o[4], o[5], o[6], o[7]);
        }
        for al in [35.0, 45.0, 55.0] {
            unsafe { *std::ptr::addr_of_mut!(RIN) = [37.0, 44.0, 3.0, al, 14.0, 70.0, 600.0, 20.0]; }
            reflector();
            let o = unsafe { *std::ptr::addr_of!(ROUT) };
            println!("refl alpha {al}: elev={:.0}deg Aexit={:.1}cm2 CR={:.2} u={:.1} H={:.0}mm coneH={:.0} fctrl={:.0}Hz", o[0], o[1], o[2], o[3], o[4], o[5], o[6]);
        }
    }
}
