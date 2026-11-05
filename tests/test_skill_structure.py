import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(ROOT.glob('*/*/SKILL.md'))
LINK = re.compile(r'\]\((?!https?://|#|mailto:)([\w./-]+?\.\w+|[\w./-]+/)(?:#[^)]*)?\)')


class SkillStructure(unittest.TestCase):
    def test_finds_skills(self):
        self.assertGreaterEqual(len(SKILLS), 29)

    def test_frontmatter_matches_folder(self):
        for path in SKILLS:
            text = path.read_text(encoding='utf-8')
            head = re.match(r'---\n(.*?)\n---\n', text, re.S)
            self.assertIsNotNone(head, path)
            name = re.search(r'^name: (.+)$', head[1], re.M)
            desc = re.search(r'^description: (.+)$', head[1], re.M)
            self.assertEqual(name[1].strip(), path.parent.name)
            self.assertLessEqual(len(desc[1].strip('"')), 1024, path)

    def test_body_stays_under_limit(self):
        for path in SKILLS:
            self.assertLessEqual(path.read_text(encoding='utf-8').count('\n'), 500, path)

    def test_relative_links_resolve(self):
        for path in SKILLS:
            for doc in [path, *path.parent.glob('references/*.md')]:
                for target in LINK.findall(doc.read_text(encoding='utf-8')):
                    self.assertTrue((doc.parent / target).exists(), f'{doc}: {target}')

    def test_references_are_one_level_deep(self):
        for path in SKILLS:
            body = path.read_text(encoding='utf-8')
            for doc in path.parent.glob('references/*.md'):
                self.assertIn(f'references/{doc.name}', body, f'{doc} is not reachable from SKILL.md')
                for target in LINK.findall(doc.read_text(encoding='utf-8')):
                    if target.endswith('.md'):
                        self.assertIn('assets/', target, f'{doc} chains to {target}')

    def test_frontmatter_metadata(self):
        for path in SKILLS:
            head = path.read_text(encoding='utf-8').split('---\n')[1]
            self.assertIn('license: MIT', head, path)
            self.assertIn('metadata:', head, path)
            self.assertNotRegex(head, r'(?m)^version:', path)

    def test_side_effect_skills_are_user_invoked(self):
        for name in ('coding/co-commit', 'coding/counterweight-setup', 'agents/orchestrate'):
            head = (ROOT / name / 'SKILL.md').read_text(encoding='utf-8').split('---\n')[1]
            self.assertIn('disable-model-invocation: true', head)

    def test_no_undefined_skill_dir(self):
        for path in SKILLS:
            self.assertNotIn('$SKILL_DIR', path.read_text(encoding='utf-8'), path)


if __name__ == '__main__':
    unittest.main()
