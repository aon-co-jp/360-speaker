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
**毎朝の自動確認(最終 2026-11-14、サイト内検索で確認できたものだけ・自動更新)**

| サイト | 確認できたブランド |
|---|---|
| [楽天市場](https://www.rakuten.co.jp/) (日本) | [Celestion](https://search.rakuten.co.jp/search/mall/Celestion+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Dayton Audio](https://search.rakuten.co.jp/search/mall/Dayton%20Audio+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Eminence](https://search.rakuten.co.jp/search/mall/Eminence+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Eton](https://search.rakuten.co.jp/search/mall/Eton+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [FOSTEX](https://search.rakuten.co.jp/search/mall/FOSTEX+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Focal](https://search.rakuten.co.jp/search/mall/Focal+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [JBL](https://search.rakuten.co.jp/search/mall/JBL+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Peerless](https://search.rakuten.co.jp/search/mall/Peerless+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Radian](https://search.rakuten.co.jp/search/mall/Radian+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Scan-Speak](https://search.rakuten.co.jp/search/mall/Scan-Speak+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Tannoy](https://search.rakuten.co.jp/search/mall/Tannoy+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) ・ [Visaton](https://search.rakuten.co.jp/search/mall/Visaton+%E3%82%B9%E3%83%94%E3%83%BC%E3%82%AB%E3%83%BC%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88/) |
| [Sound Imports](https://www.soundimports.eu/) (欧州) | [Accuton](https://www.soundimports.eu/en/search?q=Accuton) ・ [Beyma](https://www.soundimports.eu/en/search?q=Beyma) ・ [BlieSMa](https://www.soundimports.eu/en/search?q=BlieSMa) ・ [Dayton Audio](https://www.soundimports.eu/en/search?q=Dayton%20Audio) ・ [Eton](https://www.soundimports.eu/en/search?q=Eton) ・ [JBL](https://www.soundimports.eu/en/search?q=JBL) ・ [Monacor](https://www.soundimports.eu/en/search?q=Monacor) ・ [Peerless](https://www.soundimports.eu/en/search?q=Peerless) ・ [Radian](https://www.soundimports.eu/en/search?q=Radian) ・ [SB Acoustics](https://www.soundimports.eu/en/search?q=SB%20Acoustics) ・ [SEAS](https://www.soundimports.eu/en/search?q=SEAS) ・ [Scan-Speak](https://www.soundimports.eu/en/search?q=Scan-Speak) ・ [Tang Band](https://www.soundimports.eu/en/search?q=Tang%20Band) ・ [Visaton](https://www.soundimports.eu/en/search?q=Visaton) |
| [Willy's HiFi](https://willys-hifi.com/) (海外) | [Accuton](https://willys-hifi.com/search?q=Accuton) ・ [Dayton Audio](https://willys-hifi.com/search?q=Dayton%20Audio) ・ [Monacor](https://willys-hifi.com/search?q=Monacor) ・ [Peerless](https://willys-hifi.com/search?q=Peerless) ・ [SB Acoustics](https://willys-hifi.com/search?q=SB%20Acoustics) ・ [SEAS](https://willys-hifi.com/search?q=SEAS) |

確認できなかったサイト: ヨドバシ.com(接続できない(タイムアウト等))、RSコンポーネンツ(検索の仕組みを自動で見つけられない)、FOSTEX公式ストア(検索の仕組みを自動で見つけられない)、Falcon Acoustics(自動アクセスを拒否された(403)。回避はしない)、Masori(接続できない(タイムアウト等))、Toutlehautparleur(自動アクセスを拒否された(403)。回避はしない)、Lautsprechershop.de(検索の仕組みを自動で見つけられない)
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

## API 方針: REST 全廃・gRPC / Connect へ (2026-11-04)

### 日本語
- **REST は全廃する。新しい API は REST で作らない。** ブラウザや `curl` から呼ぶ API は **Connect の単純呼び出し**(`POST /<パッケージ>.<Service>/<Method>`、`content-type: application/json`、本文は JSON)、サービス間は **gRPC / gRPC-web**(RPoem の管理API `open_runo.admin.v1.Admin` と同じ流儀)。ストリーミングは、必要になってから。
- **既存の REST は、触るときに順に移す。** 移したら旧 REST の経路は消す。移行が終わるまで残るが、**新規には追加しない**。
- **JSON は RS-JSON に統一**する(読み込みは `from_str_secure` / `parse_secure` でサイズ・深さ・重複キーの上限つき、書き出しは `rust_json::fast`)。ブラウザの WASM に `prost` は入れない(サイズが増えるため)。
- **例外(自分たちの API ではなく、相手の規格が決めているもの)**: ACME、OAuth/OIDC のコールバック、第三者(GitHub など)からの Webhook、ヘルスチェック、静的ファイル配信、OTLP など。これらは規格どおりの HTTP を受ける。
- 参考実装: `RPoem`(`open_runo.admin.v1.Admin`)、`open-easy-web`(`server/src/connect.rs`、`proto/open_easy_web/admin/v1/admin.proto`)。
- ※ このリポジトリのコードが既に方針どおりかどうかは、各リポジトリの現状による。この節は方針の記録であり、コードの変更を意味しない。

### English
- **REST is being abolished. New APIs are not built as REST.** APIs called from browsers or `curl` use **Connect unary calls** (`POST /<package>.<Service>/<Method>`, `content-type: application/json`, JSON body); service-to-service calls use **gRPC / gRPC-web** (the same style as RPoem's admin API `open_runo.admin.v1.Admin`). Streaming only when it is actually needed.
- **Existing REST endpoints are migrated one by one, when they are touched.** The old REST route is removed once migrated. Until migration is finished they remain, but **no new ones are added**.
- **JSON is unified on RS-JSON**: reading with `from_str_secure` / `parse_secure` (size, depth and duplicate-key limits), writing with `rust_json::fast`. `prost` is not put into browser WASM (it would grow the binary).
- **Exceptions (shapes dictated by someone else's standard, not our own API)**: ACME, OAuth/OIDC callbacks, webhooks from third parties (e.g. GitHub), health checks, static file serving, OTLP, and so on. These accept plain HTTP as the standard requires.
- Reference implementations: `RPoem` (`open_runo.admin.v1.Admin`) and `open-easy-web` (`server/src/connect.rs`, `proto/open_easy_web/admin/v1/admin.proto`).
- Note: whether the code in a given repository already follows this policy depends on that repository. This section records the policy; it does not mean the code has been changed.

### Deutsch (KI-Übersetzung, redaktionell überarbeitet; noch nicht von Muttersprachlern geprüft)
- **REST wird vollständig abgeschafft; neue APIs entstehen nicht mehr als REST.** APIs, die aus dem Browser oder per `curl` aufgerufen werden, verwenden **unäre Connect-Aufrufe** (`POST /<Paket>.<Service>/<Methode>`, `content-type: application/json`, JSON-Body). Zwischen Diensten kommen **gRPC bzw. gRPC-web** zum Einsatz, im selben Stil wie die Admin-API von RPoem (`open_runo.admin.v1.Admin`). Streaming wird erst ergänzt, wenn es tatsächlich gebraucht wird.
- **Bestehende REST-Endpunkte werden schrittweise umgestellt, und zwar immer dann, wenn man ohnehin an ihnen arbeitet.** Sobald ein Endpunkt umgestellt ist, wird die alte REST-Route entfernt. Bis zum Abschluss der Migration bleiben die übrigen bestehen, es werden aber **keine neuen mehr hinzugefügt**.
- **JSON wird einheitlich über RS-JSON verarbeitet**: Gelesen wird mit `from_str_secure` bzw. `parse_secure` (mit Obergrenzen für Größe, Verschachtelungstiefe und doppelte Schlüssel), geschrieben mit `rust_json::fast`. `prost` wird nicht in das Browser-WASM aufgenommen, da es die Datei vergrößern würde.
- **Ausnahmen (Schnittstellen, deren Form ein fremder Standard vorgibt und die nicht zu unserer eigenen API gehören)**: ACME, OAuth/OIDC-Callbacks, Webhooks von Drittanbietern (z. B. GitHub), Health-Checks, die Auslieferung statischer Dateien, OTLP und Ähnliches. Diese nehmen, wie vom jeweiligen Standard verlangt, gewöhnliches HTTP entgegen.
- Referenzimplementierungen: `RPoem` (`open_runo.admin.v1.Admin`) und `open-easy-web` (`server/src/connect.rs`, `proto/open_easy_web/admin/v1/admin.proto`).
- Hinweis: Ob der Code eines einzelnen Repositorys diese Richtlinie bereits erfüllt, hängt vom jeweiligen Repository ab. Dieser Abschnitt dokumentiert lediglich die Richtlinie; er besagt nicht, dass der Code schon angepasst wurde.

### Русский (перевод выполнен с помощью ИИ и отредактирован; носителями языка пока не проверен)
- **От REST мы полностью отказываемся; новые API больше не создаются в стиле REST.** API, к которым обращаются из браузера или через `curl`, используют **унарные вызовы Connect** (`POST /<пакет>.<Service>/<Method>`, `content-type: application/json`, тело запроса — JSON). Для взаимодействия между сервисами применяются **gRPC и gRPC-web** — в том же стиле, что и административный API RPoem (`open_runo.admin.v1.Admin`). Потоковая передача данных добавляется лишь тогда, когда в ней действительно возникает необходимость.
- **Существующие REST-эндпоинты переводятся поэтапно — по мере того, как с ними приходится работать.** После перевода старый REST-маршрут удаляется. Пока миграция не завершена, оставшиеся эндпоинты сохраняются, но **новые не добавляются**.
- **Работа с JSON унифицирована на основе RS-JSON**: чтение — через `from_str_secure` или `parse_secure` (с ограничениями на размер, глубину вложенности и повторяющиеся ключи), запись — через `rust_json::fast`. `prost` в браузерный WASM не включается, поскольку это увеличило бы размер файла.
- **Исключения (интерфейсы, форму которых определяет чужой стандарт, а не наш собственный API)**: ACME, обратные вызовы OAuth/OIDC, вебхуки сторонних сервисов (например, GitHub), проверки работоспособности, раздача статических файлов, OTLP и тому подобное. Такие интерфейсы принимают обычный HTTP, как того требует соответствующий стандарт.
- Эталонные реализации: `RPoem` (`open_runo.admin.v1.Admin`) и `open-easy-web` (`server/src/connect.rs`, `proto/open_easy_web/admin/v1/admin.proto`).
- Примечание: соответствует ли код конкретного репозитория этой политике, зависит от самого репозитория. Данный раздел лишь фиксирует политику и не означает, что код уже изменён.

## API 方針の補足: 用語の整理と使い分け (2026-11-04)

### 日本語
**1つに統一するものではなく、別の層の話です。** 「REST の代わり」になるのは Connect・gRPC・GraphQL だけで、WASM は画面を作る技術です。

| 用語 | 何か | REST の代わりか |
|---|---|---|
| REST | URL と HTTP メソッドで操作を表す API の作り方 | 全廃する側 |
| **Connect** | `POST /サービス名/メソッド名` に JSON を送る形式。`curl` でもブラウザの `fetch` でも呼べる | はい(**採用**) |
| **gRPC** | 同じ「サービス/メソッド」の考え方を、バイナリ(protobuf)と HTTP/2 で行う形式。速く、ストリーミングも得意 | はい(**サービス同士に採用**) |
| gRPC-web | gRPC のブラウザ向けの変形版 | はい(必要なら) |
| GraphQL | 欲しい項目を問い合わせる形式 | 一部だけ(**問い合わせ(読み取り)専用**) |
| WASM | Rust をブラウザの中で動かす仕組み | いいえ(画面を作る技術) |

- **ブラウザの画面や `curl` から呼ぶ API は Connect**(POST、JSON を RS-JSON で読み書き)。ブラウザの WASM は素の gRPC を話せず、Connect なら `fetch` のままで、`prost` を足さずに済む(画面のサイズも増えない)。
- **サービス同士の通信(サーバー間、重い処理、ストリーミング)は gRPC。** 多くは Connect で足りるので、ストリーミングが必要になった所だけ gRPC に上げる。
- **GraphQL は、まとめて問い合わせたいときの読み取り専用。** 書き込み(操作)には使わない。
- **WASM は画面を作る技術として、そのまま使う。** 画面から呼ぶ API が Connect になっただけ。
- 外部の規格が形を決めるもの(ACME、OAuth のコールバック、第三者の Webhook、ヘルスチェック、静的ファイル、OTLP)は、規格どおりの HTTP のまま。
- **迷ったら Connect。**

### English
**These are not alternatives to unify; they sit at different layers.** Only Connect, gRPC and GraphQL can replace REST; WASM is a way to build the UI.

| Term | What it is | Replaces REST? |
|---|---|---|
| REST | API style that expresses operations through URLs and HTTP methods | The thing being abolished |
| **Connect** | `POST /Service/Method` with a JSON body; callable from `curl` and from a browser `fetch` | Yes (**adopted**) |
| **gRPC** | The same service/method idea over binary (protobuf) and HTTP/2; fast, good at streaming | Yes (**for service-to-service**) |
| gRPC-web | A browser-friendly variant of gRPC | Yes (if needed) |
| GraphQL | A query language: ask for exactly the fields you want | Partly (**read-only queries**) |
| WASM | Runs Rust inside the browser | No (a UI technology) |

- **APIs called from browser screens or `curl` use Connect** (POST, JSON read and written with RS-JSON). Browser WASM cannot speak plain gRPC; with Connect it stays a `fetch`, and `prost` is not needed (the binary does not grow).
- **Service-to-service calls (server to server, heavy work, streaming) use gRPC.** Connect is enough in most places; move a call to gRPC only where streaming is actually needed.
- **GraphQL is read-only**, for queries that gather several pieces of data. It is not used for writes (operations).
- **WASM stays as the way to build the UI.** The API it calls simply became Connect.
- Interfaces whose shape an outside standard dictates (ACME, OAuth callbacks, third-party webhooks, health checks, static files, OTLP) stay plain HTTP.
- **When in doubt, use Connect.**

### Deutsch (KI-Übersetzung, sprachlich überarbeitet; noch nicht von Muttersprachlern geprüft)
**Es geht nicht darum, eine einzige Technik auszuwählen – die Begriffe liegen auf unterschiedlichen Ebenen.** Als Ersatz für REST kommen nur Connect, gRPC und GraphQL in Frage; WASM dagegen ist eine Technik, mit der die Benutzeroberfläche gebaut wird.

| Begriff | Was ist das? | Ersatz für REST? |
|---|---|---|
| REST | Ein API-Stil, bei dem Operationen über URLs und HTTP-Methoden ausgedrückt werden | wird abgeschafft |
| **Connect** | `POST /Dienst/Methode` mit JSON im Body; aufrufbar mit `curl` ebenso wie mit `fetch` im Browser | ja (**gewählt**) |
| **gRPC** | Dasselbe Prinzip aus Dienst und Methode, aber über binäres protobuf und HTTP/2; schnell und gut für Streaming geeignet | ja (**zwischen Diensten**) |
| gRPC-web | Eine für den Browser angepasste Variante von gRPC | ja (bei Bedarf) |
| GraphQL | Abfragesprache, mit der man genau die benötigten Felder anfordert | teilweise (**nur für lesende Abfragen**) |
| WASM | Führt Rust-Code direkt im Browser aus | nein (Technik für die Oberfläche) |

- **APIs, die von Browseroberflächen oder per `curl` aufgerufen werden, verwenden Connect** (POST; JSON wird mit RS-JSON gelesen und geschrieben). WASM im Browser kann kein reines gRPC sprechen. Mit Connect bleibt es bei einem gewöhnlichen `fetch`, und `prost` ist nicht nötig – die WASM-Datei wird dadurch nicht größer.
- **Für die Kommunikation zwischen Diensten (Server zu Server, rechenintensive Aufgaben, Streaming) wird gRPC eingesetzt.** In den meisten Fällen reicht Connect aus; auf gRPC wird nur dort umgestellt, wo Streaming tatsächlich gebraucht wird.
- **GraphQL dient ausschließlich lesenden Abfragen**, wenn mehrere Informationen gebündelt abgefragt werden sollen. Für Schreibzugriffe (Operationen) wird es nicht verwendet.
- **WASM bleibt die Technik für die Oberfläche.** Geändert hat sich lediglich, dass die aufgerufene API nun auf Connect beruht.
- Schnittstellen, deren Form durch einen externen Standard festgelegt ist (ACME, OAuth-Callbacks, Webhooks von Drittanbietern, Health-Checks, statische Dateien, OTLP), bleiben gewöhnliches HTTP.
- **Im Zweifel: Connect.**

### Русский (перевод выполнен с помощью ИИ и литературно отредактирован; носителями языка пока не проверен)
**Это не варианты, из которых нужно выбрать один, а технологии разных уровней.** Заменить REST могут только Connect, gRPC и GraphQL; WASM же — это способ создания пользовательского интерфейса.

| Термин | Что это | Заменяет REST? |
|---|---|---|
| REST | Стиль построения API, при котором операции выражаются через URL и HTTP-методы | отменяется |
| **Connect** | `POST /Сервис/Метод` с телом в формате JSON; вызывается как из `curl`, так и из браузерного `fetch` | да (**выбран**) |
| **gRPC** | Тот же принцип «сервис — метод», но поверх двоичного формата protobuf и HTTP/2; работает быстро и хорошо подходит для потоковой передачи | да (**для связи между сервисами**) |
| gRPC-web | Адаптированный для браузера вариант gRPC | да (при необходимости) |
| GraphQL | Язык запросов: клиент запрашивает ровно те поля, которые ему нужны | частично (**только запросы на чтение**) |
| WASM | Позволяет выполнять код на Rust прямо в браузере | нет (технология для интерфейса) |

- **API, которые вызываются из браузерных интерфейсов или через `curl`, строятся на Connect** (POST; JSON читается и записывается через RS-JSON). Браузерный WASM не умеет работать с «чистым» gRPC. С Connect достаточно обычного `fetch`, а `prost` не требуется — размер WASM-файла не увеличивается.
- **Для обмена между сервисами (сервер — сервер, ресурсоёмкие задачи, потоковая передача) применяется gRPC.** В большинстве случаев достаточно Connect; на gRPC переходят только там, где потоковая передача действительно необходима.
- **GraphQL используется только для чтения**, когда нужно получить сразу несколько связанных данных. Для записи (операций) он не применяется.
- **WASM по-прежнему остаётся технологией для интерфейса.** Изменилось лишь то, что вызываемый им API теперь построен на Connect.
- Интерфейсы, форма которых задана внешним стандартом (ACME, обратные вызовы OAuth, вебхуки сторонних сервисов, проверки работоспособности, статические файлы, OTLP), остаются обычным HTTP.
- **Если есть сомнения — выбирайте Connect.**
