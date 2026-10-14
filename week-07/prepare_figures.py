"""Make the week 7 hardware figures from the team's EasyEDA exports (PIL only).

    /home/light/anaconda3/bin/python prepare_figures.py <source_dir> [out_dir]

source_dir holds the files the team sent on 2026-10-14: mainboard_1.png
(Motor Board schematic, page 1 of 3 "MOTOR&SENSOR"), mt6701_{1,2,3}.png
(MT_DS V1.0.0: 3D top, 3D bottom, schematic), kth7801_{1,2,3}.png (KTH_Enc
V1.1.2: 3D top, 3D bottom, schematic), stds_{1,2,3}.png (STDS V1.0.0:
schematic, 3D top, 3D bottom). 3D renders keep the board and lose the black
margin (and the editor's tab bar); schematics are cropped to the drawn part;
the main schematic is also cut into its blocks. Nothing is redrawn.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent


def trim_render(img, pad=24, ui_top=0, ui_right=0, ui_left=0):
    a = np.asarray(img.convert('RGB')).astype(int)
    h, w, _ = a.shape
    mask = a.max(axis=2) > 45
    mask[:ui_top] = False
    mask[:, :ui_left] = False
    if ui_right:
        mask[:, w - ui_right:] = False
    # rows that are one thin light line across the whole canvas (a viewer artefact) are not board
    sat = a.max(axis=2) - a.min(axis=2)
    light = (a.min(axis=2) > 150) & (sat < 30)
    full = light.mean(axis=1) > 0.9
    a2 = a.copy()
    for y in np.where(full)[0]:
        src = y - 2 if y >= 2 else y + 2
        a2[y] = a2[src]
        mask[y] = mask[src]
    ys, xs = np.where(mask)
    box = (max(xs.min() - pad, ui_left), max(ys.min() - pad, ui_top), min(xs.max() + pad, w - ui_right), min(ys.max() + pad, h))
    out = Image.fromarray(a2.astype('uint8')).crop(box)
    return out


def trim_sheet(img, pad=16):
    a = np.asarray(img.convert('RGB')).astype(int)
    # drawn parts: anything clearly darker or more saturated than the paper and its grid
    sat = a.max(axis=2) - a.min(axis=2)
    mask = (a.min(axis=2) < 170) | (sat > 70)
    ys, xs = np.where(mask)
    h, w = mask.shape
    return img.convert('RGB').crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, w), min(ys.max() + pad, h)))


def fit(img, width):
    if img.width <= width:
        return img
    return img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)


def main(src, out):
    out.mkdir(exist_ok=True)
    o = lambda n: out / n

    # 3D renders (black background); mt6701_1 still has the editor's tab bar and right edge
    renders = {'mt6701_1.png': ('80_mt_top.jpg', 90, 40, 30),
               'kth7801_1.png': ('81_kth_top.jpg', 0, 0),
               'stds_2.png': ('82_stds_top.jpg', 0, 0), 'stds_3.png': ('82_stds_bottom.jpg', 0, 0)}
    for name, (dst, top, right, *left) in renders.items():
        fit(trim_render(Image.open(src / name), ui_top=top, ui_right=right, ui_left=(left or [0])[0]), 1100).save(o(dst), quality=90)

    # schematics (paper background) -- PNG keeps the thin lines sharp
    for name, dst in (('mt6701_3.png', '80_mt_sch.png'), ('kth7801_3.png', '81_kth_sch.png'), ('stds_1.png', '82_stds_sch.png')):
        fit(trim_sheet(Image.open(src / name)), 1500).save(o(dst), optimize=True)

    main_sheet = Image.open(src / 'mainboard_1.png').convert('RGB')   # 2477 x 1770
    fit(main_sheet, 1800).save(o('83_main_sch.png'), optimize=True)
    # blocks of the main sheet (original pixel coordinates, read off the sheet)
    blocks = {'83_main_drv.png': (95, 100, 790, 460),      # L channel: DRV8244 U? with its parts
              '83_main_rj.png': (835, 1030, 1850, 1355)}   # RJ1/RJ2 (KTH7801 cables)
    for dst, box in blocks.items():
        fit(main_sheet.crop(box), 1400).save(o(dst), optimize=True)


if __name__ == '__main__':
    src = Path(sys.argv[1]).expanduser()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'assets'
    main(src, out)
