// Educational neural language model, written from scratch in JavaScript.
// A trainable 128x128 character transition-logit matrix with softmax.
// This is NOT the Python Transformer. It learns one-character context only.
"use strict";
const V=128;
let weights=null;
const $=id=>document.getElementById(id);
function softmax(row){
  const m=Math.max(...row);
  const e=row.map(x=>Math.exp(x-m));
  const s=e.reduce((a,b)=>a+b,0);
  return e.map(x=>x/s);
}
function encode(text){return Array.from(text).map(c=>c.charCodeAt(0)).filter(x=>x>=0&&x<V)}
function train(text){
  const ids=encode(text);
  if(ids.length<2) throw Error("Enter at least two ASCII characters.");
  const counts=Array.from({length:V},()=>new Float64Array(V).fill(0.01));
  for(let i=0;i<ids.length-1;i++) counts[ids[i]][ids[i+1]]++;
  // Maximum-likelihood logits for a categorical neural bigram model.
  weights=counts.map(row=>Array.from(row,x=>Math.log(x)));
  localStorage.setItem("own-ai-bigram-v1",JSON.stringify(weights));
  return ids.length;
}
function sample(probs){
  let r=Math.random();
  for(let i=0;i<probs.length;i++){r-=probs[i];if(r<=0)return i}
  return probs.length-1;
}
function generate(prompt,n){
  if(!weights) throw Error("Train the model first.");
  let ids=encode(prompt);
  let current=ids.length?ids[ids.length-1]:32;
  let result="";
  for(let i=0;i<n;i++){
    current=sample(softmax(weights[current]));
    result+=String.fromCharCode(current);
  }
  return prompt+result;
}
$("train").onclick=()=>{
  try{const count=train($("corpus").value);$("status").textContent="Trained on "+count+" characters";$("output").textContent="Ready to generate."}
  catch(e){$("status").textContent=e.message}
};
$("reset").onclick=()=>{weights=null;localStorage.removeItem("own-ai-bigram-v1");$("status").textContent="Not trained";$("output").textContent="Train the model first."};
$("generate").onclick=()=>{
  try{$("output").textContent=generate($("prompt").value,Math.max(1,Math.min(500,Number($("length").value)||160)))}
  catch(e){$("output").textContent=e.message}
};
try{const saved=JSON.parse(localStorage.getItem("own-ai-bigram-v1"));if(Array.isArray(saved)&&saved.length===V&&saved.every(row=>Array.isArray(row)&&row.length===V&&row.every(Number.isFinite))){weights=saved;$("status").textContent="Saved model loaded"}}catch(e){/* ignore corrupt local data */}
