import { readFileSync } from "node:fs";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

const pkg = JSON.parse(readFileSync("package.json", "utf8"));
const cdn = (name) => `https://cdn.jsdelivr.net/npm/${name}@${pkg.dependencies[name]}/+esm`;

// Default: small file, libraries from a pinned CDN URL. Offline: bundle everything.
export default defineConfig(({ mode }) => {
  const offline = mode === "offline";
  const libs = Object.keys(pkg.dependencies);
  return {
    plugins: [
      viteSingleFile(),
      !offline && {
        name: "import-map",
        transformIndexHtml: () => [{
          tag: "script",
          attrs: { type: "importmap" },
          children: JSON.stringify({ imports: Object.fromEntries(libs.map((n) => [n, cdn(n)])) }),
          injectTo: "head-prepend",
        }],
      },
    ],
    build: {
      target: "esnext",
      chunkSizeWarningLimit: 4000,
      rollupOptions: offline ? {} : { external: libs },
    },
  };
});
