const XO={5:[60,600,4200,13200],4:[150,1000,6000],3:[300,3000],2:[2500],1:[]};
// 下→上。k: s=対向2個+隙間(スリット) / r=上向き+吊り下げ円錐
const WAYD=[{n:'WAY1 超低音',k:'s',z:260,p:{rt:80,g:20,rm:190,sd:220,xm:10,cnt:2},v:0},
 {n:'WAY2 低音',k:'s',z:606,p:{rt:55,g:12,rm:100,sd:85,xm:5,cnt:2},v:0},
 {n:'WAY3 中音',k:'r',z:850,p:{a:37,sd:44,xm:3,al:45,gap:14,rc:70},v:0},
 {n:'WAY4 高音',k:'r',z:1020,p:{a:12.5,sd:4.9,xm:.5,al:45,gap:6,rc:35},v:0},
 {n:'WAY5 超高音',k:'r',z:1105,p:{a:9.5,sd:2.8,xm:.3,al:45,gap:4,rc:25},v:0}];
const NF=200,NE=121,FLO=20,FHI=40000;let W,xo=[],data,n=5,dv=[];
function lab(t,k,v,w){return t+'<input data-k="'+k+'" type="number" step="any" value="'+v+'" style="width:'+(w||4.5)+'em">'}
function build(){n=+$('ways').value;xo=XO[n].slice();dv=WAYD.slice(0,n).map(d=>JSON.parse(JSON.stringify(d)));
 const c=$('ctl');c.innerHTML='';
 dv.forEach((d,i)=>{const r=document.createElement('div');r.className='way';r.dataset.i=i;
  const p=d.p;let h='<b>'+d.n+'</b><span>'+(d.k=='s'?'<i>対向2個+隙間</i> ':'<i>上向き+吊り円錐</i> ')+lab(' 高さz mm','z',d.z,5);
  h+=d.k=='s'?lab(' スロート半径mm','rt',p.rt)+lab(' 隙間mm','g',p.g)+lab(' 出口半径mm','rm',p.rm)+lab(' 1個Sd cm²','sd',p.sd)+lab(' Xmax mm','xm',p.xm):
   lab(' ユニット半径mm','a',p.a)+lab(' 円錐半頂角°','al',p.al)+lab(' 縁の隙間mm','gap',p.gap)+lab(' 円錐半径mm','rc',p.rc)+lab(' Sd cm²','sd',p.sd)+lab(' Xmax mm','xm',p.xm);
  if(i<dv.length-1)h+=' 分割Hz<input data-x="'+i+'" type="number" value="'+xo[i]+'" style="width:5em">';
  h+='<br>音量<input data-v="1" type="range" min="-20" max="6" step="0.5" value="'+d.v+'"><span class="note" id="in'+i+'"></span></span><span id="vv'+i+'">'+d.v+' dB</span>';
  r.innerHTML=h;c.appendChild(r)});
 c.oninput=e=>{const t=e.target,i=+t.closest('.way').dataset.i,d=dv[i];if(t.dataset.v){d.v=+t.value;$('vv'+i).textContent=t.value+' dB'}
  else if(t.dataset.x!=null)xo[t.dataset.x]=+t.value;else if(t.dataset.k=='z')d.z=+t.value;else d.p[t.dataset.k]=+t.value;run()};
 run()}
function run(){if(!W)return;const f0=+$('flow').value||40,ms=+$('master').value;
 const vin=new Float64Array(W.memory.buffer,W.v_in_ptr(),20),m=new Float64Array(W.memory.buffer,W.in_ptr(),24);
 for(let i=0;i<4;i++)m[20+i]=xo[i]||1e5;
 dv.forEach((d,i)=>{const p=d.p;let H,phi0,txt;const w=[];
  if(d.k=='s'){const si=new Float64Array(W.memory.buffer,W.slot_in_ptr(),9);si.set([p.cnt,p.sd,p.xm,p.rt,p.g,p.rm,p.g*1.5,f0,20]);W.slot();const o=new Float64Array(W.memory.buffer,W.slot_out_ptr(),8).slice();
   H=p.g*1.5/1000;phi0=0;
   txt='スリット面積 '+o[0].toFixed(0)+'cm² / 圧縮比 '+o[1].toFixed(1)+' / 風速(Xmax,'+f0+'Hz) '+o[2].toFixed(0)+'m/s / 前室共振 '+Math.round(o[4])+'Hz / 最大SPL '+o[5].toFixed(0)+'dB'+(o[7]?'(隙間で制限)':'');
   if(o[2]>20)w.push('風速>20m/s: 隙間を広げる/出口をフレア/Xmax制限');if(o[4]<(xo[i]||1e4)*2)w.push('前室共振が分割に近い');if(p.g<4)w.push('隙間<4mm: 粘性損失・ガタ付き')}
  else{const ri=new Float64Array(W.memory.buffer,W.refl_in_ptr(),8);ri.set([p.a,p.sd,p.xm,p.al,p.gap,p.rc,Math.max(f0,xo[i-1]||600),20]);W.reflector();const o=new Float64Array(W.memory.buffer,W.refl_out_ptr(),8).slice();
   H=Math.max(o[4],4)/1000;phi0=o[0];
   txt='放射仰角 '+o[0].toFixed(0)+'° / 出口面積 '+o[1].toFixed(1)+'cm² / 圧縮比 '+o[2].toFixed(2)+' / 風速 '+o[3].toFixed(0)+'m/s / 円錐高さ '+o[5].toFixed(0)+'mm / 制御下限 '+Math.round(o[6])+'Hz';
   if(o[2]>1.6)w.push('圧縮比大: 縁の隙間を広げる');if(Math.abs(o[0])>8)w.push('半頂角45°で水平放射(今は'+o[0].toFixed(0)+'°)');if(o[6]>(xo[i-1]||0))w.push('円錐半径が小さく、帯域下限で拡散制御が効かない')}
  if(w.length)txt+=' ⚠ '+w.join(' / ');
  vin[i*4]=d.z/1000;vin[i*4+1]=H;vin[i*4+2]=phi0;vin[i*4+3]=d.v+ms;$('in'+i).innerHTML='<br>'+txt;});
 const len=W.vertical(n,NF,NE,FLO,FHI);data=new Float64Array(W.memory.buffer,W.v_out_ptr(),len).slice();draw()}
function col(v){const t=Math.max(0,Math.min(1,(v+40)/50));return 'hsl('+(240-240*t)+',80%,'+(25+30*t)+'%)'}
function draw(){const fg=getComputedStyle(document.body).color;
 let c=$('hm').getContext('2d'),w=600,h=320;for(let f=0;f<NF;f++)for(let a=0;a<NE;a++){c.fillStyle=col(data[f*NE+a]);c.fillRect(f*w/NF,(NE-1-a)*h/NE,w/NF+1,h/NE+1)}
 c.fillStyle='#fff';c.font='11px sans-serif';[100,1000,10000].forEach(F=>{const x=Math.log(F/FLO)/Math.log(FHI/FLO)*w;c.fillText(F>=1000?F/1000+'k':F,x,h-3)});c.fillText('+90°(上)',2,10);c.fillText('0°',2,h/2);c.fillText('-90°',2,h-14);
 const fi=+$('fs').value;$('pf').textContent=Math.round(FLO*Math.pow(FHI/FLO,fi/(NF-1)))+' Hz';
 c=$('po').getContext('2d');c.clearRect(0,0,320,320);c.strokeStyle='#8888';c.lineWidth=1;[10,20,30,40].forEach(r=>{c.beginPath();c.arc(160,160,r*3.6,0,7);c.stroke()});c.beginPath();c.moveTo(160,0);c.lineTo(160,320);c.moveTo(0,160);c.lineTo(320,160);c.stroke();
 c.strokeStyle='#2a6df4';c.lineWidth=2;c.beginPath();for(let a=0;a<NE;a++){const v=data[fi*NE+a];const r=Math.max(0,v+40)*3.6;const el=(-90+180*a/(NE-1))*Math.PI/180;const x=160+r*Math.cos(el),y=160-r*Math.sin(el);a?c.lineTo(x,y):c.moveTo(x,y)}c.stroke();
 c.fillStyle=fg;c.fillText('右=水平方向(全方位で同一) / 上=真上',4,314);
 c=$('fr').getContext('2d');c.clearRect(0,0,900,240);c.lineWidth=1.5;let worst=0,wf=0;
 const y=v=>240-(v+50)/70*240;c.strokeStyle='#8888';c.fillStyle=fg;for(let d=-40;d<=10;d+=10){c.beginPath();c.moveTo(0,y(d));c.lineTo(900,y(d));c.stroke();c.fillText(d+'dB',2,y(d)-2)}
 const e0=Math.round((NE-1)/2),lo=Math.round((NE-1)*(90-30)/180),hi=Math.round((NE-1)*(90+30)/180);
 c.strokeStyle='#2a6df4';c.beginPath();for(let f=0;f<NF;f++){const x=f*900/NF;f?c.lineTo(x,y(data[f*NE+e0])):c.moveTo(x,y(data[f*NE+e0]))}c.stroke();
 c.strokeStyle='#e8851a';c.beginPath();for(let f=0;f<NF;f++){let a=-99,b=99;for(let k=lo;k<=hi;k++){a=Math.max(a,data[f*NE+k]);b=Math.min(b,data[f*NE+k])}const dev=a-b;const fr=FLO*Math.pow(FHI/FLO,f/(NF-1));if(fr>=100&&fr<=12000&&dev>worst){worst=dev;wf=fr}const x=f*900/NF,yy=240-Math.min(dev,30)/30*240;f?c.lineTo(x,yy):c.moveTo(x,yy)}c.stroke();
 $('sum').textContent='100Hz〜12kHzの仰角±30°(聴く高さ)内の偏差の最悪値: '+worst.toFixed(1)+' dB @ '+Math.round(wf)+' Hz。小さいほど縦方向が均一。(橙の縦軸は0〜30dB。水平方向は円対称で全方位同一)';
 cost()}
const VOL={'アナログ ステップ式(目盛り付きロータリー)':1800,'モーター付き可変抵抗(リモコン対応)':1500,'デジタル(エンコーダ+ボリュームIC/DSP)':400,'ハイブリッド(エンコーダ+アナログ減衰IC/リレー、目盛りリング付き) 推奨案':1100};
