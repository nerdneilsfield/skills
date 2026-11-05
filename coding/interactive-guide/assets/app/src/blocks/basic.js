import { marked } from "marked";
import { el } from "../dom.js";
export function text(b) { const d = el("div", "prose"); d.innerHTML = marked.parse(b.md); return d; }
export function callout(b) {
  const d = el("div", "callout " + (b.kind || ""));
  if (b.title) d.append(el("b", null, b.title));
  const body = el("div"); body.innerHTML = marked.parse(b.md); d.append(body); return d;
}
export function code(b) {
  const d = el("div");
  if (b.file) d.append(el("div", "loc", b.file + (b.line ? ":" + b.line : "")));
  d.append(el("pre", null, b.code)); return d;
}
const ORIGIN = { paper: "论文原图", explain: "补充解释图" };
export const originTag = (b) => el("span", "origin " + b.origin, (ORIGIN[b.origin] || b.origin) + (b.ref ? " · " + b.ref : ""));
const CLAIM = { author: "作者主张", evidence: "论文证据", inference: "分析推断", unknown: "未报告" };
export function claim(b) {
  const d = el("div", "claim " + b.kind); d.append(el("b", null, CLAIM[b.kind]));
  const body = el("div"); body.innerHTML = marked.parse(b.md); d.append(body);
  if (b.where) d.append(el("div", "where", b.where)); return d;
}
export function figuretour(b) {
  const root = el("div", "ftour"), g = el("div", "grid"), stage = el("div", "stage"), i = el("img"), clip = el("div", "clip"), spot = el("div", "spot"), box = el("aside");
  i.src = b.src; i.alt = b.alt; clip.append(spot); stage.append(i, clip); g.append(stage, box); root.append(g);
  const ctl = el("div", "ctl"), prev = el("button", null, "上一处"), next = el("button", null, "下一处"), n = el("span", "count"); ctl.append(prev, next, n); root.append(ctl);
  if (b.caption || b.origin) { const c = el("p", "legend"); if (b.origin) c.append(originTag(b)); if (b.caption) c.append(b.caption); root.append(c); }
  let k = 0;
  const show = () => { const s = b.stops[k]; spot.style.cssText = `left:${s.x}%;top:${s.y}%;width:${s.w}%;height:${s.h}%`;
    box.replaceChildren(el("h3", null, s.title)); const p = el("div", "prose"); p.innerHTML = marked.parse(s.md); box.append(p); n.textContent = `${k + 1} / ${b.stops.length}`; };
  prev.onclick = () => { k = Math.max(0, k - 1); show(); }; next.onclick = () => { k = Math.min(b.stops.length - 1, k + 1); show(); }; show(); return root;
}
const PC = { match: "一致", differs: "有差异", unstated: "论文未写" };
export function papercode(b) {
  const root = el("div"), bar = el("div", "pc-filter"), rows = el("div"); root.append(bar, rows);
  const render = (only) => { rows.replaceChildren(...b.items.filter((x) => !only || x.status === only).map((x) => {
    const r = el("div", "pc"), grid = el("div", "pc-row"), left = el("div", "prose"), right = el("div");
    r.append(el("div", "pc-state " + x.status, PC[x.status]));
    left.innerHTML = marked.parse(x.paper); if (x.where) left.append(el("div", "loc", x.where));
    right.append(el("div", "loc", x.file + (x.line ? ":" + x.line : ""))); if (x.code) right.append(el("pre", null, x.code));
    grid.append(left, right); r.append(grid); if (x.note) r.append(el("p", "pc-note", x.note)); return r; })); };
  [[null, "全部"], ...Object.entries(PC)].forEach(([k, t], i) => { const n = k ? b.items.filter((x) => x.status === k).length : b.items.length;
    const x = el("button", i ? null : "on", `${t} ${n}`); x.onclick = () => { [...bar.children].forEach((c) => c.classList.remove("on")); x.classList.add("on"); render(k); }; bar.append(x); });
  render(null); return root;
}
export function figure(b) {
  const f = el("figure"), i = el("img"); i.src = b.src; i.alt = b.alt; i.loading = "lazy"; f.append(i);
  if (b.caption || b.origin) { const c = el("figcaption"); if (b.origin) c.append(originTag(b)); if (b.caption) c.append(b.caption); f.append(c); }
  return f;
}
export function compare(b) {
  const t = el("table", "cmp"), h = el("tr");
  b.headers.forEach((x) => h.append(el("th", null, x))); t.append(h);
  b.rows.forEach((r) => { const tr = el("tr"); r.forEach((x) => tr.append(el("td", null, x))); t.append(tr); });
  return t;
}
export function steps(b) { const o = el("ol", "stepsb"); b.items.forEach((x) => o.append(el("li", null, x))); return o; }
export function terms(b) { const d = el("dl", "terms"); b.items.forEach((t) => d.append(el("dt", null, t.term), el("dd", null, t.meaning))); return d; }
export function quiz(b) {
  const d = el("div", "quiz"); d.append(el("p", null, b.question));
  const why = el("div", "why");
  b.options.forEach((o, i) => {
    const x = el("button", null, o);
    x.onclick = () => { x.classList.add(i === b.answer ? "ok" : "no"); why.textContent = b.explain || ""; };
    d.append(x);
  });
  d.append(why); return d;
}
export async function formula(b) {
  if (import.meta.env.MODE === "offline") await import("katex/dist/katex.min.css");
  const { default: katex } = await import("katex");
  const d = el("div", "formula"); d.innerHTML = katex.renderToString(b.tex, { displayMode: true, throwOnError: false }); return d;
}
let id = 0;
export async function mermaid(b) {
  const { default: m } = await import("mermaid");
  m.initialize({ startOnLoad: false, theme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "neutral" });
  const d = el("div", "mermaid-box"); d.innerHTML = (await m.render("mmd" + id++, b.code)).svg; return d;
}
