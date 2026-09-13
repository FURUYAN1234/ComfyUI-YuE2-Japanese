const fs=require('fs');
(async()=>{
const path=require('path').join(__dirname,'../custom_nodes/comfyui-yue2-local/web/lyrics.js');
const js=fs.readFileSync(path,'utf8').replace('import { app } from "/scripts/app.js";','const app={registerExtension(){}};');
const {readableLyrics}=await import('data:text/javascript;base64,'+Buffer.from(js).toString('base64'));
const assert=require('assert/strict');
const data={title:'雨の歌',lyrics:'[Verse]\n雨の道\n街の灯り\n\n[Chorus]\n明日へ',style:'Japanese pop',audio_seconds:39.5587,folder:'/home/furu/ComfyUI/output/audio/YuE2/test',note:'確認'};
const source=JSON.stringify(data);const shown=readableLyrics(source);
assert(shown.includes('雨の道\n街の灯り'));assert(!shown.includes('\\n'));assert(shown.includes('曲名 / Title：雨の歌'));assert.equal(JSON.parse(source).lyrics,data.lyrics);
for(const x of ['hello','{bad',null,JSON.stringify({...data,folder:'/other/path'}),JSON.stringify({...data,lyrics:42})])assert.equal(readableLyrics(x),x);
console.log('PASS readable lyrics, literal newlines, original JSON, unrelated and malformed inputs');
})();
