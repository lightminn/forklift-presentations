"""Build the Riibotics mid-meeting web deck (week 7, part 1) and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

A technical mid-point review for the company that set the assignment (feedback of weeks 4-6:
docs/references/week4-6_feedback.md in the robot repository): what the team understood, the
system, what runs in simulation and what is still hardware work, the conclusions so far, the
schedule and the questions for the company. The plan is PLAN.md. Clips are cut by
prepare_clips.py and prepare_reverse_clip.py, the figures drawn by prepare_figures.py (matplotlib
PNGs in assets/). Week 6 clips are reused where the result has not changed. Since 2026-10-12 the
talk follows the brief's items in five sections -- summary, software, hardware, conclusion with the
schedule, questions (SECTIONS) -- with hardware and software kept apart; the localization slides are an
appendix. Software comes before hardware so the hardware section reads as how the simulated software is
put on the real truck (user, same day). Text-only slides became pictures the same day: status lanes (2),
gauges (4), a distance diagram (7) and a Gantt chart (17); the remaining on-screen text was compressed.
"""
from datetime import date, timedelta
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
QUEST = 'docs/references/quest.txt (과제 문서)'
NEARMOUNT = 'docs/validation/2026-10-03-near-field-mount-study.md'
NEARPLAN = 'docs/plans/2026-10-03-near-field-pocket-tracking.md'
LIDAR = 'docs/plans/2026-10-04-lidar-obstacle-map.md'
SLAM = 'docs/validation/2026-10-04-online-slam-closed-loop.md'
HW = 'docs/hardware.md'
MEASURED = 'sim/models/dls08_measured/README.md'
CROWN = 'https://patents.google.com/patent/US9990535B2/en'
QNET = 'https://www.q-net.or.kr/cst006.do?artlSeq=5211260&brdId=Q006&code=1204&gId=&gSite=Q&id=cst00602'
S4B = 'ws1 artifacts/20261011_s4b/smoke/seed_1_v0.055'
S5N1 = 'videos-from-ws1/20261007_l8_measured_seed5_n1'
S1N2 = 'videos-from-ws1/20261007_l8_measured_seed1_n2'
FB4, FB5, FB6 = ('docs/references/week4_feedback.md', 'docs/references/week5_feedback.md',
                 'docs/references/week6_feedback.md')
slides = []

BLUE, ORANGE, GREY = '#2f74c0', '#c26a1a', '#9aa3ad'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def video(src, alt, cls='media'):
    poster = src.rsplit('.', 1)[0] + '_poster.jpg'
    poster_attr = f' poster="assets/{poster}"' if (ROOT / 'assets' / poster).exists() else ''
    return (f'<video class="{cls}" src="assets/{src}"{poster_attr} autoplay loop muted playsinline '
            f'aria-label="{escape(alt, quote=True)}"></video>')


def stage(media, info, media_w):
    """Media panel and info panel sharing the space between headline and band (same top and
    bottom edges); the media panel's width follows the clip's aspect at the stage height."""
    return f'<div class="m7-stage grow" style="grid-template-columns:{media_w}px 1fr">{media}{info}</div>'


def mpanel(inner, legend=None, light=False):
    leg = f'<figcaption class="legend">{legend}</figcaption>' if legend else ''
    tone = {False: '', True: ' light', 'white': ' white'}[light]
    return f'<figure class="m7-media{tone}">{inner}{leg}</figure>'


def turbo(x):
    """The depth clip's colour map (render_depth.py: Google turbo polynomial), x in [0, 1]."""
    rgb = (0.13572138 + x*(4.61539260 + x*(-42.66032258 + x*(132.13108234 + x*(-152.94239396 + x*59.28637943)))),
           0.09140261 + x*(2.19418839 + x*(4.84296658 + x*(-14.18503333 + x*(4.27729857 + x*2.82956604)))),
           0.10667330 + x*(12.64194608 + x*(-60.58204836 + x*(110.36276771 + x*(-89.90310912 + x*27.34824973)))))
    return '#' + ''.join(f'{round(255 * min(max(c, 0.0), 1.0)):02x}' for c in rgb)


def legend(*items):
    """A graphic legend: swatches drawn in the clip's own colours, each with its term.
    items: (kind, colour, text) with kind line / dash / band / cell / dot / ring / box / none,
    ('ramp', css_gradient, (low, high)), ('text', None, words) for a plain term, or '|' for a divider."""
    out = []
    for item in items:
        if item == '|':
            out.append('<span class="sep"></span>')
            continue
        kind, colour, text = item
        if kind == 'text':
            out.append(f'<span class="lg">{text}</span>')
        elif kind == 'ramp':
            low, high = text
            out.append(f'<span class="lg">{low}<span class="sw ramp" style="background:{colour}"></span>{high}</span>')
        else:
            style = {'dash': 'border-color', 'ring': 'border-color', 'box': 'border-color'}.get(kind, 'background')
            extra = f';border-color:{colour}' if kind == 'band' else ''
            fill = f'{colour}73' if kind == 'band' else colour
            out.append(f'<span class="lg"><span class="sw {kind}" style="{style}:{fill}{extra}"></span>{text}</span>')
    return ''.join(out)


def rgb(t):
    return '#%02x%02x%02x' % t


# Clip colours, from the scripts that draw them (so the legend is the clip's own palette).
PLAN, PLAN_OLD, GRID, NEW_BOX = rgb((255, 214, 0)), rgb((150, 150, 160)), rgb((255, 130, 30)), rgb((255, 40, 40))  # compose_online_slam_video
TRUTH, ESTIMATE, ODOMETRY, GOAL = rgb((70, 150, 255)), rgb((235, 45, 45)), rgb((255, 160, 30)), rgb((0, 200, 60))   # compose_slam_video
RC_YELLOW, RC_ORANGE, RC_BLUE, RC_RED = rgb((255, 196, 40)), rgb((240, 125, 30)), rgb((60, 145, 240)), rgb((225, 45, 35))  # prepare_reverse_clip
DEPTH_RAMP = 'linear-gradient(90deg,' + ','.join(turbo(1 - k / 10) for k in range(11)) + ')'   # 0.25 m -> 3.0 m


def ipanel(title, table, cls=''):
    return f'<div class="m7-info {cls}"><p class="ph">{title}</p><div class="tb">{table}</div></div>'


def figure(name, alt):
    """A PNG drawn by prepare_figures.py (matplotlib) in assets/."""
    return f'<img class="m7-figimg" src="assets/{name}" alt="{escape(alt, quote=True)}">'


def tag(kind):
    return f'<span class="m7-tag {kind}">{TAGS[kind]}</span>'


TAGS = {'ok': '확인', 'next': '다음 단계', 'real': '실물', 'fixed': '확정', 'chosen': '선정',
        'draft': '설계 중', 'buy': '구매 예정', 'reuse': '기존 재사용', 'plan': '설계 반영 예정', 'part': '일부',
        'done': '완료', 'wait': '예정', 'design': '설계 중'}


# ----------------------------------------------------------------- 1
add('리보틱스 중간 미팅', '자율 지게차\n중간 점검', 20, '',
    """안녕하십니까. '자율 지게차 중간 점검'이라는 주제로 발표할 김광민이라고 합니다. 오늘은 지금까지의 개발 결과와 남은 과제를 기술 중심으로 정리하고, 마지막으로 리보틱스 측에 확인을 요청드릴 사항을 말씀드리겠습니다. (전환)""",
    [(QUEST, '과제: 주변 장애물을 고려한 최적의 팔레트 핸들링 경로 생성 및 제어'),
     (FB6, '§1 리보틱스 중간 미팅(형식은 중간 발표), 10/12 교수님 초안 검사 · 10/14 미팅')],
    '중간 미팅')

# ----------------------------------------------------------------- 2
# 2026-10-12 (user): "전체적으로 텍스트 많다는 평" -- the brief's items as two status lanes with a picture
# per stage instead of a four-column table; software (simulation) above, hardware (the real truck) below.
SW_LANE = [  # stage (the brief's process order), approach, thumbnail, simulation result (tag, text)
    ('팔레트 인식', 'D435i · 규격 치수 기반', 'pocket', [('ok', '포켓 위치 · 방향')]),
    ('위치 · 장애물', 'SLAM · 점유 격자', 'map', [('ok', '신규 장애물 재계획')]),
    ('장애물 회피 경로', 'Hybrid A* (전 · 후진)', 'path', [('ok', 'A–D')]),   # B as 확인 too (user, 2026-10-13)
    ('삽입 중 포켓 추적', '캐리지 하단 카메라', 'insert', [('ok', '무접촉 삽입')]),
    ('운반 · 하역', '인식 → 하역 단일 임무', 'mission', [('ok', '임무 완주')]),
]
HW_LANE = [  # stage, what, thumbnail (None: not started), state (tag, text)
    ('차체 실측', '최대 조향각 15°', 'chassis', [('done', '')]),
    ('기존 제어기 분석', '릴레이 On/Off 구동', 'ctrl', [('done', '')]),
    ('구동 보드', 'DRV8244 · MT6701', 'board', [('design', '')]),
    ('센서 장착', 'D435i · A2M12 보유', None, [('wait', '')]),
    ('실차 주행', '구동 보드 제작 후 A부터', None, [('wait', '')]),
]


def lane(cards):
    out = []
    for name, what, thumb, states in cards:
        pic = (f'<img class="th" src="assets/80_t_{thumb}.jpg" alt="">' if thumb
               else '<div class="th none"></div>')
        state = ''.join(f'{tag(k)}{t}' for k, t in states)
        cls = 'wait' if states[0][0] == 'wait' else ''
        out.append(f'<article class="{cls}">{pic}<h3>{name}</h3><p>{what}</p><p class="st">{state}</p></article>')
    return ''.join(out)


add('과제 이해와 진행 현황', '과제 요구사항별 접근과 진행 현황', 65, f"""
<h2 class="headline">시뮬레이션은 전 과정 통합, 실차는 구동 보드 설계 중</h2>
<div class="m7-lanes grow">
<p class="ln sw">소프트웨어<small>시뮬레이션</small></p><div class="lr sw">{lane(SW_LANE)}</div>
<p class="ln hw">하드웨어<small>실차</small></p><div class="lr hw">{lane(HW_LANE)}</div>
</div>
<div class="takeaway">남은 과제는 B에서 정지 없이 삽입, A–D 반복 평가, 센서 시험, 실차 주행입니다</div>
""",
    """먼저 과제 제안서의 요구사항별 접근 방법과 진행 현황을 요약하겠습니다. 위 줄은 소프트웨어로, 과제의 처리 순서대로 시뮬레이션에서 확인한 결과입니다. 센서는 제안서 구성대로 RGB-D 카메라 1대와 2D LiDAR 1대입니다. 카메라는 같은 스테레오 방식의 D435i를 선정했고, 팔레트 규격 치수를 기준으로 포켓을 검출합니다. LiDAR는 A2 계열 중 보유 중인 A2M12를 사용하며, SLAM 위치 보정과 장애물 판단에 함께 활용합니다. 과제의 두 목적인 장애물 회피 경로와 삽입 중 포켓 추적, 그리고 인식부터 하역까지의 다섯 단계는 시뮬레이션에서 하나의 임무로 연속 수행됩니다. 예시 A–D는 모두 인식부터 삽입까지 수행되며, B는 곡선으로 접근한 뒤 삽입 직전에 한 번 정지해 재관측합니다. 아래 줄은 하드웨어입니다. 소형 전동 지게차 차체를 실측하고 기존 제어기를 분석했으며, 속도 제어를 위해 구동 보드를 새로 설계하고 있습니다. 카메라와 LiDAR는 확보했고 아직 시험 전이며, 실차 적용은 구동 보드 제작 후 A부터 진행합니다. 이어서 시뮬레이션 임무 전체와 실기시험 기준 비교로 현재 결과를 요약한 뒤, 시뮬레이션에서 개발한 소프트웨어와 이를 실차에 구현하기 위한 하드웨어를 차례로 말씀드리고, 결론과 일정, 확인 요청 사항 순으로 마무리하겠습니다. (전환)""",
    [(QUEST, '센서(RGB-D Gemini 335Le · 2D RPLIDAR, SLAM · 장애물 목적) · 추천 플랫폼(소형 지게차 장난감 개조 또는 모바일 로봇 + 포크) · 목적(장애물 고려 경로, 삽입 중 pocket tracking) · 프로세스 5단계 · 예시 A–D'),
     (HW, 'D435i 확정 · RPLIDAR A2 계열 · Jetson 미구매'),
     ('사용자 답변 (2026-10-12)', 'RPLIDAR A2M12 는 이미 보유 (docs/hardware.md 는 아직 "유력안")'),
     (S4B, '인식(카메라 깊이) → 위치 → LiDAR 1대 장애물 지도 + Hybrid A* → 근접 추적 삽입 → 운반 · 하역 · 복귀, 한 임무 완주 (2026-10-11), 금지 접촉 0'),
     ('ws1 artifacts/20261008_d7_isaac/v2/d7', '현재 설정 9회 모두 완주 (새 상자 장면 포함)'),
     ('ws1 artifacts/20261012_meeting_ad', 'A–D 를 seed 5 에서 과제 그림과 같은 배치로 한 번씩 실행(정렬 직진 0.8 m, D 는 뒤 · 옆 벽), 네 경우 모두 success complete · 금지 접촉 0 (A·B · C·D 장)'),
     ('사용자 지시 (2026-10-13)', 'B 도 확인으로 표시 ("걍 확인이라 적으셈") — 로드맵 기준으로는 정지 후 삽입이라 미완료'),
     ('docs/plans/2026-09-11-development-roadmap.md', 'B 는 멈추지 않고 삽입 — 멈춘 뒤 정렬하는 구현은 B 완료로 표시하지 않음(:161); 기능 통과 A–D 각 20회 중 19회(:226). 지금 실행은 정렬 직진 시작(2.1 m)에서 멈춰 다시 관측, EPAL 6 · 장면당 1회'),
     ('week-05/SCRIPT.md', '차체 실측 · 제어기 역분석(릴레이 on/off, 속도 조절 없음) → DRV8244 구동 보드 회로 초안')],
    '출처: 과제 제안서 · 하드웨어 기록 · 실행 기록 · 단계 그림은 뒤 장의 그림과 영상 첫 장면을 자른 것 (prepare_figures.py thumbs)')

# ----------------------------------------------------------------- 3
add('시스템 구성', '실차 시스템 구성', 65, f"""
<h2 class="headline">소프트웨어는 Jetson에서, 모터 제어는 STM32 구동 보드에서 실행</h2>
<div class="grow m7-fill">{figure('40_system.png', '시스템 구성. 카메라와 LiDAR가 USB로 Jetson에, Jetson이 명령 · 상태로 STM32 보드에, STM32가 구동 · 엔코더 보드와 모터에 이어진다. 아래 무선 칸에 감시 PC(Wi-Fi)와 출력을 끊는 무선 비상정지')}</div>
<div class="takeaway">원격 정지 요구 수준과 다중 차량 운용은 마지막에 여쭙겠습니다</div>
""",
    """이제 이 소프트웨어를 실차에 구현하기 위한 하드웨어입니다. 먼저 실차 시스템 구성입니다. 왼쪽 센서는 과제 규격대로 RGB-D 카메라 1대와 2D LiDAR 1대입니다. 카메라는 과제의 Gemini 335Le 대신 같은 스테레오 방식인 D435i를 선정했습니다. 팀의 개발 경험이 있고, ROS 2 자료와 예제가 풍부하기 때문입니다. LiDAR는 과제의 A2 계열 중 보유 중인 A2M12를 사용합니다. 앞에서 보여 드린 포켓 인식, SLAM, 경로 계획과 추종, 삽입 중 추적은 가운데 Jetson에서 그대로 실행합니다. 오른쪽 STM32 보드는 경로 추종이 내는 속도 · 조향 명령을 받아 주행, 조향, 승강 모터를 제어하고, 엔코더로 바퀴 회전과 조향각을 측정합니다. 아래 점선 영역은 이번에 추가한 무선 구성입니다. 감시 PC와는 Wi-Fi로 상태와 지도만 주고받습니다. 무압축 깊이 영상은 초당 약 200메가비트로 Wi-Fi 실시간 전송이 어려워 차량에서 기록합니다. 비상정지는 Wi-Fi와 독립된 경로로 두어, 신호가 끊기면 즉시 정지하도록 합니다. 원격 정지의 요구 수준과 다중 차량 운용 여부는 마지막에 여쭙겠습니다. (전환)""",
    [(HW, 'D435i 확정 · RPLIDAR A2 계열 · Jetson Orin Nano Super 8GB 권장(미구매) · 개발 기준 ROS 2 Jazzy'),
     ('사용자 답변 (2026-10-12, LiDAR)', 'A2 계열 중 A2M12 를 고른 이유: 이미 보유'),
     ('사용자 답변 (2026-10-12)', 'Gemini 335Le 대신 D435i 를 산 이유: 전에 써 본 적이 있어 개발에 익숙함, ROS 2 자료 · 예제가 많음'),
     ('https://www.orbbec.com/gemini-335le/', 'Gemini 335Le — Active & Passive Stereo, 기가비트 이더넷 M12 · PoE(802.3af) 또는 DC 9–24 V, IP67, 124 × 29 × 50 mm · 220 g, 이상 깊이 0.25–6 m, 깊이 FOV 90° × 65° (D435i 도 스테레오 깊이, USB 3)'),
     ('week-05/build_deck.py', 'DRV8244-Q1 × 3 (L·M·R 채널, SPI 공유, DRVOFF 비상 차단) · MT6701 증분판(바퀴)·절대판(조향) · MCU 핀 배정 초안(Nucleo-64 morpho 2 × 38핀)'),
     (FB6, '§5 무선 통신 미고려 — 지게차–PC · 지게차–지게차'),
     ('config/isaac_slam_lidar.yaml', 'LiDAR 장착 높이 1.05 m (시뮬레이션 값, 실물 브래킷 미제작)'),
     ('https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html', 'M.2 Key-E 2230 — "Populated with the included wireless module" (802.11ac 모듈, 포럼 기준 RTL8822CE · AzureWave AW-CB375NF)'),
     ('https://docs.ros.org/en/jazzy/How-To-Guides/DDS-tuning.html', 'ROS 2 Jazzy DDS tuning — 손실 있는 Wi-Fi 에서 큰 메시지의 IP 조각 손실로 연결이 멈춘 것처럼 보임 (계산: 무압축 깊이 848 × 480 · 30 fps 약 195 Mbit/s, LiDAR 스캔 약 1 Mbit/s)'),
     ('https://docs.ros.org/en/jazzy/Installation/RMW-Implementations/Non-DDS-Implementations/Working-with-Zenoh.html', 'rmw_zenoh (멀티캐스트 탐색 없이 라우터 사용) — Wi-Fi 구성 후보, 미시험'),
     ('https://store.clearpathrobotics.com/products/wireless-e-stop', '산업 사례: 전용 무선 E-stop(FORT), 하트비트가 끊기면 정지, 수신기를 차량 E-stop 회로에 직결'),
     ('EU 기계지침 2006/42/EC 부속서 I 1.2.1 (2차 자료)', '무선 제어는 통신 상실 포함 올바른 신호가 없으면 자동 정지')],
    '출처: 하드웨어 기록 · 5주차 회로 초안 · 공식 문서 조사 (2026-10-11)')

# ----------------------------------------------------------------- 4
W5 = 'week-05/build_deck.py · SCRIPT.md'
CHASSIS_ROWS = [  # item, measured, comparison / effect
    ('최대 조향각', '15°', '사진 추정 대비 회전 반경 1.9배'),
    ('축거 · 윤거 · 바퀴 반경', '0.66 · 0.53 · 0.125 m', '사진 추정 대비 1–2 cm 차이'),
    ('포크 길이 · 폭 · 두께', '36 · 5.5 · 2.5 cm', 'EPAL 6 삽입 목표 33 cm (계산)'),
    ('포크 간격', '5.5–38 cm 조절', '팔레트 받침목 간격에 맞춤'),
    ('외형 · 질량', '1.46 × 0.63 × 1.01 m · 24 kg', '카탈로그 값과 일치'),
    ('최대 적재 하중', '10 kg (카탈로그)', '시뮬레이션 팔레트 질량과 같음'),
]
chassis_rows = ''.join(f'<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in CHASSIS_ROWS)
add('실물 차체', '실물 차체 실측', 60, f"""
<h2 class="headline">최대 조향각이 15°라 최소 회전 반경은 약 2.5 m, 포크 길이는 36 cm</h2>
{stage(mpanel('<img class="media" src="assets/30_chassis_pallet.jpg" alt="입고한 지게차 차체와 앞에 놓인 동봉 플라스틱 팔레트">', light=True),
        ipanel('실측 결과', f'<table class="comparison t6 m7-chassis"><tr><th>항목</th><th>실측</th><th>비교 · 영향</th></tr>{chassis_rows}</table>'), 346)}
<div class="takeaway">실측값은 시뮬레이션 차체 모델에 반영했고, 회전 반경은 주행 시험으로 검증합니다</div>
""",
    """다음은 소프트웨어를 올릴 차체입니다. 입고된 차체를 실측해 앞의 시뮬레이션 모델에 반영했습니다. 가장 큰 차이는 조향각이었습니다. 최대 조향각이 15도로, 계산한 최소 회전 반경은 약 2.5미터입니다. 사진으로 추정한 모델의 두 배에 가깝습니다. 앞의 경로 계획에서 전진과 후진을 반복해 방향을 맞추도록 한 근거가 이 값입니다. 축거, 윤거, 바퀴 반경은 사진 추정과 1에서 2센티미터 차이였습니다. 포크 길이가 36센티미터이므로 EPAL 6 팔레트의 삽입 목표는 33센티미터로 설정했고, 포크 간격은 5.5에서 38센티미터까지 조절됩니다. 최대 적재 하중은 카탈로그 기준 10킬로그램이며, 시뮬레이션 팔레트 질량도 10킬로그램으로 설정했습니다. 회전 반경은 조향각에서 계산한 값이므로 주행 시험으로 검증하겠습니다. (전환)""",
    [(MEASURED, '실측 축간 0.66 m · 윤거 0.53 m · 바퀴 0.125 m · 최대 조향 15° · 포크 360 × 55 × 25 mm · 외형 · 질량은 카탈로그와 같음을 실측으로 확인'),
     (W5, '1쪽 실측 표 — 잠정 모델(사진 추정) 축간 0.64 · 윤거 0.51 · 바퀴 0.135 m, 조향 25.8° (0.45 rad), 포크 420 mm, 포크 중심 간격 55–380 mm 조절'),
     ('계산', '최소 회전 반경 = L / tan δ: 0.66 / tan 15° = 2.46 m, 사진 추정 0.64 / tan 0.45 = 1.32 m (뒤차축, 자전거 모델) → 1.86배'),
     ('forklift CLAUDE.md', '삽입 깊이 규칙 min(깊이 × 0.6, 캐리지 한계 − 16 mm): dls08_measured 346 − 16 = 330 mm (EPAL 6 깊이 600 × 0.6 = 360 mm 보다 작음)')],
    '출처: 5주차 실측 (사진 2026-09-30, EXIF 제거)')

CONTROLLER_ROWS = [  # what, observation, so
    ('신호', '입력 동안 High 유지', 'PWM 아님'),
    ('모터 구동', '릴레이 On/Off · 방향 전환', '속도 제어 불가'),
    ('무선 수신', '메인보드 통합형', '미사용'),
    ('재사용', '전원 스위치 · 주행 · 리프트 모터', '그대로 사용'),
]
controller_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td><b>{c}</b></td></tr>' for a, b, c in CONTROLLER_ROWS)
add('기존 제어기 분석', '기존 제어기 분석', 65, f"""
<h2 class="headline">기존 제어기는 릴레이 On/Off만 가능해 구동 보드를 자체 제작</h2>
{stage(mpanel(figure('44_waveforms.png', '로직 애널라이저로 기록한 기존 제어기의 두 선. 주행 · 승강 · 조향 버튼마다 한 선만 켜지고, 누르는 동안 그대로 유지된다'), legend='로직 애널라이저(1 MHz)로 기록, 숫자는 버튼을 누르고 있던 시간', light='white'),
        f'<div class="m7-info"><img class="m7-photo" src="assets/43_la_setup.jpg" alt="기존 제어기 메인보드에 로직 애널라이저 탐침을 연결한 측정 구성">'
        f'<table class="comparison t6 m7-ctrl"><tr><th>대상</th><th>관측</th><th>판단</th></tr>{controller_rows}</table></div>', 600)}
<div class="takeaway">경로 추종이 내는 속도와 조향각 명령을 연속값으로 실행해야 합니다</div>
""",
    """경로 추종은 속도와 조향각을 연속값으로 명령하므로, 기존 제어기로 이를 실행할 수 있는지 분석했습니다. 오른쪽 위 사진과 같이 릴레이가 실장된 메인보드에 로직 애널라이저를 연결하고, 버튼 입력별로 신호를 기록했습니다. 왼쪽 파형을 보면 주행, 승강, 조향 모두 버튼마다 한 라인만 High가 되고, 입력하는 동안 그대로 유지됩니다. PWM이라면 빠르게 스위칭되어야 하므로, 이 신호는 단순 On/Off 신호입니다. 회로를 추적한 결과 모터는 릴레이로 켜고 끄며 방향만 전환하고, 속도 제어 기능은 없었습니다. 기존 제어기에 명령을 주입하더라도 On/Off 제어만 가능하므로, 기존 제어기 대신 구동 보드를 새로 제작하고 전원 스위치와 주행 · 리프트 모터는 그대로 사용합니다. (전환)""",
    [('week-05/assets/data_la_edges.json', 'DSLogic Pro 1 MHz 2채널, 주행 19 · 승강 28 · 조향 31개 레벨 변화; 명령 구간 안 변화 0개 (1 µs 튐 제외); 누르는 순간 두 선 동시 High 2.95–3.43 ms (팀 판단: 접지 튐, 미확정) — 그림의 짧은 세로선; 조향 기록은 왼쪽 1회만 포함'),
     (W5, '3–4쪽 파형 · 결론: 릴레이 on/off, 속도 조절 기능 없음, RF 메인보드 통합, 재활용: 전원 스위치 · 주행 모터 · 리프트 모터 (팀 리버스 엔지니어링 보고 2026-09-30), 전원 12.23 V'),
     ('docs/references/week4_feedback.md', '로직 애널라이저로 버튼별 신호 측정 (리버스 엔지니어링)')],
    '화면 생성: 5주차 파형 기록을 다시 그림 (prepare_figures.py hardware) · 측정 사진은 기판 · 장비 부분만 자름')

V_PER_A = 3600.0 / 4750.0          # IPROPI 3.6 kOhm / A_IPROPI 4750 A/A (VQFN-HR)
BOARD_ROWS = [  # part, choice, why
    ('모터 (기존)', '12 V · 45 W · 1.2 Ω', '정격 3.8 A · 구속 10 A'),
    ('모터 드라이버', 'DRV8244-Q1 × 3', '47 mΩ · 과전류 21 A 이상'),
    ('전류 측정', 'IPROPI 3.6 → 1.5 kΩ (예정)', '측정 범위 4.4 → 10 A'),
    ('비상 차단', 'DRVOFF 핀', '무선 비상정지 연동 예정'),
    ('조향각', 'MT6701 절대각 (SSI)', '전원 투입 즉시 각도 확인'),
    ('바퀴 회전', 'MT6701 증분 (ABZ)', 'MCU 타이머 계수'),
    ('제어기', 'STM32 (Nucleo-64)', '핀 배정 초안 완료'),
]
board_rows = ''.join(f'<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in BOARD_ROWS)
add('구동 보드 설계', '구동 보드 설계', 75, f"""
<h2 class="headline">DRV8244 3개와 MT6701 엔코더, STM32로 구동 보드 초안 설계</h2>
{stage(mpanel('<img class="media" src="assets/45_sch_drv_channel.png" alt="DRV8244 모터 드라이버 한 채널의 회로 초안. SPI 선 · 방향 입력 · DRVOFF · 전류 측정 저항">', legend='드라이버 1채널 회로 초안 (같은 회로 3채널이 SPI 버스를 공유)', light='white'),
        ipanel('부품 선정 근거', f'<table class="comparison t6 m7-board"><tr><th>기능</th><th>선정</th><th>근거</th></tr>{board_rows}</table>'), 470)}
<div class="takeaway">정격 3.8 A가 연속 허용 4 A에 가까워 방열을 검토한 뒤 PCB를 제작합니다 (10/30–11/12)</div>
""",
    f"""이 명령을 실행할 구동 보드의 회로 초안입니다. 모터 드라이버는 TI DRV8244 3개를 주행, 조향, 승강에 하나씩 배정할 계획입니다. 비교한 드라이버 중 온 저항이 47밀리옴으로 가장 작아 발열이 적고, SPI로 설정과 결함 진단이 가능합니다. 모터는 기존 12볼트 45와트 모터로 권선 저항이 약 1.2옴이므로, 정격 전류는 약 3.8암페어, 구속 시 최대 약 10암페어입니다. DRV8244의 과전류 보호 임계값은 21암페어 이상이므로 구속 상황에서도 여유가 있습니다. 모터 전류는 IPROPI 핀 저항에 걸리는 전압으로 측정하는데, 현재 초안의 3.6킬로옴으로는 약 {3.3 / V_PER_A:.1f}암페어까지만 측정되므로, 약 1.5킬로옴으로 변경해 10암페어까지 측정할 계획입니다. DRVOFF 핀은 출력을 즉시 차단하는 비상 차단용으로, 무선 비상정지와 연동할 예정입니다. 엔코더는 자기식 MT6701 한 종류로 통일했습니다. 조향축에는 절대각 출력을 사용해 전원 투입 즉시 각도를 확인하고, 바퀴에는 증분 출력을 사용해 MCU 타이머로 계수합니다. 정격 전류가 데이터시트의 연속 전류 기준인 4암페어에 근접하므로, 기판 방열을 검토한 뒤 PCB를 제작하겠습니다. (전환)""",
    [('https://www.ti.com/lit/ds/symlink/drv8244-q1.pdf', 'DRV8244-Q1 데이터시트 SLVSG24C — 4.5–35 V, RON 47 mΩ(VQFN-HR), AIPROPI 4750 A/A, DRVOFF, SPI 진단; 연속 전류는 방열이 결정(표 7-1 DC 4.0 A, 85 °C · 4층)'),
     ('사용자 답변 (2026-10-12)', '모터 12 V · 45 W, 권선 저항 약 1.2 Ω'),
     ('계산', f'정격 45 / 12 = 3.75 A, 멈춤 12 / 1.2 = 10 A; IPROPI 3.6 kΩ: 3600 / 4750 = {V_PER_A:.3f} V/A, 3.3 V ↔ {3.3 / V_PER_A:.2f} A, 전류 제한 최대 VITRIP 2.97 V ↔ {2.97 / V_PER_A:.2f} A; 1.5 kΩ: 3.3 V ↔ {3.3 * 4750 / 1500:.1f} A, 2.97 V ↔ {2.97 * 4750 / 1500:.1f} A'),
     ('DRV8244-Q1 데이터시트 SLVSG24C 7.5.9 · 7.5.8', '과전류 보호 IOCP 21–40 A (OCP_SEL 00, 기본 · HW 유일), 10.5–24 A 설정도 있음(SPI); 전류 제한 VITRIP 1.18–2.97 V (끌 수 있음), ITRIP = VITRIP / RIPROPI × AIPROPI; AIPROPI 오차 ±5 % (1.2–8.3 A)'),
     ('https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf', 'MT6701 Rev.1.5 — 14 bit 절대각(SSI · I2C), ABZ 증분 ≤ 1024 PPR, 자석 간격 0.5–2.0 mm · 축 어긋남 ≤ 0.3 mm'),
     (W5, '5–8쪽: DRV8244 · DRV8873 · DRV8876 비교, MT6701 · AS5600 · AS5047P 비교, 회로 초안(DRV8244 × 3 L · M · R, SPI MISO · MOSI · CLK 공유, 채널별 CS · IN1 · IN2 · DRVOFF · nSLEEP · nFAULT · IPROPI), 엔코더판 2종, MCU 핀 배정(Nucleo-64 morpho 2 × 38핀) — 조건: 모터 전류 실측 후 확정'),
     ('week-07-1 17쪽 일정', '10/16–22 모터 전류 실측 · PCB 설계, 10/30–11/12 구동 보드 제작')],
    '화면 생성: 5주차 팀 회로 초안(40_sch_drv8244.png)의 L 채널을 잘라 2배 확대 (prepare_figures.py hardware)')

# ----------------------------------------------------------------- 5
SIM_STILL = '70_hall.jpg'   # the recorded run's hall at the start (prepare_clips.py mission)
SIM_PARAMS = [
    ('차체', '실측 축거 · 바퀴 · 조향각', 'measure', '5주차 실측 (외형 · 질량은 카탈로그)'),
    ('물리', 'Isaac Sim 5.1 · 120 Hz', 'impl', '바퀴 토크 구동 · 팔레트 물리 적재'),
    ('LiDAR', 'A2M12 1,600점 · 10 Hz', 'spec', '카탈로그 사양'),
    ('깊이 카메라', '640 × 480 · 화각 69°', 'assume', 'D435i 컬러 화각 기준'),
    ('SLAM 연동', 'ROS 2 slam_toolbox', 'impl', '스캔 송신 → SLAM 응답 후 진행'),
    ('바닥 장애물', 'LiDAR 높이 (1.05 m) 이상', 'assume', '운용 가정 · 저상 소품 제외'),
    ('마찰 · 토크', '마찰 계수 0.8 / 0.7 · 3 N·m', 'assume', '일반 범위 값 · 실측 후 교체'),
]
KIND = {'spec': ('규격·사양', '#2f74c0'), 'measure': ('실측', '#6a4fb3'), 'impl': ('구현', '#2e9a6b'), 'assume': ('가정', '#c26a1a')}
param_rows = ''.join(
    f'<tr><td>{a}</td><td>{v}</td><td><span class="kind" style="background:{KIND[k][1]}">{KIND[k][0]}</span> {why}</td></tr>'
    for a, v, k, why in SIM_PARAMS)
add('시뮬레이션 환경', '시뮬레이션 환경', 50, f"""
<h2 class="headline">Isaac Sim 공장 홀에 실측 차체와 과제 센서 구성 적용</h2>
{stage(mpanel(f'<img class="media" src="assets/{SIM_STILL}" alt="Isaac Sim 공장 홀을 위에서 본 장면. 지게차와 팔레트, 적재물이 보인다">', light=True),
        ipanel('설정과 근거', f'<table class="comparison params6 m7-params"><tr><th>항목</th><th>값</th><th>근거</th></tr>{param_rows}</table>'), 360)}
<div class="takeaway">바퀴 마찰, 구동 토크, 센서 잡음은 실측값으로 교체할 예정입니다</div>
""",
    """다음은 소프트웨어입니다. 실차 주행 전까지는 Isaac Sim에서 개발합니다. 공장 홀 장면에 팀이 실측한 차체 값을 적용하고, 물리 연산은 120헤르츠로 수행합니다. 지게차는 바퀴 토크로 구동되며, 팔레트도 고정하지 않고 포크로 들어 올립니다. LiDAR는 A2M12 카탈로그 사양으로, 깊이 영상은 D435i 컬러 카메라 화각에 맞춰 합성합니다. SLAM은 ROS 2의 slam_toolbox로 수행하며, 시뮬레이터는 스캔마다 SLAM 응답을 받은 뒤 다음 단계로 진행합니다. 주황색 태그는 가정값입니다. 저상 바닥 장애물은 없다고 가정했고, 바퀴 마찰과 구동 토크는 일반적인 범위의 값을 적용했습니다. 센서 잡음도 실측 전 설정이며, 이 값들은 실측 결과가 나오는 대로 우선 교체합니다. (전환)""",
    [(MEASURED, '실측 반영 모델 dls08_measured (실측하지 않은 항목은 추정값, 필드별 출처)'),
     ('config/isaac_transport.yaml', '정지 · 운동 마찰 계수 0.8 / 0.7 (지게차 · 팔레트 충돌 형상, sim/isaac/scene.py configure_drives), 바퀴 토크 3 N·m — 시뮬레이터 전용 가정값'),
     ('result.json pocket_camera · perception', '깊이 640 × 480, fx 465.74 → 수평 화각 69.0° (D435i RGB 시야를 흉내 낸 합성 설정, docs/design/2026-09-11-pocket-observation-and-scene-set.md 사용자 결정 1; D435i 깊이 화각 87° × 58° 아님), depth_quantize_mm 1, 잡음 없음'),
     ('config/obstacle_layer_single.yaml', 'LiDAR 잡음 noise_std_m 0.02 (±0.06 m 절단, SLAM 과 같은 스캔)'),
     ('config/pallet_geometry_epal6.yaml', 'EPAL 6 공식 제품 시트'),
     ('forklift CLAUDE.md', 'EPAL 6 과 T11 × 0.6 모두 필수, T11 정본 치수 미확정'),
     ('result.json settings_synthetic', 'physics_hz 120, physical_wheel_drive true, pallet_fixed_attachment false, pose_teleportation_after_reset false (S4b · 녹화 실행)'),
     ('config/isaac_slam_lidar.yaml', 'RPLIDAR A2M12 카탈로그 1,600빔 · 10 Hz · 0.2–12 m'),
     ('tools/slam_bridge_container.sh · ros2/src/forklift_bringup/config/slam_toolbox_isaac_online.yaml', 'slam_toolbox online_sync, mapping, 해상도 0.05 m, Ceres, 루프 닫기; Isaac 은 스캔마다 브리지 응답을 기다림 (sim/isaac · slam_link.py)'),
     ('ws1 Isaac Sim', '5.1 (Kit 로그 Isaac-Sim Python/5.1)'),
     ('forklift bc4cc64', '--min-obstacle-height-m 1.15 — 1.05 m 평면에 닿지 않는 소품 제거 (운용 가정)')],
    '출처: 저장소 설정 · 모델 기록 (6주차 1쪽 이어 받음)')

# ----------------------------------------------------------------- 6
# 2026-10-12: the five steps on the fork tip's distance to the pallet face instead of a table (S4B
# near_tracking.json: armed 44.3 s about 1.5 m out, corrections at 1.0 / 0.6 m, front -> roof tracking at
# 63.19 s about 0.55 m, protection from 0.149 m, insertion end about 0.32 m in).
D_FAR, D_IN = 1.6, -0.4                       # axis: fork tip to pallet face, m (negative = inserted)


def at(d):
    return f'{(D_FAR - d) / (D_FAR - D_IN) * 100:.1f}%'


def span(d0, d1, text, cls=''):
    return f'<span class="bar {cls}" style="left:{at(d0)};width:calc({at(d1)} - {at(d0)})">{text}</span>'


def mark(d, text, cls=''):
    return f'<span class="mk {cls}" style="left:{at(d)}"><i></i><em>{text}</em></span>'


INSERT_STEPS = [  # row label, track content
    ('① 영상 지연 보정', span(1.5, -0.32, '촬영 시점 위치로 정합')),   # label spelled out (user, 2026-10-14)
    ('② 연속 추적', span(1.5, 0.55, '포켓 입구') + span(0.55, -0.32, '윗판 가장자리', 'alt')),
    ('③ 경로 보정', mark(1.0, '정지 · 재관측') + mark(0.6, '정지 · 재관측')),
    ('④ 간격 감시', span(0.15, -0.32, '간격 판정', 'warn')),
    ('⑤ 삽입 완료', mark(-0.32, '캐리지 여유 1.6 cm', 'end')),
]
AXIS = [(1.5, '1.5 m'), (1.0, '1.0 m'), (0.6, '0.6 m'), (0.15, '0.15'), (0.0, '앞면'), (-0.32, '−0.32 m')]
FACE = f'<span class="face" style="left:{at(0)}"></span>'
insert_rows = ''.join(f'<p class="rl">{a}</p><div class="tr">{FACE}{b}</div>' for a, b in INSERT_STEPS)
insert_axis = ''.join(f'<span style="left:{at(d)}">{t}</span>' for d, t in AXIS)
insert_diagram = f'<div class="m7-dist">{insert_rows}<p class="rl"></p><div class="ax">{insert_axis}</div></div>'
add('삽입 중 포켓 추적', '삽입 중 포켓 추적', 80, f"""
<h2 class="headline">캐리지 하단 카메라로 삽입이 끝날 때까지 포켓 추적</h2>
{stage(mpanel(video('61_insert_depth.mp4', '캐리지 하단 카메라의 깊이 영상. 팔레트에 접근하며 두 번 정지해 재관측하고, 포크 삽입 중에도 팔레트 윗판이 시야에 남는다'),
              legend(('ramp', DEPTH_RAMP, ('깊이 0.25 m', '3 m 이상')), ('none', '#000000', '측정값 없음'))),
        ipanel('구현 단계 (포크 끝–팔레트 앞면 거리)', insert_diagram), 484)}
<div class="takeaway">팔레트에 닿지 않고 약 32 cm 삽입했습니다</div>
""",
    """과제에서 강조한 삽입 중 포켓 추적입니다. 처음에는 카메라를 차체 전방 상단에 장착했는데, 포크 삽입이 시작되면 마지막 약 25센티미터를 관측하지 못했습니다. 그래서 Crown 특허 사례와 같이 카메라를 캐리지 하단으로 옮겼고, 영상과 같이 삽입 중에도 팔레트 윗판이 시야에 남습니다. 영상의 색은 거리로, 빨간색일수록 가깝습니다. 구현은 오른쪽 그림과 같이 포크 끝과 팔레트 앞면 사이의 거리에 따라 다섯 단계로 나뉩니다. 먼저 시뮬레이터에서 측정한 영상 지연 약 0.09초를 반영해, 각 영상을 촬영 시점의 차량 위치에 정합합니다. 실물에서는 이 지연을 다시 측정합니다. 포크 끝이 앞면 약 0.55미터에 들어와 포켓 입구가 시야를 벗어나면, 윗판 가장자리로 팔레트 위치를 계속 추적합니다. 포크 끝이 앞면까지 1미터와 0.6미터 남은 지점에서는 정지해 재관측하고, 남은 직진 경로를 다시 생성합니다. 포크 끝이 앞면 15센티미터 이내에 들어오면 포크와 포켓 벽 사이의 간격을 계속 감시하고, 관측 오차와 정지 거리를 더한 값보다 좁아지면 정지합니다. 삽입은 캐리지 전방에 1.6센티미터 여유를 남기는 위치에서 완료합니다. 이 실행에서 포크는 팔레트와 접촉 없이 약 32센티미터 삽입되었습니다. 다만 깊이 잡음이 없는 합성 영상이므로, 잡음을 적용한 검증이 남아 있습니다. (전환)""",
    [(S4B, 'forklift b66271f, 실측 차체 · SLAM 위치 · LiDAR 1대 · 근접 추적(보정점 1.0 / 0.6 m), 포켓 깊이 확인(D5) 끔. result.json: success, 삽입 끝 진입 323.5 / 322.2 mm, 금지 접촉 0, 하역 6.74 mm'),
     (f'{S4B}/run/near_tracking.json', '근접 추적 시작 44.3 s, 1.0 m 보정 54.03 s(정지 0.37 s), 0.6 m 보정 61.73 s, 추적 대상 앞면 → 윗판 전환 63.19 s(frames mode front → roof), 포크 끝 보호 시작 70.62 s(앞면 0.149 m), 삽입 끝 80.69 s. 그림의 약 1.5 m · 0.55 m 는 보정점(1.0 / 0.6 m)에서 뒤차축이 움직인 거리로 계산 (44.3 s 1.52 m, 63.19 s 0.55 m), 삽입 끝 −0.32 m 는 진입 323.5 / 322.2 mm'),
     (NEARPLAN, '기존 장착(높이 0.50 m · 수평)은 삽입 마지막 약 0.25 m 무관측'),
     (CROWN, 'Crown 특허 US9990535B2 — 포크 캐리지 하단 장착 (4주차 장착 사례 ②)'),
     ('config/near_field_bounds_measured.json · forklift 2313dc9', '카메라 지연 L = 91.668 ms (11 틱, 120 Hz) — 측정 대역 84.43–98.94 ms, Isaac 렌더 경로의 값 (실물 D435i 는 다시 측정)'),
     ('src/forklift_core/perception/roof_tracking.py', '윗판 뒤 가장자리로 거리, 판재 · 틈 가장자리로 방향과 좌우 위치, 가려진 포켓은 팔레트 모델로 추정'),
     ('forklift b66271f · sim/isaac/near_tracking.py', '보정점 1.0 / 0.6 m(포크 끝 추정 – 앞면), 정지 후 새 관측으로 직진 다시 그림 + 모의 주행 도착 확인; 보호 구간 0.15 m 부터 포크–벽 간격 < b_t + 정지 휩쓸림 + 0.011 m 면 정지; 캐리지 앞 모서리 여유 0.016 m 에서 삽입 끝'),
     ('config/near_field_drive_terms.json', '접근 속도 0.055 m/s — 관측 주기의 모든 틱에서 정지 예산이 성립하는 가장 큰 0.005 단계'),
     ('memory: D8 범위 (2026-10-10 사용자 결정)', '추적 프레임에는 깊이 잡음을 넣지 않음 — 잡음 없는 합성 깊이에서의 추적 흐름 실증')],
    '화면 생성: 위 실행의 근접 깊이 프레임 506장(10 Hz)을 색 지도(turbo, 0.25–3.0 m)로, 사건 시각에 왼쪽 위 단계 라벨, 2배속 (prepare_clips.py depth) · 색 범례는 슬라이드 범례(같은 turbo 식)')

# ----------------------------------------------------------------- pocket recognition (week 3 figure)
WHY_POCKET = [
    # plainer wording (user, 2026-10-14): no internal terms such as 합성 장면 or 전수
    ('학습 데이터 불필요', '팔레트 규격 치수만 입력, 치수를 바꾸면 EPAL 6과 T11 모두 인식'),
    ('시뮬레이션 시험', '2–4 m 앞 EPAL 6 팔레트 60개를 모두 찾고, 위치 오차는 95 %가 1 cm 미만'),
]
why_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in WHY_POCKET)
add('포켓 인식', '포켓 인식 처리 과정', 60, f"""
<h2 class="headline">학습 모델 없이 팔레트 규격 치수로 포켓 검출</h2>
<div class="m7-rows grow" style="grid-template-rows:auto 1fr">
<figure class="m7-media m7-pipe2"><img src="assets/20_pipeline_stages_crop.png" alt="깊이 영상, 팔레트 앞면, 받침목과 빈 공간, 판정된 포켓 위치의 네 단계">
<div class="steps"><b>① 깊이 영상</b><i></i><b>② 앞면 추출</b><i></i><b>③ 받침목 · 개구부 분리</b><i></i><b>④ 포켓 위치 · 방향</b></div>
<figcaption class="legend">{legend(('cell', rgb((60, 150, 96)), '작업 범위'), ('cell', rgb((241, 194, 50)), '앞면 후보'), ('cell', rgb((150, 108, 64)), '측정점 존재 구간'), ('box', rgb((255, 64, 255)), '개구부 · 검출 포켓'))}</figcaption></figure>
{ipanel('선정 근거', f'<table class="comparison t6 m7-why"><tr><th>이유</th><th>설명</th></tr>{why_rows}</table>')}
</div>
<div class="takeaway">가까워지면 포켓 입구가 시야를 벗어나므로 삽입 중 추적이 이어받습니다</div>
""",
    """이제 과제 단계별로 설명드리겠습니다. 첫 단계인 팔레트 인식은 학습 모델 대신 팔레트 규격의 치수와 형상 규칙을 사용합니다. 그림과 같이 깊이 영상에서 작업 범위 안의 점만 남기고, 수직 평면을 찾아 팔레트 앞면으로 설정합니다. 앞면을 세로 칸으로 분할해 받침목과 개구부를 구분하고, 개구부 폭이 규격 범위에 들면 두 포켓의 중심과 삽입 방향을 산출합니다. 학습 데이터 없이 치수만 바꿔 EPAL 6과 T11을 같은 코드로 처리하기 위해서입니다. 시뮬레이션에서는 2에서 4미터 앞에 놓인 EPAL 6 팔레트 60개를 모두 찾았고, 위치 오차는 95퍼센트가 1센티미터 미만이었습니다. 다만 깊이 잡음이 없는 장면이며, 유사 형상 물체에 대한 오검출 평가와 T11 평가는 남아 있습니다. 또한 포켓 입구가 시야를 벗어나면 검출할 수 없으므로, 다음 장의 삽입 중 포켓 추적이 이어받습니다. (전환)""",
    [('src/forklift_core/perception/pocket_detector.py', 'Depth-only geometric baseline for a known, horizontal pallet shape — 작업 범위 → 앞면 평면 → 세로 칸(받침목 · 빈 공간) → 포켓 중심 · 방향'),
     ('src/forklift_core/perception/pallet_geometry.py', '판정 기준을 규격 치수에서 계산 (3주차 6쪽: 길이는 규격 비례, 측정점 수는 관측 면적 비례)'),
     ('week-03/SCRIPT.md', '4쪽 처리 과정(빈 공간 220 mm, 규격 허용 207.5–247.5 mm)'),
     ('docs/validation/2026-09-14-epal6-capture-and-evaluation.md', 'EPAL 6 Gazebo 장면 100개 = positive 60 · occluded 20 · negative 20, 자세 2.0–4.0 m, 옛 장착 (0.75, 0, 0.5), 깊이 잡음 없음; 대상 60개 모두 검출, 위치 p95 dev 8.17 mm; 음성 0/20 은 단측 95 % 상한 13.9 % 라 오검출 성능은 주장하지 않음 (+ ADR 0004 D6 grounded 형상 결함), 홀드아웃 아님, T11 렌더 평가 없음'),
     ('week-03/assets/20_pipeline_stages.png', '3주차 그림의 위 제목 띠와 아래 단계 설명을 잘라 내고 단계명은 HTML 로 (Gazebo 장면 s003 의 실제 중간 결과)')],
    '화면: 3주차 4쪽 그림 · 근거는 3주차 6 · 8쪽')


# 2026-10-14 (user): the localization / obstacle structure appendix slide removed; its SLAM result slide stays.

# ----------------------------------------------------------------- 7
SLAM_COMPARE = [  # item, 2D LiDAR SLAM, camera (visual) SLAM -- datasheets, BKM, RTAB-Map paper (SOURCES.md)
    ('측정 거리', '0.2–12 m', '0.2 m–3 m 이상 (조명 조건에 따라)'),
    ('시야', '360°', '전방 87° × 58°'),
    ('취약 환경', '긴 복도 · 넓은 개방 공간', '무질감 벽면 · 저조도 · 반복 패턴'),
    ('지도', '2D 점유 격자 → 경로 계획 직결', '특징점 지도 → 격자 별도 생성'),
    ('연산', 'CPU 전용 (소형 보드 가능)', 'GPU 권장 · Orin Nano는 저해상도만 안정'),
]
slam_rows = ''.join(f'<tr><td>{a}</td><td class="blue"><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in SLAM_COMPARE)
add('위치 추정', 'LiDAR SLAM 위치 추정', 65, f"""
<h2 class="headline">임무 종료 시점 위치 오차는 오도메트리 3.4 m, LiDAR SLAM 약 4 cm</h2>
{stage(mpanel(video('45_slam_error.mp4', 'SLAM 운반 실행에서 slam_toolbox가 생성한 지도와 추정 경로. 아래 수치는 SLAM 위치 오차와 오도메트리 위치 오차'),
              legend(('line', TRUTH, '실제 경로'), ('line', ESTIMATE, 'SLAM 추정'), ('line', ODOMETRY, '오도메트리'))),
        ipanel('LiDAR SLAM 선정 근거', f'<table class="comparison t6 m7-slam"><tr><th>항목</th><th>2D LiDAR (선정)</th><th>카메라 (비전)</th></tr>{slam_rows}</table>'), 380)}
<div class="takeaway">오도메트리 오차는 적재 상태로 선회할 때 덜 돌아 방향이 24° 어긋난 탓입니다 (마찰 가정값에 좌우)</div>
""",
    """(부록, 질문 시) LiDAR 1대로 위치를 추정한 결과와 LiDAR를 선정한 근거입니다. 바퀴와 조향 엔코더로 계산한 오도메트리를 SLAM으로 보정하는 구조입니다. 왼쪽 영상은 이전 차체 모델로 수행한 운반 실행입니다. 빨간 SLAM 추정 경로는 파란 실제 경로를 따라가지만, 주황색 오도메트리 경로는 점차 벗어납니다. 임무 종료 시점의 오도메트리 위치 오차는 3.4미터, SLAM은 약 4센티미터였고, 임무 전체 RMSE는 약 9센티미터였습니다. 3.4미터의 대부분은 적재 상태에서 선회할 때 실제 회전량이 계산보다 작아 방향이 24도 어긋난 데서 비롯됩니다. 오른쪽 표와 같이 카메라는 전방만 관측하고 거리가 멀수록 오차가 커지지만, LiDAR는 12미터까지 360도를 측정하고 그 지도를 경로 계획에 직접 사용할 수 있습니다. 과제 문서도 2D LiDAR를 SLAM용으로 지정했으므로, 위치 추정은 LiDAR가 담당하고 카메라는 팔레트 인식에 집중하도록 역할을 나눴습니다. (전환)""",
    [(SLAM, 'S3 장면 1 — 358 s 에서 SLAM 4.0 cm 대 바퀴 회전만 340 cm, 위치 RMSE 0.088 m'),
     ('ws1 artifacts/20261004_slam_s3/seed_1/run/slam_log.npz', '2026-10-06 재계산: 거리 92.9 대 93.6 m, 끝 방향 오차 −24.3°, 회전 시 실제/계산 비 빈 차 0.998 · 운반 0.925'),
     ('week-06/SOURCES.md', '영상은 이전 S3 실행(사진 추정 차체 dls08_provisional · forklift 5de6c3a, 마찰 가정값, 장애물은 시뮬레이터 정답) — 6주차 5쪽과 같음; 4 cm 는 끝 시점, 임무 전체 RMSE 8.8 cm · 최대 19 cm'),
     ('https://cdn.robotshop.com/media/r/rpk/rb-rpk-22/pdf/rplidar-a2m12-360-laser-range-scanner-datasheet.pdf', 'RPLIDAR A2M12 데이터시트 rev.1.0 — 0.2–12 m(흰 물체), 360°, 10 Hz · 0.225° (정확도 1/2/2.5 % 는 A2 시리즈 웹 사양표 값)'),
     ('https://www.realsenseai.com/wp-content/uploads/2026/03/RealSense-D400-Series-Datasheet-Mar-2026.pdf', 'D400 데이터시트 Rev 023 — 깊이 FOV 87° × 58°, 0.2 m – "3 m 이상, 조명에 따라", RMS ≤ 2 % (≤ 2 m), 반복 패턴은 거짓 깊이 가능'),
     ('https://dev.realsenseai.com/docs/tuning-depth-cameras-for-best-performance', 'Intel BKM Rev 1.9 — 깊이 오차는 거리의 제곱으로 증가 (848 × 480, 서브픽셀 0.08 가정 시 2 m 약 14 mm · 4 m 약 57 mm, 계산값)'),
     ('https://arxiv.org/abs/2403.06341', 'Labbé & Michaud, J. Field Robotics 2019 — 카메라: 흰 벽 · 질감 없음 · 어두운 곳에서 위치 상실, 단거리 LiDAR: 넓은 빈 공간 · 긴 복도에서 문제'),
     ('https://joss.theoj.org/papers/10.21105/joss.02783', 'SLAM Toolbox (JOSS 2021) — CPU 전용, 2D 점유 격자를 Nav2 에 그대로 사용'),
     ('https://arxiv.org/abs/2506.04359', 'cuVSLAM 기술보고서 부록 B — Orin Nano Super 에서 RGB-D 모드는 424 × 240 에서만 안정 (GPU 가속 비전 SLAM)'),
     (FB6, '§4 LiDAR SLAM 과 비전 SLAM 비교 장표 (LiDAR 를 쓰는 근거) · 팀 메모: SLAM 은 깊게 들어가지 않음')],
    '화면: 6주차 5쪽 실행을 글자 없이 다시 합성 (ws1 artifacts/20261012_meeting_clean/s3_odom.mp4, prepare_clips.py slam; 오차 수치 표기만 남김) · 비교표는 데이터시트 · 논문 조사 (2026-10-11)')

# ----------------------------------------------------------------- 8
PLANNER_ROWS = [  # item, implementation
    ('차량 모델', '자전거 모델 · 계획 회전 반경 3.45 m'),
    ('탐색', '0.2 m · 10° 격자 · 호 길이 0.25 m'),
    ('충돌 검사', '차체 + 적재물 사각형 · 여유 0.1 m'),
    ('목표 연결', 'Reeds–Shepp (전 · 후진)'),
    ('추종', '뒤차축 기준 pure pursuit'),
    ('장애물', 'LiDAR 점유 격자 · 정지 궤적 검사'),
    ('재계획', '정지 위치에서 경로 재생성 (후진 포함)'),
]
planner_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in PLANNER_ROWS)
add('새 장애물 대응', '경로 계획 구현과 새 장애물', 70, f"""
<h2 class="headline">Hybrid A*로 신규 장애물 앞에서 정지하고 재계획한 뒤 재개</h2>
{stage(mpanel(video('46_new_obstacle_single.mp4', '팔레트 운반 중 경로 위에 장애물이 나타나 정지하고, 재계획한 경로로 회피하는 장면. 왼쪽은 상부 시점, 오른쪽은 SLAM 지도와 LiDAR 점유 셀'),
              legend(('text', None, '오른쪽은 SLAM 지도'), '|', ('line', PLAN, '현재 경로'), ('line', PLAN_OLD, '직전 경로'), ('cell', GRID, 'LiDAR 점유 셀'), ('box', NEW_BOX, '신규 장애물'))),
        ipanel('구현 (현재 설정)', f'<table class="comparison t6 m7-plan"><tr><th>항목</th><th>구현</th></tr>{planner_rows}</table>'), 720)}
<div class="takeaway">운반 중과 복귀 중에 나타난 1.3 m 높이 장애물을 피해 임무를 마쳤습니다</div>
""",
    """경로 계획과 추종의 구현입니다. 경로는 Hybrid A*로 생성합니다. 실측 조향각 15도로 계산한 차체 한계 2.5미터에 여유를 둔 회전 반경 3.45미터로 0.25미터 길이의 전진 · 후진 호를 연결하며 탐색하고, 차체와 적재물을 포함하는 사각형에 0.1미터 여유를 두어 충돌을 검사합니다. 생성된 경로는 뒤차축 기준 pure pursuit로 추종하며, 전진과 후진이 바뀌는 지점에서는 정지합니다. 장애물은 LiDAR 1대의 스캔으로 점유 격자를 만들고, 현재 곡률로 정지할 때 지나는 칸이 모두 비어 있어야 해당 속도로 주행합니다. 영상은 운반 중 경로 위에 LiDAR 높이보다 높은 1.3미터 상자가 나타난 경우입니다. 왼쪽은 상부 시점, 오른쪽은 SLAM 지도와 LiDAR 점유 셀입니다. 정지 궤적이 막히자 지게차가 정지하고, 재계획 후 짧게 후진한 뒤 상자를 회피합니다. 현재 설정으로 다시 실행한 운반 중 · 복귀 중 장애물 장면도 모두 회피해 완주했습니다. 그렇다면 왜 바로 회피하지 않고 후진을 선택할까요? (전환)""",
    [(S5N1, 'result.json — success, 하역 64.9 mm, 상자 출현 77.2 s · 정지 약 78 s · 재계획 94.3 s 후 후진 (운반 중)'),
     (S1N2, 'result.json — success, 하역 8.0 mm, 상자 출현 226.0 s · 재계획 227.7 s (복귀 중)'),
     ('forklift bc4cc64', '영상: 실측 차체(dls08_measured), LiDAR 1대(1.05 m) 장애물 지도 + SLAM 지도로 경로 계획, 새 상자 0.4 × 0.4 × 1.3 m, 포켓 깊이 확인 끔, 목표 연결 Dubins (D7 이전)'),
     ('ws1 artifacts/20261008_d7_isaac/v2/d7', '현재 설정(D7: Reeds–Shepp 목표 연결 · 도킹): 9회 모두 success complete, 하역 3.0–22.6 mm; 상자 장면 seed_1_n1 · 1_n2 · 3_n1 · 5_n1 하역 3.0 · 4.6 · 11.6 · 19.9 mm (장면당 1회)'),
     ('result.json travel_planner_config (S4b · 녹화 실행)', 'curvature_limit 0.29, xy 0.2 m, yaw 10°, primitive 0.25 m, clearance 0.1 m, heuristic weight 1.8, reverse ×1.3, gear change 1.0 m, goal_connection reeds_shepp, shot_cap 4 m'),
     ('src/forklift_core/planning/hybrid_astar.py', 'Dolgov et al., Practical Search Techniques in Path Planning for Autonomous Driving (2008) 기준, 참고 Nav2 Smac Hybrid-A* — docs/design/2026-09-17-hybrid-astar-transport.md'),
     ('src/forklift_core/control/path_tracking.py · tracker_configs', '뒤차축 pure pursuit, 곡률 한계 0.36 /m, 전방 주시 0.28 m(접근), 전환점 정지 허용 0.03 m · 0.05 rad'),
     ('src/forklift_core/control/drive_permission.py', '비상정지 원호(현재 곡률로 멈추는 궤적)의 칸이 모두 FREE 여야 그 속도 허용 · 앞 경로도 같은 검사')],
    '화면: 6주차 7쪽 실행을 글자 없이 다시 합성 (ws1 artifacts/20261012_meeting_clean/n1.mp4, prepare_clips.py obstacle; 같은 구간 73–118 s · 2배속)')

# ----------------------------------------------------------------- 9
REVERSE_ROWS = [  # 2026-10-14 (user, option 1): the goal-fix drawing removed; its numbers kept as the last row
    ('상자 위치', '정지 위치에서 앞 2.0 m, 오른쪽 0.6 m'),
    ('기존 경로', '최소 회전 반경에 가깝지만 상자 위를 지남'),
    ('선회 영역', '최소 회전 반경으로 돌아도 상자에 걸림'),
    ('선택', '1.75 m 후진한 뒤 선회해 회피'),
    ('방향 맞추기', '목적지 앞에서 전진만 21.7 m, 앞뒤로 1.0 m'),   # plainer (user, 2026-10-14)
]
reverse_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in REVERSE_ROWS)
add('후진을 고르는 이유', '경로 계획의 후진 선택 조건', 85, f"""
<h2 class="headline">큰 회전 반경 때문에 후진으로 선회 거리를 확보해 장애물 회피</h2>
{stage(mpanel(video('55_reverse_box.mp4', '신규 장애물 앞에서 정지한 지게차를 비스듬한 상부 시점에서 본 영상. 기존 경로는 장애물 위를 지나고, 최소 회전 반경 스윕 영역에 장애물이 있어 1.75 m 후진한 뒤 선회해 회피한다'),
        legend(('line', RC_YELLOW, '기존 경로'), ('band', RC_RED, '최소 회전 반경 스윕 영역'), ('line', RC_ORANGE, '후진'), ('line', RC_BLUE, '전진'))),
        ipanel('후진을 고른 근거', f'<table class="comparison t6 m7-plan"><tr><th>항목</th><th>내용</th></tr>{reverse_rows}</table>'), 620)}
<div class="takeaway">후진 거리는 1.3배, 전환은 1회당 1 m로 계산해 전진이 어렵거나 훨씬 멀 때만 후진합니다</div>
""",
    """원인은 큰 회전 반경입니다. 경로 비용을 계산할 때 후진 거리에는 1.3의 가중치를, 전 · 후진 전환에는 1회당 1미터를 더하므로, 전진만으로 갈 수 있으면 전진 경로를 선택합니다. 영상은 앞의 장애물 장면을 다시 실행해 비스듬한 상부 시점에서 본 것입니다. 정지 위치에서 상자는 전방 2미터, 우측 0.6미터에 있었고, 노란 기존 경로는 최소 회전 반경에 가까운 경로임에도 상자 위를 지납니다. 빨간 영역은 그 위치에서 최소 회전 반경으로 선회할 때 차체가 지나는 스윕 영역이며, 상자가 그 안에 있습니다. 따라서 1.75미터 후진해 선회 거리를 확보한 뒤 상자를 회피합니다. 전 · 후진 전환은 목적지에서도 쓰입니다. 표 마지막 줄과 같이, 목적지 직전에 방향이 1.3도만 어긋나도 전진만 사용하면 계획 회전 반경 3.45미터로 지름 약 7미터의 원을 한 바퀴, 21.7미터를 선회해야 합니다. 그래서 목적지에 접속하는 마지막 구간에 전 · 후진 전환을 허용했고, 전진 0.5미터와 후진 0.5미터, 총 1미터로 보정이 끝났습니다. 다른 목적지 접근 계획에서도 원 선회 경로는 나타나지 않았습니다. C, D와 같이 먼저 후진해야 하는 상황에도 같은 계획기를 사용합니다. (전환)""",
    [('src/forklift_core/planning/hybrid_astar.py', 'PlannerConfig: reverse_penalty 1.3, gear_change_penalty_m 1.0; D7_PLANNER_OPTIONS = Reeds–Shepp 목표 연결 + 연결 상한 4 m'),
     ('config/isaac_transport_measured.yaml', 'planner_curvature_inv_m 0.29 (계획 회전 반경 3.45 m, 차체 한계 15° = 2.46 m 에 추종 여유)'),
     ('ws1 artifacts/20261012_meeting_chase/q67_seed_5_n1', '6주차 상자 장면(l8_measured seed_5_n1, forklift df109cf)을 기록된 인자 그대로 + 고정 시점(--extra-views quarter, 눈 −2.0, −0.4, 9.0 · 대상 1.8, −0.4, 0 · 초점 2.2) 으로 다시 실행 (meeting_quarter_w6.sbatch): success complete, 하역 22 mm; 상자 출현 76.6 s (상자 위치는 6주차 실행과 같음), 재계획 83.9 s'),
     ('같은 실행 plan_history.json (prepare_reverse_clip.py)', '멈춘 뒤차축 기준 상자 앞 2.03 m · 오른쪽 0.64 m; 따라가던 경로(운반 시작의 마지막 live 계획, 멈춘 위치에서 2.5 cm)는 상자 중심에서 0.7 cm, 4 m 동안 가장 작게 꺾는 원호(반경 1/0.29 m)에서 4.6 cm 이내; 그 원호의 차체 휩쓸림 띠(회전 중심에서 3.05–4.15 m, 짐 실은 사각형 앞 1.56 · 뒤 0.17 · 폭 0.80 m) 안에 상자 중심 3.46 m; 재계획 후진 1.75 m(주행 1.752 m) → 전진, 상자 중심까지 최소 1.63 m'),
     ('tests/unit/planning/test_d7_planner_options.py', 'l8_measured 장면 1 + N1 정지 재계획: 목표 1 cm 앞 · 0.023 rad — 전진만 21.68 m, D7 0.99 m (전진 0.50 + 후진 0.49 m, 전환 1회) — prepare_figures.py 가 같은 사례를 다시 계획'),
     ('forklift 1e3cdeb', 'D7 CPU 판정: 운반 목표 고리 1,686 → 0 (목표당 2,376 계획), 목표까지 길이 중앙값 21.69 → 1.03 m'),
     (FB6, '§3 Hybrid A* 가 왜 뒤로 가는지 · 앞뒤로 돌 때의 특성')],
    '화면 생성: 왼쪽은 위 실행의 고정 시점 영상에 경로와 휩쓸림 띠를 겹친 것, 2배속 · 재계획 순간 2.5 s 정지 · 왼쪽 위 단계 라벨 (prepare_reverse_clip.py) · 오른쪽은 플래너 재실행 그림 (prepare_figures.py) · 색 범례는 슬라이드 범례')

# ----------------------------------------------------------------- approach cases A-D (v3)
AD = 'ws1 artifacts/20261012_meeting_ad'
AD_LEGEND = legend(  # 2026-10-14 (user): the brief's drawings removed, clips side by side
                   ('line', RC_BLUE, '전진 경로'), ('line', RC_ORANGE, '후진 경로'))


def ad_rows(cells):
    return ''.join(
        f'<div class="row"><p class="cap"><b>{case}</b>{what}</p><div class="body">'
        f'{video(clip, f"{case} 상황의 시뮬레이션. {what}", cls="media")}</div></div>'
        for clip, case, what in cells)


AD_SOURCES = [
    (AD, 'meeting_ad3.sbatch (v3, 2026-10-12): 녹화 실행과 같은 현재 설정(d7 팔, 실측 차체, LiDAR 1대, SLAM)에 정렬 직진 0.8 m(임무 영상은 2.1 m) · 복귀 없음(하역까지) · seed 5 · 출발점을 인식 자리 0.3 m 뒤에 둠(--start-rear) · 관측 후보 하나 · 고정 시점(--extra-views quarter, 눈 0.6, −5.0, 7.0 · 대상 0.6, 1.1, 0 · 초점 2.2). 스냅숏 p5_s4b_b66271f_worldbox = b66271f + 월드 좌표 상자(new_obstacles.py frame: world) + --start-rear (run_transport.py, WORLDBOX_PATCH.txt)'),
    (QUEST, '예시 A–D 그림 (8–11쪽) — 같은 배치로 실행 (그림은 2026-10-14 화면에서 뺌, 사용자 지시)'),
]
add('접근 상황 A · B', '과제 접근 시나리오 A · B', 45, f"""
<h2 class="headline">A는 직진으로, B는 S자 곡선으로 진입 (제안서와 같은 배치)</h2>
<div class="m7-cases2 grow">{ad_rows([
    ('56_case_a.mp4', 'A 정면 정렬', '1.15 m 전진 → 삽입'),
    ('56_case_b.mp4', 'B 측방 오프셋', 'S자 곡선 2.3 m → 재관측 → 삽입'),
])}<p class="legend">{AD_LEGEND}</p></div>
<div class="takeaway">B는 측방 오프셋 약 0.4 m까지 전 · 후진 전환 없이 진입합니다 (인식 3.6 m, 직진 0.8 m)</div>
""",
    """과제 제안서의 네 가지 접근 상황을 제안서 그림과 같은 배치로 시뮬레이션했습니다. 영상은 팔레트가 오른쪽에 오도록 비스듬한 상부 시점에서 본 것으로, 왼쪽이 A, 오른쪽이 B입니다. 파란 선은 전진, 주황 선은 후진 경로입니다. A는 팔레트 정면에서 인식해 그대로 직진 삽입합니다. B는 팔레트에 대해 측방으로 비켜 있는 경우로, S자 곡선으로 진입해 곡선 끝에서 한 번 재관측한 뒤 삽입합니다. 다만 팔레트 인식 거리가 약 3.6미터이고 마지막 0.8미터는 직진해야 하므로, 전 · 후진 전환 없이 곡선 하나로 보정할 수 있는 측방 오프셋은 약 0.4미터입니다. 이보다 크게 벗어나 있으면 전 · 후진 전환이 필요합니다. (전환)""",
    AD_SOURCES + [
        (f'{AD}/v3_A · v3_B', 'A 출발 (−0.5, 1.17, 0.006) → 인식 (−0.2, 1.17) 카메라–앞면 2.35 m → 1.15 m 전진 · 정렬 직진 0.8 m · 삽입, 하역 19.3 mm; B 출발 (−1.65, 0.82, 0) → 인식 (−1.35, 0.82) 3.51 m · 축에서 0.35 m → 2.33 m 전진(기어 전환 없음), 하역 25.1 mm. 둘 다 success complete, 금지 접촉 0'),
        ('계산 · 기록', '인식 성공 3.55 · 3.64 m, 실패 4.09 · 4.29 · 4.57 m (case_B* 기록, 깊이 잡음 없는 합성 영상). 정렬 직진 시작의 뒤차축은 앞면에서 0.11 + 1.29 + 0.8 = 2.20 m, 카메라 3.6 m 일 때 뒤차축은 3.6 + 0.959 = 4.56 m → 곡선 구간 2.36 m, 반경 3.45 m S자의 옆 이동 2R(1 − cos(asin(2.36 / 2R))) ≈ 0.42 m')],
    '화면 생성: 위 실행의 고정 시점 영상, 인식부터 리프트까지 2배속, 진행 중인 계획을 바닥에 겹침 · 왼쪽 위 단계 라벨 (prepare_ad_clips.py)')

add('접근 상황 C · D', '과제 접근 시나리오 C · D', 55, f"""
<h2 class="headline">C는 후진 후 재접근, D는 전 · 후진을 반복해 정렬</h2>
<div class="m7-cases2 grow">{ad_rows([
    ('56_case_c.mp4', 'C 근접', '1.3 m 후진 → 1.5 m 전진 정렬 → 삽입'),
    ('56_case_d.mp4', 'D 근접 · 장애물', '전 · 후진 4회 정렬 → 삽입'),
])}<p class="legend">{AD_LEGEND}</p></div>
<div class="takeaway">A–D 모두 팔레트에 닿지 않고 하역까지 마쳤습니다</div>
""",
    """C는 팔레트 바로 앞에서 오른쪽으로 비켜 있어 그대로는 진입할 수 없는 경우로, 먼저 1.3미터 후진해 거리를 확보한 뒤 방향을 맞춰 삽입합니다. D는 같은 위치에서 바로 뒤에 벽, 왼쪽에 장애물이 있는 경우입니다. 후방 공간이 부족하므로, 협소 공간에서 전진과 후진을 네 차례 반복해 방향을 맞춘 뒤 삽입했습니다. 이 배치에서는 마지막 정렬 직진 구간을 현재 임무와 같은 2.1미터로 두면 직진 시작 위치가 뒤쪽 벽과 겹치므로, 네 시나리오 모두 0.8미터로 줄여 실행했습니다. 네 경우 모두 포크와 팔레트의 접촉 없이 하역까지 완료했습니다. 지금까지가 시뮬레이션에서 개발한 소프트웨어이고, 이제 이를 실차에 구현하기 위한 하드웨어를 말씀드리겠습니다. (전환)""",
    AD_SOURCES + [
        (f'{AD}/v3_C · v3_D', 'C 출발 (0.38, 0.87, 0) → 인식 (0.68, 0.87) 포크 끝–앞면 1.1 m · 축에서 0.3 m 오른쪽 → 1.25 m 후진 · 1.52 m 전진, 하역 24.3 mm; D 같은 자리 + 뒤 벽(앞면이 인식 자리 차체 뒤 0.5 m, 0.4 × 2.27 × 1.3 m) · 왼쪽 막이(1.63 × 0.66 × 1.3 m, 팔레트 왼쪽 0.25 m 바깥) — d_walls2.yaml → 1.75 m 전진 · 1.91 m 후진 · 0.47 m 전진 · 0.14 m 후진, 하역 13.6 mm. 둘 다 success complete, 금지 접촉 0'),
        ('사전 영역 (sim/isaac/run_transport.py, observation_viewpoints.BAY_PICKUP_ZONE)', '인식 전에는 팔레트가 있을 수 있는 영역(x 2.1–4.1, y −0.7–2.0 m)이 장애물이라 포크 끝을 앞면에서 약 1.1 m 보다 가까이 둘 수 없음 — 출발을 더 붙인 v2 실행은 invalid_start'),
        ('ad2_preview.py (CPU 미리보기)', 'D 배치에서 정렬 직진 2.1 m 는 approach:invalid_goal, 0.8 m 는 여러 번 앞뒤 전환으로 계획')],
    '화면 생성: 위 실행의 고정 시점 영상, 인식부터 리프트까지 2배속, 진행 중인 계획을 바닥에 겹침 · 왼쪽 위 단계 라벨 (prepare_ad_clips.py)')

# ----------------------------------------------------------------- 10
MISSION_VIDEO = '71_mission.mp4'
MISSION_FLOW = [  # stage in the clip's order, how it is done in this run (2026-10-12: a flow beside the clip, not a table)
    ('팔레트 인식', '규격 치수 기반 형상 규칙'),
    ('접근 · 삽입', 'Hybrid A* 접근 → 직진 삽입'),   # re-observation step dropped (user, 2026-10-13)
    ('적재 · 운반', '리프트 → 운반, 앞에 장애물이 있으면 정지'),   # plain words (user, 2026-10-14); the occupancy-grid detail is answered orally (QNA)
    ('하역', 'ICP 스캔 정합 → 위치 보정'),
    ('복귀', '후진 선회로 방향 전환 → 전진 복귀'),
]
mission_flow = ''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in MISSION_FLOW)
add('운반 임무 전체', '운반 임무 전체', 45, f"""
<h2 class="headline">인식부터 복귀까지 한 임무로 자율 수행 (실측 차체 모델)</h2>
{stage(mpanel(video(MISSION_VIDEO, '공장 홀을 상부 시점에서 본 지게차. 팔레트를 인식해 적재하고, 목적지에 하역한 뒤 출발점으로 복귀한다'),
              legend(('line', PLAN, '주행 경로'), ('ring', GOAL, '목적지'))),
        ipanel('임무 흐름 (삽입 중 추적 미적용 실행)', f'<ol class="m7-vflow">{mission_flow}</ol><p class="m7-vnote"><b>위치 추정</b>전 구간에서 휠 오도메트리를 SLAM으로 보정</p>'), 424)}
<div class="takeaway">하역 오차 19 mm, 복귀 오차 23 mm로 팔레트에 닿지 않고 임무를 마쳤습니다</div>
""",
    """먼저 현재 시뮬레이션에서 처음부터 끝까지 연속으로 수행되는 운반 임무를 보여 드리겠습니다. 실측 차체 모델로 팔레트를 인식하고, 포크를 삽입해 적재한 뒤, 목적지에 하역하고 출발점으로 복귀합니다. 영상은 12배속입니다. 이 실행의 하역 오차는 19밀리미터, 출발점 복귀 오차는 23밀리미터였으며, 포크와 팔레트의 접촉은 없었습니다. 하역 뒤에는 후진으로 크게 선회해 방향을 바꾼 다음 전진으로 돌아오고, 출발점에서는 짧게 후진해 출발 자세에 맞춥니다. 오른쪽은 영상의 진행 순서에 따른 단계별 구현입니다. 위치 추정은 slam_toolbox 기반의 일반적인 구성이므로 부록으로 돌리고, 인식, 삽입, 경로 계획은 소프트웨어 부분에서 설명드리겠습니다. 삽입 중 포켓 추적은 별도 실행으로 보여 드립니다. 이 결과를 사람이 운전하는 지게차의 시험 기준과 비교해 보겠습니다. (전환)""",
    [('ws1 artifacts/20261012_return_forward/seed_5_fwd7', 'forklift 33d46b9 (브랜치 feat/return-turnaround = 6bf45a8 + 복귀 전진 우선, docs/plans/2026-10-12-return-forward-turnaround.md) 의 스냅숏 p5_retturn_6bf45a8_v7(커밋 직전 판, 이 실행의 결정은 같음), 실측 차체 · SLAM 위치 · LiDAR 1대 · --d7-planner --d7-docking --return-turnaround · --video --robot-camera (근접 추적 끔). result.json: success, complete, 하역 19.4 mm, 복귀 2.3 cm · 0.020 rad, 금지 접촉 0, 진입 319.9 / 318.1 mm, 시뮬 244.3 s'),
     ('같은 실행 paths.json · result.json live_plans (복귀)', '첫 실시간 복귀 계획 172.09 s: 직접 계획(전 구간 후진 22.8 m, 비교 비용 70.1)과 최대 곡률 후진 호 후보 10개(곡률 0.25 /m, 후진 가중 3) 중 reverse_arc:-1:90 선택(비용 56.6) — 설치 경로 전진 22.9 m · 후진 8.7 m(호 + 출발점 주차), cusp 정체 · 허가 밖 진입 없음'),
     ('ws1 artifacts/20261011_meeting_video/seed_5_d7', '이전 녹화(forklift b66271f, 전환 없음): 같은 장면 · 같은 하역 19.4 mm · 진입 319.9 / 318.1 mm, 복귀는 전 구간 후진 22.8 m, 복귀 2.7 cm · 0.040 rad, 시뮬 219.6 s'),
     ('ws1 artifacts/20261011_meeting_video/seed_1_d7', '같은 조건 장면 1: success, 하역 27.0 mm, 복귀 5.1 cm, 금지 접촉 0, 시뮬 273.8 s'),
     ('config/isaac_transport_measured.yaml', '목적지 도킹: 미리 등록한 위치의 LiDAR 스캔 정합 (등록 위치는 시뮬레이터 값)'),
     ('src/forklift_core/perception/pocket_detector.py', 'Depth-only geometric baseline for a known, horizontal pallet shape'),
     ('src/forklift_core/localization/slam_pose.py · scan_match.py · scan_docking.py', 'map<-base = map<-odom(SLAM) × odom<-base(odometry); point-to-line ICP 목적지 도킹'),
     ('src/forklift_core/control/path_tracking.py', 'RearAxlePathTracker — 뒤차축 pure pursuit (곡률 = 2 · 횡오차 / 거리²), 전환점마다 정지'),
     ('sim/isaac/run_transport.py', '이 녹화 실행은 근접 추적 끔: 정렬 직진 시작(2.1 m)에서 한 번 더 관측(near capture) 후 그 위치로 삽입')],
    '화면 생성: 위 장면 5 기록을 글자 없이 다시 합성한 영상(ws1 artifacts/20261012_meeting_clean/mission_fwd.mp4, Slurm 2494)의 조감 칸 12배속 (prepare_clips.py mission)')

# ----------------------------------------------------------------- 11
# 2026-10-13 (user, option 3): the exam's tolerances are absolute values for a full-size truck, so a
# pass against them says little for a vehicle with 36 cm forks; the slide now shows the exam's items
# carried over as our own measurements, with the tolerances asked of Riibotics (gauges removed).
EXAM = [  # item, exam rule (full-size truck), our measurement (simulation); tolerance column removed (user, 2026-10-13)
    ('하역 위치', '20 cm 넘게 어긋나면 실격', '하역 오차 최대 2.9 cm'),
    ('포크 삽입', '20 cm 넘게 덜 넣으면 실격', '덜 넣은 거리 최대 3.7 cm'),
    ('운반 중 포크 높이', '20–30 cm 유지, 50 cm 넘으면 실격', '포크 중심 20.5 cm'),
    ('낙하 · 밀림', '낙하하거나 밀면 실격', '낙하 · 밀림 없음'),
    ('틸트', '마스트를 기울여 운반', '틸트 기구 없음'),
]
exam_rows = ''.join(f'<tr><td class="it">{a}</td><td>{b}</td><td class="ours">{c}</td></tr>' for a, b, c in EXAM)

add('자격시험 기준 비교', '지게차운전기능사 실기 판정 항목', 55, f"""
<h2 class="headline">시뮬레이션 결과와 실기시험 판정 기준 비교</h2>
<div class="m7-info grow"><div class="tb"><table class="comparison m7-exam"><tr><th>항목</th><th>실기시험 (실제 지게차)</th><th>개발 차량 (시뮬레이션)</th></tr>{exam_rows}</table></div></div>
<div class="takeaway">실제 지게차 규모의 허용치는 개발 차량에 맞지 않아, 정해 주시는 허용치로 평가하겠습니다</div>
""",
    """비교 기준은 지게차운전기능사 실기시험입니다. 시험은 팔레트를 적재해 코스를 주행한 뒤 하역하는 과제로, 작업 흐름이 본 임무와 비슷합니다. 다만 시험의 허용치는 실제 지게차 규모의 절대값이라, 포크 길이가 36센티미터인 개발 차량에 그대로 대면 합격 여부가 큰 의미를 갖지 않습니다. 그래서 시험이 보는 항목을 개발 차량의 판정 항목으로 옮겨 시뮬레이션에서 측정했습니다. 완주한 실행 가운데 하역 오차는 최대 2.9센티미터, 덜 넣은 거리는 최대 3.7센티미터였고, 운반 중 포크 높이는 포크 중심 기준 20.5센티미터였습니다. 낙하나 밀림은 없었고, 이 항목은 규모와 상관없이 그대로 적용합니다. 마스트를 기울이는 틸트 기구는 없습니다. 나머지 항목의 허용치와 틸트 없는 운반의 허용 여부는 마지막에 여쭙겠습니다. 시험 코스는 치수가 차폭의 배수로 정해져 있어, 개발 차량 규모로 줄여 시뮬레이션 평가에 쓸 수 있습니다. (전환)""",
    [(QNET, '「[공개문제] 지게차운전기능사」 코스운전 및 작업 (한국산업인력공단, 2025-12-22 등록) — 유의사항 7 주행 중 포크 20–30 cm 유지, 실격 (8) 화물 · 파렛트 낙하 (9) 파손 (10) 포크로 드럼통 터치 (14) 포크 50 cm 초과 (15) 하역 20 cm 초과 (16)(17) 밀림 (18) 덜 삽입 20 cm 초과; 팔레트에 닿는 것 자체는 실격 아님. 코스 치수는 D(좌우 최외측 타이어 바깥 간 거리)의 배수. 도면은 저작물이라 화면에 싣지 않음'),
     ('같은 문서', '시험 시간 4분 — 코스 · 차체 규모가 달라 비교에서 제외 (속도 · 작업 시간은 자율 동작 완성 뒤 단계)'),
     (S4B, '하역 6.74 mm, 진입 323.5 / 322.2 mm (캐리지 한계 0.346 m) · 캐리지 앞면–팔레트 간격 22.1 mm, 금지 접촉 0, 팔레트 밀림 없음; 운반 중 승강 관절 0.165 m (명령 lift_target_m 0.2 에 못 미침) → 포크 중심 0.205 m · 밑면 0.193 m · 윗면 0.218 m (fork_center_height 0.04, 두께 0.025)'),
     ('현재 설정 완주 실행의 하역 오차', 'D7 v2 9회 3.0–22.6 mm, 녹화 장면 5 · 1: 19.4 · 27.0 mm, S4b dev9(seed 0–8, smoke 와 같은 스크립트 · 설정) 완주 8회 5.8–29.4 mm → 최대 29.4 mm = 기준 200 mm 의 14.7 % (D7 이전 6주차 실행 8.0 · 23.8 · 64.9 mm 는 제외)'),
     ('현재 설정 실행의 캐리지 앞면–팔레트 간격', 'insertion_measured: D7 v2 20.4–26.1 mm, 녹화 장면 5 · 1: 25.6 · 35.5 mm, dev9 21.7–37.4 mm → 약 2–4 cm'),
     ('week-05/SCRIPT.md', '10쪽 표준 운용 절차 대조 — 틸트 기구 없음'),
     (FB6, '§2 실제 지게차 자격증 시험 기준과 우리 지게차 비교 표 (3주차 피드백: 국가공인 시험의 표준 운용 방법)'),
     ('사용자 결정 (2026-10-13)', '허용치가 실제 지게차 규모의 절대값이라 개발 차량(포크 36 cm)에 합격 판정은 의미가 약함 → 시험 항목을 판정 항목으로 옮겨 측정값만 보이고 허용치는 확인 요청 (안 3)')],
    '출처: Q-Net 공개문제 원문 (2025) · 실행 기록')

# ----------------------------------------------------------------- 12
CONCLUSION = [  # group, what we found, so, direction -- hardware and software apart (user, 2026-10-12)
    ('소프트웨어', [('실측 조향각 15°', '최소 회전 반경 약 2.5 m', '전 · 후진 전환 경로 계획'),
                 ('근접 시 포켓 입구 시야 이탈', '포켓 직접 검출 불가', '윗판 기반 추적 · 직전 보정 · 간격 감시')]),
    ('하드웨어', [('기존 제어기', '릴레이 On/Off 제어만 가능', '자체 구동 보드 (속도 · 조향각 제어)'),
                ('상단 카메라 장착', '삽입 마지막 약 0.25 m 관측 불가', '캐리지 하단 장착'),
                ('무압축 깊이 영상', 'Wi-Fi 실시간 전송 곤란 (약 200 Mbit/s)', '차량 내 기록 · 상태만 전송 · 독립 비상정지'),
                ('LiDAR 높이 1.05 m', '그보다 낮은 바닥 장애물 감지 불가', '운용 가정으로 명시 · 현장 조건 확인')]),
]
GROUP_CLS = {'하드웨어': 'hw', '소프트웨어': 'sw'}


def concl_row(group, n, i, row):
    a, b, c = row
    grp = f'<td class="grp {GROUP_CLS[group]}" rowspan="{n}">{group}</td>' if i == 0 else ''
    return f'<tr>{grp}<td class="key">{a}</td><td class="cur">{b}</td><td class="arrow">→</td><td class="nxt">{c}</td></tr>'


concl_rows = ''.join(concl_row(group, len(rows), i, row) for group, rows in CONCLUSION for i, row in enumerate(rows))
add('결론', '확인 사항과 설계 방향', 30, f"""
<h2 class="headline">실측과 시뮬레이션에서 확인한 제약으로 설계 방향 확정</h2>
<div class="m7-info grow"><div class="tb"><table class="comparison plan6 m7-concl"><tr><th class="c0">구분</th><th class="c1">확인 사항</th><th class="c2">영향</th><th class="c3"></th><th class="c4">설계 방향</th></tr>{concl_rows}</table></div></div>
<div class="takeaway">다음 목표는 시뮬레이션 임무를 실차로 옮기는 것입니다</div>
""",
    """정리하면, 실측 차체와 시뮬레이션에서 확인한 사항을 근거로 소프트웨어와 하드웨어의 설계 방향을 정했습니다. 소프트웨어는 회전 반경이 크므로 전 · 후진 전환 경로를 도입했고, 근접 구간에서 포켓 입구가 시야를 벗어나므로 윗판 기반 추적과 직전 보정, 간격 감시로 삽입을 완료합니다. 하드웨어는 이 소프트웨어의 속도 · 조향 명령을 실행하도록 기존 제어기 대신 구동 보드를 제작하고, 삽입 완료까지 관측하도록 카메라를 캐리지 하단으로 옮깁니다. 깊이 영상은 Wi-Fi로 전송하지 않고 차량에서 기록하며, 비상정지는 독립된 경로로 둡니다. LiDAR 높이보다 낮은 바닥 장애물이 없다는 가정은 현장 조건으로 확인받고자 합니다. 다음 목표는 이 임무를 실차로 이식하는 것입니다. (전환)""",
    [(MEASURED, '실측 조향 15°, 회전 반경 2.46 m (사진 추정 1.32 m)'),
     (NEARPLAN, '기존 장착 마지막 약 0.25 m 무관측'),
     ('week-05/SCRIPT.md', '기존 제어기 릴레이 on/off, 속도 조절 기능 없음'),
     ('12쪽 시스템 구성 출처', '무압축 깊이 848 × 480 · 30 fps 약 195 Mbit/s (계산), 무선 E-stop 은 Wi-Fi 와 별도'),
     ('forklift CLAUDE.md', '과제 센서 구성(RGB-D 1 · 2D LiDAR 1) 유지, 낮은 장애물은 운용 가정'),
     ('src/forklift_core/perception/roof_tracking.py', '포켓 입구가 시야를 벗어난 뒤 윗판 가장자리로 추적 (7쪽)'),
     (FB6, '§2 결론 장표 — 무엇이 어떻게 달라지니까 무엇으로 가야 하는지'),
     ('사용자 지시 (2026-10-12)', '하드웨어 · 소프트웨어를 나눠 보임 · 소프트웨어 → 하드웨어 순서')],
    '출처: 앞 장들의 결과 정리')

# ----------------------------------------------------------------- 13
# 2026-10-12 (user): the schedule as a Gantt chart, from the start of development to the end. The bars
# up to 10/12 are what was done (dates from the repositories' history, sources below); from 10/16 the
# plan of the development roadmap's calendar. Weeks start on Friday (roadmap section 4).
G0, G1 = date(2026, 9, 4), date(2026, 12, 21)          # semester week 1 Friday .. the last exam day
GSPAN = (G1 - G0).days + 1
SW_C, HW_C, CO_C, TODAY_C = BLUE, ORANGE, '#6b7480', '#d0342c'
GANTT = [  # group, colour, rows: (label, [(start, end, state)])  state: done / plan
    ('소프트웨어', SW_C, [
        ('개발 계획 · 시뮬레이션 환경', [('09-08', '10-01', 'done')]),
        ('팔레트 인식 · 삽입 중 포켓 추적', [('09-11', '10-12', 'done')]),
        ('위치 추정 · 장애물 지도 · 경로 계획', [('09-17', '10-12', 'done')]),
        ('접근 시나리오 A–D 반복 평가', [('10-01', '10-12', 'done'), ('10-16', '10-22', 'plan')]),
        ('실물 센서 · Jetson 연동', [('10-30', '11-12', 'plan')]),
        ('실차 위치 추정 · 실물 팔레트 인식', [('11-13', '11-26', 'plan')]),
        ('실차 전체 임무 A → B · C · D', [('11-27', '12-10', 'plan')])]),
    ('하드웨어', HW_C, [
        ('부품 선정 (센서 · 컴퓨터)', [('09-10', '09-17', 'done')]),
        ('차체 입고 · 실측 · 기존 제어기 분석', [('09-23', '09-30', 'done')]),
        ('구동 보드 설계 · 모터 전류 실측', [('09-28', '10-12', 'done'), ('10-16', '10-22', 'plan')]),
        ('구동 보드 제작 · 속도 · 조향 제어', [('10-30', '11-12', 'plan')]),
        ('센서 장착 · 캘리브레이션 · 시험 팔레트', [('11-13', '11-26', 'plan')]),
        ('실차 반복 시험 · 가정값 실측 교체', [('11-27', '12-10', 'plan')])]),
    ('공통', CO_C, [('최종 시연 준비 (15주차 가정)', [('12-11', '12-17', 'plan')])]),
]
G_EXAMS = [('10-23', '10-29', '중간고사'), ('12-18', '12-21', '기말')]
G_TODAY = ('10-14', '10/14 중간 미팅')


def gday(md):
    m, d = map(int, md.split('-'))
    return date(2026, m, d)


def gx(md, end=False):
    return f'{((gday(md) - G0).days + (1 if end else 0)) / GSPAN * 100:.2f}%'


def gantt():
    cells, r = [], 2
    n = sum(len(rows) for _, _, rows in GANTT)
    weeks = [G0 + timedelta(days=7 * k) for k in range(16)]
    ticks = ''.join(f'<span style="left:{gx(w.strftime("%m-%d"))}">{w.month}/{w.day}</span>' for w in weeks[:-1])
    lines = ''.join(f'<i style="left:{gx(w.strftime("%m-%d"))}"></i>' for w in weeks[1:])
    exams = ''.join(f'<b style="left:{gx(a)};width:calc({gx(b, True)} - {gx(a)})"><em>{t}</em></b>' for a, b, t in G_EXAMS)
    today = f'<u style="left:{gx(G_TODAY[0], True)}"></u>'
    cells.append(f'<div class="ax" style="grid-row:1;grid-column:3">{ticks}'
                 f'<span class="now" style="left:{gx(G_TODAY[0], True)}">{G_TODAY[1]}</span></div>')
    cells.append(f'<div class="ov" style="grid-row:2 / span {n};grid-column:3">{lines}{exams}{today}</div>')
    for group, colour, rows in GANTT:
        cells.append(f'<p class="grp" style="grid-row:{r} / span {len(rows)};color:{colour}">{group}</p>')
        for i, (label, segs) in enumerate(rows):
            first = ' first' if i == 0 else ''
            bars = ''.join(
                f'<span class="{st}" style="left:{gx(a)};width:calc({gx(b, True)} - {gx(a)});'
                f'{"background:" + colour if st == "done" else "background:" + colour + "73;border-color:" + colour}"></span>'
                for a, b, st in segs)
            cells.append(f'<p class="lb{first}" style="grid-row:{r}">{label}</p>'
                         f'<div class="tl{first}" style="grid-row:{r}">{bars}</div>')
            r += 1
    return f'<div class="m7-gantt grow">{"".join(cells)}</div>'


GANTT_LEGEND = legend(('cell', SW_C, '소프트웨어'), ('cell', HW_C, '하드웨어'), '|',
                      ('cell', '#5a5f66', '수행'), ('band', '#5a5f66', '예정'), '|',
                      ('dash', TODAY_C, '중간 미팅 (10/14)'), ('cell', '#e3e6ea', '시험 기간'))
add('개발 일정', '개발 일정', 35, f"""
<h2 class="headline">시뮬레이션과 구동 보드 설계 후 11월 실차 주행, 12월 중순 시연</h2>
{gantt()}
<p class="m7-glegend legend">{GANTT_LEGEND}</p>
<div class="takeaway">실차 일정은 구동 보드 제작 시점에 따라 움직이며, 시연일은 15주차로 가정했습니다</div>
""",
    """개발 일정입니다. 빨간 점선이 오늘 미팅 시점으로, 왼쪽이 지금까지 수행한 내용이고 오른쪽이 앞으로의 계획입니다. 9월 초 개발 계획을 세운 뒤, 소프트웨어는 시뮬레이션 환경과 팔레트 인식을 시작으로 경로 계획, 위치 추정과 장애물 지도, 삽입 중 포켓 추적을 개발했습니다. 하드웨어는 부품을 선정하고, 9월 하순 차체가 입고된 뒤 실측과 기존 제어기 분석을 마쳤으며, 현재 구동 보드를 설계하고 있습니다. 중간고사 전에는 모터 전류를 실측해 구동 보드 PCB를 설계하고, 시뮬레이션에서 A–D를 여러 장면으로 반복 평가합니다. 중간고사 이후에는 구동 보드를 제작하고 Jetson에 센서를 연동합니다. 11월 중순부터 실차 위치 추정과 팔레트 인식을, 12월 초까지 실차 전체 임무를 검증하고, 마지막 주에 최종 시연을 준비합니다. 일정은 실물 진행 상황에 따라 조정될 수 있습니다. (전환)""",
    [('docs/plans/2026-09-11-development-roadmap.md', '§4 달력 대응: 학기 주차는 금요일 시작(1주차 09/04), 8주차 10/23–29 중간고사, 9–10주차 10/30–11/12, 11–12주차 11/13–11/26, 13–14주차 11/27–12/10, 15주차 12/11–17 예비 · 최종 시연일 미정(15주차 가정), 16주차 12/18–21 기말고사'),
     ('forklift-presentations git 이력', '2주차 개발 계획 자료 2026-09-08–09'),
     ('forklift git 이력 (수행 막대)', '09/10 저장소 · 하드웨어 결정(ADR 0001), 09/11 Gazebo 정적 장면, 09/13–16 포켓 검출 · 평가, 09/17 Isaac Sim 전환(ADR 0004) · Hybrid A* 운반, 09/19 검출기 Isaac 연동, 09/26 공장 홀 · LiDAR SLAM, 10/01 실측 차체 모델 · A–D 재검증, 10/04 캐리지 하단 장착, 10/05–08 점유 격자 · 주행 허가 · 단일 LiDAR · D7, 10/08–12 근접 추적(D8) · 운반 복구, 10/12 A–D 렌더 (meeting_ad)'),
     ('docs/hardware.md · docs/decisions/0001', 'D435i 확정 · RPLIDAR A2 계열 · Jetson 권장안 (2026-09-10, A2M12 기대 09/15)'),
     ('docs/validation/2026-09-23-chassis-intake.md', '차체 입고 · 초기 구조 조사 2026-09-23'),
     ('week-05/SOURCES.md', '실측 사진 2026-09-29–30, 팀 실측 09/30, 제어기 역분석 보고 09/30, 모터 드라이버 · 엔코더 선정 · 회로 초안(5주차 자료 09/28–30); 모터 수치 · IPROPI 검토 10/12 (15쪽)'),
     ('week-06/build_deck.py', '8쪽 다음 작업: 모터 전류 실측 → 전류 제한 · 방열 → PCB, 가정값 실측 교체, 센서 브래킷'),
     ('docs/references/week3_feedback.md', '시험 팔레트 만드는 방법(3D 프린터 · 스티로폼 · 목재 재단) — 11/13–26 배치는 팀 확인 전 제안'),
     ('사용자 지시 (2026-10-12)', '일정은 간트 차트로, 개발 시작부터 끝까지')],
    '출처: 개발 로드맵 달력 · 저장소 이력 · 6주차 다음 작업 (실물 일정은 팀 계획)')

# ----------------------------------------------------------------- 14
QUESTIONS = [  # group (week 4 feedback: asked / decided / provided), items; (True, ...) = ask first
    # 2026-10-13 (user): no "키워드: 설명" lines -- they read as translated English; plain Korean questions.
    ('여쭐 사항', [(True, '오늘 보여 드린 운반 임무가 실제 작업 흐름과 맞나요?'),
               (True, '하역 오차와 삽입 깊이는 어디까지 허용되고, 삽입 직전 정지와 틸트 없는 운반도 괜찮나요?'),
               (False, '포크 높이를 정밀하게 맞춰야 하나요? 허용 오차는 어느 정도인가요?'),
               (False, '현장에는 지게차가 동시에 몇 대 투입되고, 이를 관리하는 중앙 서버가 있나요?')]),
    ('정해 주실 사항', [(True, '팔레트와 목적지 위치를 미리 알려 주시나요, 로봇이 직접 찾아야 하나요?'),
                  (False, '실내인지 실외인지, 통로 폭과 바닥, 장애물과 작업자 동선은 어떤가요?'),
                  (False, '저희가 정한 팔레트 규격(EPAL 6, T11 0.6배 축소판, 적재 10 kg 이하)으로 개발과 시연을 이어가도 될까요?'),   # user, 2026-10-14: ask for approval of our choice, not T11's opening
                  (False, '시연은 어떤 코스와 환경에서 진행하나요?'),   # user, 2026-10-14
                  (False, '원격 정지는 어느 수준까지 필요한가요?')]),
    ('요청 자료', [(False, '작업장 도면, 운용 영상, 사용하는 팔레트 도면을 받을 수 있을까요?')]),
]
q_rows = ''.join(
    ''.join(f'<tr{" class=pri" if first else ""}>{f"<td class=grp rowspan={len(items)}>{group}</td>" if i == 0 else ""}<td class="item">{item}</td></tr>'
            for i, (first, item) in enumerate(items)) for group, items in QUESTIONS)
add('확인 요청', '리보틱스 확인 요청', 75, f"""
<h2 class="headline">작업 범위와 평가 기준, 입력 조건을 먼저 여쭙니다</h2>
<div class="m7-info grow"><div class="tb"><table class="comparison m7-q"><tr><th>구분</th><th>질문</th></tr>{q_rows}</table></div></div>
<div class="takeaway">실차 시험의 운용 조건과 판정 기준을 함께 정하고자 합니다</div>
""",
    """마지막으로 리보틱스 측에 확인을 요청드릴 사항입니다. 파랗게 표시한 세 가지를 우선 여쭙고자 합니다. 첫째, 오늘 보여 드린 운반 임무가 실제 작업 흐름과 부합하는지입니다. 둘째, 시연 판정 기준입니다. 하역 오차와 포크 삽입 깊이의 허용치, 현재와 같이 삽입 직전에 정지해 재관측하는 방식의 허용 여부, 틸트 없는 운반의 허용 여부입니다. 셋째, 팔레트와 목적지 위치를 시스템에서 제공받는지, 로봇이 직접 탐색해야 하는지입니다. 이와 함께 포크 높이를 정밀하게 조절해야 하는지, 현장에 지게차가 동시에 몇 대 투입되고 이를 관리하는 중앙 관제 서버가 있는지도 여쭙고자 합니다. 그 밖에 운용 환경, 시연 코스, 원격 정지 수준도 정해 주시면 설계에 반영하겠습니다. 팔레트는 저희가 정한 EPAL 6과 T11 0.6배 축소판, 적재 10킬로그램 이하 기준으로 개발과 시연을 이어가도 될지 여쭙고자 합니다. 작업장 도면, 운용 영상, 팔레트 도면을 제공해 주시면 시뮬레이션 장면을 그에 맞게 구성하겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [(FB4, '§1 미팅 질문 세 구분 — 우리가 궁금한 것(과제 범위 · 평가 기준) · 기업이 제공할 수 있는 것 · 기업이 결정해 줘야 하는 것(예: 실내 · 실외); 파란 세 줄을 먼저 묻는다'),
     ('week-05/build_deck.py', '11쪽 미팅 질문 (실제 운용 상황 · 초기 제공 정보 · 시뮬레이션 설정 적합성)'),
     ('forklift docs/decisions/0002-test-pallet-and-geometry-generality.md', '시험용 팔레트 EPAL 6 (800 × 600 mm) · T11 × 0.6 (660 × 660 mm)는 팀이 정한 규격; T11 진입구 235 / 350 mm 는 표준 원문으로 따로 확인 (docs/design/2026-09-17-t11-test-article-drawing.md)'),
     ('memory: 하드웨어 사실 (2026-10-12)', '들기 10 kg'),
     (FB6, '§1 팀 메모: 리보틱스 미팅 때 물어볼 것이 있음'),
     ('사용자 지시 (2026-10-13)', '질문 추가: 포크 높이 정밀 조절 필요 여부 · 현장 동시 투입 대수와 중앙 관제 서버 유무')],
    '출처: 4–6주차 피드백 · 5주차 미팅 질문 이어 받음')

TITLE = '리보틱스 중간 미팅 · 자율 지게차 중간 점검'
N_SLIDES = 19


# 2026-10-12 (user): the company works on SLAM itself, so the talk follows the brief's items and
# puts the hardware first; the localization slides stay as an appendix for questions (the week 6
# feedback asked for the LiDAR / vision comparison). Same day, later: "요약 -> hw -> sw -> 결론(향후일정)
# -> 질의응답", hardware and software apart, the licence comparison moved to the front; then software
# before hardware, "sw를 어떻게 hw에 구현할건지가 드러나는 스토리텔링".
SECTIONS = [('요약', ['과제 이해와 진행 현황', '운반 임무 전체', '자격시험 기준 비교']),
            ('소프트웨어', ['시뮬레이션 환경', '포켓 인식', '삽입 중 포켓 추적', '새 장애물 대응', '후진을 고르는 이유',
                       '접근 상황 A · B', '접근 상황 C · D']),
            ('하드웨어', ['시스템 구성', '실물 차체', '기존 제어기 분석', '구동 보드 설계']),
            ('결론', ['결론', '개발 일정']),
            ('질의응답', ['확인 요청'])]
SECTION = {label: name for name, labels in SECTIONS for label in labels}
APPENDIX = ('위치 추정',)
ORDER = ['리보틱스 중간 미팅'] + [label for _, labels in SECTIONS for label in labels] + list(APPENDIX)


def build():
    assert len(slides) == N_SLIDES, len(slides)
    # Present the whole mission right after the overview (Codex review 2026-10-11); section
    # numbers follow the final order.
    slides.sort(key=lambda s: ORDER.index(s['label']))
    main = [s for s in slides if s['label'] not in APPENDIX]
    for i, s in enumerate(main[1:], 1):
        s['title'] = f'{i:02d}  {SECTION[s["label"]]} · {s["title"]}'
    for i, s in enumerate((s for s in slides if s['label'] in APPENDIX), 1):
        s['title'] = f'부록{" " + str(i) if len(APPENDIX) > 1 else ""}  {s["title"]}'
        s['seconds'] = 0                    # shown only for questions, outside the timed talk
    total = sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'본 발표 {len(main)}장 · 시간 배분 합계 {total//60}분 {total%60}초, 부록 {len(slides) - len(main)}장(질문 대비). '
              '쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-10-14 (리보틱스 중간 미팅). 결과는 Isaac Sim 합성 장면과 CPU 합성 시험의 결과이며 실제 장비 성능이 아니다. '
              '하드웨어 쪽은 팀 실측 · 역분석 · 회로 초안이고 구동 보드는 아직 제작 전이다. '
              '원고는 발표자 문체(합니다체)로 썼고, (전환)은 다음 쪽으로 넘기는 자리다.', '']
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
                   '', s['notes'], '', '[Sources]', s['foot'], source_lines, '[/Sources]', '']
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
