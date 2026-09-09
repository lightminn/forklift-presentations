#!/usr/bin/env python3
"""Package the weekly index and published decks without repository tooling."""
import argparse
from pathlib import Path
import shutil
from weekly import ROOT, load_weeks, published_weeks, write_archive

RUNTIME_FILES = ('index.html', 'deck.css', 'support.js', 'deck-stage.js')


def build_site(output):
    output = output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise SystemExit(f'output directory is not empty: {output}')
    weeks = load_weeks(ROOT)
    published = published_weeks(weeks)
    for week in published:
        for name in (*RUNTIME_FILES, 'assets', 'vendor', 'slide-metadata.json'):
            if not (week['directory'] / name).exists():
                raise SystemExit(f'missing publication input: {week["path"]}{name}')
    if not (ROOT / 'archive.css').is_file():
        raise SystemExit('missing publication input: archive.css')
    output.mkdir(parents=True, exist_ok=True)
    write_archive(output, weeks)
    shutil.copy2(ROOT / 'archive.css', output / 'archive.css')
    for week in published:
        source = week['directory']
        target = output / source.name
        target.mkdir()
        for path in [source / 'index.html', *source.glob('*.css'), *source.glob('*.js')]:
            shutil.copy2(path, target / path.name)
        for name in ('assets', 'vendor'):
            shutil.copytree(source / name, target / name,
                            ignore=shutil.ignore_patterns('*.md', '*.py', '*.sh', '*.zip', '*.json'))
    (output / '.nojekyll').touch()
    print(f'Built {len(published)} published weeks; {sum(p.is_file() for p in output.rglob("*"))} files in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    build_site(parser.parse_args().output)
