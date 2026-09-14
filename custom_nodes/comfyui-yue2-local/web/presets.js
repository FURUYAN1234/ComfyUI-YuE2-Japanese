import { app } from "/scripts/app.js";

function syncManualInputs() {
  const graph = app.graph;
  if (!graph) return;
  for (const target of graph._nodes || []) {
    const isManual = target.type === "YuE2ManualLyrics";
    if (!isManual && target.type !== "YuE2PresetOptions") continue;
    const field = isManual ? "manual" : "settings";
    const consumers = (graph._nodes || []).filter(n => n.type === "YuE2JapanesePlanner" &&
      graph.links[n.inputs?.find(i => i.name === field)?.link]?.origin_id === target.id);
    const enabled = !consumers.length || consumers.some(n => {
      const switchLink = graph.links[n.inputs?.find(i => i.name === "switches")?.link];
      const settingsLink = graph.links[n.inputs?.find(i => i.name === "settings")?.link];
      const options = graph.getNodeById((switchLink || settingsLink)?.origin_id);
      if (["YuE2InputSwitches", "YuE2SongSwitches"].includes(options?.type)) return options.widgets.find(w => w.name === (isManual ? "use_manual" : "use_presets"))?.value === true;
      return !isManual || options?.widgets?.find(w => w.name === "mode")?.value === "手動";
    });
    target._yue2ManualEnabled = enabled;
    for (const widget of target.widgets || []) {
      if (widget.type === "yue2_usage") continue;
      if (!widget._yue2Guarded) {
        const callback = widget.callback;
        widget.callback = function (...args) {
          if (widget.disabled) { widget.value = widget._yue2StoredValue; return; }
          return callback?.apply(this, args);
        };
        widget._yue2Guarded = true;
      }
      if (!enabled && !widget.disabled) widget._yue2StoredValue = widget.value;
      widget.disabled = !enabled;
      if (widget.inputEl) {
        widget.inputEl.disabled = !enabled;
        widget.inputEl.readOnly = !enabled;
        widget.inputEl.style.opacity = enabled ? "" : "0.4";
      }
    }
  }
  graph.setDirtyCanvas?.(true, true);
}

const presets = [
  ["☀ 明るいポップ / Bright pop", {voice:"女性・やわらかい",genre:"ポップ",mood:"明るい",instruments:"ピアノ中心",bpm:110}],
  ["☕ 穏やかアコースティック / Acoustic", {voice:"女性・やわらかい",genre:"アコースティック",mood:"落ち着いた",instruments:"アコギ中心",bpm:90}],
  ["🌙 切ないバラード / Ballad", {voice:"男性・やわらかい",genre:"バラード",mood:"切ない",instruments:"ピアノ中心",bpm:75}],
  ["⚡ 元気なロック / Rock", {voice:"女性・力強い",genre:"ロック",mood:"元気",instruments:"バンド",bpm:140}],
  ["✨ 幻想的エレクトロ / Electronic", {voice:"中性的・透明感",genre:"エレクトロ",mood:"幻想的",instruments:"シンセ中心",bpm:110}],
  ["♫ 夜のジャズ / Night jazz", {voice:"女性・やわらかい",genre:"ジャズ",mood:"落ち着いた",instruments:"ジャズトリオ",bpm:85}],
  ["☁ ゆったりLo-fi / Lo-fi", {voice:"中性的・透明感",genre:"Lo-fi",mood:"落ち着いた",instruments:"Lo-fiビート",bpm:75}],
  ["◆ 軽快なダンス / Dance", {voice:"女性・力強い",genre:"ダンス",mood:"元気",instruments:"シンセ中心",bpm:125}],
  ["★ 壮大なオーケストラ / Orchestral", {voice:"男性・力強い",genre:"オーケストラ",mood:"壮大",instruments:"弦楽器中心",bpm:90}],
  ["❀ しっとり和風 / Japanese folk", {voice:"女性・やわらかい",genre:"和風",mood:"幻想的",instruments:"和楽器中心",bpm:80}],
  ["☾ 穏やかな子守歌 / Lullaby", {voice:"女性・やわらかい",genre:"子守歌",mood:"落ち着いた",instruments:"ピアノ中心",bpm:60}]
];

app.registerExtension({
  name: "yue2.presetButtons",
  afterConfigureGraph() { syncManualInputs(); },
  nodeCreated(node) {
    if (!["YuE2InputSwitches", "YuE2PresetOptions", "YuE2SongSwitches", "YuE2SongOptions", "YuE2ManualLyrics", "YuE2JapanesePlanner"].includes(node.type)) return;
    const changed = node.onConnectionsChange;
    node.onConnectionsChange = function () {
      const result = changed?.apply(this, arguments);
      queueMicrotask(syncManualInputs);
      return result;
    };
  },
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
            lines.forEach((line, i) => ctx.fillText(i === 0 && node._yue2ManualEnabled === false ? "Manual OFF: inputs disabled / 手動OFF：入力欄は無効" : line, 12, y + 18 + i * 19));
            ctx.restore();
          }
        });
        return result;
      };
      return;
    }
    if (!["YuE2InputSwitches", "YuE2PresetOptions", "YuE2SongOptions", "YuE2SongSwitches"].includes(nodeData.name)) return;
    if (["YuE2InputSwitches", "YuE2SongSwitches"].includes(nodeData.name)) {
      const configured = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function () {
        const result = configured?.apply(this, arguments);
        const preset = this.widgets.find(w => w.name === "use_presets");
        const manual = this.widgets.find(w => w.name === "use_manual");
        // Repair old invalid files after all serialized widget values have loaded.
        if (preset && manual && preset.value !== true && manual.value !== true) preset.value = true;
        queueMicrotask(syncManualInputs);
        this.setDirtyCanvas(true, true);
        return result;
      };
    }
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = created?.apply(this, arguments);
      const thisNode = this;
      if (["YuE2InputSwitches", "YuE2SongSwitches"].includes(nodeData.name)) {
        for (const [name, label] of [["use_presets", "Presets / プリセットを使う"], ["use_manual", "Manual / 手動入力を使う"]]) {
          const widget = this.widgets.find(w => w.name === name);
          if (widget) {
            widget.label = label;
            const callback = widget.callback;
            widget.callback = function (value, ...args) {
              const peer = thisNode.widgets.find(w => w.name === (name === "use_presets" ? "use_manual" : "use_presets"));
              const accepted = value === false && peer?.value !== true ? true : value;
              widget.value = accepted;
              const result = callback?.call(this, accepted, ...args);
              widget.value = accepted;
              syncManualInputs();
              thisNode.setDirtyCanvas(true, true);
              return result;
            };
          }
        }
      }
      if (nodeData.name === "YuE2InputSwitches") {
        this.addCustomWidget({name:"switch_usage",type:"yue2_usage",options:{serialize:false},computeSize:()=>[500,132],draw(ctx,node,width,y){
          ctx.save();ctx.font="13px sans-serif";ctx.fillStyle="#e5e7eb";
          ["At least one ON; both ON allowed / 最低1つON・両方ONも可能",
           "OFF: dimmed, read-only; text retained / OFF：グレー表示・編集不可・入力保持",
           "Both ON: manual title/lyrics win / 両方ON：曲名・歌詞は自由入力を使用",
           "Style: presets + manual additions / 曲調：プリセット＋自由入力を併用（上書きしない）",
           "No automatic conflict priority / 矛盾した曲調の自動優先処理はありません",
           "Use manual only to ignore preset style / プリセット曲調を使わない場合は自由入力のみON"]
          .forEach((line,i)=>ctx.fillText(line,12,y+18+i*20));ctx.restore();
        }});
        return result;
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
