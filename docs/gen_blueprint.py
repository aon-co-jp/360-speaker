"""設計図(受動ネットワーク回路図+構造断面図)のSVG/HTMLを生成する。 python docs/gen_blueprint.py
構造: WAY1(超低音)・WAY2(低音)=2個を向き合わせ、わずかな隙間(環状スリット)から360°放射。
      WAY3〜5(中・高・超高音)=上向きユニットの上に、下が尖り上が平らな円錐を吊り下げる。"""
import math, pathlib
from lr4_ladder import lr4_lp_g
G = lr4_lp_g()   # LR4(24dB/oct)受動ラダーの正規化値 [L1,C1,L2,C2](R=1, w=1)

FX = [150, 580, 4400, 14500]                 # 分割周波数 Hz(シミュレーターの探索結果)
RS = [4.0, 4.0, 8.0, 8.0, 8.0]              # 各WAYの公称負荷: WAY1,2=8Ω×2並列=4Ω / WAY3〜5=8Ω×1
NAMES = [("超低音(サブウーファー)", "20-150Hz"), ("低音", "150-580Hz"), ("中音", "580Hz-4.4kHz"),
         ("高音", "4.4k-14.5kHz"), ("超高音", "14.5k-40kHz+")]
DRV = ["φ200mm(8in)ウーファー×2 対向", "φ130mm(5in)ウーファー×2 対向", "φ75mm(3in)ミッド×1 上向き",
       "φ25mm ドームツィーター×1 上向き", "φ19mm リボン/AMT×1 上向き(40kHz以上)"]

def lr2_lp(f, R): return R / (math.pi * f) * 1e3, 1 / (4 * math.pi * f * R) * 1e6   # mH, uF
def lr2_hp(f, R): return R / (4 * math.pi * f) * 1e3, 1 / (math.pi * f * R) * 1e6   # mH, uF
def fmt(v): return f"{v:.2f}" if v < 10 else f"{v:.1f}" if v < 100 else f"{v:.0f}"

INK = "#111"
def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{s}</text>'
def line(x1, y1, x2, y2, w=1.6, d=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="{w}" {d}/>'
def rect(x, y, w, h, fill="none", sw=1.8, st=INK, d=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{st}" stroke-width="{sw}" {d}/>'

def s_cap(x, y, lab):
    return (f'<rect x="{x-32}" y="{y-20}" width="64" height="40" fill="#fff"/>' + line(x - 30, y, x - 5, y) + line(x + 5, y, x + 30, y)
            + line(x - 5, y - 16, x - 5, y + 16, 2.4) + line(x + 5, y - 16, x + 5, y + 16, 2.4) + text(x, y - 24, lab, 12, "middle"))
def s_ind(x, y, lab):
    p = f"M{x-30},{y} " + "".join("a7.5,9 0 0 1 15,0 " for _ in range(4))
    return f'<rect x="{x-32}" y="{y-12}" width="64" height="24" fill="#fff"/><path d="{p}" fill="none" stroke="{INK}" stroke-width="1.8"/>' + text(x, y - 18, lab, 12, "middle")
def sh_cap(x, y, g, lab):
    m = (y + g) / 2
    return line(x, y, x, m - 5) + line(x, m + 5, x, g) + line(x - 16, m - 5, x + 16, m - 5, 2.4) + line(x - 16, m + 5, x + 16, m + 5, 2.4) + text(x + 22, m + 4, lab, 12)
def sh_ind(x, y, g, lab):
    p = f"M{x},{y} " + "".join("a9,7.5 0 0 1 0,15 " for _ in range(4))
    return f'<path d="{p}" fill="none" stroke="{INK}" stroke-width="1.8"/>' + line(x, y + 60, x, g) + text(x + 14, y + 36, lab, 12)
def res(x, y, lab, vert=False):
    if vert:
        return rect(x - 6, y, 12, 40, "#fff") + text(x + 12, y + 24, lab, 11)
    return rect(x - 20, y - 6, 40, 12, "#fff") + text(x, y - 12, lab, 11, "middle")
def speaker(x, y, lab):
    return (rect(x, y - 10, 14, 20) + f'<path d="M{x+14},{y-10} L{x+30},{y-22} L{x+30},{y+22} L{x+14},{y+10}" fill="none" stroke="{INK}" stroke-width="1.8"/>' + text(x + 38, y + 4, lab, 11))

def lpad(R, k_db):
    k = 10 ** (-k_db / 20)
    return R * (1 - k), R * k / (1 - k)

def schematic():
    W, H = 1700, 1180
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Meiryo,Yu Gothic,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         text(40, 44, "360-speaker  受動ネットワーク回路図(1台のアンプ→5WAY)", 24, weight="bold"),
         text(40, 70, "図1/2  2026-10-25 第3版  WAY1・2=8Ω×2並列(4Ω)・WAY3〜5=8Ω×1  クロスオーバーは4次LR(Linkwitz-Riley, 24dB/oct)", 13)]
    gy = 1074
    o.append(line(150, gy, 1560, gy, 2.2)); o.append(text(142, gy + 4, "GND", 12, "end"))
    o.append(rect(40, 480, 70, 130, "none", 2.4) + text(75, 540, "AMP", 18, "middle", "bold") + text(75, 562, "1台", 13, "middle"))
    o.append(line(110, 510, 150, 510, 2.4)); o.append(text(116, 504, "+", 14)); o.append(line(75, 610, 75, gy, 2.2)); o.append(line(75, gy, 150, gy, 2.2))
    o.append(line(150, 150, 150, 960, 2.4))
    ys = [150 + i * 200 for i in range(5)]
    for i in range(5):
        y = ys[i]; g = y + 85; R = RS[i]
        o.append(text(170, y - 50, f"WAY{i+1}  {NAMES[i][0]}  {NAMES[i][1]}   [{DRV[i]}]", 15, weight="bold"))
        body = []
        x = 230
        if i > 0:      # HP(LR4): 直列C, 並列L, 直列C, 並列L
            w = 2 * math.pi * FX[i - 1]
            for k, gg in enumerate(G):
                if k % 2 == 0:
                    body.append(s_cap(x, y, f"C{k//2+1} {fmt(1 / (gg * R * w) * 1e6)}µF")); x += 70
                else:
                    body.append(sh_ind(x - 20, y, g, f"L{k//2+1} {fmt(R / (gg * w) * 1e3)}mH")); x += 40
        if i < 4:      # LP(LR4): 直列L, 並列C, 直列L, 並列C
            w = 2 * math.pi * FX[i]
            for k, gg in enumerate(G):
                if k % 2 == 0:
                    body.append(s_ind(x + 40, y, f"L{k//2+1} {fmt(gg * R / w * 1e3)}mH")); x += 90
                else:
                    body.append(sh_cap(x - 20, y, g, f"C{k//2+1} {fmt(gg / (w * R) * 1e6)}µF")); x += 40
        x += 80
        body.append(res(x, y, "Rs"))
        body.append(line(x + 55, y, x + 55, y + 20) + res(x + 55, y + 20, "Rp", True) + line(x + 55, y + 60, x + 55, g))
        body.append(f'<rect x="{x-70}" y="{y-34}" width="180" height="118" fill="none" stroke="#c0392b" stroke-width="1.3" stroke-dasharray="6 4"/>')
        rs, rp = lpad(R, 6)
        body.append(text(x + 20, y + 100, f"VR{i+1} 24接点L-pad({R:.0f}Ω) -6dB: Rs {rs:.1f}Ω / Rp {rp:.1f}Ω", 11, "middle", fill="#c0392b"))
        x += 150
        o.append(line(150, y, x, y))
        o.extend(body)
        if i < 2:   # 対向2個(並列、片方は逆極性配線)
            o.append(line(x, y - 30, x, y + 30)); o.append(line(x, y - 30, x + 40, y - 30)); o.append(line(x, y + 30, x + 40, y + 30))
            o.append(speaker(x + 40, y - 30, "下側ユニット(上向き) 正極性")); o.append(speaker(x + 40, y + 30, "上側ユニット(下向き) 逆極性"))
            xe = x + 54
            o.append(line(xe, y - 30, xe, y + 30)); o.append(text(xe + 8, y + 56, "対向: 片方を逆極性に配線 → 両コーンが同時に隙間へ向かう(押し合い)", 11))
            o.append(line(xe, y + 30, xe, g))
        else:
            o.append(line(x, y, x + 40, y)); o.append(speaker(x + 40, y, "上向き(吊り下げ円錐で水平360°へ反射)"))
            xe = x + 54
            o.append(line(xe, y + 10, xe, g))
        o.append(line(200, g, 1560, g, 1.6))
    o.append(line(1560, ys[0] + 85, 1560, gy, 1.6))
    notes = ["L-padはフィルターの後段(ユニット側)に置くので、フィルターから見た負荷は減衰量によらず一定(WAY1・2=4Ω、WAY3〜5=8Ω)。分割周波数が動かない。",
             "抵抗は無誘導巻線または金属箔(バルク)、接点は金/銀メッキのロータリー。減衰 0〜-20dB(24段)+ミュート。WAY1・2は大電力(50W級)・WAY3〜5は小電力(5W級)の抵抗を選ぶ。",
             "LC値は単独LR4(ラダー)の理論値(分割ごと)。実機はユニットのインピーダンス曲線で変わるためゾベル回路と実測による調整が必須(初期値)。",
             "複数WAYの並列接続: アンプから見た負荷は帯域内で各WAYの4Ω/8Ω。パワーアンプは4Ω負荷対応を選ぶ。"]
    for j, n in enumerate(notes):
        o.append(text(40, 1106 + j * 18, n, 12))
    o.append("</svg>")
    return "\n".join(o)

def mech():
    W, H = 1700, 1180
    S = 0.85                                  # px/mm
    base_y = 1120
    def Y(mm): return base_y - mm * S
    def hw(dia): return dia * S / 2
    cx = 360
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Meiryo,Yu Gothic,sans-serif">',
         f'<defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#c0392b"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         text(40, 44, "360-speaker  構造断面図(対向スリット + 吊り下げ円錐)", 24, weight="bold"),
         text(40, 70, "図2/2  単位mm(初期案)  中心軸の断面。WAY1・2=向き合う2個+環状スリット / WAY3〜5=上向き+吊り下げ円錐", 13)]
    o.append(rect(cx - 175, Y(40), 350, 40 * S, "#ddd"))
    o.append(text(cx, Y(0) + 18, "ベース φ350 / ネットワーク室(底部・防振)", 12, "middle"))
    o.append(rect(cx - hw(430), Y(480), 430 * S, 440 * S, "#f4f4f6", 2.2))
    o.append(rect(cx - hw(250), Y(732), 250 * S, 252 * S, "#f4f4f6", 2.2))
    for (a, b, lab) in [(40, 250, "後室(密閉) 約20L"), (270, 480, "後室(密閉) 約20L")]:
        o.append(rect(cx - hw(380), Y(b), 380 * S, (b - a) * S, "#fff", 1.2, "#999"))
        o.append(text(cx - hw(380) + 8, Y(b) + 20, lab, 11))
    for sgn, ybase in [(1, 250), (-1, 270)]:
        yb = Y(ybase)
        o.append(f'<path d="M{cx-hw(200)},{yb} L{cx-hw(70)},{yb - sgn*60*S} L{cx+hw(70)},{yb - sgn*60*S} L{cx+hw(200)},{yb} Z" fill="#999" stroke="{INK}" stroke-width="1.6"/>')
    for dx in (-1, 1):
        o.append(f'<path d="M{cx+dx*(hw(430)+4)},{Y(260)} l{dx*50},0" stroke="#c0392b" stroke-width="2.4" marker-end="url(#a)"/>')
    o.append(text(cx + hw(430) + 62, Y(260) + 4, "環状スリット(隙間20mm→出口30mmへフレア)から水平360°放射", 12, fill="#c0392b"))
    for (a, b, lab) in [(480, 600, "後室 約4L"), (612, 732, "後室 約4L")]:
        o.append(rect(cx - hw(200), Y(b), 200 * S, (b - a) * S, "#fff", 1.2, "#999"))
        o.append(text(cx - hw(200) + 6, Y(b) + 18, lab, 11))
    for sgn, ybase in [(1, 600), (-1, 612)]:
        yb = Y(ybase)
        o.append(f'<path d="M{cx-hw(130)},{yb} L{cx-hw(50)},{yb - sgn*40*S} L{cx+hw(50)},{yb - sgn*40*S} L{cx+hw(130)},{yb} Z" fill="#999" stroke="{INK}" stroke-width="1.6"/>')
    o.append(text(cx + hw(250) + 10, Y(606) + 4, "← 隙間12mm(フレア出口18mm)", 12, fill="#c0392b"))
    cells = [("WAY3 中音 φ75", 732, 80, 62, 70, 14), ("WAY4 高音 φ25", 930, 60, 26, 35, 6), ("WAY5 超高音 φ19", 1040, 50, 20, 25, 4)]
    ods = [180, 140, 110]
    for (nm, y0, rear, drv, rc, gap), od in zip(cells, ods):
        o.append(rect(cx - hw(od), Y(y0 + rear), od * S, rear * S, "#fff", 1.2, "#999"))
        o.append(text(cx + hw(od) + 10, Y(y0 + rear / 2) + 4, f"{nm}(後室 密閉)", 12))
        yd = y0 + rear
        o.append(f'<path d="M{cx-hw(drv)},{Y(yd)} L{cx-hw(drv*0.45)},{Y(yd+12)} L{cx+hw(drv*0.45)},{Y(yd+12)} L{cx+hw(drv)},{Y(yd)} Z" fill="#999" stroke="{INK}" stroke-width="1.5"/>')
        apex = yd + 12 + gap
        o.append(f'<path d="M{cx},{Y(apex)} L{cx-rc*S},{Y(apex+rc)} L{cx+rc*S},{Y(apex+rc)} Z" fill="#cfe3ff" stroke="#2a6df4" stroke-width="1.8"/>')
        o.append(line(cx - rc * S, Y(apex + rc), cx + rc * S, Y(apex + rc), 2.4))
        o.append(f'<path d="M{cx+rc*S*0.75+6},{Y(apex+rc*0.75)} l40,0" stroke="#c0392b" stroke-width="2.4" marker-end="url(#a)"/>')
    o.append(text(cx + 150, Y(990) + 4, "吊り下げ円錐(頂角90°、下が尖り上が平ら)→ 水平へ反射", 12, fill="#2a6df4"))
    o.append(text(cx, Y(1160), "吊り円錐は細い支柱3本で上段から吊る(共振を避けるため太くしない)", 12, "middle"))
    px = 900
    o.append(text(px, 120, "設計のポイント", 16, weight="bold"))
    rows = [("WAY", "帯域", "方式", "ユニット", "分割(LR4)"),
            ("1", "20-150Hz", "対向2個+隙間20mm", "φ200×2(8in)", "LP 150Hz"),
            ("2", "150-580Hz", "対向2個+隙間12mm", "φ130×2(5in)", "HP150 / LP580Hz"),
            ("3", "0.58-4.4kHz", "上向き+吊り円錐", "φ75×1", "HP580 / LP4.4k"),
            ("4", "4.4-14.5kHz", "上向き+吊り円錐", "φ25×1", "HP4.4k / LP14.5k"),
            ("5", "14.5k-40kHz+", "上向き+吊り円錐", "φ19リボン×1", "HP14.5kHz")]
    xs = [px, px + 50, px + 190, px + 400, px + 560]
    for j, r_ in enumerate(rows):
        for k, c in enumerate(r_):
            o.append(text(xs[k], 152 + j * 26, c, 13, weight="bold" if j == 0 else "normal"))
        o.append(line(px, 158 + j * 26, px + 740, 158 + j * 26, 0.8))
    notes = ["・WAY1・2: 2個のコーンが同時に隙間へ向かう押し合い配線(片方を逆極性)。隙間が小さいほど圧縮比が上がり風速が増す→ 超低音は隙間20mm以上を推奨(40Hz・Xmaxで風速11m/s、10mmでは22m/sで制限)。",
             "・隙間は外へフレア(出口を広げる)して風切り音・圧縮を抑える。前室(コーン間)の共振は1.1〜2.0kHz→ 分割より十分高い。",
             "・WAY3〜5: 円錐の半頂角45°で水平放射(反射角=2×半頂角)。縁の隙間は圧縮比1.6以下に。円錐半径は帯域下限の波長に対し大きく(小さいと拡散制御が効かない)。",
             "・水平面は円対称で全方位。垂直面は各WAYの位置・開口高さでロービング(縦方向の山谷)が出る→ シミュレーターで分割次数・間隔・開口・円錐形状を比較(仰角±30°内のばらつき 約13〜14dB、4.4kHz付近に残る。条件による差は小さい)。",
             "・外殻は円筒(壁のたわみは平板より小さい)。MDF25mm程度から。内部に補強リブ・吸音材。ユニット背面には防振ガスケット。",
             "・実機では円錐形状・支柱・隙間を試作し、指向性測定(水平・垂直)で詰める必要がある。"]
    yy = 340
    for n in notes:
        for k in range(0, len(n), 50):
            o.append(text(px, yy, n[k:k + 50], 13)); yy += 20
        yy += 8
    o.append(text(px, 1130, "※全高 約1140mm(ベース40mm含む)。寸法は図示の初期案。", 12))
    o.append("</svg>")
    return "\n".join(o)

def page(svg):
    return '<!doctype html><html lang="ja"><meta charset="utf-8"><style>@page{size:1700px 1180px;margin:0}html,body{margin:0;background:#fff}svg{display:block}</style><body>' + svg + '</body></html>'

if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parent.parent / "out"
    out.mkdir(exist_ok=True)
    a, b = schematic(), mech()
    (out / "blueprint1-schematic.svg").write_text(a, encoding="utf-8")
    (out / "blueprint2-mechanical.svg").write_text(b, encoding="utf-8")
    (out / "blueprint1.html").write_text(page(a), encoding="utf-8")
    (out / "blueprint2.html").write_text(page(b), encoding="utf-8")
    (out / "blueprint-all.html").write_text('<!doctype html><meta charset="utf-8"><style>@page{size:1700px 1180px;margin:0}html,body{margin:0}svg{display:block;page-break-after:always}</style>' + a + b, encoding="utf-8")
    print("generated")
