import { marked } from "marked";
import { el, put, gap, blank } from "../dom.js";
import { codeBlock, highlightProse } from "../code.js";
const md = (host, src, what) => { if (blank(src)) { host.append(gap(what)); return host; } host.innerHTML = marked.parse(src); highlightProse(host); return host; };
export function text(b) { return md(el("div", "prose"), b.md, "正文"); }
export function callout(b) {
  const d = el("div", "callout " + (b.kind || ""));
  if (b.title) d.append(el("b", null, b.title));
  d.append(md(el("div"), b.md, "正文")); return d;
}
export function code(b) {
  const d = el("div");
  if (b.file) d.append(el("div", "loc", b.file + (b.line ? ":" + b.line : "")));
  d.append(codeBlock(b.code, b.lang, b.file)); return d;
}
const ORIGIN = { paper: "论文原图", explain: "补充解释图" };
export const originTag = (b) => el("span", "origin " + b.origin, (ORIGIN[b.origin] || b.origin) + (b.ref ? " · " + b.ref : ""));
const CLAIM = { author: "作者主张", evidence: "论文证据", inference: "分析推断", unknown: "未报告" };
export function claim(b) {
  const d = el("div", "claim " + b.kind); d.append(el("b", null, CLAIM[b.kind]));
  d.append(md(el("div"), b.md, "正文"));
  if (b.where) d.append(el("div", "where", b.where)); return d;
}
export function figuretour(b) {
  const root = el("div", "ftour"), g = el("div", "grid"), stage = el("div", "stage"), i = el("img"), clip = el("div", "clip"), spot = el("div", "spot"), box = el("aside");
  i.src = b.src; i.alt = b.alt || ""; clip.append(spot); stage.append(i, clip); g.append(stage, box); root.append(g);
  const ctl = el("div", "ctl"), prev = el("button", null, "上一处"), next = el("button", null, "下一处"), n = el("span", "count"); ctl.append(prev, next, n); root.append(ctl);
  if (b.caption || b.origin || blank(b.alt)) { const c = el("p", "legend"); if (b.origin) c.append(originTag(b)); if (b.caption) c.append(b.caption); if (blank(b.alt)) c.append(gap("图片说明")); root.append(c); }
  let k = 0;
  const show = () => { const s = b.stops[k]; spot.style.cssText = `left:${s.x}%;top:${s.y}%;width:${s.w}%;height:${s.h}%`;
    box.replaceChildren(put(el("h3"), s.title, "标题"), md(el("div", "prose"), s.md, "说明")); n.textContent = `${k + 1} / ${b.stops.length}`; };
  prev.onclick = () => { k = Math.max(0, k - 1); show(); }; next.onclick = () => { k = Math.min(b.stops.length - 1, k + 1); show(); }; show(); return root;
}
const PC = { match: "一致", differs: "有差异", unstated: "论文未写" };
export function papercode(b) {
  const root = el("div"), bar = el("div", "pc-filter"), rows = el("div"); root.append(bar, rows);
  const render = (only) => { rows.replaceChildren(...b.items.filter((x) => !only || x.status === only).map((x) => {
    const r = el("div", "pc"), grid = el("div", "pc-row"), left = el("div", "prose"), right = el("div");
    r.append(el("div", "pc-state " + x.status, PC[x.status]));
    md(left, x.paper, "论文内容"); if (x.where) left.append(el("div", "loc", x.where));
    if (x.file) right.append(el("div", "loc", x.file + (x.line ? ":" + x.line : "")));
    else if (x.status !== "unstated") right.append(gap("代码位置"));
    if (x.code) right.append(codeBlock(x.code, x.lang, x.file));
    grid.append(left, right); r.append(grid); if (x.note) r.append(el("p", "pc-note", x.note)); return r; })); };
  [[null, "全部"], ...Object.entries(PC)].forEach(([k, t], i) => { const n = k ? b.items.filter((x) => x.status === k).length : b.items.length;
    const x = el("button", i ? null : "on", `${t} ${n}`); x.onclick = () => { [...bar.children].forEach((c) => c.classList.remove("on")); x.classList.add("on"); render(k); }; bar.append(x); });
  render(null); return root;
}
export function figure(b) {
  const f = el("figure"), i = el("img"); i.src = b.src; i.alt = b.alt || ""; i.loading = "lazy"; f.append(i);
  if (b.caption || b.origin || blank(b.alt)) { const c = el("figcaption"); if (b.origin) c.append(originTag(b)); if (b.caption) c.append(b.caption); if (blank(b.alt)) c.append(gap("图片说明")); f.append(c); }
  return f;
}
export function compare(b) {
  const t = el("table", "cmp"), h = el("tr");
  b.headers.forEach((x) => h.append(el("th", null, x))); t.append(h);
  b.rows.forEach((r) => { const tr = el("tr"); for (let i = 0; i < Math.max(r.length, b.headers.length); i++) tr.append(put(el("td"), r[i], "内容")); t.append(tr); });
  return t;
}
export function steps(b) { const o = el("ol", "stepsb"); b.items.forEach((x) => o.append(put(el("li"), x, "步骤"))); return o; }
export function terms(b) { const d = el("dl", "terms"); b.items.forEach((t) => d.append(put(el("dt"), t.term, "术语"), put(el("dd"), t.meaning, "含义"))); return d; }
export function quiz(b) {
  const d = el("div", "quiz"); d.append(put(el("p"), b.question, "问题"));
  const why = el("div", "why");
  b.options.forEach((o, i) => {
    const x = el("button", null, o);
    x.onclick = () => { x.classList.add(i === b.answer ? "ok" : "no"); why.textContent = b.explain || ""; };
    d.append(x);
  });
  d.append(why); return d;
}
async function loadTex() {
  if (import.meta.env.MODE === "offline") await import("katex/dist/katex.min.css");
  const { default: katex } = await import("katex");
  return (tex, displayMode) => katex.renderToString(tex, { displayMode, throwOnError: false });
}
const tex = (host, render, src, display) => { host.innerHTML = render(src, display); return host; };
export async function formula(b) {
  const render = await loadTex(), root = el("div", "formula-card");
  if (b.name) root.append(el("h3", null, b.name));
  root.append(tex(el("div", "formula"), render, b.tex, true));
  if (b.symbols?.length) {
    const t = el("table", "cmp syms"), h = el("tr"); ["符号", "含义", "形状或单位"].forEach((x) => h.append(el("th", null, x))); t.append(h);
    b.symbols.forEach((s) => { const r = el("tr"); r.append(tex(el("td"), render, s.sym, false), put(el("td"), s.meaning, "含义"), el("td", null, s.shape || "")); t.append(r); });
    root.append(t);
  }
  if (b.why) root.append(md(el("div", "prose"), b.why));
  return root;
}
const TRACE = { paper: "论文中的数字", invented: "自拟数字，仅作演示" };
export async function trace(b) {
  const render = await loadTex(), root = el("div", "ftour trace"), g = el("div", "grid"), stage = el("div", "stage-t"), box = el("aside");
  if (b.title) root.append(el("h3", null, b.title));
  root.append(TRACE[b.data] ? el("span", "tag" + (b.data === "invented" ? " inferred" : ""), TRACE[b.data]) : gap("数字来源"));
  if (b.input) root.append(md(el("div", "prose"), b.input));
  g.append(stage, box); root.append(g);
  const ctl = el("div", "ctl"), prev = el("button", null, "上一步"), next = el("button", null, "下一步"), n = el("span", "count"); ctl.append(prev, next, n); root.append(ctl);
  let k = 0;
  const show = () => { const s = b.steps[k], rows = el("table", "cmp");
    (s.state || []).forEach((v) => { const r = el("tr"); r.append(put(el("th"), v.name, "变量"), put(el("td"), v.value, "取值")); rows.append(r); });
    stage.replaceChildren(...(s.tex ? [tex(el("div", "formula"), render, s.tex, true)] : []), rows);
    box.replaceChildren(put(el("h3"), s.title, "标题"), md(el("div", "prose"), s.md, "说明"));
    n.textContent = `${k + 1} / ${b.steps.length}`; prev.disabled = k === 0; next.disabled = k === b.steps.length - 1; };
  prev.onclick = () => { k = Math.max(0, k - 1); show(); }; next.onclick = () => { k = Math.min(b.steps.length - 1, k + 1); show(); }; show(); return root;
}
let id = 0;
export async function mermaid(b) {
  const { default: m } = await import("mermaid");
  m.initialize({ startOnLoad: false, theme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "neutral" });
  const d = el("div", "mermaid-box"); d.innerHTML = (await m.render("mmd" + id++, b.code)).svg; return d;
}
