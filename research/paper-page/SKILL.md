---
name: paper-page
description: "用户要求把一篇论文做成网页、一次读完三轮，或要带原图和讲解图的交互式精读时使用：一次完成问题、方法与证据、局限与复现三轮，生成内嵌论文原图和补充解释图的单文件网页。逐轮对话式精读用 qi-read-paper。不用于多篇比较（paper-compare）或综述（research-report）。"
license: MIT
compatibility: 需要 python3、poppler（pdfimages、pdftoppm）、Node 与 npm。依赖同仓库的 interactive-guide 和 qi-read-paper 两个 skill。
metadata:
  author: DengQi
---

# 把论文读成一个网页

一次做完 `qi-read-paper` 的三轮，结果是一个可以反复翻看的页面，不是一段聊天回复。三轮各自要讲什么、证据如何核验，以 `qi-read-paper` 为准，先读它。这里不分轮等待用户回复“继续”，也不省略任何一轮。

页面由 `interactive-guide` 构建，组件见其 `references/blocks.md`，保持它的配色和排版。缺少这两个 skill 时，告诉用户安装，不要自己写 HTML。

## 1. 取得正文和图

先通读全文，再动手做页面。文字用 `pdftotext -layout`，公式损坏或双栏错乱时回看渲染页。

在本 skill 目录下运行 `scripts/extract_figures.py`：

```sh
python3 scripts/extract_figures.py paper.pdf --list
python3 scripts/extract_figures.py paper.pdf --pages 3,7 work/pages
python3 scripts/extract_figures.py paper.pdf --crop 3 8 12 84 40 work/fig3.png
```

矢量图不在 `pdfimages` 结果里，这是常态：先渲染整页，看清位置后用 `--crop` 按页面百分比裁切。每张图都要亲眼看过，确认没有裁掉坐标轴、图例或图注。

## 2. 写页面数据

存成 `work/guide.json`，每个 tab 一页：

| 页 | `level` | 内容 |
| --- | --- | --- |
| 速览 | 概览 | 一句话、最关键的结果、一张核心图，读者一分钟知道值不值得读 |
| 第一轮 | 问题 | 问题、不足、贡献、推荐先看的图 |
| 第二轮 | 方法与证据 | 流程、公式、3 到 5 张关键图、比较是否公平 |
| 第三轮 | 局限与复现 | 可靠结论、假设、失败场景、最小复现路径、后续问题 |
| 术语 | 附录 | 可选 |

组件的用法：

- 关键图用 `figuretour`，逐处高亮讲解，坐标是图片的百分比。不重要的图用 `figure`。
- 论文的图设 `origin: "paper"`，`ref` 写 `Fig. 3`；自己补的图设 `origin: "explain"`。
- 主张、证据、推断用 `claim` 分开，`where` 写章节、图表或公式编号。论文没说的写 `unknown`，不要补造。
- 公式用 `formula`，方法流程用 `flow`，一个步骤对应一个模块。
- 每轮结尾一道 `quiz`，考应用，不考复述。

## 3. 补充解释图

原图讲不清时才补。按 `interactive-guide` 的插图顺序：自带生图工具，其他能生图的 agent，用户的画图 MCP，最后 SVG 或 Mermaid。

解释图用来帮助理解，不能冒充实验结果：不画论文没有的数据，图注写明它是示意。

## 4. 构建

在 `interactive-guide` 目录下运行：

```sh
python3 scripts/build_guide.py work/guide.json work/paper.html
```

打开检查每个 tab，确认图都显示了，`figuretour` 的高亮对得上。

## Gotchas

- 高亮坐标凭猜会对不上。看着裁好的图定坐标，构建后逐处核对。
- 提取出的数值可能错位。写进页面的每个数字都回到原表核对。
- 补充解释图容易比原图更好看，读者会把它当证据，所以 `origin` 不能省。
- 原图做成页面只供自己阅读。公开发布前确认论文的许可。
- 页面图片多时文件会很大。整页用 220 dpi 只作定位，正文只放裁切后的图。
- 只读到摘要时不要生成完整页面，说明缺什么。

## 汇报

说明论文版本、读过的范围、页面路径和大小、原图与解释图数量，以及标为未报告或待核验的内容。
