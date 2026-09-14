import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

const plannerTypes = new Set(["YuE2JapanesePlanner", "YuE2LyricPlanner"]);
const labels = {queued:"✓ 実行受付済み",running:"⏳ LM Studio処理中",complete:"✓ LM Studio完了",error:"✕ LM Studio停止"};
function llmNodes(prompt) {
  return Object.entries(prompt || {}).filter(([,node]) => {
    if (!plannerTypes.has(node?.class_type)) return false;
    const inputs = node.inputs || {};
    if(Array.isArray(inputs.visual)&&prompt[inputs.visual[0]]?.inputs?.enabled===true)return true;
    const link = inputs.switches || inputs.settings;
    const control = Array.isArray(link) ? prompt[link[0]]?.inputs : null;
    return true;
  }).map(([id]) => String(id));
}
function titlePrefix(node) {
  const status=node._yue2LlmStatus;
  if (!status) return "";
  const seconds=status.state==="running" ? ` ${Math.floor((Date.now()-status.started)/1000)}秒` : "";
  return `${labels[status.state]}${seconds}｜`;
}
app.registerExtension({
  name: "yue2.llmStatus",
  beforeRegisterNodeDef(nodeType,nodeData) {
    if (!plannerTypes.has(nodeData.name)) return;
    const original=nodeType.prototype.getTitle;
    nodeType.prototype.getTitle=function(){return titlePrefix(this)+(original?.apply(this,arguments)||this.title||nodeData.display_name);};
  },
  setup() {
    let panel, timer, ticker, activeNode, phase="";
    let pendingNodes=[];
    const nodeState=(id,state) => {
      const node=app.graph?.getNodeById(id);
      if (!plannerTypes.has(node?.comfyClass||node?.type)) return;
      node._yue2LlmStatus={state,started:state==="running"&&node._yue2LlmStatus?.state==="running"?node._yue2LlmStatus.started:Date.now()};
      node.setDirtyCanvas?.(true,true);
    };
    const hide=()=>{clearTimeout(timer);if(panel)panel.hidden=true;};
    const stop=()=>{clearInterval(ticker);ticker=undefined;activeNode=undefined;};
    const show=(state,text)=>{
      if(!panel){
        panel=document.createElement("div");panel.id="yue2-llm-status";
        panel.setAttribute("role","status");panel.setAttribute("aria-live","polite");
        Object.assign(panel.style,{position:"fixed",zIndex:"100000",top:"78px",left:"50%",transform:"translateX(-50%)",minWidth:"360px",maxWidth:"min(720px, calc(100vw - 40px))",boxSizing:"border-box",padding:"11px 18px",border:"2px solid #5caeff",borderRadius:"9px",boxShadow:"0 8px 24px #0007",font:"700 14px/20px system-ui, sans-serif",textAlign:"center",pointerEvents:"none"});
        document.body.append(panel);
      }
      clearTimeout(timer);panel.hidden=false;panel.dataset.state=state;
      const colors={queued:["#5caeff","#081826","#eaf6ff"],running:["#ffc14d","#312208","#fff4cf"],complete:["#55d98b","#072b1b","#e1ffed"],error:["#ff6b73","#370a0e","#ffe5e7"]}[state];
      [panel.style.borderColor,panel.style.background,panel.style.color]=colors;
      panel.textContent=text;
      if(state==="complete"||state==="error")timer=setTimeout(hide,state==="error"?15000:8000);
    };
    const update=()=>{
      const node=app.graph?.getNodeById(activeNode);
      const seconds=node?._yue2LlmStatus ? Math.floor((Date.now()-node._yue2LlmStatus.started)/1000) : 0;
      show("running",`⏳ ${phase} … ${seconds}秒`);node?.setDirtyCanvas?.(true,false);
    };
    const originalQueue=api.queuePrompt;
    api.queuePrompt=async function(number,payload){
      const ids=llmNodes(payload?.output||payload?.prompt);
      if(ids.length && activeNode===undefined){
        pendingNodes=ids;for(const id of ids)nodeState(id,"queued");
        show("queued","✓ 実行受付済み。LM Studioの開始を待っています / Waiting for LLM");
      }
      try{return await originalQueue.apply(this,arguments);}
      catch(error){if(ids.length&&activeNode===undefined){for(const id of ids)nodeState(id,"error");pendingNodes=[];show("error","✕ 送信に失敗しました。ComfyUIの入力エラーを確認してください / Submission failed");}throw error;}
    };
    api.addEventListener("yue2.llm_status",({detail})=>{
      if(!detail||!["running","complete","error"].includes(detail.state)||typeof detail.message!=="string")return;
      const id=String(detail.node_id);nodeState(id,detail.state);
      if(detail.state==="running"){
        activeNode=id;phase=detail.message;update();if(ticker===undefined)ticker=setInterval(update,1000);
      }else{pendingNodes=[];stop();show(detail.state,`${detail.state==="complete"?"✓":"✕"} ${detail.message}`);}
    });
    api.addEventListener("execution_cached",({detail})=>{
      const cached=(detail?.nodes||[]).map(String);
      if(activeNode===undefined&&pendingNodes.length&&pendingNodes.every(id=>cached.includes(id))){
        for(const id of pendingNodes)nodeState(id,"complete");pendingNodes=[];
        show("complete","✓ 作詞結果を再利用します。LLMの起動なし / Cached lyrics; no LLM startup");
      }
    });
    const fail=(text)=>{if(activeNode!==undefined||pendingNodes.length){if(activeNode!==undefined)nodeState(activeNode,"error");for(const id of pendingNodes)nodeState(id,"error");stop();show("error",text);}pendingNodes=[];};
    api.addEventListener("execution_interrupted",()=>fail("✕ LLM処理を中断しました / LLM interrupted"));
    api.addEventListener("reconnecting",()=>fail("● 接続が切れました。処理状態は未確認です / Disconnected; status unknown"));
    api.addEventListener("execution_error",({detail})=>{if(String(detail?.node_id)===activeNode||(activeNode===undefined&&pendingNodes.length))fail("✕ LLM処理が停止しました。実行エラーを確認してください / LLM stopped");});
    api.addEventListener("execution_success",()=>{pendingNodes=[];});
  }
});
