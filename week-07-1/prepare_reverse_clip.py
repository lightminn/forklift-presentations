#!/usr/bin/env python3
"""Cut the "후진을 고르는 이유" clip: the new-box scene from a fixed camera with the paths on the floor
(conda base: numpy, opencv, PIL; ffmpeg).

    python prepare_reverse_clip.py RUN_DIR

RUN_DIR is ws1 artifacts/20261012_meeting_chase/q67_seed_5_n1/run: the week 6 box run
(artifacts/20261005_p5_l3/l8_measured/seed_5_n1, snapshot p5_df109cf) again with its recorded
arguments plus a fixed view (--extra-views quarter, eye -2.0,-0.4,9.0, target 1.8,-0.4,0,
focal 2.2) -- meeting_quarter_w6.sbatch. It needs frames.jsonl, plan_history.json, result.json and
view_quarter.mp4 (1280 x 720, 30 fps).

The camera is the run's quarter camera (result.json extra_views.quarter; focal length x 10 mm on
the default 20.955 mm horizontal aperture, scene.usda /World/QuarterCamera), so a floor point is
projected with the pinhole model of that look-at pose. Drawn on the floor (z 1 cm), hidden where
the truck (with the pallet) or the box covers it:
- the transport plan the truck was following in yellow (the last live plan before the replan; the
  runner's own thin yellow line is the transport plan made before the pickup, within 10 cm of it
  at the stop and 5.5 cm of the box),
- at the replan, the band the loaded body sweeps on the tightest right turn from the stop
  (rear axle radius 1 / 0.29 m, inner side R - 0.40 m, outer front corner hypot(R + 0.40, 1.56) m),
- the replan's reverse run (orange) and forward run (blue), each shortened as the truck drives it.
Stage labels (a small tag in the top-left corner, caption(); colour meanings are the slide's legend, not
text in the clip) mark the clip's events; the clip ends when the rear axle is 1 m past the box. Driving plays at 2x, the replan frame is held 2.5 s, the last
frame 1.5 s -> assets/55_reverse_box.mp4 (cropped to 1080 x 720) and its poster (the held frame).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/noto-cjk/NotoSansCJK-Medium.ttc'
ACCENT, TAG_FILL = (127, 179, 240), (15, 18, 21, 215)   # the deck's caption-bar blue, dark tag
W, H, FPS = 1280, 720, 30
CROP = (120, 0, 1080, 720)                       # x, y, w, h: the panel's aspect, action kept
TRUCK = ((-0.51, 1.22), (-0.40, 0.40), (0.0, 1.05))   # base frame extent of truck + pallet (m)
REAR_AXLE_X = -0.34
YELLOW, ORANGE, BLUE, RED = (255, 196, 40), (240, 125, 30), (60, 145, 240), (225, 45, 35)


class Camera:
    def __init__(self, eye, target, focal):
        self.eye = np.asarray(eye, float)
        f = np.asarray(target, float) - self.eye
        self.f = f / np.linalg.norm(f)
        r = np.cross(self.f, [0.0, 0.0, 1.0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        self.fx = focal * 10 / 20.955 * W

    def project(self, pts):
        p = np.atleast_2d(np.asarray(pts, float)) - self.eye
        x, y, z = p @ self.r, p @ self.u, p @ self.f
        z = np.where(z > 1e-3, z, np.nan)
        return np.stack([W / 2 + self.fx * x / z, H / 2 - self.fx * y / z], 1), p @ self.f


def corners(x, y, yaw, xr, yr, zr):
    c, s = math.cos(yaw), math.sin(yaw)
    return np.array([(x + c * a - s * b, y + s * a + c * b, h) for a in xr for b in yr for h in zr])


def silhouettes(cam, pose, boxes):
    """Projected convex hulls with their nearest depth: the truck and the boxes standing on the floor."""
    shapes = [corners(pose[0], pose[1], pose[2], *TRUCK)]
    shapes += [corners(bx, by, byaw, (-sx / 2, sx / 2), (-sy / 2, sy / 2), (0.0, sz))
               for bx, by, byaw, sx, sy, sz in boxes]
    out = []
    for pts in shapes:
        uv, z = cam.project(pts)
        if np.isfinite(uv).all():
            out.append((cv2.convexHull(uv.astype(np.float32)), float(np.min(z))))
    return out


def draw_path(img, cam, hulls, poly, rgb, width):
    if len(poly) < 2:
        return
    pts = [np.asarray(poly[0], float)]
    for a, b in zip(poly, poly[1:]):
        a, b = np.asarray(a, float), np.asarray(b, float)
        n = max(1, int(math.ceil(np.linalg.norm(b - a) / 0.02)))
        pts += [a + (b - a) * k / n for k in range(1, n + 1)]
    pts = np.array(pts)
    uv, z = cam.project(np.column_stack([pts, np.full(len(pts), 0.01)]))
    keep = np.isfinite(uv).all(1)
    for hull, zmin in hulls:
        for i in np.nonzero(keep)[0]:
            if z[i] > zmin and cv2.pointPolygonTest(hull, (float(uv[i, 0]), float(uv[i, 1])), False) >= 0:
                keep[i] = False
    run = []
    for i in range(len(pts) + 1):
        if i < len(pts) and keep[i]:
            run.append(uv[i])
            continue
        if len(run) >= 2:
            cv2.polylines(img, [np.round(np.array(run) * 4).astype(np.int32)], False, rgb, width, cv2.LINE_AA, shift=2)
        run = []


def tint(img, cam, hulls, poly, rgb, alpha=0.42):
    """Tint a floor polygon except where a silhouette covers it, with a solid edge."""
    uv, _ = cam.project(np.column_stack([np.asarray(poly), np.full(len(poly), 0.01)]))
    if not np.isfinite(uv).all():
        return img
    hide = np.zeros(img.shape[:2], np.uint8)
    for hull, _ in hulls:
        cv2.fillConvexPoly(hide, np.round(hull.reshape(-1, 2)).astype(np.int32), 1)
    q = [np.round(uv * 4).astype(np.int32)]
    area = np.zeros(img.shape[:2], np.uint8)
    cv2.fillPoly(area, q, 1, cv2.LINE_AA, shift=2)
    edge = np.zeros_like(img)
    cv2.polylines(edge, q, True, rgb, 3, cv2.LINE_AA, shift=2)
    out = img.copy()
    m = (area > 0) & (hide == 0)
    out[m] = (out[m] * (1 - alpha) + np.array(rgb) * alpha).astype(np.uint8)
    e = edge.any(2) & (hide == 0)
    out[e] = edge[e]
    return out


def caption(img, text, size=32):
    """Stage label: a small dark tag in the top-left corner with a blue accent bar on its left."""
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil, 'RGBA')
    font = ImageFont.truetype(FONT, size)
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    x, y, bar, px, py = round(0.6 * size), round(0.5 * size), max(4, size // 7), round(0.45 * size), round(0.28 * size)
    d.rectangle([x, y, x + bar + 2 * px + (r - l), y + 2 * py + (b - t)], fill=TAG_FILL)
    d.rectangle([x, y, x + bar - 1, y + 2 * py + (b - t)], fill=(*ACCENT, 255))
    d.text((x + bar + px - l, y + py - t), text, font=font, fill=(255, 255, 255, 255))
    return np.asarray(pil)


def gear_runs(poses):
    """Split a planned rear-axle path at its cusps (the motion turns by more than 2 rad)."""
    pts = [tuple(p[:2]) for p in poses]
    runs, cur, prev = [], [pts[0]], None
    for a, b in zip(pts, pts[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-6:
            continue
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        if prev is not None and abs((ang - prev + math.pi) % (2 * math.pi) - math.pi) > 2.0:
            runs.append(cur)
            cur = [a]
        cur.append(b)
        prev = ang
    runs.append(cur)
    return runs


def length(pts):
    return float(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])))


def after(pts, s0):
    """The part of a polyline after arc length s0."""
    out, s = [], 0.0
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        if s + d >= s0:
            if not out:
                f = (s0 - s) / d if d > 0 else 0.0
                out.append((a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])))
            out.append(b)
        s += d
    return out


def main(run):
    run = Path(run)
    result = json.loads((run / 'result.json').read_text())
    view = result['extra_views']['quarter']
    cam = Camera(view['eye_m'], view['target_m'], view['focal_length_mm'])
    rows = [json.loads(line) for line in open(run / 'frames.jsonl')]
    t = np.array([r['simulation_time_s'] for r in rows])
    pose = []
    for r in rows:
        w, x, y, z = r['base_orientation_wxyz']
        pose.append((*r['base_position_m'][:2], math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))))
    pose = np.array(pose)
    rear = pose[:, :2] + REAR_AXLE_X * np.column_stack([np.cos(pose[:, 2]), np.sin(pose[:, 2])])
    travel = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(rear, axis=0), axis=1))])
    v = np.zeros(len(t))
    v[1:] = np.sum(np.diff(rear, axis=0) * np.column_stack([np.cos(pose[1:, 2]), np.sin(pose[1:, 2])]), 1) / np.diff(t)

    history = json.loads((run / 'plan_history.json').read_text())
    spawn = history['new_obstacles'][0]
    _, bx, by, byaw, size = spawn['detail']
    box = (bx, by, byaw, *size)
    replan = next(e for e in history['plans'] if e['why'] == 'replan')
    # the plan the truck was following: the last live transport plan before the replan (the
    # transport start records two, 0.04 s apart; the stop is 2.5 cm off the second)
    live = [tuple(p[:2]) for p in [e for e in history['plans'] if e['why'] == 'live' and e['phase'] == 'transport'
                                   and e['time_s'] <= replan['time_s']][-1]['poses']]
    rev, *rest = gear_runs(replan['poses'])
    fwd = [q for r in rest for q in r]
    t_spawn, t_replan = spawn['time_s'], replan['time_s']
    i = int(np.searchsorted(t, t_replan))
    i_rev0 = i + int(np.argmax(v[i:] < -0.02))
    i_rev1 = i_rev0 + int(np.argmax(v[i_rev0:] > -0.005))
    i_fwd0 = i_rev1 + int(np.argmax(v[i_rev1:] > 0.02))
    t_rev0, t_fwd0 = t[i_rev0], t[i_fwd0]
    fwd_np = np.array(fwd)
    s_fwd = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(fwd_np, axis=0), axis=1))])
    s_end = float(s_fwd[np.nonzero(fwd_np[:, 1] < by - 1.0)[0][0]])   # 1 m past the box (still in frame)
    t_end = float(np.interp(np.interp(t_fwd0, t, travel) + s_end, travel, t))

    x0, y0, yaw0 = history['replans'][0]['rear_pose']
    R = 1 / 0.29
    cx, cy = x0 + R * math.sin(yaw0), y0 - R * math.cos(yaw0)        # centre of the tightest right turn
    phis = np.linspace(math.atan2(y0 - cy, x0 - cx), math.atan2(by - cy, bx - cx) - 0.30, 60)
    r_in, r_out = R - 0.40, math.hypot(R + 0.40, 1.56)
    band = ([(cx + r_out * math.cos(q), cy + r_out * math.sin(q)) for q in phis]
            + [(cx + r_in * math.cos(q), cy + r_in * math.sin(q)) for q in phis[::-1]])
    rev_m = length(rev)
    c0, s0 = math.cos(yaw0), math.sin(yaw0)
    i_live = min(range(len(live)), key=lambda k: math.hypot(live[k][0] - x0, live[k][1] - y0))
    ahead = live[i_live:]
    s_live = np.concatenate([[0], np.cumsum([math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ahead, ahead[1:])])])
    arc_dev = max(abs(math.hypot(q[0] - cx, q[1] - cy) - R) for q, s in zip(ahead, s_live) if s <= 4.0)
    meta = dict(t_spawn=round(t_spawn, 2), t_replan=round(t_replan, 2), t_reverse=round(float(t_rev0), 2),
                t_forward=round(float(t_fwd0), 2), t_end=round(t_end, 2), reverse_plan_m=round(rev_m, 3),
                reverse_driven_m=round(float(travel[i_rev1] - travel[i_rev0]), 3),
                box_ahead_m=round(c0 * (bx - x0) + s0 * (by - y0), 3),
                box_left_m=round(-s0 * (bx - x0) + c0 * (by - y0), 3),
                box_from_turn_centre_m=round(math.hypot(bx - cx, by - cy), 3),
                body_sweep_m=[round(r_in, 3), round(r_out, 3)],
                live_min_to_box_m=round(min(math.hypot(p[0] - bx, p[1] - by) for p in live), 3),
                stop_to_live_m=round(min(math.hypot(p[0] - x0, p[1] - y0) for p in live), 3),
                live_off_tightest_arc_4m=round(arc_dev, 3),
                replan_min_to_box_m=round(min(math.hypot(p[0] - bx, p[1] - by) for p in rev + fwd), 3))
    print(json.dumps(meta))

    def caption_at(tt):
        if tt < t_spawn:
            return None
        if tt < t_replan:
            return '신규 장애물 감지 · 정지'
        if tt < t_rev0 + 1.0:
            return '최소 회전 반경 스윕 영역 – 장애물 간섭'
        if tt < t_fwd0:
            return f'① 후진 {rev_m:.2f} m'
        return '② 전진 · 장애물 회피'

    picks = []
    for a, b, speed in ((t_spawn - 3.0, t_replan, 2.0), (t_replan, None, 2.5), (t_replan, t_end, 2.0)):
        if b is None:                       # hold the frame at a for `speed` seconds
            picks += [int(np.searchsorted(t, a))] * int(round(speed * FPS))
            continue
        tt = a
        while tt <= b:
            picks.append(int(np.searchsorted(t, tt)))
            tt += speed / FPS
    picks += [picks[-1]] * int(1.5 * FPS)
    held = int(np.searchsorted(t, t_replan))

    cx0, cy0, cw, ch = CROP
    out = HERE / 'assets/55_reverse_box.mp4'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{cw}x{ch}',
                            '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p',
                            '-movflags', '+faststart', str(out)], stdin=subprocess.PIPE)
    first, last = picks[0], picks[-1]
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{first / FPS:.4f}', '-i', str(run / 'view_quarter.mp4'),
                            '-frames:v', str(last - first + 1), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                           stdout=subprocess.PIPE)
    j = 0
    for k in range(last - first + 1):
        buf = dec.stdout.read(W * H * 3)
        idx = first + k
        if idx != picks[j]:
            continue
        tt = t[idx]
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        hulls = silhouettes(cam, pose[idx], [box] if tt >= t_spawn else [])
        if t_replan <= tt < t_rev0 + 1.0:
            img = tint(img, cam, hulls, band, RED)
        layer = img.copy()
        draw_path(layer, cam, hulls, live, YELLOW, 4)
        if tt >= t_replan:
            if tt < t[i_rev1]:
                draw_path(layer, cam, hulls, after(rev, max(0.0, travel[idx] - travel[i_rev0])), ORANGE, 9)
            draw_path(layer, cam, hulls, after(fwd, max(0.0, travel[idx] - travel[i_fwd0]) if tt >= t_fwd0 else 0.0),
                      BLUE, 9)
        img = cv2.addWeighted(layer, 0.9, img, 0.1, 0)[cy0:cy0 + ch, cx0:cx0 + cw]
        text = caption_at(tt)
        img = np.ascontiguousarray(caption(np.ascontiguousarray(img), text) if text else img)
        if idx == held:
            Image.fromarray(img).save(HERE / 'assets/55_reverse_box_poster.jpg', quality=88)
        while j < len(picks) and picks[j] == idx:
            enc.stdin.write(img.tobytes())
            j += 1
        if j >= len(picks):
            break
    dec.stdout.close()
    dec.wait()
    enc.stdin.close()
    enc.wait()


if __name__ == '__main__':
    main(sys.argv[1])
