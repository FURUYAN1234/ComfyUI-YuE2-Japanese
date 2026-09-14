import {app} from '/scripts/app.js';
import {api} from '/scripts/api.js';
const opened=new Map();
function show(item){
 if(opened.has(item.request_id))return;
 const dialog=document.createElement('dialog');opened.set(item.request_id,dialog);
 Object.assign(dialog.style,{width:'min(1100px,92vw)',maxHeight:'90vh',overflow:'auto',background:'#20242c',color:'#fff',border:'1px solid #64748b',borderRadius:'12px',padding:'22px',zIndex:10000});
 const add=(tag,text,parent=dialog)=>{const el=document.createElement(tag);if(text)el.textContent=text;parent.append(el);return el;};
 add('h2','歌詞の読みを確認 / Review lyric readings');add('strong',item.title);
 add('p','読みを修正してから曲生成へ進みます。表示歌詞は保持されます。 / Confirm readings before generating; display lyrics stay unchanged.');
 const field=(label,value,readonly,parent=dialog)=>{const box=add('label',label,parent);const t=add('textarea','',box);t.value=value;t.readOnly=readonly;Object.assign(t.style,{display:'block',width:'100%',height:'76px',boxSizing:'border-box',fontSize:'16px',lineHeight:'1.6'});return t;};
 const original=item.lyrics.split('\n'),initial=item.singing_lyrics.split('\n');const readingFields=[];
 const rows=add('div');Object.assign(rows.style,{display:'grid',gap:'12px',marginTop:'16px'});
 for(let i=0;i<original.length;i++){
   if(!original[i].trim())continue;
   if(original[i].trim().startsWith('[')){add('h3',original[i],rows);continue;}
   const row=add('div','',rows);Object.assign(row.style,{padding:'12px',background:'#111827',borderRadius:'8px'});
   add('div',`${readingFields.length+1}. 元の歌詞 / Original`,row);add('p',original[i],row);
   const input=field('読み（編集できます） / Reading',initial[i]??original[i],false,row);input.setAttribute('aria-label',`歌詞${readingFields.length+1}の読み`);readingFields.push(input);
 }
 const action=add('select');action.setAttribute('aria-label','辞書の操作');for(const label of ['今回だけ / Once','記憶・更新 / Remember','登録を削除 / Delete']){const opt=add('option',label,action);opt.value=label;}action.value=item.action;
 add('p','単語=よみ を1行ずつ入力（例：今日=きょう）。削除は単語だけ。 / One word=reading per line; deletion uses words only.');
 const edits=field('読みの修正 / Corrections',item.corrections,false,dialog);edits.style.height='100px';edits.setAttribute('aria-label','読みの修正');
 const details=add('details');add('summary','記憶した読み / Remembered readings',details);add('pre',Object.entries(item.remembered||{}).map(([k,v])=>k+'='+v).join('\n')||'登録なし / Empty',details);
 const error=add('p');error.setAttribute('role','status');error.style.color='#fbbf24';
 const buttons=add('div');Object.assign(buttons.style,{display:'flex',gap:'12px',marginTop:'12px'});
 async function request(op,cancelled=false){const r=await api.fetchApi('/yue2/reading-review/'+op,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request_id:item.request_id,action:action.value,corrections:edits.value,readings:readingFields.map(t=>t.value),cancelled})});const data=await r.json();if(!r.ok)throw Error(data.error||r.statusText);return data;}
 const close=()=>{dialog.close();dialog.remove();opened.delete(item.request_id);};
 const button=(text,fn)=>{const b=add('button',text,buttons);b.style.padding='10px 16px';b.onclick=async()=>{b.disabled=true;error.textContent='';try{await fn();}catch(e){error.textContent=e.message;}finally{b.disabled=false;}};return b;};
 button('読みをプレビュー / Preview',async()=>{const result=(await request('preview')).singing_lyrics.split('\n').filter(l=>l.trim()&&!l.trim().startsWith('['));result.forEach((line,i)=>readingFields[i].value=line);error.textContent='プレビュー反映済み / Preview updated';});
 button('この読みで曲生成 / Generate song',async()=>{await request('submit');close();});
 button('生成を中止 / Cancel',async()=>{await request('submit',true);close();});
 dialog.addEventListener('cancel',e=>{e.preventDefault();error.textContent='中止する場合は「生成を中止」を押してください。';});
 document.body.append(dialog);dialog.showModal();
}
app.registerExtension({name:'yue2.readingReview',setup(){
 api.addEventListener('yue2.reading_review',e=>show(e.detail));
 const recover=async()=>{try{const r=await api.fetchApi('/yue2/reading-review/pending');if(r.ok){const data=await r.json();for(const p of data.pending)show(p);for(const [id,d] of opened)if(!data.pending.some(p=>p.request_id===id)){d.close();d.remove();opened.delete(id);}}}catch{}};
 api.addEventListener('reconnected',recover);recover();setInterval(recover,5000);
}});