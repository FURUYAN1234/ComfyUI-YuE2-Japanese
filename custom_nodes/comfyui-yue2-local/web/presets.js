import { app } from "/scripts/app.js";

const presets = [
  ["☀ 明るいポップ / Bright pop", {voice:"女性・やわらかい",genre:"ポップ",mood:"明るい",instruments:"ピアノ中心",bpm:110}],
  ["☕ 穏やかアコースティック / Acoustic", {voice:"女性・やわらかい",genre:"アコースティック",mood:"落ち着いた",instruments:"アコギ中心",bpm:90}],
  ["🌙 切ないバラード / Ballad", {voice:"男性・やわらかい",genre:"バラード",mood:"切ない",instruments:"ピアノ中心",bpm:75}],
  ["⚡ 元気なロック / Rock", {voice:"女性・力強い",genre:"ロック",mood:"元気",instruments:"バンド",bpm:140}],
  ["✨ 幻想的エレクトロ / Electronic", {voice:"中性的・透明感",genre:"エレクトロ",mood:"幻想的",instruments:"シンセ中心",bpm:110}]
];

app.registerExtension({
  name: "yue2.presetButtons",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name === "YuE2ManualLyrics") {
      const created = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const result = created?.apply(this, arguments);
        const lines = [
          "Manual ON only / 手動ONのときだけ使用",
          "Manual OFF ignores all fields / 手動OFFなら全欄を無視",
          "Lyrics required; no LLM / 歌詞は必須・LLM作詞なし",
          "Both ON: style adds to presets / 両方ON：曲調を追加",
          "Example: light reverb / 例：薄いリバーブを追加",
          "No conflict resolution / 矛盾する指定の自動調整なし",
          "Match voice/instruments / 声・楽器はプリセットと合わせる",
          "Manual only: style required / 手動だけON：曲調も必須"
        ];
        this.addCustomWidget({
          name: "manual_usage", type: "yue2_usage", options: {serialize: false},
          computeSize: () => [480, 164],
          draw(ctx, node, width, y) {
            ctx.save(); ctx.font = "13px sans-serif"; ctx.fillStyle = "#e5e7eb";
            lines.forEach((line, i) => ctx.fillText(line, 12, y + 18 + i * 19));
            ctx.restore();
          }
        });
        return result;
      };
      return;
    }
    if (!["YuE2SongOptions", "YuE2SongSwitches"].includes(nodeData.name)) return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = created?.apply(this, arguments);
      if (nodeData.name === "YuE2SongSwitches") {
        for (const [name, label] of [["use_presets", "Presets / プリセットを使う"], ["use_manual", "Manual / 手動入力を使う"]]) {
          const widget = this.widgets.find(w => w.name === name);
          if (widget) widget.label = label;
        }
      }
      for (const [label, values] of presets) {
        const button = this.addWidget("button", label, null, () => {
          // Update the actual input widgets, so queueing and saving use the same values.
          for (const [name, value] of Object.entries(nodeData.name === "YuE2SongSwitches" ? { use_presets: true, ...values } : { mode: "プリセット", ...values })) {
            const widget = this.widgets.find(w => w.name === name);
            if (!widget) continue;
            widget.value = value;
            widget.callback?.(value);
          }
          this.setDirtyCanvas(true, true);
        });
        button.options = { ...button.options, serialize: false };
      }
      return result;
    };
  }
});
