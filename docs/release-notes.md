# Preset and manual switches / プリセット・手動切替 — v1.1.0

### Preset and manual switches / プリセットと手動の切り替え

Presets ON + Manual OFF: use the selected presets and let LM Studio write lyrics. / プリセットON・手動OFF：選択した設定でLM Studioが作詞します。

Presets OFF + Manual ON: use only your title, lyrics and style; lyrics and style are required. / プリセットOFF・手動ON：自由入力の曲名・歌詞・曲調だけを使い、歌詞と曲調は必須です。

Both ON: use your lyrics and add your style to the selected presets. / 両方ON：手動歌詞を使い、プリセットに手動曲調を追加します。

Both OFF is rejected before execution. / 両方OFFは実行前にエラーで拒否します。

Preset buttons enable presets and preserve the manual switch. / プリセットボタンはプリセットをONにし、手動スイッチは維持します。

Conflicting instructions are not resolved automatically; match voice/instrument selections or leave those preset fields automatic. / 矛盾する指定は自動調整しないため、声・楽器を合わせるか該当プリセットをおまかせにしてください。


[Installer ZIP / 導入ZIP](https://github.com/FURUYAN1234/ComfyUI-YuE2-Japanese/releases/download/v1.1.0/YuE2_Japanese_LMStudio_v1.1.0.zip) · [Workflow JSON / ワークフローJSON](https://github.com/FURUYAN1234/ComfyUI-YuE2-Japanese/releases/download/v1.1.0/YuE2_Japanese_LMStudio.json)

Validation: 11 Python tests, preset button tests, actual API checks for all switch combinations, and a full 54.959-second song generated with both ON. / 検証：Python 11件、プリセットボタン、全切替組合せの実API、両方ONで54.959秒の曲生成を確認。
