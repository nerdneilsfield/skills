import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import cmake from "highlight.js/lib/languages/cmake";
import cpp from "highlight.js/lib/languages/cpp";
import diff from "highlight.js/lib/languages/diff";
import go from "highlight.js/lib/languages/go";
import ini from "highlight.js/lib/languages/ini";
import javascript from "highlight.js/lib/languages/javascript";
import json from "highlight.js/lib/languages/json";
import python from "highlight.js/lib/languages/python";
import rust from "highlight.js/lib/languages/rust";
import typescript from "highlight.js/lib/languages/typescript";
import yaml from "highlight.js/lib/languages/yaml";

const LANGS = { bash, cmake, cpp, diff, go, ini, javascript, json, python, rust, typescript, yaml };
Object.entries(LANGS).forEach(([name, lang]) => hljs.registerLanguage(name, lang));
const EXT = { py: "python", pyi: "python", c: "cpp", h: "cpp", cc: "cpp", cpp: "cpp", cxx: "cpp", hpp: "cpp", hh: "cpp", js: "javascript", mjs: "javascript", jsx: "javascript", ts: "typescript", tsx: "typescript",
  rs: "rust", go: "go", sh: "bash", bash: "bash", zsh: "bash", cmake: "cmake", json: "json", yaml: "yaml", yml: "yaml", toml: "ini", ini: "ini", diff: "diff", patch: "diff" };
const ALIAS = { "c++": "cpp", c: "cpp", py: "python", js: "javascript", ts: "typescript", sh: "bash", shell: "bash", toml: "ini" };

function resolve(lang, file) {
  const named = lang && (ALIAS[lang.toLowerCase()] || lang.toLowerCase());
  if (named && LANGS[named]) return named;
  if (file?.endsWith("CMakeLists.txt")) return "cmake";
  return EXT[file?.split(".").pop()?.toLowerCase()];
}
function colour(code, source, lang, file) {
  const name = resolve(lang, file), out = name ? hljs.highlight(source, { language: name }) : hljs.highlightAuto(source, Object.keys(LANGS));
  code.innerHTML = out.value; code.classList.add("hljs");
}
export function codeBlock(source, lang, file) {
  const pre = document.createElement("pre"), code = document.createElement("code");
  colour(code, source, lang, file); pre.append(code); return pre;
}
export function highlightProse(root) {
  root.querySelectorAll("pre code").forEach((c) => colour(c, c.textContent, c.className.match(/language-([\w+-]+)/)?.[1]));
}
