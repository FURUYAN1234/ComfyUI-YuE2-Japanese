# v1.1.1 — Keep one input enabled / 最低1つの入力をONに維持

The last enabled switch stays ON when clicked OFF; enable the other switch first to change sides. / 最後のONをOFFにしようとしてもONを維持します。切り替える場合は先にもう片方をONにしてください。

Saved files with both OFF are restored with presets ON; valid manual-only and combined states are preserved. / 両方OFFの保存ファイルはプリセットONで復元し、手動のみ・両方ONの有効な状態は維持します。

Server-side rejection of invalid external API requests remains in place. / 外部APIからの不正な指定を拒否するサーバー側検査も維持します。


### Separate input control / 独立した入力切り替え

The Input switches node controls separate Presets and Free input nodes; timing stays in the controller. / 入力切替ノードで独立したプリセット・自由入力ノードを制御し、時間も切替ノードで設定します。

OFF inputs are dimmed and cannot be edited; existing values are retained and restored when enabled. / OFF側はグレー表示・編集不可となり、入力内容は消さずにONへ戻したときに再利用します。

With both ON, title and lyrics come from free input; style combines presets and free text without overwriting. / 両方ONでは曲名と歌詞は自由入力を使い、曲調はプリセットと自由入力を上書きせず併用します。

No automatic priority resolves contradictory styles; use free input alone to exclude all preset style. / 矛盾する曲調の自動優先処理はなく、プリセットの曲調を外したい場合は自由入力のみONにしてください。

Eleven preset buttons now include jazz, Lo-fi, dance, orchestral, Japanese folk and lullaby. / ジャズ・Lo-fi・ダンス・オーケストラ・和風・子守歌を追加し、プリセットボタンを11種類に増やしました。

Validated: 11 preset configurations via the live API, last-ON protection and disabled inputs in the browser, and actual song generation. / 全11プリセット設定の実API、実画面での最後のON保護・OFF入力の無効化、実際の曲生成を確認しました。
