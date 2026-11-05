import { el, sv, describe, reduce } from "../dom.js";
const W = 760, NW = 150, NH = 46, GAPY = 96, TOP = 40;
function layout(nodes) {
  const layers = [...new Set(nodes.map((n) => n.layer))].sort((a, b) => a - b), pos = {};
  layers.forEach((L, i) => { const row = nodes.filter((n) => n.layer === L), step = W / (row.length + 1);
    row.forEach((n, j) => { pos[n.id] = { x: step * (j + 1), y: TOP + i * GAPY }; }); });
  return { pos, H: TOP + layers.length * GAPY };
}
function draw(b, host, onPick) {
  const { pos, H } = layout(b.nodes), s = sv("svg", { class: "map", viewBox: `0 0 ${W} ${H}`, role: "img" }), edges = {}, nodes = {};
  b.edges.forEach((e) => { const A = pos[e.from], B = pos[e.to], m = (A.y + B.y) / 2;
    const p = sv("path", { class: "edge" + (e.verified === false ? " inferred" : ""), d: `M${A.x} ${A.y + NH / 2} C${A.x} ${m},${B.x} ${m},${B.x} ${B.y - NH / 2}` });
    edges[e.from + ">" + e.to] = p; s.append(p); });
  b.nodes.forEach((n) => { const g = sv("g", { class: "node", tabindex: "0", role: "button", "aria-label": n.label }), c = pos[n.id];
    g.append(sv("rect", { x: c.x - NW / 2, y: c.y - NH / 2, width: NW, height: NH, rx: 2 }));
    const t = sv("text", { x: c.x, y: c.y + 5, "text-anchor": "middle" }); t.textContent = n.label; g.append(t);
    const pick = () => { Object.values(nodes).forEach((x) => x.classList.remove("sel")); g.classList.add("sel"); onPick(n); };
    g.addEventListener("click", pick); g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
    nodes[n.id] = g; s.append(g); });
  host.append(s); return { svg: s, nodes, edges };
}
export function flow(b) {
  const root = el("div"), pick = el("div", "flows"), g = el("div", "grid"), left = el("div"), box = el("aside");
  root.append(pick, g); g.append(left, box);
  const map = draw(b, left, (n) => describe(box, n));
  const ctl = el("div", "ctl"), prev = el("button", null, "上一步"), play = el("button", null, "播放"), next = el("button", null, "下一步"), count = el("span", "count");
  ctl.append(prev, play, next, count); left.append(ctl);
  const bar = el("div", "bar"), fill = el("i"); bar.append(fill); left.append(bar);
  left.append(el("p", "legend", "实线已核对，虚线为推断。方向键单步，空格播放。"));
  const pulse = sv("circle", { class: "pulse", r: 6, opacity: 0 }); map.svg.append(pulse);
  let cur = b.flows[0], idx = 0, timer = null, raf = null;
  const fly = (p) => { cancelAnimationFrame(raf); if (!p || reduce) { pulse.setAttribute("opacity", 0); return; }
    const len = p.getTotalLength(), t0 = performance.now(); pulse.setAttribute("opacity", 1);
    const go = (t) => { const k = Math.min(1, (t - t0) / 650), e = k < .5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2, q = p.getPointAtLength(len * e);
      pulse.setAttribute("cx", q.x); pulse.setAttribute("cy", q.y); if (k < 1) raf = requestAnimationFrame(go); else pulse.setAttribute("opacity", 0); };
    raf = requestAnimationFrame(go); };
  const show = () => { const st = cur.steps[idx], used = new Set(cur.steps.flatMap((s) => [s.from, s.to]));
    Object.values(map.nodes).forEach((n) => n.classList.remove("act", "dim")); Object.values(map.edges).forEach((e) => e.classList.remove("act"));
    Object.entries(map.nodes).forEach(([id, n]) => { if (!used.has(id)) n.classList.add("dim"); });
    map.nodes[st.to].classList.add("act"); if (st.from) map.nodes[st.from].classList.add("act");
    const p = map.edges[st.from + ">" + st.to]; if (p) p.classList.add("act"); fly(p);
    describe(box, st); count.textContent = `${idx + 1} / ${cur.steps.length}`; fill.style.width = (idx + 1) / cur.steps.length * 100 + "%"; };
  const stop = () => { clearInterval(timer); timer = null; play.textContent = "播放"; };
  const step = (d) => { idx = Math.max(0, Math.min(cur.steps.length - 1, idx + d)); show(); };
  const toggle = () => { if (timer) return stop(); if (idx >= cur.steps.length - 1) idx = -1; play.textContent = "暂停";
    const tick = () => { if (idx >= cur.steps.length - 1) return stop(); step(1); }; tick(); timer = setInterval(tick, 2600); };
  prev.onclick = () => { stop(); step(-1); }; next.onclick = () => { stop(); step(1); }; play.onclick = toggle;
  b.flows.forEach((f, i) => { const x = el("button", i ? null : "on", f.title);
    x.onclick = () => { stop(); cur = f; idx = 0; [...pick.children].forEach((c) => c.classList.remove("on")); x.classList.add("on"); show(); }; pick.append(x); });
  root.tabIndex = 0; root.addEventListener("keydown", (e) => { if (e.target.closest("button,.node")) return;
    if (e.key === "ArrowRight") { stop(); step(1); } else if (e.key === "ArrowLeft") { stop(); step(-1); } else if (e.key === " ") { e.preventDefault(); toggle(); } });
  show(); return root;
}
