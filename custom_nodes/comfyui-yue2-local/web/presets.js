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
    if (nodeData.name !== "YuE2SongOptions") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = created?.apply(this, arguments);
      for (const [label, values] of presets) {
        const button = this.addWidget("button", label, null, () => {
          // Update the actual input widgets, so queueing and saving use the same values.
          for (const [name, value] of Object.entries({ mode: "プリセット", ...values })) {
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
