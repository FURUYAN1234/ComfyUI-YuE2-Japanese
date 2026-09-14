import { app } from "/scripts/app.js";

// Keep the JSON output intact; only the YuE2 preview is made readable.
export function readableLyrics(value) {
  if (typeof value !== "string") return value;
  let data;
  try { data = JSON.parse(value); } catch { return value; }
  if (!data || typeof data.lyrics !== "string" || typeof data.title !== "string" ||
      typeof data.style !== "string" || typeof data.audio_seconds !== "number" ||
      typeof data.folder !== "string" || !data.folder.includes("/audio/YuE2/")) return value;
  const seconds = value => Number.isFinite(value) ? `${value.toFixed(1)}秒` : "記録なし";
  return [
    "✅ 曲の生成が完了 / Completed",
    `曲名 / Title：${data.title}`,
    `曲の長さ / Duration：${seconds(data.audio_seconds)}`,
    `目標時間 / Target：${data.target_seconds == null ? "指定なし" : seconds(data.target_seconds)}${data.duration_mode === "ぴったり尺（編集）" ? "（編集で調整）" : "（目安）"}`,
    `作成方法 / Creation：${data.creation_mode || "おまかせ"}`,
    `元の曲の長さ / Original：${seconds(data.postprocess?.original_seconds ?? data.audio_seconds)}`,
    `時間設定 / Mode：${data.duration_mode || "歌詞量で指定（従来）"}`,
    `曲生成・保存 / Generation：${seconds(data.song_generation_seconds)}（作詞時間を除く）`,
    ...(data.image_reading?["", "画像の読み取り / Image interpretation", data.image_reading]:[]),
    "", "歌詞 / Lyrics", data.lyrics,
    "", "曲調・声・楽器 / Style", data.style,
    "", "保存先 / Saved folder", "ComfyUI/output/audio/YuE2/" + data.folder.split("/audio/YuE2/")[1],
    "", data.duration_note || "目標秒数は目安です。",
    data.note || "日本語歌唱の品質は試聴して確認してください。"
  ].join("\n");
}

app.registerExtension({
  name: "yue2.readableLyrics",
  onNodeOutputsUpdated(outputs) {
    // History restoration also updates previews without calling onExecuted.
    queueMicrotask(() => {
      for (const [id, output] of Object.entries(outputs)) {
        const node = app.graph?.getNodeById(id);
        if (node?.type !== "PreviewAny") continue;
        const widget = node.widgets?.find(w => w.name === "preview_text");
        if (widget && Array.isArray(output?.text)) widget.value = output.text.map(readableLyrics).join("\n\n");
      }
    });
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "PreviewAny") return;
    const executed = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      const display = Array.isArray(message?.text)
        ? { ...message, text: message.text.map(readableLyrics) } : message;
      return executed?.call(this, display);
    };
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const result = configured?.apply(this, arguments);
      for (const widget of this.widgets || []) {
        if (widget.name === "preview_text") widget.value = readableLyrics(widget.value);
      }
      return result;
    };
  }
});
