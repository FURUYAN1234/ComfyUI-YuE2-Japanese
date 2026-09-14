import {app} from '/scripts/app.js';
import {api} from '/scripts/api.js';
const opened=new Map();
function show(item){
 if(opened.has(item.request_id))return;
 const dialog=document.createElement('dialog');opened.set(item.request_id,dialog);
 Object.assign(dialog.style,{width:'min(1100px,92vw)',height:'min(92vh,1000px)',maxHeight:'92vh',overflow:'hidden',background:'#20242c',color:'#fff',border:'1px solid #64748b',borderRadius:'12px',padding:'22px',zIndex:10000});
 const body=document.createElement('div');Object.assign(body.style,{overflow:'auto',flex:'1 1 auto',minHeight:'0',paddingRight:'4px'});dialog.append(body);
 const add=(tag,text,parent=body)=>{const el=document.createElement(tag);if(text)el.textContent=text;parent.append(el);return el;};
 add('h2','歌詞の読みを確認 / Review lyric readings');add('strong',item.title);
 add('p','読みを修正してから曲生成へ進みます。表示歌詞は保持されます。 / Confirm readings before generating; display lyrics stay unchanged.');
 const field=(label,value,readonly,parent=body)=>{const box=add('label',label,parent);const t=add('textarea','',box);t.value=value;t.readOnly=readonly;Object.assign(t.style,{display:'block',width:'100%',height:'76px',boxSizing:'border-box',fontSize:'16px',lineHeight:'1.6'});return t;};
 const original=item.lyrics.split('\n'),initial=item.singing_lyrics.split('\n');const readingFields=[];
 add('p',`全${original.filter(l=>l.trim()&&!l.trim().startsWith('[')).length}行 / All lyric lines — 下へスクロールして最後まで確認できます`);
 const rows=add('div');Object.assign(rows.style,{display:'grid',gap:'12px',marginTop:'16px'});
 for(let i=0;i<original.length;i++){
   if(!original[i].trim())continue;
   if(original[i].trim().startsWith('[')){add('h3',original[i],rows);continue;}
   const row=add('div','',rows);Object.assign(row.style,{padding:'12px',background:'#111827',borderRadius:'8px'});
   add('div',`${readingFields.length+1}. 元の歌詞 / Original`,row);add('p',original[i],row);
   const input=field('ひらがなの読み（編集できます） / Hiragana reading',initial[i]??original[i],false,row);input.setAttribute('aria-label',`歌詞${readingFields.length+1}の読み`);readingFields.push(input);
 }
 add('p','自動変換の読み候補です。人名・多義語は確認してください。英数字などが残る行は、ひらがなで指定してから進めます。 / Review automatic readings, especially names; replace unresolved letters or numbers.');
 const dictionaryOption=add('label');Object.assign(dictionaryOption.style,{display:'flex',gap:'8px',alignItems:'center',margin:'14px 0'});
 const remember=add('input','',dictionaryOption);remember.type='checkbox';remember.checked=item.action==='記憶・更新 / Remember';add('span','手で修正した読みを発音辞書へ登録する',dictionaryOption);
 const details=add('details');add('summary','記憶した読みを確認 / Remembered readings',details);add('pre',Object.entries(item.remembered||{}).map(([k,v])=>k+'='+v).join('\n')||'登録なし / Empty',details);
 const error=add('p','',dialog);error.setAttribute('role','status');error.style.color='#fbbf24';
 const buttons=add('div','',dialog);Object.assign(buttons.style,{display:'flex',flex:'0 0 auto',justifyContent:'flex-end',gap:'12px',paddingTop:'14px',borderTop:'1px solid #555'});
 async function request(op,cancelled=false){const r=await api.fetchApi('/yue2/reading-review/'+op,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request_id:item.request_id,action:remember.checked?'記憶・更新 / Remember':'今回だけ / Once',corrections:item.action==='登録を削除 / Delete'?'':item.corrections,readings:readingFields.map(t=>t.value),cancelled})});const data=await r.json();if(!r.ok)throw Error(data.error||r.statusText);return data;}
 for(const input of readingFields)input.addEventListener('input',()=>{error.textContent='';});
 const close=()=>{dialog.close();dialog.remove();opened.delete(item.request_id);};
 const button=(text,fn)=>{const b=add('button',text,buttons);b.style.padding='10px 16px';b.onclick=async()=>{b.disabled=true;error.textContent='';try{await fn();}catch(e){error.textContent=e.message;}finally{b.disabled=false;}};return b;};
 button('今回の生成を中止',async()=>{await request('submit',true);close();});
 button('この読みで曲を生成',async()=>{await request('submit');close();});
 dialog.addEventListener('cancel',e=>{e.preventDefault();error.textContent='中止する場合は「生成を中止」を押してください。';});
 document.body.append(dialog);dialog.showModal();dialog.style.display='flex';dialog.style.flexDirection='column';
}
app.registerExtension({name:'yue2.readingReview',setup(){
 api.addEventListener('yue2.reading_review',e=>show(e.detail));
 const recover=async()=>{try{const r=await api.fetchApi('/yue2/reading-review/pending');if(r.ok){const data=await r.json();for(const p of data.pending)show(p);for(const [id,d] of opened)if(!data.pending.some(p=>p.request_id===id)){d.close();d.remove();opened.delete(id);}}}catch{}};
 api.addEventListener('reconnected',recover);recover();setInterval(recover,5000);
}});