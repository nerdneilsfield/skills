import D from "./data.json";
import "./style.css";
import { el, put, gap, blank, GAP } from "./dom.js";
import { blocks } from "./blocks/index.js";
import { createHighlights } from "./highlight.js";
import { createPresent } from "./present.js";

const header = document.querySelector("header.top"), answer = D.mode === "answer";
document.title = D.title || GAP;
document.body.classList.toggle("answer", answer);
document.body.classList.toggle("solo", D.pages.length === 1);
put(document.getElementById("title"), D.title, "标题");
put(document.getElementById("summary"), D.summary, "摘要");
const meta = document.getElementById("meta");
meta.textContent = [D.repo, D.commit].filter(Boolean).join(" @ ");
if (D.repo && blank(D.commit)) meta.append(" @ ", gap("提交"));
if (D.assumptions?.length) {
  const box = el("div", "assume"), list = el("ul"); box.append(el("b", null, "未经确认的假设"), list);
  D.assumptions.forEach((a) => list.append(el("li", null, a))); header.append(box);
}
const main = document.getElementById("main"), tabs = document.getElementById("tabs"), key = "guide:" + D.title;
const load = () => { try { return JSON.parse(localStorage.getItem(key)) || []; } catch { return []; } };
let done = new Set(load());
const links = D.pages.map((p) => { const a = el("a", done.has(p.id) ? "done" : null, p.title || GAP); a.href = "#" + p.id; tabs.append(a); return a; });
const hl = createHighlights(key, D.pages, tabs);
const built = {};
async function page(p, i) {
  const s = el("section", "page"); if (p.level) s.append(el("div", "level", p.level));
  if (!answer) s.append(put(el("h2"), p.title, "标题")); if (p.intro) s.append(el("p", "intro", p.intro));
  for (const b of p.blocks) { const box = el("div", "block"); box.dataset.type = b.type; box.append(await blocks[b.type](b)); s.append(box); }
  const pager = el("div", "pager"), prev = D.pages[i - 1], next = D.pages[i + 1];
  const left = el("span"), right = el("span"); if (prev) { const a = el("a", null, "← " + (prev.title || GAP)); a.href = "#" + prev.id; left.append(a); }
  if (next) { const a = el("a", null, (next.title || GAP) + " →"); a.href = "#" + next.id; right.append(a); } pager.append(left, right); s.append(pager); return s;
}
const section = (i) => (built[D.pages[i].id] ||= page(D.pages[i], i));
function display(s, i) {
  const p = D.pages[i];
  links.forEach((a, j) => a.classList.toggle("on", i === j));
  done.add(p.id); links[i].classList.add("done"); try { localStorage.setItem(key, JSON.stringify([...done])); } catch { /* private mode */ }
  main.replaceChildren(s);
  s.querySelectorAll('[data-type="graph"]>*').forEach((g) => g.mount && g.offsetParent && g.mount());
  hl.attach(s, p.id);
}
const pageIndex = () => D.pages.findIndex((p) => "#" + p.id === location.hash);
let turn = 0;
async function route() {
  if (deck.on) return;
  const me = ++turn, i = Math.max(0, pageIndex()), s = await section(i);
  if (me === turn && !deck.on) { display(s, i); scrollTo(0, 0); }
}
const deck = createPresent({ D, main, header, section, display, pageIndex, leave: route });
if (D.pages.reduce((n, p) => n + p.blocks.length, 0) > 1) { const b = el("button", "hl-open", "演示"); b.onclick = () => deck.enter(); tabs.parentElement.append(b); }
addEventListener("hashchange", route);
if (new URLSearchParams(location.search).has("present")) deck.enter(); else route();
