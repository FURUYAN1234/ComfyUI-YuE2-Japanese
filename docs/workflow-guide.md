# 日本語おまかせ作曲 / YuE2
日本語の一言 → LM Studioが作詞・曲調作成 → YuE2が歌と伴奏 → 再生。
Japanese brief → lyrics/style → vocals/music → listen.

## 初回導入 / First-time setup
**JSONだけでは動きません。ZIP一式と同梱READMEを用意してください。**
1. WindowsのNVIDIAドライバー＋WSL2 Ubuntu 24.04を準備。Ubuntuで `nvidia-smi` がRTXを表示することを確認 / Check GPU in WSL.
2. [ComfyUI公式手順](https://docs.comfy.org/installation/manual_install)でWSL内にComfyUIを準備。Python 3.12のvenvを使用 / Use a WSL ComfyUI environment.
3. 配布フォルダーで `python3 verify_package.py`、続けて `python3 install.py --comfyui ~/ComfyUI` を実行。専用venv・ノード1パッケージ・JSONを配置 / Install isolated runtime and nodes.
4. Windowsに[LM Studio](https://lmstudio.ai/download)を導入し、[Qwen3.5 9Bを開く](https://lmstudio.ai/models/qwen/qwen3.5-9b)から **Q4_K_M** を取得。LM Studioを起動した状態にする / Download in LM Studio.
5. ComfyUIを再起動し、保存後にブラウザーを再読込。②の「必須モデル一式を取得」ボタンを押す / Restart, then download missing files.

## 必須ファイル / Required models
[YuE2-3B](https://huggingface.co/m-a-p/YuE2-3B)＋[YuE2-Vae](https://huggingface.co/m-a-p/YuE2-Vae)：約7.8GB。
標準の不足モデル案内で重みの取得先を開けます。②の **必須モデル一式を取得** ボタンなら設定・トークナイザー等を含む13ファイルを保存・SHA256確認します。
配置 / Place under: `ComfyUI/models/yue2/YuE2-3B/` と `YuE2-Vae/`。
ボタンが使えない場合は、配布フォルダーから `python3 download_models.py --comfyui ~/ComfyUI` を実行。

## 使い方・時間 / Controls
①に「雨の日の帰り道、切ないけど明るい曲」などを入力して実行。
**duration_mode**：従来の歌詞量／30秒／60秒／120秒／数値指定。
**target_seconds**：数値指定時の目標（10～240秒）。秒数モードが本文より優先。
従来モードは **length** の4行／16行を使用。秒数の精度は低く、30秒指定で62.1秒の実測あり。曲は機械的に切りません。④に「✅曲の生成が完了」、曲名・長さ・歌詞・曲調・保存先を表示。実際の長さは④に表示 / Target is approximate; no automatic trimming.
①②の **seed**：変更すると別の候補。固定すると同じ条件 / Seed controls variations.

## GPUと保存 / Processing & output
LM Studio GPU → LLM解放 → YuE2 GPU。重い生成は同じGPUで順番に実行。
Runtime: `~/Codex/work/yue2`。Nodes: `custom_nodes/comfyui-yue2-local`。
保存 / Output: `ComfyUI/output/audio/YuE2/日時_ID/`。
`audio.flac`、`song_plan.json`（歌詞・曲調・元の指示）、`score.abc`、実行設定を保存。

## 検証とライセンス / Validation & license
RTX 5080 16GBで日本語入力から実生成・再生。従来4行の実測：39.6秒の曲、全工程166.2秒（LLM読込を含む）。
ASR結果にはばらつきがあり、発音・音楽品質は試聴が必要です / Listen to each take.
YuE2モデル **CC BY-NC 4.0（非商用）**／コード Apache-2.0。その他の取得物は各配布元の条件に従います。
詳しい環境構築・エラー対処・変更履歴は同梱README / See README for full setup and troubleshooting.
