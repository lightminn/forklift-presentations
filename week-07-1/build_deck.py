"""Build the Riibotics mid-meeting web deck (week 7, part 1) and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

A technical mid-point review for the company that set the assignment (feedback of weeks 4-6:
docs/references/week4-6_feedback.md in the robot repository): what the team understood, the
system, what runs in simulation and what is still hardware work, the conclusions so far, the
schedule and the questions for the company. The plan is PLAN.md. Clips are cut by
prepare_clips.py, the path figures drawn by prepare_figures.py (figures/, inlined here so the
deck font applies). Week 6 clips are reused where the result has not changed.
"""
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


def figure_svg(name):
    """An SVG from prepare_figures.py, inlined (an <img> would not see the deck font)."""
    return (ROOT / 'figures' / name).read_text(encoding='utf-8').replace(
        '<svg xmlns="http://www.w3.org/2000/svg" ', '<svg class="diagram" ')


def tag(kind):
    return f'<span class="m7-tag {kind}">{TAGS[kind]}</span>'


TAGS = {'ok': '확인', 'next': '다음 단계', 'real': '실물 전', 'fixed': '확정', 'chosen': '선정',
        'draft': '설계 중', 'buy': '구매 예정', 'reuse': '기존 재사용', 'plan': '설계 반영 예정'}


# ----------------------------------------------------------------- 1
add('리보틱스 중간 미팅', '자율 지게차\n중간 점검', 20, '',
    """안녕하십니까. 자율 지게차 개발 중간 점검을 발표할 김광민이라고 합니다. 지금까지 만든 것과 남은 일을 기술 위주로 정리하고, 마지막에 리보틱스 측에 확인을 부탁드릴 내용을 말씀드리겠습니다. (전환)""",
    [(QUEST, '과제: 주변 장애물을 고려한 최적의 팔레트 핸들링 경로 생성 및 제어'),
     (FB6, '§1 리보틱스 중간 미팅(형식은 중간 발표), 10/12 교수님 초안 검사 · 10/14 미팅')],
    '중간 미팅')

# ----------------------------------------------------------------- 2
PIPE = [  # step, sim, real
    ('팔레트 인식', '깊이 영상으로 포켓 찾기', '카메라 실물 시험 전'),
    ('로봇 기준 팔레트 위치', '인식 결과를 차체 좌표로', '장착 · 좌표 보정 전'),
    ('장애물 회피 경로', 'LiDAR 1대 지도 + Hybrid A*', 'LiDAR 실물 시험 전'),
    ('삽입 · 포켓 추적 · 적재', '직전 두 번 보정 · 넣는 동안 간격 감시', '구동 보드 제작 후'),
    ('운반 · 하역', 'SLAM 위치로 완주', '구동 보드 제작 후'),
]
pipe_html = ''.join(
    f'<article><span class="n">{"①②③④⑤"[i]}</span><h3>{step}</h3>'
    f'<p>{tag("ok")}{sim}</p><p class="real">{tag("real")}{real}</p></article>'
    for i, (step, sim, real) in enumerate(PIPE))
add('과제 이해와 진행 현황', '01  과제 이해와 진행 현황', 70, f"""
<h2 class="headline">과제 5단계를 시뮬레이션에서 한 임무로 연결 · 실물은 구동부 제작 단계</h2>
<div class="m7-pipe grow">{pipe_html}</div>
<table class="comparison m7-cases"><tr><th>접근 상황 (과제)</th><th>A 정면 정렬</th><th>B 옆으로 비켜 있음</th><th>C 너무 가까움</th><th>D 가깝고 뒤에 장애물</th></tr>
<tr><td>시뮬레이션</td><td>{tag("ok")}직진 삽입</td><td>{tag("ok")}곡선 접근 후 삽입</td><td>{tag("next")}후진 후 삽입</td><td>{tag("next")}공간 안에서 재정렬</td></tr></table>
<div class="takeaway">현재: 인식부터 하역까지 시뮬레이션에서 자율 동작 · 실차 주행은 구동 보드 제작 후 (예정)</div>
""",
    """먼저 과제를 어떻게 이해했고 어디까지 왔는지입니다. 과제 문서의 순서대로 팔레트를 인식하고, 로봇 기준 위치를 구하고, 장애물을 피하는 경로를 만든 뒤, 포켓을 추적하면서 포크를 넣고, 목적지로 옮겨 내려놓는 다섯 단계로 나눴습니다. 다섯 단계는 모두 시뮬레이션에서 한 임무로 이어서 돌아갑니다. 실물은 차체를 재고 기존 제어기를 분석한 단계이고, 구동 보드를 만든 뒤 실차 주행을 시작합니다. 아래 표는 과제가 제시한 네 가지 접근 상황입니다. 정면 접근과 옆으로 비켜 있는 팔레트로의 곡선 접근은 시뮬레이션에서 확인했고, 너무 가까워 먼저 후진해야 하는 C와 뒤에 장애물까지 있는 D는 다음 단계에서 확인합니다. (전환)""",
    [(QUEST, '필수 처리 순서 5단계 · 접근 상황 A–D (8–11쪽)'),
     (S4B, '인식(카메라 깊이) → 위치 → LiDAR 1대 장애물 지도 + Hybrid A* → 근접 추적 삽입 → SLAM 위치 운반 · 하역 · 복귀, 한 임무 완주 (2026-10-11)'),
     ('forklift CLAUDE.md', 'A–D 를 모든 계획기 · 제어기의 시험 사례로 사용; C · D 는 아직 별도 확인 전'),
     (HW, '실물: 차체 실측 · 제어기 역분석 완료, 구동 보드 회로 초안, Jetson 미구매')],
    '출처: 과제 문서 · 로봇 저장소 실행 기록')

# ----------------------------------------------------------------- 3
def block_diagram():
    W, H = 1180, 470
    parts = ['<defs><marker id="bd-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
             'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#5d6670"/></marker></defs>']
    colours = {'fixed': '#2f74c0', 'chosen': '#6a4fb3', 'draft': '#c26a1a', 'buy': '#8c959e',
               'reuse': '#2e9a6b', 'plan': '#c26a1a'}

    def box(x, y, w, h, title, lines, kind, dashed=False, fill='#ffffff'):
        dash = ' stroke-dasharray="8 6"' if dashed else ''
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="#44505c" stroke-width="2"{dash}/>',
               f'<text x="{x + 14}" y="{y + 30}" font-size="21" font-weight="700" fill="#1b1f24">{title}</text>']
        tw = 16 * len(TAGS[kind]) + 16
        out.append(f'<rect x="{x + w - tw - 10}" y="{y + 11}" width="{tw}" height="25" rx="3" fill="{colours[kind]}"/>'
                   f'<text x="{x + w - tw / 2 - 10}" y="{y + 29}" font-size="15" font-weight="700" fill="#fff" text-anchor="middle">{TAGS[kind]}</text>')
        for i, line in enumerate(lines):
            out.append(f'<text x="{x + 14}" y="{y + 58 + 25 * i}" font-size="18" fill="#44505c">{line}</text>')
        return ''.join(out)

    def link(points, label=None, at=None, dashed=False, both=False, anchor='middle'):
        d = ' '.join(f'{x},{y}' for x, y in points)
        dash = ' stroke-dasharray="8 6"' if dashed else ''
        start = ' marker-start="url(#bd-ah)"' if both else ''
        out = f'<polyline points="{d}" fill="none" stroke="#5d6670" stroke-width="2.5"{dash}{start} marker-end="url(#bd-ah)"/>'
        if label:
            x, y = at
            out += f'<text x="{x}" y="{y}" font-size="16" fill="#44505c" text-anchor="{anchor}">{label}</text>'
        return out

    # sensors (left), upper computer (centre), lower control and drive (right), wireless (bottom)
    parts.append(f'<text x="0" y="16" font-size="17" font-weight="700" fill="#2f74c0">센서</text>'
                 f'<text x="410" y="16" font-size="17" font-weight="700" fill="#2f74c0">상위 연산</text>'
                 f'<text x="820" y="16" font-size="17" font-weight="700" fill="#2f74c0">하위 제어 · 구동</text>')
    parts.append(box(0, 30, 300, 112, 'RGB-D 카메라', ['RealSense D435i', '캐리지 하단 · 포켓 인식'], 'fixed'))
    parts.append(box(0, 168, 300, 112, '2D LiDAR', ['RPLIDAR A2 (A2M12 예상)', '높이 1.05 m · 지도 · 장애물'], 'fixed'))
    parts.append(box(410, 30, 310, 250, 'Jetson Orin Nano', ['ROS 2 Jazzy', '팔레트 · 포켓 인식', 'SLAM (slam_toolbox)',
                                                          '경로 계획 (Hybrid A*)', '경로 추종 · 삽입 추적'], 'buy'))
    parts.append(box(820, 30, 360, 112, 'STM32 Nucleo-64', ['속도 · 조향 · 승강 제어', '엔코더 읽기 · 비상 차단'], 'draft'))
    parts.append(box(820, 168, 360, 112, '구동 · 엔코더 보드', ['드라이버 DRV8244 × 3', '엔코더 MT6701 (바퀴 · 조향각)'], 'draft'))
    parts.append(box(820, 306, 360, 70, '모터 3개 · 12 V 배터리', [], 'reuse'))
    parts.append(link([(300, 86), (410, 86)], 'USB 3', (355, 76)))
    parts.append(link([(300, 224), (410, 224)], 'USB 시리얼', (355, 214)))
    parts.append(link([(720, 86), (820, 86)], '명령 · 상태', (770, 74), both=True))
    parts.append(link([(1000, 142), (1000, 168)], both=True))
    parts.append(link([(1000, 280), (1000, 306)], both=True))
    # wireless (not yet designed in: week 6 feedback §5)
    parts.append(f'<text x="0" y="436" font-size="17" font-weight="700" fill="#c26a1a">무선 (추가 설계)</text>')
    parts.append(box(410, 392, 310, 76, '감시 PC', [WIFI_LINE], 'plan', dashed=True, fill='#fff8f0'))
    parts.append(box(820, 392, 360, 76, '무선 비상정지', [ESTOP_LINE], 'plan', dashed=True, fill='#fff8f0'))
    parts.append(link([(565, 392), (565, 280)], 'Wi-Fi', (596, 340), dashed=True, both=True))
    parts.append(link([(820, 430), (790, 430), (790, 236), (820, 236)], '출력 차단', (780, 340), dashed=True, anchor='end'))
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="시스템 구성. 카메라와 LiDAR가 Jetson에, '
            f'Jetson이 STM32 보드에 연결되고, STM32가 드라이버 세 개로 모터를 돌리며 엔코더를 읽는다. 무선 감시 PC와 무선 비상정지는 추가 설계 항목">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


WIFI_LINE = '내장 Wi-Fi · 상태 · 지도만 전송'
ESTOP_LINE = 'Wi-Fi와 별도 · 신호 끊기면 정지'

add('시스템 구성', '02  시스템 구성', 60, f"""
<h2 class="headline">센서 2종 (과제 규격) → Jetson (인식 · 위치 · 경로) → STM32 (모터 · 엔코더)</h2>
<div class="grow m7-fill">{block_diagram()}</div>
<div class="takeaway">무선 설계: 영상은 보내지 않고 상태 · 지도만 Wi-Fi로 · 비상정지는 Wi-Fi와 따로 · 지게차끼리 통신은 운용 대수 확인 후</div>
""",
    """전체 시스템 구성입니다. 센서는 과제 규격대로 RGB-D 카메라 한 대와 2D LiDAR 한 대입니다. 카메라는 RealSense D435i로 캐리지 하단에 달아 팔레트 포켓을 보고, LiDAR는 RPLIDAR A2로 1.05미터 높이에서 지도와 장애물을 봅니다. 상위 연산은 Jetson Orin Nano에서 ROS 2로 인식, SLAM, 경로 계획, 경로 추종을 돌릴 예정입니다. 하위 제어는 STM32 보드가 Jetson의 속도와 조향 명령을 받아 모터 드라이버 세 개로 주행, 조향, 승강 모터를 돌리고, 엔코더로 바퀴 속도와 조향각을 읽습니다. 지난 발표에서 무선 통신을 아직 고려하지 않았다는 지적을 받아, 아래 점선 두 가지를 설계에 넣고 있습니다. 하나는 감시 PC와의 Wi-Fi 연결입니다. Jetson 개발자 키트에는 Wi-Fi 모듈이 들어 있고, 카메라 영상처럼 큰 데이터는 Wi-Fi에서 끊기기 쉬워 상태와 지도, 위치만 보내고 영상은 차에서 기록합니다. 다른 하나는 무선 비상정지입니다. 산업용 로봇처럼 Wi-Fi와 따로 두고, 신호가 끊기면 바로 멈추도록 수신기가 드라이버 출력을 직접 끊게 합니다. 지게차끼리의 통신은 여러 대를 함께 운용하는지 확인한 뒤 정하려고 합니다. (전환)""",
    [(HW, 'D435i 확정 · RPLIDAR A2 계획(A2M12 유력) · Jetson Orin Nano Super 8GB 권장(미구매) · 개발 기준 ROS 2 Jazzy'),
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
CHASSIS_ROWS = [
    ('최대 조향각', '15° → 최소 회전 반경 약 2.5 m', '추정 모델의 2배 → 앞뒤로 방향 맞춤'),
    ('포크 길이', '36 cm', '삽입 목표 33 cm (차체 한계 기준)'),
    ('기존 제어기', '릴레이로 켜기 · 끄기만', '속도 조절 불가 → 자체 구동 보드'),
    ('구동 보드', '드라이버 DRV8244 × 3 · 엔코더 MT6701', '회로 초안 → 모터 전류 실측 후 PCB'),
]
chassis_rows = ''.join(f'<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in CHASSIS_ROWS)
add('실물 차체와 구동부', '03  실물 차체와 구동부', 65, f"""
<h2 class="headline">실측 조향각 15° → 회전 반경 약 2.5 m · 속도 제어를 위해 구동 보드 새로 제작</h2>
<div class="split grow" style="grid-template-columns:0.42fr 1.58fr;gap:26px">
<figure class="shot"><img class="media" src="assets/30_chassis_pallet.jpg" alt="입고한 지게차 차체와 앞에 놓인 동봉 플라스틱 팔레트"></figure>
<div class="stack" style="justify-content:center"><table class="comparison t6 m7-chassis"><tr><th>항목</th><th>실측 · 분석</th><th>영향</th></tr>{chassis_rows}</table></div>
</div>
<div class="takeaway">실물 진행: 차체 실측 · 제어기 분석 완료 → 구동 보드 제작 → 실차 주행 (예정)</div>
""",
    """실물 쪽입니다. 들어온 차체를 직접 재 보니 가장 큰 차이는 조향각이었습니다. 최대 조향각이 15도라 최소 회전 반경이 약 2.5미터로, 사진으로 추정했던 모델의 두 배 가까이 됩니다. 그래서 좁은 곳에서는 앞뒤로 움직이며 방향을 맞춰야 하고, 이 내용은 뒤의 경로 계획에서 다시 말씀드리겠습니다. 포크는 36센티미터라 삽입 목표를 33센티미터로 잡았습니다. 또 기존 제어기를 로직 애널라이저로 분석해 보니, 무선 조종기 신호로 릴레이를 켜고 끄기만 해서 속도를 조절할 수 없었습니다. 그래서 기존 제어기 대신 모터 드라이버 DRV8244 세 개와 자석식 엔코더 MT6701로 구동 보드를 새로 만들고 있습니다. 지금은 회로 초안 단계이고, 모터 전류를 잰 뒤 전류 제한과 방열을 정해 PCB로 만듭니다. (전환)""",
    [(MEASURED, '실측 축간 0.66 m · 윤거 0.53 m · 바퀴 0.125 m · 최대 조향 15° · 포크 360 × 55 × 25 mm'),
     ('계산', '최소 회전 반경 = L / tan δ: 0.66 / tan 15° = 2.46 m, 사진 추정 0.64 / tan 0.45 = 1.32 m (뒤차축, 자전거 모델)'),
     ('forklift CLAUDE.md', '삽입 깊이 규칙 min(깊이 × 0.6, 캐리지 한계 − 16 mm): dls08_measured 346 − 16 = 330 mm (EPAL 6 깊이 600 × 0.6 = 360 mm 보다 작음)'),
     ('week-05/SCRIPT.md', '4–9쪽: DSLogic 파형, 릴레이 on/off · 속도 조절 기능 없음, DRV8244-Q1 · MT6701 선정, 회로 초안 (조건: 모터 전류 실측 후 확정)')],
    '출처: 5주차 실측 · 역분석 · 회로 초안')

# ----------------------------------------------------------------- 5
SIM_STILL = '70_hall.jpg'   # the recorded run's hall at the start (prepare_clips.py mission)
SIM_PARAMS = [
    ('차체', '실측 축간 · 바퀴 · 조향각', 'measure', '외형 · 무게는 카탈로그 값'),
    ('센서', '카메라 1대 · LiDAR 1대', 'spec', '과제 규격 · 제품 사양 그대로'),
    ('팔레트', 'EPAL 6 (T11 은 추후)', 'spec', '공식 제품 시트 치수 그대로'),
    ('바닥 장애물', 'LiDAR 높이 (1.05 m) 이상만', 'assume', '운용 가정 · 낮은 소품은 장면에서 뺌'),
    ('마찰 · 토크', '마찰 0.8 / 0.7 · 3 N·m', 'assume', '고무–콘크리트 일반 범위 · 가속에 충분'),
    ('센서 잡음', '바퀴 · 조향 · 거리', 'assume', '센서 실측 전 가정값 (실측 후 교체)'),
]
KIND = {'spec': ('규격·사양', '#2f74c0'), 'measure': ('실측', '#6a4fb3'), 'assume': ('가정', '#c26a1a')}
param_rows = ''.join(
    f'<tr><td>{a}</td><td>{v}</td><td><span class="kind" style="background:{KIND[k][1]}">{KIND[k][0]}</span> {why}</td></tr>'
    for a, v, k, why in SIM_PARAMS)
add('시뮬레이션 환경', '04  시뮬레이션 환경', 50, f"""
<h2 class="headline">Isaac Sim 공장 홀에 실측 차체 · 과제 규격 센서를 넣어 개발</h2>
<div class="split grow" style="grid-template-columns:0.62fr 1.38fr;gap:26px">
<figure class="shot"><img class="media" src="assets/{SIM_STILL}" alt="Isaac Sim 공장 홀을 위에서 본 장면. 지게차와 팔레트, 적재물이 보인다"></figure>
<div class="stack" style="justify-content:center"><table class="comparison params6 m7-params"><tr><th>항목</th><th>값</th><th>근거</th></tr>{param_rows}</table></div>
</div>
<div class="takeaway">실측으로 먼저 바꿀 가정값: 바퀴 마찰 · 구동 토크 · 센서 잡음</div>
""",
    """실차 주행 전까지는 Isaac Sim에서 개발합니다. 공장 홀 장면에 실측한 차체 값과 과제 규격의 센서를 넣었고, 팔레트는 EPAL 6를 씁니다. 두 번째 팔레트인 T11은 치수가 정해지면 같은 방식으로 확인합니다. 주황색은 가정값입니다. LiDAR 높이보다 낮은 바닥 장애물은 없다고 가정했고, 바퀴 마찰과 구동 토크, 센서 잡음은 실측 전이라 일반적인 범위의 값을 넣었습니다. 이 값들은 실측이 나오면 먼저 바꿉니다. (전환)""",
    [(MEASURED, '실측 반영 모델 dls08_measured (실측하지 않은 항목은 추정값, 필드별 출처)'),
     ('config/isaac_transport.yaml', '마찰 0.8 / 0.7 (지게차 · 팔레트 충돌 형상), 바퀴 토크 3 N·m — 시뮬레이터 전용 가정값'),
     ('config/pallet_geometry_epal6.yaml', 'EPAL 6 공식 제품 시트'),
     ('forklift CLAUDE.md', 'EPAL 6 과 T11 × 0.6 모두 필수, T11 정본 치수 미확정'),
     ('forklift bc4cc64', '--min-obstacle-height-m 1.15 — 1.05 m 평면에 닿지 않는 소품 제거 (운용 가정)')],
    '출처: 저장소 설정 · 모델 기록 (6주차 1쪽 이어 받음)')

# ----------------------------------------------------------------- 6
add('삽입 중 포켓 추적', '05  팔레트 인식과 삽입 중 추적', 75, f"""
<h2 class="headline">캐리지 하단 카메라로 포켓을 끝까지 보며 앞면 1.0 m · 0.6 m에서 경로 다시 그림</h2>
<div class="split grow" style="grid-template-columns:1.2fr 0.8fr;gap:26px">
<figure class="shot">{video('61_insert_depth.mp4', '캐리지 하단 카메라의 깊이 영상. 팔레트에 다가가며 두 번 멈춰 다시 보고, 포크가 들어가는 동안 팔레트 윗판이 화면에 남는다')}</figure>
<div class="phase-flow vert m7-steps"><b>① 팔레트 2 m 앞에서 위치 다시 측정</b><span class="arrow">↓</span><b>② 근접 추적 시작 (포켓을 계속 확인)</b><span class="arrow">↓</span><b>③ 앞면 1.0 m · 0.6 m: 멈춰서 다시 보고 경로 다시 그림</b><span class="arrow">↓</span><b>④ 포크 끝 도달 후 포켓 벽 간격 감시</b><span class="arrow">↓</span><b>⑤ 삽입 끝: 포크 약 32 cm 진입</b></div>
</div>
<div class="takeaway">결과: 포크 · 팔레트 접촉 없이 삽입 · 하역 오차 7 mm (시연 1회 · 깊이 잡음 없는 합성 영상)</div>
""",
    """과제가 강조한 삽입 중 포켓 추적입니다. 처음에는 카메라를 차체 앞 높은 곳에 달았는데, 포크를 넣기 시작하면 팔레트가 화면 밖으로 빠져 마지막 약 25센티미터를 보지 못했습니다. 그래서 Crown 특허처럼 카메라를 캐리지 하단으로 옮겼고, 영상처럼 포크를 넣는 동안에도 포켓과 윗판이 화면에 남습니다. 이 화면으로 팔레트 앞면 1미터와 0.6미터 지점에서 잠깐 멈춰 팔레트 위치를 다시 보고, 남은 삽입 경로를 다시 그립니다. 포크 끝이 앞면에 닿기 직전부터는 포크와 포켓 벽 사이 간격을 계속 감시하고, 간격이 모자라면 멈춥니다. 이 실행에서 포크는 팔레트에 닿지 않고 약 32센티미터 들어갔고, 팔레트를 목적지에 7밀리미터 오차로 내려놓았습니다. 다만 아직 한 번 돌린 결과이고, 깊이 잡음이 없는 합성 영상이라 실제 카메라 잡음을 넣은 확인이 남아 있습니다. (전환)""",
    [(S4B, 'forklift b66271f, 실측 차체 · SLAM 위치 · LiDAR 1대 · 근접 추적(보정점 1.0 / 0.6 m), 포켓 깊이 확인(D5) 끔. result.json: success, 삽입 끝 진입 323.5 / 322.2 mm, 금지 접촉 0, 하역 6.74 mm'),
     (f'{S4B}/run/near_tracking.json', '근접 추적 시작 44.3 s, 1.0 m 보정 54.03 s(정지 0.37 s), 0.6 m 보정 61.73 s, 포크 끝 보호 시작 70.62 s(앞면 0.149 m), 삽입 끝 80.69 s'),
     (NEARPLAN, '기존 장착(높이 0.50 m · 수평)은 삽입 마지막 약 0.25 m 무관측'),
     (CROWN, 'Crown 특허 US9990535B2 — 포크 캐리지 하단 장착 (4주차 장착 사례 ②)'),
     ('memory: D8 범위 (2026-10-10 사용자 결정)', '추적 프레임에는 깊이 잡음을 넣지 않음 — 잡음 없는 합성 깊이에서의 추적 흐름 실증')],
    '화면 생성: 위 실행의 근접 깊이 프레임 506장(10 Hz)을 색 지도로, 사건 시각에 글자, 2배속 (prepare_clips.py depth)')

# ----------------------------------------------------------------- 7
SLAM_COMPARE = [  # item, 2D LiDAR SLAM, camera (visual) SLAM -- datasheets, BKM, RTAB-Map paper (SOURCES.md)
    ('측정 거리', '0.2–12 m', '0.2–약 3 m (조명에 따라)'),
    ('시야', '360°', '앞쪽 87° × 58°'),
    ('약한 환경', '긴 복도 · 넓은 빈 공간', '흰 벽 · 어두운 곳 · 반복 무늬'),
    ('지도', '2D 격자 → 경로 계획에 그대로', '특징점 → 격자는 따로 생성'),
    ('연산', 'CPU만 (소형 보드도 가능)', 'GPU 권장 · 팔레트 인식과 나눠 씀'),
]
slam_rows = ''.join(f'<tr><td>{a}</td><td class="blue"><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in SLAM_COMPARE)
add('위치 추정', '06  위치 추정: LiDAR SLAM', 75, f"""
<h2 class="headline">끝 시점 위치 오차: 바퀴 회전만 계산하면 3.4 m → LiDAR SLAM은 약 4 cm</h2>
<div class="split grow" style="grid-template-columns:0.72fr 1.28fr;gap:26px">
<figure class="shot">{video('45_slam_error.mp4', 'SLAM 운반 실행에서 slam_toolbox가 만든 지도와 추정 경로. 아래 숫자는 SLAM 위치 오차와 바퀴 회전만으로 계산한 위치의 오차')}<figcaption class="small muted">빨강: SLAM · 주황: 바퀴 회전만 · 파랑: 실제</figcaption></figure>
<div class="stack" style="gap:8px;justify-content:center"><p class="panel-h">2D LiDAR SLAM과 카메라 SLAM</p>
<table class="comparison t6 m7-slam"><tr><th>항목</th><th>2D LiDAR (선택)</th><th>카메라 (비전)</th></tr>{slam_rows}</table></div>
</div>
<div class="takeaway">선택: 위치 추정은 LiDAR (넓은 거리 · 360° · 경로 계획용 지도) · 카메라는 팔레트 인식에 집중</div>
""",
    """위치 추정입니다. 왼쪽 영상에서 빨간 SLAM 경로는 파란 실제 경로를 따라가지만, 주황색으로 그린 바퀴 회전만으로 계산한 경로는 갈수록 벗어납니다. 임무가 끝날 때 바퀴 회전만으로 계산한 위치는 3.4미터 어긋났고 SLAM은 약 4센티미터였습니다. 3.4미터의 대부분은 팔레트를 싣고 돌 때 계산보다 덜 돌아서 방향이 24도 틀어진 탓이라, 실물에서도 SLAM이 필요하다고 판단했습니다. 지난 발표에서 카메라 기반 SLAM과 비교해 보라는 의견을 받아 오른쪽 표로 정리했습니다. 가까운 거리에서는 카메라 깊이가 오히려 정밀하지만, 측정 거리가 3미터 안팎이고 그보다 멀면 오차가 거리의 제곱으로 커집니다. LiDAR는 12미터까지 360도를 재고, 만든 2D 지도를 경로 계획에 그대로 쓸 수 있습니다. 두 센서 모두 약한 환경이 있어서, LiDAR는 긴 복도나 넓은 빈 공간, 카메라는 흰 벽이나 어두운 곳에서 위치를 놓치기 쉽습니다. 그래서 공장처럼 넓은 곳의 위치 추정은 LiDAR로 하고, 카메라는 팔레트 인식에 집중하도록 나눴습니다. (전환)""",
    [(SLAM, 'S3 장면 1 — 358 s 에서 SLAM 4.0 cm 대 바퀴 회전만 340 cm, 위치 RMSE 0.088 m'),
     ('ws1 artifacts/20261004_slam_s3/seed_1/run/slam_log.npz', '2026-10-06 재계산: 거리 92.9 대 93.6 m, 끝 방향 오차 −24.3°, 회전 시 실제/계산 비 빈 차 0.998 · 운반 0.925'),
     ('week-06/SOURCES.md', '영상은 이전 S3 실행(사진 추정 차체, 장애물은 시뮬레이터 정답) — 6주차 5쪽과 같음'),
     ('https://cdn.robotshop.com/media/r/rpk/rb-rpk-22/pdf/rplidar-a2m12-360-laser-range-scanner-datasheet.pdf', 'RPLIDAR A2M12 데이터시트 rev.1.0 — 0.2–12 m(흰 물체), 360°, 10 Hz · 0.225° (정확도 1/2/2.5 % 는 A2 시리즈 웹 사양표 값)'),
     ('https://www.realsenseai.com/wp-content/uploads/2026/03/RealSense-D400-Series-Datasheet-Mar-2026.pdf', 'D400 데이터시트 Rev 023 — 깊이 FOV 87° × 58°, 0.2 m – "3 m 이상, 조명에 따라", RMS ≤ 2 % (≤ 2 m), 반복 패턴은 거짓 깊이 가능'),
     ('https://dev.realsenseai.com/docs/tuning-depth-cameras-for-best-performance', 'Intel BKM Rev 1.9 — 깊이 오차는 거리의 제곱으로 증가 (848 × 480, 서브픽셀 0.08 가정 시 2 m 약 14 mm · 4 m 약 57 mm, 계산값)'),
     ('https://arxiv.org/abs/2403.06341', 'Labbé & Michaud, J. Field Robotics 2019 — 카메라: 흰 벽 · 질감 없음 · 어두운 곳에서 위치 상실, 단거리 LiDAR: 넓은 빈 공간 · 긴 복도에서 문제'),
     ('https://joss.theoj.org/papers/10.21105/joss.02783', 'SLAM Toolbox (JOSS 2021) — CPU 전용, 2D 점유 격자를 Nav2 에 그대로 사용'),
     ('https://arxiv.org/abs/2506.04359', 'cuVSLAM 기술보고서 부록 B — Orin Nano Super 에서 RGB-D 모드는 424 × 240 에서만 안정 (GPU 가속 비전 SLAM)'),
     (FB6, '§4 LiDAR SLAM 과 비전 SLAM 비교 장표 (LiDAR 를 쓰는 근거) · 팀 메모: SLAM 은 깊게 들어가지 않음')],
    '화면: 6주차 5쪽 영상 그대로 · 비교표는 데이터시트 · 논문 조사 (2026-10-11)')

# ----------------------------------------------------------------- 8
add('새 장애물 대응', '07  새 장애물 감지와 재계획', 55, f"""
<h2 class="headline">운반 중 나타난 상자 감지 → 정지 → 후진 후 새 경로로 재개</h2>
<div class="split grow" style="grid-template-columns:1.75fr 1fr;gap:28px">
<figure class="shot">{video('46_new_obstacle_single.mp4', '팔레트를 들고 운반하던 중 경로 위에 상자가 나타나자 멈추고, 새 경로로 바꿔 돌아가는 장면. 왼쪽은 위에서 본 주행, 오른쪽은 SLAM 지도와 LiDAR 장애물 칸')}<figcaption class="small muted">노랑: 현재 경로 · 회색: 직전 경로 (재계획 직후) · 주황: LiDAR 장애물 칸</figcaption></figure>
<div class="phase-flow vert"><b>① LiDAR가 경로 위 상자 감지</b><span class="arrow">↓</span><b>② 정지</b><span class="arrow">↓</span><b>③ 멈춘 자리에서 새 경로 계획</b><span class="arrow">↓</span><b>④ 후진 후 새 경로로 운반 재개</b></div>
</div>
<div class="takeaway">결과: 운반 중 · 복귀 중 나타난 상자 (높이 1.3 m) 모두 피해서 완주</div>
""",
    """임무 중에 새 장애물이 나타나는 경우입니다. 팔레트를 들고 가는 경로 위에 키 1.3미터 상자가 새로 나타나면, LiDAR가 상자를 보고 지게차가 멈춘 뒤 그 자리에서 새 경로를 짭니다. 영상처럼 조금 후진했다가 상자를 피해 다시 출발합니다. 복귀하는 길에 상자가 나타난 경우도 같은 방식으로 피해서 임무를 마쳤습니다. 그런데 왜 바로 돌아가지 않고 후진할까요? (전환)""",
    [(S5N1, 'result.json — success, 하역 64.9 mm, 상자 출현 77.2 s · 정지 약 78 s · 재계획 94.3 s 후 후진 (운반 중)'),
     (S1N2, 'result.json — success, 하역 8.0 mm, 상자 출현 226.0 s · 재계획 227.7 s (복귀 중)'),
     ('forklift bc4cc64', '실측 차체(dls08_measured), LiDAR 1대(1.05 m) 장애물 지도 + SLAM 지도로 경로 계획, 새 상자 0.4 × 0.4 × 1.3 m, 포켓 깊이 확인 끔')],
    '화면: 6주차 7쪽 영상 그대로 (week-06/prepare_clips.py single)')

# ----------------------------------------------------------------- 9
add('후진을 고르는 이유', '08  경로 계획: 후진을 고르는 이유', 80, f"""
<h2 class="headline">회전 반경이 커서 전진만으로 비킬 거리가 없을 때 후진 · 앞뒤 전환으로 방향 맞춤</h2>
<div class="split grow m7-paths">
<div class="stack m7-fig"><p class="panel-h">새 상자 앞: 1.25 m 후진 → 상자 안쪽으로 전진</p><div class="m7-svg">{figure_svg('52_reverse_obstacle.svg')}</div>
<p class="m7-cap">상자 위치: 앞 2.0 m · 오른쪽 0.6 m (뒤차축 기준)</p></div>
<div class="stack m7-fig"><p class="panel-h">목적지 앞 방향 맞춤: 21.7 m 한 바퀴 → 전진 · 후진 1.0 m</p><div class="m7-svg">{figure_svg('53_goal_fix.svg')}</div>
<p class="m7-cap">방향 1.3° 차이 · 목적지 1 cm 앞</p></div>
</div>
<div class="takeaway">경로 비용: 후진 거리 1.3배 · 방향 전환마다 1 m 추가 → 전진만으로 못 가거나 훨씬 멀 때만 후진</div>
""",
    """경로 계획에는 Hybrid A*를 씁니다. 차가 실제로 돌 수 있는 반경을 지키면서 전진과 후진 동작을 이어 붙여 길을 찾는 방법입니다. 후진에는 거리를 1.3배로 치고 방향을 바꿀 때마다 1미터만큼 비용을 더하기 때문에, 전진만으로 갈 수 있으면 전진을 고릅니다. 왼쪽은 앞의 상자 장면입니다. 멈춘 자리에서 상자는 앞으로 2미터, 오른쪽으로 0.6미터에 있었고, 원래 경로는 상자 위를 지나고 있었습니다. 회전 반경이 커서 이 거리 안에서는 옆으로 충분히 비킬 수 없으므로, 1.25미터 후진해 거리를 번 뒤 상자 안쪽으로 꺾어 나갑니다. 오른쪽은 앞뒤로 움직일 때의 특성입니다. 목적지 바로 앞에서 방향이 1.3도만 틀어져도, 전진만 쓰면 지름 약 7미터 원을 한 바퀴, 21.7미터를 돌아야 맞출 수 있습니다. 그래서 목적지에 붙는 마지막 연결에 앞뒤 전환을 허용해, 0.5미터 전진하고 0.5미터 후진하는 경로로 바꿨습니다. 목적지 앞 계획을 모아 시험해 보니 이런 한 바퀴 경로가 모두 사라졌습니다. (전환)""",
    [('src/forklift_core/planning/hybrid_astar.py', 'PlannerConfig: reverse_penalty 1.3, gear_change_penalty_m 1.0; D7_PLANNER_OPTIONS = Reeds–Shepp 목표 연결 + 연결 상한 4 m'),
     ('config/isaac_transport_measured.yaml', 'planner_curvature_inv_m 0.29 (계획 회전 반경 3.45 m, 차체 한계 15° = 2.46 m 에 추종 여유)'),
     (f'{S5N1}/plan_history.json', '재계획 94.3 s: 뒤차축 기준 상자 앞 1.97 m · 오른쪽 0.61 m, 후진 1.25 m → 전진 22.95 m, 원래 경로의 상자 중심 최소 거리 0.01 m (prepare_figures.py)'),
     ('tests/unit/planning/test_d7_planner_options.py', 'l8_measured 장면 1 + N1 정지 재계획: 목표 1 cm 앞 · 0.023 rad — 전진만 21.68 m, D7 0.99 m (전진 0.50 + 후진 0.49 m, 전환 1회) — prepare_figures.py 가 같은 사례를 다시 계획'),
     ('forklift 1e3cdeb', 'D7 CPU 판정: 운반 목표 고리 1,686 → 0 (목표당 2,376 계획), 목표까지 길이 중앙값 21.69 → 1.03 m'),
     (FB6, '§3 Hybrid A* 가 왜 뒤로 가는지 · 앞뒤로 돌 때의 특성')],
    '화면 생성: 실행 기록 · 플래너 재실행으로 그린 경로 (prepare_figures.py)')

# ----------------------------------------------------------------- 10
MISSION_VIDEO = '71_mission.mp4'
MISSION_ROWS = [  # input, source
    ('팔레트 위치', '카메라 깊이 인식'),
    ('로봇 위치', 'SLAM 추정'),
    ('장애물', 'LiDAR 1대 + SLAM 지도'),
    ('경로', '앞뒤 전환 연결 · 도킹 재시도'),
    ('목적지', '미리 등록한 위치 (LiDAR 스캔 정합)'),
]
mission_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in MISSION_ROWS)
add('운반 임무 전체', '09  운반 임무 전체', 60, f"""
<h2 class="headline">실측 차체로 인식 → 삽입 → 들기 → 운반 → 하역 → 복귀를 사람 개입 없이 완주</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr;gap:32px">
<figure class="shot">{video(MISSION_VIDEO, '공장 홀을 위에서 본 지게차. 팔레트를 인식해 들고, 목적지에 내린 뒤 출발점으로 돌아온다')}</figure>
<div class="stack" style="justify-content:center"><table class="comparison t6"><tr><th>입력</th><th>얻는 방법</th></tr>{mission_rows}</table></div>
</div>
<div class="takeaway">결과: 하역 오차 19 mm · 출발점 복귀 오차 3 cm · 포크 · 팔레트 충돌 없음</div>
""",
    """지금까지 말씀드린 것을 한 임무로 보여 드리겠습니다. 실측 차체 모델로 팔레트를 인식하고, 포크를 넣어 들어 올린 뒤, 목적지에 내려놓고 출발점으로 돌아옵니다. 오른쪽 표처럼 팔레트 위치는 카메라로, 로봇 위치는 SLAM으로, 장애물은 LiDAR 한 대로 구했고, 목적지는 미리 등록해 둔 위치를 LiDAR 스캔과 맞춰 찾습니다. 이 실행에서 팔레트는 목적지에 19밀리미터 오차로 내려놓았고, 출발점에는 3센티미터 오차로 돌아왔으며, 포크와 팔레트의 충돌은 없었습니다. 처음부터 끝까지 사람이 개입하지 않고 자율로 동작했습니다. (전환)""",
    [('ws1 artifacts/20261011_meeting_video/seed_5_d7', 'forklift b66271f 스냅숏, 실측 차체 · SLAM 위치 · LiDAR 1대 · --d7-planner --d7-docking · --video --robot-camera (근접 추적 끔). result.json: success, complete, 하역 19.4 mm, 복귀 2.7 cm · 0.040 rad, 금지 접촉 0, 진입 319.9 / 318.1 mm, 시뮬 219.6 s'),
     ('ws1 artifacts/20261011_meeting_video/seed_1_d7', '같은 조건 장면 1: success, 하역 27.0 mm, 복귀 5.1 cm, 금지 접촉 0, 시뮬 273.8 s'),
     ('config/isaac_transport_measured.yaml', '목적지 도킹: 미리 등록한 위치의 LiDAR 스캔 정합 (등록 위치는 시뮬레이터 값)')],
    '화면 생성: 위 장면 5 3분할 영상의 조감 칸 12배속 (prepare_clips.py mission)')

# ----------------------------------------------------------------- 11
EXAM = [  # item, exam (disqualification unless noted), ours (simulation), verdict
    ('작업 흐름', '팔레트 상차 → 코스 주행 → 하차 → 복귀', '인식 → 삽입 → 들기 → 운반 → 내리기 → 복귀', 'like'),
    ('하역 위치', '가로 · 세로 20 cm 넘게 어긋나면 실격', '하역 오차 7–65 mm (완주한 실행)', 'ok'),
    ('포크 삽입', '덜 넣은 정도 20 cm 넘으면 실격', '쓸 수 있는 길이 34.6 cm 중 약 32 cm', 'ok'),
    ('접촉 · 낙하', '포크로 드럼 · 팔레트를 건드리거나 떨어뜨리면 실격', '포크 · 팔레트 접촉 없음 · 낙하 없음', 'ok'),
    ('운반 중 포크 높이', '지면에서 20–30 cm (50 cm 넘으면 실격)', '20 cm 들고 운반', 'ok'),
    ('후진', '하차 후 후진 · 코스 후진 주행', '필요할 때 후진 (재계획 · 방향 맞춤)', 'like'),
    ('틸트', '리프트 · 틸트 레버로 마스트 각도 조절', '틸트 기구 없음', 'diff'),
]
VERDICT = {'ok': ('기준 안', 'ok'), 'like': ('비슷', 'like'), 'diff': ('다름', 'diff')}
exam_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td><span class="m7-v {VERDICT[v][1]}">{VERDICT[v][0]}</span></td></tr>'
                    for a, b, c, v in EXAM)
add('자격시험 기준 비교', '10  지게차운전기능사 실기 기준과 비교', 75, f"""
<h2 class="headline">지게차운전기능사 실기 실격 기준 대비: 하역 · 삽입 · 접촉은 기준 안 · 틸트 기구는 없음</h2>
<table class="comparison m7-exam grow"><tr><th>항목</th><th>실기시험 (2025 공개문제)</th><th>우리 지게차 (시뮬레이션)</th><th>비교</th></tr>{exam_rows}</table>
<div class="takeaway">제안: 시험 코스는 모든 치수가 차폭 (바깥 타이어 간 거리)의 배수 → 우리 차 기준으로 줄인 코스를 시뮬레이션 평가에 사용</div>
""",
    """지난 발표에서 실제 지게차 운전 기준과 비교해 보라는 의견을 받아, 국가기술자격 지게차운전기능사 실기시험의 실격 기준과 대조했습니다. 시험은 드럼 위 팔레트를 싣고 코스를 돈 뒤 다른 팔레트 위에 내려놓는 과제입니다. 내려놓은 위치가 20센티미터 넘게 어긋나면 실격인데, 우리 하역 오차는 7에서 65밀리미터였습니다. 포크를 덜 넣은 정도가 20센티미터를 넘어도 실격인데, 우리는 포크에서 쓸 수 있는 길이 34.6센티미터 중 약 32센티미터를 넣습니다. 포크로 팔레트나 드럼을 건드리거나 짐을 떨어뜨려도 실격인데, 시뮬레이션에서 접촉과 낙하는 없었습니다. 다른 점은 틸트입니다. 시험은 마스트를 기울이는 조작을 요구하지만 우리 차체에는 틸트 기구가 없어서, 틸트 없이 짐을 안정시키는 방법을 따로 정해야 합니다. 시험 코스 도면은 모든 치수가 차폭의 배수라, 우리 차 크기로 줄인 시험 코스를 시뮬레이션에 만들어 평가 기준으로 쓰는 것도 제안드립니다. (전환)""",
    [(QNET, '「[공개문제] 지게차운전기능사」 코스운전 및 작업 (한국산업인력공단, 2025-12-22 등록) — 요구사항 가–다, 실격 (8)(9)(10)(14)(15)(16)(17)(18), 도면 치수는 D(좌우 최외측 타이어 바깥 간 거리)의 배수. 도면은 저작물이라 화면에 싣지 않음'),
     ('같은 문서', '시험 시간 4분 — 코스 · 차체 규모가 달라 비교에서 제외 (속도 · 작업 시간은 자율 동작 완성 뒤 단계)'),
     (S4B, '하역 6.74 mm, 진입 323.5 / 322.2 mm (캐리지 한계 0.346 m), 금지 접촉 0'),
     ('week-06/SOURCES.md', '실측 차체 · LiDAR 1대 완주 실행 하역 8.0 · 23.8 · 64.9 mm (6주차), 새 녹화 장면 5 · 1: 19.4 · 27.0 mm'),
     ('config/isaac_transport_measured.yaml', 'lift_target_m 0.2 (운반 중 포크 높이)'),
     ('week-05/SCRIPT.md', '10쪽 표준 운용 절차 대조 — 틸트 기구 없음'),
     (FB6, '§2 실제 지게차 자격증 시험 기준과 우리 지게차 비교 표 (3주차 피드백: 국가공인 시험의 표준 운용 방법)')],
    '출처: Q-Net 공개문제 원문 (2025) · 실행 기록')

# ----------------------------------------------------------------- 12
CONCLUSION = [  # what we found, so, direction
    ('실측 조향각 15°', '회전 반경 약 2.5 m (예상의 2배)', '앞뒤로 움직여 방향 맞추는 경로'),
    ('높은 카메라 장착', '삽입 마지막 약 0.25 m 화면 밖', '캐리지 하단 장착 · 직전 보정 · 삽입 중 감시'),
    ('바퀴 회전만 계산', '짐 싣고 돌 때 방향이 틀어져 3.4 m 어긋남', 'LiDAR SLAM으로 위치 추정'),
    ('기존 제어기', '켜기 · 끄기만 가능', '자체 구동 보드 (속도 · 조향 제어)'),
    ('LiDAR 1대 (1.05 m)', '그보다 낮은 바닥 장애물은 못 봄', '운용 가정으로 명시 · 현장 조건 확인'),
]
concl_rows = ''.join(f'<tr><td>{a}</td><td class="cur">{b}</td><td class="arrow">→</td><td class="nxt">{c}</td></tr>'
                     for a, b, c in CONCLUSION)
add('결론', '11  결론', 65, f"""
<h2 class="headline">결론: 실측 차체 · 규격 센서의 제약에 맞춰 경로 · 카메라 · 위치 추정 · 구동부를 바꿈</h2>
<table class="comparison plan6 m7-concl grow"><tr><th class="c1">확인한 것</th><th class="c2">그래서</th><th class="c3"></th><th class="c4">바꾼 방향</th></tr>{concl_rows}</table>
<div class="takeaway">다음 목표: 시뮬레이션에서 이어 놓은 임무를 실차로 (구동 보드 → 실차 주행 → 실물 센서)</div>
""",
    """정리하면, 실제 차체와 센서 조건을 확인하면서 처음 계획에서 다섯 가지를 바꿨습니다. 조향각이 15도로 작아 회전 반경이 두 배가 되었기 때문에 앞뒤로 움직여 방향을 맞추는 경로를 넣었습니다. 높이 단 카메라는 삽입 마지막을 보지 못해 캐리지 하단으로 옮기고, 넣기 직전 보정과 넣는 동안의 간격 감시를 넣었습니다. 바퀴 회전만으로 계산한 위치는 짐을 싣고 돌 때 크게 틀어져서 LiDAR SLAM으로 위치를 구합니다. 기존 제어기는 켜고 끄기만 되어서 구동 보드를 새로 만듭니다. 마지막으로 규격대로 LiDAR가 한 대라 그 높이보다 낮은 장애물은 볼 수 없어서, 이것은 운용 가정으로 두고 현장 조건을 여쭤보려고 합니다. 다음 목표는 시뮬레이션에서 이어 놓은 임무를 실차로 옮기는 것입니다. (전환)""",
    [(MEASURED, '실측 조향 15°, 회전 반경 2.46 m (사진 추정 1.32 m)'),
     (NEARPLAN, '기존 장착 마지막 약 0.25 m 무관측'),
     (SLAM, '358 s 에서 SLAM 4.0 cm 대 바퀴 회전만 340 cm (방향 −24.3°)'),
     ('week-05/SCRIPT.md', '기존 제어기 릴레이 on/off, 속도 조절 기능 없음'),
     ('forklift CLAUDE.md', '과제 센서 구성(RGB-D 1 · 2D LiDAR 1) 유지, 낮은 장애물은 운용 가정'),
     (FB6, '§2 결론 장표 — 무엇이 어떻게 달라지니까 무엇으로 가야 하는지')],
    '출처: 3–9쪽 결과 정리')

# ----------------------------------------------------------------- 13
SCHEDULE = [  # period, software, hardware
    ('10/16–22', '여러 장면 반복 · C · D 상황 확인', '모터 전류 실측 · 구동 보드 PCB 설계'),
    ('10/23–29', '중간고사', ''),
    ('10/30–11/12', '실물 센서 연결 (Jetson · 카메라 · LiDAR)', '구동 보드 제작 · 속도 · 조향 제어'),
    ('11/13–11/26', '실차 위치 추정 · 실물 팔레트 인식', '센서 브래킷 장착 · 좌표 보정'),
    ('11/27–12/10', '실차 A 전체 임무 → B · C · D', '반복 시험 · 가정값을 실측값으로'),
    ('12/11–12/17', '최종 시연 준비', ''),
]
sched_rows = ''.join(
    (f'<tr class="exam"><td>{p}</td><td colspan="2">{s}</td></tr>' if not h and s == '중간고사' else
     f'<tr><td>{p}</td><td colspan="2">{s}</td></tr>' if not h else
     f'<tr><td>{p}</td><td>{s}</td><td>{h}</td></tr>') for p, s, h in SCHEDULE)
add('남은 과제와 일정', '12  남은 과제와 일정', 60, f"""
<h2 class="headline">남은 일정: 중간고사 전 구동 보드 설계 → 11월 실차 주행 → 12월 중순 최종 시연</h2>
<table class="comparison m7-sched grow"><tr><th>기간</th><th>소프트웨어</th><th>하드웨어</th></tr>{sched_rows}</table>
<div class="takeaway">일정 조건: 구동 보드 제작 시점에 따라 실차 단계 조정 · 최종 시연일은 15주차로 가정</div>
""",
    """남은 일정입니다. 다음 주에는 모터 전류를 재서 구동 보드 PCB를 설계하고, 시뮬레이션에서는 여러 장면과 C, D 상황을 반복해서 확인합니다. 중간고사가 끝나면 구동 보드를 만들어 속도와 조향 제어를 붙이고, Jetson에 카메라와 LiDAR를 연결합니다. 11월 중순부터는 실차로 위치 추정과 팔레트 인식을 확인하고, 12월 초까지 실차로 A 상황 전체 임무를 한 뒤 B, C, D로 넓힙니다. 마지막 주는 최종 시연을 준비합니다. 실물 진행에 따라 일정은 조정될 수 있습니다. (전환)""",
    [('docs/plans/2026-09-11-development-roadmap.md', '§4 달력 대응: 8주차 10/23–29 중간고사, 9–10주차 10/30–11/12, 11–12주차 11/13–11/26, 13–14주차 11/27–12/10, 15주차 12/11–17 예비 · 최종 시연일 미정(15주차 가정)'),
     ('week-06/build_deck.py', '8쪽 다음 작업: 모터 전류 실측 → 전류 제한 · 방열 → PCB, 가정값 실측 교체, 센서 브래킷')],
    '출처: 개발 로드맵 달력 · 6주차 다음 작업 (실물 일정은 팀 계획)')

# ----------------------------------------------------------------- 14
QUESTIONS = [
    ('실제 운용 환경', ['작업장 규모 · 통로 폭 · 바닥 (실내 · 경사)', '다루는 팔레트 종류 · 하중 · 적재 높이', '주변 사람 · 장애물 · 한 번의 작업 흐름']),
    ('받고 싶은 자료', ['작업장 도면 · 지도 · 실제 운용 영상', '사용 팔레트 도면 (T11 진입구 폭 235 / 350 mm)', '마커 · 반사판 설치 가능 여부']),
    ('정해 주셨으면 하는 것', ['팔레트 위치 · 목적지를 알려 주는지, 직접 찾는지', '포크 삽입 깊이 (끝까지 / 팔레트 깊이 60 %)', '무선 감시 · 원격 정지 수준 · 여러 대 동시 운용 여부',
                         'LiDAR보다 낮은 바닥 장애물 여부 · 평가 기준 · 시연 환경']),
]
q_rows = ''.join(
    ''.join(f'<tr>{f"<td class=grp rowspan={len(items)}>{group}</td>" if i == 0 else ""}<td class="item">{item}</td></tr>'
            for i, item in enumerate(items)) for group, items in QUESTIONS)
add('확인 요청', '13  리보틱스 확인 요청', 60, f"""
<h2 class="headline">확인 요청: 실제 운용 환경 · 받고 싶은 자료 · 정해 주셨으면 하는 것</h2>
<table class="comparison m7-q grow"><tr><th>구분</th><th>질문</th></tr>{q_rows}</table>
""",
    """마지막으로 리보틱스 측에 여쭤보고 싶은 것입니다. 먼저 실제 운용 환경입니다. 작업장 크기와 통로 폭, 바닥 상태, 다루는 팔레트와 하중, 주변의 사람과 장애물을 알고 싶습니다. 다음으로 받고 싶은 자료입니다. 작업장 도면이나 지도, 실제 운용 영상, 사용하는 팔레트 도면을 받을 수 있는지 여쭤봅니다. 특히 T11 팔레트는 포크 진입구 폭을 235밀리미터로 볼지 350밀리미터로 볼지 아직 정하지 못했습니다. 마지막으로 정해 주셨으면 하는 것입니다. 팔레트 위치와 목적지를 알려 주시는지 아니면 로봇이 찾아야 하는지, 포크를 끝까지 넣어야 하는지, 무선 감시와 원격 정지는 어느 수준이 필요하고 여러 대를 함께 운용하는지, LiDAR보다 낮은 바닥 장애물이 있는지, 그리고 평가 기준과 시연 환경입니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [(FB4, '§1 미팅 질문 세 구분 — 우리가 궁금한 것 · 기업이 제공할 수 있는 것 · 기업이 결정해 줘야 하는 것'),
     ('week-05/build_deck.py', '11쪽 미팅 질문 (실제 운용 상황 · 초기 제공 정보 · 시뮬레이션 설정 적합성)'),
     ('forklift CLAUDE.md', 'T11 진입구 235 / 350 mm 두 해석, 어느 것도 채택하지 않음 (docs/design/2026-09-17-t11-test-article-drawing.md)'),
     (FB6, '§1 팀 메모: 리보틱스 미팅 때 물어볼 것이 있음')],
    '출처: 4–6주차 피드백 · 5주차 미팅 질문 이어 받음')

TITLE = '리보틱스 중간 미팅 · 자율 지게차 중간 점검'
N_SLIDES = 14


def build():
    assert len(slides) == N_SLIDES, len(slides)
    total = sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {total//60}분 {total%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
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
