"""web/index.html に ユニット口径選択・振動板材質(ハイブリッド/トライブリッド)・統合ハイブリッドSTw(4WAY)を追加する一回限りのパッチ。"""
import pathlib
p = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
s = p.read_text(encoding="utf-8")
if "id=\"matp\"" in s:
    print("already patched"); raise SystemExit

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

# --- 構成選択に4WAY統合ハイブリッドを追加 ---
rep('<option>4</option><option selected>5</option></select></label>',
    '<option>4</option><option value="4h">4(ツィーター+スーパー統合ハイブリッド)</option><option selected>5</option></select></label>')
rep("const XO={5:", "const XO={'4h':[150,580,7000],5:")

# --- ユニット定義: 口径Dを持たせ、統合ハイブリッド(HYB)を追加 ---
rep("{n:'WAY1 超低音',k:'s',z:260,p:", "{n:'WAY1 超低音',k:'s',D:200,z:260,p:")
rep("{n:'WAY2 低音',k:'s',z:606,p:", "{n:'WAY2 低音',k:'s',D:130,z:606,p:")
rep("{n:'WAY3 中音',k:'r',z:850,p:", "{n:'WAY3 中音',k:'r',D:75,z:850,p:")
rep("{n:'WAY4 高音',k:'r',z:1020,p:", "{n:'WAY4 高音',k:'r',D:25,z:1020,p:")
rep("{n:'WAY5 超高音',k:'r',z:1105,p:", "{n:'WAY5 超高音',k:'r',D:19,z:1105,p:")
rep("const NF=200,NE=121,FLO=20,FHI=40000;",
    "const HYB={n:'WAY4 ハイブリッドSTw(ツィーター+スーパー統合)',k:'r',D:25,z:1020,p:{a:12.5,sd:4.9,xm:.5,al:45,gap:6,rc:35},v:0};\n"
    "const SIZES=[[150,165,200,250,300,380],[100,130,165,200],[50,75,100,130],[19,25,28,34],[10,13,19,25],[19,25,28,34]];\n"
    "const XMAX={150:8,165:8,200:10,250:12,300:14,380:16,100:3,130:5,165.1:6,50:1.5,75:3,28:.6,34:.8,13:.2,10:.15};\n"
    "const NF=200,NE=121,FLO=20,FHI=40000;")

# --- build(): 4h対応 ---
rep("function build(){n=+$('ways').value;xo=XO[n].slice();dv=WAYD.slice(0,n).map(d=>JSON.parse(JSON.stringify(d)));",
    "function build(){const wv=$('ways').value;xo=XO[wv].slice();n=wv=='4h'?4:+wv;dv=(wv=='4h'?[WAYD[0],WAYD[1],WAYD[2],HYB]:WAYD.slice(0,n)).map(d=>JSON.parse(JSON.stringify(d)));")

# --- 行に口径選択を追加 ---
rep("const p=d.p;let h='<b>'+d.n+'</b><span>'+",
    "const p=d.p;const sz=SIZES[wv=='4h'&&i==3?5:Math.min(i,4)];let h='<b>'+d.n+'</b><span>口径<select data-d=\"1\">'+sz.map(v=>'<option value=\"'+v+'\"'+(v==d.D?' selected':'')+'>'+(i<3?(v/25.4).toFixed(1)+'in('+v+')':v+'mm')+'</option>').join('')+'</select> '+")
rep("if(t.dataset.v){d.v=+t.value;$('vv'+i).textContent=t.value+' dB'}",
    "if(t.dataset.d){setSize(d,i,+t.value);build2(i);return}else if(t.dataset.v){d.v=+t.value;$('vv'+i).textContent=t.value+' dB'}")

js = r"""
// ---- ユニット口径の変更 ----
function setSize(d,i,D){d.D=D;const p=d.p,eff=0.83*D/2;
 if(d.k=='s'){p.sd=+(Math.PI*eff*eff/100).toFixed(1);p.rt=Math.round(0.4*D);p.rm=Math.round((i==0?0.95:0.77)*D);p.xm=XMAX[D]||p.xm;p.g=Math.max(8,Math.round(p.g*Math.sqrt(p.sd/ (i==0?220:85))))}
 else if(i<3&&!d.hyb){p.a=+(D/2).toFixed(1);p.sd=+(Math.PI*eff*eff/100).toFixed(1);p.xm=XMAX[D]||p.xm;p.rc=Math.round(1.9*p.a);p.gap=Math.max(6,Math.round(0.38*p.a))}
 else{p.a=+(D/2).toFixed(1);p.sd=+(0.85*Math.PI*(D/2)*(D/2)/100).toFixed(2);p.xm=XMAX[D]||0.4;p.rc=Math.round(2.8*p.a);p.gap=Math.max(3,Math.round(0.5*p.a))}}
function build2(i){const c=$('ctl');const keep=dv.map(d=>d.v);const row=c.children[i];if(!row)return;// 該当行の入力値を更新
 const d=dv[i],p=d.p;row.querySelectorAll('input[data-k]').forEach(el=>{const k=el.dataset.k;el.value=k=='z'?d.z:p[k]});run();matUI()}

// ---- 振動板材質(単体/ハイブリッド/トライブリッド) ----
var MATS=[];
function mixMat(m){const ids=[m.a,m.b,m.c].filter(Boolean),pc=[m.pa,m.pb,m.pc];let tot=0,E=0,rho=0,nu=0,eta=0;ids.forEach((id,k)=>{const x=MATS.find(q=>q.id==id);if(!x)return;const f=Math.max(0,pc[k]||0);tot+=f;E+=f*x.E;rho+=f*x.rho;nu+=f*x.nu;eta+=f*x.eta});if(!tot)return null;return{E:E/tot,rho:rho/tot,nu:nu/tot,eta:eta/tot}}
function matCalc(d,i){const m=d.m,mx=mixMat(m);if(!mx)return null;const a=d.p.a/1000,t=m.t*1e-6;
 const cl=Math.sqrt(mx.E*1e9/(mx.rho*(1-mx.nu*mx.nu)));const fbu=0.06*cl/a;           // 経験式: Al 25mm ≈ 26kHz に較正
 const mass=mx.rho*t*1.2*Math.PI*a*a*1000;                                             // g(浅いドーム面積≈1.2πa²)
 const ref=2700*40e-6*1.2*Math.PI*0.0125*0.0125*1000;                                  // 基準: Al 25mm 40µm
 return{fbu,cl,mass,dB:-20*Math.log10(mass/ref),eta:mx.eta,mix:mx}}
function matUI(){const box=$('matp');if(!box||!MATS.length)return;box.innerHTML='';
 dv.forEach((d,i)=>{if(!(d.k=='r'&&(i>=3||d.hyb)))return;if(!d.m)d.m={a:i==dv.length-1?'be':'al',b:'',c:'',pa:100,pb:0,pc:0,t:40};
  const m=d.m,opt=sel=>'<option value="">—</option>'+MATS.map(x=>'<option value="'+x.id+'"'+(x.id==sel?' selected':'')+'>'+x.name+(x.temp?' (候補)':'')+'</option>').join('');
  const need=i==dv.length-1?40000:(xo[i]||1e4)*1.3,r=matCalc(d,i);
  const ok=r&&r.fbu>=need;
  const div=document.createElement('div');div.className='way';div.dataset.i=i;
  div.innerHTML='<b>'+d.n.replace(/\(.*$/,'')+'</b><span>材質A<select data-m="a">'+opt(m.a)+'</select><input data-m="pa" type="number" value="'+m.pa+'" style="width:3.5em">% 材質B<select data-m="b">'+opt(m.b)+'</select><input data-m="pb" type="number" value="'+m.pb+'" style="width:3.5em">% 材質C<select data-m="c">'+opt(m.c)+'</select><input data-m="pc" type="number" value="'+m.pc+'" style="width:3.5em">% 厚み µm<input data-m="t" type="number" value="'+m.t+'" style="width:4em"><br><span class="note">'+
   (r?'音速 '+Math.round(r.cl)+'m/s / 分割振動(ブレークアップ)の目安 '+(r.fbu/1000).toFixed(1)+'kHz / 振動板質量 '+r.mass.toFixed(3)+'g(基準Al25mm 40µm比 感度 '+(r.dB>=0?'+':'')+r.dB.toFixed(1)+'dB) / 損失係数 '+r.eta.toFixed(3)+(ok?' <b style="color:#2a8a4a">✓ 必要 '+(need/1000).toFixed(1)+'kHz以上を満たす</b>':' <b style="color:#c0392b">⚠ 必要 '+(need/1000).toFixed(1)+'kHz(上限分割の1.3倍/40kHz)に不足</b>'):'比率を入れてください')+'</span></span><span></span>';
  box.appendChild(div)});
 box.oninput=e=>{const t=e.target,i=+t.closest('.way').dataset.i,k=t.dataset.m;if(!k)return;dv[i].m[k]=(k.length==1&&k!='t')?t.value:+t.value;matUI()}}
fetch('materials.json').then(r=>r.json()).then(j=>{MATS=j.materials;matUI();loadCand()}).catch(()=>{});
function loadCand(){fetch('data/materials-candidates.json').then(r=>r.ok?r.json():null).then(j=>{if(!j||!j.items)return;const el=$('cand');if(!el)return;
 const show=j.items.slice(0,40);el.innerHTML='<p class="note">自動収集(毎朝)の新素材候補 '+j.items.length+'件(最終更新 '+(j.updated||'?')+')。<b>未検証</b>。数値が本文から抽出できたものだけ「試算に使う」で仮の材質に追加できます。</p>'+show.map((x,k)=>'<div class="note">・<a href="'+x.url+'" target="_blank" rel="noopener noreferrer">'+x.title.replace(/</g,'&lt;')+'</a> ('+(x.first_seen||'')+')'+(x.E&&x.rho?' E≈'+x.E+'GPa, ρ≈'+x.rho+'kg/m³ <button data-c="'+k+'">試算に使う</button>':'')+'</div>').join('');
 el.onclick=e=>{const b=e.target.closest('button[data-c]');if(!b)return;const x=show[+b.dataset.c];MATS.push({id:'cand'+b.dataset.c,name:x.title.slice(0,24),E:x.E,rho:x.rho,nu:0.3,eta:0.01,temp:true});matUI()}}).catch(()=>{})}
"""
rep("// ---- 実測データ取り込み・較正 ----", js + "\n// ---- 実測データ取り込み・較正 ----")

# --- HTML: 材質パネル ---
rep('<div class="grid">\n <div><h2>垂直面(仰角)',
    '<h2>ツィーター/スーパーツィーターの振動板材質 <span class="note">(単体・ハイブリッド(2種)・トライブリッド(3種)。比率は%。目安式であり実測の代わりではない)</span></h2>\n<div id="matp"></div>\n<div id="cand"></div>\n<div class="grid">\n <div><h2>垂直面(仰角)')

# buildの最後でmatUIも更新
rep(" run()}\nfunction run(){", " run();matUI()}\nfunction run(){")
p.write_text(s, encoding="utf-8")
print("patched")
