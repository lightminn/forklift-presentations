"""Extract the level changes of the three DSLogic captures of the remote.

    python prepare_la.py DSLogic_Front_Back.csv DSLogic_UB.csv DSLogic_LR.csv

Each CSV is a libsigrok export (1 MHz, two channels). Only the samples where
either channel changes are kept, so the slides can draw the traces from a few
dozen points. Writes assets/data_la_edges.json. Standard library only.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = {'Front_Back': 'drive', 'UB': 'lift', 'LR': 'steer'}


def edges(path):
    out, last, t = [], None, None
    rate = None
    with open(path, newline='') as f:
        for row in csv.reader(f):
            if not row:
                continue
            if row[0].startswith(';'):
                if 'Sample rate' in row[0]:
                    rate = row[0].split(':', 1)[1].strip()
                continue
            if row[0].startswith('Time'):
                continue
            t, v = float(row[0]), (int(row[1]), int(row[2]))
            if v != last:
                out.append([round(t, 6), *v])
                last = v
    return {'rate': rate, 'start_s': out[0][0], 'end_s': t, 'edges': out}


if __name__ == '__main__':
    given = {next((v for k, v in NAMES.items() if f'_{k}.' in Path(a).name), None): a for a in sys.argv[1:]}
    if set(given) != set(NAMES.values()):
        sys.exit('pass all three captures (Front_Back, UB, LR); the JSON is rewritten as a whole')
    data = {}
    for arg in given.values():
        key = next(v for k, v in NAMES.items() if f'_{k}.' in Path(arg).name)
        data[key] = edges(arg)
        print(key, len(data[key]['edges']), 'edges', data[key]['start_s'], '→', data[key]['end_s'])
    (HERE / 'assets/data_la_edges.json').write_text(json.dumps(data, separators=(',', ':')) + '\n')
