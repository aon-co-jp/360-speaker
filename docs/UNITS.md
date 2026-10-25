# 実在ユニット候補(2026-10-25 調査)

英語・日本語・ドイツ語・中国語の検索で確認できた範囲。**数値は販売ページ・メーカー資料の記載で、実測ではない**。採用前に各社のデータシートで再確認すること(販売終了品を含む)。
調査で確認できなかったもの: 40kHz対応の**小口径(3インチ級)同軸ユニット**、ダイヤモンド振動板の同軸ユニット、CNF振動板の市販ツィーター(特許のみ確認)。

## 超高音・高音(ハイブリッドSTw候補、WAY4/5)
| 候補 | 方式・材質 | 公称の帯域・仕様 | 備考(出典) |
|---|---|---|---|
| Scan-Speak D3004/664000 | 1インチ ベリリウムドーム | 平坦に40kHz超、fs 500Hz、4Ω、91.5dB、有効径26mm、推奨分割2.5kHz | **メーカー販売終了**との販売店記載。代替に SB29BAC-C000-4 が挙がる([メーカーPDF](https://img.audiomania.ru/data/scanspeak_d3004664000_1.pdf)、[販売店](https://willys-hifi.com/products/scanspeak-d3004-664000-tweeter)) |
| BlieSMa T25B-6 | 25mm ベリリウムドーム | 推奨 2.2〜40kHz | [Falcon Acoustics](https://www.falconacoustics.co.uk/drive-units-1/bliesma-t25b-6.html) |
| BlieSMa T34B-4 | 34mm ベリリウムドーム | 推奨 1.3〜40kHz、4Ω、97.5dB、チタンボビン | [Falcon Acoustics](https://falconacoustics.co.uk/drive-units-1/bliesma-loudspeakers-drive-units/bliesma-t34b-4.html) |
| SB Acoustics Satori TW29BN-B / TW29BNWG-4 | ベリリウムドーム(WG版は導波管付き) | 40kHzまで再生可能と記載 | [Falcon Acoustics](https://www.falconacoustics.co.uk/tw29bnwg-4-satori-tweeter-by-sb-acoustics.html)、[Masori](https://masori.de/en/products/satori-tw29-bn-b-beryllium) |
| Focal Be逆ドーム(Utopia系) | ベリリウム逆ドーム | 1〜40kHz | [Focal](https://www.focal.com/technologies/the-beryllium-tweeter) |
| ムジカノート S-STW02(国内) | ベリリウム銅合金ハードドーム | 〜40kHz | 既存スピーカーに追加するスーパーツィーター。**1WAYトッピング版の競合参考**([検索結果](https://dime.jp/genre/496578/)) |
| FOSTEX PT20K(国内) | φ20mmドーム | 3〜32kHz | 40kHzには届かない([検索結果](https://joshinweb.jp/diy/35743/4589804900342.html)) |
| FYNE AUDIO 60kHzスーパーツィーター | 360度放射 | 60kHzまで | **360度放射の競合**、2025年の記事([AV Watch](https://av.watch.impress.co.jp/img/avw/docs/1579/231/html/st2_o.jpg.html)) |

## 中音・同軸の参考(WAY3、WAY3+4の同軸)
| 候補 | 内容 | 備考 |
|---|---|---|
| BlieSMa M74B-6 | 74mm ベリリウムドーム ミッド、推奨 440Hz〜8kHz | φ75mmミッド候補に近い([Falcon](https://www.falconacoustics.co.uk/bliesma-m74b-6.html)) |
| TAD Evolution One の同軸 | 35mmベリリウムツィーター+140mmマグネシウム中低音の同軸、28Hz〜100kHz(システム) | 同軸構造の実例だが大口径([Stereophile](https://www.stereophile.com/content/tad-evolution-one-loudspeaker-specifications)) |
| Radian 12CRF6430 他(同軸) | 40Hz〜30kHz クラス、ホーン/リボン併用 | 小口径ではない(出典: Sound Imports) |
| 市販の小口径同軸(KEF Uni-Q系など) | **今回の検索では確認できず** | 要追加調査: 小口径・40kHz対応の同軸は少ない見込み。なければ「中音に別ツィーターを中心に近接」または自社開発 |

## 振動板材質について
- ベリリウム: 40kHzまで伸ばせる実例が多い(上表)。加工時の粉塵が有毒で、調達・製造管理が必要。
- ダイヤモンド: 今回の検索では具体的な製品の数値が確認できなかった。
- CNF(セルロースナノファイバー): 特許は複数([US11979724](https://patents.google.com/patent/US11979724)、[US9521490](https://patents.google.com/patent/US9521490)等)で、**純CNFは再生帯域が狭くなりやすく、他の繊維や層との複合が検討されている**。市販ツィーターの確認はできなかった。
- ハイブリッド/トライブリッドは、シミュレーターの材質混合で比較できる(実測が必要)。

## 次の判断
1. **40kHz対応を満たすのはベリリウム系が現実的**(T25B-6、T34B-4、Satori、Be逆ドーム)。ハイブリッドSTw(WAY4+5統合)は、推奨 2〜40kHz級のベリリウムドーム1個で、ツィーターとスーパーの両方を兼ねる案が最短。
2. **中音+高音の同軸**は、既製品がなければ「ベリリウムドームを中音φ75の中心近くに置く」自社構造を試作で確認する(干渉は実機測定が必要)。
3. 価格・在庫・販売終了の状況はユニットごとに要確認。購入前にメーカーの最新データシートを取得する。
