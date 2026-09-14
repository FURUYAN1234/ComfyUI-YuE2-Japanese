# v1.5.2

Explain per-song JSON records, their lack of workflow import, and how to preserve playback when saving a workflow. / 曲ごとのJSONの用途、ワークフローへの読込非対応、再生を保持する保存方法を説明。

# v1.5.1 / 標準の1曲完走へ復帰

Remove selectable verse counts and restore the original standard two-verse planner; preserve reading review and lyric scrolling. / 番数選択を削除し、従来の標準構成（2番まで）へ復帰。読み確認と歌詞スクロールは維持。

## v1.5.0 / 今回の更新

The default is a full song with two verses; select one to three verses in Input switches. / 初期設定は2番までの1曲完走。入力切替で1〜3番を選べます。
Adding verses regenerates the whole arrangement, so duration does not grow proportionally. / 番数を増やすと曲全体を作り直すため、長さは比例して増えません。
Controlled trials with shared lyrics, style and seed produced 181.8s and 193.1s; ASR found the added verse and chorus, but other sections shortened. / 共通歌詞・曲調・seedでの比較は181.8秒と193.1秒。音声認識で追加の番とサビを確認しましたが、他の部分が短くなりました。
Review hiragana line by line before generation; optionally remember corrected phrases in a private dictionary. / 生成前にひらがなの読みを行ごとに確認し、修正した語句を個人辞書へ記憶できます。
The confirmation warns that edits after generation require a new song; existing audio is retained. / 生成後の修正は再生成となり曲が変わることを確認画面で案内。元音声は残ります。
Audio and MIDI lyrics can auto-scroll by playback progress; manual scrolling pauses following. This is approximate, not vocal alignment. / 音声・MIDIの歌詞は再生時間に合わせて自動スクロールし、手動操作で停止。歌声と厳密に同期する方式ではありません。
Dedicated image loading is disabled when image mode is OFF; the guide includes the folder layout. / 画像OFF時は専用画像読込を無効化し、説明欄にフォルダ構成図を掲載しました。

# v1.4.1

Correct the version attributed to the historical both-inputs-ON measurement; retain the v1.4.0 features and known download issue. / 両方ONの過去実測に付いていた版の誤記を訂正し、v1.4.0の機能と既知の保存問題を維持します。

# v1.1.1

## v1.4.0

- Added optional comic/artwork theme songs with AI musical choices and full-song structure. / 漫画・1枚絵から音楽設定もおまかせで1曲を作る入力を追加。
- Added AI titles for every mode, preserving manually entered lyrics. / 入力歌詞を保持し、全モードの曲名をAIが作成。
- Added completion colors and notifications, separate audio/MIDI players, visible downloads and lyric displays. / 完了色・通知、独立した音声／MIDI再生・保存・歌詞表示を追加。
- Added kana lyric events to MIDI and documented VOCALOID6 import support and untested limits. / MIDIにかな歌詞を収録し、VOCALOID6の読込対応と未検証範囲を明記。
- Added version/date/time download names, portable example artwork, and updated installation and workflow guides. / バージョン・日時付き取得名、配布可能な見本画像を追加し、導入・ワークフロー説明を更新。

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
