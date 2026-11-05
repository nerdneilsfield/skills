# Skills

[中文](#中文) | [English](#english)

## 中文

本仓库收录可复用的 Agent Skills，涵盖编码工作流、Git 提交、论文精读、文本去 AI 化、技术写作和文学风格改写。每个 skill 都以 `SKILL.md` 为入口，可通过 [Skills CLI](https://github.com/vercel-labs/skills) 安装。工具选型见 [推荐工具](RECOMMENDED_TOOLS.md)。

### 可用 skills

| Skill | 用途 |
| --- | --- |
| [`qi-read-paper`](research/qi-read-paper/) | 用户给出论文要求精读、评估复现，或论文和代码对照着读时使用，可选对话或生成网页；只问一个具体点时直接回答。不用于写技术文档或改文风。 |
| [`research-hypothesis`](research/research-hypothesis/) | 把观察、假设、机制、预测和证据分开，运行前定好能区分假设的预测。 |
| [`paper-library`](research/paper-library/) | 用分层索引管理本地文献目录，按索引导航，不整篇读大文件。 |
| [`research-figure`](research/research-figure/) | 不绑定生图工具，制作学术图和技术图，含可编辑源文件。 |
| [`research-report`](research/research-report/) | 用户要求基于多个来源写调研报告或综述时使用：来源简述、大纲、分章、配图、全文审阅与导出。 |
| [`paper-search`](research/paper-search/) | 用户要求找论文、查相关工作或追引用时使用：扩展检索词、多来源交叉、按既定标准筛选、记录检索过程与停止条件。不用于精读单篇（qi-read-paper）或据此写综述（research-report）。 |
| [`paper-compare`](research/paper-compare/) | 用户要求横向比较多篇方法或做对比表时使用：区分作者声称、实验证据与你的推断，标出不可比的指标和数据集。不用于找论文或精读单篇。 |
| [`paper-to-code`](research/paper-to-code/) | 用户要求按论文写实现时使用：把公式、算法步骤和符号映射到代码，记录代码与论文的差异、未写明的超参和实现技巧。不用于读懂论文（qi-read-paper）或复现数字（paper-reproduce）。 |
| [`paper-reproduce`](research/paper-reproduce/) | 用户要求复现论文报告的数字或验证某条主张时使用：先定目标值与容差，先跑作者代码或基线，再区分方法、环境与设置三类偏差。不用于从零实现（paper-to-code）或设计新实验（algorithm-experiment）。 |
| [`algorithm-experiment`](research/algorithm-experiment/) | 用户要跑实验验证算法想法时使用：先定假设、基线与指标，每次只改一处做消融，按种子报告离散度，逐次记录运行，防数据泄漏与调参偏差。不用于设计方法（algorithm-design）或复现他人数字（paper-reproduce）。 |
| [`algorithm-design`](research/algorithm-design/) | 用户要从问题出发设计新方法时使用：列候选、分析复杂度与失败模式、先建最简基线，并判断何时停止加组件。不用于跑对比实验（algorithm-experiment）。 |
| [`orchestrate`](agents/orchestrate/) | 仅手动调用。不绑定工具地协调多个 agent：判断是否派发、任务状态与结果整合。 |
| [`eval-plan`](agents/eval-plan/) | 仅手动调用。预注册模型评测，先干跑和小样本试跑，批准后全量运行。 |
| [`agent-brief`](agents/agent-brief/) | 把工作交给其他 agent 或新会话时使用。 |
| [`agent-verify`](agents/agent-verify/) | agent 报告完成或疑似卡住时使用：按证据决定接受、重试或替换。 |
| [`spec`](agents/spec/) | 仅手动调用。把已讨论清楚的内容整理成规格（目标、约束、不做什么、可验收检查），可选拆成票，写本地文件，只用于跨会话或派发的工作。不用于盘问未决问题（grill-me）或实现。 |
| [`council`](agents/council/) | 仅手动调用。决策有多条可信路径时使用：怀疑者、务实者、批评者独立表态后汇总，防止锚定，先给证据不给结论。不用于代码审查、实现或答案明确的问题。 |
| [`steward-board`](agents/steward-board/) | 仅手动调用。把一批 chronicle 事件和证据写成 `BOARD.md` 与项目日记录，保留批次、证据与缺口，最后推进消费水位；只读查询不改状态。不用于写日报周报或提炼项目经验。 |
| [`steward-reports`](agents/steward-reports/) | 仅手动调用。从同一批证据生成 `daily/<date>.md` 和 `weekly/<year>-W<week>.md`，事实、结果、卡点与缺口分开写，下一步只作建议。不用于更新白板或提炼项目经验。 |
| [`co-commit`](coding/co-commit/) | 用户要求按仓库惯例分组并逐次本地提交时使用。不用于 push、开 PR 或改写历史。 |
| [`counterweight`](coding/counterweight/) | 用户要求实现、修复、重构或调试代码时使用，并按证据选择最轻流程。不用于答疑、独立评审、写文档、初始化 `AGENTS.md` 或事后删减清单。 |
| [`counterweight-setup`](coding/counterweight-setup/) | 用户要求在仓库根 `AGENTS.md` 启用或修复 Counterweight 时使用。不用于实现功能或列删减清单。 |
| [`counterweight-cut`](coding/counterweight-cut/) | 实现之后，用户询问这次 diff 里什么没挣到留下资格时使用。默认只出清单，用户点名才改。不用于实现功能或正确性审查。 |
| [`cpp`](coding/cpp/) | 编写、审阅或维护 C++ 时使用，可与专科技能同时加载，提供语言、所有权与接口约定。新建项目或重构构建交给 `cpp-project-init`。 |
| [`cpp-project-init`](coding/cpp-project-init/) | 用户要求新建 C++ 项目，或改 CMake presets、vendor 与命令入口时使用。不用于普通源码修复、排错、性能或数值内核。 |
| [`cpp-testing`](coding/cpp-testing/) | 编写、修复或整理 C++ 测试、CTest 接线与不稳定测试。崩溃原因未明时交给 `cpp-debug`。 |
| [`cpp-debug`](coding/cpp-debug/) | 最小排查后仍未解释的崩溃、挂起、数据竞争、内存破坏或不确定失败。数值契约问题交给 `cpp-numerics`。 |
| [`cpp-performance`](coding/cpp-performance/) | 用户要求优化，或已测量到 C++ CPU 延迟、吞吐、缓存、线程或内存问题。崩溃交给 `cpp-debug`，数值模型交给 `cpp-numerics`。 |
| [`cpp-numerics`](coding/cpp-numerics/) | Eigen、残差、求解器、流形或数值数据边界的正确性、不稳定结果，以及由模型、布局或精度导致的慢。进程级性能交给 `cpp-performance`。 |
| [`python`](coding/python/) | 编写、审阅或维护 Python 时使用，可与专科技能同时加载，提供数据契约、可变性、资源与失败约定。 |
| [`python-testing`](coding/python-testing/) | 编写、修复或整理 Python 测试、夹具、mock 与不稳定测试。未解释的故障交给 `python-debug`。 |
| [`python-debug`](coding/python-debug/) | 崩溃、挂起、卡住的异步任务，或看完首个 traceback 仍未解释的失败。 |
| [`python-project-init`](coding/python-project-init/) | 用户要求新建 Python 项目，或添加 pyproject、Ruff、ty、pytest 配置时使用。不用于普通修复。 |
| [`python-performance`](coding/python-performance/) | 测量并修复 Python 热点、等待、内存增长或扩展性。不用于数值内核、环境修复、训练循环或表格分析。 |
| [`python-numerics`](coding/python-numerics/) | 数组形状、dtype、布局、精度、求解器、BLAS 或 JIT 边界。进程级剖析交给 `python-performance`。 |
| [`python-environments`](coding/python-environments/) | 创建、复现或修复 uv、venv、Conda、Pixi、锁文件、离线制品与 CUDA/原生 ABI。不用于写 CUDA kernel 或改数值算法。 |
| [`python-ml`](coding/python-ml/) | 经典机器学习或深度学习的划分、训练、评估、checkpoint 与训练循环性能。描述性表格交给 `python-data-analysis`。 |
| [`python-data-analysis`](coding/python-data-analysis/) | 表格、时间或缺失数据的连接、分组口径、大规模聚合与诚实可视化。预测训练交给 `python-ml`。 |
| [`grill-me`](coding/grill-me/) | 用户明确要求拷问或压力测试计划、设计或决策时使用。不用于直接实现该计划。 |
| [`project-learning`](coding/project-learning/) | 把用户纠正、重复失败或已核实的非显然事实放到真正起作用的位置，也用于写 `.cw/PRACTICES.md`、`.cw/BUGS.md`、复盘和清理过期指引；跨项目经验先进待批列表，用户确认后才写全局实践。不用于启用 Counterweight 或写用户文档。 |
| [`code-reading`](coding/code-reading/) | 用户要读陌生仓库或大模块时使用：先建地图，沿数据流找到核心循环，结论带 文件:行号，区分读到的与推断的。不用于审查某个改动（code-review）或重设计模块（codebase-design）。 |
| [`interactive-guide`](coding/interactive-guide/) | 用组件模板生成交互网页：调用动画、从小白到专家的学习路径、单页回答和演示模式。图片内联，库默认走 CDN。 |
| [`code-review`](coding/code-review/) | 用户要求审查某个改动时使用：先定基线 commit，沿仓库规范与需求两条线审查，只报能给出失败场景的问题。不用于评审自己刚写的 diff 或做模块设计批评（codebase-design）。 |
| [`codebase-design`](coding/codebase-design/) | 用户要设计或改进模块接口、决定接缝位置、提高可测性时使用：深模块、接缝、测试边界，有证据才改结构，与 counterweight 配合。不用于实现改动或审查 diff。 |
| [`tool-compose`](coding/tool-compose/) | 用户要决定用什么工具查代码或语料，或检索为空、噪声太大时使用：按问题类型分层路由，缺失工具时给退路，并核对结果。不用于审查改动、设计模块或通读仓库。 |
| [`deai`](writing/deai/) | 用户要求审阅或改写中英文里的模板化、官僚化、说教式或防御性 AI 写作痕迹时使用。不用于从零写技术文档或鲁迅文风。 |
| [`luxun-style`](writing/luxun-style/) | 用户要求用鲁迅的语气、用词、逻辑和修辞写作或改写时使用。不用于技术文档或论文精读。 |
| [`technical-writing`](writing/technical-writing/) | 用户要求写作、改写或审阅软件、硬件和工程技术文档时使用。不用于学术论文或学术稿件、鲁迅文风或单纯去 AI 化。 |
| [`academic-writing`](writing/academic-writing/) | 算法、硬件和软硬件协同论文的写作、修改、审计与回复审稿。 |
| [`typst-slides`](writing/typst-slides/) | 用 Typst 投影做研究汇报、项目评审、答辩和客户演示，可复现现有模板。 |
| [`podcast`](writing/podcast/) | 把资料写成多人播客逐字稿，并用可配置的 TTS 合成音频。 |

### 安装

运行以下命令前，请确认系统中可以使用 `npx`。先查看仓库内可安装的 skills：

```bash
npx skills add nerdneilsfield/skills --list
```

全局安装全部 skills，并为 CLI 识别到的所有 agent 启用：

```bash
npx skills add nerdneilsfield/skills --all -g
```

Skills CLI 默认安装到当前项目。只安装一个 skill 时，使用 `--skill` 指定名称：

```bash
npx skills add nerdneilsfield/skills --skill technical-writing
```

只全局安装一个 skill 时，添加 `-g`：

```bash
npx skills add nerdneilsfield/skills --skill technical-writing -g
```

安装后，可在支持 Agent Skills 的 agent 中按名称调用相应 skill。例如：

```text
使用 $technical-writing 改写这份部署指南。
```

`counterweight` 覆盖实现、修复、重构和调试，供隐式选择。根 `AGENTS.md` 归 `counterweight-setup`；实现后的删减清单归 `counterweight-cut`。具体文本以各 skill 为准。

C++ 技能可离线使用。`cpp` 只保留共享语言与接口约定。新建项目与 vendor 归 `cpp-project-init`，崩溃与未解释失败归 `cpp-debug`，已测量的 CPU 与线程预算归 `cpp-performance`，Eigen 与求解器数值契约归 `cpp-numerics`。先加载一个专用技能，证据跨界时再加载另一个。验证方法见 [tests/README.md](tests/README.md)。

Python 同样按症状选择专用技能：新建项目归 `python-project-init`，测试归 `python-testing`，排错归 `python-debug`，环境归 `python-environments`，热点归 `python-performance`，数组与求解器归 `python-numerics`，训练与评估归 `python-ml`，表格与图表归 `python-data-analysis`。`python` 保留共享契约，可与专用技能同时加载。技能正文离线自足，实际离线重建仍需预先准备兼容制品。各资产提供独立运行入口，完整仓库测试见 [tests/README.md](tests/README.md)。

### 仓库结构

Skills 按用途存放在 `coding/`、`writing/` 和 `research/` 中。每个 skill 的规则位于该目录的 `SKILL.md`，详细规范、脚本和测试放在同一 skill 目录内。

本项目采用 [MIT License](LICENSE)。

## English

This repository contains reusable Agent Skills for coding workflows, Git commits, paper reading, de-AI editing, technical writing, and literary-style rewriting. Each skill uses `SKILL.md` as its entry point and can be installed with the [Skills CLI](https://github.com/vercel-labs/skills). Tool selection is covered in [Recommended tools](RECOMMENDED_TOOLS.md).

### Available skills

| Skill | Purpose |
| --- | --- |
| [`qi-read-paper`](research/qi-read-paper/) | Use when the user supplies a paper and asks for a close reading, round-by-round explanation, or reproduction assessment. Answer a single concrete question directly. Not for writing technical docs or changing literary voice. Optional web page and paper-to-code round. |
| [`research-hypothesis`](research/research-hypothesis/) | Keep observation, hypothesis, mechanism, prediction, and evidence apart, and fix discriminating predictions before running. |
| [`paper-library`](research/paper-library/) | Manage a local paper folder through layered indexes, without reading large files whole. |
| [`research-figure`](research/research-figure/) | Make academic and technical figures with any image backend, with editable sources. |
| [`research-report`](research/research-report/) | Use for research reports or surveys from many sources: source notes, outline, chapters, figures, full review, and export. |
| [`paper-search`](research/paper-search/) | Use when the user asks to find papers, gather related work, or track citations: expand the query, cross-check several sources, screen against stated criteria, and log the search and its stopping rule. Not for reading one paper (qi-read-paper) or writing the survey from the hits (research-report). |
| [`paper-compare`](research/paper-compare/) | Use to compare several methods side by side or build a comparison table: separate the authors' claims from measured evidence and your inference, and flag metrics or datasets that are not comparable. Not for finding the papers or reading one closely. |
| [`paper-to-code`](research/paper-to-code/) | Use when implementing a paper's method: map its equations, steps, and notation to code, and record where the code differs from the paper and which hyperparameters it never states. Not for reading the paper (qi-read-paper) or reproducing its numbers (paper-reproduce). |
| [`paper-reproduce`](research/paper-reproduce/) | Use to reproduce a paper's reported numbers or test a claim: fix the target and tolerance first, run the authors' code or a baseline, then attribute a mismatch to the method, the environment, or the setup. Not for implementing from scratch (paper-to-code) or designing new experiments (algorithm-experiment). |
| [`algorithm-experiment`](research/algorithm-experiment/) | Use to run experiments on an algorithmic idea: fix the hypothesis, baseline, and metric, ablate one thing at a time, report seed spread, log every run, and guard against leakage and tuning bias. Not for designing the method (algorithm-design) or reproducing a published number (paper-reproduce). |
| [`algorithm-design`](research/algorithm-design/) | Use to design a method from a problem: enumerate candidates, analyze complexity and failure modes, build the simplest baseline first, and decide when to stop adding components. Not for running the comparison (algorithm-experiment). |
| [`orchestrate`](agents/orchestrate/) | Manual only. Coordinate several agents toward one goal, independent of the runtime: delegation, task status, and integration. |
| [`eval-plan`](agents/eval-plan/) | Manual only. Preregister a model-backed eval, dry-run and pilot it, then approve the full run. |
| [`agent-brief`](agents/agent-brief/) | Use when handing work to another agent or a fresh session. |
| [`agent-verify`](agents/agent-verify/) | Use when an agent reports done or looks stalled: check against evidence, then accept, retry, or replace. |
| [`spec`](agents/spec/) | Manual only. Turn what was already discussed into a specification (goal, constraints, out of scope, checkable acceptance), optionally split into tickets, written to local files, only for work crossing a session or delegated. Not for interviewing about open choices (grill-me) or implementing. |
| [`council`](agents/council/) | Manual only. Use when a decision has several credible paths: get independent positions from a skeptic, a pragmatist, and a critic, then surface the disagreement instead of hiding it. Not for code review, implementation, or a question with one answer. |
| [`steward-board`](agents/steward-board/) | Manual only. Turn a batch of chronicle events and evidence into `BOARD.md` and the project day records, keeping batch, evidence, and gap ids, then advance the watermark; a read-only query changes nothing. Not for daily or weekly reports or distilling practices. |
| [`steward-reports`](agents/steward-reports/) | Manual only. Write `daily/<date>.md` and `weekly/<year>-W<week>.md` from the same evidence, with facts, results, blockers, and gaps kept apart and next steps marked as suggestions. Not for refreshing the board or distilling practices. |
| [`co-commit`](coding/co-commit/) | Use when the user asks to group uncommitted work by the repo's commit conventions and create the local commits. Not for push, opening a PR, or rewriting history. |
| [`counterweight`](coding/counterweight/) | Use when the user asks to implement, fix, refactor, or debug code, and pick the lightest process the evidence supports. Not for Q&A, standalone review, prose, root `AGENTS.md` setup, or a post-diff cut list. |
| [`counterweight-setup`](coding/counterweight-setup/) | Use when the user asks to enable or repair Counterweight in the repository root `AGENTS.md`. Not for implementing features or listing cuts. |
| [`counterweight-cut`](coding/counterweight-cut/) | After implementation, use when the user asks what in this diff did not earn the cost of staying. Default is a cut list; edit only when the user asks to apply it. Not for implementing features or correctness review. |
| [`cpp`](coding/cpp/) | Use when writing, reviewing, or maintaining C++, including alongside a specialist, for language, ownership, and interface conventions. Hand project creation or build restructuring to `cpp-project-init`. |
| [`cpp-project-init`](coding/cpp-project-init/) | Use when the user asks to create a C++ project or restructure CMake presets, vendored dependencies, or command entry points. Not for ordinary fixes, crashes, CPU tuning, or numerical kernels. |
| [`cpp-testing`](coding/cpp-testing/) | Use to write, fix, or organize C++ tests, CTest wiring, and flaky tests. Hand unexplained crashes to `cpp-debug`. |
| [`cpp-debug`](coding/cpp-debug/) | Use for crashes, hangs, races, memory corruption, or failures still unexplained after the first diagnostic. Hand numerical-contract bugs to `cpp-numerics`. |
| [`cpp-performance`](coding/cpp-performance/) | Use when the user asks to optimize C++ CPU code, or for measured latency, throughput, cache, thread, or memory problems. Hand crashes to `cpp-debug` and numerical models to `cpp-numerics`. |
| [`cpp-numerics`](coding/cpp-numerics/) | Use for Eigen, residuals, solvers, manifolds, or numerical data-boundary correctness, including unstable results and slowness rooted in the model, layout, or precision. Hand process-wide performance to `cpp-performance`. |
| [`python`](coding/python/) | Use when writing, reviewing, or maintaining Python, including alongside a specialist, for data, mutation, resource, and failure contracts. |
| [`python-testing`](coding/python-testing/) | Use to write, fix, or organize Python tests, fixtures, mocks, and flaky tests. Hand unexplained failures to `python-debug`. |
| [`python-debug`](coding/python-debug/) | Use for crashes, hangs, stuck tasks, and failures still unexplained after the first traceback. |
| [`python-project-init`](coding/python-project-init/) | Use when asked to create a Python project or add pyproject, Ruff, ty, or pytest configuration. Not for ordinary fixes. |
| [`python-performance`](coding/python-performance/) | Use when measuring or fixing Python hotspots, waiting, memory growth, or scaling. Not for numerical kernels, environment repair, training loops, or tabular analysis. |
| [`python-numerics`](coding/python-numerics/) | Use for array shape, dtype, layout, precision, solvers, BLAS, or JIT boundaries. Hand process-wide profiling to `python-performance`. |
| [`python-environments`](coding/python-environments/) | Use when creating, reproducing, or repairing uv, venv, Conda, Pixi, lockfiles, offline artifacts, or CUDA/native ABI. Not for writing CUDA kernels or changing numerical algorithms. |
| [`python-ml`](coding/python-ml/) | Use for classical ML or deep-learning splits, training, evaluation, checkpoints, and training-loop performance. Hand descriptive tables to `python-data-analysis`. |
| [`python-data-analysis`](coding/python-data-analysis/) | Use for tabular, time, or missing-data joins, grouping, large aggregation, and honest charts. Hand predictive training to `python-ml`. |
| [`grill-me`](coding/grill-me/) | Use when the user explicitly asks to grill or stress-test a plan, design, or decision. Not for implementing that plan. |
| [`project-learning`](coding/project-learning/) | Use to put user corrections, repeated failures, and verified non-obvious facts where they change behavior; also to write `.cw/PRACTICES.md` and `.cw/BUGS.md`, run retros, and prune stale guidance. Cross-project lessons queue as candidates and become global practices only after the user confirms. Not for enabling Counterweight or user-facing docs. |
| [`code-reading`](coding/code-reading/) | Use to read an unfamiliar repository or a large module: build a map, follow the data flow to the core loop, cite `file:line`, and keep what you read separate from what you inferred. Not for reviewing a change (code-review) or redesigning a module (codebase-design). |
| [`interactive-guide`](coding/interactive-guide/) | Build an interactive page from a component template: animated flows, beginner-to-expert paths, one-page answers, and slides. Images are inlined; libraries use a CDN by default. |
| [`code-review`](coding/code-review/) | Use to review a change against a fixed baseline: check the repository's standards and the spec as two separate lines, and report only problems you can state a failing scenario for. Not for reviewing your own fresh diff or a design critique (codebase-design). |
| [`codebase-design`](coding/codebase-design/) | Use to design or improve a module's interface, place a seam, or make code testable: deep modules, real seams, the interface as the test surface, structure changed only with evidence. Not for implementing the change or reviewing a diff. |
| [`tool-compose`](coding/tool-compose/) | Use to choose how to investigate a codebase or corpus, or when a search returns nothing or too much: route by question type, fall back when a tool is missing, and verify the result. Not for reviewing a change, designing a module, or reading a repository end to end. |
| [`deai`](writing/deai/) | Use when the user asks to review or rewrite Chinese or English prose that sounds templated, bureaucratic, paternalistic, or defensively AI-written. Not for authoring technical docs from scratch or Lu Xun voice. |
| [`luxun-style`](writing/luxun-style/) | Use when the user asks to write or rewrite in Lu Xun's tone, diction, reasoning, and rhetoric. Not for technical documentation or paper reading. |
| [`technical-writing`](writing/technical-writing/) | Use when the user asks to write, rewrite, or review software, hardware, or engineering documentation. Not for academic papers or scholarly manuscripts, Lu Xun voice, or a de-AI-only pass. |
| [`academic-writing`](writing/academic-writing/) | Write, revise, audit, and answer reviewers for algorithm, hardware, and co-design papers. |
| [`typst-slides`](writing/typst-slides/) | Build talks, reviews, defences, and client demos as Typst slides, and replicate existing templates. |
| [`podcast`](writing/podcast/) | Turn material into a multi-host podcast script and synthesize it with a configurable TTS backend. |

### Install

Before running these commands, make sure `npx` is available. List the skills that the repository provides:

```bash
npx skills add nerdneilsfield/skills --list
```

Install every skill globally and enable it for every agent detected by the CLI:

```bash
npx skills add nerdneilsfield/skills --all -g
```

The Skills CLI installs into the current project by default. To install one skill, select it with `--skill`:

```bash
npx skills add nerdneilsfield/skills --skill technical-writing
```

To install one skill globally, add `-g`:

```bash
npx skills add nerdneilsfield/skills --skill technical-writing -g
```

After installation, invoke a skill by name in an agent that supports Agent Skills. For example:

```text
Use $technical-writing to rewrite this deployment guide.
```

`counterweight` covers implementation, fixes, refactoring, and debugging for implicit selection. Root `AGENTS.md` belongs to `counterweight-setup`. A cut list after the diff belongs to `counterweight-cut`. The exact text lives in each skill.

C++ skills work offline. `cpp` keeps shared language and interface conventions. Project creation and vendoring belong to `cpp-project-init`, crashes and unexplained failures to `cpp-debug`, measured CPU and thread budgets to `cpp-performance`, and Eigen or solver numerical contracts to `cpp-numerics`. Start with one specialist and load another only when the evidence crosses its boundary. See [tests/README.md](tests/README.md) for validation.

Python follows the same split: new projects to `python-project-init`, tests to `python-testing`, diagnosis to `python-debug`, environments to `python-environments`, hotspots to `python-performance`, arrays and solvers to `python-numerics`, training and evaluation to `python-ml`, and tables and charts to `python-data-analysis`. `python` keeps the shared contract and can load alongside a specialist. Guidance is self-contained offline; actual offline reconstruction still requires compatible artifacts. Assets have standalone entrypoints; repository validation is documented in [tests/README.md](tests/README.md).

### Repository layout

Skills are grouped by purpose under `coding/`, `writing/`, and `research/`. Each skill keeps its rules in `SKILL.md`, with detailed references, scripts, and tests in that same skill directory.

This project is available under the [MIT License](LICENSE).
