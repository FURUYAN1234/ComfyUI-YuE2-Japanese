# v1.3.0 — LLM startup status / LLM起動・進行表示

Show a centered status banner and elapsed time in the lyric node title, matching the MiniMax H3 workflow. / MiniMax H3ワークフローと同じ形式の上部中央通知と、作詞ノード名の経過秒数表示を追加しました。

Follow GPU loading, lyric generation, GPU release and completion; stop the timer on errors, interruption or disconnection. / GPU読込・作詞・GPU解放・完了を表示し、エラー・中断・接続断ではタイマーを止めます。

Manual lyrics skip LLM startup; cached results explicitly display that the LLM is not starting. / 手動歌詞ではLLMを省略し、キャッシュ再利用時はLLMを起動しないことを表示します。

Preserve the 11 music presets, six lyric-length presets, custom line counts, input switches and duration settings. / 11種類の曲調プリセット、6種類の歌詞行数、自由行数、入力切替、曲の秒数設定を維持します。

Validated in the browser with a real seven-line generation (30.0-second output, 193.572 seconds including model loading) and a cached rerun; focused Python and frontend tests also passed. / 実ブラウザーで7行の実生成（出力30.0秒、モデル読込込み193.572秒）とキャッシュ再実行を確認し、Python・通知の検査も合格しました。
