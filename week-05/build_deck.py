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

# Share of 400 rays cast at the provisional URDF collision boxes that hit the
# truck itself, laser at base_link x = -0.12 m (validation record section 1).
SELF_OCCLUSION = [(0.55, 60.0), (0.65, 18.8), (0.75, 9.5), (1.05, 0.0)]


def occlusion_chart():
    left, top, row, bar_h, scale = 118, 56, 66, 34, 6.5   # px per percent
    rows = []
    for i, (height, pct) in enumerate(SELF_OCCLUSION):
        y = top + i * row
        w = pct * scale
        label = f'{pct:g} %' + ('  ← 이번 실증 장착' if height == 1.05 else '')
        rows.append(
            f'<text x="{left - 14}" y="{y + bar_h / 2 + 8}" text-anchor="end" font-size="22" '
            f'fill="#1b1f24" font-weight="700">{height:.2f} m</text>'
            + (f'<rect x="{left}" y="{y}" width="{w}" height="{bar_h}" rx="4" fill="{SLAM_BLUE}"/>'
               if w else '')
            + f'<text x="{left + w + 10}" y="{y + bar_h / 2 + 8}" font-size="21" fill="#1b1f24">{label}</text>')
    axis = (f'<line x1="{left}" y1="{top - 8}" x2="{left}" y2="{top + 4 * row - 24}" '
            f'stroke="#8c959e" stroke-width="2"/>')
    return (f'<svg class="diagram grow" viewBox="0 0 600 330" role="img" aria-label="LiDAR 장착 높이별로 '
            f'차체에 가려지는 빔 비율: 0.55 m 60 %, 0.65 m 18.8 %, 0.75 m 9.5 %, 1.05 m 0 %">'
            f'<g font-family="var(--uos-font)">'
            f'<text x="0" y="24" font-size="22" font-weight="700" fill="#44505c">장착 높이별 차체 가림 비율 (잠정 차체 모델)</text>'
            f'{axis}{"".join(rows)}</g></svg>')


# Side view: a high scan plane passes over a low box, a low plane hits the
# truck's own body. Concept only; nothing is to scale.
LIDAR_CONCEPT = """
<svg class="diagram grow" viewBox="0 0 600 330" role="img" aria-label="개념도: 높은 스캔 평면은 낮은 물체 위를 지나가고, 낮은 스캔 평면은 자기 차체에 가려진다">
<g font-family="var(--uos-font)">
<line x1="10" y1="300" x2="590" y2="300" stroke="#8c959e" stroke-width="3"/>
<rect x="40" y="200" width="200" height="70" rx="14" fill="#d8dce1"/>
<g stroke="#5d6670" stroke-width="7" stroke-linecap="round"><line x1="70" y1="200" x2="80" y2="110"/><line x1="220" y1="200" x2="228" y2="110"/><line x1="64" y1="108" x2="236" y2="108"/></g>
<rect x="240" y="96" width="12" height="190" fill="#8a939c"/><rect x="252" y="276" width="100" height="8" fill="#3d444b"/>
<circle cx="80" cy="272" r="26" fill="#50585f"/><circle cx="200" cy="272" r="26" fill="#50585f"/>
<rect x="130" y="84" width="24" height="16" rx="3" fill="#0b3c8c"/>
<line x1="154" y1="92" x2="585" y2="92" stroke="#2f74c0" stroke-width="4" stroke-dasharray="10 7"/>
<text x="585" y="76" text-anchor="end" font-size="20" fill="#0b3c8c" font-weight="700">높은 장착: 차체 가림 없음</text>
<rect x="430" y="232" width="90" height="68" fill="#e3d6c3" stroke="#b98b54" stroke-width="2"/>
<text x="475" y="222" text-anchor="middle" font-size="19" fill="#8a5a1f" font-weight="700">낮은 물체 미관측</text>
<rect x="18" y="178" width="22" height="14" rx="3" fill="#c26a1a"/>
<line x1="40" y1="185" x2="238" y2="185" stroke="#c26a1a" stroke-width="4" stroke-dasharray="10 7"/>
<text x="262" y="176" font-size="19" fill="#8a4a10" font-weight="700">← 낮은 장착: 마스트·차체 가림</text>
</g></svg>"""


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
    return f"""<svg class="diagram grow traj" viewBox="0 0 {size} {size}" role="img" aria-label="위에서 본 116 m 지도 작성 경로. 정답 경로 위로 SLAM 추정이 겹치고, 바퀴·조향 추정은 점점 벗어난다">
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
    """이번 주에는 4주차 입고 조사에 이어 차체 실측과 배선 조사로 실물 개발을 본격화하였다. 먼저 4주차 피드백에 대한 답을 보이고, 실물 조사 결과와 앞으로 필요한 위치 추정 기술을 시뮬레이션에서 미리 확인한 기술 실증을 차례로 보인 뒤, 중간 미팅에서 확인할 질문과 다음 작업으로 마친다.""",
    [(MAP, '개발 로드맵'), (FACTORY, '공장 홀과 LiDAR 지도 작성 실증')], '진행 보고')

# ----------------------------------------------------------------- 2
add('개발 단계와 이번 주 위치', '01  개발 단계와 이번 주 위치', 40, """
<h2 class="headline">실물 개발 단계와 이번 주 위치</h2>
<div class="pipeline grow">
<article class="pipeline-step now"><h3>① 차체 조사</h3><img class="step-thumb" src="assets/t1_chassis.jpg" alt=""><p>치수 실측<br>전장·신호 조사</p><p class="state">진행 중</p></article>
<article class="pipeline-step wait"><h3>② 하위 제어</h3><img class="step-thumb" src="assets/t2_remote.jpg" alt=""><p>컴퓨터 명령 입력<br>주행 상태 읽기</p><p class="state">예정</p></article>
<article class="pipeline-step wait"><h3>③ 모델 검증</h3><img class="step-thumb" src="assets/t3_model.jpg" alt=""><p>실측 차체 모델<br>주행 특성 비교</p><p class="state">예정</p></article>
<article class="pipeline-step demo"><h3>④ 위치 추정</h3><img class="step-thumb" src="assets/t4_map.jpg" alt=""><p>지도 기반<br>자기 위치 추정</p><p class="state">시뮬레이션 실증 <small class="new-tag">NEW</small></p></article>
<article class="pipeline-step wait"><h3>⑤ 삽입·운반</h3><img class="step-thumb" src="assets/t5_carry.jpg" alt=""><p>포크 삽입<br>적재·운반·하역</p><p class="state">예정</p></article>
</div>
<div class="takeaway">이번 주: 차체 실측 시작 · ④ 위치 추정용 2D LiDAR SLAM을 시뮬레이션으로 미리 확인</div>
""",
    """개발 계획서의 실물 개발 단계이다. 첫 단계인 차체 조사는 4주차 입고 조사에 이어 이번 주에 치수 실측과 전장·신호 조사를 진행하였다. 그다음이 컴퓨터가 명령을 넣고 상태를 읽는 하위 제어, 실측 차체 모델의 검증, 지도를 이용한 위치 추정, 그리고 포크 삽입과 운반이다. 이번 주에는 이 가운데 네 번째 단계인 위치 추정에 필요한 2D LiDAR SLAM을 시뮬레이션에서 미리 확인하였다. 이것은 실증이며, 실제 구성은 그 단계에서 실물 센서와 차체로 정한다.""",
    [(MAP, '로드맵 H0–H4, M4–M6 (발표에서는 단계 이름으로 표기)'), (STATUS, '현재 진행 상태'), (FACTORY, '이번 주 시뮬레이션 실증')],
    '출처: 개발 로드맵')

# ----------------------------------------------------------------- 10
add('피드백 대응', '02  4주차 피드백 대응', 85, f"""
<h2 class="headline">버튼별 신호 측정 · 오차를 여유 대비 비율로 표현</h2>
<div class="fb-top"><b>포크 끝 오차는 여유의 약 13 % · 가장 큰 원인은 차체 방향</b>{margin_bar()}<span class="fb-note">4주차 시뮬레이션 1회 · 잠정 포크 치수 · 차 위치는 정답 사용</span></div>
<div class="fb-cards grow">
<article class="key"><h3>버튼별 신호 <small>실물</small></h3><p>로직 애널라이저로 조종기 버튼별 신호 측정<br><b>→ 측정 결과: 04 버튼 신호</b></p></article>
<article><h3>카메라 장착 위치</h3><p>Crown 방식 포크 캐리지 하단 후보<br>D435i는 ToF 아닌 적외선 스테레오<br><b>→ 근거리 관측 확인 후 센서 추가 판단</b></p></article>
<article><h3>엔코더 분해능</h3><p>시뮬레이션은 분해능 미반영<br><b>→ 실물 바퀴·조향 신호 측정 후 결정</b></p></article>
<article><h3>작업자 운용 절차</h3><p>지게차 표준 작업 순서 조사<br><b>→ 임무 단계와 대조 예정</b></p></article>
</div>
""",
    """4주차 피드백에 대한 답을 먼저 보인다. 가장 중요한 요청은 조종기 버튼마다 신호가 어떻게 들어가는지 확인하라는 것이었다. 로직 애널라이저로 버튼을 하나씩 눌러 측정했고, 결과는 뒤의 포크·팔레트·버튼 신호 장에서 보인다. 둘째, 오차를 비율로 표현하라는 피드백이다. 위 막대는 4주차 시뮬레이션 삽입 한 사례로, 포크 끝이 빗나간 5.7밀리미터는 포켓 벽까지 여유 45밀리미터의 약 13퍼센트이고, 그 가운데 차가 비스듬히 선 방향 오차가 약 63퍼센트로 가장 크다. 차 위치를 시뮬레이터가 알려 준 결과라 실물에서 더해질 자기 위치 추정 오차는 들어 있지 않고, 여유 45밀리미터는 포크 실측으로 갱신한다. 셋째, 카메라는 Crown 특허처럼 포크 캐리지 하단에 다는 방식을 후보로 둔다. 우리 D435i는 ToF가 아니라 적외선 패턴을 쓰는 스테레오 방식이므로, 그 자리에서 가까운 거리를 볼 수 있는지 먼저 확인하고 부족할 때 근거리 센서를 더한다. 센서 조합은 조언대로 우선순위를 낮게 둔다. 넷째, 이번 시뮬레이션은 관절 값을 그대로 써서 엔코더 분해능을 판단할 근거가 되지 않으므로, 실물 바퀴와 조향 신호를 잰 뒤 정한다. 다섯째, 사람의 운전과 비슷하게 움직이도록 지게차 표준 작업 순서를 조사해 우리 임무 단계와 대조한다.""",
    [('forklift-presentations/week-04/SOURCES.md', '4주차 포크 끝 좌우 5.7 mm = 추정 1.34 + 정지 0.78 + 방향 3.58 mm, 포켓 벽 45 mm 계산식'),
     (ADR3, '포켓 벽까지 45 mm (잠정 포크 치수)'),
     (FACTORY, '§4 거리 0.05 % 일치 · 방향 오차'),
     (D435I, 'D435i — 능동 IR 스테레오 깊이'), (CROWN, 'Crown 특허 — 캐리지 장착'),
     (ADAPT, 'ADAPT — 근거리 전용 센서'), (FEEDBACK, '4주차 피드백과 팀 메모')],
    '출처: 4주차 측정값 · 제조사 사양 · 팀 검토')

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
add('차체 실측', '03  차체 실측', 75, f"""
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

# ----------------------------------------------------------------- 4 (placeholder)
add('포크·팔레트·버튼 신호', '04  포크 · 팔레트 · 버튼 신호', 80, f"""
<h2 class="headline">포크·동봉 팔레트 실측 및 버튼별 신호 확인 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{placeholder('포크 · 동봉 팔레트', '포크 치수·팔레트 개구 실측 | 동봉 팔레트의 시험용 사용 가능성')}
{placeholder('배선 · 버튼 신호', '확인된 배선·버튼 신호 | 파형 미확보 시 다음 측정 위치')}
</div>
<div class="takeaway">다음 작업: 신호 형식 확인 후 컴퓨터 명령 입력 위치 결정</div>
""",
    """[작성 예정] 포크의 폭·두께·간격과 최저·최고 높이, 동봉 팔레트의 외형과 개구를 잰 결과를 보인다. 포크 치수는 시험 팔레트 제작의 선행 조건이다. 오른쪽에는 전원에서 제어기, 모터까지 확인한 배선과, 조종기 버튼별로 측정한 신호를 보인다. 파형을 얻지 못한 경우에는 확인한 배선과 다음 측정점을 구분해 보인다.""",
    [(INTAKE, '입고 때 관찰한 전장 구성'), (MAP, '로드맵 H1 전장과 피드백')],
    '화면 생성: 실물 사진 (작성 예정)')

# ----------------------------------------------------------------- 6 demo
add('LiDAR 장착 높이', '05  2D LiDAR 장착 높이', 45, f"""
<h2 class="headline">LiDAR 장착 높이에 따른 관측 범위 차이 {badge('기술 실증 · LiDAR 장착 검토')}</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{LIDAR_CONCEPT}
{occlusion_chart()}
</div>
<div class="takeaway">낮게 달면 차체가 가리고, 높게 달면 낮은 물체를 놓침 | 실물 장착 높이: 차체 실측 후 결정</div>
""",
    """이번 주 시뮬레이션에서 새로 더한 센서는 2D LiDAR이다. 지도를 보기 전에 장착 높이부터 본다. 2D LiDAR는 한 높이의 수평면만 본다. 그래서 장착 높이가 두 가지를 맞바꾼다. 낮게 달면 마스트와 차체가 빔을 가리고, 높게 달면 그보다 낮은 물체를 보지 못한다. 오른쪽은 잠정 차체 모델에 빔 400개를 쏘아, 높이별로 자기 차체에 가려지는 비율을 잰 것이다. 0.55미터에서는 60퍼센트가 가려지고, 1.05미터에서는 가리지 않는다. 이번 실증은 차체 최상단 1.01미터보다 높은 1.05미터에 달았고, 그 대가로 이보다 낮은 물체는 지도에 나타나지 않아, 공장 장면의 적재 높이도 이 평면에 닿도록 맞추었다. 이 수치는 사진으로 만든 잠정 모델의 것이므로, 실물 장착 높이는 실측 차체로 다시 계산해 정한다.""",
    [(FACTORY, '§1 — 빔 400개, base_link x = −0.12 m: 0.55 m 60 %, 0.65 m 18.8 %, 0.75 m 9.5 %, 1.05 m 0 %'),
     (LIDAR_CFG, '실증 장착 (−0.12, 0, 1.05) m — 합성 장착이며 하드웨어 결정 아님'),
     (HW, 'LiDAR 장착 위치 미확정')],
    '화면 생성: 개념도 · 잠정 모델 충돌 형상에 대한 광선 계산')

# ----------------------------------------------------------------- 7 demo
add('지도 작성', '06  2D LiDAR 지도 작성', 75, f"""
<h2 class="headline">2D LiDAR 기록 재생으로 만든 30 × 31 m 공장 지도와 자기 위치 {badge('신규 · 기술 실증')}</h2>
<div class="delta"><span class="was"><b>4주차</b>카메라: 팔레트 위치</span><i>→</i><span class="now"><b>5주차</b>+ 2D LiDAR: 지도·자기 위치 (기록 재생)</span><em>임무 주행은 여전히 시뮬레이터 위치</em></div>
<div class="pair grow"><div class="pair-box">
<span class="pair-tag left">Isaac 주행 <i>빨간 점: LiDAR 측정점</i></span>
<span class="pair-tag right">SLAM 지도 <i>빨강 SLAM 추정이 파랑 정답과 거의 겹침</i></span>
<video class="pair-video" src="assets/21_slam_map_pair.mp4" poster="assets/21_slam_map_pair_poster.jpg" autoplay loop muted playsinline aria-label="왼쪽은 공장 홀을 위에서 본 지게차의 시뮬레이션 주행, 오른쪽은 같은 순간까지 slam_toolbox가 만든 지도와 추정 경로"></video>
</div></div>
<div class="chips"><span>Isaac 주행 기록</span><i>→</i><span>ROS 2 재생</span><i>→</i><span>slam_toolbox 지도·위치 추정</span><i>→</i><span>정답과 비교</span></div>
""",
    """4주차에는 카메라로 팔레트 위치만 알아냈고, 이번 주에는 2D LiDAR로 지도를 만들고 그 안에서 자기 위치를 추정하는 기술을 시뮬레이션에서 확인하였다. Isaac의 30 곱하기 31미터 공장에서 지게차가 116미터 경로를 달리며 LiDAR 스캔과 바퀴 회전, 조향각을 기록하고, 이 기록을 ROS 2에서 재생해 공개 SLAM 패키지인 slam_toolbox가 지도와 위치를 추정하게 했다. 왼쪽은 위에서 본 주행이고, 오른쪽은 그 시각까지 만들어진 지도와 추정 경로이다. 지게차가 돌수록 지도가 넓어지고, 빨간 추정 위치가 파란 정답 경로 위를 따라간다. 다만 기록을 다시 재생해 얻은 결과이고, 주행 자체는 시뮬레이터가 알려 준 정답 위치로 하였다. 즉 SLAM 결과로 차를 움직인 것은 아니다.""",
    [(FACTORY, '§3 기록 · §4 재생 · §6 3분할 영상'), (FACTORY, '§1 30 × 31 m 공장 홀'),
     (LIDAR_CFG, '합성 LiDAR 1,600빔 · 10 Hz · 0.2–12 m (A2M12 카탈로그 값, 실측 아님)')],
    '화면 생성: Isaac Sim 기록 + ROS 2 slam_toolbox 재생 20260928_week05_replay, 3분할 영상에서 조감·지도 두 칸만 잘라 8배속')

# ----------------------------------------------------------------- 8 demo
add('위치 추정 오차', '07  위치 추정 오차', 55, f"""
<h2 class="headline">LiDAR 지도와 맞춘 위치 오차 약 5 cm · 바퀴·조향만으로는 약 78 cm {badge('신규 · 기술 실증')}</h2>
<div class="split grow" style="grid-template-columns:1fr 1.05fr">
<div class="traj-box">{trajectory_anim()}
<div class="legend"><span><i style="background:#c9ced4"></i>정답 경로</span><span><i style="background:#2f74c0"></i>SLAM 추정</span><span><i style="background:#c26a1a"></i>바퀴·조향 추정</span></div></div>
<div class="stack" style="justify-content:center;gap:10px">
<p class="chart-cap">116 m 주행 기록 10회 재생 · 점 1개 = 재생 1회 · 막대 = 평균</p>
{ate_compact()}
<p class="chart-cap">바퀴·조향 추정: 거리는 정확 · 방향이 약 6° 틀어지며 오차 누적</p>
</div>
</div>
<div class="takeaway">다음 확인: 실물 바퀴·조향 신호로 방향 오차 누적량 측정</div>
""",
    """왼쪽은 위에서 본 지도 작성 경로이다. 앞 장의 영상과 달리 이 도표에서는 파랑이 SLAM 추정이다. 회색 정답 경로 위로 파란 SLAM 추정은 거의 그대로 겹치고, 주황 바퀴·조향 추정은 점점 벗어나 끝에서 약 80센티미터 떨어진다. 오른쪽은 같은 주행 기록을 배치와 잡음을 바꿔 열 번 재생한 결과이다. 평균 위치 오차는 SLAM이 약 5센티미터, 바퀴와 조향만으로는 약 78센티미터였다. 바퀴·조향 추정은 달린 거리는 정확했지만 방향이 조금씩 틀어지며 오차가 쌓였다. 이것은 시뮬레이터의 관절 값에서 나온 결과이므로, 실물에서는 바퀴와 조향 신호를 직접 측정해 확인한다.""",
    [(FACTORY, '§6 재생 10회 — 시작 정렬 ATE, 잡음 없음 평균 SLAM 0.040 · 바퀴 0.773 m, 합성 잡음 0.055 · 0.782 m'),
     (FACTORY, '§4 — 누적 거리 115.92 대 115.98 m, 회전 9.54 대 9.43 rad, 원인 미확정 (seed 0)'),
     (FACTORY, '합성 잡음: 거리 σ 0.02 m · 뒷바퀴 σ 0.2 rad/s · 조향 σ 0.005 rad (가정값)')],
    '화면 생성: 재생 평가 수치 도식 (2026-09-28 재실행: 12개 값 중 11개가 소수 셋째 자리까지 일치, 1개는 0.001 m 차)')

# ----------------------------------------------------------------- 9 demo
add('공장 임무', '08  공장 규모 자율 임무', 50, f"""
<h2 class="headline">카메라로 팔레트를 찾아 운반·하역·복귀까지 이어진 공장 임무 {badge()}</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{figure('22_mission_side_seed16.mp4', '16번 배치 임무를 지게차 옆 위에서 따라가며 본 영상. 팔레트에 접근해 포크를 넣고 들어 올린 뒤 운반해 초록 원 목적지에 내려놓는다', 'Isaac Sim 추적 시점 · 16번 배치 사례 1건 · 임무 주행은 시뮬레이터 위치 사용', cls='')}
<div class="stack" style="justify-content:center;gap:16px">
<div class="flow-chips"><span>관측</span><i>→</i><span>접근·삽입</span><i>→</i><span>들기</span><i>→</i><span>운반</span><i>→</i><span>하역</span><i>→</i><span>복귀</span></div>
<table class="comparison auto">
<tr><th>임무 주행 입력</th><th>4주차</th><th>5주차</th></tr>
<tr><td>팔레트 위치</td><td class="ok">카메라</td><td class="ok">카메라</td></tr>
<tr><td>로봇 위치</td><td>시뮬레이터</td><td>시뮬레이터 <small>(LiDAR 실증 별도)</small></td></tr>
<tr><td>장애물 지도</td><td>시뮬레이터</td><td>시뮬레이터 <small>(LiDAR 실증 별도)</small></td></tr></table>
<p class="vs-note">5주차 추가: LiDAR 위치 추정·지도 작성을 별도 기록 재생으로 실증 (06–07)</p>
</div>
</div>
<div class="takeaway">시뮬레이션 다음 단계: LiDAR로 추정한 위치·지도로 임무 주행 시험</div>
""",
    """4주차에 작은 구역에서 보인 임무를 넓은 공장 작업장으로 옮겨 수행하였다. 지게차는 카메라로 팔레트를 찾아 접근해 포크를 넣고 들어 올린 뒤, 출하장까지 운반해 내려놓고 출발 자리로 돌아온다. 고른 사례 하나이며 성공률이 아니다. 오른쪽 표는 입력별로 4주차와 이번 주를 비교한 것이다. 팔레트 위치는 4주차부터 카메라로 추정하였고, 이번 주에는 로봇 위치와 장애물 지도를 LiDAR로 만들 수 있음을 기록 재생으로 실증하였다. 다만 영상 속 임무 주행에는 아직 시뮬레이터 값을 쓴다. 시뮬레이션에서의 다음 단계는 LiDAR로 추정한 위치와 지도로 임무를 주행해 보는 것이며, 실물 적용 방식은 차체와 센서를 갖춘 뒤 정한다.""",
    [(FACTORY, '§7 공장 모드 인식 임무 — 16번 배치 완주, 팔레트 위치만 카메라 추정'),
     (STATUS, '현재 운반 코드가 사용하는 입력')],
    '화면 생성: Isaac Sim 추적 시점, 기본 속도 설정 재렌더 (ws1 20260928_week05_viewsD, 카메라 3.2 m 뒤·3.2 m 옆·2.6 m 위) · 관측~들기 4배속, 운반 8배속, 하역 3배속 편집')

# ----------------------------------------------------------------- 11
add('미팅 확인 사항과 다음 작업', '09  중간 미팅 확인 사항과 다음 작업', 85, """
<h2 class="headline">중간 미팅 확인 사항과 다음 작업</h2>
<div class="spread grow"><div class="qcols">
<article><h3>확인 사항</h3><ul><li>시연 장소·바닥 상태 (실내·실외)</li><li>평가 기준 (성공률 · 시간 · 정밀도)</li><li>시험 팔레트 치수·적재 하중</li><li>다우테크놀로지 사례 공유</li></ul></article>
<article><h3>자료 요청</h3><ul><li>제어기·조종기 배선·신호 자료</li><li>실제 지게차 운용 영상·데이터</li></ul></article>
<article><h3>협의 사항</h3><ul><li>시험 공간</li><li>허용 속도 상한</li><li>EPAL 6·축소 T11 시험 조건</li><li>동봉 팔레트 활용</li></ul></article>
</div>
<div class="next-plan"><b>다음 작업 <small>실물 측정 결과에 따라 조정</small></b>
<article class="now"><h4>다음 주</h4><p>버튼 신호·모터 구동 방식 분석<br>컴퓨터 명령 입력 경로 결정</p></article><i>→</i>
<article><h4>중간고사 전</h4><p>하위 제어 (명령 입력·상태 읽기)<br>실측 차체 모델 · 주행 특성 비교</p></article><i>→</i>
<article><h4>중간고사 후</h4><p>고정 지도 기반 위치 추정<br>포크 삽입 시험</p></article>
<em>병행: 카메라·LiDAR 장착과 보정 · 안전 정지(기울기·과적) 설계</em></div>
</div>
""",
    """추석 이후 중간 미팅에서 확인할 질문이다. 먼저 최종 시연 환경이 실내인지 실외인지, 평가를 성공률과 시간, 정밀도 가운데 무엇으로 하는지, 시험 팔레트와 적재 하중을 확인한다. 추천받은 다우테크놀로지 사례의 작업 공간과 험지 주행 여부도 확인한다. 요청할 자료는 제어기와 조종기의 배선·신호 자료, 실제 지게차의 운용 영상과 데이터이다. 시험 공간과 허용 속도, 그리고 EPAL 6·축소 T11의 시험 조건과 동봉 팔레트 활용 여부는 기업과 함께 정한다. 다음 작업은 계획서 순서대로 진행하며, 시점은 실물 측정 결과에 따라 조정한다. 다음 주에는 버튼별 신호 형식과 모터 구동 방식을 분석해 컴퓨터가 명령을 넣을 위치를 정한다. 중간고사 전까지 명령을 넣고 상태를 읽는 하위 제어를 만들고, 실측 차체로 모델을 만들어 주행 특성을 비교한다. 중간고사 뒤에는 고정 지도를 이용한 위치 추정과 포크 삽입 시험으로 넘어간다. 카메라와 LiDAR 장착과 보정, 그리고 팀에서 제안한 기울기·과적 감지 안전 정지의 설계는 그와 병행하며, 기준값은 무게중심과 적재 한도를 잰 뒤 정한다.""",
    [(FEEDBACK, '§1 중간 미팅 준비 — 궁금한 것 · 제공 요청 · 결정 요청'), (MAP, '로드맵 H1–H4 · M4'), (FEEDBACK, '팀 메모 — 기울기·과적 감지 정지')],
    '출처: 4주차 피드백 · 개발 로드맵')

TITLE = '5주차 자율 지게차 개발'
TOTAL = 610


def build():
    assert len(slides) == 10, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'10장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-29. 3쪽 오차 막대는 4주차 시뮬레이션 한 사례이고, 4·5쪽은 차체 실측 자료를 받아 채울 자리이다. 시뮬레이션 쪽(6–9)은 '
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
