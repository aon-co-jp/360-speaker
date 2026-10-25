"""web/index.html に「実測データの取り込み・較正」を追加する一回限りのパッチ(適用済みなら何もしない)。"""
import pathlib
p = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
s = p.read_text(encoding="utf-8")
if "id=\"meas\"" in s:
    print("already patched"); raise SystemExit

html = """<h2>実測データの取り込み・モデル較正 <span class="note">(REWなどで測った垂直指向性CSV/TXT。ファイル名に仰角を含める 例: <code>el_+15.txt</code>, <code>-30.csv</code>)</span></h2>
<div id="meas">
 <div class="row"><input id="mf" type="file" multiple accept=".txt,.csv"> <button id="mclear">クリア</button> <button id="mfit">モデルを較正(z・開口・角度)</button> <button id="mreset">較正を戻す</button></div>
 <p class="note" id="mi">未読込。0°(正面)のファイルが必須。各ファイルは「周波数 SPL」の2列以上(REW書き出し形式可)。0°基準の相対値で比較します。</p>
 <div class="grid">
  <div><b>実測(0°基準 dB)</b><canvas id="c_m" width="420" height="220"></canvas></div>
  <div><b>モデル(0°基準 dB)</b><canvas id="c_s" width="420" height="220"></canvas></div>
  <div><b>差(実測−モデル、±12dB)</b><canvas id="c_d" width="420" height="220"></canvas></div>
 </div>
 <p class="note" id="mo"></p>
</div>
"""
anchor = '<p class="note" id="sum"></p>'
assert anchor in s
s = s.replace(anchor, anchor + "\n" + html, 1)

js = r"""
// ---- 実測データ取り込み・較正 ----
var cal={dz:[0,0,0,0,0],hs:1,dphi:0};
var meas=null;
function parseMeas(text){const pts=[];for(const ln of text.split(/\r?\n/)){const t=ln.trim();if(!t||/^[*#%;]/.test(t))continue;const c=t.split(/[\s,;\t]+/).map(Number);if(c.length>=2&&isFinite(c[0])&&isFinite(c[1])&&c[0]>0)pts.push([c[0],c[1]])}pts.sort((a,b)=>a[0]-b[0]);return pts}
function interpLog(pts,f){if(f<pts[0][0]||f>pts[pts.length-1][0])return NaN;let lo=0,hi=pts.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(pts[m][0]<=f)lo=m;else hi=m}const t=(Math.log(f)-Math.log(pts[lo][0]))/(Math.log(pts[hi][0])-Math.log(pts[lo][0]));return pts[lo][1]+(pts[hi][1]-pts[lo][1])*t}
function loadMeasurement(files){const cur={};for(const f of files){const m=f.name.replace(/\.[^.]*$/,'').match(/([+-]?\d+(?:\.\d+)?)(?!.*\d)/);if(!m)continue;const a=+m[1];const pts=parseMeas(f.text);if(pts.length>5)cur[a]=pts}
 const angs=Object.keys(cur).map(Number).sort((a,b)=>a-b);
 if(!angs.length){$('mi').textContent='読み込めるファイルがありません(ファイル名に仰角の数値が必要)';meas=null;return}
 if(!(0 in cur)){$('mi').textContent='0°のファイル(0.txt など)が必要です。読込角: '+angs.join(', ');meas=null;return}
 meas={angs,cur};$('mi').textContent='読込: '+angs.length+'本 / 仰角 '+angs.join(', ')+'° / 0°基準の相対値で比較';compare()}
function measRel(f,a){ // 0°基準の相対dB(仰角方向は線形補間)
 const A=meas.angs;if(a<A[0]||a>A[A.length-1])return NaN;let hi=A.findIndex(x=>x>=a);if(hi<=0)hi=1;const lo=hi-1;
 const g=k=>{const c=interpLog(meas.cur[A[k]],f),z=interpLog(meas.cur[0],f);return c-z};
 const t=(a-A[lo])/(A[hi]-A[lo]);return g(lo)+(g(hi)-g(lo))*t}
function compare(){if(!meas||!data)return null;const e0=(NE-1)/2;let sq=0,cnt=0;const M=[],S=[],D=[];
 for(let f=0;f<NF;f++){const fr=FLO*Math.pow(FHI/FLO,f/(NF-1));for(let e=0;e<NE;e++){const a=-90+180*e/(NE-1);const mr=measRel(fr,a),sr=data[f*NE+e]-data[f*NE+e0];M[f*NE+e]=mr;S[f*NE+e]=sr;D[f*NE+e]=mr-sr;
   if(!isNaN(mr)&&fr>=100&&fr<=12000&&Math.abs(a)<=30){sq+=(mr-sr)*(mr-sr);cnt++}}}
 const rms=cnt?Math.sqrt(sq/cnt):NaN;compare.last={rms,M,S,D};
 // 実測のばらつき(P90-P10, ±30°)
 let w=0,wf=0;for(let f=0;f<NF;f++){const fr=FLO*Math.pow(FHI/FLO,f/(NF-1));if(fr<100||fr>12000)continue;const arr=[];for(let e=0;e<NE;e++){const a=-90+180*e/(NE-1);if(Math.abs(a)<=30&&!isNaN(M[f*NE+e]))arr.push(M[f*NE+e])}if(arr.length<4)continue;arr.sort((x,y)=>x-y);const d=arr[Math.floor(arr.length*0.9)]-arr[Math.floor(arr.length*0.1)];if(d>w){w=d;wf=fr}}
 $('mo').textContent='実測とモデルの差 RMS(±30°, 100Hz〜12kHz): '+(rms).toFixed(2)+' dB / 実測のばらつき(P90−P10, ±30°)の最悪: '+w.toFixed(1)+' dB @ '+Math.round(wf)+' Hz'+(cal.hs!=1||cal.dphi||cal.dz.some(x=>x)?' / 較正: z補正 ['+cal.dz.map(x=>x.toFixed(0)).join(',')+']mm, 開口×'+cal.hs.toFixed(2)+', 角度'+cal.dphi.toFixed(1)+'°':'');
 drawMeas();return rms}
function paintMap(id,A,colf){const c=$(id).getContext('2d'),w=420,h=220;c.clearRect(0,0,w,h);for(let f=0;f<NF;f++)for(let e=0;e<NE;e++){const v=A[f*NE+e];c.fillStyle=isNaN(v)?'#8884':colf(v);c.fillRect(f*w/NF,(NE-1-e)*h/NE,w/NF+1,h/NE+1)}}
function drawMeas(){const r=compare.last;if(!r)return;const cr=v=>'hsl('+(240-240*Math.max(0,Math.min(1,(v+30)/32)))+',80%,'+(30+25*Math.max(0,Math.min(1,(v+30)/32)))+'%)';
 paintMap('c_m',r.M,cr);paintMap('c_s',r.S,cr);paintMap('c_d',r.D,v=>{const t=Math.max(-1,Math.min(1,v/12));return t>=0?'hsl(10,80%,'+(90-45*t)+'%)':'hsl(220,80%,'+(90+45*t)+'%)'})}
function fitModel(){if(!meas){$('mo').textContent='先に実測データを読み込んでください';return}
 const _d=draw;draw=()=>{};const t0=Date.now();const score=()=>{run();return compare()};let best=score();const start=best;const rnd=(a,b)=>a+Math.random()*(b-a);
 while(Date.now()-t0<9000){const bk=JSON.stringify(cal);const k=Math.floor(rnd(0,7));
  if(k<5)cal.dz[k]=Math.max(-80,Math.min(80,cal.dz[k]+rnd(-12,12)));else if(k==5)cal.hs=Math.max(.4,Math.min(2.5,cal.hs*Math.exp(rnd(-.15,.15))));else cal.dphi=Math.max(-20,Math.min(20,cal.dphi+rnd(-3,3)));
  const r=score();if(r<best)best=r;else{Object.assign(cal,JSON.parse(bk))}}
 draw=_d;run();compare();$('mo').textContent='較正: RMS '+start.toFixed(2)+' → '+best.toFixed(2)+' dB。 '+$('mo').textContent}
function resetCal(){cal={dz:[0,0,0,0,0],hs:1,dphi:0};run();compare()}
$('mf').onchange=async e=>{const fs=[];for(const f of e.target.files)fs.push({name:f.name,text:await f.text()});loadMeasurement(fs)};
$('mclear').onclick=()=>{meas=null;$('mi').textContent='未読込。';$('mo').textContent='';['c_m','c_s','c_d'].forEach(i=>$(i).getContext('2d').clearRect(0,0,420,220))};
$('mfit').onclick=fitModel;$('mreset').onclick=resetCal;
"""
mark = "// ---- エンクロージャー ----"
assert mark in s
s = s.replace(mark, js + "\n" + mark, 1)
# run() に較正を適用、draw末尾で比較を更新
for a, b in [("vin[i*8]=zz/1000;", "vin[i*8]=(zz+cal.dz[i])/1000;"),
             ("vin[i*8+1]=H;", "vin[i*8+1]=H*(d.k=='r'?cal.hs:1);"),
             ("vin[i*8+2]=phi0;", "vin[i*8+2]=phi0+(d.k=='r'?cal.dphi:0);"),
             (" cost()}", " cost();if(meas&&!draw.fit)compare()}")]:
    assert a in s, a
    s = s.replace(a, b, 1)
p.write_text(s, encoding="utf-8")
print("patched")
