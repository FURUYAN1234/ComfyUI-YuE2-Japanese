# Japanese Song Creation / 日本語おまかせ作曲 — 20260914065948

The README and these release notes now pair each English sentence with Japanese after a slash, instead of separating languages into sections. / READMEとこのリリース説明を、言語ごとの別セクションではなく、各英文の後にスラッシュで日本語を併記する形式へ修正しました。

Installation commands, configuration details, limitations, lyrics, images and existing runtime functionality are preserved. / 導入コマンド・設定の説明・制約・歌詞・画像・既存の実行機能を維持しています。

## Features / 機能

- LM Studio turns a casual Japanese request into lyrics and musical style, then YuE2 generates vocals and accompaniment. / 日本語の気軽な希望からLM Studioが歌詞と曲調を作り、YuE2が歌と伴奏を生成します。
- Download all 13 required model files from the workflow with SHA256 verification. / ワークフローから必須モデル13ファイルを取得し、SHA256を検査できます。
- Use duration presets or numeric targets, seeds, audio playback, readable lyrics, song information and a completion indicator. / 目標時間の選択・数値入力、seed、音声再生、読みやすい歌詞・曲情報・完了表示を利用できます。
- Use LM Studio on Windows with ComfyUI in WSL2 and an isolated YuE2 Python environment. / WindowsのLM Studio、WSL2のComfyUI、独立したYuE2 Python環境を組み合わせます。

## Download and install / 取得と導入

Download `YuE2_Japanese_LMStudio_20260914065948.zip` from this Release, rather than GitHub's automatic Source code ZIP. / GitHub自動生成のSource code ZIPではなく、このReleaseの `YuE2_Japanese_LMStudio_20260914065948.zip` を取得してください。

Extract the entire ZIP and follow the sentence-by-sentence bilingual README for setup. / ZIP全体を展開し、文ごとに英日併記したREADMEに従って環境を構築してください。

Weights, generated songs and credentials are excluded from the ZIP. / モデルの重み・生成曲・認証情報はZIPに含みません。

## Validation and limits / 検証と制約

Runtime code is unchanged from the version verified through actual generation and browser lyrics/completion display. / 実生成とブラウザーでの歌詞・完了表示を確認した版から、実行コードは変更していません。

This revision is checked for inline English/Japanese pairing, retained setup content, package integrity and identical rebuilding from a clean public tag. / 今回は文ごとの英日対応、導入内容の保持、配布整合性、クリーンな公開タグからの再構築一致を検査します。

Duration is approximate: a 30-second target produced 62.1 seconds in one test. / 時間は目安であり、30秒指定から62.1秒になった実測があります。

60/120-second runs and a fresh installation on another PC are untested. / 60秒・120秒の実生成と、他PCへの新規導入は未検証です。

Listen to each result because sung words can differ from the supplied lyrics. / 指定した歌詞と歌唱が異なる場合があるため、結果ごとに試聴してください。

Integration code: Apache-2.0; YuE2 models: CC BY-NC 4.0, noncommercial. / 連携コードはApache-2.0、YuE2モデルは非商用のCC BY-NC 4.0です。

Version: `20260914065948`; tag: `yue2-20260914065948`. / 配布版は `20260914065948`、タグは `yue2-20260914065948` です。
