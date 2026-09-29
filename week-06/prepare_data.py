"""Extract the small data files the week 5 charts are drawn from.

Run once with a Python that has NumPy (the robot repository's environment),
from any directory:

    python prepare_data.py /path/to/forklift/artifacts

Reads the 2026-09-26 Isaac records and the 2026-09-28 slam_toolbox replays
(see SOURCES.md) and writes assets/data_*.json. build_deck.py only reads those
JSON files, so the deck itself still builds without NumPy.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
STAMP_TOLERANCE_S = 1e-6


def _yaw(q):
    w, x, y, z = q.T
    return np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


def _csv(path):
    return np.loadtxt(path, delimiter=',', skiprows=1)


def _rows_at(stamps, table):
    order = np.argsort(table)
    ordered = table[order]
    right = np.clip(np.searchsorted(ordered, stamps), 0, len(ordered) - 1)
    left = np.clip(right - 1, 0, len(ordered) - 1)
    near = np.where(np.abs(ordered[left] - stamps) < np.abs(ordered[right] - stamps), left, right)
    found = np.abs(ordered[near] - stamps) <= STAMP_TOLERANCE_S
    return np.where(found, order[near], -1)


def _to_world(poses, start):
    c, s = math.cos(start[2]), math.sin(start[2])
    return np.column_stack((start[0] + c * poses[:, 0] - s * poses[:, 1],
                            start[1] + s * poses[:, 0] + c * poses[:, 1]))


def trajectories(record, replay, clock_offset=10.0, keep=400):
    """World paths at scan stamps, start-pose aligned exactly as
    tools/evaluate_slam_replay.py does, plus the error along the path."""
    with np.load(record / 'slam_log.npz') as d:
        joints, base, scans = d['joint_stamps_s'], d['base_pose_world'].astype(float), d['scan_stamps_s']
    truth_all = np.column_stack((base[:, 0], base[:, 1], _yaw(base[:, 3:7])))
    start = truth_all[0]
    truth = truth_all[_rows_at(scans, joints)][:, :2]
    slam = _csv(replay / 'slam/slam_trajectory.csv')
    rows = _rows_at(scans, slam[:, 0] - clock_offset)
    odom = _csv(replay / 'odometry.csv')
    orows = _rows_at(scans, odom[:, 0])
    ok = rows >= 0
    slam_w = _to_world(slam[rows[ok], 1:], start)
    odom_w = _to_world(odom[orows, 1:], start)
    truth_ok = truth[ok]
    dist = np.concatenate(([0], np.cumsum(np.hypot(*np.diff(truth_ok, axis=0).T))))
    step = max(1, len(truth_ok) // keep)
    pick = np.arange(0, len(truth_ok), step)
    r = lambda a: np.round(a, 3).tolist()
    return {
        'truth': r(truth_ok[pick]), 'slam': r(slam_w[pick]), 'odom': r(odom_w[ok][pick]),
        'distance_m': r(dist[pick]),
        'slam_error_m': r(np.hypot(*(slam_w - truth_ok)[pick].T)),
        'odom_error_m': r(np.hypot(*(odom_w[ok] - truth_ok)[pick].T)),
    }


def main():
    art = Path(sys.argv[1])
    survey = trajectories(art / '20260926_factory_slam_v3/survey_seed_0',
                          art / '20260928_week05_replay/survey_seed_0_clean')
    (HERE / 'assets/data_survey_seed0.json').write_text(json.dumps(survey, separators=(',', ':')))
    print('survey points', len(survey['truth']), 'final errors', survey['slam_error_m'][-1], survey['odom_error_m'][-1])


if __name__ == '__main__' and len(sys.argv) == 2:
    main()


def map_growth_video(replay, record, out_mp4, out_png, seconds=12, size=720):
    """The slam_toolbox map as it grew, north up, with the true path drawn so
    far. Uses map_history.npz written by slam_recorder (map_history:=true)."""
    import subprocess
    from PIL import Image, ImageDraw
    hist = np.load(replay / 'slam/map_history.npz')
    names = sorted(k for k in hist.files if k.startswith('map_'))
    origins, stamps = hist['origins'], hist['stamps_ns'] / 1e9 - 10.0
    res = float(hist['resolutions_m'][0])
    with np.load(record / 'slam_log.npz') as d:
        t, base = d['joint_stamps_s'], d['base_pose_world'].astype(float)
    start_yaw = float(_yaw(base[:1, 3:7])[0])
    x0, y0 = base[0, 0], base[0, 1]
    # map frame -> world: rotate by the start heading about the start pose
    c, s = math.cos(start_yaw), math.sin(start_yaw)
    last = hist[names[-1]]
    ox, oy = origins[-1, :2]
    corners = np.array([[ox, oy], [ox + last.shape[1] * res, oy], [ox, oy + last.shape[0] * res],
                        [ox + last.shape[1] * res, oy + last.shape[0] * res]])
    world = np.column_stack((x0 + c * corners[:, 0] - s * corners[:, 1], y0 + s * corners[:, 0] + c * corners[:, 1]))
    wx0, wy0 = world.min(axis=0) - 0.5
    wx1, wy1 = world.max(axis=0) + 0.5
    scale = (size - 20) / max(wx1 - wx0, wy1 - wy0)
    W, H = int((wx1 - wx0) * scale) + 20, int((wy1 - wy0) * scale) + 20
    W += W % 2; H += H % 2

    def px(xw, yw):
        return 10 + (xw - wx0) * scale, H - 10 - (yw - wy0) * scale

    def render(k):
        grid = hist[names[k]]
        ox, oy = origins[k, :2]
        rgb = np.full(grid.shape + (3,), (214, 218, 224), np.uint8)
        rgb[(grid >= 0) & (grid <= 25)] = (255, 255, 255)
        rgb[grid >= 65] = (11, 60, 140)
        tile = Image.fromarray(np.flipud(rgb))
        tile = tile.resize((max(1, int(tile.width * res * scale)), max(1, int(tile.height * res * scale))), Image.NEAREST)
        tile = tile.rotate(math.degrees(start_yaw), expand=True, fillcolor=(214, 218, 224), resample=Image.NEAREST)
        cx, cy = ox + grid.shape[1] * res / 2, oy + grid.shape[0] * res / 2
        wx, wy = x0 + c * cx - s * cy, y0 + s * cx + c * cy
        u, v = px(wx, wy)
        frame = Image.new('RGB', (W, H), (214, 218, 224))
        frame.paste(tile, (int(u - tile.width / 2), int(v - tile.height / 2)))
        upto = np.searchsorted(t, stamps[k])
        path = [px(x, y) for x, y in base[:max(upto, 2):20, :2]]
        dr = ImageDraw.Draw(frame)
        dr.line(path, fill=(47, 116, 192), width=4)
        ex, ey = path[-1]
        dr.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=(194, 106, 26))
        return frame

    fps = 30
    total = seconds * fps
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-crf', '24', '-pix_fmt', 'yuv420p',
                             '-movflags', '+faststart', str(out_mp4)], stdin=subprocess.PIPE)
    for f in range(total):
        k = min(len(names) - 1, int(f / (total - fps) * (len(names) - 1)))   # hold the last map 1 s
        proc.stdin.write(render(k).tobytes())
    proc.stdin.close(); proc.wait()
    render(len(names) - 1).save(out_png, quality=90)
    print('map growth', W, H, len(names), 'maps')


if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[2] == 'map':
    art = Path(sys.argv[1])
    map_growth_video(art / '20260928_week05_replay/survey_seed_0_clean', art / '20260926_factory_slam_v3/survey_seed_0',
                     HERE / 'assets/23_map_growth.mp4', HERE / 'assets/23_map_growth_poster.jpg')
