"""Weekly publishing must preserve past decks and exclude unfinished copies."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def snapshot(root):
    return {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


class WeeklyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        def ignore(directory, names):
            excluded = {'.git', '_site', '__pycache__', 'tests', 'docs'}
            if Path(directory) == ROOT:
                excluded.update(name for name in names if name.startswith('week-') and name != 'week-02')
            return set(names) & excluded
        shutil.copytree(ROOT, self.root, ignore=ignore)

    def run_tool(self, *args):
        return subprocess.run([sys.executable, *args], cwd=self.root,
                              capture_output=True, text=True)

    def create_week(self, number):
        result = self.run_tool('tools/new_week.py', str(number), '--from', '2',
                               '--title', f'{number}주차 수행 내용')
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.root / f'week-{number:02d}'

    def test_new_week_is_an_independent_unpublished_copy(self):
        original = snapshot(self.root)
        week = self.create_week(3)
        info = json.loads((week / 'week.json').read_text())
        self.assertEqual(info['week'], 3)
        self.assertEqual(info['status'], 'draft')
        self.assertEqual(info['title'], '3주차 수행 내용')
        self.assertIn('미검증', (week / 'VALIDATION.md').read_text())
        self.assertTrue((week / 'index.html').is_file())
        (week / 'deck.css').write_text('/* independent edit */')
        self.assertEqual(snapshot(self.root / 'week-02'),
                         {p.removeprefix('week-02/'): h for p, h in original.items()
                          if p.startswith('week-02/')})
        result = self.run_tool('tools/build_site.py', '--output', '_site')
        self.assertEqual(result.returncode, 0, result.stderr)
        site = self.root / '_site'
        self.assertFalse((site / 'week-03').exists())
        self.assertNotIn('week-03/', (site / 'index.html').read_text())
        self.assertIn('../week-02/', (site / 'latest/index.html').read_text())

    def test_existing_week_cannot_be_overwritten(self):
        original = snapshot(self.root)
        result = self.run_tool('tools/new_week.py', '2', '--title', '덮어쓰기')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('already exists', result.stderr)
        self.assertEqual(snapshot(self.root), original)

    def test_default_source_uses_latest_published_week_and_skips_drafts(self):
        draft = self.create_week(3)
        (draft / 'deck.css').write_text('/* unfinished draft */')
        result = self.run_tool('tools/new_week.py', '4')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'week-04/deck.css').read_bytes(),
                         (self.root / 'week-02/deck.css').read_bytes())
        self.assertEqual(json.loads((self.root / 'week-04/week.json').read_text())['status'], 'draft')

    def test_publishing_new_week_updates_index_and_latest_without_changing_week2(self):
        original = snapshot(self.root / 'week-02')
        week = self.create_week(10)
        metadata = week / 'week.json'
        info = json.loads(metadata.read_text())
        info.update(status='published', title='경로 추종 <검증>', summary='시험 조건 & 결과')
        metadata.write_text(json.dumps(info, ensure_ascii=False))
        result = self.run_tool('build_deck.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_tool('tools/build_site.py', '--output', '_site')
        self.assertEqual(result.returncode, 0, result.stderr)
        site = self.root / '_site'
        html = (site / 'index.html').read_text()
        self.assertLess(html.index('data-week="10"'), html.index('data-week="2"'))
        self.assertIn('경로 추종 &lt;검증&gt;', html)
        self.assertIn('시험 조건 &amp; 결과', html)
        self.assertIn('../week-10/', (site / 'latest/index.html').read_text())
        self.assertTrue((site / 'week-02/index.html').is_file())
        self.assertTrue((site / 'week-10/index.html').is_file())
        self.assertEqual(snapshot(self.root / 'week-02'), original)

    def test_invalid_week_numbers_do_not_write_files(self):
        original = snapshot(self.root)
        for number in ('0', '-1', '100', '../week-03', 'abc'):
            result = self.run_tool('tools/new_week.py', number)
            self.assertNotEqual(result.returncode, 0)
        self.assertEqual(snapshot(self.root), original)

    def test_invalid_status_blocks_publication_before_output_is_created(self):
        week = self.create_week(3)
        metadata = week / 'week.json'
        info = json.loads(metadata.read_text())
        info['status'] = 'publshed'
        metadata.write_text(json.dumps(info))
        result = self.run_tool('tools/build_site.py', '--output', '_site')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('status', result.stderr)
        self.assertFalse((self.root / '_site').exists())


if __name__ == '__main__':
    unittest.main()
