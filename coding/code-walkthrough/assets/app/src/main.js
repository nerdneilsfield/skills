import D from "./data.json";
import "./style.css";

const NS="http://www.w3.org/2000/svg";
const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
const el=(t,c,x)=>{const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e};
const sv=(t,a={})=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);return e};
document.title=D.title;
document.getElementById("title").textContent=D.title;
document.getElementById("summary").textContent=D.summary;
document.getElementById("meta").textContent=[D.repo,D.commit].filter(Boolean).join(" @ ");
document.getElementById("foot").textContent="虚线和“推断”标记的内容未在源码中逐一证实。位置基于上述 commit。";
const main=document.getElementById("main"),nav=document.getElementById("nav");
const LEVELS=[["l1","一 全貌"],["l2","二 结构"],["l3","三 调用"]];
if((D.terms||[]).length)LEVELS.push(["l4","四 术语"]);
if(D.graph)LEVELS.push(["l5","五 图谱"]);
LEVELS.forEach(([id,t])=>{const a=el("a",null,t);a.href="#"+id;nav.append(a)});
function section(id,title,intro){const s=el("section");s.id=id;s.append(el("h2",null,title));if(intro)s.append(el("p","intro",intro));main.append(s);return s}
function describe(box,o){box.replaceChildren();box.append(el("h3",null,o.title||o.label));
  if(o.file){const l=el("div","loc",o.file+(o.line?":"+o.line:""));const t=el("span","tag"+(o.verified===false?" inferred":""),o.verified===false?"推断":"已核对");l.append(t);box.append(l)}
  const b=o.explain||o.summary;if(b)box.append(el("p",null,b));if(o.code)box.append(el("pre",null,o.code))}
/* layered layout: each node declares layer and optional band */
const W=760,NW=150,NH=46,GAPY=96,TOP=40;
const layers=[...new Set(D.nodes.map(n=>n.layer))].sort((a,b)=>a-b);
const pos={};
layers.forEach((L,i)=>{const row=D.nodes.filter(n=>n.layer===L);const step=W/(row.length+1);
  row.forEach((n,j)=>{pos[n.id]={x:step*(j+1),y:TOP+i*GAPY}})});
const H=TOP+layers.length*GAPY;
function drawMap(host,onPick){const s=sv("svg",{class:"map",viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":D.title});
  const edges={},nodes={};
  D.edges.forEach(e=>{const a=pos[e.from],b=pos[e.to];const my=(a.y+b.y)/2;
    const p=sv("path",{class:"edge"+(e.verified===false?" inferred":""),d:`M${a.x} ${a.y+NH/2} C${a.x} ${my},${b.x} ${my},${b.x} ${b.y-NH/2}`});
    edges[e.from+">"+e.to]=p;s.append(p)});
  D.nodes.forEach(n=>{const g=sv("g",{class:"node",tabindex:"0",role:"button","aria-label":n.label});const c=pos[n.id];
    g.append(sv("rect",{x:c.x-NW/2,y:c.y-NH/2,width:NW,height:NH,rx:2}));
    const t=sv("text",{x:c.x,y:c.y+5,"text-anchor":"middle"});t.textContent=n.label;g.append(t);
    const pick=()=>{Object.values(nodes).forEach(x=>x.classList.remove("sel"));g.classList.add("sel");onPick(n)};
    g.addEventListener("click",pick);g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();pick()}});
    nodes[n.id]=g;s.append(g)});
  host.append(s);return {svg:s,nodes,edges}}
/* level one */
const s1=section("l1","全貌",D.overview||"");
const list=el("dl","terms");(D.stages||[]).forEach(x=>{list.append(el("dt",null,x.name),el("dd",null,x.text))});if((D.stages||[]).length)s1.append(list);
/* level two */
const s2=section("l2","结构","点击模块查看职责和入口位置。");const g2=el("div","grid");s2.append(g2);
const left2=el("div"),box2=el("aside");g2.append(left2,box2);drawMap(left2,n=>describe(box2,n));describe(box2,D.nodes[0]);
const lg=el("p","legend","实线为已核对的调用，虚线为推断。");left2.append(lg);
/* level three */
const s3=section("l3","调用","选一个问题，看一次调用怎样走过代码。方向键单步，空格播放。");
const pick=el("div","flows");s3.append(pick);const g3=el("div","grid");s3.append(g3);
const left3=el("div"),box3=el("aside");g3.append(left3,box3);
const map=drawMap(left3,n=>describe(box3,n));
const ctl=el("div","ctl"),prev=el("button",null,"上一步"),play=el("button",null,"播放"),next=el("button",null,"下一步"),count=el("span","count");ctl.append(prev,play,next,count);left3.append(ctl);
const bar=el("div","bar"),fill=el("i");bar.append(fill);left3.append(bar);
const pulse=sv("circle",{class:"pulse",r:6,opacity:0});map.svg.append(pulse);
let flow=D.flows[0],idx=0,timer=null,raf=null;
function clear(){Object.values(map.nodes).forEach(n=>n.classList.remove("act","dim"));Object.values(map.edges).forEach(e=>e.classList.remove("act"))}
function fly(path){cancelAnimationFrame(raf);if(!path||reduce){pulse.setAttribute("opacity",0);return}
  const len=path.getTotalLength(),t0=performance.now(),dur=650;pulse.setAttribute("opacity",1);
  const go=t=>{const k=Math.min(1,(t-t0)/dur),e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2,p=path.getPointAtLength(len*e);pulse.setAttribute("cx",p.x);pulse.setAttribute("cy",p.y);
    if(k<1)raf=requestAnimationFrame(go);else pulse.setAttribute("opacity",0)};raf=requestAnimationFrame(go)}
function show(){const st=flow.steps[idx];clear();const used=new Set(flow.steps.flatMap(s=>[s.from,s.to]));
  Object.entries(map.nodes).forEach(([id,n])=>{if(!used.has(id))n.classList.add("dim")});
  map.nodes[st.to].classList.add("act");if(st.from)map.nodes[st.from].classList.add("act");
  const p=map.edges[st.from+">"+st.to]||null;if(p)p.classList.add("act");fly(p);
  describe(box3,st);count.textContent=`${idx+1} / ${flow.steps.length}`;fill.style.width=((idx+1)/flow.steps.length*100)+"%"}
function stop(){clearInterval(timer);timer=null;play.textContent="播放"}
function step(d){idx=Math.max(0,Math.min(flow.steps.length-1,idx+d));show()}
function toggle(){if(timer){stop();return}if(idx>=flow.steps.length-1)idx=-1;play.textContent="暂停";const tick=()=>{if(idx>=flow.steps.length-1){stop();return}step(1)};tick();timer=setInterval(tick,2600)}
prev.onclick=()=>{stop();step(-1)};next.onclick=()=>{stop();step(1)};play.onclick=toggle;
D.flows.forEach((f,i)=>{const b=el("button",i?null:"on",f.title);b.onclick=()=>{stop();flow=f;idx=0;[...pick.children].forEach(c=>c.classList.remove("on"));b.classList.add("on");show()};pick.append(b)});
document.addEventListener("keydown",e=>{if(e.target.closest&&e.target.closest("button,.node"))return;
  if(e.key==="ArrowRight"){stop();step(1)}else if(e.key==="ArrowLeft"){stop();step(-1)}else if(e.key===" "){e.preventDefault();toggle()}});
show();
/* level four */
if((D.terms||[]).length){const s4=section("l4","术语","代码里反复出现、读懂调用要先知道的词。");const d=el("dl","terms");D.terms.forEach(t=>d.append(el("dt",null,t.term),el("dd",null,t.meaning)));s4.append(d)}
/* level five: knowledge graph */
if(D.graph){
  const {default:cytoscape}=await import("cytoscape");
  const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const s5=section("l5","图谱","全部概念、模块和它们的关系。搜索或点击节点，只看它的邻居。");
  const tools=el("div","gtools"),q=el("input","q");q.placeholder="搜索节点";q.setAttribute("aria-label","搜索节点");tools.append(q);
  const kinds=[...new Set(D.graph.nodes.map(n=>n.kind||"其他"))],off=new Set();
  const g5=el("div","grid"),host=el("div"),box5=el("aside");host.id="kg";g5.append(host,box5);s5.append(tools,g5);
  const palette=[css("--ai"),css("--shu"),css("--koke"),css("--yamabuki"),css("--rikyu"),css("--koiai")];
  const colour=k=>palette[kinds.indexOf(k)%palette.length];
  const cy=cytoscape({container:host,minZoom:.25,maxZoom:3,
    elements:[...D.graph.nodes.map(n=>({data:{...n,kind:n.kind||"其他",label:n.label,colour:colour(n.kind||"其他")}})),
      ...D.graph.edges.map((e,i)=>({data:{id:"e"+i,source:e.from,target:e.to,rel:e.rel||"",dash:e.verified===false?"dashed":"solid"}}))],
    style:[{selector:"node",style:{"background-color":"data(colour)",width:14,height:14,label:"data(label)",color:css("--sumi"),"font-size":12,"text-margin-y":-6,"font-family":"serif"}},
      {selector:"edge",style:{width:1,"line-color":css("--line"),"line-style":"data(dash)","curve-style":"bezier","target-arrow-shape":"triangle","target-arrow-color":css("--line"),"arrow-scale":.7}},
      {selector:".faded",style:{opacity:.12}},{selector:"edge.hot",style:{"line-color":css("--shu"),"target-arrow-color":css("--shu"),width:1.6,label:"data(rel)","font-size":10,color:css("--nezumi")}},{selector:"node:selected",style:{width:20,height:20}}],
    layout:{name:"cose",animate:false,padding:30,nodeRepulsion:9000,idealEdgeLength:90}});
  const focus=n=>{cy.elements().removeClass("faded hot");const near=n.closedNeighborhood();cy.elements().not(near).addClass("faded");near.edges().addClass("hot");describe(box5,n.data())};
  cy.on("tap","node",e=>focus(e.target));
  cy.on("tap",e=>{if(e.target===cy)cy.elements().removeClass("faded hot")});
  const apply=()=>{cy.nodes().forEach(n=>n.style("display",off.has(n.data("kind"))?"none":"element"))};
  kinds.forEach(k=>{const b=el("button","on",k);b.onclick=()=>{off.has(k)?off.delete(k):off.add(k);b.classList.toggle("on");apply()};tools.append(b)});
  q.addEventListener("input",()=>{const v=q.value.trim().toLowerCase();cy.elements().removeClass("faded hot");if(!v)return;
    const hit=cy.nodes().filter(n=>n.data("label").toLowerCase().includes(v));cy.elements().not(hit).addClass("faded");if(hit.length===1)focus(hit[0])});
  {const b=el("button",null,"三维");let g3=null;let ForceGraph3D=null;tools.append(b);
    const obs=new ResizeObserver(()=>g3&&g3.width(host.clientWidth).height(host.clientHeight));obs.observe(host);
    b.onclick=async()=>{if(!ForceGraph3D)({default:ForceGraph3D}=await import("3d-force-graph"));const on=b.classList.toggle("on");if(!on){if(g3){g3._destructor();g3=null}host.replaceChildren();cy.mount(host);return}
      cy.unmount();host.replaceChildren();
      g3=ForceGraph3D()(host).width(host.clientWidth).height(host.clientHeight).backgroundColor(css("--gofun"))
        .graphData({nodes:D.graph.nodes.map(n=>({...n})),links:D.graph.edges.map(e=>({source:e.from,target:e.to}))})
        .nodeLabel("label").nodeColor(n=>colour(n.kind||"其他")).linkColor(()=>css("--rikyu")).linkOpacity(.5).onNodeClick(n=>describe(box5,n))}}
  describe(box5,D.graph.nodes[0]);
}
const links=[...nav.children];const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)links.forEach(a=>a.classList.toggle("on",a.hash==="#"+e.target.id))}),{rootMargin:"-40% 0px -55% 0px"});
document.querySelectorAll("section").forEach(s=>io.observe(s));
