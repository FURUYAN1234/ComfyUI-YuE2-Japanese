const fs=require('fs'),vm=require('vm'),assert=require('assert');
class E{constructor(tag){this.tag=tag;this.style={};this.children=[];this.events={};this.scrollHeight=1000;this.clientHeight=180;this.currentTime=0;this.duration=100;}append(x){this.children.push(x)}replaceChildren(){this.children=[]}setAttribute(){}addEventListener(n,f){this.events[n]=f}insertBefore(a,b){this.children.splice(this.children.indexOf(b),0,a)}}
const src=fs.readFileSync('/home/furu/Codex/work/yue2/project/custom_nodes/comfyui-yue2-local/web/media_outputs.js','utf8').replace(/import .*?;\n/,'');
const context={app:{registerExtension(){}},document:{createElement:t=>new E(t)},URLSearchParams};vm.createContext(context);vm.runInContext(src,context);
const root=new E('div');context.node={_yue2Media:root,size:[500,450],setSize(){}};context.item={kind:'audio',title:'test',seconds:100,lyrics:'one\ntwo',play:'a.flac',download:'a.flac',subfolder:'audio'};vm.runInContext('render(node,item)',context);
const audio=root.children.find(x=>x.tag==='audio'),lyrics=root.children.find(x=>x.tag==='pre'),button=root.children.find(x=>x.tag==='button');
audio.currentTime=50;audio.events.timeupdate();assert.equal(lyrics.scrollTop,410);
lyrics.events.wheel();audio.currentTime=75;audio.events.timeupdate();assert.equal(lyrics.scrollTop,410);
button.events.click();assert.equal(lyrics.scrollTop,615);
audio.currentTime=0;audio.events.seeked();assert.equal(lyrics.scrollTop,0);
audio.currentTime=100;audio.events.ended();assert.equal(lyrics.scrollTop,820);
console.log('PASS: progress, manual pause, resume, seek, end');