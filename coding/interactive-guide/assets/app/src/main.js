import D from "./data.json";
import "./style.css";
import { el } from "./dom.js";
import { blocks } from "./blocks/index.js";
import { createHighlights } from "./highlight.js";

document.title = D.title;
document.getElementById("title").textContent = D.title;
document.getElementById("summary").textContent = D.summary;
document.getElementById("meta").textContent = [D.repo, D.commit].filter(Boolean).join(" @ ");
const main = document.getElementById("main"), tabs = document.getElementById("tabs"), key = "guide:" + D.title;
const load = () => { try { return JSON.parse(localStorage.getItem(key)) || []; } catch { return []; } };
let done = new Set(load());
const links = D.pages.map((p) => { const a = el("a", done.has(p.id) ? "done" : null, p.title); a.href = "#" + p.id; tabs.append(a); return a; });
const hl = createHighlights(key, D.pages, tabs);
const built = {};
async function page(p, i) {
  const s = el("section", "page"); if (p.level) s.append(el("div", "level", p.level));
  s.append(el("h2", null, p.title)); if (p.intro) s.append(el("p", "intro", p.intro));
  for (const b of p.blocks) { const box = el("div", "block"); box.dataset.type = b.type; box.append(await blocks[b.type](b)); s.append(box); }
  const pager = el("div", "pager"), prev = D.pages[i - 1], next = D.pages[i + 1];
  const left = el("span"), right = el("span"); if (prev) { const a = el("a", null, "← " + prev.title); a.href = "#" + prev.id; left.append(a); }
  if (next) { const a = el("a", null, next.title + " →"); a.href = "#" + next.id; right.append(a); } pager.append(left, right); s.append(pager); return s;
}
async function route() {
  const i = Math.max(0, D.pages.findIndex((p) => "#" + p.id === location.hash)), p = D.pages[i];
  links.forEach((a, j) => a.classList.toggle("on", i === j));
  done.add(p.id); links[i].classList.add("done"); try { localStorage.setItem(key, JSON.stringify([...done])); } catch { /* private mode */ }
  built[p.id] ||= await page(p, i); main.replaceChildren(built[p.id]);
  built[p.id].querySelectorAll('[data-type="graph"]>*').forEach((g) => g.mount && g.mount());
  hl.attach(built[p.id], p.id);
  scrollTo(0, 0);
}
addEventListener("hashchange", route); route();
