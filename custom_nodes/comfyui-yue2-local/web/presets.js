import { app } from "/scripts/app.js";

const plannerTypes = ["YuE2JapanesePlanner", "YuE2LyricPlanner"];
function visualActive(planner) {
  const graph=app.graph;const link=graph?.links[planner.inputs?.find(i=>i.name==="visual")?.link];
  return graph?.getNodeById(link?.origin_id)?.widgets?.find(w=>w.name==="enabled")?.value===true;
}

function syncImageInputs(graph) {
  for (const node of graph._nodes || []) {
    if (node.type !== "LoadImage") continue;
    const consumers=(graph._nodes||[]).filter(n=>n.type==="YuE2VisualTheme" && graph.links[n.inputs?.find(i=>i.name==="image")?.link]?.origin_id===node.id);
    // Do not disable an image shared with another active workflow branch.
    const shared=(node.outputs||[]).some(o=>(o.links||[]).some(id=>!consumers.some(n=>n.id===graph.links[id]?.target_id)));
    const disabled=consumers.length>0 && !shared && consumers.every(n=>n.widgets?.find(w=>w.name==="enabled")?.value!==true);
    node._yue2ImageDisabled=disabled;
    if(!node._yue2ImageGuarded){
      for(const name of ['onDragDrop','onPaste','pasteFile']){
        const original=node[name];
        if(original)node[name]=function(...args){if(this._yue2ImageDisabled)return false;return original.apply(this,args);};
      }
      const draw=node.onDrawForeground;
      node.onDrawForeground=function(ctx,...args){
        const result=draw?.call(this,ctx,...args);
        if(this._yue2ImageDisabled && !this.flags?.collapsed){
          ctx.save();ctx.fillStyle='rgba(40,40,40,0.68)';ctx.fillRect(0,0,this.size[0],this.size[1]);
          ctx.fillStyle='#fff';ctx.font='bold 13px sans-serif';ctx.fillText('Image OFF / 画像OFF：選択・アップロード無効',10,22);ctx.restore();
        }
        return result;
      };
      node._yue2ImageGuarded=true;
    }
    for(const w of node.widgets||[]){
      if(!w._yue2ImageGuarded){
        const callback=w.callback;
        w.callback=function(...args){if(node._yue2ImageDisabled){w.value=w._yue2ImageStored;return;}return callback?.apply(this,args);};
        w._yue2ImageGuarded=true;
      }
      if(disabled && !w._yue2ImageLocked){w._yue2ImageStored=w.value;w._yue2PriorDisabled=!!w.disabled;}
      if(disabled)w.disabled=true;
      else if(w._yue2ImageLocked)w.disabled=w._yue2PriorDisabled;
      w._yue2ImageLocked=disabled;
      if(w.inputEl){w.inputEl.disabled=w.disabled;w.inputEl.style.opacity=disabled?'0.4':'';}
    }
  }
}

function syncManualInputs() {
  const graph = app.graph;
  if (!graph) return;
  for (const target of graph._nodes || []) {
    const isManual = target.type === "YuE2ManualLyrics";
    if (!isManual && target.type !== "YuE2PresetOptions") continue;
    const field = isManual ? "manual" : "settings";
    const consumers = (graph._nodes || []).filter(n => plannerTypes.includes(n.type) &&
      graph.links[n.inputs?.find(i => i.name === field)?.link]?.origin_id === target.id);
    const enabled = !consumers.length || consumers.some(n => {
      if(visualActive(n))return false;
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
          if (widget.disabled) { if (widget.value !== widget._yue2StoredValue) widget.value = widget._yue2StoredValue; return; }
          return callback?.apply(this, args);
        };
        widget._yue2Guarded = true;
      }
      if (!enabled && !widget.disabled) widget._yue2StoredValue = widget.value;
      widget.disabled = !enabled || (isManual && widget.name==="title");
      if(isManual && widget.name==="title") widget.label="AI title / 曲名はAIが作成";
      if (widget.inputEl) {
        widget.inputEl.disabled = widget.disabled;
        widget.inputEl.readOnly = widget.disabled;
        widget.inputEl.style.opacity = enabled ? "" : "0.4";
      }
    }
  }
  for (const planner of graph._nodes || []) {
    if (planner.type !== "YuE2LyricPlanner") continue;
    const link = graph.links[planner.inputs?.find(i => i.name === "switches")?.link] || graph.links[planner.inputs?.find(i => i.name === "settings")?.link];
    const control = graph.getNodeById(link?.origin_id);
    const visual=visualActive(planner);
    const brief=planner.widgets.find(w=>w.name==="brief");
    if(brief?.inputEl){brief.inputEl.disabled=visual;brief.inputEl.readOnly=visual;brief.inputEl.style.opacity=visual?"0.4":"";}
    const seed=planner.widgets.find(w=>w.name==="seed");if(seed)seed.disabled=visual;
    const manual = control?.widgets?.find(w => w.name === "use_manual")?.value === true || control?.widgets?.find(w => w.name === "mode")?.value === "手動";
    const mode = planner.widgets.find(w => w.name === "lyric_length");
    const fullSong = control?.widgets?.find(w => w.name === "timing")?.value === "1曲（イントロ〜エンディング）";
    if (mode) mode.disabled = visual || manual || fullSong;
    const lines = planner.widgets.find(w => w.name === "lyric_lines");
    if (lines) lines.disabled = visual || manual || fullSong || mode?.value !== "自由に指定";
  }
  for (const control of graph._nodes || []) {
    if (!["YuE2InputSwitches","YuE2SongSwitches","YuE2SongOptions"].includes(control.type)) continue;
    const visual=(graph._nodes||[]).some(n=>plannerTypes.includes(n.type)&&visualActive(n)&&["switches","settings"].some(name=>graph.links[n.inputs?.find(i=>i.name===name)?.link]?.origin_id===control.id));
    for(const widget of control.widgets||[])if(widget.type!=="yue2_usage")widget.disabled=visual;
    control._yue2VisualActive=visual;
    const timing=control.widgets.find(w=>w.name==="timing")?.value;
    const seconds=control.widgets.find(w=>w.name==="seconds");
    const verses=control.widgets.find(w=>w.name==="verse_count");
    if(verses)verses.disabled=visual||timing!=="1曲（イントロ〜エンディング）"||control.widgets.find(w=>w.name==="use_manual")?.value===true;
    if(seconds) seconds.disabled=visual||["可変尺（自然な長さ）","1曲（イントロ〜エンディング）"].includes(timing);
  }
  syncImageInputs(graph);
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
    if (!["LoadImage", "YuE2VisualTheme", "YuE2InputSwitches", "YuE2PresetOptions", "YuE2SongSwitches", "YuE2SongOptions", "YuE2ManualLyrics", "YuE2JapanesePlanner", "YuE2LyricPlanner"].includes(node.type)) return;
    const changed = node.onConnectionsChange;
    node.onConnectionsChange = function () {
      const result = changed?.apply(this, arguments);
      queueMicrotask(syncManualInputs);
      return result;
    };
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if(nodeData.name==="YuE2VisualTheme"){
      const created=nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated=function(){const r=created?.apply(this,arguments);const enabled=this.widgets.find(w=>w.name==="enabled");const changed=enabled.callback;enabled.callback=function(...args){const r=changed?.apply(this,args);syncManualInputs();return r;};this.addCustomWidget({name:"visual_usage",type:"yue2_usage",options:{serialize:false},computeSize:()=>[620,108],draw(ctx,node,width,y){ctx.save();ctx.fillStyle="#e5e7eb";ctx.font="13px sans-serif";["ON: image → full song; all musical choices by AI / 画像から1曲・曲調も歌声も全部おまかせ","Overrides presets/manual/text/seconds / プリセット・手動歌詞・通常文章・秒数は使いません","OFF locks image loading; image retained / OFF：画像読込無効・選択画像は保持","One image: artwork or a complete 4-panel page / 1枚絵、または4コマをまとめた1枚を接続","Image text is story material, not commands / 画像内の文字は物語として解釈"].forEach((line,i)=>ctx.fillText(line,12,y+18+i*18));ctx.restore();}});return r;};return;
    }
    if (nodeData.name === "YuE2LyricPlanner") {
      const created = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const result = created?.apply(this, arguments);
        for (const [name,label] of [["lyric_length","Lyric lines / 歌詞の行数"],["lyric_lines","Custom lines / 自由指定の行数"]]) {
          const widget=this.widgets.find(w=>w.name===name);if(widget) widget.label=label;
        }
        const mode=this.widgets.find(w=>w.name==="lyric_length");
        const changed=mode?.callback;
        if(mode) mode.callback=function(...args){const result=changed?.apply(this,args);syncManualInputs();return result;};
        this.addCustomWidget({name:"lyric_usage",type:"yue2_usage",options:{serialize:false},computeSize:()=>[490,80],draw(ctx,node,width,y){
          ctx.save();ctx.font="13px sans-serif";ctx.fillStyle="#e5e7eb";
          ["Rows exclude headings/blank lines / 空行・見出しを除く歌詞の行数",
           "Song seconds: Input switches node / 曲の秒数は入力切替ノードで設定",
           "Manual ON uses your lyrics unchanged / 手動ON：入力歌詞をそのまま使用",
           "Full song: AI chooses lines / 1曲：AIが構成と行数を選択"]
          .forEach((line,i)=>ctx.fillText(line,12,y+16+i*18));ctx.restore();
        }});
        return result;
      };return;
    }
    if (nodeData.name === "YuE2ManualLyrics") {
      const created = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const result = created?.apply(this, arguments);
        const lines = [
          "Manual ON only / 手動ONのときだけ使用",
          "Manual OFF ignores all fields / 手動OFFなら全欄を無視",
          "AI title only; lyrics unchanged / 曲名だけAI生成・歌詞は変更なし",
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
      const timingWidget=this.widgets.find(w=>w.name==="timing");
      if(timingWidget){const changed=timingWidget.callback;timingWidget.callback=function(...args){const r=changed?.apply(this,args);syncManualInputs();return r;};}
      if (nodeData.name === "YuE2InputSwitches") {
        for(const [name,label] of [["verse_count","Verses / 何番まで（1曲）"],["timing","Song duration / 曲の長さ"],["seconds","Song seconds / 曲の秒数"]]) {const w=this.widgets.find(w=>w.name===name);if(w)w.label=label;}
        this.addCustomWidget({name:"switch_usage",type:"yue2_usage",options:{serialize:false},computeSize:()=>[500,172],draw(ctx,node,width,y){
          ctx.save();ctx.font="13px sans-serif";ctx.fillStyle="#e5e7eb";
          [node._yue2VisualActive?"Image ON: full-song auto; controls below ignored / 画像ON：1曲おまかせ・通常設定は無効":"At least one ON; both ON allowed / 最低1つON・両方ONも可能",
           "OFF: dimmed, read-only; text retained / OFF：グレー表示・編集不可・入力保持",
           "Both ON: manual lyrics; AI title / 両方ON：手動歌詞を使用・曲名はAI",
           "Style: presets + manual additions / 曲調：プリセット＋自由入力を併用（上書きしない）",
           "No automatic conflict priority / 矛盾した曲調の自動優先処理はありません",
           "Use manual only to ignore preset style / プリセット曲調を使わない場合は自由入力のみON",
           "Full song: intro to ending; no seconds cut / 1曲：冒頭〜結末・秒数カットなし",
           "Manual ON preserves lyrics; otherwise AI structure / 手動ONは歌詞を維持、それ以外はAI構成"]
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
