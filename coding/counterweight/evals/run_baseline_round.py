#!/usr/bin/env python3
"""Instruction-overhead and fixture-oracle round. Not a model eval."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
PKG = ROOT.parent
YAGNI = "YAGNI. Do not over-engineer. Keep changes minimal."


def words(path: Path) -> int:
    return len(path.read_text().split())


def main() -> None:
    skill = words(PKG / "SKILL.md")
    yagni = len(YAGNI.split())
    fixtures = sorted(p.name for p in (ROOT / "fixtures").iterdir() if p.is_dir())
    print(f"yagni_words={yagni}")
    print(f"skill_words={skill}")
    print(f"instruction_word_delta={skill - yagni}")
    print(f"fixtures={len(fixtures)}")
    for name in fixtures:
        print(f"  {name}")
    print("round=oracle")
    print("live_model_trials=0")


if __name__ == "__main__":
    main()
