// 答辩 / 开题 / 结题, 15-25 分钟。English labels are fine too; set lang: "en".
// 结构: 问题 -> 现状与缺口 -> 贡献 -> 方法 -> 结果 -> 不足 -> 计划 -> 致谢; 备份页放附录回答提问。
#import "theme.typ": *

#show: jp-theme.with(
  config-info(title: [基于缓存键复用的低延迟解码方法], subtitle: [硕士学位论文答辩],
    author: [答辩人：姓名], institution: [学院 / 导师：导师姓名], date: datetime(year: 2026, month: 11, day: 5)),
  lang: "zh",
  footer: [学位论文答辩],
)

#title-slide()

== 本文把解码延迟降低 40%，精度不变
#stats(
  stat("−40%", "中位解码延迟"),
  stat("3 项", "主要贡献", color: jp.green),
  stat("2 篇", "已发表论文", color: jp.purple),
)
#speaker-note[先讲结论，再说本文回答了什么问题。1 分钟。]

= 研究问题
== 批量越大，解码越受访存限制，现有方法无法绕开
- 现有方法优化计算，访存重复读取没有被处理
- 缺口：缺少在不改变输出的前提下复用中间结果的方法
#callout(title: "研究问题", kind: "key")[能否在不重新训练的前提下，跳过重复访存？]

= 贡献
== 本文有三项贡献
+ 提出只读缓存结构，输出与原模型一致
+ 给出访存次数的理论上界
+ 在三个任务上验证，延迟降低 20% 到 40%

= 方法与结果
== 只读缓存让每步少读一次键张量
#grid(columns: (1fr, 1fr), column-gutter: 1.5em,
  [
    - 编码器输出后，缓存只读
    - 解码器复用同一份键
    - 无需微调
  ],
  figure-slot("方法结构图：输入 - 编码器 - 键缓存 - 解码器", height: 7cm),
)

== 三个任务上延迟均下降，精度差在 0.1 以内
#table(columns: (2fr, 1fr, 1fr, 1fr), align: (left, right, right, right),
  [任务], [基线 (ms)], [本文 (ms)], [变化],
  [任务 A], [118], [74], [#text(fill: jp.green)[−37%]],
  [任务 B], [96], [70], [#text(fill: jp.green)[−27%]],
  [任务 C], [210], [126], [#text(fill: jp.green)[−40%]],
)
#source(label: "数据来源")[作者实验，单卡，5 次平均。请替换为自己的数据。]

= 不足与计划
== 小批量下没有收益，后续研究长序列
- 批量小于 8 时计算受限，缓存无益
- 任务 B 精度下降 0.4 个点，原因待查
- 后续：长序列、多卡场景

#focus-slide[复用键张量，保持输出，降低延迟。感谢各位老师指正。]

#show: appendix
= 备份
== 备份：实验设置与完整结果
硬件、随机种子、完整结果表放在这里，用于回答提问。
