# v1.5.3 LM Studio startup recovery / LM Studio起動の復旧

The planner now checks for a ready LM Studio API after invoking the CLI and waits up to 30 seconds. If the server remains unavailable, it invokes the start command once more and waits again before reporting a clear error. / 作詞処理はCLI呼び出し後にLM Studio APIの準備完了を確認し、最大30秒待機します。サーバーがまだ使えない場合は起動コマンドを1回だけ再実行して再度待機し、その後に明確なエラーを表示します。

This fixes the observed case where a cold LM Studio launch outlived the original CLI timeout. It does not claim recovery from invalid responses, wrong ports, or model errors. / LM Studioのコールド起動が元のCLIタイムアウトを超えた事例を修正します。不正な応答、誤ったポート、モデルエラーからの復旧を保証するものではありません。

## v1.5.2 Output record guide / 生成記録の説明

Document each output JSON and distinguish records from importable ComfyUI workflows. / 出力JSONごとの用途と、読込用ワークフローJSONとの違いを明記。

Keep the audio/MIDI folder with a saved workflow to preserve player references. / 保存したワークフローと音声・MIDIの曲フォルダーを一緒に保管する手順を追加。

Song generation behavior is unchanged. / 曲生成の動作は変更していません。
