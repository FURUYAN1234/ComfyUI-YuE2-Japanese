import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";
const kind="YuE2LocalSong";
const labels={running:"⏳ 作曲中 / Creating",complete:"✅ 曲の生成完了 / Song complete",error:"✕ 曲生成停止 / Stopped"};
function mark(node,state){if(node?.comfyClass!==kind&&node?.type!==kind)return;node._yue2SongState=state;node.setDirtyCanvas?.(true,true);}
app.registerExtension({
 name:"yue2.songStatus",
 beforeRegisterNodeDef(Node,data){
  if(data.name!==kind)return;
  const title=Node.prototype.getTitle;
  Node.prototype.getTitle=function(){return (this._yue2SongState?labels[this._yue2SongState]+"｜":"")+(title?.apply(this,arguments)||this.title);};
  const draw=Node.prototype.onDrawForeground;
  Node.prototype.onDrawForeground=function(ctx){
   draw?.apply(this,arguments);
   if(!this._yue2SongState)return;
   ctx.save();ctx.strokeStyle=this._yue2SongState==="complete"?"#55e08b":this._yue2SongState==="error"?"#ff6b73":"#ffca55";ctx.lineWidth=5;
   ctx.strokeRect(-2,-30,this.size[0]+4,(this.flags?.collapsed?0:this.size[1])+32);ctx.restore();
  };
  const created=Node.prototype.onNodeCreated;
  Node.prototype.onNodeCreated=function(){const r=created?.apply(this,arguments);this.addCustomWidget({name:"song_status",type:"yue2_usage",options:{serialize:false},computeSize:()=>[490,42],draw(ctx,node,width,y){ctx.save();ctx.fillStyle=node._yue2SongState==="complete"?"#124f2d":"#252525";ctx.fillRect(8,y+3,width-16,34);ctx.fillStyle="#fff";ctx.font="bold 16px sans-serif";ctx.fillText(labels[node._yue2SongState]||"未実行 / Ready",16,y+26);ctx.restore();}});return r;};
 },
 onNodeOutputsUpdated(outputs){for(const [id,o] of Object.entries(outputs||{}))if(o?.yue2_song?.length)mark(app.graph?.getNodeById(id),"complete");},
 setup(){
  let panel,timeout,active;
  const show=(text,error=false)=>{if(!panel){panel=document.createElement("div");panel.id="yue2-song-status";panel.setAttribute("role","status");panel.setAttribute("aria-live","polite");Object.assign(panel.style,{position:"fixed",top:"132px",left:"50%",transform:"translateX(-50%)",zIndex:100000,maxWidth:"min(760px,90vw)",padding:"16px 24px",borderRadius:"10px",border:"3px solid #55e08b",font:"bold 18px/26px system-ui",color:"#fff",textAlign:"center"});document.body.append(panel);}clearTimeout(timeout);panel.hidden=false;panel.style.background=error?"#5b151a":"#124f2d";panel.textContent=text;timeout=setTimeout(()=>{panel.hidden=true;},25000);};
  api.addEventListener("executing",({detail})=>{const id=detail?.node??detail;const n=app.graph?.getNodeById(id);if(n?.comfyClass===kind||n?.type===kind){active=String(id);mark(n,"running");if(panel)panel.hidden=true;}});
  api.addEventListener("executed",({detail})=>{const song=detail?.output?.yue2_song?.[0];if(!song)return;mark(app.graph?.getNodeById(detail.node),"complete");active=undefined;show(`✅ 曲の生成完了 / Song complete\n${song.title} · ${Number(song.seconds).toFixed(1)}秒\n③で再生・④に歌詞と曲情報 / Play in ③; details in ④`);});
  api.addEventListener("execution_error",({detail})=>{if(String(detail?.node_id)!==active)return;mark(app.graph?.getNodeById(active),"error");active=undefined;show("✕ 曲生成に失敗しました。実行エラーを確認してください / Song generation failed",true);});
  for(const event of ["execution_interrupted","reconnecting"])api.addEventListener(event,()=>{if(active===undefined)return;mark(app.graph?.getNodeById(active),"error");active=undefined;show(event==="reconnecting"?"接続断・処理状態は未確認 / Disconnected; status unknown":"曲生成を中断 / Song interrupted",true);});
 }
});