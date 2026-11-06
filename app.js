"use strict";
const $=id=>document.getElementById(id), key="own-ai-workspace-v2";
const uid=()=>crypto.randomUUID();
let state;try{state=JSON.parse(localStorage.getItem(key))}catch{}
if(!state||!Array.isArray(state.chats)||!Array.isArray(state.docs)||!Array.isArray(state.folders))state={chats:[],docs:[],folders:[],active:null,doc:null};
let model=null;try{model=JSON.parse(localStorage.getItem("own-ai-bigram-v1"))}catch{}
const save=()=>{try{localStorage.setItem(key,JSON.stringify(state))}catch{alert("Browser storage is full. Export your data before adding more.")}};
const active=()=>state.chats.find(c=>c.id===state.active);
function newChat(){const c={id:uid(),title:"New chat",folder:null,messages:[]};state.chats.unshift(c);state.active=c.id;save();render();section("chat")}
function render(){const h=$("history");h.replaceChildren();state.chats.forEach(c=>{const b=document.createElement("button");b.textContent=(c.id===state.active?"● ":"")+c.title;b.onclick=()=>{state.active=c.id;save();render();section("chat")};h.append(b)});const f=$("folders");f.replaceChildren();state.folders.forEach(folder=>{const b=document.createElement("button");b.textContent="▸ "+folder.name;b.onclick=()=>{const c=active();if(!c)return alert("Create a chat first.");c.folder=folder.id;save();alert("Chat moved to "+folder.name)};f.append(b)});const m=$("messages");m.replaceChildren();const c=active();if(!c||!c.messages.length){const p=document.createElement("h1");p.textContent="What would you like to explore?";m.append(p)}else c.messages.forEach(msg=>{const d=document.createElement("div");d.className="message "+msg.role;d.textContent=msg.text;m.append(d)});renderDocs()}
function section(name){document.querySelectorAll(".page").forEach(el=>el.classList.toggle("hidden",el.id!==name));$("pageTitle").textContent={chat:"Own AI",images:"Images",documents:"Documents",lab:"Model Lab"}[name]||name;if(innerWidth<701)$("sidebar").classList.add("closed")}
document.querySelectorAll("[data-section]").forEach(b=>b.onclick=()=>section(b.dataset.section));
$("newChat").onclick=newChat;$("toggle").onclick=()=>$("sidebar").classList.toggle("closed");
$("newFolder").onclick=()=>{const name=prompt("Folder name");if(!name?.trim())return;state.folders.push({id:uid(),name:name.trim()});save();render()};
function predict(promptText){
  const q=promptText.trim().toLowerCase();
  if(/^(hi|hello|hey|good morning|good evening)[!. ]*$/.test(q))return "Hello! This is Own AI Test. My conversational model is still being developed. You can switch to Other AI for a more capable assistant.";
  if(/^(thanks|thank you)[!. ]*$/.test(q))return "You're welcome!";
  if(/^(what can you do|help)[?.! ]*$/.test(q))return "I can save this conversation in your browser and provide a model-training playground. I cannot yet answer general questions reliably. Switch to Other AI for that.";
  return "Own AI Test is not yet trained well enough to answer this reliably. I won't generate random text and pretend it's an answer. Switch to Other AI for a capable chat service, or open Model Lab to experiment with training.";
}
$("composer").onsubmit=e=>{e.preventDefault();const text=$("prompt").value.trim();if(!text)return;if(!active())newChat();const c=active();c.messages.push({role:"user",text});if(c.title==="New chat")c.title=text.slice(0,40);c.messages.push({role:"ai",text:predict(text)});$("prompt").value="";save();render()};
$("train").onclick=()=>{const ids=Array.from($("corpus").value).map(c=>c.charCodeAt(0)).filter(n=>n>=0&&n<128);if(ids.length<2)return alert("Enter more training text.");const counts=Array.from({length:128},()=>new Float64Array(128).fill(.01));for(let i=0;i<ids.length-1;i++)counts[ids[i]][ids[i+1]]++;model=counts.map(row=>Array.from(row,n=>Math.log(n)));try{localStorage.setItem("own-ai-bigram-v1",JSON.stringify(model))}catch{}$("trainStatus").textContent="Trained on "+ids.length+" characters."};
function renderDocs(){const d=$("docList");d.replaceChildren();state.docs.forEach(doc=>{const b=document.createElement("button");b.textContent="▤ "+doc.title;b.onclick=()=>openDoc(doc.id);d.append(b)})}
function openDoc(id){state.doc=id;const d=state.docs.find(x=>x.id===id);$("editor").classList.remove("hidden");$("docTitle").value=d.title;$("docBody").value=d.body;save()}
$("newDoc").onclick=()=>{const d={id:uid(),title:"Untitled document",body:""};state.docs.unshift(d);save();renderDocs();openDoc(d.id)};
$("saveDoc").onclick=()=>{const d=state.docs.find(x=>x.id===state.doc);if(!d)return;d.title=$("docTitle").value||"Untitled document";d.body=$("docBody").value;save();renderDocs()};
$("deleteDoc").onclick=()=>{if(!state.doc||!confirm("Delete this document?"))return;state.docs=state.docs.filter(x=>x.id!==state.doc);state.doc=null;save();$("editor").classList.add("hidden");renderDocs()};
$("pdfDoc").onclick=()=>{const d=state.docs.find(x=>x.id===state.doc);if(!d)return alert("Create a document first.");$("saveDoc").click();let print=$("printDoc");if(!print){print=document.createElement("div");print.id="printDoc";print.hidden=true;document.body.append(print)}print.textContent=$("docTitle").value+"\n\n"+$("docBody").value;print.hidden=false;window.print();print.hidden=true};
$("imageUpload").onchange=e=>{for(const file of e.target.files){if(!file.type.startsWith("image/"))continue;const img=document.createElement("img");img.alt=file.name;img.src=URL.createObjectURL(file);$("gallery").append(img)}};
if(!state.chats.length)newChat();else{render();section("chat")}

// Separate experimental and third-party AI experiences.
$("testMode").onclick=()=>{ $("ownChat").classList.remove("hidden");$("externalChat").classList.add("hidden");$("testMode").setAttribute("aria-pressed","true");$("otherMode").setAttribute("aria-pressed","false") };
$("otherMode").onclick=()=>{ $("ownChat").classList.add("hidden");$("externalChat").classList.remove("hidden");$("testMode").setAttribute("aria-pressed","false");$("otherMode").setAttribute("aria-pressed","true") };
