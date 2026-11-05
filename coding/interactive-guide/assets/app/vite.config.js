import { readFileSync } from "node:fs";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const pkg = JSON.parse(readFileSync("package.json", "utf8"));
const cdn = (name) => `https://cdn.jsdelivr.net/npm/${name}@${pkg.dependencies[name]}/+esm`;
const KATEX_CSS = `https://cdn.jsdelivr.net/npm/katex@${pkg.dependencies.katex}/dist/katex.min.css`;

// Default: small file, libraries from a pinned CDN URL. Offline: bundle everything.
export default defineConfig(({ mode }) => {
  const offline = mode === "offline";
  const libs = Object.keys(pkg.dependencies).filter((n) => n !== "marked");
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
    build: {
      target: "esnext",
      assetsInlineLimit: Number.MAX_SAFE_INTEGER,
      chunkSizeWarningLimit: 4000,
      rollupOptions: offline ? {} : { external: [...libs, /^katex\//] },
    },
  };
});
