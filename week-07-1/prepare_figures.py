#!/usr/bin/env python3
"""Draw the meeting deck's figures as PNG with matplotlib (conda base: numpy, matplotlib, PIL).

    python prepare_figures.py /path/to/forklift [PLANNER_SRC]
    python prepare_figures.py stages

Writes assets/ (published with the page; the deck font Noto Sans CJK is the system's noto-cjk):
1. 40_system.png -- slide 4, the system: sensors -> Jetson -> STM32 -> drive board -> motors,
   and the wireless parts below (hardware record and the week 5 circuit draft).
2. 41_structure.png -- slide 9, localization and the obstacle map as four lanes (position,
   drive permission, planning, delivery docking) into the path tracker (slam_pose, slam_link,
   obstacle_grid, drive_permission, planning_memory, scan_match / scan_docking).
3. 52_reverse_obstacle.png -- slide 12 left, the week 6 new-obstacle scene (measured chassis,
   seed 5, box during transport; videos-from-ws1/20261007_l8_measured_seed5_n1/plan_history.json)
   in the truck's frame at the stop (94.3 s replan): the live plan, the replan (reverse, then
   forward) and the tightest right turn from the stop at the planner's radius 1 / 0.29 m, whose
   rear-axle arc runs through the box (the body sweeps 3.05-4.15 m from the turn centre).
4. 53_goal_fix.png -- slide 12 right, the D7 test case (tests/unit/planning/test_d7_planner_options.py:
   l8_measured seed 1 + N1 stall replan, goal 1 cm ahead and 0.023 rad off) planned with the
   forward-only goal connection and with D7_PLANNER_OPTIONS (Reeds-Shepp, 4 m cap), both to scale.
   PLANNER_SRC is the robot repository's src/ to import (default REPO/src); the deck used the
   b66271f snapshot (git archive b66271f src).
5. assets/20_pipeline_stages_crop.png (`stages`) -- the week 3 pocket-detection figure
   (week-03/assets/20_pipeline_stages.png, drawn by forklift tools/deck/pipeline_stages.py from
   Gazebo scene s003) without its title band and step captions (rows 98-410; the step names are
   HTML). The small labels are redrawn for projection: the arrow captions are removed, the
   viewpoint tags are drawn larger, and the two colour legends move to the HTML legend.

Sizes are in slide canvas pixels (1280 x 720 deck) and saved at 2.5x.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
SCALE = 2.5                        # saved pixels per canvas pixel
BLUE, ORANGE, GREY, RED, INK, GREEN = '#2f74c0', '#c26a1a', '#9aa3ad', '#c0392b', '#1b1f24', '#2e9a6b'
UOS, MUTED, RULE = '#004094', '#5a5f66', '#c9c7c2'
TAG = {'fixed': ('확정', BLUE), 'buy': ('구매 예정', '#8c959e'), 'draft': ('설계 중', ORANGE),
       'reuse': ('기존 재사용', GREEN), 'plan': ('설계 반영 예정', ORANGE)}
FONT_REGULAR = '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'
FONT_BOLD = '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc'
LOADED = (1.56, 0.17, 0.40)        # planning footprint: ahead of / behind the rear axle, half width
PLAN_RADIUS = 1 / 0.29             # planner curvature limit (config/isaac_transport_measured.yaml)


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


# ---------------------------------------------------------------- drawing helpers
def mpl():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import patches
    from matplotlib.font_manager import FontProperties
    return plt, patches, FontProperties(fname=FONT_REGULAR), FontProperties(fname=FONT_BOLD)


def pt(px):
    """Canvas pixels -> points at 100 dpi."""
    return px * 0.72


class Canvas:
    """A figure in canvas pixels, y down (diagrams)."""

    def __init__(self, width, height):
        self.plt, self.patches, self.reg, self.bold = mpl()
        self.fig = self.plt.figure(figsize=(width / 100, height / 100), dpi=100)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, width)
        self.ax.set_ylim(height, 0)
        self.ax.axis('off')

    def text(self, x, y, s, size, colour=INK, bold=False, ha='left', va='center', **kw):
        self.ax.text(x, y, s, fontproperties=self.bold if bold else self.reg, fontsize=pt(size),
                     color=colour, ha=ha, va=va, **kw)

    def box(self, x, y, w, h, title, lines=(), tag=None, fill='#ffffff', edge='#44505c', dashed=False,
            title_size=24, line_size=20):
        self.ax.add_patch(self.patches.FancyBboxPatch(
            (x, y), w, h, boxstyle='round,pad=0,rounding_size=7', facecolor=fill, edgecolor=edge,
            linewidth=1.6, linestyle=(0, (5, 4)) if dashed else '-'))
        self.text(x + 14, y + 24, title, title_size, bold=True)
        first = y + 24 + title_size * 0.75 + 10
        if tag:   # its own row under the title, so a long title never runs under it
            word, colour = TAG[tag]
            tw = 16 * len(word) + 18
            self.ax.add_patch(self.patches.FancyBboxPatch(
                (x + 14, y + 46), tw, 26, boxstyle='round,pad=0,rounding_size=4', facecolor=colour,
                edgecolor='none'))
            self.text(x + 14 + tw / 2, y + 59, word, 16, colour='#ffffff', bold=True, ha='center')
            first = y + 46 + 26 + 6
        for i, line in enumerate(lines):
            self.text(x + 14, first + (line_size + 9) * i + line_size / 2 + 4, line, line_size, colour='#3d464f')

    def arrow(self, points, label=None, at=None, dashed=False, both=False, colour='#5d6670', ha='center',
              label_size=18):
        from matplotlib.patches import FancyArrowPatch
        from matplotlib.path import Path as MPath
        codes = [MPath.MOVETO] + [MPath.LINETO] * (len(points) - 1)
        style = '<|-|>' if both else '-|>'
        self.ax.add_patch(FancyArrowPatch(path=MPath(points, codes), arrowstyle=style, mutation_scale=18,
                                          color=colour, linewidth=2.2,
                                          linestyle=(0, (5, 4)) if dashed else '-', shrinkA=0, shrinkB=0))
        if label:
            self.text(at[0], at[1], label, label_size, colour='#3d464f', ha=ha)

    def save(self, name):
        ASSETS.mkdir(exist_ok=True)
        self.fig.savefig(ASSETS / name, dpi=100 * SCALE, facecolor='#ffffff')
        self.plt.close(self.fig)
        return name


# ---------------------------------------------------------------- slide 4
WIFI_LINE = 'Wi-Fi: 상태 · 지도만 전송'
ESTOP_LINE = 'Wi-Fi와 별도 · 신호 끊기면 정지'


def system():
    c = Canvas(1180, 520)
    for x, label in ((0, '센서'), (335, '상위 연산'), (690, '하위 제어'), (960, '구동')):
        c.text(x, 12, label, 20, colour=UOS, bold=True)
    c.box(0, 36, 270, 146, 'RGB-D 카메라', ['RealSense D435i', '캐리지 하단 (시뮬)'], 'fixed')
    c.box(0, 196, 270, 146, '2D LiDAR', ['RPLIDAR A2', '높이 1.05 m (시뮬)'], 'fixed')
    c.box(335, 36, 265, 306, 'Jetson Orin Nano', ['ROS 2 Jazzy', '팔레트 · 포켓 인식', 'SLAM (slam_toolbox)',
                                                  '경로 계획 (Hybrid A*)', '경로 추종 · 삽입 추적'], 'buy')
    c.box(690, 36, 200, 306, 'STM32 보드', ['속도 · 조향 · 승강', '엔코더 읽기', '비상 차단'], 'draft')
    c.box(960, 36, 220, 150, '구동 보드', ['DRV8244 × 3', 'MT6701 엔코더'], 'draft')
    c.box(960, 210, 220, 132, '모터 3개', ['12 V 배터리'], 'reuse')
    c.arrow([(270, 110), (335, 110)], 'USB 3', (302, 90))
    c.arrow([(270, 270), (335, 270)], 'USB', (302, 250))
    c.arrow([(600, 190), (690, 190)], '명령\n상태', (645, 156), both=True)
    c.arrow([(890, 110), (960, 110)], both=True)
    c.arrow([(1070, 186), (1070, 210)], both=True)
    # wireless (week 6 team memo: not yet designed in)
    c.ax.add_patch(c.patches.FancyBboxPatch((0, 372), 1180, 146, boxstyle='round,pad=0,rounding_size=8',
                                            facecolor='#fff8f0', edgecolor='#e7c9a8', linewidth=1.2))
    c.text(18, 434, '무선', 24, colour=ORANGE, bold=True)
    c.text(18, 466, '(추가 설계)', 19, colour=ORANGE)
    c.box(335, 386, 300, 122, '감시 PC', [WIFI_LINE], 'plan', edge=ORANGE, dashed=True)
    c.box(830, 386, 350, 122, '무선 비상정지', [ESTOP_LINE], 'plan', edge=ORANGE, dashed=True)
    c.arrow([(467, 386), (467, 342)], 'Wi-Fi', (480, 364), dashed=True, both=True, colour=ORANGE, ha='left')
    c.arrow([(925, 386), (925, 150), (960, 150)], '출력 차단', (937, 357), dashed=True, colour=ORANGE,
            ha='left', label_size=17)
    return c.save('40_system.png')


# ---------------------------------------------------------------- slide 9
def structure():
    c = Canvas(1180, 450)
    cols = {'in': (120, 240), 'proc': (405, 270), 'out': (720, 280)}
    for key, label in (('in', '입력'), ('proc', '처리'), ('out', '판단 · 결과')):
        c.text(cols[key][0], 12, label, 20, colour=UOS, bold=True)
    c.text(1040, 12, '제어', 20, colour=UOS, bold=True)
    lanes = [  # lane, input, process, output (title, line, fill, edge)
        ('위치', ('엔코더 + LiDAR', '바퀴 · 조향각 · 스캔'), ('오도메트리 + SLAM', '0.45 m · 0.5 rad마다 보정'),
         ('제어 위치', '응답 0.25 s 끊기면 정지', '#eef3fa', BLUE)),
        ('장애물', ('LiDAR 스캔', '10 Hz · 높이 1.05 m'), ('장애물 격자', '오래된 스캔일수록 크게'),
         ('주행 허가', '멈추는 궤적이 비어야 주행', '#fff4ea', ORANGE)),
        ('경로', ('장애물 기억', '+ SLAM 지도'), ('Hybrid A*', '전진 · 후진 호 탐색'),
         ('경로', '전진 · 후진 구간 포함', '#ffffff', '#44505c')),
        ('하역', ('등록 스캔', '+ 지금 스캔'), ('ICP 정합', '점–선 거리'),
         ('하역 위치 보정', '목적지 직선 다시 그림', '#ffffff', '#44505c')),
    ]
    top, step, h = 34, 104, 90
    for i, (lane, inp, proc, out) in enumerate(lanes):
        y = top + i * step
        c.text(0, y + h / 2, lane, 22, colour=UOS, bold=True)
        c.box(cols['in'][0], y, cols['in'][1], h, inp[0], [inp[1]], title_size=22, line_size=19)
        c.box(cols['proc'][0], y, cols['proc'][1], h, proc[0], [proc[1]], title_size=22, line_size=19)
        c.box(cols['out'][0], y, cols['out'][1], h, out[0], [out[1]], fill=out[2], edge=out[3],
              title_size=22, line_size=19)
        c.arrow([(cols['in'][0] + cols['in'][1], y + h / 2), (cols['proc'][0], y + h / 2)])
        c.arrow([(cols['proc'][0] + cols['proc'][1], y + h / 2), (cols['out'][0], y + h / 2)])
        c.arrow([(cols['out'][0] + cols['out'][1], y + h / 2), (1040, y + h / 2)])
    c.box(1040, top, 140, 3 * step + h, '경로 추종', ['속도 · 조향', '명령', '→ STM32'], fill='#eef3fa', edge=BLUE,
          title_size=22, line_size=19)
    return c.save('41_structure.png')


# ---------------------------------------------------------------- slide 12
class Plot:
    """A to-scale plan view in metres inside a canvas of the given pixel size."""

    def __init__(self, width, height, xlim, ylim):
        self.plt, self.patches, self.reg, self.bold = mpl()
        self.fig = self.plt.figure(figsize=(width / 100, height / 100), dpi=100)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)
        self.ax.set_aspect('equal', adjustable='datalim')
        self.ax.axis('off')

    def text(self, x, y, s, size, colour=INK, bold=True, ha='center', va='center'):
        self.ax.text(x, y, s, fontproperties=self.bold if bold else self.reg, fontsize=pt(size),
                     color=colour, ha=ha, va=va)

    def line(self, pts, colour, width, dashed=False, arrow=False):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self.ax.plot(xs, ys, color=colour, linewidth=width, solid_capstyle='round',
                     linestyle=(0, (4, 3)) if dashed else '-')
        if arrow and len(pts) > 1:
            self.ax.annotate('', xy=pts[-1], xytext=pts[-2],
                             arrowprops=dict(arrowstyle='-|>', color=colour, lw=width, mutation_scale=22))

    def body(self, x, y, yaw, edge=INK, fill='#eef3fa', dashed=False, footprint=LOADED):
        front, rear, half = footprint
        c, s = math.cos(yaw), math.sin(yaw)
        pts = [(x + c * a - s * b, y + s * a + c * b)
               for a, b in ((front, half), (-rear, half), (-rear, -half), (front, -half))]
        self.ax.add_patch(self.patches.Polygon(pts, closed=True, facecolor=fill, edgecolor=edge, linewidth=2,
                                               linestyle=(0, (4, 3)) if dashed else '-'))
        tip = (x + c * (front + 0.35), y + s * (front + 0.35))
        self.ax.annotate('', xy=tip, xytext=(x + c * front, y + s * front),
                         arrowprops=dict(arrowstyle='-|>', color=edge, lw=2, mutation_scale=16))

    def square(self, x, y, size, yaw, edge, fill):
        c, s = math.cos(yaw), math.sin(yaw)
        h = size / 2
        pts = [(x + c * a - s * b, y + s * a + c * b) for a, b in ((h, h), (-h, h), (-h, -h), (h, -h))]
        self.ax.add_patch(self.patches.Polygon(pts, closed=True, facecolor=fill, edgecolor=edge, linewidth=2))

    def scale_bar(self, x, y, metres=1.0, dy=0.28):
        self.ax.plot([x, x + metres], [y, y], color=MUTED, linewidth=3, solid_capstyle='butt')
        self.text(x + metres / 2, y - dy, f'{metres:g} m', 18, colour=MUTED, bold=False)

    def save(self, name):
        ASSETS.mkdir(exist_ok=True)
        self.fig.savefig(ASSETS / name, dpi=100 * SCALE, facecolor='#ffffff')
        self.plt.close(self.fig)
        return name


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
    # Frame: truck heading to the right (+x), its left up (+y).
    xlim, ylim = (-2.6, 6.0), (-3.9, 1.5)
    p = Plot(580, 390, xlim, ylim)

    def inside(q):
        return xlim[0] <= q[0] <= xlim[1] and ylim[0] <= q[1] <= ylim[1]

    # The live plan from the stop is the tightest right turn: within 1.7 cm of the rear-axle arc
    # about (0, -1 / 0.29) over its first 4 m, and that arc runs through the box.
    p.line([q for q in old if inside(q)], GREY, 3.5, dashed=True)
    reverse = [pts for gear, pts in runs if gear < 0][0]
    forward = [pts for gear, pts in runs if gear > 0][0]
    p.line(reverse, ORANGE, 5, arrow=True)
    p.line([q for q in forward if inside(q)][:-2], BLUE, 5, arrow=True)
    p.body(0.0, 0.0, 0.0)
    p.square(box[0], box[1], spawn[4][0], spawn[3] - yaw0, RED, '#f6d5d0')
    reverse_len, forward_len = length(reverse), length(forward)
    R = PLAN_RADIUS
    p.text(0.75, 0.9, '멈춘 위치', 23)
    p.text(box[0] + 0.5, box[1] + 0.05, '새 상자', 23, colour=RED, ha='left')
    p.text(-1.3, 0.75, f'① 후진 {reverse_len:.2f} m', 23, colour=ORANGE)
    p.text(-0.4, -2.3, '② 전진', 23, colour=BLUE, ha='right')
    p.text(3.5, -1.05, '원래 경로', 22, colour='#6b7480', ha='left')
    p.text(3.5, -1.6, '가장 작게 꺾어도', 20, colour='#6b7480', bold=False, ha='left')
    p.text(3.5, -2.08, '상자 위를 지남', 20, colour='#6b7480', bold=False, ha='left')
    p.scale_bar(-2.3, -3.25)
    meta = dict(reverse_m=round(reverse_len, 2), forward_m=round(forward_len, 2),
                box_ahead_m=round(box[0], 2), box_right_m=round(-box[1], 2),
                stop_turn_box_offset_m=round(math.hypot(box[0], box[1] + R) - R, 3),
                new_min_to_box_m=round(min(math.hypot(q[0] - box[0], q[1] - box[1]) for q in new), 2))
    return p.save('52_reverse_obstacle.png'), meta


def goal_fix(repo, planner_src=None):
    sys.path.insert(0, str(planner_src or repo / 'src'))
    import numpy as np
    from forklift_core.planning import Bounds, Footprint, Pose2D
    from forklift_core.planning.hybrid_astar import PlannerConfig, plan_hybrid_astar
    from forklift_core.planning.pallet_mission import D7_PLANNER_OPTIONS
    bounds = Bounds(-30.0, 10.0, -30.0, 10.0)
    loaded = Footprint(*LOADED)
    measured = dict(curvature_limit_inv_m=0.29, primitive_length_m=0.25, max_expansions=30000, clearance_m=0.10)
    start, goal = Pose2D(-7.848, -18.669, -1.422), Pose2D(-7.851, -18.681, -1.399)
    plans = {}
    for name, config in (('forward', PlannerConfig(**measured)),
                         ('d7', PlannerConfig(**measured, **D7_PLANNER_OPTIONS))):
        result = plan_hybrid_astar(start, goal, [], loaded, bounds, config)
        assert result.success, name
        d = np.asarray(result.directions)
        plans[name] = dict(poses=np.asarray(result.poses)[:, :2].tolist(), directions=d.tolist(),
                           length=float(result.length_m), gear_changes=int((d[1:] != d[:-1]).sum()))
    c, s = math.cos(start.yaw_rad), math.sin(start.yaw_rad)

    def local(q):
        return (c * (q[0] - start.x_m) + s * (q[1] - start.y_m), -s * (q[0] - start.x_m) + c * (q[1] - start.y_m))

    loop = [local(q) for q in plans['forward']['poses']]
    d7 = [local(q) for q in plans['d7']['poses']]
    gl = local((goal.x_m, goal.y_m))
    xs, ys = [q[0] for q in loop], [q[1] for q in loop]
    p = Plot(580, 390, (min(xs) - 0.9, max(xs) + 0.9), (min(ys) - 1.0, max(ys) + 0.9))
    p.ax.set_position([0.0, 0.0, 0.54, 1.0])
    p.line(loop, GREY, 3, dashed=True, arrow=True)
    p.body(0.0, 0.0, 0.0)
    p.ax.add_patch(p.patches.Rectangle((-0.45, -0.75), 2.6, 1.5, facecolor='none', edgecolor=MUTED,
                                       linewidth=1.2, linestyle=(0, (2, 2))))
    mid_x, mid_y = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    p.text(mid_x, mid_y + 0.5, '전진만', 23, colour='#6b7480')
    p.text(mid_x, mid_y - 0.5, f'한 바퀴 {plans["forward"]["length"]:.1f} m', 23, colour='#6b7480')
    p.scale_bar(min(xs) - 0.6, min(ys) - 0.55)
    # The enlarged spot: same truck, the two moves of the D7 plan to scale (side by side).
    inset = p.fig.add_axes([0.57, 0.08, 0.43, 0.84])
    inset.set_xlim(-0.55, 2.35)
    inset.set_ylim(-1.45, 1.45)
    inset.set_aspect('equal', adjustable='datalim')
    inset.axis('off')
    main_ax, p.ax = p.ax, inset
    runs = split_by_gear(d7, 0.0)
    fwd = [pts for gear, pts in runs if gear > 0][0]
    rev = [pts for gear, pts in runs if gear < 0][0]
    p.body(0.0, 0.0, 0.0)
    p.ax.plot([gl[0]], [gl[1]], 'o', color=GREEN, markersize=8, zorder=5)
    p.line([(q[0], 0.62) for q in fwd], BLUE, 5, arrow=True)
    p.line([(q[0], -0.62) for q in rev], ORANGE, 5, arrow=True)
    p.text(0.25, 1.0, f'① 앞 {length(fwd):.2f} m', 22, colour=BLUE)
    p.text(0.25, -1.0, f'② 뒤 {length(rev):.2f} m', 22, colour=ORANGE)
    p.text(0.9, 1.4, '같은 자리 확대', 19, colour=MUTED, bold=False)
    p.text(0.9, -1.42, f'방향 {math.degrees(abs(goal.yaw_rad - start.yaw_rad)):.1f}° 맞춤', 19,
           colour=MUTED, bold=False)
    p.scale_bar(1.6, -0.62, 0.5, dy=0.14)
    p.ax = main_ax
    meta = dict(forward_m=round(plans['forward']['length'], 2), d7_m=round(plans['d7']['length'], 2),
                d7_forward_m=round(length(fwd), 2), d7_reverse_m=round(length(rev), 2),
                d7_gear_changes=plans['d7']['gear_changes'],
                heading_fix_rad=round(goal.yaw_rad - start.yaw_rad, 3),
                goal_ahead_m=round(gl[0], 3), goal_left_m=round(gl[1], 3))
    return p.save('53_goal_fix.png'), meta


# ---------------------------------------------------------------- slide 7 (week 3 figure)
# Week 3 figure geometry (forklift tools/deck/pipeline_stages.py): four 385 px panels with 88 px
# arrow gaps, panels pasted at y 100 of the canvas; the crop keeps canvas rows 98-410.
PANEL_W, GAP_W, CROP_ROWS = 385, 88, (98, 410)   # 410: below it only floor, and the table needs the room
TAG_FONT = '/usr/share/fonts/TTF/NanumGothic.ttf'
VIEWS = ('카메라에서 본 모습', '위에서 본 모습', '앞면을 좌우로 나눈 결과', '카메라에서 본 모습')


def pocket_stages():
    from PIL import Image, ImageDraw, ImageFont
    src = ROOT.parent / 'week-03/assets/20_pipeline_stages.png'
    img = Image.open(src).convert('RGB')
    img = img.crop((0, CROP_ROWS[0], img.width, CROP_ROWS[1]))
    d = ImageDraw.Draw(img)
    new = ImageFont.truetype(TAG_FONT, 26)
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
    out = ASSETS / '20_pipeline_stages_crop.png'
    img.save(out, optimize=True)
    print(out.name, img.size)


def main(repo, planner_src=None):
    repo = Path(repo).resolve()
    meta = {'40_system.png': system(), '41_structure.png': structure()}
    for name, make in (('52_reverse_obstacle.png', lambda: reverse_obstacle(repo)),
                       ('53_goal_fix.png', lambda: goal_fix(repo, planner_src))):
        _, info = make()
        meta[name] = info
    print(json.dumps(meta, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'stages':
        pocket_stages()
    else:
        main(sys.argv[1], Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None)
