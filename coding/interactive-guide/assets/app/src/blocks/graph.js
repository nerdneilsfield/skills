import { el, css, describe } from "../dom.js";
export async function graph(b) {
  const { default: cytoscape } = await import("cytoscape");
  const root = el("div"), tools = el("div", "gtools"), q = el("input", "q"), g = el("div", "grid"), host = el("div", "kg"), box = el("aside");
  q.placeholder = "搜索节点"; q.setAttribute("aria-label", "搜索节点"); tools.append(q); g.append(host, box); root.append(tools, g);
  const kinds = [...new Set(b.nodes.map((n) => n.kind || "其他"))], off = new Set();
  const palette = ["--ai", "--shu", "--koke", "--yamabuki", "--rikyu", "--koiai"].map(css), colour = (k) => palette[kinds.indexOf(k) % palette.length];
  let cy;
  const start = () => {
    cy = cytoscape({ container: host, minZoom: .2, maxZoom: 1.6, elements: [
      ...b.nodes.map((n) => ({ data: { ...n, kind: n.kind || "其他", colour: colour(n.kind || "其他") } })),
      ...b.edges.map((e, i) => ({ data: { id: "e" + i, source: e.from, target: e.to, rel: e.rel || "", dash: e.verified === false ? "dashed" : "solid" } }))],
    style: [
      { selector: "node", style: { "background-color": "data(colour)", width: 12, height: 12, label: "data(label)", color: css("--sumi"), "font-size": 11, "text-margin-y": -5, "min-zoomed-font-size": 7, "font-family": "serif" } },
      { selector: "edge", style: { width: 1, "line-color": css("--rikyu"), "line-style": "data(dash)", "curve-style": "bezier", "target-arrow-shape": "triangle", "target-arrow-color": css("--rikyu"), "arrow-scale": .6 } },
      { selector: ".faded", style: { opacity: .12 } },
      { selector: "edge.hot", style: { "line-color": css("--shu"), "target-arrow-color": css("--shu"), width: 1.5, label: "data(rel)", "font-size": 9, color: css("--nezumi") } },
      { selector: "node:selected", style: { width: 17, height: 17 } }],
    layout: { name: "cose", animate: false, padding: 48, nodeRepulsion: 9000, idealEdgeLength: 90 } });
    cy.ready(() => { cy.fit(undefined, 48); if (cy.zoom() > 1.1) { cy.zoom(1.1); cy.center(); } });
    const focus = (n) => { cy.elements().removeClass("faded hot"); const near = n.closedNeighborhood(); cy.elements().not(near).addClass("faded"); near.edges().addClass("hot"); describe(box, n.data()); };
    cy.on("tap", "node", (e) => focus(e.target));
    cy.on("tap", (e) => { if (e.target === cy) cy.elements().removeClass("faded hot"); });
    q.addEventListener("input", () => { const v = q.value.trim().toLowerCase(); cy.elements().removeClass("faded hot"); if (!v) return;
      const hit = cy.nodes().filter((n) => n.data("label").toLowerCase().includes(v)); cy.elements().not(hit).addClass("faded"); if (hit.length === 1) focus(hit[0]); });
  };
  kinds.forEach((k) => { const x = el("button", "on", k); x.onclick = () => { off.has(k) ? off.delete(k) : off.add(k); x.classList.toggle("on");
    cy.nodes().forEach((n) => n.style("display", off.has(n.data("kind")) ? "none" : "element")); }; tools.append(x); });
  const b3 = el("button", null, "三维"); tools.append(b3); let g3 = null;
  b3.onclick = async () => { const on = b3.classList.toggle("on");
    if (!on) { g3._destructor(); g3 = null; host.replaceChildren(); start(); return; }
    const { default: FG } = await import("3d-force-graph"); cy.destroy(); host.replaceChildren();
    g3 = FG()(host).width(host.clientWidth).height(host.clientHeight).backgroundColor(css("--gofun"))
      .graphData({ nodes: b.nodes.map((n) => ({ ...n })), links: b.edges.map((e) => ({ source: e.from, target: e.to })) })
      .nodeLabel("label").nodeColor((n) => colour(n.kind || "其他")).linkColor(() => css("--rikyu")).linkOpacity(.5).onNodeClick((n) => describe(box, n)); };
  root.mount = () => { if (!cy && !g3) start(); }; describe(box, b.nodes[0]); return root;
}
