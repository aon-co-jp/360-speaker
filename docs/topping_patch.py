"""web/index.html の修正パッチ(一回限り):
1) 合成サンプルの文字列リテラル中の実改行を \\n に直す
2) 1WAYハイブリッドSTwを「既存スピーカーの上にトッピング」するモデル(既存スピーカーのツィーター+トッピングの2源)に対応
"""
import pathlib, re
p = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"
s = p.read_text(encoding="utf-8")

# 1) 実改行の修復
i = s.index("$('mdemo').onclick")
j = s.index("$('mfit').onclick=fitModel;")
seg = s[i:j]
seg = seg.replace("ノイズ)\n';", "ノイズ)\\n';").replace("+'\t'+", "+'\\t'+").replace(".toFixed(2)+'\t0\n'}", ".toFixed(2)+'\\t0\\n'}")
s = s[:i] + seg + s[j:]

def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

# 2) トッピング入力欄
rep(' <label>1WAYハイブリッドSTw 入力ハイパス Hz <input id="hp" type="number" value="3500" style="width:4.5em"></label>',
    ' <label>1WAYハイブリッドSTw 入力ハイパス Hz <input id="hp" type="number" value="10000" style="width:4.5em"></label>\n'
    ' <label>(トッピング時)既存ツィーターとの高低差 mm <input id="dz" type="number" value="150" style="width:4.5em"></label>\n'
    ' <label>既存スピーカーの高域上限 Hz <input id="exh" type="number" value="20000" style="width:5em"></label>')
rep("['ord','shape','taper','sp','cx','hp'].forEach", "['ord','shape','taper','sp','cx','hp','dz','exh'].forEach")
rep("function FMIN(){return $('ways').value=='1h'?(+$('hp').value||3500)*1.2:100}", "function FMIN(){return $('ways').value=='1h'?(+$('hp').value||10000)*1.2:100}")

# run(): 1h は既存スピーカー(way0)+トッピング(way1)
rep("for(let i=0;i<4;i++)m[20+i]=xo[i]||1e5;\n dv.forEach((d,i)=>{const p=d.p;let H,phi0,txt;const w=[];",
    "const top1=$('ways').value=='1h',off=top1?1:0;for(let i=0;i<4;i++)m[20+i]=xo[i]||1e5;if(top1)m[20]=+$('hp').value||10000;\n"
    " if(top1){vin[0]=(dv[0].z-(+$('dz').value||150))/1000;vin[1]=0.025;vin[2]=0;vin[3]=0;vin[4]=0;vin[5]=0;}\n"
    " dv.forEach((d,i0)=>{const i=i0+off;const p=d.p;let H,phi0,txt;const w=[];")
# 以降の dv[...] 参照・i を使った箇所の整合(トッピング時は i=1)
rep("const zr=dv.length>2?dv[2].z:0,cx=+$('cx').value;let zz=(d.k=='r'&&i>2)?zr+(d.z-zr)*(+$('sp').value||1):d.z;if(i==3&&cx>=1)zz=zr;if(i==4&&cx==1)zz=zr+(d.z-dv[3].z)*(+$('sp').value||1);if(i==4&&cx==2)zz=zr;vin[i*8]=(zz+cal.dz[i])/1000;",
    "const zr=dv.length>2?dv[2].z:0,cx=+$('cx').value;let zz=(d.k=='r'&&i0>2)?zr+(d.z-zr)*(+$('sp').value||1):d.z;if(i0==3&&cx>=1)zz=zr;if(i0==4&&cx==1)zz=zr+(d.z-dv[3].z)*(+$('sp').value||1);if(i0==4&&cx==2)zz=zr;vin[i*8]=(zz+cal.dz[i0])/1000;")
rep("$('in'+i).innerHTML='<br>'+txt;});", "$('in'+i0).innerHTML='<br>'+txt;});")
rep("vin[42]=$('ways').value=='1h'?(+$('hp').value||0):0;const len=W.vertical2(n,NF,NE,FLO,FHI);",
    "vin[42]=0;vin[43]=top1?(+$('exh').value||20000):0;const len=W.vertical2(n+off,NF,NE,FLO,FHI);")
p.write_text(s, encoding="utf-8")
print("patched")
