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
export function figure(b) {
  const f = el("figure"), i = el("img"); i.src = b.src; i.alt = b.alt; i.loading = "lazy"; f.append(i);
  if (b.caption) f.append(el("figcaption", null, b.caption)); return f;
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
