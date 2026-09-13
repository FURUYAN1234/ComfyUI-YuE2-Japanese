# 20260914064818 / 公開導入ガイド更新 / Public setup guide update

## 20260914065948

- Pair README and release-note sentences as English / Japanese, preserving setup and runtime behavior. / READMEとリリース説明を文ごとの英語 / 日本語へ修正し、導入内容と実行機能を維持。


- 読者向けサムネイル、英日README・Release、GitHub公開リンク。
- Reader-focused thumbnail, bilingual README/Release, GitHub distribution links.
- Runtime and workflow execution unchanged / 実行コード・ワークフロー接続は維持。

# 20260914045244

- 歌詞を改行付きで読みやすく表示。曲情報と生成完了表示を追加。
- PreviewAnyの生成記録JSONと既存接続を維持。
- noteに生成曲と対応する歌詞を追加。
- 実生成・キャッシュ再表示を実ブラウザーで確認。

# 変更履歴

## 20260913234820

- 日本語のおまかせ入力から、LM Studio GPUで作詞、LLM解放、YuE2 GPUで歌と伴奏の生成へ接続。
- 目標秒数の選択・数値入力を追加。実測の精度不足を踏まえ「試験的」と表示し、初期設定は従来4行を維持。
- 標準の不足モデル取得メタデータに加え、ノードから13ファイル一式を取得・SHA256確認するボタンを追加。
- モデル選択肢を実際のファイルから取得し、未取得の重みを取得済みと誤認しないよう修正。
- 移植可能な専用環境インストーラー、README、note原稿、提供画像と生成サムネイルを追加。
- 導入コマンドの作業フォルダーと起動・停止手順を明示。
- Git管理、バイト保持設定、完全なファイル一覧検査、タグからの再構築手順を用意。

## baseline-20260913230926

4行の日本語歌詞から39.6秒の音声を実生成。実行ボタンから保存・ブラウザー再生まで確認した導入時点の退避タグ。
