"""Week 11 slide 05 media from rc_95e61a74/rc_G_aisle_rack_s11 (Isaac top view + its plan_history.json).

The Isaac overlay draws every return path in one colour, so the plan the truck had (planned 204.7 s) and the one it
made at the gear-change point (221.1 s) are drawn here again in two colours: the old plan from the cusp before the
stop on (orange), the new plan (cyan); after the replan the old one is faded. World -> pixel for the drawn path lines
was fitted to the Isaac path pixels of a frame (top view: u = 576 - 76 (y - ye), v = 368 - 76 (x - xe)).

    python make_replan.py VIDEO PLAN_HISTORY OUTDIR
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

VIDEO, PH, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1280, 720
E = (1.9057142857142855, -8.952142857142858)
S, CX, CY = 76.0, 576.0, 368.0
T_REPLAN = 221.108
OLD_C, NEW_C = (255, 150, 40), (40, 220, 245)
FONT = ImageFont.truetype("/usr/share/fonts/TTF/Pretendard-Bold.ttf", 30)

ph = json.load(open(PH))
ret = [p for p in ph["plans"] if p["phase"] == "return_home"]
old = np.array(ret[0]["poses"])[40:]   # from the cusp before the stop (the reverse leg it was on) to the end
new = np.array(ret[1]["poses"])


def px(a):
    return [(CX - S * (y - E[1]), CY - S * (x - E[0])) for x, y in a]


def overlay(im, t):
    base = im.convert("RGBA")
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if t < T_REPLAN:
        d.line(px(old), fill=OLD_C + (255,), width=4, joint="curve")
    else:
        d.line(px(old), fill=OLD_C + (110,), width=4, joint="curve")
        d.line(px(new), fill=NEW_C + (255,), width=4, joint="curve")
    return Image.alpha_composite(base, lay).convert("RGB")


def frames(t0, t1):
    """(time, PIL frame) every source frame (60 fps) between t0 and t1."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", VIDEO, "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k = 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        yield t0 + k / 60.0, Image.frombytes("RGB", (W, H), buf)
        k += 1
    p.wait()


def badge(im, n):
    d = ImageDraw.Draw(im)
    d.ellipse((8, 8, 52, 52), fill=(47, 116, 192), outline=(255, 255, 255), width=3)
    d.text((30, 29), str(n), font=FONT, fill=(255, 255, 255), anchor="mm")
    return im


# the zoomed clip: 4x until the arrival, real speed over arrival - stop - replan - departure, 4x after
ZOOM = (560, 220, 1040, 490)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "960x540", "-r", "30",
                        "-i", "-", "-an", "-c:v", "libx264", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        str(OUT / "t05_replan.mp4")], stdin=subprocess.PIPE)
keys = {218.60: 1, 221.00: 2, 221.45: 3, 223.00: 4}
got = {}
n = 0
for t, im in frames(200.0, 236.0):
    step = 2 if 219.0 <= t < 224.0 else 8   # 60 fps source -> 30 fps out: every 2nd = 1x, every 8th = 4x
    for kt, kn in keys.items():
        if kn not in got and t >= kt:
            got[kn] = overlay(im, t)
    if n % step == 0:
        enc.stdin.write(overlay(im, t).crop(ZOOM).resize((960, 540), Image.LANCZOS).tobytes())
    n += 1
enc.stdin.close()
enc.wait()
KEY = (640, 235, 960, 415)   # 320 x 180 around the gear-change point
for kn, im in got.items():
    badge(im.crop(KEY).resize((480, 270), Image.LANCZOS), kn).save(OUT / f"t05_key{kn}.jpg", quality=90)
# the whole scene at the replan, the zoomed area outlined
for t, im in frames(221.45, 221.5):
    full = overlay(im, t)
    d = ImageDraw.Draw(full)
    d.rectangle(ZOOM, outline=(255, 255, 255), width=4)
    full.crop((0, 150, 1280, 650)).save(OUT / "t05_overview.jpg", quality=88)
    break
first = next(iter(frames(212.0, 212.05)))
overlay(first[1], first[0]).crop(ZOOM).resize((960, 540)).save(OUT / "t05_replan_poster.jpg", quality=88)
print("done", sorted(got))
