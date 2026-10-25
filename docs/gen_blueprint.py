"""設計図(受動ネットワーク回路図+構造図)のSVG/HTMLを生成する。 python docs/gen_blueprint.py"""
import math, pathlib

R = 4.0                       # 各WAYの公称負荷(8Ω×2並列)
FX = [100, 600, 3000, 12000]  # 分割周波数 Hz
WAYS = [("超低音(サブウーファー)", "20-100Hz", "φ250mm ウーファー", "φ250"),
        ("低音", "100-600Hz", "φ130mm ウーファー", "φ130"),
        ("中音", "600Hz-3kHz", "φ75mm コーン/ドーム", "φ75"),
        ("高音", "3k-12kHz", "φ25mm ドームツィーター", "φ25"),
        ("超高音", "12k-40kHz+", "φ19mm リボン/AMT(〜40kHz以上)", "φ19")]

def lr2_lp(f): return R / (math.pi * f) * 1e3, 1 / (4 * math.pi * f * R) * 1e6   # mH, uF
def lr2_hp(f): return R / (4 * math.pi * f) * 1e3, 1 / (math.pi * f * R) * 1e6   # mH, uF
def fmt(v): return f"{v:.2f}" if v < 10 else f"{v:.1f}" if v < 100 else f"{v:.0f}"

INK = "#111"
def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{s}</text>'
def line(x1, y1, x2, y2, w=1.6, d=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="{w}" {d}/>'

def s_cap(x, y, lab):   # 直列コンデンサ
    return f'<rect x="{x-32}" y="{y-20}" width="64" height="40" fill="#fff"/>' + line(x - 30, y, x - 5, y) + line(x + 5, y, x + 30, y) + line(x - 5, y - 16, x - 5, y + 16, 2.4) + line(x + 5, y - 16, x + 5, y + 16, 2.4) + text(x, y - 24, lab, 12, "middle")
def s_ind(x, y, lab):   # 直列コイル
    p = f"M{x-30},{y} " + "".join(f"a7.5,9 0 0 1 15,0 " for _ in range(4))
    return f'<rect x="{x-32}" y="{y-12}" width="64" height="24" fill="#fff"/>' + f'<path d="{p}" fill="none" stroke="{INK}" stroke-width="1.8" transform="translate(0,0)"/>' + text(x, y - 18, lab, 12, "middle")
def sh_cap(x, y, g, lab):  # 並列コンデンサ(下へ)
    m = (y + g) / 2
    return line(x, y, x, m - 5) + line(x, m + 5, x, g) + line(x - 16, m - 5, x + 16, m - 5, 2.4) + line(x - 16, m + 5, x + 16, m + 5, 2.4) + text(x + 22, m + 4, lab, 12)
def sh_ind(x, y, g, lab):
    p = f"M{x},{y} " + "".join("a9,7.5 0 0 1 0,15 " for _ in range(4))
    return line(x, y + 0, x, y) + f'<path d="{p}" fill="none" stroke="{INK}" stroke-width="1.8"/>' + line(x, y + 60, x, g) + text(x + 14, y + 36, lab, 12)
def res(x, y, lab, vert=False):
    if vert:
        return f'<rect x="{x-6}" y="{y}" width="12" height="40" fill="none" stroke="{INK}" stroke-width="1.8"/>' + text(x + 12, y + 24, lab, 11)
    return f'<rect x="{x-20}" y="{y-6}" width="40" height="12" fill="#fff" stroke="{INK}" stroke-width="1.8"/>' + text(x, y - 12, lab, 11, "middle")
def speaker(x, y, lab):
    return (f'<rect x="{x}" y="{y-10}" width="14" height="20" fill="none" stroke="{INK}" stroke-width="1.8"/>'
            f'<path d="M{x+14},{y-10} L{x+30},{y-22} L{x+30},{y+22} L{x+14},{y+10}" fill="none" stroke="{INK}" stroke-width="1.8"/>' + text(x + 38, y + 4, lab, 11))

def lpad(k_db):  # 定インピーダンスL型アッテネーター
    k = 10 ** (-k_db / 20)
    return R * (1 - k), R * k / (1 - k)

def schematic():
    W, H = 1700, 1180
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Meiryo,Yu Gothic,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         text(40, 44, "360-speaker  受動ネットワーク回路図(1台のアンプ→5WAY)", 24, weight="bold"),
         text(40, 70, "図1/2  2026-10-25 初版  公称負荷4Ω/WAY(8Ω×2並列)  クロスオーバーは2次LR(Linkwitz-Riley)", 13)]
    gx0, gy = 150, 1074
    o.append(line(gx0, gy, 1520, gy, 2.2)); o.append(text(gx0 - 8, gy + 4, "GND", 12, "end"))
    # アンプ
    o.append(f'<rect x="40" y="480" width="70" height="130" fill="none" stroke="{INK}" stroke-width="2.4"/>' + text(75, 540, "AMP", 18, "middle", "bold") + text(75, 562, "1台", 13, "middle"))
    o.append(line(110, 510, 150, 510, 2.4)); o.append(text(116, 504, "+", 14)); o.append(line(110, 590, 110, 590)); o.append(line(75, 610, 75, gy, 2.2)); o.append(line(75, gy, gx0, gy, 2.2))
    o.append(line(150, 150, 150, 510, 2.4)); o.append(line(150, 510, 150, 960, 2.4))
    ys = [150 + i * 200 for i in range(5)]
    for i, (name, band, drv, d) in enumerate(WAYS):
        y = ys[i]; g = y + 85
        o.append(text(170, y - 50, f"WAY{i+1}  {name}  {band}", 15, weight="bold"))
        xwire = len(o)
        o.append(line(150, y, 200, y))
        x = 230
        has_hp = i > 0; has_lp = i < 4
        if has_hp:
            L, C = lr2_hp(FX[i - 1])
            o.append(s_cap(x, y, f"C {fmt(C)}µF")); x += 70
            o.append(line(x - 40, y, x, y)); o.append(sh_ind(x - 20, y, g, f"L {fmt(L)}mH"))
            x += 40
        if has_lp:
            L, C = lr2_lp(FX[i])
            o.append(line(x - 10, y, x, y)); o.append(s_ind(x + 40, y, f"L {fmt(L)}mH")); x += 100
            o.append(line(x - 20, y, x, y)); o.append(sh_cap(x - 20, y, g, f"C {fmt(C)}µF")); x += 40
        # L型アッテネーター(目盛り付きステップ式)
        o.append(line(x, y, x + 40, y)); x += 80
        rs, rp = lpad(6)
        o.append(res(x, y, f"Rs"))
        o.append(line(x + 20, y, x + 70, y)); o.append(line(x - 60, y, x - 20, y))
        o.append(line(x + 55, y, x + 55, y + 20)); o.append(res(x + 55, y + 20, f"Rp", True)); o.append(line(x + 55, y + 60, x + 55, g))
        o.append(f'<rect x="{x-70}" y="{y-34}" width="180" height="118" fill="none" stroke="#c0392b" stroke-width="1.3" stroke-dasharray="6 4"/>')
        o.append(text(x + 20, y + 100, f"VR{i+1} 24接点ステップ式L-pad(定インピーダンス4Ω)", 11, "middle", fill="#c0392b"))
        x += 150
        o.append(line(x - 70, y, x, y))
        # ドライバー対(並列)
        o.append(line(x, y - 30, x, y + 30)); o.append(line(x, y - 30, x + 40, y - 30)); o.append(line(x, y + 30, x + 40, y + 30))
        o.append(speaker(x + 40, y - 30, f"{d} 前向き")); o.append(speaker(x + 40, y + 30, f"{d} 後向き"))
        o.append(line(x + 40, y - 30, x + 40, y - 30))
        o.insert(xwire, line(150, y, x - 0, y, 1.6))
        # ドライバー戻り→GND
        xe = x + 40 + 14
        o.append(line(xe, y + 30, xe, g)); o.append(text(xe + 6, y + 56, "前後とも同極性(外向き同時に動く)", 11))
        o.append(f'<line x1="{xe}" y1="{y - 30}" x2="{xe+90}" y2="{y - 30}" stroke="none"/>')
        # 戻り線を共通GNDレールへ
        o.append(line(200, g, 1560, g, 1.6)); o.append(line(xe, y + 30, xe, g)); o.append(line(xe, y - 30, xe, y + 30))
    o.append(line(1560, ys[0] + 85, 1560, gy, 1.6))
    # 説明
    notes = ["目盛り付きボリュームは各WAYのL-pad(Rs直列+Rp並列)。スピーカー側から見たインピーダンスが減衰量によらず4Ωで一定のため、前段のLC回路の分割周波数が動かない。",
             "抵抗は無誘導巻線または金属箔(バルク)タイプ、接点は金メッキ/銀接点のロータリー。減衰量は 0〜-20dB(24段)+ミュート。",
             "例 -6dB: Rs=2.0Ω, Rp=4.0Ω(許容電力は超低音WAYで大きく取る=50W級、高音WAYは5W級)。-12dB: Rs=3.0Ω, Rp=1.3Ω。",
             "LC値は単独LR2の理論値。実機はドライバーのインピーダンス曲線で変わるため、ゾベル回路・測定による微調整が必須(初期値)。"]
    for j, n in enumerate(notes):
        o.append(text(40, 1106 + j * 20, n, 12))
    o.append("</svg>")
    return "\n".join(o), notes

def mech():
    W, H = 1700, 1180
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Meiryo,Yu Gothic,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         text(40, 44, "360-speaker  構造図(対向ユニット×5WAY)", 24, weight="bold"),
         text(40, 70, "図2/2  単位mm(寸法は初期案)  各WAYは前後に向き合ったユニット2個で1組", 13)]
    # 立面
    x0, base, top = 130, 1090, 130
    hs = [230, 190, 165, 145, 125]  # 下→上(超低音が最下部)
    o.append(text(x0 + 100, 108, "正面立面(全高約1230)", 14, "middle", "bold"))
    y = base
    cx = x0 + 100
    sec = []
    for i in range(5):
        h = hs[i]
        sec.append((i, y - h, h)); y -= h
    o.append(f'<rect x="{x0}" y="{y-40}" width="200" height="{base-y+60}" fill="#f4f4f6" stroke="{INK}" stroke-width="2.2"/>')
    o.append(f'<rect x="{x0-30}" y="{base+20}" width="260" height="18" fill="#ddd" stroke="{INK}" stroke-width="1.8"/>' + text(cx, base + 56, "ベース(台座φ360)", 12, "middle"))
    rad = [75, 48, 34, 20, 14]; names = ["超低音", "低音", "中音", "高音", "超高音"]
    for i, ys, h in sec:
        o.append(line(x0, ys, x0 + 200, ys, 1.2))
        o.append(f'<circle cx="{cx}" cy="{ys + h/2}" r="{rad[i]}" fill="#fff" stroke="{INK}" stroke-width="2"/><circle cx="{cx}" cy="{ys + h/2}" r="{rad[i]*0.4}" fill="#999" stroke="{INK}"/>')
        o.append(text(x0 + 215, ys + h / 2 + 4, f"WAY{i+1} {names[i]}  {WAYS[i][3]}  ×2(前・後)", 13))
    o.append(text(cx, y - 50, "ネットワーク室は底部(別室・防振)/端子は背面下部", 12, "middle"))
    # 平面断面(5WAY)
    px0 = 780
    o.append(text(px0 + 330, 108, "平面断面(水平面)— 各WAYとも対向配置", 14, "middle", "bold"))
    cols = [(px0 + 80, 220), (px0 + 330, 220), (px0 + 580, 220), (px0 + 205, 470), (px0 + 455, 470)]
    for i, (cx2, cy2) in enumerate(cols):
        R2 = [100, 80, 64, 50, 40][i]
        o.append(f'<circle cx="{cx2}" cy="{cy2}" r="{R2}" fill="#f4f4f6" stroke="{INK}" stroke-width="2.2"/>')
        r = rad[i]
        for sgn, lab in ((-1, "前"), (1, "後")):
            o.append(f'<rect x="{cx2 - 12 if False else cx2 - r*0.35}" y="{cy2 + sgn*(R2-8) - 8}" width="{r*0.7}" height="16" fill="#999" stroke="{INK}" stroke-width="1.6"/>')
            o.append(text(cx2 + 12 + r * 0.4, cy2 + sgn * (R2 - 8) + 5, lab, 12))
        o.append(text(cx2, cy2 + 4, f"WAY{i+1}", 13, "middle", "bold")); o.append(text(cx2, cy2 + R2 + 28, f"{names[i]} 内径{R2*2}", 12, "middle"))
    o.append(text(px0 + 330, 590, "※ 前後2方向が基本。高域ほど側面(90°)が弱くなる→ WAYごとに45°ずつ回して段積みすると水平のばらつきを減らせる(検討案)。", 12, "middle"))
    # 仕様表
    rows = [("WAY", "帯域", "ユニット(対向×2)", "LR2分割", "ネットワーク")]
    for i in range(5):
        lo = "-" if i == 0 else f"HP {FX[i-1]}Hz"; hi = "-" if i == 4 else f"LP {FX[i]}Hz"
        rows.append((str(i + 1), WAYS[i][1], WAYS[i][2], f"{lo} / {hi}", "L・C 図1参照"))
    ty = 680
    o.append(text(780, ty, "仕様表", 15, weight="bold"))
    xs = [780, 830, 960, 1200, 1400]
    for j, r_ in enumerate(rows):
        for k, c in enumerate(r_):
            o.append(text(xs[k], ty + 28 + j * 26, c, 13, weight="bold" if j == 0 else "normal"))
        o.append(line(780, ty + 34 + j * 26, 1600, ty + 34 + j * 26, 0.8))
    notes = ["・対向配置は同極性で配線し、前後のユニットが同時に外向き/内向きに動く(反力が打ち消され、箱の振動が減る)。",
             "・1台のアンプ→受動ネットワーク(コイル+コンデンサ)→各WAYのL-pad(目盛り付きボリューム)→前後ユニットを並列接続(4Ω)。",
             "・ボリューム5個: WAY別。劣化を抑えるため可変抵抗でなく無誘導抵抗のステップ式L-pad。-6dB以上絞るとアンプ電力を抵抗が消費する(効率とのトレードオフ)。",
             "・超高音はリボン/AMT等で40kHz以上まで再生可能なユニットを選定(例: 帯域を公表している製品の実測を確認)。",
             "・実機調整: 各WAYの能率差(超低音は-6dB以上絞ることが多い)をL-padの初期値で吸収。ゾベル回路と実測の微調整が必要。"]
    yy = 880
    for n in notes:
        for k in range(0, len(n), 56):
            o.append(text(780, yy, n[k:k+56], 13)); yy += 20
        yy += 6
    o.append("</svg>")
    return "\n".join(o)

def page(svg, extra=""):
    return ('<!doctype html><html lang="ja"><meta charset="utf-8"><style>@page{size:1700px 1180px;margin:0}html,body{margin:0;background:#fff}svg{display:block}</style><body>' + svg + extra + '</body></html>')

if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parent.parent / "out"
    out.mkdir(exist_ok=True)
    s1, notes = schematic()
    # 注記を下部に追加(回路図)
    foot = "".join(f'<text x="40" y="{1135 + j*0}" font-size="1"></text>' for j in range(0))
    s1 = s1.replace("</svg>", "".join(text(40, 1135 + j * 0, "", 1) for j in range(0)) + "</svg>")
    (out / "blueprint1-schematic.svg").write_text(s1, encoding="utf-8")
    (out / "blueprint2-mechanical.svg").write_text(mech(), encoding="utf-8")
    (out / "blueprint1.html").write_text(page(s1), encoding="utf-8")
    (out / "blueprint2.html").write_text(page(mech()), encoding="utf-8")
    (out / "notes.txt").write_text("\n".join(notes), encoding="utf-8")
    print("generated")
