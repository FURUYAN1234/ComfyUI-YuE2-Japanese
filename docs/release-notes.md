## v1.5.0 / 今回の更新

The default is a full song with two verses; select one to three verses in Input switches. / 初期設定は2番までの1曲完走。入力切替で1〜3番を選べます。
Adding verses regenerates the whole arrangement, so duration does not grow proportionally. / 番数を増やすと曲全体を作り直すため、長さは比例して増えません。
Controlled trials with shared lyrics, style and seed produced 181.8s and 193.1s; ASR found the added verse and chorus, but other sections shortened. / 共通歌詞・曲調・seedでの比較は181.8秒と193.1秒。音声認識で追加の番とサビを確認しましたが、他の部分が短くなりました。
Review hiragana line by line before generation; optionally remember corrected phrases in a private dictionary. / 生成前にひらがなの読みを行ごとに確認し、修正した語句を個人辞書へ記憶できます。
The confirmation warns that edits after generation require a new song; existing audio is retained. / 生成後の修正は再生成となり曲が変わることを確認画面で案内。元音声は残ります。
Audio and MIDI lyrics can auto-scroll by playback progress; manual scrolling pauses following. This is approximate, not vocal alignment. / 音声・MIDIの歌詞は再生時間に合わせて自動スクロールし、手動操作で停止。歌声と厳密に同期する方式ではありません。
Dedicated image loading is disabled when image mode is OFF; the guide includes the folder layout. / 画像OFF時は専用画像読込を無効化し、説明欄にフォルダ構成図を掲載しました。

Install the complete ZIP, verify it, run install.py, then restart ComfyUI and reload the saved workflow. / ZIP全体を展開・検査し、install.pyで導入後、ComfyUI再起動と保存済みワークフローの再読込を行ってください。
Private dictionaries and generated media are not included. / 個人辞書と生成メディアは同梱しません。
