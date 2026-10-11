#!/usr/bin/env python3
"""Draw the path-planning figures of the meeting deck as SVG (stdlib + numpy).

    python prepare_figures.py /path/to/forklift

Writes figures/ (inlined into the page by build_deck.py so the deck font applies):
1. 52_reverse_obstacle.svg -- the week 6 new-obstacle scene (measured chassis, seed 5, box
   during transport; videos-from-ws1/20261007_l8_measured_seed5_n1/plan_history.json): the
   live transport plan before the box, and the replan made at the stop (94.3 s), drawn in the
   truck's frame at that stop. Directions come from the motion against the stopped heading.
2. 53_goal_fix.svg -- the D7 test case (tests/unit/planning/test_d7_planner_options.py:
   l8_measured seed 1 + N1 stall replan, goal 1 cm ahead and 0.023 rad off) planned with the
   original forward-only goal connection and with D7_PLANNER_OPTIONS (Reeds-Shepp, 4 m cap).
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLUE, ORANGE, GREY, RED, INK = '#2f74c0', '#c26a1a', '#9aa3ad', '#c0392b', '#1b1f24'
FONT = 'var(--uos-font)'


def svg(width, height, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="{label}"><g font-family="{FONT}">{body}</g></svg>\n')


def polyline(points, colour, width=4, dash=None):
    d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)
    extra = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<polyline points="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')


def rect(cx, cy, length, width, yaw, colour, fill, to_px, sw=2.5):
    c, s = math.cos(yaw), math.sin(yaw)
    corners = [(cx + c * a - s * b, cy + s * a + c * b)
               for a, b in ((length / 2, width / 2), (-length / 2, width / 2),
                            (-length / 2, -width / 2), (length / 2, -width / 2))]
    d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in map(to_px, corners))
    return f'<polygon points="{d}" fill="{fill}" stroke="{colour}" stroke-width="{sw}"/>'


def truck(x, y, yaw, to_px, prefix, colour=INK, fill='#ffffff'):
    """Loaded planning footprint: 1.56 m ahead of the rear axle, 0.17 m behind, 0.80 m wide
    (the D7 test's LOADED footprint)."""
    front, rear, half = 1.56, 0.17, 0.40
    cx = x + math.cos(yaw) * (front - rear) / 2
    cy = y + math.sin(yaw) * (front - rear) / 2
    out = rect(cx, cy, front + rear, 2 * half, yaw, colour, fill, to_px)
    tip = to_px((x + math.cos(yaw) * (front + 0.25), y + math.sin(yaw) * (front + 0.25)))
    base = to_px((x + math.cos(yaw) * front, y + math.sin(yaw) * front))
    return out + (f'<line x1="{base[0]:.1f}" y1="{base[1]:.1f}" x2="{tip[0]:.1f}" y2="{tip[1]:.1f}" '
                  f'stroke="{colour}" stroke-width="3" marker-end="url(#{prefix}-ah)"/>')


def split_by_gear(points, heading):
    """Split a pose sequence into (gear, points) runs; the first gear is from the motion
    against the given heading, a gear change where the motion turns by more than 2 rad."""
    runs, prev = [], None
    for a, b in zip(points, points[1:]):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        if prev is None:
            gear = 1 if math.cos(ang - heading) > 0 else -1
            runs.append([gear, [a]])
        elif abs((ang - prev + math.pi) % (2 * math.pi) - math.pi) > 2.0:
            gear = -runs[-1][0]
            runs.append([gear, [a]])
        runs[-1][1].append(b)
        prev = ang
    return runs


def length(points):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def arrows(prefix):
    # Marker ids carry the figure's prefix: both figures are inlined into one page.
    return '<defs>' + ''.join(
        f'<marker id="{prefix}-{name}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{colour}"/></marker>'
        for name, colour in (('ah', INK), ('ah-b', BLUE), ('ah-o', ORANGE))) + '</defs>'


def reverse_obstacle(repo):
    run = repo / 'videos-from-ws1/20261007_l8_measured_seed5_n1'
    history = json.loads((run / 'plan_history.json').read_text())
    replan = next(e for e in history['plans'] if e['why'] == 'replan')
    live = next(e for e in history['plans'] if e['why'] == 'live' and e['phase'] == 'transport')
    x0, y0, yaw0 = history['replans'][0]['rear_pose']
    spawn = history['new_obstacles'][0]['detail']          # name, x, y, yaw, size
    c, s = math.cos(yaw0), math.sin(yaw0)

    def local(p):
        return (c * (p[0] - x0) + s * (p[1] - y0), -s * (p[0] - x0) + c * (p[1] - y0))

    old = [local(p) for p in live['poses']]
    start = min(range(len(old)), key=lambda i: math.hypot(*old[i]))
    old = old[start:]
    new = [local(p) for p in replan['poses']]
    runs = split_by_gear(new, 0.0)
    box = local(spawn[1:3])
    box_yaw = spawn[3] - yaw0
    # Frame: truck heading to the right; +y (left of the truck) up.
    xmin, xmax, ymin, ymax = -2.0, 6.2, -3.4, 1.5
    width, scale = 640, 640 / (xmax - xmin)
    height = round((ymax - ymin) * scale)

    def px(p):
        return ((p[0] - xmin) * scale, (ymax - p[1]) * scale)

    def clip(points):
        return [p for p in points if xmin <= p[0] <= xmax and ymin <= p[1] <= ymax]

    parts = [arrows('rv'), truck(0.0, 0.0, 0.0, px, 'rv', fill='#eef3fa')]
    parts.append(polyline([px(p) for p in clip(old)], GREY, 4, '10 8'))
    reverse_len = forward_len = 0.0
    for gear, points in runs:
        if gear < 0:
            reverse_len += length(points)
        else:
            forward_len += length(points)
        parts.append(polyline([px(p) for p in clip(points)], ORANGE if gear < 0 else BLUE, 5))
    parts.append(rect(box[0], box[1], spawn[4][0], spawn[4][1], box_yaw, RED, '#f6d5d0', px))
    bx, by = px(box)
    parts.append(f'<text x="{bx + 26:.0f}" y="{by + 8:.0f}" font-size="21" font-weight="700" fill="{RED}">새 상자</text>')
    for xy, text, colour, anchor in (((0.70, 0.60), '멈춘 위치', INK, 'middle'),
                                     ((-1.05, 0.30), f'① 후진 {reverse_len:.2f} m', ORANGE, 'middle'),
                                     ((0.92, -1.85), '② 전진', BLUE, 'end'),
                                     ((3.05, -1.55), '원래 경로', '#6b7480', 'start')):
        x, y = px(xy)
        parts.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="21" font-weight="700" fill="{colour}" '
                     f'text-anchor="{anchor}">{text}</text>')
    label = (f'새 상자 앞에서 멈춘 지게차의 재계획 경로. 회색 점선은 원래 경로로 상자를 지나간다. '
             f'주황은 후진 {reverse_len:.2f} m, 파랑은 이어지는 전진')
    meta = dict(reverse_m=round(reverse_len, 2), forward_m=round(forward_len, 2),
                box_ahead_m=round(box[0], 2), box_right_m=round(-box[1], 2),
                old_min_to_box_m=round(min(math.hypot(p[0] - box[0], p[1] - box[1]) for p in old), 2),
                new_min_to_box_m=round(min(math.hypot(p[0] - box[0], p[1] - box[1]) for p in new), 2))
    return svg(width, height, ''.join(parts), label), meta


def goal_fix(repo):
    sys.path.insert(0, str(repo / 'src'))
    import numpy as np
    from forklift_core.planning import Bounds, Footprint, Pose2D
    from forklift_core.planning.hybrid_astar import PlannerConfig, plan_hybrid_astar
    from forklift_core.planning.pallet_mission import D7_PLANNER_OPTIONS
    bounds = Bounds(-30.0, 10.0, -30.0, 10.0)
    loaded = Footprint(1.56, 0.17, 0.40)
    measured = dict(curvature_limit_inv_m=0.29, primitive_length_m=0.25, max_expansions=30000, clearance_m=0.10)
    start, goal = Pose2D(-7.848, -18.669, -1.422), Pose2D(-7.851, -18.681, -1.399)
    plans = {}
    for name, config in (('forward', PlannerConfig(**measured)),
                         ('d7', PlannerConfig(**measured, **D7_PLANNER_OPTIONS))):
        result = plan_hybrid_astar(start, goal, [], loaded, bounds, config)
        assert result.success, name
        d = np.asarray(result.directions)
        plans[name] = dict(poses=np.asarray(result.poses)[:, :2].tolist(), length=float(result.length_m),
                           gear_changes=int((d[1:] != d[:-1]).sum()))
    c, s = math.cos(start.yaw_rad), math.sin(start.yaw_rad)

    def local(p):
        return (c * (p[0] - start.x_m) + s * (p[1] - start.y_m), -s * (p[0] - start.x_m) + c * (p[1] - start.y_m))

    loop = [local(p) for p in plans['forward']['poses']]
    short = [local(p) for p in plans['d7']['poses']]
    xs = [p[0] for p in loop]
    ys = [p[1] for p in loop]
    pad = 0.9
    xmin, xmax, ymin, ymax = min(xs) - pad, max(xs) + pad + 1.2, min(ys) - pad, max(ys) + pad + 0.6
    width = 640
    scale = width / (xmax - xmin)
    height = round((ymax - ymin) * scale)

    def px(p):
        return ((p[0] - xmin) * scale, (ymax - p[1]) * scale)

    runs = split_by_gear(short, 0.0)
    gears = [(gear, length(points)) for gear, points in runs]
    parts = [arrows('gf'), truck(0.0, 0.0, 0.0, px, 'gf', fill='#eef3fa'),
             polyline([px(p) for p in loop], GREY, 4, '10 8')]
    gl = local((goal.x_m, goal.y_m))
    gx, gy = px(gl)
    parts.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="7" fill="#2e9a6b"/>')
    # Inset (not to scale): the D7 plan's gears in order, each as an arrow with its length.
    cx, cy = px(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2))
    box_w, box_h = 300, 64 + 52 * len(gears)
    x0b, y0b = cx - box_w / 2, cy - box_h / 2 + 10
    parts.append(f'<rect x="{x0b:.0f}" y="{y0b:.0f}" width="{box_w}" height="{box_h}" rx="8" fill="#ffffff" '
                 f'stroke="#c9ced6" stroke-width="2"/>')
    parts.append(f'<text x="{cx:.0f}" y="{y0b + 34:.0f}" font-size="20" font-weight="700" fill="{INK}" '
                 f'text-anchor="middle">후진 · 전진 연결 (확대)</text>')
    for i, (gear, run_len) in enumerate(gears):
        y = y0b + 72 + 52 * i
        colour = ORANGE if gear < 0 else BLUE
        a, b = (x0b + 40, x0b + 150) if gear > 0 else (x0b + 150, x0b + 40)
        marker = 'gf-ah-o' if gear < 0 else 'gf-ah-b'
        parts.append(f'<line x1="{a:.0f}" y1="{y:.0f}" x2="{b:.0f}" y2="{y:.0f}" stroke="{colour}" stroke-width="6" '
                     f'marker-end="url(#{marker})"/>')
        word = '전진' if gear > 0 else '후진'
        parts.append(f'<text x="{x0b + 172:.0f}" y="{y + 7:.0f}" font-size="20" font-weight="700" fill="{colour}">'
                     f'{i + 1}. {word} {run_len:.2f} m</text>')
    lx, ly = px(((min(xs) + max(xs)) / 2, min(ys) - 0.55))
    parts.append(f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="21" font-weight="700" fill="#6b7480" '
                 f'text-anchor="middle">전진만 쓴 경로 (한 바퀴)</text>')
    tx, ty = px((0.70, 0.62))
    parts.append(f'<text x="{tx:.0f}" y="{ty:.0f}" font-size="20" fill="{INK}" text-anchor="middle">현재 위치</text>')
    meta = dict(forward_m=round(plans['forward']['length'], 2), d7_m=round(plans['d7']['length'], 2),
                d7_gear_changes=plans['d7']['gear_changes'],
                heading_fix_rad=round(goal.yaw_rad - start.yaw_rad, 3),
                goal_ahead_m=round(gl[0], 3), goal_left_m=round(gl[1], 3))
    label = (f'목적지 앞에서 방향 {abs(meta["heading_fix_rad"]):.3f} rad 를 맞추는 경로. 전진만 쓰면 회색 점선처럼 '
             f'{meta["forward_m"]:.1f} m 를 한 바퀴 돌고, 후진과 전진을 이으면 {meta["d7_m"]:.2f} m')
    return svg(width, height, ''.join(parts), label), meta


def main(repo):
    repo = Path(repo).resolve()
    assets = ROOT / 'figures'      # inlined into index.html by build_deck.py, not published as files
    assets.mkdir(exist_ok=True)
    meta = {}
    for name, make in (('52_reverse_obstacle.svg', reverse_obstacle), ('53_goal_fix.svg', goal_fix)):
        text, info = make(repo)
        (assets / name).write_text(text, encoding='utf-8')
        meta[name] = info
    print(json.dumps(meta, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
