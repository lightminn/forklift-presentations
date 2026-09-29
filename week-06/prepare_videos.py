"""Render the two explanatory LiDAR clips of the week 5 deck from the recorded
Isaac survey (no simulator needed).

    python prepare_videos.py /path/to/forklift/artifacts

Needs NumPy, Pillow and ffmpeg. Inputs are the 2026-09-26 survey record
(seed 0: scans, ground-truth laser pose, obstacle layout) and the 2026-09-28
slam_toolbox replay of it (SLAM and wheel-odometry trajectories).

- assets/25_scan_view.mp4: a camera that follows the truck from above; the
  current scan is drawn as rays to every hit, so the audience sees what one
  planar LiDAR sweep returns and which objects the scan plane misses.
- assets/26_map_compare.mp4: the same scans stacked into a map twice, once at
  the wheel/steering pose and once at the SLAM pose, growing side by side.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from prepare_data import _csv, _rows_at, _to_world, _yaw

HERE = Path(__file__).resolve().parent
FONTS = ('/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
BG, FLOOR = (238, 241, 244), (255, 255, 255)
LOW, HIGH = (214, 218, 224), (120, 132, 146)      # below / reaching the scan plane
RAY, HIT, TRUCK = (242, 170, 160), (200, 40, 30), (26, 58, 110)


def _font(size):
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _encoder(path, w, h, fps, crf=23):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}',
                             '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-crf', str(crf), '-pix_fmt', 'yuv420p',
                             '-movflags', '+faststart', str(path)], stdin=subprocess.PIPE)


def _box(o):
    c, s = math.cos(o['yaw_rad']), math.sin(o['yaw_rad'])
    hx, hy = o['length_m'] / 2, o['width_m'] / 2
    return [(o['x_m'] + c * x - s * y, o['y_m'] + s * x + c * y) for x, y in ((hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy))]


def load(record, replay, clock_offset=10.0):
    meta = json.loads((record / 'meta.json').read_text())
    with np.load(record / 'slam_log.npz') as d:
        scans, ranges = d['scan_stamps_s'], d['scan_ranges_m']
        laser = d['laser_pose_world']
        joints, base = d['joint_stamps_s'], d['base_pose_world'].astype(float)
    start = np.array([base[0, 0], base[0, 1], _yaw(base[:1, 3:7])[0]])
    mount = meta['laser']['mount_xyz_m'][0]
    def laser_world(table, stamps, offset):
        rows = _rows_at(stamps, table[:, 0] - offset)
        ok = rows >= 0
        xy = _to_world(table[rows[ok], 1:3], start)
        yaw = table[rows[ok], 3] + start[2]
        xy = xy + mount * np.column_stack((np.cos(yaw), np.sin(yaw)))
        pose = np.full((len(stamps), 3), np.nan)
        pose[ok] = np.column_stack((xy, yaw))
        return pose
    slam = laser_world(_csv(replay / 'slam/slam_trajectory.csv'), scans, clock_offset)
    odom = laser_world(_csv(replay / 'odometry.csv'), scans, 0.0)
    angles = meta['laser']['angle_min_rad'] + meta['laser']['angle_increment_rad'] * np.arange(ranges.shape[1])
    return dict(meta=meta, ranges=ranges, angles=angles, truth=laser, slam=slam, odom=odom,
                plane=meta['laser']['mount_xyz_m'][2])


def _hits(pose, rng, angles, rmax):
    ok = np.isfinite(rng) & (rng > 0) & (rng < rmax - 1e-3)
    a = pose[2] + angles[ok]
    return np.column_stack((pose[0] + rng[ok] * np.cos(a), pose[1] + rng[ok] * np.sin(a)))


def scan_view(data, out, seconds=20, fps=30, W=1120, H=840, span=18.0):
    """Top-down follow camera with the live scan."""
    meta, rmax = data['meta'], data['meta']['laser']['range_max_m']
    # an object meets the scan plane only if the plane passes between its bottom and top
    boxes = [(_box(o), o['base_m'] <= data['plane'] <= o['base_m'] + o['height_m']) for o in meta['obstacles']]
    hall = meta['hall']
    scale = W / span
    n = len(data['ranges'])
    frames = seconds * fps
    font, small = _font(30), _font(24)
    proc = _encoder(out, W, H, fps, crf=30)
    for f in range(frames):
        k = min(n - 1, int(f / frames * n * 0.55))             # first 55 % of the route
        pose = data['truth'][k]
        cx, cy = pose[0], pose[1]
        px = lambda x, y: (W / 2 + (x - cx) * scale, H / 2 - (y - cy) * scale)
        im = Image.new('RGB', (W, H), BG)
        dr = ImageDraw.Draw(im)
        dr.polygon([px(hall['x_min_m'], hall['y_min_m']), px(hall['x_max_m'], hall['y_min_m']),
                    px(hall['x_max_m'], hall['y_max_m']), px(hall['x_min_m'], hall['y_max_m'])], fill=FLOOR)
        for pts, high in boxes:
            dr.polygon([px(*p) for p in pts], fill=HIGH if high else LOW)
        hits = _hits(pose, data['ranges'][k], data['angles'], rmax)
        o = px(pose[0], pose[1])
        for x, y in hits[::4]:
            dr.line([o, px(x, y)], fill=RAY, width=1)
        for x, y in hits:
            u, v = px(x, y)
            dr.ellipse((u - 2.5, v - 2.5, u + 2.5, v + 2.5), fill=HIT)
        c, s = math.cos(pose[2]), math.sin(pose[2])
        body = [(0.9, 0.32), (-0.6, 0.32), (-0.6, -0.32), (0.9, -0.32)]
        dr.polygon([px(pose[0] + c * x - s * y, pose[1] + s * x + c * y) for x, y in body], fill=TRUCK)
        dr.ellipse((o[0] - 7, o[1] - 7, o[0] + 7, o[1] + 7), fill=(255, 255, 255), outline=HIT, width=3)
        # legend
        dr.rounded_rectangle((16, 16, 560, 150), 8, fill=(255, 255, 255))
        dr.ellipse((34, 38, 50, 54), fill=HIT); dr.text((62, 28), '스캔이 닿은 점 (한 바퀴 1,600빔)', font=small, fill=(30, 30, 30))
        dr.rectangle((34, 76, 50, 92), fill=HIGH); dr.text((62, 66), '스캔 높이 1.05 m에 걸친 물체', font=small, fill=(30, 30, 30))
        dr.rectangle((34, 114, 50, 130), fill=LOW); dr.text((62, 104), '걸치지 않는 물체 — 안 보임', font=small, fill=(30, 30, 30))
        proc.stdin.write(im.tobytes())
        if f == int(frames * 0.45):
            im.save(out.with_name(out.stem + '_poster.jpg'), quality=90)
    proc.stdin.close(); proc.wait()


def map_compare(data, out, seconds=18, fps=30, panel=620, pad=16):
    """Scans stacked at the wheel/steering pose (left) and the SLAM pose (right)."""
    meta, rmax = data['meta'], data['meta']['laser']['range_max_m']
    hall = meta['hall']
    x0, x1, y0, y1 = hall['x_min_m'] - 1.5, hall['x_max_m'] + 1.5, hall['y_min_m'] - 1.5, hall['y_max_m'] + 1.5
    scale = panel / max(x1 - x0, y1 - y0)
    PW, PH = int((x1 - x0) * scale), int((y1 - y0) * scale)
    head = 96
    W, H = 2 * PW + 3 * pad, PH + head + pad
    W += W % 2; H += H % 2
    grids = {k: np.zeros((PH, PW), np.float32) for k in ('odom', 'slam')}
    colour = {'odom': np.array([194, 106, 26]), 'slam': np.array([47, 116, 192])}
    title = {'odom': '바퀴·조향 추정 위치로 쌓은 지도', 'slam': 'SLAM 추정 위치로 쌓은 지도'}
    n = len(data['ranges'])
    frames = seconds * fps
    font = _font(28)
    done = 0
    proc = _encoder(out, W, H, fps)

    def add(upto):
        nonlocal done
        for k in range(done, upto):
            for key in grids:
                pose = data[key][k]
                if np.isnan(pose[0]):
                    continue
                h = _hits(pose, data['ranges'][k], data['angles'], rmax)
                u = ((h[:, 0] - x0) * scale).astype(int); v = ((y1 - h[:, 1]) * scale).astype(int)
                m = (u >= 0) & (u < PW) & (v >= 0) & (v < PH)
                np.add.at(grids[key], (v[m], u[m]), 1.0)
        done = upto

    def render(upto):
        im = Image.new('RGB', (W, H), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        for i, key in enumerate(('odom', 'slam')):
            ink = np.clip(grids[key] / 6.0, 0, 1)[..., None]
            rgb = (255 * (1 - ink) + colour[key] * ink).astype(np.uint8)
            left = pad + i * (PW + pad)
            im.paste(Image.fromarray(rgb), (left, head))
            dr.rectangle((left, head, left + PW - 1, head + PH - 1), outline=(200, 205, 212), width=2)
            path = data[key][:upto:10]
            path = path[~np.isnan(path[:, 0])]
            if len(path) > 1:
                dr.line([(left + (x - x0) * scale, head + (y1 - y) * scale) for x, y, _ in path], fill=(30, 30, 30), width=2)
            dr.text((left + 4, 8), title[key], font=font, fill=tuple(int(c * 0.8) for c in colour[key]))
            dr.text((left + 4, 52), '검은 선: 그 방식으로 추정한 경로', font=_font(20), fill=(90, 90, 90))
        return im

    for f in range(frames):
        upto = min(n, int(f / (frames - fps) * n) + 1)
        add(upto)
        proc.stdin.write(render(upto).tobytes())
    proc.stdin.close(); proc.wait()
    render(n).save(out.with_name(out.stem + '_poster.jpg'), quality=90)


if __name__ == '__main__':
    art = Path(sys.argv[1])
    d = load(art / '20260926_factory_slam_v3/survey_seed_0', art / '20260928_week05_replay/survey_seed_0_clean')
    which = sys.argv[2:] or ['scan', 'map']
    if 'scan' in which:
        scan_view(d, HERE / 'assets/25_scan_view.mp4')
    if 'map' in which:
        map_compare(d, HERE / 'assets/26_map_compare.mp4')
    print('done', which)
