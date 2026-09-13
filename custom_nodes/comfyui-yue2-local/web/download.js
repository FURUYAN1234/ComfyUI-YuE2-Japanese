import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";
app.registerExtension({
  name: "yue2.requiredModels",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "YuE2LocalSong") return;
    const previous = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      previous?.apply(this, arguments);
      let busy = false;
      const widget = this.addWidget("button", "必須モデル一式を取得 / Download models", null, async () => {
        if (busy) return;
        busy = true; widget.name = "取得・検査中 / Downloading…"; this.setDirtyCanvas(true, true);
        try {
          const response = await api.fetchApi("/yue2/download-models", {method: "POST"});
          const result = await response.json();
          if (!response.ok) throw new Error(result.error || "Download failed");
          widget.name = "取得・検査完了 / Models ready";
          app.ui.dialog.show(result.message);
        } catch (error) {
          widget.name = "取得失敗・再試行 / Retry download";
          app.ui.dialog.show(String(error.message || error));
        } finally { busy = false; this.setDirtyCanvas(true, true); }
      }, {serialize: false});
      return undefined;
    };
  }
});
