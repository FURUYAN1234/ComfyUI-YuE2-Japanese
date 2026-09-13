# 日本語おまかせ作曲 / Japanese Song Creation — 20260914064818

## 日本語
日本語の短い希望から、LM Studioが歌詞と曲調を作り、YuE2が歌と伴奏を生成するComfyUIワークフローです。
- ワークフローから必須モデル13ファイルを取得・SHA256検査。
- 目標時間の選択・数値入力、seed、再生、歌詞・曲情報・完了表示。
- WindowsのLM Studio＋WSL2のComfyUI＋独立したYuE2環境。導入はREADMEの手順を参照。
- 読者向けに記事・サムネイルを修正し、機種名を見出しから除去。GitHub配布リンクと英語導入ガイドを追加。

配布ZIP：`YuE2_Japanese_LMStudio_20260914064818.zip`。モデル・生成曲・認証情報は含みません。Source code ZIPではなく、この配布ZIPを使ってください。

検証：既存の実生成・歌詞表示確認済みコードを維持。新版はドキュメント・画像更新で、テストとZIP整合性検査、クリーンなタグからの再構築一致を確認。詳細な実測はREADMEの検証欄へ。

制約：時間は目安（30秒指定→62.1秒の例）。60/120秒・他PCの新規導入は未検証。生成歌詞と歌唱は一致しない場合があり試聴が必要です。連携コードApache-2.0、YuE2モデルCC BY-NC 4.0（非商用）。

## English
Turn a casual Japanese request into lyrics and musical style with LM Studio, then generate vocals and accompaniment with YuE2 in ComfyUI.
- Download all 13 required model files from the workflow and verify SHA256.
- Duration presets/numeric targets, seeds, audio playback, readable lyrics/song details and completion status.
- Windows LM Studio + WSL2 ComfyUI + a separate YuE2 Python environment. Follow the bilingual README for installation.
- Updated the tutorial and thumbnail for readers, removed hardware-specific headline copy, and added GitHub release links and an English setup guide.

Download `YuE2_Japanese_LMStudio_20260914064818.zip`, not GitHub's automatic Source code ZIP. Model weights, generated songs and credentials are excluded.

Validation: unchanged runtime previously passed actual generation and browser lyric-display checks. This documentation/image update is checked with tests, exact package manifests and a clean tagged-source rebuild. Measurement conditions are documented in the README.

Limitations: duration is approximate (a 30-second target produced 62.1 seconds); 60/120-second runs and fresh installation on another PC are untested. Listen to each result; sung words can differ from supplied lyrics. Integration code: Apache-2.0. YuE2 models: CC BY-NC 4.0, noncommercial.

Tag: `yue2-20260914064818`. Version: `20260914064818`.
