// The original approval is a fixture. Each amendment is a separate scenario.
const comparison = document.createElement("section");
comparison.id = "compare";
comparison.innerHTML = `<div class="amend-head"><div><h2>Amendment review</h2>
<p>Compare each revision with the same confirmed filing for series AF-27.</p></div>
<label>Revision<select id="revision"></select></label></div>
<div class="versions"><section><div class="sheet-head"><span>Original filing</span><span>Confirmed in fixture</span></div><ol class="transcript" id="before"></ol></section>
<section><div class="sheet-head"><span>Revised filing</span><span id="newVersion"></span></div><ol class="transcript" id="after"></ol></section></div>
<div class="amend-decision"><div><h3 id="outcome" aria-live="polite"></h3><p id="explain"></p></div><div class="actions"><button id="approveRevision">Confirm revised issuer</button><button class="secondary" id="reopenRevision">Reopen decision</button></div></div>
<details><summary>Amendment decision history</summary><ol id="revisionAudit"></ol></details><a class="back" href="#review">Back to note review</a>`;
document.querySelector("main").append(comparison);
revisions.forEach(v=>el("revision").add(new Option("Amendment "+v.version,v.version)));
function displayVersion(id, lines, other){
  el(id).replaceChildren(...lines.map(text=>{
    const li=document.createElement("li"), span=document.createElement(other.includes(text)?"span":"mark");
    span.textContent=text;li.append(span);return li;
  }));
}
function revisionState(){
  const v=revisions[el("revision").selectedIndex];
  const history=events.filter(e=>e.series===v.series && e.version===v.version);
  return {v,history,approved:history.at(-1)?.action==="Confirmed"};
}
function paintRevision(){
  const {v,history,approved}=revisionState(), [status,reason,name]=v.decision;
  displayVersion("before",original.lines,v.lines);displayVersion("after",v.lines,original.lines);
  el("newVersion").textContent=v.series+" · amendment "+v.version;
  el("outcome").textContent=approved?"Confirmed for "+v.version+" · "+name:status;
  el("explain").textContent=approved?"Directory "+entities[name]+". The original still records Alder Funding LLC.":reason;
  el("approveRevision").disabled=approved||!name;el("reopenRevision").disabled=!approved;
  el("revisionAudit").replaceChildren(...history.map(e=>{const li=document.createElement("li");li.textContent=[e.at,e.series,e.version,e.action,e.name,e.id,"line "+e.lines.join(", ")].join(" · ");return li}));
}
function recordRevision(action){
  const {v,approved}=revisionState(),[,,name,lines]=v.decision;
  if(!name || (action==="Confirmed")===approved)return;
  events.push({series:v.series,version:v.version,action,at:new Date().toISOString(),name,id:entities[name],lines});
  localStorage.setItem(key,JSON.stringify(events));paintRevision();
}
el("revision").onchange=paintRevision;
el("approveRevision").onclick=()=>recordRevision("Confirmed");
el("reopenRevision").onclick=()=>recordRevision("Reopened");
paintRevision();
