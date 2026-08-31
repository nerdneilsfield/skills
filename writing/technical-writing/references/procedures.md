# Procedures

procedure 是可执行、按顺序完成任务的一组动作。tutorial、how-to、deployment、user manual、troubleshooting 和 test-verification 可共享这些规则，但各自读者意图仍不同。

## Required information

在步骤前给出执行者做计划所需的信息：

- 任务目标和适用范围；
- prerequisites：版本、权限、工具、材料、环境、设备状态和备份；
- 会改变路线的条件或限制；
- 预计停机、数据影响或不可逆操作；
- 相关 Warning 或 Caution。

不要把核心前置条件藏在第 4 步或 Note 中。若条件只影响某一步，将条件紧靠该步并置于动作之前。

## Write executable steps

1. 每一步以动作开始。中文用明确动词；英文用 imperative。
2. 一步通常只包含一个主要动作。紧密相连且发生在同一位置的小动作可合并。
3. 按读者实际执行顺序排列。位置、模式和条件先于动作。
4. 写出必需的按钮、命令、参数、值、单位和确认动作。
5. 动作产生读者需要识别的状态时，紧接着写 expected result。
6. 读者必须作选择时，说明判断条件，而非只列选项。

Bad:

> 1. 写入配置，完成后重启服务，如使用外部数据库则先迁移 schema。

Good:

> 如果使用外部数据库，先运行 `acme migrate` 迁移 schema。
>
> 1. 将配置写入 `/etc/acme/config.yaml`。
> 2. 运行 `systemctl restart acme`。
> 3. 确认 `systemctl is-active acme` 返回 `active`。

## Commands and output

复杂命令步骤按以下顺序写：

1. 说明命令要完成的动作。
2. 给出命令，不带 shell prompt。
3. 解释占位符、变量和必须替换的值。
4. 必要时解释副作用或关键 option。
5. 给出与正文一致的预期输出。
6. 说明如何判断成功。

命令与输出分开标注。不得把 `$`、`#` 等 prompt 混进可复制命令，除非 prompt 本身是讲解对象。

## Optional steps and branches

- 可选步骤在开头明确标记：`可选：` 或 `Optional:`。
- 不同条件产生不同动作时，先写条件，再写对应动作。
- 主路径优先。替代方法只有在面向不同环境、权限或可访问性需求时才保留，并分别成节。
- 不要同时给出多条等价路径让读者自行猜“最佳方法”。默认记录最短、最可靠且可访问的路径。

## Expected result and verification

expected result 是动作后的可观察状态；verification 是确认整体目标是否达成的方法。二者不可用“成功”“正常”代替具体证据。

Bad:

> 服务应正常启动。

Good:

> `GET /healthz` 返回 HTTP `200`，响应体中的 `status` 为 `ready`。

test-verification 还须定义测量方法、容差及 pass/fail criteria；见文档类型规则和模板。

## Warnings, cautions, and notes

- Warning/Caution 放在危险动作之前，不能放在动作后的结果段。
- Note 只补充理解或效率信息，不承载必需条件、步骤或风险。
- 不因视觉突出而重复正文；callout 必须有独立功能。
- 安全写法详见 [warnings-safety.md](warnings-safety.md)。

## UI procedures

- 优先描述目标；只有 UI 位置不明显或必须逐步导航时才描述控件。
- UI 标签逐字匹配界面，并按项目格式标记，通常用粗体。
- 说明动作发生的位置：`在 **Network** 页，选择 **Add route**。`
- 菜单路径可写为 `**File > Export > PDF**`，但不要用 `>` 串联不同类型的复杂交互。
- 优先使用输入方式中立的动词，如“选择”“打开”“输入”；只有动作确实依赖鼠标、触摸或键盘时才写“单击”“轻扫”“按住”。
- 避免“上方”“右侧”等仅靠视觉方向定位的表述；使用控件名称、区域名或可访问标签。

## Troubleshooting procedures

按以下顺序组织：

1. 可搜索的症状或原始错误信息。
2. 适用环境和影响范围。
3. 可能原因；多个原因与解决方法一一对应。
4. 先无损、后有损的诊断步骤。
5. workaround 或 resolution。
6. 验证恢复的方法。
7. 停止条件和升级信息，例如需要保留的日志、测量值或现场状态。

不得把删除数据、禁用安全控制、短接信号或超规格运行当成普通“尝试”。确需进行时，先写风险、备份/隔离措施和恢复路径。

## Procedure check

- 读者能否在开始前准备好权限、材料、版本、停机和备份？
- 每一步是否包含可执行动作？
- 条件、位置和目标是否在动作之前？
- 必填参数、值、单位和确认操作是否齐全？
- 顺序是否明确；可选项与分支是否可判断？
- 是否有可观察的 expected result 和最终 verification？
- 风险信息是否在危险动作之前？

