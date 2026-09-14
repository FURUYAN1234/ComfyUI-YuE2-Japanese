# Japanese Song Creation / 日本語おまかせ作曲
Japanese brief → lyrics/style → vocals/music → listen. / 日本語の希望→歌詞・曲調→歌と伴奏→再生。

## Download and install / 取得と導入
[Installer ZIP / 導入ZIP](https://github.com/FURUYAN1234/ComfyUI-YuE2-Japanese/releases/download/v1.3.0/YuE2_Japanese_LMStudio_v1.3.0.zip) · [README / 導入手順](https://github.com/FURUYAN1234/ComfyUI-YuE2-Japanese#readme)
1. Prepare WSL2 Ubuntu, NVIDIA drivers and ComfyUI; check `nvidia-smi`. / WSL2 Ubuntu・NVIDIAドライバー・ComfyUIを準備し `nvidia-smi` で確認。
2. Extract the full ZIP; run `python3 verify_package.py` then `python3 install.py --comfyui YOUR_COMFYUI_PATH` in Ubuntu. / ZIP全体を展開し、Ubuntuで左記を実行。配置先は自分のComfyUIへ置換。
3. Launch [LM Studio](https://lmstudio.ai/download) on Windows and download [Qwen3.5 9B Q4_K_M](https://lmstudio.ai/models/qwen/qwen3.5-9b). / WindowsでLM Studioを起動し、指定の作詞モデルを取得。
4. Restart ComfyUI and open this JSON by Open or drag-and-drop. / ComfyUIを再起動し、「開く」かドラッグ＆ドロップでこのJSONを読込。

## Music models / 曲生成モデル
Use node ②’s Download models button for all 13 files with SHA256 checks. / ②の「必須モデル一式を取得」で全13ファイルを取得・SHA256検査。
[YuE2-3B](https://huggingface.co/m-a-p/YuE2-3B) + [YuE2-Vae](https://huggingface.co/m-a-p/YuE2-Vae): about 7.8GB. / 合計約7.8GB。
Files go under your `ComfyUI/models/yue2/`; weights alone are insufficient. / 自分のComfyUIの `models/yue2/` 配下へ配置し、重み以外の設定等も必要。
CLI alternative: `python3 download_models.py --comfyui YOUR_COMFYUI_PATH`. / ボタンが使えない場合は左記コマンド。

## Controls and results / 設定と結果
Press a preset button, then adjust voice, genre, mood, instruments or BPM if desired. / プリセットボタンを押し、必要なら声・曲調・雰囲気・楽器・BPMを調整。
At least one input stays ON; OFF inputs are dimmed and read-only. / 最低1つの入力をONに維持し、OFF側はグレー表示・編集不可。
Both ON: manual title/lyrics; preset style + manual additions; no automatic conflict priority. / 両方ON：曲名・歌詞は自由入力、曲調はプリセット＋追記。矛盾の自動優先処理なし。
Natural length keeps the song; Target is approximate; Exact edits the output to the selected seconds. / 可変尺は曲を維持、目標尺は目安、ぴったり尺は指定秒数へ編集。
Exact mode fades and cuts or pads silence, preserving audio_original.flac. / ぴったり尺はフェード・カットまたは無音補完を行い、元音声を保存。
Lyrics: 4 / 8 / 12 / 16 / 24 / 32 / Custom 1–64 lines; manual ON uses your lyrics and disables line controls. / 歌詞は4・8・12・16・24・32行・自由指定1〜64行。手動ONは入力歌詞を使い行数設定を無効化。

Song duration and seconds are set only in Input switches. / 曲の長さ・秒数は入力切替ノードで設定。
④ shows completion, title, duration, lyrics, style and saved folder. / ④に完了・曲名・長さ・歌詞・曲調・保存先を表示。

## Processing and files / 処理と保存
Top banner + node title show LLM phases and elapsed time; manual lyrics skip LLM. / 上部通知とノード名でLLMの段階・経過秒数を表示。手動歌詞はLLMを省略。
LM Studio GPU → unload LLM → YuE2 GPU, sequentially. / 作詞LLMを解放してから曲生成し、GPUを順番に使用。
Runtime location is chosen during installation; nodes: `custom_nodes/comfyui-yue2-local`. / 専用環境の場所は導入時に選択し、ノードは左記へ配置。
Output: `ComfyUI/output/audio/YuE2/`; FLAC, lyrics/style JSON, ABC score, run details. / 左記へ音声・歌詞曲調JSON・楽譜・生成記録を保存。

## Validation and license / 検証とライセンス
Tested: 16GB VRAM, 39.6s audio in 166.2s including LLM loading. / 検証例はVRAM 16GB、39.6秒の音声、LLM読込込み166.2秒。
Preset generation produced 68.3s; manual input produced 53.5s, edited to exactly 10s. / プリセット生成は68.3秒、自由入力は53.5秒から10秒への編集を確認。
Other PCs and musical quality are not guaranteed; listen to each result. / 他PCの動作と音楽品質は保証せず、結果を試聴してください。
Models: CC BY-NC 4.0, noncommercial; bridge code: Apache-2.0. / モデルは非商用、連携コードはApache-2.0。