import { codeBlock } from "./code.js";

export const GAP = "⚠ 未指定";
export const blank = (v) => v == null || String(v).trim() === "";
export const gap = (what) => el("span", "missing", `${GAP}：${what}`);
/* Show a fact, or a visible gap when the data has none. Never fill it with a guess. */
export const put = (e, v, what) => { if (blank(v)) e.append(gap(what)); else e.textContent = v; return e; };
export const NS = "http://www.w3.org/2000/svg";
export const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
export const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
export const sv = (t, a = {}) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };
export const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
export function describe(box, o) {
  box.replaceChildren(put(el("h3"), o.title || o.label, "标题"));
  if (o.file) {
    const l = el("div", "loc", o.file + (o.line ? ":" + o.line : ""));
    l.append(el("span", "tag" + (o.verified === false ? " inferred" : ""), o.verified === false ? "推断" : "已核对"));
    box.append(l);
  }
  const b = o.explain || o.summary;
  if (b) box.append(el("p", null, b));
  if (o.code) box.append(codeBlock(o.code, o.lang, o.file));
}
