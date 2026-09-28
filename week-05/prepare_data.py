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


if __name__ == '__main__':
    main()
