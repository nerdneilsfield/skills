# Warnings and safety information

安全信息用于降低真实风险，不是视觉强调。项目、产品、法规或行业已有 signal word 和分级体系时，必须沿用；不要自行重新分级。

## Default use when no taxonomy exists

- **Warning:** 可能造成人身伤害、重大安全事件或严重安全暴露的条件。
- **Caution:** 可能造成设备、数据、财产、环境损坏，或不可逆错误结果的条件。
- **Note:** 有助于理解或提高效率的信息；不存在危险后果。

对受监管产品，以上默认值不替代适用法规、产品安全标准或风险评估。若缺少正式风险等级，标记待确认，不凭语气强弱猜测。

## Write complete safety messages

安全消息应让读者立即知道：

1. hazard：危险源或危险动作是什么；
2. consequence：可能发生什么；
3. avoidance：如何避免或降低风险；
4. condition：风险在何种状态、范围或人群中适用。

Bad:

> Warning: Be careful when servicing the board.

Good:

> **Warning:** 电源板带电时，散热器可能处于 325 V DC。接触散热器会导致严重电击。拆下外壳前，断开主电源，并确认 `DC_LINK` 测试点电压低于 30 V。

不要只写“注意安全”“谨慎操作”“可能存在风险”。

## Placement and sequence

- 在读者接触危险之前放置消息；不要等到步骤完成后再警告。
- 消息紧邻适用步骤。开篇安全章节不能代替逐步提示。
- 规避动作本身有顺序时，用可执行步骤写明。
- 风险持续存在时，在进入风险区域处重复必要信息；不要依赖远处交叉引用。
- 不把必需防护措施放入 Note 或括号。

## Distinguish emphasis from risk

以下内容通常不是 Warning：快捷技巧、常见错误、兼容性提示、性能建议、非破坏性失败。把它们写成普通正文、prerequisite 或 Note。

以下内容不能只写成 Note：

- 可能删除或不可恢复地修改数据；
- 可能使设备超过额定值、短路、过热或意外运动；
- 可能泄露 credential、降低安全控制或扩大权限；
- 可能导致人员暴露于电、热、机械、化学、辐射或其他危险。

## Software and data safety

破坏性命令应说明确切对象、范围、备份或恢复条件，以及无法恢复的部分。

Bad:

> Caution: This command may remove some data.

Good:

> **Caution:** `acme purge --all` 永久删除当前 tenant 的对象和 audit logs。命令不影响其他 tenant，但删除后无法从服务端恢复。运行前导出需要保留的 audit logs。

安全 workaround 不得建议长期禁用 TLS 验证、访问控制、interlock 或保护电路。若临时诊断确实需要降低保护，明确隔离环境、最短持续时间、恢复步骤和停止条件。

## Hardware safety

- 区分 absolute maximum ratings 与正常工作条件；前者不是可持续运行点。
- 说明断电、放电、锁定、接地、ESD、PPE 或机械固定要求及验证方法。
- 写明 residual energy、自动重启、远程启动、hot surface 和 moving parts 等非显而易见风险。
- 安全数值必须有来源、单位、测量点和条件。不得自行推断安全距离、等待时间或阈值。
- 示意图不能成为唯一安全说明；关键动作仍需文本表达。

## Review safety information

检查：风险是否真实且与动作相关；等级是否符合项目体系；hazard、consequence、avoidance、condition 是否完整；位置是否在危险动作之前；正文、图、标签和步骤是否一致。

