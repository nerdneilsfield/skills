# Skills

[中文](#中文) | [English](#english)

## 中文

本仓库收录可复用的 Agent Skills，涵盖编码工作流、Git 提交、文本去 AI 化、技术写作和文学风格改写。每个 skill 都以 `SKILL.md` 为入口，可通过 [Skills CLI](https://github.com/vercel-labs/skills) 安装。

### 可用 skills

| Skill | 用途 |
| --- | --- |
| [`co-commit`](coding/co-commit/) | 分析 Git 变更，按仓库既有提交惯例分组并逐次提交。 |
| [`counterweight`](coding/counterweight/) | 让编码工作的流程、实现复杂度、测试和知识沉淀与当前证据及风险相称。 |
| [`grill-me`](coding/grill-me/) | 应用户要求，对计划、设计或决策做克制的压力测试。 |
| [`project-learning`](coding/project-learning/) | 将真实开发中发现的少量、持久且可复用的项目知识沉淀到现有项目指引。 |
| [`deai`](writing/deai/) | 审阅或改写中英文文本，减少模板化、官僚化、说教式和其他明显的 AI 写作痕迹，同时保留事实与技术含义。 |
| [`luxun-style`](writing/luxun-style/) | 以鲁迅的语气、用词、逻辑和修辞写作或改写杂文、散文和评论。 |
| [`technical-writing`](writing/technical-writing/) | 写作、改写和审阅软件、硬件及工程技术文档，不用于论文或学术稿件。 |

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

`counterweight` 的描述覆盖 coding implementation / modification，支持隐式 Skill 选择。若 Agent 依赖项目指令选择默认 Skill，可在项目 `AGENTS.md` 加一行：

```text
Use $counterweight by default for coding implementation and modification tasks.
```

### 仓库结构

Skills 按用途存放在 `coding/` 和 `writing/` 等目录中。每个 skill 的规则位于该目录的 `SKILL.md`，详细规范、脚本和测试仅在实际需要时提供。

本项目采用 [MIT License](LICENSE)。

## English

This repository contains reusable Agent Skills for coding workflows, Git commits, de-AI editing, technical writing, and literary-style rewriting. Each skill uses `SKILL.md` as its entry point and can be installed with the [Skills CLI](https://github.com/vercel-labs/skills).

### Available skills

| Skill | Purpose |
| --- | --- |
| [`co-commit`](coding/co-commit/) | Analyzes Git changes, groups them according to the repository's existing commit conventions, and creates the commits in sequence. |
| [`counterweight`](coding/counterweight/) | Keeps coding process, implementation complexity, tests, and retained knowledge proportional to current evidence and risk. |
| [`grill-me`](coding/grill-me/) | Pressure-tests a plan, design, or decision when the user explicitly requests it. |
| [`project-learning`](coding/project-learning/) | Persists small amounts of durable, reusable project knowledge discovered during real work. |
| [`deai`](writing/deai/) | Reviews or rewrites Chinese and English prose to reduce templated, bureaucratic, paternalistic, and other conspicuous AI-writing patterns while preserving facts and technical meaning. |
| [`luxun-style`](writing/luxun-style/) | Writes or rewrites essays, prose, and commentary in Lu Xun's tone, diction, reasoning, and rhetoric. |
| [`technical-writing`](writing/technical-writing/) | Writes, rewrites, and reviews software, hardware, and engineering documentation. It does not cover academic papers or scholarly manuscripts. |

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

The `counterweight` description covers coding implementation and modification for implicit Skill selection. If an agent relies on project instructions for default Skills, add one line to the project's `AGENTS.md`:

```text
Use $counterweight by default for coding implementation and modification tasks.
```

### Repository layout

Skills are grouped by purpose under directories such as `coding/` and `writing/`. Each skill keeps its rules in `SKILL.md` and includes detailed references, scripts, or tests only when they are needed.

This project is available under the [MIT License](LICENSE).
