"""Publication contracts: all assets, Pages subpaths, and output preservation."""
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urljoin, urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.sections = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.sections.append(attrs)
        self.urls.extend(attrs[k] for k in ('src', 'href', 'from') if attrs.get(k))


class PublicationTests(unittest.TestCase):
    def run_builder(self, output):
        return subprocess.run(
            [sys.executable, str(ROOT / 'tools/build_site.py'), '--output', str(output)],
            capture_output=True, text=True,
        )

    def test_bundle_resolves_all_deck_assets_under_repository_prefix(self):
        with tempfile.TemporaryDirectory() as temp:
            site = Path(temp) / 'site'
            result = self.run_builder(site)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((site / 'week-02/index.html').is_file(), 'Week 2 needs a permanent URL')
            parser = References()
            parser.feed((site / 'week-02/index.html').read_text())
            self.assertEqual(len(parser.sections), 13)
            self.assertEqual(sum(int(s['data-duration']) for s in parser.sections), 645)
            base = 'https://example.github.io/forklift-presentations/'
            references = []
            for html in site.rglob('*.html'):
                page = References()
                page.feed(html.read_text())
                page_url = urljoin(base, html.relative_to(site).as_posix())
                references.extend((page_url, url) for url in page.urls)
            for css in site.rglob('*.css'):
                css_url = urljoin(base, css.relative_to(site).as_posix())
                references.extend((css_url, u) for u in re.findall(r'url\([\"\']?([^\)\"\']+)', css.read_text()))
            for page, ref in references:
                if ref.startswith(('http:', 'https:', 'data:', '#')):
                    continue
                resolved = urlsplit(urljoin(page, ref)).path
                self.assertTrue(resolved.startswith('/forklift-presentations/'), resolved)
                relative = unquote(resolved.removeprefix('/forklift-presentations/'))
                target = site / relative
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), ref)
            self.assertTrue((site / '.nojekyll').is_file())
            self.assertFalse((site / 'build_deck.py').exists())
            self.assertFalse((site / '.github').exists())
            self.assertFalse((site / 'tests').exists())
            self.assertFalse((site / 'week-02/build_deck.py').exists())
            self.assertFalse((site / 'week-02/week.json').exists())

    def test_nonempty_destination_is_preserved_and_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            sentinel = output / 'existing.txt'
            sentinel.write_text('keep this')
            result = self.run_builder(output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('not empty', result.stderr)
            self.assertEqual(sentinel.read_text(), 'keep this')
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_repository_cannot_be_used_as_output(self):
        source = (ROOT / 'index.html').read_bytes()
        result = self.run_builder(ROOT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not empty', result.stderr)
        self.assertEqual((ROOT / 'index.html').read_bytes(), source)


if __name__ == '__main__':
    unittest.main()
