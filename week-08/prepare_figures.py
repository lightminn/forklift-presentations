"""Cut the week 8 figures from operator-console screenshots and the adapter preview (PIL only).

    /home/light/anaconda3/bin/python prepare_figures.py <shots_dir> <scenario.pdf> [out_dir]

shots_dir holds headless-Chromium screenshots of the console (console/web on
the robot repository's main): c3_* and c2a-* were taken on the Isaac live
runner and the observation-only gateway (console sessions, 2026-10-15/17);
the others on the fake vehicle (console.mock_vehicle, 2026-10-20) and are
placeholders until the Isaac recordings exist (VALIDATION.md). Viewports are
1600 x 900 CSS px except the phone (400 x 860) and c3b_transport (1018 x 880);
the fake-vehicle shots were retaken at device scale 2 (phone 3) on 2026-10-20,
so crop boxes are in CSS px and scaled by each image's width over its viewport.
scenario.pdf is Riibotics' demo scenario deck (2026-10-19, the resend with the
environment numbers); pdftoppm renders it at 200 dpi and the figure part of
pages 2-7 is cut out (boxes measured at the dpi noted beside each).
Nothing is redrawn; each figure is a plain crop.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent

# out name: (source, (left, top, right, bottom)) in screenshot pixels; None = whole image
# The console screenshots (a01_* · a03_* · a04_* · a07_*) are no longer on the slides: slides 1 and 3-5 show
# recordings of the console on the fake vehicle instead (assets/v0*.mp4, README.md, user 2026-10-21).
CROPS = {}
# scenario figures: page -> (out name, dpi the box was measured at, box)
# 3-7 (the scenario drawings) are no longer on the slides: slide 6 shows CPU planning animations of the
# same layouts (tools/riibotics_cpu_video.py in the robot repository, user 2026-10-20).
SCENARIO = {2: ('s02_truck.png', 70, (110, 140, 385, 392))}
CSS_WIDTH = {'30_phone.png': 400, 'c3b_transport.png': 1018}   # everything else 1600


def main():
    shots, pdf = Path(sys.argv[1]), Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / 'assets'
    out.mkdir(exist_ok=True)
    for name, (src, box) in CROPS.items():
        img = Image.open(shots / src).convert('RGB')
        k = img.width / CSS_WIDTH.get(src, 1600)
        (img.crop(tuple(round(v * k) for v in box)) if box else img).save(out / name, optimize=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdftoppm', '-r', '200', '-png', str(pdf), f'{tmp}/p'], check=True)
        for page, (name, dpi, box) in SCENARIO.items():
            img = Image.open(f'{tmp}/p-{page}.png').convert('RGB')
            k = 200 / dpi
            b = [round(v * k) for v in box]
            img.crop((b[0], b[1], min(b[2], img.width), min(b[3], img.height))).save(out / name, optimize=True)
    print(f'wrote {len(CROPS) + len(SCENARIO)} figures to {out}')


if __name__ == '__main__':
    main()
