"""web/index.html にFOSTEXユニット選択・購入リスト(購入先リンク)を追加する一回限りのパッチ。"""
import pathlib
p = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
s = p.read_text(encoding="utf-8")
if 'id="fx"' in s:
    print("already patched"); raise SystemExit

html = """<h2>FOSTEXユニットの選択と購入リスト <span class="note">(数値は販売店・DB記載。購入は公式/正規取扱店。このページは決済を扱いません)</span></h2>
<div id="fx"></div>
<div class="row"><button id="fxcopy">購入リスト(CSV)をコピー</button> <span class="note" id="fxgate"></span></div>
<pre class="note" id="fxlist" style="white-space:pre-wrap"></pre>
"""
anchor = '<div id="matp"></div>'
assert anchor in s
s = s.replace(anchor, html + anchor, 1)

js = r"""
// ---- FOSTEXユニット選択・購入リスト ----
var FX=[];
function roleOf(d,i){if(d.hyb)return 'hybrid';if(d.k=='s')return d.D>=250||i==0&&(dv.length>2)?'sub':'bass';if(d.t=='cone')return 'mid';return 'high'}
function fxUI(){const box=$('fx');if(!box||!FX.length)return;box.innerHTML='';
 dv.forEach((d,i)=>{const role=roleOf(d,i),opts=FX.filter(u=>u.roles.includes(role)||(role=='sub'&&u.roles.includes('bass')));
  const div=document.createElement('div');div.className='way';div.dataset.i=i;
  const sel=d.fx||'';const u=FX.find(x=>x.id==sel);
  div.innerHTML='<b>'+d.n.replace(/\(.*$/,'')+'</b><span>FOSTEX<select data-f="1"><option value="">(未選択)</option>'+opts.map(x=>'<option value="'+x.id+'"'+(x.id==sel?' selected':'')+'>'+x.name.replace('FOSTEX ','')+'</option>').join('')+'</select>'+
   (u?' <span class="note">'+(u.fs?'Fs '+u.fs+'Hz / Qts '+u.qts+' / Vas '+u.vas+'L':'')+(u.xmax?' / Xmax '+u.xmax+'mm':'')+(u.note?' / '+u.note:'')+' ・ <a href="'+u.src+'" target="_blank" rel="noopener noreferrer">出典</a> ・ <a href="https://www.fostex.jp/?s='+encodeURIComponent(u.id)+'" target="_blank" rel="noopener noreferrer">FOSTEX公式で検索</a></span>':(opts.length?'':'<span class="note"> この用途のFOSTEX候補なし(docs/UNITS.md参照)</span>'))+'</span><span></span>';
  box.appendChild(div)});
 box.onchange=e=>{const t=e.target;if(!t.dataset.f)return;const i=+t.closest('.way').dataset.i,d=dv[i],u=FX.find(x=>x.id==t.value);d.fx=t.value;
  if(u&&u.D){const sz=SIZES[d.sk],near=sz.reduce((a,b)=>Math.abs(b-u.D)<Math.abs(a-u.D)?b:a);setSize(d,i,near);if(u.xmax)d.p.xm=u.xmax;const row=$('ctl').children[i];const sl=row&&row.querySelector('select[data-d]');if(sl)sl.value=near;build2(i)}
  if(u&&u.fs&&i<3){const k=Math.min(i,2);DRV[k]={...DRV[k],fs:u.fs,q:u.qts,v:u.vas};if(+$('ew').value==k)eload()}
  fxUI();fxList();run()};fxList()}
function fxList(){const rows=[['WAY','FOSTEX型番','数量(1本)','数量(左右SET)','公式検索URL']];let any=false;
 dv.forEach((d,i)=>{const u=FX.find(x=>x.id==d.fx);if(!u)return;any=true;const q=(d.k=='s')?2:1;rows.push([d.n.replace(/\(.*$/,''),u.id,q,q*2,'https://www.fostex.jp/?s='+encodeURIComponent(u.id)])});
 $('fxlist').textContent=any?rows.map(r=>r.join(',')).join('\n'):'FOSTEXユニットを選ぶと、購入リストがここに出ます。';
 const sumTxt=$('sum').textContent,m=sumTxt.match(/最悪値: ([\d.]+) dB/),v=m?+m[1]:NaN;
 $('fxgate').textContent=!any?'':(v<=6?'✓ 縦のばらつき '+v.toFixed(1)+'dB: 目標(6dB以下)を満たす。購入リストを作成できます。':'縦のばらつき '+(isNaN(v)?'?':v.toFixed(1))+'dB: 目標(6dB以下)には未達。同軸配置などで改善してから購入を検討してください(購入リスト自体は作成可)。')}
$('fxcopy').onclick=()=>{navigator.clipboard&&navigator.clipboard.writeText($('fxlist').textContent)};
fetch('fostex.json').then(r=>r.json()).then(j=>{FX=j.units;fxUI()}).catch(()=>{});
"""
mark = "// ---- 実測データ取り込み・較正 ----"
assert mark in s
s = s.replace(mark, js + "\n" + mark, 1)
# 構成変更・口径変更・再計算の都度、購入リストとゲートを更新
for a, b in [("function build(){", "function build(){setTimeout(()=>{if(typeof fxUI=='function')fxUI()},0);"),
             (" cost();if(meas&&!draw.fit)compare()}", " cost();if(meas&&!draw.fit)compare();if(typeof fxList=='function')fxList()}")]:
    assert a in s, a
    s = s.replace(a, b, 1)
p.write_text(s, encoding="utf-8")
print("patched")
