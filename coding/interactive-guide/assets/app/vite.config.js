import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const pkg = JSON.parse(readFileSync("package.json", "utf8"));
const cdn = (name) => `https://cdn.jsdelivr.net/npm/${name}@${pkg.dependencies[name]}/+esm`;
const KATEX_CSS = `https://cdn.jsdelivr.net/npm/katex@${pkg.dependencies.katex}/dist/katex.min.css`;

// Offline bundles every dynamic import. Libraries that no block in this page uses are
// replaced by an empty module, so a two-block page does not carry mermaid and three.js.
const NEEDS = { katex: ["formula"], mermaid: ["mermaid"], cytoscape: ["graph"], "3d-force-graph": ["graph"] };
function unusedLibs() {
  let used;
  try { used = new Set(JSON.parse(readFileSync("src/data.json", "utf8")).pages.flatMap((p) => p.blocks.map((b) => b.type))); }
  catch { return []; }
  return Object.keys(NEEDS).filter((lib) => !NEEDS[lib].some((t) => used.has(t)));
}

// Default: small file, libraries from a pinned CDN URL. Offline: bundle everything.
export default defineConfig(({ mode }) => {
  const offline = mode === "offline";
  const libs = Object.keys(pkg.dependencies).filter((n) => !["marked", "highlight.js"].includes(n));
  return {
    plugins: [
      viteSingleFile(),
      !offline && {
        name: "import-map",
        transformIndexHtml: () => [
          { tag: "script", attrs: { type: "importmap" }, injectTo: "head-prepend",
            children: JSON.stringify({ imports: Object.fromEntries(libs.map((n) => [n, cdn(n)])) }) },
          { tag: "link", attrs: { rel: "stylesheet", href: KATEX_CSS }, injectTo: "head" },
        ],
      },
    ],
    resolve: {
      alias: offline ? unusedLibs().map((lib) => ({ find: new RegExp(`^${lib}(/.*)?$`), replacement: fileURLToPath(new URL("./src/stub.js", import.meta.url)) })) : [],
    },
    build: {
      target: "esnext",
      assetsInlineLimit: Number.MAX_SAFE_INTEGER,
      chunkSizeWarningLimit: 4000,
      rollupOptions: offline ? {} : { external: [...libs, /^katex\//] },
    },
  };
});
