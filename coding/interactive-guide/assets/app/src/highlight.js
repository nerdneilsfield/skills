// Reader highlights: stored as quoted text with context, so they survive rebuilds that keep the wording.
import { el } from "./dom.js";

const COLORS = { yamabuki: "山吹", wakatake: "若竹", sakura: "桜" };
const CONTEXT = 24;

function textNodes(root) {
  const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) =>
    n.parentElement.closest("button,svg,canvas,input,.pager,.count,.hl-bar") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
  const nodes = []; while (walk.nextNode()) nodes.push(walk.currentNode); return nodes;
}
const indexOfNodes = (nodes) => { let at = 0; return nodes.map((node) => { const r = { node, start: at }; at += node.data.length; return r; }); };

function wrap(root, start, end, item) {
  const parts = indexOfNodes(textNodes(root)).filter((p) => p.start < end && p.start + p.node.data.length > start);
  parts.forEach((p) => { const r = document.createRange();
    r.setStart(p.node, Math.max(0, start - p.start)); r.setEnd(p.node, Math.min(p.node.data.length, end - p.start));
    const m = el("mark", "hl " + item.color); m.dataset.id = item.id; if (item.note) m.title = item.note; r.surroundContents(m); });
}
function locate(root, item) {
  const full = textNodes(root).map((n) => n.data).join("");
  let at = full.indexOf(item.prefix + item.text + item.suffix);
  if (at >= 0) return at + item.prefix.length;
  at = full.indexOf(item.text); return at;
}

export function createHighlights(storageKey, pages, tabs) {
  const key = storageKey + ":hl";
  let items = [];
  try { items = JSON.parse(localStorage.getItem(key)) || []; } catch { /* storage may be blocked */ }
  const save = () => { try { localStorage.setItem(key, JSON.stringify(items)); } catch { /* keep in memory */ } count(); };
  const button = el("button", "hl-open"); button.setAttribute("aria-label", "打开高亮列表"); tabs.parentElement.append(button);
  const count = () => { button.textContent = `高亮 ${items.length}`; };
  const bar = el("div", "hl-bar"); bar.hidden = true; document.body.append(bar);
  const panel = el("aside", "hl-panel"); panel.hidden = true; document.body.append(panel);
  let root = null, pageId = null, pending = null, active = null;

  const hide = () => { bar.hidden = true; pending = null; active = null; };
  const place = (rect) => { bar.hidden = false; const x = Math.min(innerWidth - bar.offsetWidth - 8, Math.max(8, rect.left));
    bar.style.left = x + "px"; bar.style.top = Math.max(8, rect.top - bar.offsetHeight - 8) + "px"; };
  const unmark = (id) => root.querySelectorAll(`mark.hl[data-id="${id}"]`).forEach((m) => { m.replaceWith(...m.childNodes); }), tidy = () => root.normalize();
  const remove = (id) => { items = items.filter((x) => x.id !== id); unmark(id); tidy(); save(); hide(); renderPanel(); };
  const setNote = (item) => { const note = prompt("批注", item.note || ""); if (note === null) return; item.note = note;
    root.querySelectorAll(`mark.hl[data-id="${item.id}"]`).forEach((m) => { m.title = note; }); save(); hide(); renderPanel(); };
  const recolour = (item, c) => { item.color = c; root.querySelectorAll(`mark.hl[data-id="${item.id}"]`).forEach((m) => { m.className = "hl " + c; }); save(); hide(); };

  function add(color) {
    const { start, end } = pending, full = textNodes(root).map((n) => n.data).join("");
    const item = { id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), page: pageId, color, note: "",
      text: full.slice(start, end), prefix: full.slice(Math.max(0, start - CONTEXT), start), suffix: full.slice(end, end + CONTEXT) };
    wrap(root, start, end, item); items.push(item); save(); getSelection().removeAllRanges(); hide(); renderPanel(); return item;
  }
  function showNew(rect) {
    bar.replaceChildren(...Object.entries(COLORS).map(([c, t]) => { const b = el("button", "hl-c " + c, t); b.onmousedown = (e) => e.preventDefault(); b.onclick = () => add(c); return b; }));
    const n = el("button", null, "批注"); n.onmousedown = (e) => e.preventDefault(); n.onclick = () => setNote(add("yamabuki")); bar.append(n); place(rect);
  }
  function showExisting(item, rect) {
    active = item;
    bar.replaceChildren(...Object.entries(COLORS).map(([c, t]) => { const b = el("button", "hl-c " + c, t); b.onclick = () => recolour(item, c); return b; }));
    const n = el("button", null, "批注"), d = el("button", null, "删除"); n.onclick = () => setNote(item); d.onclick = () => remove(item.id); bar.append(n, d); place(rect);
  }
  function selectionRange() {
    const s = getSelection(); if (!s.rangeCount || s.isCollapsed || !root) return null;
    const r = s.getRangeAt(0); if (!root.contains(r.commonAncestorContainer)) return null;
    let start = -1, end = -1;
    for (const p of indexOfNodes(textNodes(root))) {
      if (p.node === r.startContainer) start = p.start + r.startOffset;
      if (p.node === r.endContainer) end = p.start + r.endOffset;
    }
    if (r.startContainer.nodeType !== 3 || r.endContainer.nodeType !== 3 || start < 0 || end <= start) return null;
    return { start, end, rect: r.getBoundingClientRect() };
  }
  const onSelect = () => { const r = selectionRange(); if (r) { pending = r; showNew(r.rect); } };
  document.addEventListener("mouseup", (e) => { if (bar.contains(e.target)) return; setTimeout(onSelect, 0); });
  document.addEventListener("touchend", () => setTimeout(onSelect, 250));
  document.addEventListener("click", (e) => { const m = e.target.closest?.("mark.hl");
    if (m && getSelection().isCollapsed) { const it = items.find((x) => x.id === m.dataset.id); if (it) showExisting(it, m.getBoundingClientRect()); return; }
    if (!bar.contains(e.target) && getSelection().isCollapsed) hide(); });

  function markdown() {
    return pages.map((p) => { const rows = items.filter((x) => x.page === p.id); if (!rows.length) return "";
      return `## ${p.title}\n\n` + rows.map((x) => `> ${x.text}` + (x.note ? `\n\n批注：${x.note}` : "")).join("\n\n") + "\n"; }).filter(Boolean).join("\n");
  }
  function renderPanel() {
    panel.replaceChildren(el("h3", null, "高亮与批注"));
    const tools = el("div", "ctl"), exp = el("button", null, "导出 Markdown"), close = el("button", null, "关闭");
    exp.onclick = () => { const a = el("a"); a.href = URL.createObjectURL(new Blob([markdown()], { type: "text/markdown" })); a.download = "highlights.md"; a.click(); URL.revokeObjectURL(a.href); };
    close.onclick = () => { panel.hidden = true; }; tools.append(exp, close); panel.append(tools);
    if (!items.length) panel.append(el("p", "legend", "选中文字即可高亮。"));
    pages.forEach((p) => { const rows = items.filter((x) => x.page === p.id); if (!rows.length) return; panel.append(el("h4", null, p.title));
      rows.forEach((x) => { const a = el("a", "hl-item " + x.color, x.text); a.href = "#" + p.id; a.onclick = () => { panel.hidden = true; setTimeout(() => root?.querySelector(`mark.hl[data-id="${x.id}"]`)?.scrollIntoView({ block: "center" }), 150); }; panel.append(a);
        if (x.note) panel.append(el("p", "legend", x.note)); }); });
  }
  button.onclick = () => { renderPanel(); panel.hidden = !panel.hidden; };
  count();
  return {
    attach(pageRoot, id) { root = pageRoot; pageId = id; hide();
      if (pageRoot.dataset.hl) return; pageRoot.dataset.hl = "1";
      items.filter((x) => x.page === id).forEach((x) => { const at = locate(pageRoot, x); if (at >= 0) wrap(pageRoot, at, at + x.text.length, x); else x.lost = true; }); },
  };
}
