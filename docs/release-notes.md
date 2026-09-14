# v1.4.0 — Japanese song creation with image themes and lyrics MIDI / 日本語おまかせ作曲・画像テーマ・歌詞MIDI

Casual Japanese requests remain the main workflow; comics and artwork can now provide the story for a complete theme song. / 日本語でざっくり希望を伝える作曲を基本に、漫画・1枚絵から1曲のテーマソングを作れるようにしました。

- Added full-song structure, an explicit completion banner and green song-node border. / 1曲構成・完了通知・曲生成ノードの緑枠を追加。
- Image mode lets AI choose the musical settings and disables normal inputs until switched OFF. / 画像モードでは音楽設定をAIに任せ、OFFへ戻すまで通常入力を非活性化。
- AI generates every title while preserving manually supplied lyrics. / 手動歌詞を維持し、全曲の曲名をAIが作成。
- Audio and MIDI have separate players, visible downloads and lyric displays. / 音声とMIDIを独立した再生・ダウンロード・歌詞表示ノードに分離。
- MIDI includes kana lyric events; note assignment is approximate and editable. / MIDIにかなの歌詞イベントを収録し、音符への仮割当を編集可能。
- Downloads share the song title, semantic workflow version and a 14-digit date/time stamp. / 取得名に曲名・ワークフローのバージョン番号・14桁の年月日時分秒を共通で付加。

VOCALOID6 6.2+ officially supports MIDI lyric import; see README for the phoneme-conversion procedure and limitations. Actual VOCALOID singing has not been tested here. / VOCALOID6 6.2以降は公式にMIDI歌詞読込へ対応。発音記号の変換手順と制限はREADMEへ。本体での歌唱は未検証です。

Use the complete installer ZIP for initial setup and the separate JSON after installation. / 初回は導入ZIP一式を使い、環境構築後は単独JSONでも読み込めます。

Models are downloaded separately and remain subject to their licenses, including YuE2's CC BY-NC 4.0. / モデルは別途取得し、YuE2のCC BY-NC 4.0を含む各ライセンスに従ってください。

The MIDI player highlights kana lyrics at the MIDI event times and follows seeking. This is approximate score alignment, not forced alignment to the generated vocals. / MIDI再生ノードでは歌詞イベントの時刻に合わせてかな歌詞を強調し、シークにも追従します。楽譜への仮割当であり、生成された歌声との厳密な同期ではありません。

Full-song artwork verification generated 214.48 seconds of audio without duration editing and completed both audio and MIDI output; this does not certify every visual detail or musical quality. / 1枚絵の1曲検証では214.48秒の音声を秒数編集なしで生成し、音声・MIDIの両出力が完了しました。画像の全細部の理解や音楽的品質を保証する検証ではありません。

Save the workflow after generation to retain the audio/MIDI player references and lyrics when reopening it. The media files remain in the output folder and are not embedded in the JSON. / 生成後にワークフローを保存すると、開き直した際に音声・MIDIの再生参照と歌詞を復元します。メディア本体はoutputフォルダーに保存され、JSONには埋め込みません。
