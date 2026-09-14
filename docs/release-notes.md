# v1.2.0 — Custom lyric lines / 歌詞の自由行数

Choose Short trial (4 lines), Normal (16 lines), or Custom (1–64 lines) in the lyric planner. / 作詞ノードの「歌詞の行数」で「短い試作（4行）」「通常（16行）」「自由に指定（1〜64行）」を選べます。

Headings and blank lines do not count; Custom lines is editable only in Custom mode. / 見出し・空行を除いて数え、「自由指定の行数」は自由指定のときだけ編集できます。

Manual ON uses the entered lyrics unchanged and disables both line-count controls. / 手動ONでは入力歌詞をそのまま使い、行数の設定は両方とも無効になります。

Set song duration and seconds in Input switches & priority; the current planner has no duplicate time controls. / 曲の長さと秒数は「入力切替・優先関係」で設定し、現行の作詞ノードには重複する時間設定を置きません。

Target seconds do not change the selected lyric count; short targets with many lines may require editing or a different lyric count. / 目標秒数によって選択した行数は変えず、短い秒数に多くの行を指定した場合は編集や行数の見直しが必要になることがあります。

Eleven presets, last-ON protection, disabled inputs and existing workflows remain supported. / 11種類のプリセット、最後のONの保護、OFF入力の無効化、既存ワークフローの互換性を維持します。

Validated in the live workflow: 7 requested lyric lines produced 7 lines, 73.0s original audio and an exact 30.0s edited output in 194.824s end to end, including model loading and no cached node skipping. / 実ワークフローで7行指定から7行の歌詞・約73.0秒の元音声・30.0秒の編集音声を生成し、全工程194.824秒（モデル読込込み・キャッシュ省略なし）でした。

Manual API verification preserved the entered 4 lines even with a stored custom count of 17; the LLM was not called. / 手動の実API検証では自由指定17行の保存値があっても入力した4行を保持し、LLMは呼び出されませんでした。

The distributed example starts with Custom 7 lines and Exact 30 seconds; choose Natural to keep the full generated song. / 配布例の初期値は自由指定7行・ぴったり尺30秒で、生成された曲を全て残す場合は可変尺を選んでください。

Line validation covers 1–64; actual song generation was checked at 7 lines, not every length. / 行数の検査範囲は1〜64行で、実際の曲生成は7行で確認し、全行数を実生成したわけではありません。

Fixed recursion when disabled DOM inputs restored their values during queueing; a regression test covers the callback setter. / 無効な入力欄が実行時に値を復元して再帰する不具合を修正し、値設定コールバックの回帰テストを追加しました。
