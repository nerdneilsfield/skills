// Click-through view of the same pages: a fixed 16:9 stage, scaled whole, showing one block per slide.
import { el } from "./dom.js";

const W = 1280, H = 720, MIN_FIT = .6;
const INTERACTIVE = "a,button,input,aside,pre,mark,svg,canvas,.kg,.quiz,.ftour";

export function createPresent({ D, main, header, section, display, pageIndex, leave }) {
  const slides = [{ cover: true }, ...D.pages.flatMap((p, i) => p.blocks.map((_, block) => ({ page: i, block })))];
  const bar = el("div", "deck-bar"), prev = el("button", null, "上一页"), next = el("button", null, "下一页"), count = el("span", "count"), close = el("button", null, "退出");
  bar.append(prev, count, next, close); bar.hidden = true; document.body.append(bar);
  const cover = el("section", "page deck-cover");
  let at = 0, on = false, turn = 0;

  const fit = () => { main.style.transform = `translate(-50%,-50%) scale(${Math.min(innerWidth / W, innerHeight / H)})`; };
  async function go(n) {
    at = Math.max(0, Math.min(slides.length - 1, n)); const s = slides[at], me = ++turn;
    count.textContent = `${at + 1} / ${slides.length}`; prev.disabled = at === 0; next.disabled = at === slides.length - 1;
    document.activeElement?.blur?.();
    const root = s.cover ? cover : await section(s.page);
    if (me !== turn || !on) return;
    if (s.cover) main.replaceChildren(cover);
    else { root.querySelectorAll(":scope>.block").forEach((b, i) => b.classList.toggle("cur", i === s.block)); display(root, s.page); }
    await Promise.all([...root.querySelectorAll(".cur img")].map((i) => i.decode().catch(() => {})));
    if (me !== turn || !on) return;
    main.style.setProperty("--fit", 1);
    // Shrinking rewraps text in the wider column, so measure once more after the first fit.
    for (let k = 1, i = 0; i < 2; i++) { k = Math.max(MIN_FIT, Math.min(1, k * H / main.scrollHeight)); main.style.setProperty("--fit", k); }
    main.scrollTop = 0;
  }
  function enter() {
    if (on) return;
    on = true; document.body.classList.add("present"); bar.hidden = false; fit();
    cover.replaceChildren(...[...header.children].map((c) => { const x = c.cloneNode(true); x.removeAttribute("id"); return x; }));
    const i = pageIndex();
    return go(i < 0 ? 0 : slides.findIndex((s) => s.page === i));
  }
  function exit() {
    const s = slides[at];
    on = false; turn++; document.body.classList.remove("present"); bar.hidden = true;
    main.style.transform = ""; main.style.removeProperty("--fit");
    if (!s.cover) history.replaceState(null, "", "#" + D.pages[s.page].id);
    leave();
  }
  prev.onclick = () => go(at - 1); next.onclick = () => go(at + 1); close.onclick = exit;
  addEventListener("resize", () => { if (on) fit(); });
  main.addEventListener("click", (e) => { if (on && !e.target.closest(INTERACTIVE) && !String(getSelection())) go(at + 1); });
  addEventListener("keydown", (e) => {
    const t = e.target;
    if (!on || t.closest?.("input,textarea")) return;
    if (e.key === "Escape") return exit();
    // A focused flow keeps the arrows and space; a focused button keeps its own activation keys.
    if (t.closest?.("[tabindex]") || (t.closest?.("button") && [" ", "Enter"].includes(e.key))) return;
    const to = { ArrowRight: at + 1, PageDown: at + 1, " ": at + 1, ArrowLeft: at - 1, PageUp: at - 1, Home: 0, End: slides.length - 1 }[e.key];
    if (to !== undefined) { e.preventDefault(); go(to); }
  });
  return { enter, get on() { return on; } };
}
