#!/usr/bin/env python3
"""Regenerate each weekly deck and the public presentation index."""
import subprocess
import sys
from tools.weekly import ROOT, load_weeks, write_archive


def main():
    weeks = load_weeks(ROOT)
    for week in weeks:
        subprocess.run([sys.executable, str(week['directory'] / 'build_deck.py')],
                       cwd=week['directory'], check=True)
    write_archive(ROOT, weeks)
    print('Built weekly index and latest redirect.')


if __name__ == '__main__':
    main()
