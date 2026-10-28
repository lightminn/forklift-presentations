"""Make week 9's figures in assets/ from the team's main-board pictures, the photos of the first encoder
magnet mount print and console captures (conda base Python: PIL).

    python prepare_figures.py <board pictures folder> <mount photos folder> <captures folder>

The board pictures are the eight KakaoTalk_20261028_03*.png the user sent on 2026-10-28; only the top-side
3D render and the top-side layout are used (the bottom side carries the designer's silkscreen, which the
deck does not show -- user, 2026-10-28). The captures are the fake vehicle's console (w9_*.png, SOURCES.md). The sources are not kept in this repository.
Every output is re-encoded, so no metadata is carried over.
"""
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'assets'

BOARD_3D_TOP = 'KakaoTalk_20261028_034637093.png'
BOARD_LAYOUT_TOP = 'KakaoTalk_20261028_034718769.png'


def save(im, name, quality=90):
    im = im.convert('RGB')
    if name.endswith('.png'):
        im.save(OUT / name, optimize=True)
    else:
        im.save(OUT / name, quality=quality, optimize=True)
    print(name, im.size)


def main(board, preview, caps):  # preview: the mount photos folder
    board, caps = Path(board), Path(caps)
    # the main board, top side: the render on black, cropped to the board with a small margin
    im = Image.open(board / BOARD_3D_TOP)
    save(im.crop((60, 90, 1580, 1336)), 'h02_board_top.jpg')
    # the top layout with its outline dimensions (114.173 x 91.567 mm, headers 33.0 mm apart)
    im = Image.open(board / BOARD_LAYOUT_TOP).convert('RGB').crop((100, 40, 1580, 1365))
    # the bottom silkscreen (board name and designer) shows through faintly near C70-C72: median-filter it out
    box = (880, 1118, 1165, 1218)
    im.paste(im.crop(box).filter(ImageFilter.MedianFilter(9)), box[:2])
    save(im, 'h03_layout_top.jpg')
    # the first mount print (2026-10-26 phone photos, 3000 x 4000): the parts on the desk, and one on the motor shaft
    prints = Path(preview)
    im = ImageOps.exif_transpose(Image.open(prints / '20261026_145724.jpg'))  # the phone stores it rotated
    save(im.crop((620, 1080, 2340, 2700)).resize((860, 810)), 'h05_print.jpg', 86)
    im = ImageOps.exif_transpose(Image.open(prints / '20261026_145743.jpg'))
    save(im.crop((500, 1380, 1960, 2840)).resize((810, 810)), 'h05_mounted.jpg', 86)
    # console captures (1600 x 900 CSS px): the queue panel, the status page, the results summary
    q = Image.open(caps / 'w9_c5.png')
    save(q.crop((1262, 330, 1590, 900)), 'c07_queue.png')
    s = Image.open(caps / 'w9_health.png')
    save(s.crop((205, 105, 990, 845)), 'c07_health.png')
    r = Image.open(caps / 'w9_summary.png')
    save(r.crop((1262, 255, 1590, 885)), 'c07_summary.png')
    # the Isaac clip of slide 8 (n08_aisle_stall.mp4) is cut on ws1 with ffmpeg, see README.md


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
