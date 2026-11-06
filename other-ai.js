// On-device third-party language model. Separate from the self-coded Own AI test model.
// WebLLM downloads public model artifacts and performs inference locally with WebGPU.
"use strict";
const byId=id=>document.getElementById(id);
let engine=null, busy=false;
const history=[{role:"system",content:"You are a helpful, concise assistant. If unsure, say so."}];
function status(message){byId("externalStatus").textContent=message}
function addMessage(role,text){
  const el=document.createElement("div");
  el.className="message "+(role==="user"?"user":"ai");
  el.textContent=text;
  byId("externalMessages").append(el);
  el.scrollIntoView({block:"nearest"});
  return el;
}
byId("loadExternal").onclick=async()=>{
  if(busy||engine)return;
  if(!("gpu" in navigator)){status("WebGPU unavailable on this browser. Try Chrome or a newer Safari.");return}
  busy=true;byId("loadExternal").disabled=true;
  try{
    status("Loading WebLLM library...");
    const webllm=await import("https://esm.run/@mlc-ai/web-llm@0.2.87");
    const preferred=["Qwen2-0.5B-Instruct-q4f16_1-MLC","Qwen2-0.5B-Instruct-q4f32_1-MLC","Llama-3.2-1B-Instruct-q4f16_1-MLC"];
    const available=webllm.prebuiltAppConfig.model_list.map(x=>x.model_id);
    const chosen=preferred.find(x=>available.includes(x))||available.find(x=>/0\.5B.*Instruct/i.test(x));
    if(!chosen)throw Error("No supported small instruction model was found in the installed WebLLM library.");
    status("Downloading "+chosen+" — this can take several minutes...");
    engine=await webllm.CreateMLCEngine(chosen,{initProgressCallback:p=>status(p.text||"Loading model...")});
    status("Ready: "+chosen);
    byId("externalSend").disabled=false;
    byId("loadExternal").textContent="Model loaded";
  }catch(err){
    status("Could not load model: "+(err?.message||String(err)));
    byId("loadExternal").disabled=false;
  }finally{busy=false}
};
byId("externalForm").onsubmit=async e=>{
  e.preventDefault();
  const text=byId("externalPrompt").value.trim();
  if(!text||!engine||busy)return;
  busy=true;byId("externalSend").disabled=true;
  byId("externalPrompt").value="";
  addMessage("user",text);
  history.push({role:"user",content:text});
  const reply=addMessage("assistant","Thinking...");
  try{
    const result=await engine.chat.completions.create({messages:history,max_tokens:256,temperature:0.7});
    const answer=result.choices?.[0]?.message?.content||"No response generated.";
    reply.textContent=answer;
    history.push({role:"assistant",content:answer});
    status("Ready");
  }catch(err){
    reply.textContent="Generation failed: "+(err?.message||String(err));
    history.pop();
    status("Error generating reply");
  }finally{busy=false;byId("externalSend").disabled=false}
};
