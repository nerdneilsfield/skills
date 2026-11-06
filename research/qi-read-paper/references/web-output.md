# 网页输出

一次做完全部轮次，结果是一个可以反复翻看的页面。各轮要讲什么、证据如何核验，以 `SKILL.md` 为准，这里只说怎么做成页面。页面由 `interactive-guide` 构建，组件见其 `references/blocks.md`，保持它的配色和排版。没装这个 skill 时告诉用户安装，不要自己写 HTML。

## 1. 取得正文和图

先通读全文，再动手做页面。文字用 `pdftotext -layout`，公式损坏或双栏错乱时回看渲染页。

两个脚本分属 `qi-read-paper` 和 `interactive-guide` 两个 skill 目录，安装位置不固定。先定位，之后全部用绝对路径，可以在任何目录运行：

```sh
EXTRACT=$(find "$HOME" -path '*qi-read-paper/scripts/extract_figures.py' -print -quit)
BUILD=$(find "$HOME" -path '*interactive-guide/scripts/build_guide.py' -print -quit)
WORK=$PWD/work    # 工作目录，绝对路径；找不到脚本时问用户 skill 装在哪

python3 "$EXTRACT" /abs/paper.pdf --list
python3 "$EXTRACT" /abs/paper.pdf --pages 3,7 "$WORK/pages"
python3 "$EXTRACT" /abs/paper.pdf --crop 3 8 12 84 40 "$WORK/fig3.png"
```

`--pages` 也接受范围，如 `2-5,9`；页码越界会报一行错误并以状态 2 退出。裁切百分比相对于显示出来的页面（已应用页面旋转）。

矢量图不在 `pdfimages` 结果里，这是常态：先渲染整页，看清位置后用 `--crop` 按页面百分比裁切。每张图都要亲眼看过，确认没有裁掉坐标轴、图例或图注。

## 2. 写页面数据

存成 `$WORK/guide.json`，图片路径相对于它（如 `pages/page-3.png`），每个 tab 一页。读了代码时在第三轮后加“代码对照”页：

| 页 | `level` | 内容 |
| --- | --- | --- |
| 速览 | 概览 | 一句话、最关键的结果、一张核心图，读者一分钟知道值不值得读 |
| 第一轮 | 问题 | 问题、不足、贡献、推荐先看的图 |
| 第二轮 | 方法与证据 | 流程、公式、3 到 5 张关键图、比较是否公平 |
| 第三轮 | 局限与复现 | 可靠结论、假设、失败场景、最小复现路径、后续问题 |
| 代码对照 | 实现 | 读了代码时才有：`papercode` 逐条对照，`flow` 走真实调用 |
| 术语 | 附录 | 可选 |

组件的用法：

- 关键图用 `figuretour`，逐处高亮讲解，坐标是图片的百分比。不重要的图用 `figure`。
- 论文的图设 `origin: "paper"`，`ref` 写 `Fig. 3`；自己补的图设 `origin: "explain"`。
- 主张、证据、推断用 `claim` 分开，`where` 写章节、图表或公式编号。论文没说的写 `unknown`，不要补造。
- 公式用 `formula`，方法流程用 `flow`，一个步骤对应一个模块。
- 代码对照用 `papercode`，`status` 取 `match`、`differs`、`unstated`。构建时加 `--repo`，核对位置。
- 每轮结尾一道 `quiz`，考应用，不考复述。

## 3. 补充解释图

原图讲不清时才补。用 `research-figure` 选后端并制作。

解释图用来帮助理解，不能冒充实验结果：不画论文没有的数据，图注写明它是示意。

## 4. 构建

用上面定位到的 `$BUILD`，不必切换目录：

```sh
python3 "$BUILD" "$WORK/guide.json" "$WORK/paper.html"
```

打开检查每个 tab，确认图都显示了，`figuretour` 的高亮对得上。

## Gotchas

- 高亮坐标凭猜会对不上。看着裁好的图定坐标，构建后逐处核对。
- 提取出的数值可能错位。写进页面的每个数字都回到原表核对。
- 补充解释图容易比原图更好看，读者会把它当证据，所以 `origin` 不能省。
- 原图做成页面只供自己阅读。公开发布前确认论文的许可。
- 页面图片多时文件会很大。整页用 220 dpi 只作定位，正文只放裁切后的图。
- 只读到摘要时不要生成完整页面，说明缺什么。


完成后说明论文版本、读过的范围、页面路径和大小、原图与解释图数量，以及标为未报告或待核验的内容。
