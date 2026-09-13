const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const source = fs.readFileSync(process.argv[2], 'utf8').replace(/^import .*;\r?\n/, '');
let extension;
vm.runInNewContext(source, {app:{registerExtension:e=>extension=e}});
function Node(){this.widgets=['mode','voice','genre','mood','instruments','bpm','timing','seconds'].map(name=>({name,value:name==='seconds'?30:'unchanged'}));}
Node.prototype.addWidget=function(type,name,value,callback){const w={type,name,value,callback};this.widgets.push(w);return w;};
Node.prototype.setDirtyCanvas=function(){};
extension.beforeRegisterNodeDef(Node,{name:'YuE2SongOptions'});
const n=new Node();n.onNodeCreated();
const buttons=n.widgets.filter(w=>w.type==='button');assert.equal(buttons.length,5);
const outputs=[];
for(const button of buttons){button.callback(); const values=Object.fromEntries(n.widgets.filter(w=>w.type!=='button').map(w=>[w.name,w.value]));assert.equal(values.mode,'プリセット');assert.equal(values.seconds,30);assert.equal(values.timing,'unchanged');assert.equal(button.options.serialize,false);outputs.push(values);}
console.log(JSON.stringify(outputs));