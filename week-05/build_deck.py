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
            '로봇 제어는 시뮬레이터 정답 위치</div>')
SLAM_BLUE, ODOM_ORANGE = '#2f74c0', '#c26a1a'   # validated pair (dataviz)


def add(label, title, seconds, body, notes, sources, foot='측정 결과'):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def figure(src, alt, caption, *, video=None, cls='wide'):
    if video is None:
        video = src.rsplit('.', 1)[-1].lower() in {'mp4', 'webm'}
    tag = (f'<video class="media" src="assets/{src}" autoplay loop muted playsinline '
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
        label = f'{pct:g} %'
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
            f'<text x="0" y="24" font-size="22" font-weight="700" fill="#44505c">장착 높이별 · 자기 차체에 가려지는 빔</text>'
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
<text x="585" y="76" text-anchor="end" font-size="20" fill="#0b3c8c" font-weight="700">높은 평면 — 차체 가림 없음</text>
<rect x="430" y="232" width="90" height="68" fill="#e3d6c3" stroke="#b98b54" stroke-width="2"/>
<text x="475" y="222" text-anchor="middle" font-size="19" fill="#8a5a1f" font-weight="700">낮은 물체: 안 보임</text>
<rect x="18" y="178" width="22" height="14" rx="3" fill="#c26a1a"/>
<line x1="40" y1="185" x2="238" y2="185" stroke="#c26a1a" stroke-width="4" stroke-dasharray="10 7"/>
<text x="262" y="176" font-size="19" fill="#8a4a10" font-weight="700">← 낮은 평면: 마스트·차체가 가림</text>
</g></svg>"""


# slam_toolbox replays of the 0.5 m/s survey loop, start-pose-aligned ATE in
# metres, layout seeds 0-4 (validation record section 6): (seed, clean, noisy).
REPLAY_ATE = {
    'SLAM': [(0, 0.025, 0.062), (1, 0.040, 0.050), (2, 0.039, 0.032), (3, 0.046, 0.084), (4, 0.047, 0.045)],
    '바퀴만': [(0, 0.576, 0.651), (1, 0.806, 0.757), (2, 0.807, 0.832), (3, 0.868, 0.853), (4, 0.806, 0.818)],
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
    colours = {'SLAM': SLAM_BLUE, '바퀴만': ODOM_ORANGE}
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
    note = (f'<text x="{left}" y="24" font-size="19" fill="#44505c">막대 = 10회 평균 · 점 = 재생 한 번의 위치 오차 RMSE '
            f'(출발 자세만 맞춤, 배치 5종 × 잡음 없음·합성 잡음)</text>')
    return (f'<svg class="budget" viewBox="0 0 1200 290" role="img" aria-label="116 m 조사 주행 재생 10회의 위치 오차. '
            f'같은 0 기준 축에서 SLAM 평균 0.05 m, 바퀴만 쓴 추정 평균 0.78 m">'
            f'<g font-family="var(--uos-font)">{note}{"".join(parts)}</g></svg>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '5주차\n자율 지게차 개발', 20, '',
    """이번 주에는 차체 실측과 배선 조사로 실물 개발을 시작하였다. 함께, 앞으로 필요한 위치 추정 기술을 시뮬레이션에서 미리 확인한 기술 실증을 보이고, 4주차 피드백에 대한 답과 중간 미팅에서 확인할 질문을 정리한다.""",
    [(MAP, '개발 로드맵'), (FACTORY, '공장 홀과 LiDAR 지도 작성 실증')], '진행 보고')

# ----------------------------------------------------------------- 2
add('계획서상 위치', '01  계획서상 위치', 45, """
<h2 class="headline">주 경로는 실물 · 시뮬레이션은 다음 단계 기술을 미리 확인</h2>
<div class="lanes grow">
<div class="lane-name main">실물<br>개발 경로</div>
<div class="lane">
<article class="now"><h3>차체 조사</h3><p>치수 실측<br>전장·신호 조사</p><p class="state">이번 주 시작</p></article>
<article class="wait"><h3>하위 제어</h3><p>컴퓨터 명령 입력<br>주행 상태 읽기</p></article>
<article class="wait"><h3>모델 검증</h3><p>실측 차체 모델<br>주행 특성 비교</p></article>
<article class="wait"><h3>위치 추정</h3><p>미리 만든 지도로<br>위치 추정·장애물 지도</p></article>
<article class="wait"><h3>삽입·운반</h3><p>포크 삽입<br>적재·운반·하역</p></article>
</div>
<div class="lane-name demo">시뮬레이션<br>기술 실증</div>
<div class="lane demo">
<article class="done span2"><h3>~4주차</h3><p>인식 → 경로 → 삽입 → 운반</p><p class="state">Isaac Sim</p></article>
<article class="now span2"><h3>이번 주</h3><p>공장 규모 작업장 · 2D LiDAR 지도 작성</p><p class="state">위치 추정 기술을 미리 확인</p></article>
</div>
</div>
<div class="takeaway">실증 결과는 실물의 위치 추정 단계에서 실제 센서·차체로 다시 정한다</div>
""",
    """개발 계획서의 순서를 먼저 확인한다. 위 줄이 주 경로이다. 차체를 실측하고 전장과 신호를 조사하는 첫 단계를 이번 주에 시작하였다. 그다음이 컴퓨터가 명령을 넣고 상태를 읽는 하위 제어, 실측 차체로 만든 모델의 검증, 그리고 미리 만든 고정 지도로 위치를 추정하고 장애물 지도를 만드는 단계이다. 지도를 만들며 동시에 위치를 추정하는 온라인 SLAM은 별도 조건으로 평가한다. 아래 줄은 시뮬레이션이다. 4주차까지 인식부터 운반까지를 연결하였고, 이번 주에는 넓은 공장 작업장과 2D LiDAR 지도 작성을 붙여 보았다. 이것은 위치 추정 단계에 필요한 기술을 미리 확인한 실증이며, 실제 구성은 그 단계에서 실물 센서와 차체로 다시 정한다.""",
    [(MAP, '로드맵 H0–H4, M4–M6 (발표에서는 단계 이름으로 표기)'), (STATUS, '현재 진행 상태'), (FACTORY, '이번 주 시뮬레이션 실증')],
    '출처: 개발 로드맵')

# ----------------------------------------------------------------- 3 (placeholder)
MEASURE_ROWS = [
    ('전장 × 전폭 × 전고', '1.46 × 0.63 × 1.01 m (카탈로그)'),
    ('질량', '24 kg (카탈로그)'),
    ('축간 거리 · 윤거', '0.64 · 0.51 m (사진 추정)'),
    ('바퀴 반지름', '0.135 m (사진 추정)'),
    ('포크 길이 · 폭 · 두께', '0.42 · 0.055 · 0.024 m (사진 추정)'),
    ('포크 중심 간격', '0.29 m (사진 추정)'),
    ('승강 범위', '0.28 m (사진 추정)'),
    ('최소 회전 반경', '— (주행 시험 필요)'),
]
measure_table = ''.join(f'<tr><td>{k}</td><td class="pending">실측 입력</td><td class="muted">{v}</td></tr>'
                        for k, v in MEASURE_ROWS)
add('차체 실측', '02  차체 실측', 70, f"""
<h2 class="headline">차체 실측 결과와 잠정 모델의 차이 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:0.8fr 1.2fr">
{placeholder('치수선 사진', '실측 사진에 측정 기준점과 치수선 표시')}
<table class="comparison measure"><tr><th>항목</th><th>실측</th><th>잠정 모델</th></tr>{measure_table}</table>
</div>
<div class="takeaway">실측값으로 시뮬레이션 모델과 좌표 변환을 갱신</div>
""",
    """[작성 예정] 차체 실측 결과를 보인다. 측정 대상과 기준점, 측정값을 표로 정리하고, 지금까지 시뮬레이션에 쓴 잠정 모델 값과 비교한다. 잠정 모델은 상품 사진과 카탈로그로 만든 것이므로 실측값으로 바꾼다. 최소 회전 반경은 주행 시험이 필요해 정적 실측과 따로 표시한다.""",
    [(MODEL, '잠정 모델 치수 — 카탈로그 값과 사진 비례 추정'), (INTAKE, '입고 때 미측정 항목')],
    '화면 생성: 실물 사진 (작성 예정)')

# ----------------------------------------------------------------- 4 (placeholder)
add('포크·팔레트·배선', '03  포크 · 팔레트 · 배선', 60, f"""
<h2 class="headline">포크와 동봉 팔레트 실측 · 배선과 버튼 신호 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{placeholder('포크 · 동봉 팔레트', '포크 치수와 팔레트 개구 실측 · 시험 치구로 쓸 수 있는지')}
{placeholder('배선 · 버튼 신호', '확인한 배선도 · 로직 애널라이저 파형 (없으면 다음 측정점)')}
</div>
<div class="takeaway">다음: 신호 형식을 확인한 뒤 컴퓨터 명령을 넣을 위치를 정한다</div>
""",
    """[작성 예정] 포크의 폭·두께·간격과 최저·최고 높이, 동봉 팔레트의 외형과 개구를 잰 결과를 보인다. 포크 치수는 시험 팔레트 제작의 선행 조건이다. 오른쪽에는 전원에서 제어기, 모터까지 확인한 배선과, 조종기 버튼별로 측정한 신호를 보인다. 파형을 얻지 못한 경우에는 확인한 배선과 다음 측정점을 구분해 보인다.""",
    [(INTAKE, '입고 때 관찰한 전장 구성'), (MAP, '로드맵 H1 전장과 피드백')],
    '화면 생성: 실물 사진 (작성 예정)')

# ----------------------------------------------------------------- 5 demo
add('공장 규모 작업장', '04  [실증] 공장 규모 작업장', 40, f"""
<h2 class="headline">넓은 작업장에서 경로 계획과 지도 작성을 시험하는 장면</h2>
<div class="split grow" style="grid-template-columns:1.5fr 1fr">
{figure('20_factory_survey.mp4', '공장 홀을 위에서 본 영상. 지게차가 적재 팔레트 사이의 조사 경로를 돌고, 빨간 점은 그 순간의 LiDAR 적중점', 'Isaac Sim 조감 · 116 m 조사 주행 8배속 · 빨간 점 = LiDAR 적중', cls='')}
<table class="comparison facts2">
<tr><th colspan="2">장면 구성</th></tr>
<tr><td>작업장</td><td>약 30 × 31 m</td></tr>
<tr><td>팔레트 적재</td><td>55–63 개</td></tr>
<tr><td>적재 상자</td><td>394–563 개</td></tr>
<tr><td>작업장 물품</td><td>23 개</td></tr>
<tr><td>배치</td><td>seed마다 새로 생성</td></tr>
<tr><td>조사 경로</td><td>정한 경유점 14개를<br>경로 계획기가 연결</td></tr></table>
</div>
{DEMO_TAG}
""",
    """이번 주 시뮬레이션 실증은 넓은 공장 작업장에서 시작한다. NVIDIA 창고 장면의 남쪽 홀, 약 30 곱하기 31미터를 적재 팔레트와 작업장 물품으로 채웠다. 배치는 seed마다 새로 만들어지므로 같은 절차를 여러 배치에서 반복해 볼 수 있다. 4주차까지 쓰던 작은 운반 구역은 이 홀 안에 그대로 두었다. 영상 속 파란 선은 조사 경로로, 홀을 한 바퀴 도는 경유점 14개를 미리 정해 두고, 이웃한 경유점 사이를 경로 계획기가 장애물을 피해 자동으로 이어 만든 116미터 경로이다. 지게차는 시뮬레이터가 알려 주는 위치로 이 경로를 따라간다. 이 장면은 실제 시험장을 본뜬 것이 아니라, 긴 경로와 지도 작성을 시험하기 위한 합성 환경이다.""",
    [(FACTORY, '§1 공장 배치 — seed 0–19 팔레트 55–63 · 상자 394–563 · 작업장 물품 23'),
     (FACTORY_PLAN, '홀 계획 경계 x −25.6~4.7, y −22.9~8.3 m (30.3 × 31.2 m)'),
     ('config/factory_south_hall.yaml', 'survey_route 경유점 14개 — plan_survey_route 가 이웃 경유점을 Hybrid A* 로 연결')],
    '화면 생성: Isaac Sim 조감 녹화 8배속 (20260926_factory_slam_v3 seed 0)')

# ----------------------------------------------------------------- 6 demo
add('LiDAR 장착 높이', '05  [실증] 2D LiDAR 장착 높이', 45, f"""
<h2 class="headline">장착 높이가 보이는 범위를 정한다 — 낮으면 차체가 가리고, 높으면 낮은 물체를 놓친다</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{LIDAR_CONCEPT}
{occlusion_chart()}
</div>
<div class="takeaway">실물 LiDAR 장착 높이는 실측 차체로 다시 계산해 정한다</div>
{DEMO_TAG}
""",
    """2D LiDAR는 한 높이의 수평면만 본다. 그래서 장착 높이가 두 가지를 맞바꾼다. 낮게 달면 마스트와 차체가 빔을 가리고, 높게 달면 그보다 낮은 물체를 보지 못한다. 오른쪽은 잠정 차체 모델에 빔 400개를 쏘아, 높이별로 자기 차체에 가려지는 비율을 잰 것이다. 0.55미터에서는 60퍼센트가 가려지고, 1.05미터에서는 가리지 않는다. 이번 실증은 가드 위 1.05미터에 달았고, 그 대가로 이보다 낮은 물체는 지도에 나타나지 않는다. 이 수치는 사진으로 만든 잠정 모델의 것이므로, 실물 장착 높이는 실측 차체로 다시 계산해 정한다.""",
    [(FACTORY, '§1 — 빔 400개, base_link x = −0.12 m: 0.55 m 60 %, 0.65 m 18.8 %, 0.75 m 9.5 %, 1.05 m 0 %'),
     (LIDAR_CFG, '실증 장착 (−0.12, 0, 1.05) m — 합성 장착이며 하드웨어 결정 아님'),
     (HW, 'LiDAR 장착 위치 미확정')],
    '화면 생성: 개념도 · 잠정 모델 충돌 형상에 대한 광선 계산')

# ----------------------------------------------------------------- 7 demo
add('지도 작성', '06  [실증] 저장한 주행 기록으로 지도 만들기', 65, f"""
<h2 class="headline">주행 기록을 재생해 slam_toolbox로 지도와 위치를 추정</h2>
<div class="pair grow"><div class="pair-box">
<span class="pair-tag left">실제 움직임 <i>빨간 점 = LiDAR가 닿은 곳</i></span>
<span class="pair-tag right">SLAM이 만든 지도 <i>파랑 = 실제 · 빨강 = 추정</i></span>
<video class="pair-video" src="assets/21_slam_map_pair.mp4" autoplay loop muted playsinline aria-label="왼쪽은 공장 홀을 위에서 본 지게차의 실제 움직임, 오른쪽은 같은 순간까지 slam_toolbox가 만든 지도와 추정 경로"></video>
</div></div>
<div class="phase-flow flow5"><b>Isaac 주행 기록</b><span>스캔·바퀴·조향</span><span class="arrow">→</span><b>ROS 2 재생</b><span class="arrow">→</span><b>slam_toolbox</b><span class="arrow">→</span><b>지도 · 추정 위치</b><span class="arrow">→</span><b>정답과 비교</b></div>
{DEMO_TAG}
""",
    """Isaac에서 지게차가 116미터 조사 경로를 달리며 LiDAR 스캔과 바퀴 회전, 조향각을 기록한다. 이 기록을 ROS 2에서 재생해, 널리 쓰이는 공개 SLAM 패키지인 slam_toolbox가 지도를 만들고 매 순간 자기 위치를 추정하게 했다. 왼쪽은 위에서 본 실제 움직임이고, 오른쪽은 그 시각까지 만들어진 지도와 추정 경로이다. 지게차가 돌수록 오른쪽 지도가 넓어지고, 빨간 추정 위치가 파란 실제 경로 위를 따라간다. 이 지도와 위치는 기록을 다시 재생해 얻은 것이고, 주행 자체는 시뮬레이터가 알려 주는 정답 위치로 하였다. 즉 SLAM 결과로 차를 움직인 것은 아니다.""",
    [(FACTORY, '§3 기록 · §4 재생 · §6 3분할 영상'),
     (LIDAR_CFG, '합성 LiDAR 1,600빔 · 10 Hz · 0.2–12 m (A2M12 카탈로그 값, 실측 아님)')],
    '화면 생성: Isaac Sim 기록 + ROS 2 slam_toolbox 재생 20260928_week05_replay, 3분할 영상에서 조감·지도 두 칸만 잘라 8배속')

# ----------------------------------------------------------------- 8 demo
add('위치 추정 오차', '07  [실증] 위치 추정 오차', 55, f"""
<h2 class="headline">바퀴만으로는 방향 오차가 쌓이고, 지도와 맞춰 보면 수 cm로 줄어든다</h2>
{ate_chart()}
<div class="split" style="grid-template-columns:1fr 1fr">
<div class="fact-box"><b>바퀴만 쓴 추정</b><span>달린 거리는 정답과 0.05 % 안에서 일치 · 회전량을 9.54 대 9.43 rad로 다르게 세어 위치가 벌어짐</span></div>
<div class="fact-box"><b>조건</b><span>116 m 조사 주행 · 0.5 m/s · 합성 잡음은 가정값</span></div>
</div>
<div class="takeaway">실물의 바퀴·조향 신호로 방향 오차가 얼마나 쌓이는지 확인한다</div>
{DEMO_TAG}
""",
    """같은 주행을 다섯 가지 배치에서, 잡음 없이 한 번, 합성 잡음을 넣어 한 번씩 모두 열 번 재생하였다. 두 줄은 같은 0 기준 축 위에 있고, 막대는 열 번의 평균, 점 하나는 재생 한 번의 위치 오차이다. 출발 자세만 맞춘 뒤 주행 전체에서 구한 제곱평균제곱근이다. 바퀴 회전과 조향각만으로 위치를 계산하면 116미터를 달리는 동안 평균 0.8미터쯤 벗어났다. 달린 거리는 정답과 0.05퍼센트 안에서 맞았는데, 회전한 양을 조금씩 다르게 세어 방향이 어긋난 것이 원인이다. LiDAR 스캔을 지도와 맞추는 SLAM은 같은 주행에서 평균 5센티미터 안쪽이었다. 다만 이것은 시뮬레이터의 관절 값과 합성 센서에서 나온 결과이다. 엔코더 분해능을 시험한 것이 아니며, 실물에서 방향 오차가 얼마나 쌓이는지는 바퀴와 조향 신호를 측정해 확인한다.""",
    [(FACTORY, '§6 재생 10회 — 시작 정렬 ATE, 잡음 없음 평균 SLAM 0.040 · 바퀴 0.773 m, 합성 잡음 0.055 · 0.782 m'),
     (FACTORY, '§4 — 누적 거리 115.92 대 115.98 m, 회전 9.54 대 9.43 rad, 원인 미확정 (seed 0)'),
     (FACTORY, '합성 잡음: 거리 σ 0.02 m · 뒷바퀴 σ 0.2 rad/s · 조향 σ 0.005 rad (가정값)')],
    '화면 생성: 재생 평가 수치 도식 (2026-09-28 재실행에서 같은 값 확인)')

# ----------------------------------------------------------------- 9 demo
add('공장 임무', '08  [실증] 넓은 작업장에서의 임무와 속도', 60, f"""
<h2 class="headline">최고 8 km/h 설정에서도 빠르게 달린 시간은 몇 초뿐이었다</h2>
<div class="split grow" style="grid-template-columns:0.85fr 1.15fr">
{figure('22_mission_overview_seed16.mp4', 'seed 16 임무를 위에서 본 영상과 아래의 현재 단계·속도 표시', 'seed 16 · 4배속 · 아래 = 현재 단계와 속도', cls='')}
<table class="comparison facts2">
<tr><th>고른 두 사례</th><th>seed 5</th><th>seed 16</th></tr>
<tr><td>기본 설정 임무 시간</td><td>220.8 s</td><td>175.4 s</td></tr>
<tr><td>빠른 설정 (최고 8 km/h)</td><td>213.8 s</td><td>118.2 s</td></tr>
<tr><td>1 m/s 넘게 달린 시간</td><td>6.9 s</td><td>8.8 s</td></tr>
<tr><td>팔레트 위치</td><td colspan="2">카메라 추정</td></tr></table>
</div>
<div class="takeaway">seed 16 빠른 직선에서 재생 추정 오차 증가(원인 확인 중) → 실물 속도 상한과 센서 주기를 함께 정한다</div>
{DEMO_TAG}
""",
    """4주차에 보인 찾기, 집기, 운반, 하역, 복귀 임무를 넓은 공장에서 수행하고, 최고속도 설정을 시속 8킬로미터까지 올려 보았다. 고른 두 사례이며 성공률이 아니다. 최고속도에는 닿았지만 1미터 매초를 넘게 달린 시간은 두 사례 모두 10초가 안 되었고, 나머지는 곡선과 후진 구간을 느리게 달렸다. 빠른 설정은 최고속도 말고도 가속과 도착 허용 오차를 함께 바꾼 것이고, seed 5는 운반 경로 길이도 달랐다. 그래서 이 표는 속도만 바꾼 비교가 아니라, 고른 두 실행에서 관측한 시간이다. 또 seed 16의 빠른 직선 구간에서, 기록을 재생해 추정한 위치 오차가 3센티미터에서 0.9미터까지 커졌다가 돌아왔다. 원인은 아직 가르지 않았다. 8 km/h는 시뮬레이터 설정일 뿐 실제 차체의 속도가 아니며, 실물에서는 속도 상한과 센서 주기를 함께 정해야 한다.""",
    [(FACTORY, '§7 기본 속도 임무 220.8 / 175.4 s · §7a 8 km/h 설정 213.8 / 118.2 s, 1 m/s 초과 6.9 / 8.8 s'),
     (FACTORY, '§7a seed 16 SLAM 재생 오차 60–66 s 구간 0.9 m, 원인 미분리'),
     (FACTORY, '팔레트 위치만 카메라 추정 · 로봇 자세·충돌 지도·목적지는 정답 · 조향·바퀴 속도는 합성 값')],
    '화면 생성: 정보 패널 영상에서 Isaac 조감과 단계·속도 표시만 잘라 4배속 (seed 16)')

# ----------------------------------------------------------------- 10
add('피드백 대응', '09  4주차 피드백 대응', 60, """
<h2 class="headline">4주차 피드백에 대한 답과 다음 확인</h2>
<table class="comparison fb grow">
<tr><th>피드백</th><th>답</th></tr>
<tr><td>오차를 비율과 비중으로</td><td>4주차 삽입 끝 포크 끝 오차 5.7 mm = 포켓 벽까지 여유 45 mm의 <b>약 13 %</b> · 비중은 차 방향 <b>62.8 %</b>, 카메라 추정 23.5 %, 멈춘 자리 13.7 % (4주차 한 사례)</td></tr>
<tr><td>엔코더 분해능</td><td>시뮬레이션에서 바퀴로 잰 거리는 정답과 0.05 % 안 · 오차는 방향에서 쌓임 → 실물 바퀴·조향 신호로 확인</td></tr>
<tr><td>ToF 카메라 필요 여부</td><td>D435i는 적외선 패턴을 쓰는 능동 스테레오이며 ToF가 아님 · 캐리지 하단 장착 후보에서 근거리 관측을 먼저 확인하고, 부족하면 근거리 센서 추가</td></tr>
<tr><td>사람과 비슷한 운용</td><td>지게차 표준 작업 순서를 조사해 우리 임무 단계와 대조</td></tr>
<tr><td>안전 정지</td><td>기울기(IMU)·과적 감지 정지를 설계 후보로 검토 · 기준값은 무게중심·적재 한도 실측 후</td></tr></table>
""",
    """4주차 피드백에 대한 답이다. 첫째, 오차를 비율로 보면 4주차 삽입 결과에서 포크 끝이 빗나간 5.7밀리미터는 포켓 벽까지 여유 45밀리미터의 약 13퍼센트이고, 그 가운데 차가 비스듬히 선 방향 오차가 약 63퍼센트로 가장 크다. 4주차에 분석한 한 사례의 분해이다. 여유 45밀리미터는 잠정 포크 치수로 계산한 것이라 실측으로 갱신한다. 둘째, 엔코더 분해능은 시뮬레이션에서 거리보다 방향 오차가 문제였으므로, 실물의 바퀴와 조향 신호로 확인한다. 셋째, 우리 카메라 D435i는 ToF가 아니라 적외선 패턴을 쓰는 스테레오 방식이다. 포크 캐리지 하단 장착 후보에서 가까운 거리를 볼 수 있는지 먼저 확인하고, 부족하면 근거리 센서를 더한다. 넷째, 사람의 운전과 비슷하게 움직이도록 표준 작업 순서를 조사해 우리 임무 단계와 대조한다. 다섯째, 기울기와 과적을 감지해 멈추는 기능은 설계 후보로 두고, 기준값은 차체의 무게중심과 적재 한도를 잰 뒤 정한다.""",
    [('forklift-presentations/week-04/SOURCES.md', '4주차 포크 끝 좌우 5.7 mm = 추정 1.34 + 정지 0.78 + 방향 3.58 mm, 포켓 벽 45 mm 계산식'),
     (ADR3, '포켓 벽까지 45 mm (잠정 포크 치수)'),
     (FACTORY, '§4 거리 0.05 % 일치 · 방향 오차'),
     (D435I, 'D435i — 능동 IR 스테레오 깊이'), (CROWN, 'Crown 특허 — 캐리지 장착'),
     (ADAPT, 'ADAPT — 근거리 전용 센서'), (FEEDBACK, '4주차 피드백과 팀 메모')],
    '출처: 4주차 측정값 · 제조사 사양 · 팀 검토')

# ----------------------------------------------------------------- 11
add('미팅 질문과 다음 작업', '10  중간 미팅 질문과 다음 작업', 90, """
<h2 class="headline">중간 미팅에서 시험 조건을 확정하고, 계획서 순서대로 진행</h2>
<div class="qcols grow">
<article><h3>확인할 것</h3><ul><li>최종 시연 환경 (실내·실외, 바닥)</li><li>평가 기준 (성공률 · 시간 · 정밀도)</li><li>시험 팔레트 규격과 적재 하중</li></ul></article>
<article><h3>요청할 자료</h3><ul><li>제어기·조종기 배선·신호 자료</li><li>실제 지게차 운용 영상·데이터</li><li>다우테크놀로지 사례 자료</li></ul></article>
<article><h3>함께 정할 조건</h3><ul><li>운용 환경 · 시험 공간</li><li>허용 속도 상한</li><li>시험 팔레트 (EPAL 6 · 축소 T11 · 동봉품)</li></ul></article>
</div>
<div class="roadmap next">
<article class="now"><h3>신호 분석</h3><p>버튼별 신호 형식<br>모터 구동 방식</p></article>
<article class="wait"><h3>하위 제어</h3><p>컴퓨터 명령 입력<br>속도·조향·승강 상태</p></article>
<article class="wait"><h3>모델 검증</h3><p>실측 차체 모델<br>주행 특성 비교</p></article>
<article class="wait"><h3>위치 추정</h3><p>미리 만든 지도로 위치 추정<br>병행: 센서 장착·보정</p></article>
</div>
""",
    """추석 이후 중간 미팅에서 확인할 질문이다. 먼저 최종 시연 환경이 실내인지 실외인지, 평가를 성공률과 시간, 정밀도 가운데 무엇으로 하는지, 시험 팔레트와 적재 하중을 확인한다. 요청할 자료는 제어기와 조종기의 배선·신호 자료, 실제 지게차의 운용 영상과 데이터, 그리고 추천받은 다우테크놀로지 사례이다. 운용 환경과 허용 속도, 시험 팔레트는 기업과 함께 정한다. 다음 작업은 계획서 순서대로 진행한다. 버튼별 신호 형식과 모터 구동 방식을 분석하고, 컴퓨터가 명령을 넣고 상태를 읽는 하위 제어를 만든다. 실측 차체로 모델을 만들어 주행 특성을 비교한 뒤, 고정 지도를 이용한 위치 추정으로 넘어간다. 카메라와 LiDAR 장착과 좌표 변환 보정은 그와 병행한다.""",
    [(FEEDBACK, '§1 중간 미팅 준비 — 궁금한 것 · 제공 요청 · 결정 요청'), (MAP, '로드맵 H1–H4')],
    '출처: 4주차 피드백 · 개발 로드맵')

TITLE = '5주차 자율 지게차 개발'
TOTAL = 610


def build():
    assert len(slides) == 11, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'11장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-28 (초안). 실물 수치는 차체 실측 결과이고, 시뮬레이션 쪽(04–08)은 '
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
