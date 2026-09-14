const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8').replace(/^import .*;\r?\n/, '');
let extension;
const mockApp={registerExtension:e=>extension=e};
vm.runInNewContext(source, {app:mockApp,queueMicrotask:fn=>fn()});
function Node(){this.widgets=['mode','voice','genre','mood','instruments','bpm','timing','seconds'].map(name=>({name,value:name==='seconds'?30:'unchanged'}));}
Node.prototype.addWidget=function(type,name,value,callback){const w={type,name,value,callback};this.widgets.push(w);return w;};
Node.prototype.setDirtyCanvas=function(){};
extension.beforeRegisterNodeDef(Node,{name:'YuE2SongOptions'});
const n=new Node();n.onNodeCreated();
const buttons=n.widgets.filter(w=>w.type==='button');assert.equal(buttons.length,11);
const outputs=[];
for(const button of buttons){button.callback(); const values=Object.fromEntries(n.widgets.filter(w=>w.type!=='button').map(w=>[w.name,w.value]));assert.equal(values.mode,'プリセット');assert.equal(values.seconds,30);assert.equal(values.timing,'unchanged');assert.equal(button.options.serialize,false);outputs.push(values);}
console.log(JSON.stringify(outputs));
function SwitchNode(){this.widgets=['use_presets','use_manual','voice','genre','mood','instruments','bpm','timing','seconds'].map(name=>({name,value:name==='use_manual'?true:false}));}
SwitchNode.prototype.addWidget=Node.prototype.addWidget;
SwitchNode.prototype.setDirtyCanvas=Node.prototype.setDirtyCanvas;
extension.beforeRegisterNodeDef(SwitchNode,{name:'YuE2SongSwitches'});
const sn=new SwitchNode();sn.onNodeCreated();
for(const w of sn.widgets.filter(w=>w.type==='button')){w.callback();assert.equal(sn.widgets.find(w=>w.name==='use_presets').value,true);assert.equal(sn.widgets.find(w=>w.name==='use_manual').value,true);}
console.log('New preset buttons preserve manual ON: PASS');
const pw=sn.widgets.find(w=>w.name==='use_presets');
const mw=sn.widgets.find(w=>w.name==='use_manual');
function toggle(w,value){w.value=value;w.callback(value);}
toggle(pw,false);assert.equal(pw.value,false);assert.equal(mw.value,true);
toggle(mw,false);assert.equal(mw.value,true);assert.equal(pw.value,false);
toggle(pw,true);toggle(mw,false);assert.equal(mw.value,false);assert.equal(pw.value,true);
toggle(pw,false);assert.equal(pw.value,true);assert.equal(mw.value,false);
for(const [p,m,ep,em] of [[false,false,true,false],[false,true,false,true],[true,false,true,false],[true,true,true,true]]){
 pw.value=p;mw.value=m;sn.onConfigure();assert.equal(pw.value,ep);assert.equal(mw.value,em);
}
console.log('Last-ON guard and all restored states: PASS');
const manualNode={id:7,type:'YuE2ManualLyrics',widgets:['title','lyrics','style'].map(name=>({name,value:'keep text',inputEl:{style:{}}}))};
sn.id=6;sn.type='YuE2SongSwitches';
const plannerNode={id:2,type:'YuE2JapanesePlanner',inputs:[{name:'settings',link:1},{name:'manual',link:2}]};
mockApp.graph={_nodes:[sn,manualNode,plannerNode],links:{1:{origin_id:6},2:{origin_id:7}},getNodeById:id=>id===6?sn:manualNode,setDirtyCanvas:()=>{}};
pw.value=true;toggle(mw,false);
for(const w of manualNode.widgets){assert.equal(w.disabled,true);assert.equal(w.inputEl.disabled,true);assert.equal(w.inputEl.readOnly,true);assert.equal(w.value,'keep text');}
toggle(mw,true);
for(const w of manualNode.widgets){assert.equal(w.disabled,w.name==='title');assert.equal(w.inputEl.disabled,w.name==='title');assert.equal(w.inputEl.readOnly,w.name==='title');assert.equal(w.value,'keep text');}
console.log('Manual OFF disables fields; ON restores without data loss: PASS');const external={id:8,type:'YuE2InputSwitches',widgets:[{name:'use_presets',value:false},{name:'use_manual',value:true}]};
const presetNode={id:9,type:'YuE2PresetOptions',widgets:[{name:'voice',value:'original'}]};
plannerNode.inputs=[{name:'switches',link:3},{name:'settings',link:4},{name:'manual',link:2}];
mockApp.graph._nodes=[external,presetNode,manualNode,plannerNode];mockApp.graph.links[3]={origin_id:8};mockApp.graph.links[4]={origin_id:9};mockApp.graph.getNodeById=id=>mockApp.graph._nodes.find(n=>n.id===id);
extension.afterConfigureGraph();assert.equal(presetNode.widgets[0].disabled,true);assert.equal(manualNode.widgets[0].disabled,true);assert.equal(manualNode.widgets[1].disabled,false);
presetNode.widgets[0].value='changed';presetNode.widgets[0].callback('changed');assert.equal(presetNode.widgets[0].value,'original');
external.widgets[0].value=true;external.widgets[1].value=false;extension.afterConfigureGraph();assert.equal(presetNode.widgets[0].disabled,false);assert.equal(manualNode.widgets[0].disabled,true);
console.log('External controller disables the correct linked node and preserves values: PASS');
plannerNode.type='YuE2LyricPlanner';plannerNode.widgets=[{name:'lyric_length',value:'短い試作（4行）'},{name:'lyric_lines',value:7}];
extension.afterConfigureGraph();assert.equal(plannerNode.widgets[0].disabled,false);assert.equal(plannerNode.widgets[1].disabled,true);
plannerNode.widgets[0].value='自由に指定';extension.afterConfigureGraph();assert.equal(plannerNode.widgets[1].disabled,false);
external.widgets[1].value=true;extension.afterConfigureGraph();assert.equal(plannerNode.widgets[0].disabled,true);assert.equal(plannerNode.widgets[1].disabled,true);assert.equal(plannerNode.widgets[1].value,7);
external.widgets[1].value=false;extension.afterConfigureGraph();assert.equal(plannerNode.widgets[0].disabled,false);assert.equal(plannerNode.widgets[1].disabled,false);
console.log('Custom lyric lines and manual OFF/ON enabled states: PASS');

const recursiveWidget=manualNode.widgets[1];let stored=recursiveWidget.value;let callbackCount=0;
Object.defineProperty(recursiveWidget,'value',{get(){return stored;},set(v){stored=v;if(++callbackCount>5)throw Error('Recursive disabled callback');recursiveWidget.callback(v);}});
recursiveWidget.value='unwanted mutation';assert.equal(recursiveWidget.value,'keep text');assert.equal(callbackCount,2);
console.log('DOM value setter callback does not recurse on disabled inputs: PASS');
