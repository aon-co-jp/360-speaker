"""web/index.html の上部(水平リング指向性)を、対向スリット+吊り下げ円錐の垂直指向性UIへ置換する一回限りのパッチ。"""
import pathlib
p = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
s = p.read_text(encoding="utf-8")
a = s.index("<h1>")
b = s.index("<h2>エンクロージャー設計")
top = """<h1>360-speaker シミュレーター <span class="note">(Rust→WASM / 近似モデル)</span></h1>
<p class="note">構造: <b>WAY1・2(超低音・低音)</b>=2個のユニットを向き合わせ、わずかな隙間(環状スリット)から360°放射。<b>WAY3〜5(中・高・超高音)</b>=下から上へ上向きに配置し、各ユニットの上から<b>下が尖り上が平らな円錐</b>を吊り下げて水平360°へ反射。→ 水平面は円対称(全方位)、課題は<b>垂直面の指向性</b>と<b>隙間・反射部の風速(圧縮)</b>。</p>
<div class="row">
 <label>WAY数 <select id="ways"><option>1</option><option>2</option><option>3</option><option>4</option><option selected>5</option></select></label>
 <label>マスター(左右連動) <input id="master" type="range" min="-30" max="6" value="0" step="0.5"> <span id="mv">0 dB</span></label>
 <label>下限周波数(風速評価) Hz <input id="flow" type="number" value="40" style="width:4em"></label>
</div>
<h2>各WAYの構造・ボリューム(下→上)</h2>
<div id="ctl"></div>
<div class="grid">
 <div><h2>垂直面(仰角)×周波数(dB)</h2><canvas id="hm" width="600" height="320"></canvas></div>
 <div><h2>垂直極座標 <span id="pf"></span> <input id="fs" type="range" min="0" max="199" value="100"></h2><canvas id="po" width="320" height="320"></canvas></div>
</div>
<h2>周波数特性(青=水平0°、橙=仰角±30°内の最大偏差)</h2><canvas id="fr" width="900" height="240"></canvas>
<p class="note" id="sum"></p>
"""
s = s[:a] + top + s[b:]
j0 = s.index("const XO=")
j1 = s.index("// ---- エンクロージャー ----")
c0 = s.index("function cost()")
costfn = s[c0:j1].replace("cfg[i][0]", "2")
js = pathlib.Path(__file__).with_name("newui.js").read_text(encoding="utf-8")
s = s[:j0] + js + costfn + s[j1:]
s = s.replace("$('ways').onchange=build;$('ver').onchange=build;$('fs').oninput=()=>data&&draw();", "$('ways').onchange=build;$('flow').oninput=run;$('fs').oninput=()=>data&&draw();")
p.write_text(s, encoding="utf-8")
print("patched")
