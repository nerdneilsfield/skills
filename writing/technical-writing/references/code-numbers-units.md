# Code, numbers, and units

## Code and technical identifiers

使用 inline code 标记需逐字输入或匹配的技术实体：

- commands、options、arguments 和 environment variables
- function、class、method、field、parameter 和 constant names
- filenames、paths、package names 和 configuration keys
- API methods、status codes、register names 和 signal names
- literal input/output、error messages 和 short code values

产品名、组织名和普通概念不用 code style。UI 标签通常用粗体；若 UI 中显示的是代码值，可按项目约定同时区分 UI 标签与输入值。

代码标识符不翻译、不改大小写、不加中文词形变化。给标识符补充普通名词，使句法清楚。

Bad:

> `POST` 数据后读取 `response` 的 `status`。

Good:

> 发送 `POST` 请求后，读取 `response.status` 字段。

## Code blocks and commands

- 指定语言或内容类型，以便正确高亮。
- 命令与输出分开；输出前写明“输出类似如下”，避免暗示动态值逐字相同。
- 不在可复制命令中包含 shell prompt。
- 占位符使用一致格式，如 `<device_id>`，并紧邻解释。
- 不用真实 secret、token、个人信息或生产地址作示例。
- 截断输出时说明省略内容；不要省略会影响判断的 warning、error 或状态字段。
- 示例版本与正文版本一致。

## Numbers

- 技术数值用数字表示，避免把精确值拼写成文字。
- 范围写清上下界是否包含；不要用含糊短横线表达负数范围。
- 小数精度应反映实际测量或接口精度，不补无意义的零。
- 表格列名或表头给出单位时，列内不要混入其他单位。
- 日期和时间使用无歧义格式，并给出时区：`2026-08-31 14:00 UTC+8` 或 ISO 8601。
- 版本号、错误码、地址、bit position 和 protocol value 保留权威格式。

## Units

- 数值与 SI unit symbol 之间留空格：`5 V`、`20 ms`、`2.4 GHz`。角度 `90°` 和百分比 `65%` 通常不留空格；遵从项目或行业标准时保持一致。
- 温度写作 `25 °C`；Kelvin 写作 `298 K`。
- 区间两端均写单位：`-40 °C to 85 °C`；中文可写 `-40 °C～85 °C`，但整个文档只选一种范围格式。
- unit symbol 不加复数，不随语言翻译；大小写有意义：`mW` 与 `MW` 不同。
- 区分 decimal 与 binary byte units：`MB`（10^6 bytes）和 `MiB`（2^20 bytes）。按被记录技术的真实计量体系写，不互换。
- rate 明确分母：`100 requests/s`、`1 Gbit/s`。`MB/s` 与 `Mbit/s` 不同。
- 首次出现不常见单位时定义测量基准或换算关系。

## Hardware notation

- 十六进制使用稳定前缀和位宽，如 `0x00FF`；必要时说明 signedness 和 endianness。
- bit range 采用项目约定，如 `bits [7:4]`，并说明编号方向。不要只写“高 4 位”。
- bit width 作前置修饰时写 `32-bit register`；中文写“32-bit 寄存器”或“32 位寄存器”，全篇一致。
- active-low signal 保留权威命名，如 `RESET_N`；首次说明低电平有效。
- register address 与 offset 不混用；若基址参与计算，给出公式和示例。
- timing symbol、波形标注和参数表必须一致。

## Lists, tables, and UI

- 有顺序的内容用 numbered list；无顺序项目用 bullets；属性比较用 table。
- 同一列表保持平行句法和一致标点。
- 表格前用一句话说明其用途；表头必须能独立解释各列。
- UI 标签逐字匹配当前界面，并使用项目约定的强调格式。不要用引号假装 UI 样式。
- 不依赖颜色、位置或图标形状作为唯一指示；给出名称或可访问文本。

## Accessibility

- 图片提供能表达其用途的 alt text；装饰图用空 alt。正文不得只在图片中提供关键事实。
- 代码、命令和终端输出使用文本，而非截图。
- 表格只用于真正的二维关系；避免合并单元格和在 procedure 中放复杂表格。
- 链接文字说明目标，不写“点击这里”。
- 视频或音频提供字幕、transcript 或等价说明。

