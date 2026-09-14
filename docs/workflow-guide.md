# Japanese Song Creation / 日本語おまかせ作曲
Japanese requests become lyrics, vocals and music. Comics and artwork can also become theme songs. / 日本語の希望から歌詞・歌・伴奏を作成。漫画や1枚絵からテーマソングも作れます。

## Setup / 導入
[Download v1.4.0 / 配布ZIP](https://github.com/FURUYAN1234/ComfyUI-YuE2-Japanese/releases/download/v1.4.0/YuE2_Japanese_LMStudio_v1.4.0.zip) · [README / 詳しい導入手順](https://github.com/FURUYAN1234/ComfyUI-YuE2-Japanese#readme)
1. Prepare Windows LM Studio and WSL2 Ubuntu ComfyUI with a working NVIDIA GPU. / WindowsのLM Studioと、NVIDIA GPUが動くWSL2 UbuntuのComfyUIを用意。
2. Extract the full ZIP and run `python3 -B verify_package.py`, then `python3 install.py --comfyui YOUR_COMFYUI_PATH` in Ubuntu. / ZIP全体を展開し、Ubuntuで左記を実行。配置先は自分のComfyUIへ置換。
3. Download Qwen3.5 9B Q4_K_M in LM Studio; use node ②'s model-download button for YuE2's 13 required files. / LM StudioでQwen3.5 9B Q4_K_Mを取得し、②のモデル取得ボタンでYuE2の必須13ファイルを取得。
4. Restart ComfyUI and load this JSON. / ComfyUIを再起動し、このJSONを開きます。

## Inputs / 入力
Normal mode: enter a Japanese request in ①; select presets if desired. / 通常は①へ日本語の希望を入力し、必要ならプリセットを選択。
Use the input controller for presets, free lyrics and duration; both inputs cannot be OFF. / 切替ノードでプリセット・自由歌詞・時間を設定し、両方OFFは不可。
Both ON uses your lyrics and combines preset style with your additions; contradictory styles have no automatic priority. / 両方ONは入力歌詞を使い、曲調はプリセット＋追記。矛盾する曲調の自動優先処理はありません。
OFF fields are dimmed and read-only; turning them ON restores the values. AI creates every song title. / OFF欄はグレー・編集不可で、ONへ戻すと値を再利用。曲名は全曲AIが作成。

## Images / 画像
Load a comic or artwork and enable Visual theme; choose its type and reading order. / 漫画・1枚絵を読み込み、画像テーマをONにして種類・読む順番を選択。
Image ON fixes full-song mode and lets AI choose lyrics, voice, style, instruments and tempo; normal inputs become inactive. / 画像ONでは1曲構成に固定し、歌詞・声・曲調・楽器・テンポをおまかせ。通常の入力欄は非活性化。
Image OFF restores normal input. Read the interpretation in Details to check dialogue and the ending. / 画像OFFで通常入力へ戻ります。詳細欄の画像解釈でセリフ・結末を確認。

## Length / 長さ
Full song requests intro, verses, choruses, bridge and ending, without trimming. / 1曲はイントロ・各番・サビ・ブリッジ・結末を作り、秒数で切りません。
Natural keeps the generated length; Target is approximate; Exact fades/cuts or pads silence and preserves original audio. / 可変尺は生成尺を保持。目標尺は目安。ぴったり尺はフェード・カット／無音補完し、元音声を保存。
Lyrics: 4 / 8 / 12 / 16 / 24 / 32 or Custom 1–64 lines; full song and manual lyrics override this count. / 歌詞は4・8・12・16・24・32行または自由1〜64行。1曲・手動歌詞では行数指定を使いません。

## Progress and output / 進行と出力
LM Studio GPU → unload → YuE2 GPU → playback and MIDI. Startup banner shows the LLM phase; green song border and completion banner show saved audio. / LLM→解放→YuE2→再生・MIDIの順。起動通知でLLM段階、緑枠・完了通知で音声保存完了を表示。
Audio and MIDI nodes show lyrics, players and download buttons. MIDI uses kana lyric events with approximate note assignment; its preview is synthetic instrument audio. / 音声・MIDIノードに歌詞・再生・ダウンロードを表示。MIDIはかな歌詞の仮割当で、試聴は簡易楽器音。
The MIDI player highlights timed kana lyrics, shows instrumental sections and marks playback completion. / MIDIはかな歌詞を再生位置に合わせて強調し、間奏・後奏・再生完了も表示。
VOCALOID6 6.2+ supports MIDI lyric import; editor singing is untested here. See README for conversion and adjustment. / VOCALOID6 6.2以降はMIDI歌詞読込対応。本体歌唱は未検証。変換・調整手順はREADMEへ。
Saved under `ComfyUI/output/audio/YuE2/`: title, version and date/time in audio/MIDI download names, plus score and JSON records. / 左記に保存し、音声・MIDIの取得名に曲名・バージョン・年月日時分秒を付加。楽譜・JSONも保存。

## Requirements and validation / 必須環境・検証
Models: YuE2-3B + YuE2-Vae, about 7.8GB, under `models/yue2`; runtime is separate from ComfyUI Python. / 必須モデルは左記2種・約7.8GB。専用環境はComfyUIのPythonと分離。
Text full-song test: 194.9s audio, 283.5s including LLM loading; no truncation or duration cut. Listen to each result. / 文章の1曲検証：194.9秒の曲・LLM読込込み283.5秒。打切り・秒数カットなし。結果は試聴してください。
Models: CC BY-NC 4.0, noncommercial; integration code: Apache-2.0. / モデルは非商用、連携コードはApache-2.0。各配布元の条件を参照。