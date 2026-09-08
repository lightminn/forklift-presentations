#!/usr/bin/env python3
"""Package the web deck for GitHub Pages without publishing repository tooling."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = ('index.html', 'deck.css', 'support.js', 'deck-stage.js')


def build_site(output):
    output = output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise SystemExit(f'output directory is not empty: {output}')
    # Validate inputs before creating a partial publication directory.
    for name in (*RUNTIME_FILES, 'assets', 'vendor'):
        if not (ROOT / name).exists():
            raise SystemExit(f'missing publication input: {name}')
    output.mkdir(parents=True, exist_ok=True)
    for name in RUNTIME_FILES:
        shutil.copy2(ROOT / name, output / name)
    for name in ('assets', 'vendor'):
        shutil.copytree(
            ROOT / name, output / name,
            ignore=shutil.ignore_patterns('*.md', '*.py', '*.sh', '*.zip', '*.json'),
        )
    (output / '.nojekyll').touch()
    print(f'Built {sum(p.is_file() for p in output.rglob("*"))} files in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    build_site(parser.parse_args().output)
