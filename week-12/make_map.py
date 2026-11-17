"""Week 12 slide 04: the B-P2d survey map (hall_s5b_G0, map 3edf24b0) with the start-relocalization outcome of
each start of the reloc-observe-move batch drawn on it. Usage: python -I make_map.py GRID_NPZ VAL_S5_JSON COMPARE_JSON OUT_PNG"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw

grid_p, val_p, cmp_p, out_p = sys.argv[1:5]
g = np.load(grid_p, allow_pickle=False)
data, origin, res = g['data'], g['origin'], float(g['resolution_m'])
H, W = data.shape
img = np.full((H, W, 3), 205, np.uint8)          # unknown
img[data == 0] = (250, 250, 250)                  # free
occ = data >= 50
img[occ] = (40, 48, 58)                           # occupied
img = img[::-1]                                   # row 0 = top = max y
poses = {p['id']: p['base'] for p in json.load(open(val_p))['poses']}
cmp = json.load(open(cmp_p))
pairs = cmp['pairs']
NO_RELOC = set(cmp.get('no_reloc') or [])
S = 1                                             # pixels per cell in the output
im = Image.fromarray(img).resize((W * S, H * S), Image.NEAREST)
d = ImageDraw.Draw(im)
COL = {'static': (34, 160, 80), 'moved': (47, 116, 192), 'fail': (214, 69, 65)}
counts = {k: 0 for k in COL}
fails = []
skipped = []
for p in pairs:
    x, y, _ = poses[p['id']]
    if p['id'] in NO_RELOC:
        skipped.append(p['id'])
        continue
    if p['a_success']:
        k = 'static'
    elif p['b_success']:
        k = 'moved'
    else:
        k = 'fail'
    counts[k] += 1
    c = (x - origin[0]) / res * S
    r = (H - 1 - (y - origin[1]) / res) * S
    if k == 'fail':
        fails.append((x, y))
    rad = 12
    d.ellipse([c - rad, r - rad, c + rad, r + rad], fill=COL[k], outline=(255, 255, 255), width=2)
print('counts', counts, 'pairs', len(pairs), 'skipped (no relocalization record)', skipped)
fx = [f[0] for f in fails]; fy = [f[1] for f in fails]
print('fail x range %.1f..%.1f  y range %.1f..%.1f' % (min(fx), max(fx), min(fy), max(fy)))
print('map x %.1f..%.1f  y %.1f..%.1f' % (origin[0], origin[0] + W * res, origin[1], origin[1] + H * res))
# 5 m scale bar, bottom left inside the hall
from PIL import ImageFont
f = ImageFont.truetype('/usr/share/fonts/noto-cjk/NotoSansCJK-Medium.ttc', 22, index=1)
x0, y0 = 30, H * S - 28
L = 5.0 / res * S
d.rectangle([x0, y0, x0 + L, y0 + 6], fill=(40, 48, 58))
d.text((x0 + L + 10, y0 - 12), '5 m', font=f, fill=(40, 48, 58))
CROP_TOP = 110                                    # rows above the hall: unobserved area and LiDAR rays through the doors
im = im.crop((0, CROP_TOP * S, W * S, H * S))
im.save(out_p)
