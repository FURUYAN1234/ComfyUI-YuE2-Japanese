# v1.5.4 Image-text lyric recovery / 画像文字混入時の歌詞復旧

Image labels and licence text can contain Latin characters or digits that do not belong in a singable lyric. The planner first asks the LLM to fix such a line; if the retry still contains the image fragment, it substitutes only that line with a natural Japanese lyric and continues the full song. / 画像内のラベルやライセンス表記には、歌詞に向かない英数字が含まれることがあります。作詞器はまずLLMへその行の修正を依頼し、再試行後も画像断片が残る場合だけ、その行を自然な日本語の歌詞へ置換して1曲の生成を続けます。

A live image-mode execution using the formerly failing image completed successfully and saved a 182.96-second FLAC and MIDI. Other image-reading, API, and generation failures remain errors. / 以前失敗した画像を使う実機の画像モードは成功し、182.96秒のFLACとMIDIを保存しました。画像読取り・API・生成の別の失敗は引き続きエラーとして表示します。

# v1.5.3 LM Studio startup recovery / LM Studio起動の復旧

The planner now checks for a ready LM Studio API after invoking the CLI and waits up to 30 seconds. If the server remains unavailable, it invokes the start command once more and waits again before reporting a clear error. / 作詞処理はCLI呼び出し後にLM Studio APIの準備完了を確認し、最大30秒待機します。サーバーがまだ使えない場合は起動コマンドを1回だけ再実行して再度待機し、その後に明確なエラーを表示します。

This fixes the observed case where a cold LM Studio launch outlived the original CLI timeout. It does not claim recovery from invalid responses, wrong ports, or model errors. / LM Studioのコールド起動が元のCLIタイムアウトを超えた事例を修正します。不正な応答、誤ったポート、モデルエラーからの復旧を保証するものではありません。

## v1.5.2 Output record guide / 生成記録の説明

Document each output JSON and distinguish records from importable ComfyUI workflows. / 出力JSONごとの用途と、読込用ワークフローJSONとの違いを明記。

Keep the audio/MIDI folder with a saved workflow to preserve player references. / 保存したワークフローと音声・MIDIの曲フォルダーを一緒に保管する手順を追加。

Song generation behavior is unchanged. / 曲生成の動作は変更していません。
