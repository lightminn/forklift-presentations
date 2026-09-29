"""Build the week 5 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 5 has two strands and keeps them apart on screen. The main path is the
physical chassis (measurement, wiring), following the roadmap. The simulation
slides are a technology demonstration: they show what the Isaac factory hall and
an offline 2D LiDAR SLAM replay can do, not the direction the project has
committed to. Every demonstration slide carries the same tag and ends with what
has to be decided on the physical robot.

Slides 3-4 are placeholders until the chassis measurements arrive. The SLAM
videos come from the ws1 rerun 20260928_week05_replay (the 2026-09-26 Isaac
records replayed through slam_toolbox again); its twelve evaluations match the
2026-09-26 table to the third decimal except one odometry value (0.806 vs
0.807 m), so the numbers below are unchanged.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
MAP = 'docs/plans/2026-09-11-development-roadmap.md'
STATUS = 'docs/plans/2026-09-17-project-status-and-next-steps.md'
INTAKE = 'docs/validation/2026-09-23-chassis-intake.md'
FACTORY = 'docs/validation/2026-09-26-factory-hall-and-isaac-slam.md'
FACTORY_PLAN = 'docs/plans/2026-09-26-factory-hall-and-isaac-slam.md'
LIDAR_CFG = 'config/isaac_slam_lidar.yaml'
MODEL = 'sim/models/dls08_provisional/parameters.yaml'
VIEWS = 'docs/validation/2026-09-23-isaac-multiview-recording.md'
ADR3 = 'docs/decisions/0003-target-selection-and-blind-zone-insertion.md'
FEEDBACK = 'docs/references/week4_feedback.md'
HW = 'docs/hardware.md'
D435I = 'https://www.realsenseai.com/products/depth-camera-d435i/'
CROWN = 'https://patents.google.com/patent/US9990535B2/en'
ADAPT = 'https://arxiv.org/html/2503.14331v1'
slides = []

DEMO_TAG = ('<div class="demo-tag"><b>기술 실증</b> · Isaac Sim 합성 장면 · '
            '로봇 제어에 시뮬레이터 정답 위치 사용</div>')
SLAM_BLUE, ODOM_ORANGE = '#2f74c0', '#c26a1a'   # validated pair (dataviz)


def add(label, title, seconds, body, notes, sources, foot='측정 결과'):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def figure(src, alt, caption, *, video=None, cls='wide'):
    if video is None:
        video = src.rsplit('.', 1)[-1].lower() in {'mp4', 'webm'}
    poster = src.rsplit('.', 1)[0].replace('_seed16', '') + '_poster.jpg'
    poster_attr = f' poster="assets/{poster}"' if (ROOT / 'assets' / poster).exists() else ''
    tag = (f'<video class="media" src="assets/{src}"{poster_attr} autoplay loop muted playsinline '
           f'aria-label="{escape(alt, quote=True)}"></video>' if video else
           f'<img class="media" src="assets/{src}" alt="{escape(alt, quote=True)}">')
    cap = f'<figcaption class="small muted">{caption}</figcaption>' if caption else ''
    return f'<figure class="shot {cls}">{tag}{cap}</figure>'


def placeholder(what, detail, cls='grow'):
    """A visible slot for material that does not exist yet."""
    return (f'<div class="placeholder {cls}"><b>{what}</b>'
            f'<span>{detail}</span></div>')


# ----------------------------------------------------------------- charts
# Drawn from the recorded numbers below, so the bars cannot drift from the
# source tables. Colours: one series = SLAM blue; the SLAM/odometry pair was
# checked with the dataviz validator (light surface, all checks pass).

# slam_toolbox replays of the 0.5 m/s survey loop, start-pose-aligned ATE in
# metres, layout seeds 0-4 (validation record section 6): (seed, clean, noisy).
REPLAY_ATE = {
    'SLAM': [(0, 0.025, 0.062), (1, 0.040, 0.050), (2, 0.039, 0.032), (3, 0.046, 0.084), (4, 0.047, 0.045)],
    '바퀴·조향 추정': [(0, 0.576, 0.651), (1, 0.806, 0.757), (2, 0.807, 0.832), (3, 0.868, 0.853), (4, 0.806, 0.818)],
}


def _swarm(xs, radius=6, step=11):
    """Vertical offsets so no two dots overlap: each dot takes the first lane
    (0, -step, +step, -2 step, ...) with no dot closer than 2 radius in x."""
    lanes, placed = [0], []
    for k in range(1, 6):
        lanes += [-k * step, k * step]
    for cx in sorted(xs):
        for dy in lanes:
            if all(abs(cx - px) >= 2 * radius or dy != pdy for px, pdy in placed):
                placed.append((cx, dy))
                break
    return placed


def ate_chart():
    """Both rows start at the same zero line: a bar to the ten-run mean with
    the individual runs as dots on it, so the two rows read as one scale."""
    left, width, xmax = 170, 1150 - 170, 0.9

    def x(v):
        return left + v / xmax * width
    colours = {'SLAM': SLAM_BLUE, '바퀴·조향 추정': ODOM_ORANGE}
    parts = []
    for tick in (0, 0.2, 0.4, 0.6, 0.8):
        parts.append(f'<line x1="{x(tick):.1f}" y1="44" x2="{x(tick):.1f}" y2="256" stroke="#e3e6ea" stroke-width="1.5"/>'
                     f'<text x="{x(tick):.1f}" y="280" text-anchor="middle" font-size="19" fill="#44505c">{tick:.1f} m</text>')
    parts.append(f'<line x1="{left}" y1="44" x2="{left}" y2="256" stroke="#44505c" stroke-width="2.5"/>')
    for row, (name, runs) in enumerate(REPLAY_ATE.items()):
        y = 92 + row * 118
        colour = colours[name]
        values = [c for _, c, _ in runs] + [n for _, _, n in runs]
        mean = sum(values) / len(values)
        parts.append(f'<text x="{left - 20}" y="{y + 8}" text-anchor="end" font-size="23" font-weight="700" fill="#1b1f24">{name}</text>')
        parts.append(f'<rect x="{left}" y="{y - 36}" width="{x(mean) - left:.1f}" height="72" rx="4" fill="{colour}" opacity="0.28"/>')
        parts.append(f'<line x1="{x(mean):.1f}" y1="{y - 38}" x2="{x(mean):.1f}" y2="{y + 38}" stroke="{colour}" stroke-width="3"/>')
        for cx, dy in _swarm([x(v) for v in values]):
            parts.append(f'<circle cx="{cx:.1f}" cy="{y + dy}" r="6" fill="{colour}" stroke="#fff" stroke-width="1.5"/>')
        if x(mean) - left < 140:   # short bar: label beside the dots
            lx, ly, anchor = x(max(values)) + 18, y + 8, 'start'
        else:                      # long bar: label above its mean line
            lx, ly, anchor = x(mean), y - 42, 'middle'
        parts.append(f'<text x="{lx:.1f}" y="{ly}" text-anchor="{anchor}" font-size="22" font-weight="700" fill="#1b1f24">평균 {mean:.2f} m</text>')
    note = (f'<text x="{left}" y="24" font-size="19" fill="#44505c">5개 배치(주행 궤적 3종) × 잡음 2조건 · 막대: 10회 평균 · '
            f'점: 재생 1회 위치 오차(RMSE = 제곱평균제곱근, 출발 자세 정렬)</text>')
    return (f'<svg class="budget" viewBox="0 0 1200 290" role="img" aria-label="116 m 지도 작성 주행 재생 10회의 위치 오차. '
            f'같은 0 기준 축에서 SLAM 평균 0.05 m, 바퀴·조향 추정 평균 0.78 m">'
            f'<g font-family="var(--uos-font)">{note}{"".join(parts)}</g></svg>')


# ----------------------------------------------------------------- week 5 visuals
# Drawn from assets/data_*.json, which prepare_data.py extracts from the Isaac
# records and the slam_toolbox replays. The deck build itself stays stdlib-only.
DIR_BLUE, CAM_ORANGE, STOP_GREEN = SLAM_BLUE, ODOM_ORANGE, '#2e9a6b'   # validated trio


def _data(name):
    return json.loads((ROOT / 'assets' / name).read_text())


def badge(text='기술 실증 · Isaac Sim'):
    return f'<span class="badge">{text}</span>'


def trajectory_anim():
    """Top view of the survey loop: truth, SLAM and wheel-only estimate drawn
    together, so the wheel-only path is seen drifting away."""
    d = _data('data_survey_seed0.json')
    pts = d['truth'] + d['slam'] + d['odom']
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    size, pad = 560, 20
    scale = (size - 2 * pad) / max(x1 - x0, y1 - y0)
    def path(seq):
        return 'M' + ' L'.join(f'{pad + (x - x0) * scale:.1f},{size - pad - (y - y0) * scale:.1f}' for x, y in seq)
    end = d['odom'][-1]
    ex, ey = pad + (end[0] - x0) * scale, size - pad - (end[1] - y0) * scale
    return f"""<svg class="diagram grow traj" viewBox="0 0 {size} {size}" role="img" aria-label="위에서 본 116 m 지도 작성 경로. 실제 경로 위로 SLAM 추정이 겹치고, 바퀴·조향 추정은 점점 벗어난다">
<path d="{path(d['truth'])}" fill="none" stroke="#c9ced4" stroke-width="12" stroke-linejoin="round"/>
<path class="draw" pathLength="1" d="{path(d['odom'])}" fill="none" stroke="{ODOM_ORANGE}" stroke-width="4" stroke-linejoin="round"/>
<path class="draw" pathLength="1" d="{path(d['slam'])}" fill="none" stroke="{SLAM_BLUE}" stroke-width="4" stroke-linejoin="round"/>
<circle class="endmark" cx="{ex:.1f}" cy="{ey:.1f}" r="9" fill="{ODOM_ORANGE}"/>
</svg>"""


def ate_compact():
    """Ten replays per row on one zero line, sized for a half-width column."""
    left, width, xmax = 128, 440, 0.9
    def x(v):
        return left + v / xmax * width
    colours = {'SLAM': SLAM_BLUE, '바퀴·조향 추정': ODOM_ORANGE}
    labels = {'SLAM': 'SLAM', '바퀴·조향 추정': '바퀴·조향'}
    parts = []
    for tick in (0, 0.4, 0.8):
        parts.append(f'<line x1="{x(tick):.1f}" y1="30" x2="{x(tick):.1f}" y2="236" stroke="#e3e6ea" stroke-width="1.5"/>'
                     f'<text x="{x(tick):.1f}" y="262" text-anchor="middle" font-size="20" fill="#44505c">{tick * 100:.0f} cm</text>')
    parts.append(f'<line x1="{left}" y1="30" x2="{left}" y2="236" stroke="#44505c" stroke-width="2.5"/>')
    for row, (name, runs) in enumerate(REPLAY_ATE.items()):
        y = 80 + row * 104
        values = [c for _, c, _ in runs] + [n for _, _, n in runs]
        mean = sum(values) / len(values)
        colour = colours[name]
        parts.append(f'<text x="{left - 16}" y="{y + 8}" text-anchor="end" font-size="23" font-weight="700" fill="#1b1f24">{labels[name]}</text>')
        parts.append(f'<rect x="{left}" y="{y - 34}" width="{x(mean) - left:.1f}" height="68" rx="4" fill="{colour}" opacity="0.28"/>')
        for cx, dy in _swarm([x(v) for v in values], radius=5, step=10):
            parts.append(f'<circle cx="{cx:.1f}" cy="{y + dy}" r="5" fill="{colour}" stroke="#fff" stroke-width="1.2"/>')
        lx = x(max(values)) + 14 if x(mean) - left < 140 else x(mean) - 8
        anchor = 'start' if x(mean) - left < 140 else 'end'
        ly = y + 8 if anchor == 'start' else y - 44
        parts.append(f'<text x="{lx:.1f}" y="{ly}" text-anchor="{anchor}" font-size="24" font-weight="700" fill="#1b1f24">{mean * 100:.0f} cm</text>')
    return (f'<svg class="diagram" viewBox="0 0 600 272" role="img" aria-label="재생 10회 위치 오차: SLAM 평균 0.05 m, '
            f'바퀴·조향 추정 평균 0.78 m"><g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


def margin_bar():
    """Week 4 fork-tip lateral error inside the 45 mm pocket margin."""
    left, width, full = 20, 1140, 45.0
    def w(mm):
        return mm / full * width
    segs = [(3.58, DIR_BLUE, '차체 방향'), (1.34, CAM_ORANGE, '카메라 추정'), (0.78, STOP_GREEN, '정지 위치')]
    parts = [f'<rect x="{left}" y="40" width="{width}" height="46" rx="4" fill="#eef1f4"/>']
    x = left
    for mm, fill, _ in segs:
        parts.append(f'<rect x="{x:.1f}" y="40" width="{w(mm):.1f}" height="46" fill="{fill}"/>')
        x += w(mm)
    parts.append(f'<line x1="{left + width}" y1="30" x2="{left + width}" y2="96" stroke="#c0392b" stroke-width="4"/>'
                 f'<text x="{left + width}" y="22" text-anchor="end" font-size="21" font-weight="700" fill="#c0392b">포켓 벽까지 45 mm</text>'
                 f'<text x="{left + w(5.7) + 14:.1f}" y="72" font-size="24" font-weight="700" fill="#1b1f24">포크 끝 좌우 오차 5.7 mm</text>')
    lx = left
    for mm, fill, name in segs:
        parts.append(f'<rect x="{lx}" y="112" width="18" height="18" fill="{fill}"/>'
                     f'<text x="{lx + 26}" y="128" font-size="20" fill="#1b1f24">{name} {100 * mm / 5.70:.1f} %</text>')
        lx += 230
    return (f'<svg class="diagram" viewBox="0 0 1180 140" role="img" aria-label="포크 끝 옆 오차 5.7 mm는 포켓 벽까지 여유 45 mm의 약 13 %. '
            f'차체 방향 62.8 %, 카메라 23.5 %, 정지 위치 13.7 %"><g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '5주차\n자율 지게차 개발', 20, '',
    """이번 주 진행은 두 가지이다. 입고한 차체의 치수와 포크, 동봉 팔레트를 실측하고 조종기 버튼별 신호를 측정하였다. 그리고 시뮬레이션에서 2D LiDAR로 공장 지도를 만들고 그 안에서 자기 위치를 추정하는 데 성공하였다. 마지막으로 중간 미팅에서 확인할 사항을 정리한다.""",
    [(MAP, '개발 로드맵'), (FACTORY, '공장 홀과 LiDAR 지도 작성 실증')], '진행 보고')

# ----------------------------------------------------------------- 3 (placeholder)
MEASURE_ROWS = [
    ('전장 × 전폭 × 전고', '1.46 × 0.63 × 1.01 m (카탈로그)'),
    ('질량', '24 kg (카탈로그)'),
    ('축간 거리 · 윤거', '0.64 · 0.51 m (사진 추정)'),
    ('바퀴 반지름', '0.135 m (사진 추정)'),
    ('포크 길이 · 폭 · 두께', '420 · 55 · 24 mm (사진 추정)'),
    ('포크 중심 간격', '290 mm (사진 추정)'),
    ('승강 범위', '280 mm (사진 추정)'),
    ('최소 회전 반경', '— (주행 시험 필요)'),
]
measure_table = ''.join(f'<tr><td>{k}</td><td class="pending">—</td><td class="muted">{v}</td></tr>'
                        for k, v in MEASURE_ROWS)
add('차체 실측', '01  차체 실측', 90, f"""
<h2 class="headline">차체 실측값과 잠정 모델 비교 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:0.8fr 1.2fr">
{placeholder('치수선 사진', '측정 기준점·치수선 표시')}
<table class="comparison measure"><tr><th>항목</th><th>실측 (예정)</th><th>잠정 모델</th></tr>{measure_table}</table>
</div>
<div class="takeaway">반영 계획: 실측값으로 시뮬레이션 모델·좌표 변환 갱신</div>
""",
    """[작성 예정] 차체 실측 결과를 보인다. 측정 대상과 기준점, 측정값을 표로 정리하고, 지금까지 시뮬레이션에 쓴 잠정 모델 값과 비교한다. 잠정 모델은 상품 사진과 카탈로그로 만든 것이므로 실측값으로 바꾼다. 최소 회전 반경은 주행 시험이 필요해 정적 실측과 따로 표시한다.""",
    [(MODEL, '잠정 모델 치수 — 카탈로그 값과 사진 비례 추정'), (INTAKE, '입고 때 미측정 항목')],
    '화면 생성: 실물 사진 (작성 예정)')

# ----------------------------------------------------------------- 3 (placeholder)
add('포크·동봉 팔레트', '02  포크 · 동봉 팔레트', 80, f"""
<h2 class="headline">포크·동봉 팔레트 실측 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{placeholder('포크 사진 · 치수선', '폭 · 두께 · 간격 · 최저·최고 높이')}
{placeholder('동봉 팔레트 사진 · 치수선', '외형 · 포켓 개구 폭·높이 · 포크와의 여유')}
</div>
<div class="takeaway">포크 치수: 시험 팔레트 제작과 삽입 여유 계산의 기준</div>
""",
    """[작성 예정] 포크의 폭과 두께, 두 포크의 간격, 최저·최고 높이를 잰 결과를 보인다. 오른쪽은 차체와 함께 온 팔레트의 외형과 포켓 개구이다. 포크 치수와 포켓 개구의 차이가 삽입할 때의 좌우·상하 여유가 되므로, 이 값이 시험 팔레트 제작과 삽입 목표의 기준이 된다.""",
    [(INTAKE, '입고 때 관찰한 포크·동봉 팔레트'), (MODEL, '잠정 모델 포크 치수 — 사진 추정')],
    '화면 생성: 실물 사진 (작성 예정)')

# ----------------------------------------------------------------- 4 (placeholder)
add('버튼별 신호', '03  조종기 버튼별 신호', 100, f"""
<h2 class="headline">조종기 버튼별 신호 측정 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:0.8fr 1.2fr">
{placeholder('측정 구성 사진', '조종기·수신기 · 로직 애널라이저 연결 지점')}
{placeholder('버튼별 파형', '전진·후진·조향·승강 버튼을 하나씩 눌렀을 때의 파형')}
</div>
<div class="takeaway">다음 작업: 신호 형식 확인 후 컴퓨터 명령 입력 위치 결정</div>
""",
    """[작성 예정] 4주차 피드백에 따라 로직 애널라이저로 조종기 버튼을 하나씩 눌러 신호를 측정하였다. 왼쪽은 측정 구성으로, 어디에 탐침을 연결했는지 보인다. 오른쪽은 전진·후진, 조향, 승강 버튼별 파형이다. 버튼마다 신호가 어떤 형식으로 바뀌는지가 컴퓨터가 명령을 넣을 위치와 방식을 정한다.""",
    [(INTAKE, '입고 때 관찰한 전장 구성'), (FEEDBACK, '§2 로직 애널라이저로 버튼별 신호 측정')],
    '화면 생성: 실물 사진 · 로직 애널라이저 캡처 (작성 예정)')

# ----------------------------------------------------------------- 5 demo (new clip)
add('LiDAR가 보는 것', '04  2D LiDAR 스캔', 75, f"""
<h2 class="headline">2D LiDAR는 1.05 m 높이 한 평면만 관측</h2>
<div class="split grow" style="grid-template-columns:1.15fr 0.85fr">
{figure('25_scan_view.mp4', '지게차를 위에서 따라가며 본 LiDAR 스캔. 빨간 선과 점은 한 바퀴 스캔이 닿은 곳이고, 진한 회색 물체만 닿고 옅은 회색 물체는 스캔에 나타나지 않는다', 'Isaac 주행 기록의 스캔 · 시뮬레이터상 실제 위치 기준 · 약 7배속', cls='')}
<div class="stack lidar-facts">
<div class="fact"><b>1,600</b><span>빔 / 한 바퀴 (0.225° 간격)</span></div>
<div class="fact"><b>10 Hz</b><span>한 바퀴 주기</span></div>
<div class="fact"><b>0.2–12 m</b><span>측정 거리</span></div>
<p class="vs-note">합성 센서 · A2M12 카탈로그 값 기준, 실측 아님</p>
</div>
</div>
""",
    """2D LiDAR가 무엇을 보는지부터 보인다. 영상은 Isaac 주행 기록의 스캔을 지게차를 따라가며 그린 것이다. LiDAR는 한 바퀴에 1,600개의 빔을 쏘아 빔마다 처음 닿은 곳까지 거리를 재며, 그 지점이 빨간 점이다. 한 바퀴는 0.1초이다. 빔은 1.05미터 높이의 수평면 하나에만 있으므로, 이 높이에 걸친 진한 회색 물체만 점으로 나타나고, 걸치지 않는 옅은 회색 물체는 바로 옆을 지나가도 보이지 않는다. 또 가까운 물체 뒤에 가려진 면은 찍히지 않는다. 그래서 실물에서는 지도에 담아야 할 물체의 높이를 보고 장착 높이를 정한다. 센서 값은 우리가 쓸 A2M12의 카탈로그 값을 따른 합성 센서이다.""",
    [(FACTORY, '§3 Isaac SLAM 기록 seed 0 — 스캔 2,454개'),
     (LIDAR_CFG, '합성 LiDAR 1,600빔 · 10 Hz · 0.2–12 m · 장착 높이 1.05 m (A2M12 카탈로그 값, 실측 아님)')],
    '화면 생성: slam_log.npz 의 스캔과 정답 레이저 자세를 prepare_videos.py 로 그림 (물체 윤곽은 meta.json 배치)')

# ----------------------------------------------------------------- 7 demo
add('지도 작성', '05  2D LiDAR 지도 작성', 70, f"""
<h2 class="headline">LiDAR로 만든 30 × 31 m 공장 지도와 자기 위치</h2>
<div class="pair grow"><div class="pair-box">
<span class="pair-tag left">Isaac 주행 <i>빨간 점: LiDAR 측정점</i></span>
<span class="pair-tag right">SLAM 지도 <i>파랑 SLAM 추정이 회색 실제 경로와 거의 겹침</i></span>
<video class="pair-video" src="assets/21_slam_map_pair.mp4" poster="assets/21_slam_map_pair_poster.jpg" autoplay loop muted playsinline aria-label="왼쪽은 공장 홀을 위에서 본 지게차의 시뮬레이션 주행, 오른쪽은 같은 순간까지 slam_toolbox가 만든 지도와 추정 경로"></video>
</div></div>
<div class="chips"><span>Isaac 주행 기록</span><i>→</i><span>ROS 2 재생</span><i>→</i><span>slam_toolbox 지도·위치 추정</span><i>→</i><span>정답과 비교</span></div>
""",
    """Isaac의 30 곱하기 31미터 공장에서 지게차가 116미터 경로를 달리며 LiDAR 스캔과 바퀴 회전, 조향각을 기록하고, 이 기록을 ROS 2에서 재생해 공개 SLAM 패키지인 slam_toolbox가 지도와 위치를 추정하게 했다. 왼쪽은 위에서 본 주행이고, 오른쪽은 그 시각까지 만들어진 지도와 추정 경로이다. 지게차가 돌수록 지도가 넓어지고, 파란 SLAM 추정 위치가 회색 실제 경로 위를 따라간다. 다만 기록을 다시 재생해 얻은 결과이고, 주행 자체는 시뮬레이터가 알려 준 정답 위치로 하였다. 즉 SLAM 결과로 차를 움직인 것은 아니다.""",
    [(FACTORY, '§3 기록 · §4 재생 · §6 3분할 영상'), (FACTORY, '§1 30 × 31 m 공장 홀'),
     (LIDAR_CFG, '합성 LiDAR 1,600빔 · 10 Hz · 0.2–12 m (A2M12 카탈로그 값, 실측 아님)')],
    '화면 생성: Isaac Sim 기록 + ROS 2 slam_toolbox 재생 20260928_week05_replay, 3분할 영상에서 조감·지도 두 칸만 잘라 8배속')

# ----------------------------------------------------------------- map compare (new clip)
add('지도 비교', '06  위치 추정에 따른 지도 차이', 75, f"""
<h2 class="headline">위치 추정이 틀리면 같은 스캔도 지도가 번짐</h2>
<div class="pair grow"><div class="pair-box" style="aspect-ratio:1254/732">
<video class="pair-video" src="assets/26_map_compare.mp4" poster="assets/26_map_compare_poster.jpg" autoplay loop muted playsinline aria-label="같은 스캔을 왼쪽은 바퀴·조향으로 추정한 위치에, 오른쪽은 SLAM이 추정한 위치에 쌓아 지도를 만드는 영상. 왼쪽은 물체 윤곽이 여러 겹으로 번지고 오른쪽은 선명하다"></video>
</div></div>
<div class="takeaway">SLAM: 스캔을 이미 만든 지도와 맞춰 위치를 바로잡음 → 물체 윤곽이 한 겹</div>
""",
    """SLAM이 왜 필요한지 보이는 장이다. 같은 LiDAR 스캔을 두 가지 위치 추정에 따라 한 장의 지도로 쌓았다. 왼쪽은 바퀴 회전과 조향각만으로 추정한 위치에 쌓은 것으로, 달릴수록 방향 오차가 쌓여 같은 물체가 여러 겹으로 번지고 벽이 비스듬해진다. 오른쪽은 SLAM이 스캔을 이전 지도와 맞춰 가며 추정한 위치에 쌓은 것으로, 물체 윤곽이 한 겹으로 선명하다. 지도가 선명하다는 것은 그 위치 추정이 맞다는 뜻이기도 하다.""",
    [(FACTORY, '§4 재생 — 같은 기록의 slam_toolbox 궤적과 바퀴 오도메트리'),
     ('artifacts/20260928_week05_replay/survey_seed_0_clean', 'slam_trajectory.csv · odometry.csv')],
    '화면 생성: 같은 스캔을 두 궤적에 놓아 prepare_videos.py 로 누적 (slam_toolbox 가 만든 지도가 아님)')

# ----------------------------------------------------------------- 8 demo
add('위치 추정 오차', '07  위치 추정 오차', 70, f"""
<h2 class="headline">LiDAR 지도와 맞춘 위치 오차 약 5 cm · 바퀴·조향만으로는 약 78 cm</h2>
<div class="split grow" style="grid-template-columns:1fr 1.05fr">
<div class="traj-box">{trajectory_anim()}
<div class="legend"><span><i style="background:#c9ced4"></i>실제 경로</span><span><i style="background:#2f74c0"></i>SLAM 추정</span><span><i style="background:#c26a1a"></i>바퀴·조향 추정</span></div></div>
<div class="stack" style="justify-content:center;gap:10px">
<p class="chart-cap">116 m 주행 기록 10회 재생 · 점 1개 = 재생 1회 · 막대 = 평균</p>
{ate_compact()}
<p class="chart-cap">바퀴·조향 추정: 거리는 정확 · 방향이 약 6° 틀어지며 오차 누적</p>
</div>
</div>
<div class="takeaway">다음 확인: 실물 바퀴·조향 신호로 방향 오차 누적량 측정</div>
""",
    """왼쪽은 위에서 본 지도 작성 경로이다. 회색 실제 경로 위로 파란 SLAM 추정은 거의 그대로 겹치고, 주황 바퀴·조향 추정은 점점 벗어나 끝에서 약 80센티미터 떨어진다. 오른쪽은 물건 배치가 다른 다섯 공장 장면의 주행 기록을, 잡음 없이와 합성 잡음을 넣어 모두 열 번 재생한 결과이다. 평균 위치 오차는 SLAM이 약 5센티미터, 바퀴와 조향만으로는 약 78센티미터였다. 바퀴·조향 추정은 달린 거리는 정확했지만 방향이 조금씩 틀어지며 오차가 쌓였다. 이것은 시뮬레이터의 관절 값에서 나온 결과이므로, 실물에서는 바퀴와 조향 신호를 직접 측정해 확인한다.""",
    [(FACTORY, '§6 재생 10회 — 시작 정렬 ATE, 잡음 없음 평균 SLAM 0.040 · 바퀴 0.773 m, 합성 잡음 0.055 · 0.782 m'),
     (FACTORY, '§4 — 누적 거리 115.92 대 115.98 m, 회전 9.54 대 9.43 rad, 원인 미확정 (seed 0)'),
     (FACTORY, '합성 잡음: 거리 σ 0.02 m · 뒷바퀴 σ 0.2 rad/s · 조향 σ 0.005 rad (가정값)')],
    '화면 생성: 재생 평가 수치 도식 (2026-09-28 재실행: 12개 값 중 11개가 소수 셋째 자리까지 일치, 1개는 0.001 m 차)')

# ----------------------------------------------------------------- 11
add('중간 미팅 확인 사항', '08  중간 미팅 확인 사항', 30, """
<h2 class="headline">중간 미팅 확인 사항</h2>
<div class="spread grow"><div class="qcols">
<article><h3>확인 사항</h3><ul><li>시연 장소·바닥 상태 (실내·실외)</li><li>평가 기준 (성공률 · 시간 · 정밀도)</li><li>시험 팔레트 치수·적재 하중</li><li>다우테크놀로지 사례 공유</li></ul></article>
<article><h3>자료 요청</h3><ul><li>제어기·조종기 배선·신호 자료</li><li>실제 지게차 운용 영상·데이터</li></ul></article>
<article><h3>협의 사항</h3><ul><li>시험 공간</li><li>허용 속도 상한</li><li>EPAL 6·축소 T11 시험 조건</li><li>동봉 팔레트 활용</li></ul></article>
</div>
<div class="next-strip"><b>다음 작업</b><span class="now">버튼 신호 분석</span><i>→</i><span>하위 제어 (명령 입력·상태 읽기)</span></div>
</div>
""",
    """마지막으로 추석 이후 중간 미팅에서 확인할 사항이다. 시연 환경과 평가 기준, 시험 팔레트를 확인하고, 제어기·조종기 자료와 운용 영상을 요청하며, 시험 공간과 팔레트 조건은 기업과 함께 정한다. 다음 작업은 측정한 버튼 신호를 분석해 하위 제어를 만드는 것이다.""",
    [(FEEDBACK, '§1 중간 미팅 준비 — 궁금한 것 · 제공 요청 · 결정 요청'), (MAP, '로드맵 H1–H4 · M4')],
    '출처: 4주차 피드백 · 개발 로드맵')

TITLE = '5주차 자율 지게차 개발'
TOTAL = 610


def build():
    assert len(slides) == 9, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'9장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-29. 2–4쪽은 차체 실측 결과이고, 시뮬레이션 쪽(5–8)은 '
              'Isaac Sim 합성 장면의 기술 실증이다. 시뮬레이션 수치는 실제 장비 성능이 아니며, '
              '로봇 제어는 시뮬레이터 정답 위치를 썼다.', '']
    elapsed = 0
    for i, s in enumerate(slides, 1):
        source_lines = '\n'.join(f'{label}: {url}' for url, label in s['sources'])
        notes = (f"권장 {s['seconds']}초\n\n{s['notes']}\n\n"
                 f"[Sources]\n{s['foot']}\n{source_lines}\n[/Sources]")
        if i == 1:
            component = (f'<x-import component-from-global-scope="UOSSlideDS.TitleSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}" '
                         f'subtitle="팔레트 핸들링 경로 생성 및 제어"></x-import>'
                         f'<img class="partner-mark" src="assets/riibotics-logo.png" '
                         f'alt="Riibotics">')
        else:
            component = (f'<x-import component-from-global-scope="UOSSlideDS.ContentSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}">'
                         f'<div class="slide-body">{s["body"]}</div></x-import>')
        section_class = ' class="title-section"' if i == 1 else ''
        sections.append(
            f'<section{section_class} '
            f'data-label="{escape(s["label"], quote=True)}" data-screen-label="{i:02d}" '
            f'data-duration="{s["seconds"]}" data-speaker-notes="{escape(notes, quote=True)}" '
            f'style="background:#fff">\n{component}\n</section>')
        end = elapsed + s['seconds']
        script += [f'## {i}쪽 · {s["label"]} ({elapsed//60:02d}:{elapsed%60:02d}–{end//60:02d}:{end%60:02d}, {s["seconds"]}초)',
                   '', s['notes'], '', '[Sources]', source_lines, '[/Sources]', '']
        elapsed = end
    html = f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{TITLE}</title>
<link rel="icon" href="data:,">
<script src="vendor/react.production.min.js"></script><script src="vendor/react-dom.production.min.js"></script><script src="./support.js"></script></head>
<body><x-dc><helmet><meta name="viewport" content="width=device-width, initial-scale=1"><title>{TITLE}</title>
<link rel="stylesheet" href="vendor/uos-slide-template/fonts/fonts.css"><link rel="stylesheet" href="vendor/uos-slide-template/_ds_bundle.css"><link rel="stylesheet" href="vendor/uos-slide-template/styles.css"><link rel="stylesheet" href="deck.css"><script src="vendor/uos-slide-template/_ds_bundle.js"></script></helmet>
<x-import component-from-global-scope="deck-stage" from="./deck-stage.js" width="1280" height="720" hint-size="100%,100%">
''' + '\n\n'.join(sections) + '\n</x-import></x-dc></body></html>\n'
    revision = sha256((ROOT/'deck.css').read_bytes()).hexdigest()[:12]
    html = html.replace('"deck.css"', f'"deck.css?v={revision}"')
    (ROOT/'index.html').write_text(html, encoding='utf-8')
    (ROOT/'SCRIPT.md').write_text('\n'.join(script), encoding='utf-8')
    (ROOT/'slide-metadata.json').write_text(
        json.dumps([{k: v for k, v in s.items() if k != 'body'} for s in slides],
                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(slides)} slides; timing {elapsed}s; '
          f'Korean script {sum(len(s["notes"]) for s in slides)} characters.')


if __name__ == '__main__':
    build()
