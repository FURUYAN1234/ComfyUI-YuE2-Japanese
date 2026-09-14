# v1.1.1

## v1.3.0

Add MiniMax H3-style LLM startup/progress banners and elapsed node titles, with manual/cache exclusion and error handling. / MiniMax H3形式のLLM起動・進行通知とノード名の経過秒数を追加し、手動・キャッシュでの省略とエラー表示に対応しました。

Verified real LLM-to-song execution and cached rerun; update screenshots and installation article. / 実際のLLMから曲生成までとキャッシュ再実行を確認し、画面画像・導入記事を更新しました。

Separate input controller, dimmed OFF inputs, visible combined-input rules and eleven presets. / 入力切替を独立ノードに分離し、OFF入力のグレー表示、両方ON時の規則表示、11種類のプリセットを追加。


Prevent switching the last enabled input OFF in the UI; restore invalid saved states with presets ON. / 画面上で最後のONをOFFにできないよう修正し、不正な保存状態はプリセットONで復元。

# v1.1.0

Independent preset/manual switches; both-OFF validation; visible usage notes. / プリセット・手動の個別切替、両方OFFの拒否、ノード内の使用説明を追加。

# Changelog / 変更履歴

## v1.0.0

- Add automatic, preset and manual free-input song creation. / おまかせ・プリセット・手動自由入力による作曲を追加。
- Add voice, genre, mood, instruments and tempo selections. / 声・ジャンル・雰囲気・楽器・テンポの選択を追加。
- Add natural, approximate and sample-exact edited duration modes, preserving original audio. / 元音声を残す可変尺・目標尺・サンプル単位のぴったり尺編集を追加。
- Replace machine-specific workflow folders with portable installation and direct JSON import. / PC固有のフォルダーを汎用の導入先とJSON直接読込へ変更。
- Publish direct ZIP/JSON links, semantic version tags and newly captured screenshots. / ZIP・JSON直接リンク、バージョン番号タグ、撮影し直した画像で公開。
- Preserve sentence-paired English / Japanese documentation. / 文ごとの英語 / 日本語の併記を維持。

Earlier timestamp labels were development identifiers and are superseded by semantic versioning. / 以前の日時ラベルは開発識別子であり、今後はバージョン番号で管理します。
