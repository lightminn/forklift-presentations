"""Cut the week 8 figures from operator-console screenshots and the adapter preview (PIL only).

    /home/light/anaconda3/bin/python prepare_figures.py <shots_dir> <adapter_preview.png> [out_dir]

shots_dir holds headless-Chromium screenshots of the console (console/web on
the robot repository's main): c3_* and c2a-* were taken on the Isaac live
runner and the observation-only gateway (console sessions, 2026-10-15/17);
the others on the fake vehicle (console.mock_vehicle, 2026-10-20) and are
placeholders until the Isaac recordings exist (VALIDATION.md). Viewports are
1600 x 900 CSS px except the phone (400 x 860) and c3b_transport (1018 x 880).
Nothing is redrawn; each figure is a plain crop.
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent

# out name: (source, (left, top, right, bottom)) in screenshot pixels; None = whole image
CROPS = {
    'a01_watch.png': ('c3_live_auto.png', (200, 130, 1260, 890)),
    'a01_order.png': ('03_wizard3.png', (490, 258, 1112, 642)),
    'a01_drive.png': ('22_teleop_drive.png', (1262, 136, 1600, 620)),
    'a03_layout.png': ('c3_live_auto.png', None),
    'a03_phone.png': ('30_phone.png', None),
    'a04_step1.png': ('01_wizard1.png', (490, 258, 1112, 642)),
    'a04_step2.png': ('02b_wizard2.png', (490, 238, 1112, 662)),
    'a04_step3.png': ('03_wizard3.png', (490, 258, 1112, 642)),
    'a05_slam.png': ('c2a-isaac-live-2.png', (580, 186, 1040, 810)),
    'a05_path.png': ('10_run_3s.png', (230, 140, 1230, 600)),
    'a06_cam.png': ('c3_live_auto.png', (208, 600, 568, 888)),
    'a06_state.png': ('c3b_transport.png', (700, 345, 1002, 585)),
    'a07_teleop.png': ('22_teleop_drive.png', (196, 96, 1600, 900)),
    'a08_results.png': ('11_done.png', (1262, 600, 1600, 900)),
}


def main():
    shots, preview = Path(sys.argv[1]), Path(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / 'assets'
    out.mkdir(exist_ok=True)
    for name, (src, box) in CROPS.items():
        img = Image.open(shots / src).convert('RGB')
        (img.crop(box) if box else img).save(out / name, optimize=True)
    # adapter preview (2100 x 1200): the 3D model and the dimensioned section, without its own title
    p = Image.open(preview).convert('RGB')
    p.crop((300, 330, 860, 800)).save(out / 'a09_model.png', optimize=True)
    p.crop((1200, 330, 2000, 880)).save(out / 'a09_section.png', optimize=True)
    print(f'wrote {len(CROPS) + 2} figures to {out}')


if __name__ == '__main__':
    main()
