#!/usr/bin/env python3
"""Chinese prose word-preference table for the DeAI checker.

Rule shape: regex -> replacement. A replacement of None means the word must be
avoided and the clause rewritten as concrete action, state, or detail; a
string is the mandated replacement when the source semantics allow it.

The table is authoritative. deai_check.py reports hits; the reviewer decides
whether a replacement fits the sentence.
"""

from __future__ import annotations

import re

WORD_REPLACEMENTS: dict[str, str] = {
    r"脊背": "后背/背部",
    r"深入骨髓": "些许/轻微",
    r"乐了": "笑了笑",
    r"降维打击": "大获全胜",
    r"亚空间": "混沌",
    # 规范译名优先：门限是 threshold 的旧式直译，学科通用译名为阈值。
    r"门限": "阈值",
}

WORD_AVOID: dict[str, None] = {
    r"长长地呼出一口气": None,
    r"抽干全身力气": None,
    r"血色尽褪": None,
    r"(?:血压|上涌)": None,
    r"(?:滚烫|滚热|发烫|热辣辣|火辣辣)": None,
    r"(?:热|烫)(?=得)": None,
    r"燃烧": None,
    r"一道惊雷": None,
    r"[\"“]?轰[\"”]?地一(?:下|声)": None,
    r"像(?:是)?一(?:根|条|枚)?[^，。！？；]{0,6}针": None,
    r"像(?:是)?一(?:把|柄)?[^，。！？；]{0,6}刀": None,
    r"(?:石子|石头|湖面|涟漪)": None,
    r"(?:爆发|爆炸|炸开)": None,
    r"(?:猛地|瞬间)": None,
    r"(?:无力感|疲惫感)": None,
    r"(?:倦意|无力|脱力|疲惫|虚弱|虚脱)": None,
    r"(?:麻木|绝望|灭顶|面无表情)": None,
    r"(?:过度|强烈|剧烈|极度|深深)": None,
    r"(?:震惊|惊慌)": None,
    r"(?:激动|紧张|紧绷|绷紧|突然|死死地)": None,
    r"(?:自我厌弃|自暴自弃|破罐子破摔)": None,
    r"(?:残酷|残忍|冷酷)": None,
    r"(?:生气|愤怒|羞愤|怒吼|咆哮|吼叫|吼)": None,
    r"(?:睫毛|紧闭|滴出血来)": None,
    r"(?:锁骨|尾椎骨|喉结|骨节分明|修长)": None,
    r"(?:握拳|握紧|攥紧|攥住)": None,
    r"(?:指尖|指节)": None,
    r"(?:们|我|你|他|她|它)的手": None,
    r"(?:牙缝|紧咬|咬着)": None,
    r"牙酸": None,
    r"(?:狂热|信徒|仪式|献祭|祭品|宗教|信仰)": None,
    r"机械(?:式|地)?": None,
    r"(?:冰冷|冰凉|手术刀|解剖)": None,
    r"(?:荒唐|荒诞|荒谬)": None,
    r"不易察觉": None,
    r"(?:展品|雕塑)": None,
    r"精密": None,
    r"仪器": None,
    r"(?:颤抖|颤音)": None,
    r"(?:直冲|直窜)": None,
    r"(?:冷静|审视|审判)": None,
    r"(?:打圈|打转|打着圈|打着转)": None,
    r"(?:如释重负|如蒙大赦)": None,
    r"(?:前所未有|前所未来|难以言喻|潮水|淹没|席卷)": None,
    r"(?:狡黠|挤了挤眼睛|眨了眨眼)": None,
    r"教具": None,
    r"通红": None,
    r"(?:冒充|假冒|假扮)": None,
    r"(?:当做|当作|当成)": None,
    # 技术黑话：英文动词的直译和 AI 生成文本的口头禅。
    # 改写为常规动词或直接陈述系统行为（见 CHINESE_PROSE.md §4）。
    r"洗成": None,
    r"塞进": None,
    r"吸到": None,
    r"凑足": None,
    r"(?:偷偷|悄悄)": None,
    # 只命中「隐瞒式修改」搭配；「静默安装」等规范 IT 术语不在表中。
    r"静默(?=更改|变更|替换|覆盖|删除|忽略|篡改|修改)": None,
    r"有预算的": None,
    # 情绪直译：以身体感觉或「接住」框架代替情感动作，是 AI 情感文的口头禅。
    # 「接住球」等物理动作不在表中。
    r"烧心": None,
    r"接住[^，。！？；]{0,6}情绪": None,
    r"(?:情绪|委屈|心事|眼泪)[^，。！？；]{0,3}被接住": None,
    # held-out 没有规范中文译名；留出数据/留出集是直译，直接使用 held-out。
    # 只命中数据类搭配，「留出一个小时」不在表中。
    r"留出(?:数据集|数据|集|样本)": None,
    # 禁令式开头（CHINESE_PROSE.md §1）。只命中句首，句中的禁止词不报。
    # 用词边界挡住「不要紧」这类固定词组。
    r"(?:^|[。！？；\n])\s*(?:(?:不能|不得|禁止|不应|不允许|不可)(?!要)|不要(?!紧))": None,
    # 平衡句式（§2）不在这里：它和「一方面……另一方面」同属比较结构，
    # 放在 deai_check.py 的 ZH_COMPARISON_STRUCTURE 里。
    # 正文里的免责说明（§3）。起草时的「不要写 X」漏进了交付物。
    r"(?:本文|我们)不(?:讨论|涉及|处理|保证)": None,
    r"我们不会(?:在本文中)?(?:讨论|处理|涉及)": None,
    r"本文不保证": None,
}

WORD_RULES: list[tuple[str, str | None]] = [
    *WORD_REPLACEMENTS.items(),
    *WORD_AVOID.items(),
]


def replacement_patterns() -> dict[str, str]:
    return {pattern: "swap_word" for pattern in WORD_REPLACEMENTS}


def avoid_patterns() -> dict[str, str]:
    return {pattern: "avoid_word" for pattern in WORD_AVOID}


def find_rule(matched: str) -> tuple[str, str | None] | None:
    """Return the rule that produced `matched`, first match in table order."""
    for pattern, replacement in WORD_RULES:
        if re.search(pattern, matched):
            return pattern, replacement
    return None
