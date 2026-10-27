# 360-speaker

360度全方位 5WAY トールボーイスピーカーの設計案とWebシミュレーター(Rust→WASM)。
1本でも、2本SETでも、サラウンド用に複数本でも製造・販売する計画。

**公開シミュレーター: <https://easy-web.tokyo/360-speaker/>**(ブラウザで動作、Rust→WASM)

## ラインアップ案

- **WAY構成**: 5WAY / 4WAY / 3WAY / 2WAY / 1WAY
- **版**: 通常ウーファー版 / スーパーツィーター版 / サブウーファー版(各WAYで3種)
- **端子**: 左右とも「サブウーファー端子」と「サブウーファー用+WAY数ぶんの個別入力端子」
- **構成の選択肢**
  - A. アンプ内蔵: スピーカー側に、WAYごとの目盛り付きアナログボリューム + 左右連動マスター
  - B. **アンプ無し(パッシブ・WAY別端子)+ オプションのプリアンプ(別売)** ← 2026-10-25の追加案
    プリ側に、WAYごと(左右連動)の目盛り付きボリューム n 個 + 全体連動マスター。出力は外部パワーアンプへ。

## 中身

| パス | 内容 |
|---|---|
| [`docs/DESIGN.md`](docs/DESIGN.md) | 設計案(構造・ボリューム・端子・プリアンプ) |
| [`docs/RESEARCH.md`](docs/RESEARCH.md) | 調査・製品比較・ボリューム方式と採算の考察 |
| [`sim/`](sim/) | シミュレーター本体(Rust、依存ゼロ、WASM) |
| [`web/`](web/) | ブラウザ画面(`sim.wasm` 同梱)。`python -m http.server` で配信して開く |
| [`out/`](out/) | 書き出し(JPG・PDF) |

## ビルド

```
cd sim
cargo build --release --target wasm32-unknown-unknown
copy target\wasm32-unknown-unknown\release\speaker360_sim.wasm ..\web\sim.wasm
```

## 注意

シミュレーターは設計の方向性を見るための近似(ピストン指向性+円筒バッフルの影+LR4分割、水平面のみ)です。
実機の測定に代わるものではありません。コスト・採算の単価は推定の初期値で、見積りではありません。

## 現在の構造(第2版・2026-10-25)

- WAY1・2(超低音・低音): ユニットを**向き合わせ**、わずかな環状スリット(隙間)から360°放射。
- WAY3〜5(中・高・超高音): **下から上へ上向きに配置**し、ユニットの上から**下が尖り上が平らな円錐**を吊り下げて水平へ反射。
- 水平は円対称で全方位。課題は垂直指向性・スリット/円錐縁の風速(圧縮)。詳細は [`docs/DESIGN.md`](docs/DESIGN.md) の6章。

[特注・専用設計の製作先を探す(外部検索)](https://www.google.com/search?q=%E3%82%AA%E3%83%BC%E3%83%80%E3%83%BC%E3%83%A1%E3%82%A4%E3%83%89%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC&ie=UTF-8)

[FOSTEX公式ストア](https://store.fostex.jp/) ・ [FOSTEXユニット(公式ストア カテゴリ)](https://store.fostex.jp/view/category/ct76) ・ [FOSTEXユニット(Amazon.co.jp)](https://www.amazon.co.jp/s?k=FOSTEX%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88)

[JBL公式: 商品はどこで買えますか(JBL Japan)](https://support.jbl.com/jp/ja/howto/%E5%95%86%E5%93%81%E3%81%AF%E3%81%A9%E3%81%93%E3%81%A7%E8%B2%B7%E3%81%88%E3%81%BE%E3%81%99%E3%81%8B-jbl-japan/000035728.html)

[JBLユニットの購入先を探す(外部検索)](https://www.google.com/search?q=JBL%E3%80%80%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%E8%B3%BC%E5%85%A5&ie=UTF-8)

**ユニットを実際に通販しているサイト(2026-10-25 検索で確認できたもの)**

| サイト | 確認できたブランド | 備考 |
|---|---|---|
| [ヨドバシ.com(日本)](https://www.yodobashi.com/maker/0000008439/) | Scan-Speak | 掲載の多くが販売終了表示。在庫は要確認 |
| [楽天市場(日本)](https://www.rakuten.co.jp/category/568345/) | Scan-Speak・SB Acoustics・Dayton Audio(出品ショップによる) | ショップごとに在庫・価格が異なる |
| [RSコンポーネンツ(日本)](https://jp.rs-online.com/web/c/computing-peripherals/audio-video/speaker-drivers/) | Visaton等の汎用ユニット | 汎用品が中心 |
| [Falcon Acoustics(英国)](https://www.falconacoustics.co.uk/) | BlieSMa・SB Acoustics・Scan-Speak | 海外発送の可否・送料は要確認 |
| [Masori(ドイツ)](https://masori.de/en/) | Scan-Speak・SB Acoustics・Focal | 海外発送の可否・送料は要確認 |
| [Sound Imports(欧州)](https://www.soundimports.eu/) | SEAS・Radian・Dayton Audio | 海外発送の可否・送料は要確認 |
| [Willy's HiFi](https://willys-hifi.com/) | Scan-Speak | 海外発送の可否・送料は要確認 |
| [Toutlehautparleur(フランス)](https://en.toutlehautparleur.com/) | FOSTEX | 海外発送の可否・送料は要確認 |
| [Lautsprechershop.de(ドイツ)](https://lautsprechershop.de/hifi/fostex_en.htm) | FOSTEX | 海外発送の可否・送料は要確認 |
| [一品館(日本)](https://e.ippinkan.com/shopbrand/BC015400/) | TAD | ユーザー提供。TADのブランドページ |
| [コイズミ無線(日本)](https://shop.koizumi-musen.com/?mode=grp&gid=2727983) | TAD | ユーザー提供。TADのグループページ |
| [ジョーシンweb(日本)](https://joshinweb.jp/audio/5033.html?MKN=TAD) | TAD | ユーザー提供。TADのメーカー絞り込みページ |

Tang Band、Peerless/Vifa、Accuton、Monacor、Eton、Eminence、Celestion、Beyma、B&C Speakers、Tannoy、パイオニア、Focal(単品)は、今回の検索では取扱店を確認できませんでした(調べ不足の可能性があります。TADは追加の指摘で取扱店が見つかりました)(外部検索リンクを使ってください)。 在庫・価格・販売の可否は各サイトで必ず確認してください。

<!-- SHOPS:START -->
**毎朝の自動確認(最終 2026-10-27、サイト内検索で確認できたものだけ・自動更新)**

| サイト | 確認できたブランド |
|---|---|
| [楽天市場](https://www.rakuten.co.jp/) (日本) | [Celestion](https://search.rakuten.co.jp/search/mall/Celestion+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Dayton Audio](https://search.rakuten.co.jp/search/mall/Dayton%20Audio+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Eminence](https://search.rakuten.co.jp/search/mall/Eminence+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Eton](https://search.rakuten.co.jp/search/mall/Eton+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [FOSTEX](https://search.rakuten.co.jp/search/mall/FOSTEX+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Focal](https://search.rakuten.co.jp/search/mall/Focal+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [JBL](https://search.rakuten.co.jp/search/mall/JBL+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Peerless](https://search.rakuten.co.jp/search/mall/Peerless+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Radian](https://search.rakuten.co.jp/search/mall/Radian+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Scan-Speak](https://search.rakuten.co.jp/search/mall/Scan-Speak+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Tannoy](https://search.rakuten.co.jp/search/mall/Tannoy+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Visaton](https://search.rakuten.co.jp/search/mall/Visaton+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) |
| [Sound Imports](https://www.soundimports.eu/) (欧州) | [Accuton](https://www.soundimports.eu/en/search?q=Accuton) ・ [Beyma](https://www.soundimports.eu/en/search?q=Beyma) ・ [BlieSMa](https://www.soundimports.eu/en/search?q=BlieSMa) ・ [Dayton Audio](https://www.soundimports.eu/en/search?q=Dayton%20Audio) ・ [Eton](https://www.soundimports.eu/en/search?q=Eton) ・ [JBL](https://www.soundimports.eu/en/search?q=JBL) ・ [Monacor](https://www.soundimports.eu/en/search?q=Monacor) ・ [Peerless](https://www.soundimports.eu/en/search?q=Peerless) ・ [Radian](https://www.soundimports.eu/en/search?q=Radian) ・ [SB Acoustics](https://www.soundimports.eu/en/search?q=SB%20Acoustics) ・ [SEAS](https://www.soundimports.eu/en/search?q=SEAS) ・ [Scan-Speak](https://www.soundimports.eu/en/search?q=Scan-Speak) ・ [Tang Band](https://www.soundimports.eu/en/search?q=Tang%20Band) ・ [Visaton](https://www.soundimports.eu/en/search?q=Visaton) |
| [Willy's HiFi](https://willys-hifi.com/) (海外) | [Accuton](https://willys-hifi.com/search?q=Accuton) ・ [Dayton Audio](https://willys-hifi.com/search?q=Dayton%20Audio) ・ [Monacor](https://willys-hifi.com/search?q=Monacor) ・ [Peerless](https://willys-hifi.com/search?q=Peerless) ・ [SB Acoustics](https://willys-hifi.com/search?q=SB%20Acoustics) ・ [SEAS](https://willys-hifi.com/search?q=SEAS) |

確認できなかったサイト: ヨドバシ.com(接続できない(タイムアウト等))、RSコンポーネンツ(検索の仕組みを自動で見つけられない)、FOSTEX公式ストア(検索の仕組みを自動で見つけられない)、Falcon Acoustics(自動アクセスを拒否された(403)。回避はしない)、Masori(検索の仕組みを自動で見つけられない)、Toutlehautparleur(自動アクセスを拒否された(403)。回避はしない)、Lautsprechershop.de(検索の仕組みを自動で見つけられない)
<!-- SHOPS:END -->

**他ブランドのスピーカーユニット(外部検索リンク)**

- [Scan-Speakユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Scan-Speak%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [SB Acousticsユニットの購入先を探す(外部検索)](https://www.google.com/search?q=SB%20Acoustics%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [SEASユニットの購入先を探す(外部検索)](https://www.google.com/search?q=SEAS%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Dayton Audioユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Dayton%20Audio%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Tang Bandユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Tang%20Band%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Peerless/Vifaユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Peerless%20Vifa%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Accutonユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Accuton%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Visatonユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Visaton%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Monacorユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Monacor%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Etonユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Eton%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Eminenceユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Eminence%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Celestionユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Celestion%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Beymaユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Beyma%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [B&C Speakersユニットの購入先を探す(外部検索)](https://www.google.com/search?q=B%26C%20Speakers%20%E3%83%89%E3%83%A9%E3%82%A4%E3%83%90%E3%83%BC%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Radianユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Radian%20Audio%20%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Focalユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Focal%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E5%8D%98%E5%93%81%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [TADユニットの購入先を探す(外部検索)](https://www.google.com/search?q=TAD%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [Tannoyユニットの購入先を探す(外部検索)](https://www.google.com/search?q=Tannoy%20%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [パイオニアユニットの購入先を探す(外部検索)](https://www.google.com/search?q=%E3%83%91%E3%82%A4%E3%82%AA%E3%83%8B%E3%82%A2%20%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)
- [コイズミ無線・自作スピーカー用ユニットの購入先を探す(外部検索)](https://www.google.com/search?q=%E8%87%AA%E4%BD%9C%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%20%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%20%E8%B3%BC%E5%85%A5&ie=UTF-8)

## 構成バリエーション(シミュレーターで切替)
5WAY / 4WAY(ツィーター+スーパーツィーター統合ハイブリッド)/ 3WAY / 2WAY / **1WAY(ハイブリッドSTw単体=既存スピーカーの上に載せるトッピング用)**。
WAY3〜5の配置は「別々」「中音+高音を同軸」「3つ同軸」から選べる(同軸で縦のばらつきが約13dB→3〜6dB)。ユニット口径(WAY1〜3・高音域)と振動板材質(単体・ハイブリッド・トライブリッド)も選べる。

## 実測と新素材の自動収集
- 実測の手順書: [`docs/MEASUREMENT.md`](docs/MEASUREMENT.md)、試作マトリクス: `measurement/`。シミュレーターに実測CSVを取り込み、モデルを較正できる。
- 毎朝5:30(VPS)に `crawler/`(Rust)が arXiv・Crossref から振動板の新素材候補を集め、画面に「未検証」として表示する(材質表は自動では書き換えない)。設定: `deploy/install-crawler.sh`。

## 未了(ハードウェア・実物が必要なもの)
- 試作機の製作と実測(垂直・水平指向性、インピーダンス、風切り音、歪み)。モデルは近似で、較正は実測が揃ってから。
- ユニットのT/Sと材質値は仮定の代表値。実在ユニットの選定とデータシートでの置換。
- 自動収集した候補素材の数値検証(人手)。
- 同軸・統合ハイブリッドの実在ユニット確認、トッピング時の既存スピーカーとの干渉の聴感評価。
- 量産コスト・価格の実見積り、競合比較の追加(Ohm Walsh型・国内現行品)。
