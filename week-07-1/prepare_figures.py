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

    python prepare_figures.py stages

3. assets/20_pipeline_stages_crop.png -- the week 3 pocket-detection figure
   (week-03/assets/20_pipeline_stages.png, drawn by forklift tools/deck/pipeline_stages.py from
   Gazebo scene s003) without its title band and step captions (rows 98-410; the step names are
   HTML). The small labels are redrawn for projection: the arrow captions are removed, the
   viewpoint tags are drawn larger, and the two colour legends move to the HTML legend.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLUE, ORANGE, GREY, RED, INK, GREEN = '#2f74c0', '#c26a1a', '#9aa3ad', '#c0392b', '#1b1f24', '#2e9a6b'
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
        for name, colour in (('ah', INK), ('ah-b', BLUE), ('ah-o', ORANGE), ('ah-g', '#2e9a6b'))) + '</defs>'


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
                                     ((-1.05, 0.62), f'① 후진 {reverse_len:.2f} m', ORANGE, 'middle'),   # above the box's left edge
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
    gl = local((goal.x_m, goal.y_m))
    width, height = 640, 400
    parts = [arrows('gf')]

    # Left: the forward-only plan, to scale -- the whole loop with the truck at its start.
    xs, ys = [p[0] for p in loop], [p[1] for p in loop]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) + 2.2
    lsc = 220 / span
    lcx, lcy = 125, 215

    def lp(q):
        return (lcx + (q[0] - (min(xs) + max(xs)) / 2) * lsc, lcy - (q[1] - (min(ys) + max(ys)) / 2) * lsc)

    parts.append(f'<text x="{lcx}" y="40" font-size="22" font-weight="700" fill="#6b7480" text-anchor="middle">전진만</text>')
    parts.append(polyline([lp(q) for q in loop], GREY, 4, '9 7'))
    parts.append(truck(0.0, 0.0, 0.0, lp, 'gf', fill='#eef3fa'))
    gx, gy = lp(gl)
    parts.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="6" fill="{GREEN}"/>')
    parts.append(f'<text x="{lcx}" y="372" font-size="21" fill="#44505c" text-anchor="middle">한 바퀴 {plans["forward"]["length"]:.1f} m</text>')
    parts.append(f'<line x1="262" y1="60" x2="262" y2="360" stroke="#e3e6ea" stroke-width="2"/>')

    # Right: the forward-and-reverse connection as a concept (angle exaggerated; the drawn tilt is
    # not the case's sign, so the moves are named one way / the other way): start pose
    # (tilted, dashed) and end pose (on the goal heading) at the same rear axle; the two moves,
    # forward steering right then reverse steering left, both lower the heading
    # (curvature x signed travel).
    rcx = 460
    parts.append(f'<text x="{rcx}" y="40" font-size="22" font-weight="700" fill="{INK}" text-anchor="middle">전진 · 후진 (개념도)</text>')
    sc, tilt = 105.0, math.radians(16)
    ox, oy = 300, 175

    def ip(q):
        return (ox + q[0] * sc, oy - q[1] * sc)

    def body(yaw, colour, fill, dash=None):
        front, rear, half = 1.56, 0.17, 0.30
        mid = (front - rear) / 2
        c_, s_ = math.cos(yaw), math.sin(yaw)
        pts = [ip((mid * c_ + c_ * u - s_ * v, mid * s_ + s_ * u + c_ * v))
               for u, v in (((front + rear) / 2, half), (-(front + rear) / 2, half),
                            (-(front + rear) / 2, -half), ((front + rear) / 2, -half))]
        d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        extra = f' stroke-dasharray="{dash}"' if dash else ''
        tip0, tip1 = ip((front * c_, front * s_)), ip(((front + 0.3) * c_, (front + 0.3) * s_))
        return (f'<polygon points="{d}" fill="{fill}" stroke="{colour}" stroke-width="2.5"{extra}/>'
                f'<line x1="{tip0[0]:.1f}" y1="{tip0[1]:.1f}" x2="{tip1[0]:.1f}" y2="{tip1[1]:.1f}" '
                f'stroke="{colour}" stroke-width="3" marker-end="url(#gf-{"ah-g" if colour == GREEN else "ah"})"/>')

    g0, g1 = ip((-0.25, 0.0)), ip((3.15, 0.0))
    parts.append(f'<line x1="{g0[0]:.1f}" y1="{g0[1]:.1f}" x2="{g1[0]:.1f}" y2="{g1[1]:.1f}" stroke="{GREEN}" '
                 f'stroke-width="2" stroke-dasharray="7 6"/>')
    parts.append(body(tilt, '#8c959e', 'none', dash='6 5'))
    parts.append(body(0.0, GREEN, '#eaf6f0'))
    t1 = ip((1.95 * math.cos(tilt), 1.95 * math.sin(tilt)))
    parts.append(f'<text x="{t1[0] + 6:.0f}" y="{t1[1] - 4:.0f}" font-size="19" fill="#6b7480">처음</text>')
    parts.append(f'<text x="{g1[0]:.0f}" y="{g1[1] + 26:.0f}" font-size="19" fill="{GREEN}" text-anchor="end">목표 방향</text>')
    ya, yb = 268, 312
    xa, xb = 286, 380
    parts.append(f'<path d="M{xa},{ya - 8} Q{(xa + xb) / 2},{ya + 6} {xb},{ya + 8}" fill="none" stroke="{BLUE}" '
                 f'stroke-width="5" marker-end="url(#gf-ah-b)"/>')
    parts.append(f'<text x="{xb + 16}" y="{ya + 9}" font-size="20" font-weight="700" fill="{BLUE}">① 한쪽으로 꺾으며 전진</text>')
    parts.append(f'<path d="M{xb},{yb + 8} Q{(xa + xb) / 2},{yb + 6} {xa},{yb - 8}" fill="none" stroke="{ORANGE}" '
                 f'stroke-width="5" marker-end="url(#gf-ah-o)"/>')
    parts.append(f'<text x="{xb + 16}" y="{yb + 9}" font-size="20" font-weight="700" fill="{ORANGE}">② 반대로 꺾으며 후진</text>')
    parts.append(f'<text x="{rcx}" y="372" font-size="21" fill="#44505c" text-anchor="middle">앞뒤 {plans["d7"]["length"]:.1f} m · 각도는 크게 그림</text>')

    meta = dict(forward_m=round(plans['forward']['length'], 2), d7_m=round(plans['d7']['length'], 2),
                d7_gear_changes=plans['d7']['gear_changes'],
                heading_fix_rad=round(goal.yaw_rad - start.yaw_rad, 3),
                goal_ahead_m=round(gl[0], 3), goal_left_m=round(gl[1], 3))
    label = (f'목적지 앞에서 방향 {abs(meta["heading_fix_rad"]):.3f} rad 를 맞추는 경로. 전진만 쓰면 '
             f'{meta["forward_m"]:.1f} m 를 한 바퀴 돌고, 한쪽으로 꺾으며 전진한 뒤 반대로 꺾으며 후진하면 '
             f'{meta["d7_m"]:.2f} m 로 제자리에서 방향이 맞는다(개념도)')
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


# Week 3 figure geometry (forklift tools/deck/pipeline_stages.py): four 385 px panels with 88 px
# arrow gaps, panels pasted at y 100 of the canvas; the crop keeps canvas rows 98-432.
PANEL_W, GAP_W, CROP_ROWS = 385, 88, (98, 410)   # 410: below it only floor, and the table needs the room
TAG_FONT = '/usr/share/fonts/TTF/NanumGothic.ttf'
VIEWS = ('카메라에서 본 모습', '위에서 본 모습', '앞면을 좌우로 나눈 결과', '카메라에서 본 모습')


def pocket_stages():
    from PIL import Image, ImageDraw, ImageFont
    src = ROOT.parent / 'week-03/assets/20_pipeline_stages.png'
    img = Image.open(src).convert('RGB')
    img = img.crop((0, CROP_ROWS[0], img.width, CROP_ROWS[1]))
    d = ImageDraw.Draw(img)
    old, new = ImageFont.truetype(TAG_FONT, 19), ImageFont.truetype(TAG_FONT, 26)
    for i, view in enumerate(VIEWS):
        x = i * (PANEL_W + GAP_W)
        if i in (1, 2):   # flat panel background: clear both old tag rows (view + colour legend)
            d.rectangle([x + 6, 10, x + PANEL_W - 6, 80], fill=(26, 29, 36))
        w = d.textlength(view, font=new)
        d.rectangle([x + 8, 10, x + 8 + w + 16, 10 + 26 + 11], fill=(16, 18, 23))
        d.text((x + 16, 14), view, font=new, fill=(232, 236, 244))
        if i < 3:         # the arrow's caption (15 px) above the arrow in the gap
            ax = x + PANEL_W
            d.rectangle([ax + 1, 120, ax + GAP_W - 1, 155], fill=(18, 20, 24))
    out = ROOT / 'assets/20_pipeline_stages_crop.png'
    img.save(out, optimize=True)
    print(out.name, img.size)


if __name__ == '__main__':
    if sys.argv[1] == 'stages':
        pocket_stages()
    else:
        main(sys.argv[1])
