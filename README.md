# Skills

[中文](#中文) | [English](#english)

## 中文

本仓库收录可复用的 Agent Skills，涵盖编码工作流、Git 提交、论文精读、文本去 AI 化、技术写作和文学风格改写。每个 skill 都以 `SKILL.md` 为入口，可通过 [Skills CLI](https://github.com/vercel-labs/skills) 安装。

### 可用 skills

| Skill | 用途 |
| --- | --- |
| [`qi-read-paper`](research/qi-read-paper/) | 用户给出论文并要求精读、逐轮讲解或评估复现时使用；只问一个具体点时直接回答。不用于写技术文档或改文风。 |
| [`research-report`](research/research-report/) | 用户要求基于多个来源写调研报告或综述时使用：来源简述、大纲、分章、配图、全文审阅与导出。 |
| [`orchestrate`](agents/orchestrate/) | 仅手动调用。不绑定工具地协调多个 agent：判断是否派发、任务状态与结果整合。 |
| [`agent-brief`](agents/agent-brief/) | 把工作交给其他 agent 或新会话时使用。 |
| [`agent-verify`](agents/agent-verify/) | agent 报告完成或疑似卡住时使用：按证据决定接受、重试或替换。 |
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
| [`project-learning`](coding/project-learning/) | 真实开发中刚核实、以后会反复付出代价的项目事实要写入现有指引时使用。不用于启用 Counterweight 或写用户文档。 |
| [`deai`](writing/deai/) | 用户要求审阅或改写中英文里的模板化、官僚化、说教式或防御性 AI 写作痕迹时使用。不用于从零写技术文档或鲁迅文风。 |
| [`luxun-style`](writing/luxun-style/) | 用户要求用鲁迅的语气、用词、逻辑和修辞写作或改写时使用。不用于技术文档或论文精读。 |
| [`technical-writing`](writing/technical-writing/) | 用户要求写作、改写或审阅软件、硬件和工程技术文档时使用。不用于学术论文或学术稿件、鲁迅文风或单纯去 AI 化。 |

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

This repository contains reusable Agent Skills for coding workflows, Git commits, paper reading, de-AI editing, technical writing, and literary-style rewriting. Each skill uses `SKILL.md` as its entry point and can be installed with the [Skills CLI](https://github.com/vercel-labs/skills).

### Available skills

| Skill | Purpose |
| --- | --- |
| [`qi-read-paper`](research/qi-read-paper/) | Use when the user supplies a paper and asks for a close reading, round-by-round explanation, or reproduction assessment. Answer a single concrete question directly. Not for writing technical docs or changing literary voice. |
| [`research-report`](research/research-report/) | Use for research reports or surveys from many sources: source notes, outline, chapters, figures, full review, and export. |
| [`orchestrate`](agents/orchestrate/) | Manual only. Coordinate several agents toward one goal, independent of the runtime: delegation, task status, and integration. |
| [`agent-brief`](agents/agent-brief/) | Use when handing work to another agent or a fresh session. |
| [`agent-verify`](agents/agent-verify/) | Use when an agent reports done or looks stalled: check against evidence, then accept, retry, or replace. |
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
| [`project-learning`](coding/project-learning/) | Use when real work just verified a durable project fact that later agents would otherwise rediscover. Not for enabling Counterweight or writing user-facing docs. |
| [`deai`](writing/deai/) | Use when the user asks to review or rewrite Chinese or English prose that sounds templated, bureaucratic, paternalistic, or defensively AI-written. Not for authoring technical docs from scratch or Lu Xun voice. |
| [`luxun-style`](writing/luxun-style/) | Use when the user asks to write or rewrite in Lu Xun's tone, diction, reasoning, and rhetoric. Not for technical documentation or paper reading. |
| [`technical-writing`](writing/technical-writing/) | Use when the user asks to write, rewrite, or review software, hardware, or engineering documentation. Not for academic papers or scholarly manuscripts, Lu Xun voice, or a de-AI-only pass. |

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
