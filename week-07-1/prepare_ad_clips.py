#!/usr/bin/env python3
"""Cut the A-D clips: each approach case from detection to the lift, from the fixed quarter camera,
with the plan being driven drawn on the floor (conda base: numpy, opencv, PIL; ffmpeg).

    python prepare_ad_clips.py RUN_ROOT

RUN_ROOT is ws1 artifacts/20261012_meeting_ad (meeting_ad3.sbatch): v3_{A,B,C,D}/run, each one recorded
mission on seed 5 with one observation candidate (the case's detection pose) and D's box. Every case
writes assets/56_case_{a,b,c,d}.mp4 and _poster.jpg (cropped to the approach area, CROP), and prints
its timeline and gear runs.

The clip starts at the far capture (the post-detection observe plan), follows the observe leg to the
alignment straight's start, the stop there (the near capture), the straight approach and insertion,
and ends 1 s after the lift; a small stage label (prepare_reverse_clip.caption) sits in the top-left corner.
The plan being driven is drawn with its remaining part only, forward runs
blue and reverse runs orange; hidden where the truck or the box covers it (prepare_reverse_clip).
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import prepare_reverse_clip as rc

HERE = Path(__file__).resolve().parent
FPS = 30
SPEED = 2.0
CROP = (150, 130, 1040, 372)        # x, y, w, h: the approach area, the 2 x 2 cell's aspect
STAGE = {'approach': '정렬 직진', 'insert': '포크 삽입', 'lift': '리프트'}


def gear_runs_with_sign(poses, yaw0):
    """Plan polyline -> [(sign, points)] using the start heading for the first run's sign."""
    runs = rc.gear_runs(poses)
    out = []
    for k, pts in enumerate(runs):
        if k == 0:
            a, b = pts[0], pts[min(1, len(pts) - 1)]
            sign = 1 if math.cos(math.atan2(b[1] - a[1], b[0] - a[0]) - yaw0) >= 0 else -1
        else:
            sign = -out[-1][0]
        out.append((sign, pts))
    return out


def clip(case, run, out_name):
    result = json.loads((run / 'result.json').read_text())
    view = result['extra_views']['quarter']
    cam = rc.Camera(view['eye_m'], view['target_m'], view['focal_length_mm'])
    rows = [json.loads(line) for line in open(run / 'frames.jsonl')]
    t = np.array([r['simulation_time_s'] for r in rows])
    phase = [r['phase'] for r in rows]
    pose = []
    for r in rows:
        w, x, y, z = r['base_orientation_wxyz']
        pose.append((*r['base_position_m'][:2], math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))))
    pose = np.array(pose)
    rear = pose[:, :2] + rc.REAR_AXLE_X * np.column_stack([np.cos(pose[:, 2]), np.sin(pose[:, 2])])
    travel = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(rear, axis=0), axis=1))])
    v = np.zeros(len(t))
    v[1:] = np.sum(np.diff(rear, axis=0) * np.column_stack([np.cos(pose[1:, 2]), np.sin(pose[1:, 2])]), 1) / np.diff(t)

    history = json.loads((run / 'plan_history.json').read_text())
    wp = result['arguments']['observation_waypoints'][0]
    plans = [e for e in history['plans'] if e['phase'] in ('observe', 'approach', 'insert')]
    # the far capture: the first observe plan made after the start, from (near) the detection pose
    after = [e for e in plans if e['phase'] == 'observe' and e['time_s'] > 0.5
             and math.hypot(e['poses'][0][0] - wp[0], e['poses'][0][1] - wp[1]) < 0.4]
    if not after:
        raise SystemExit(f'{case}: no post-detection observe plan')
    t_detect = after[0]['time_s']
    driven = [e for e in plans if e['time_s'] >= t_detect - 1e-6]
    i_lift = [k for k, p in enumerate(phase) if p == 'lift']
    i_extract = [k for k, p in enumerate(phase) if p == 'extract']
    t_end = t[i_extract[0]] + 1.0 if i_extract else (t[i_lift[-1]] + 1.0 if i_lift else t[-1])
    boxes = [(d[1], d[2], d[3], *d[4]) for d in (n['detail'] for n in history.get('new_obstacles', []))]

    # plan polylines with gear signs, and the travel at which each plan started
    segments = []
    for e in driven:
        i0 = int(np.searchsorted(t, e['time_s']))
        yaw0 = pose[min(i0, len(pose) - 1), 2]
        segments.append(dict(t=e['time_s'], s0=travel[min(i0, len(travel) - 1)], phase=e['phase'],
                             runs=gear_runs_with_sign([tuple(p[:2]) for p in e['poses']], yaw0)))
    summary = dict(case=case, waypoint=wp, t_detect=round(t_detect, 2), t_end=round(float(t_end), 2),
                   success=result.get('success'), phase=result.get('phase'),
                   delivery_mm=None if result.get('delivery_error_m') is None else round(1000 * result['delivery_error_m'], 1),
                   plans=[(s['phase'], round(s['t'], 2), [('F' if g > 0 else 'R', round(rc.length(p), 2)) for g, p in s['runs']])
                          for s in segments],
                   boxes=boxes)
    print(json.dumps(summary, ensure_ascii=False))

    def active(tt):
        cur = None
        for s in segments:
            if s['t'] <= tt:
                cur = s
        return cur

    def caption_at(i):
        tt, ph = t[i], phase[i]
        if ph in STAGE:
            return STAGE[ph]
        if tt < t_detect + 1.5 and abs(v[i]) < 0.01:
            return '인식 · 경로 계획'
        if v[i] > 0.01:
            return '전진'
        if v[i] < -0.01:
            return '후진'
        return '재관측'

    picks = []
    tt = t_detect
    hold = int(1.0 * FPS)
    picks += [int(np.searchsorted(t, t_detect))] * hold
    while tt <= t_end:
        picks.append(int(np.searchsorted(t, tt)))
        tt += SPEED / FPS
    picks += [picks[-1]] * int(1.0 * FPS)
    W, H = rc.W, rc.H
    cx0, cy0, cw, ch = CROP
    out = HERE / 'assets' / out_name
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{cw}x{ch}',
                            '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p',
                            '-movflags', '+faststart', str(out)], stdin=subprocess.PIPE)
    first, last = picks[0], picks[-1]
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{first / FPS:.4f}', '-i', str(run / 'view_quarter.mp4'),
                            '-frames:v', str(last - first + 1), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                           stdout=subprocess.PIPE)
    j, poster_at = 0, None
    for k in range(last - first + 1):
        buf = dec.stdout.read(W * H * 3)
        idx = first + k
        if len(buf) < W * H * 3:
            break
        if idx != picks[j]:
            continue
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        hulls = rc.silhouettes(cam, pose[idx], boxes)
        layer = img.copy()
        seg = active(t[idx])
        if seg is not None:
            done = max(0.0, travel[idx] - seg['s0'])
            for g, pts in seg['runs']:
                n = rc.length(pts)
                if done >= n:
                    done -= n
                    continue
                rc.draw_path(layer, cam, hulls, rc.after(pts, done), rc.BLUE if g > 0 else rc.ORANGE, 9)
                done = 0.0
        img = np.ascontiguousarray(rc.cv2.addWeighted(layer, 0.9, img, 0.1, 0)[cy0:cy0 + ch, cx0:cx0 + cw])
        img = np.ascontiguousarray(rc.caption(img, caption_at(idx), size=28))
        if poster_at is None and v[idx] != 0 and abs(v[idx]) > 0.05:
            poster_at = idx
            Image.fromarray(img).save(HERE / 'assets' / out_name.replace('.mp4', '_poster.jpg'), quality=88)
        while j < len(picks) and picks[j] == idx:
            enc.stdin.write(img.tobytes())
            j += 1
        if j >= len(picks):
            break
    dec.stdout.close()
    dec.wait()
    enc.stdin.close()
    enc.wait()
    return summary


# run folder -> case (the deck's clips, 2026-10-12 v3, after the brief's drawings on slides 8-11): the truck starts
# 0.3 m behind its detection pose (meeting_ad3.sbatch, --start-rear), the alignment straight is 0.8 m, D has a wall
# behind and a block on the left (d_walls2.yaml). The first sets (case_*, v2_*) are kept in RUN_ROOT.
DECK_RUNS = (('v3_A', 'a'), ('v3_B', 'b'), ('v3_C', 'c'), ('v3_D', 'd'))

if __name__ == '__main__':
    root = Path(sys.argv[1])
    for run_name, label in DECK_RUNS:
        clip(run_name, root / run_name / 'run', f'56_case_{label}.mp4')
