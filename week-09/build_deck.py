"""Build the week 9 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 9 answers the week 8 feedback (docs/references/week8_feedback.md in the robot repository): the hardware
half shows the team's main board (top-side 3D render and layout, the whole schematic set; the user approved
the public deck and asked not to name the designer, 2026-10-28), its MCU core board, its power section and
the encoder magnet mount; the software half shows localization on a pre-built map and the console against
commercial fleet managers, then the conclusion and next week. The slide wording was written by agy
(Gemini 4 Argon) from the raw facts (global writing rule); the narration was written directly (project
memory script-md-no-agy). Simulated demos are Isaac renders (user, 2026-10-28).
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
slides = []

BLUE = '#2f74c0'
ORANGE = '#e07b39'

ROBOT = 'lightminn/forklift main f60da30a'
TEAM_PCB = '팀 메인보드 자료 (Forklift Main Control Board V1.0.0, EasyEDA 회로도 5쪽 중 1 · 2 · 3 · 5쪽, 3D 렌더, PCB 배치도; 2026-10-28 사용자 전달)'
FEEDBACK = f'{ROBOT} docs/references/week8_feedback.md'
PINMAP = f'{ROBOT} docs/design/2026-10-22-h743-pinmap-draft-review.md'
SLAM_PLAN = f'{ROBOT} docs/plans/2026-10-26-slam-localization-default.md'
REMEASURE = f'{ROBOT} docs/plans/2026-10-27-slam-a-return-start-remeasure.md (PR #179)'
FMS = f'{ROBOT} docs/design/2026-10-22-fms-case-survey.md (PR #87)'
CONSOLE = f'{ROBOT} console/README.md (PR #90 대기열 · #93 상태·경보 · #95 실적 요약)'
MOCK = '콘솔 캡처 — 가짜 차량 console.mock_vehicle (콘솔 코드 = main f60da30a), 헤드리스 Chromium 1600 × 900, 2026-10-28'
STALL = 'lightminn/forklift diag/transport-start-stall docs/validation/2026-10-27-transport-start-stall.md'
PRESTEER = 'lightminn/forklift feat/escape-presteer docs/plans/2026-10-27-escape-presteer.md (2판, b38048da)'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def img(src, alt, cap=None, cls='shot'):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="{cls}"><img class="media" src="assets/{src}" '
            f'alt="{escape(alt, quote=True)}">{c}</figure>')


def video(src, alt, cap=None, cls='shot'):
    """A looping muted clip in a figure, its poster frame when one exists (week 6's helper)."""
    poster = src.rsplit('.', 1)[0] + '_poster.jpg'
    pa = f' poster="assets/{poster}"' if (ROOT / 'assets' / poster).exists() else ''
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="{cls}"><video class="media" src="assets/{src}"{pa} autoplay loop muted playsinline '
            f'aria-label="{escape(alt, quote=True)}"></video>{c}</figure>')


def table(head, rows, cls='comparison h7', merge_first=False):
    h = ''.join(f'<th>{x}</th>' for x in head)
    if not merge_first:
        body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
        return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'
    body = ''
    for i, r in enumerate(rows):
        if i and rows[i - 1][0] == r[0]:
            first = ''
        else:
            n = 1
            while i + n < len(rows) and rows[i + n][0] == r[0]:
                n += 1
            span = f' rowspan="{n}"' if n > 1 else ''
            first = f'<td class="lead"{span}>{r[0]}</td>'
        body += '<tr>' + first + ''.join(f'<td>{x}</td>' for x in r[1:]) + '</tr>'
    return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'


def lgd(*items):
    """Legend: (kind, colour, text), kind box / line / dash."""
    out = []
    for kind, colour, text in items:
        if kind == 'line':
            sw = f'<span class="sw ln" style="background:{colour}"></span>'
        elif kind == 'split':
            c1, c2 = colour
            sw = f'<span class="sw" style="background:linear-gradient(90deg,{c1} 50%,{c2} 50%)"></span>'
        elif kind == 'dash':
            sw = f'<span class="sw dash" style="border-color:{colour}"></span>'
        else:
            sw = f'<span class="sw" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="lgd7">{"".join(out)}</div>'


def band(text):
    return f'<div class="takeaway">{text}</div>'


# ----------------------------------------------------------------- figures
def power_diagram():
    """The main board's power path from the schematic pages 3 and 5: battery -> fuse -> input protection and
    switch -> 12 V (VCC) -> the four motor drivers / the 5 V buck to the MCU and sensor boards / the 19 V boost
    and its protection to the Jetson. Photos: our chassis (week 5) for the motors, a Jetson kit (Wikimedia
    Commons, week 8 SOURCES) for the Jetson. Box words are agy's figure text."""
    W, H = 1272, 268
    ah = 'marker-end="url(#ah9)"'

    def box(x, y, w, h, t, sub=None, fill='#eef4fb', stroke=BLUE):
        out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>'
               f'<text x="{x + w / 2}" y="{y + h / 2 + (-4 if sub else 7)}" text-anchor="middle" font-size="21" font-weight="700" fill="#1b1f24">{t}</text>')
        if sub:
            out += f'<text x="{x + w / 2}" y="{y + h / 2 + 21}" text-anchor="middle" font-size="16" fill="#44505c">{sub}</text>'
        return out

    def pic(src, x, y, w, h):
        cid = f'c9_{src.split(".")[0]}'
        return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></clipPath>'
                f'<image href="assets/{src}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="#c3cad3" stroke-width="1.5"/>')

    def arrow(x1, y1, x2, y2):
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BLUE}" stroke-width="4" {ah}/>'

    p = [f'<defs><marker id="ah9" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker></defs>']
    cy = 134
    p.append(box(4, cy - 36, 150, 72, '12 V 배터리', 'XT60'))
    p.append(arrow(154, cy, 172, cy))
    p.append(box(176, cy - 36, 180, 72, '50 A 퓨즈', '(배터리 + 배선에 설치)', fill='#fff', stroke='#9aa3ad'))
    p.append(arrow(356, cy, 374, cy))
    p.append(box(378, cy - 36, 180, 72, '입력 보호·스위치', 'LM74801'))
    p.append(arrow(558, cy, 584, cy))
    p.append(box(588, cy - 36, 130, 72, '12 V (VCC)'))
    # three branches
    bx, bw = 760, 200
    p.append(f'<polyline points="718,{cy} 736,{cy} 736,44 {bx - 4},44" fill="none" stroke="{BLUE}" stroke-width="4" {ah}/>')
    p.append(arrow(718, cy, bx - 4, cy))
    p.append(f'<polyline points="718,{cy} 736,{cy} 736,224 {bx - 4},224" fill="none" stroke="{BLUE}" stroke-width="4" {ah}/>')
    p.append(box(bx, 12, bw, 64, '모터 드라이버 4개', 'DRV8244'))
    p.append(box(bx, cy - 32, bw, 64, '5 V 강압', 'LMR60440, 4 A'))
    p.append(box(bx, 192, bw, 64, '19 V 승압·보호', 'LM5122, TPS26630'))
    for y in (44, cy, 224):
        p.append(arrow(bx + bw, y, bx + bw + 28, y))
    px = bx + bw + 32
    p.append(pic('d02_truck.jpg', px, 4, 80, 80) + f'<text x="{px + 88}" y="51" font-size="17" font-weight="700" fill="#1b1f24">구동·조향·승강 모터 4개</text>')
    p.append(box(px, cy - 30, 230, 60, 'MCU·센서 보드', fill='#fff', stroke='#9aa3ad'))
    p.append(pic('d02_jetson.jpg', px, 186, 96, 76) + f'<text x="{px + 106}" y="231" font-size="19" font-weight="700" fill="#1b1f24">Jetson (원형 잭)</text>')
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="12 V 배터리에서 50 A 퓨즈와 입력 보호 스위치를 지나 '
            f'12 V(VCC)가 되고, 모터 드라이버 4개, 5 V 강압을 거쳐 MCU와 센서 보드, 19 V 승압과 보호를 거쳐 Jetson으로 갈라짐">'
            f'<g font-family="var(--uos-font)">{"".join(p)}</g></svg>')


# per-minute medians of the applied position error (|control - truth|, cm), line_m seed 3 of the S3 second
# check (ws1 test_runs/live/s3conf2_3a37e216, slam.control): R = mapping (ended by slam_link_failed at 56 min),
# L = localization on the survey bundle (65 min, the session's end)
ERR_OLD = [1.6, 3.8, 5.6, 7.9, 3.2, 12.6, 12.4, 8.4, 21.5, 4.7, 8.3, 3.8, 11.0, 11.7, 9.9, 17.2, 5.3, 11.8, 4.2,
           9.1, 13.3, 11.8, 7.6, 9.1, 14.2, 3.5, 5.9, 22.1, 22.1, 4.8, 10.3, 5.7, 12.3, 3.5, 4.7, 11.0, 1.8, 10.2,
           3.5, 11.1, 21.8, 19.2, 9.3, 8.1, 8.9, 12.8, 3.1, 9.5, 9.7, 15.6, 12.4, 14.1, 3.7, 10.4, 12.1, 12.4, 12.6]
ERR_NEW = [1.1, 3.8, 2.2, 3.1, 1.9, 4.5, 2.4, 3.3, 3.9, 4.2, 4.2, 3.8, 4.4, 2.6, 3.8, 2.4, 3.9, 1.8, 4.0, 1.4,
           4.0, 2.5, 4.3, 3.3, 3.7, 4.5, 3.1, 4.0, 1.8, 4.0, 2.4, 3.9, 1.5, 2.4, 2.2, 4.1, 3.7, 4.6, 3.9, 3.4, 3.9,
           2.0, 4.5, 1.8, 3.9, 1.6, 3.3, 2.1, 4.1, 3.0, 2.0, 3.9, 1.7, 3.9, 2.2, 5.3, 2.2, 3.9, 2.0, 4.1, 3.9, 4.3,
           3.9, 2.1, 4.4, 0.9]


def error_chart():
    """Position error against running time, the two SLAM modes on one axis (cm, one-minute medians)."""
    W, H = 640, 360
    L, R, T, B = 62, 18, 14, 54
    xmax, ymax = 66, 25
    X = lambda m: L + (W - L - R) * m / xmax
    Y = lambda v: T + (H - T - B) * (1 - v / ymax)
    g = []
    for v in (0, 5, 10, 15, 20, 25):
        g.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="#e6e9ed" stroke-width="1"/>'
                 f'<text x="{L - 8}" y="{Y(v) + 6:.1f}" text-anchor="end" font-size="16" fill="#44505c">{v}</text>')
    for m in (0, 10, 20, 30, 40, 50, 60):
        g.append(f'<text x="{X(m):.1f}" y="{H - B + 24}" text-anchor="middle" font-size="16" fill="#44505c">{m}</text>')
    g.append(f'<line x1="{L}" y1="{H - B}" x2="{W - R}" y2="{H - B}" stroke="#9aa3ad" stroke-width="1.5"/>')
    g.append(f'<text x="{(L + W - R) / 2}" y="{H - 6}" text-anchor="middle" font-size="17" fill="#1b1f24">운행 시간 (분)</text>')
    g.append(f'<text x="16" y="{(T + H - B) / 2}" text-anchor="middle" font-size="17" fill="#1b1f24" '
             f'transform="rotate(-90 16 {(T + H - B) / 2})">위치 오차 (cm)</text>')

    def line(vals, colour):
        pts = ' '.join(f'{X(i + 0.5):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
        return f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
    g.append(line(ERR_OLD, ORANGE))
    g.append(line(ERR_NEW, BLUE))
    xe = X(len(ERR_OLD) - 0.5)
    g.append(f'<line x1="{xe:.1f}" y1="{Y(ymax):.1f}" x2="{xe:.1f}" y2="{H - B}" stroke="{ORANGE}" stroke-width="1.5" stroke-dasharray="5 4"/>'
             f'<text x="{xe - 6:.1f}" y="{Y(23.2):.1f}" text-anchor="end" font-size="17" font-weight="700" fill="#1b1f24">56분 SLAM 끊김</text>')
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="운행 시간에 따른 위치 오차. 기존 방식은 10에서 20 센티미터를 '
            f'오르내리다 56분에 SLAM이 끊기고, 지금 방식은 65분 동안 3에서 4 센티미터">'
            f'<g font-family="var(--uos-font)">{"".join(g)}</g></svg>')


# ----------------------------------------------------------------- cover
add('개발 진행 보고', '9주차\n자율 지게차 개발', 20, '',
    """안녕하십니까. 9주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 주는 8주차 발표에서 받은 피드백에 답하는 구성입니다. 먼저 피드백별로 무엇을 했는지 정리하고, 하드웨어인 메인보드와 MCU, 전원부, 엔코더 자석 마운트를 보인 뒤, 소프트웨어에서는 미리 만든 지도 위에서 위치를 추정하는 방식과 운용 콘솔을 상용 관제 시스템과 비교한 결과를 말씀드리겠습니다. 마지막으로 결론과 다음 주 계획으로 마치겠습니다. (전환)""",
    [(FEEDBACK, '8주차 피드백 1–5절'), (TEAM_PCB, '메인보드 회로도 · PCB')], '진행 보고')

# ----------------------------------------------------------------- 1
FB_ROWS = [
    ('하드웨어·하위 제어 우선', '메인보드 PCB(114×92 mm) 설계, 마운트 구멍(3.25 mm) 확인', '메인보드 제작, 마운트 출력·자석 부착 뒤 엔코더 확인'),
    ('MCU 성능', '메인 MCU로 STM32H743(480 MHz) 채택', '—'),
    ('상용 FMS와 콘솔 비교', '상용 7종 참고해 대기열·상태·실적 화면 추가', '—'),
    ('시연 장소와 배터리 충전', '보드에 전압 분압 회로 반영 (핀 미배정)', '확인 필요'),
]
add('8주차 피드백 대응', '01  8주차 피드백 대응', 45, f"""
<h2 class="headline">메인보드 PCB 배치와 H743 코어 보드 적용, 콘솔 운용 기능 3가지 추가</h2>
{table(['8주차 피드백', '이번 주 진행', '다음 단계'], FB_ROWS, 'comparison h7 fb9 grow')}
""",
    """지난주 피드백에 대한 대응입니다. 가장 큰 지적은 시뮬레이션 같은 상위 제어보다 하드웨어와 하위 제어를 먼저 하라는 것이었습니다. 그래서 이번 주에는 하드웨어 쪽에서 메인보드의 전체 회로도와 PCB 배치를 마쳤고, 엔코더 자석을 모터 축에 붙이는 마운트를 출력해 축에 맞는 구멍 지름을 찾았습니다. 다음 주에 메인보드를 제작하고, 마운트를 실제 자석에 맞춰 다시 출력해 달 계획입니다. 두 번째로 MCU 성능에 대한 의견이 있었는데, 메인 MCU로 STM32H743을 채택해 메인보드에 꽂도록 설계했습니다. 이유는 뒤 MCU 장에서 말씀드리겠습니다. 세 번째로 콘솔을 상용 FMS와 비교해 보라는 의견에는 관제 제품 일곱 개를 조사해 작업 대기열, 장비 상태와 경보, 실적 요약 세 가지를 콘솔에 넣었습니다. 시연 장소와 배터리 충전은 아직 확인하지 못했습니다. 다만 배터리 전압을 MCU로 읽을 수 있게 메인보드에 분압 회로는 넣어 두었습니다. (전환)""",
    [(FEEDBACK, '1절 하드웨어 · 하위 제어 우선, 2절 G474 느림, 3절 FMS 비교(시스콘), 5절 2공학관 지하 · 배터리 충전'),
     (TEAM_PCB, '보드 외곽 114.173 × 91.567 mm, 3쪽 BATTERY MONITOR ADC_BAT = VCC / 11 (MCU ADC 핀 미배정)'),
     (PINMAP, 'WeAct Studio MiniSTM32H7xx 의 STM32H743VIT6'),
     ('ST 제품 정보', 'STM32H743VI Cortex-M7 480 MHz · 플래시 2 MB · RAM 1 MB'),
     ('사용자 (2026-10-28)', 'G474 를 H743 으로 대체한 흐름이 아니라 메인 MCU 로 H743 을 채택; 이유는 고성능, 많은 핀 개수, 가성비 등'),
     (FMS, '상용 FMS 7종 사례 조사, 권고 1–3 최소안')],
    '표: 8주차 피드백별 대응')

# ----------------------------------------------------------------- 2
BOARD_ROWS = [
    ('MCU', 'Nucleo STM32H533RE', '<b>STM32H743 코어 보드<br>(2×22 헤더 장착)</b>'),
    ('전원 구성', '12 V → 5 V → 3.3 V', '<b>배터리 보호와<br>Jetson 19 V 공급 추가</b>'),
    ('모터·엔코더', 'DRV8244 4채널,<br>차동·LVDS 입력', '7주차와 같음<br>(XT30 4개, RJ 2개)'),
    ('진행 상태', '모터·센서<br>부분 회로도', '<b>전체 회로도와 PCB 배치<br>완료 (제작 전)</b>'),
]
add('메인보드 설계', '02  메인보드 설계', 55, f"""
<h2 class="headline">H743 코어 보드와 Jetson 19 V 전원을 합친 114.2×91.6 mm 메인보드 PCB 배치 완료</h2>
<div class="hw7 board9 grow">
{img('h02_board_top.jpg', '메인보드 3D 렌더 앞면. 왼쪽 위와 가운데에 2열 22핀 헤더 두 줄, 오른쪽 위에 RJ 잭 두 개와 2열 4핀 커넥터 두 개, 오른쪽에 XT60 배터리 단자와 큰 인덕터, 아래에 모터 드라이버 네 개와 XT30 모터 커넥터 네 개, 오른쪽 아래에 전해 커패시터와 Jetson 출력 단자', '메인보드 3D 렌더 앞면', 'shot r3d')}
{table(['항목', '7주차', '이번 주 (V1.0.0)'], BOARD_ROWS, 'comparison h7 bd9')}
</div>
""",
    """팀원이 설계한 메인보드입니다. 크기는 114.2에 91.6밀리미터이고, 회로도 전체와 PCB 배치까지 마쳤으며 아직 제작 전입니다. 왼쪽 위와 가운데에 보이는 두 줄의 긴 헤더가 MCU 코어 보드를 꽂는 자리입니다. 아래쪽에는 모터 드라이버 네 개와 모터 커넥터 네 개가 있고, 오른쪽 위에는 조향과 승강의 절대 엔코더를 잇는 RJ 잭 두 개와 바퀴 엔코더 커넥터 두 개가 있습니다. 오른쪽에는 배터리 단자와 전원부가 있습니다. 7주차와 비교하면 모터 드라이버와 엔코더 회로는 그대로이고, 바뀐 것은 세 가지입니다. 메인 MCU로 STM32H743 코어 보드를 채택해 메인보드에 꽂게 했고, 전원부에 배터리 입력 보호와 Jetson에 줄 19볼트 전원이 더해졌고, 모터와 센서 쪽만 있던 회로도가 전체 회로도와 PCB 배치로 완성됐습니다. (전환)""",
    [(TEAM_PCB, '3D 렌더 앞면(실크 V1.0.0), PCB 배치도 외곽 114.173 × 91.567 mm; 1쪽 MOTOR&SENSOR U14 · U15 · U1 · U11 DRV8244SQRYJRQ1, CN3–CN6 XT30PW-F20 (L · R · M · H), CN1 · CN2 HX JN1.27-2x4P, RJ1 · RJ2 5558067-1; 3쪽 POWER U13 XT60PW-M, SW1; 5쪽 JETSON_19V J2 KF301-5.0-2P'),
     ('week-07/build_deck.py', '7주차 전원 12 V → 5 V 벅 → 3.3 V LDO, MCU Nucleo STM32H533RE, 메인보드 모터 · 센서 쪽 회로도, 향후 작업 "PCB 배치 → 제작"'),
     ('사용자 (2026-10-28)', 'L · R 구동 모터, M 조향, H 승강; 설계자는 화면에 표시하지 않음')],
    '그림: 팀 메인보드 3D 렌더 앞면 (검은 여백만 잘라 냄)')

# ----------------------------------------------------------------- 3
PIN_ROWS = [
    ('모터 드라이버 4개', '공유 SPI, 개별 CS·방향·PWM·차단·고장·전류(ADC)'),
    ('바퀴 엔코더 L·R', 'A·B·Z 펄스 입력'),
    ('조향·승강 절대 엔코더', 'SPI 버스와 개별 CS 2개'),
    ('통신과 저장장치', 'Wi-Fi용 UART, USB, SD 카드(SDMMC)'),
    ('보조 센서와 표시', 'IMU용 SPI CS·인터럽트 자리, 보드 LED'),
]
add('MCU 보드와 핀 배정', '03  MCU 보드와 핀 배정', 50, f"""
<h2 class="headline">480 MHz STM32H743에 모터 드라이버 4개와 엔코더 4개, 통신·센서 핀을 모두 배정</h2>
<div class="hw7 pin9 grow">
{img('h03_layout_top.jpg', '메인보드 PCB 배치도 앞면. 외곽 치수 114.173 mm와 91.567 mm, 2열 22핀 헤더 두 줄 U2와 U4 사이 간격 33.0 mm 치수선, 빨간 구리면 위 배선', '메인보드 PCB 배치도 앞면', 'shot r3d')}
{table(['연결 대상', '배정한 신호'], PIN_ROWS, 'comparison h7 pins9')}
</div>
{band('고성능(Cortex-M7 480 MHz), 많은 핀(100핀), 가격 대비 성능을 보고 메인 MCU로 채택했습니다')}
""",
    """MCU입니다. 메인 MCU로는 STM32H743을 채택했습니다. 이유는 세 가지입니다. 첫째로 Cortex-M7 480메가헤르츠에 플래시 2메가바이트, RAM 1메가바이트로 성능이 높습니다. 둘째로 100핀 패키지라 모터 드라이버 네 개와 엔코더 네 개, 통신과 센서까지 한 칩에 다 붙일 만큼 핀이 많습니다. 셋째로 이 성능에 비해 값이 쌉니다. MCU는 메인보드에 직접 올리지 않고, 이 칩이 달린 시판 코어 보드인 WeAct Studio의 MiniSTM32H7xx를 사서 꽂습니다. 왼쪽 배치도에서 33밀리미터 간격으로 놓인 2열 22핀 헤더 두 줄이 코어 보드 자리입니다. 오른쪽 표는 회로도에서 MCU 핀에 배정한 신호를 묶은 것입니다. 모터 드라이버 네 개는 SPI 한 묶음을 같이 쓰고, 드라이버마다 칩 선택과 방향, PWM, 출력 차단, 고장 신호, 전류 감지를 따로 받습니다. 바퀴 엔코더는 A, B, Z 펄스로, 조향과 승강의 절대 엔코더는 SPI로 들어옵니다. 그 밖에 Wi-Fi 모듈용 UART와 USB, SD 카드 자리, IMU를 달 자리와 보드 LED까지 핀을 정해 두었습니다. (전환)""",
    [(TEAM_PCB, '2쪽 STM32: 헤더 U2 · U4 HC-PM254-8.5H-2x22PZ, A0–A3 L/R/M/H_CS, A5 CLK · A7 MOSI · B4 MISO, B0 MTR_SLEEP, A6 · B1 · C0 · C4 IPROPI, B11–B15 FAULT · KTH_CLK, C1 · C2 KTH_MOSI · MISO, D0 · D1 KTH_CS1 · 2, E1 · E2 · E4–E6 · E9 · E11 · E13 · E14 IN1/IN2, D9 · D10 · D13 · D14 DRVOFF, B10 · D11 · D12 · E1 ENC_A/B, C6 · C7 Z, B8 · B9 · A10 WIFI, A11 · A12 USB_OTG_FS, C8–C12 · D2 SDMMC1, D4 SD_DETECT, D3 · D5 IMU_NCS · IMU_INT, E3 BOARD_LED; PCB 배치도 헤더 간격 33.0 mm'),
     (PINMAP, 'WeAct Studio MiniSTM32H7xx 의 STM32H743VIT6, 초안의 모든 신호 핀이 보드의 2×22 헤더 두 줄(P1 · P2)에 나와 있음'),
     ('사용자 (2026-10-28)', 'MCU 코어 보드 링크 (AliExpress 1005006632336183) — 페이지 내용은 열리지 않아 저장소 핀맵 검토 문서의 보드 이름을 씀'),
     ('ST STM32H743VI 제품 페이지', 'Arm Cortex-M7 480 MHz, 2 MB 플래시, 1 MB RAM')],
    '그림: 팀 메인보드 PCB 배치도 앞면 (외곽 치수선 포함)')

# ----------------------------------------------------------------- 4
POWER_ROWS = [
    ('배터리 입력 (12 V)', 'XT60 입력, 주 스위치(SW1)', '배선 50 A 퓨즈, 역전압·저전압(10.41 V)·과전압 차단'),
    ('모터 구동 (12 V)', '보호 스위치 통과 직결', '순간 과전압 흡수 TVS(SMBJ18CA)'),
    ('로직·센서 (5 V)', 'LMR60440 강압 (5.016 V, 4 A)', '센서 보드에서 각자 3.3 V로 강압'),
    ('Jetson (19 V)', 'LM5122 승압 (목표 3 A)', 'TPS26630 전류 제한(3.2 A), 19.5 V 차단, 5 V 연동'),
    ('배터리 전압 감시', '1/11 저항 분압', 'MCU ADC 연결 준비 (핀 배정 전)'),
]
add('전원 구성과 보호', '04  전원 구성과 보호', 60, f"""
<h2 class="headline">12 V 배터리에 입력 보호를 두고 모터 12 V, 로직 5 V, Jetson 19 V로 분기</h2>
<div class="pw9">{power_diagram()}</div>
{table(['전원 계통', '전압 변환 방식', '보호 회로와 조건'], POWER_ROWS, 'comparison h7 pwt9 grow')}
{band('시제품 제작 뒤에 루프 안정성, 기동, 부하 변동, 발열, 모터 과도 전압을 확인할 예정입니다')}
""",
    """전원부입니다. 12볼트 배터리는 XT60 단자로 들어오고, 배터리 바로 옆 배선에 50암페어 퓨즈를 둡니다. 보드에 들어오면 먼저 입력 보호 스위치를 지납니다. LM74801 컨트롤러와 MOSFET 두 개로 배터리를 거꾸로 꽂아도 전류가 흐르지 않게 막고, 전압이 10.41볼트 아래로 떨어지면 끄고 11.33볼트가 되면 다시 켜며, 16볼트 정도를 넘으면 차단합니다. 주 스위치로 전체를 켜고 끕니다. 이렇게 보호된 12볼트를 세 갈래로 나눕니다. 모터 드라이버 네 개는 12볼트를 그대로 쓰고, LMR60440 강압 컨버터가 5볼트를 만들어 MCU와 센서 보드에 주며, 센서 보드는 7주차처럼 각자 3.3볼트로 한 번 더 낮춥니다. 이번에 새로 들어간 것이 Jetson 전원입니다. LM5122 승압 컨버터로 12볼트를 19볼트로 올리고, 출력 약 3암페어를 목표로 합니다. 뒤에 TPS26630 보호 칩을 두어 전류를 약 3.2암페어로 제한하고 천천히 켜지게 했고, 19.5볼트를 넘으면 끊고 5볼트가 정상일 때만 19볼트가 나가게 했습니다. 배터리 전압은 11분의 1로 나눠 MCU가 읽을 수 있게 했습니다. 아직 만들기 전이라 제작 뒤에 안정성과 발열 같은 항목을 확인할 예정입니다. (전환)""",
    [(TEAM_PCB, '3쪽 POWER: 12V BATTERY INPUT → HIGH-SIDE NMOS SWITCH → VCC, Q6 · Q7 CSD18510Q5B, U16 LM74801QDRRRQ1 「EN UVLO ~11.33V ON / 10.41V OFF. Battery OVP ~16V」, D1 · D2 SMBJ18CA, 「External F1 (50A) is installed beside battery +」 0498050.M · 홀더 04980921GXM5, SW1 MSK12C02, U12 LMR604403SRAKR 「5.016V nominal」(4A IC), ADC_BAT = VCC/11 「MCU ADC pin unassigned」; 5쪽 JETSON_19V: U20 LM5122MH/NOPB 「19V nominal | about 3A output target | 5A power-stage sizing」, U22 TPS26630RGET 「UVLO + current limit ~3.2A + controlled startup」, U21 TLV6700DDCR 「PRECISION OVP (~19.5V) AND 5V INTERLOCK」, J2 「Jetson barrel 5.5/2.5mm, center positive」, 「Prototype review required: loop stability, startup, load steps, thermals and motor transients」'),
     ('그림 사진', 'd02_truck.jpg 팀 차체 사진(5주차), d02_jetson.jpg Wikimedia Commons NVIDIA Jetson Nano Developer Kit (SparkFun, CC BY 2.0) — 8주차 SOURCES.md 와 같은 파일')],
    '그림: 회로도 3 · 5쪽의 전원 경로를 다시 그림')

# ----------------------------------------------------------------- 5c PCB cost (user, 2026-10-28)
COST_ROWS = [
    ('메인보드', '114.2 × 91.6', '$402', '$110'),
    ('바퀴 엔코더 (MT6701)', '22.8 × 10.4', '$13', '$5'),
    ('절대 엔코더 (KTH7801)', '22.8 × 10.4', '$26', '$8'),
    ('STDS 변환 보드', '32.6 × 18.4', '$46', '$12'),
    ('<b>합계</b>', '', '<b>$487</b>', '<b>$135</b>'),
]
add('보드 부품값', '05  보드 부품값', 45, f"""
<h2 class="headline">보드 4종 부품값은 5장씩 약 $487 (약 68만 원), 1장씩이면 약 $135</h2>
{table(['보드', '크기 (mm)', '부품값 (5장)', '부품값 (1장)'], COST_ROWS, 'comparison h7 cost9 grow')}
<p class="note9">LCSC 가격 기준 추정, PCB 제작비와 조립비 제외 (1 USD = 1,400원)</p>
""",
    """보드 부품값입니다. 팀원이 보드 네 종류에 들어가는 부품값을 LCSC 가격으로 추정했습니다. 다섯 장씩 만들면 합계 약 487달러, 우리 돈 약 68만 원이고, 그 대부분인 402달러가 메인보드입니다. 메인보드에는 모터 드라이버 네 개와 전원부 부품이 들어가기 때문입니다. 한 장씩만 만들면 합계 약 135달러입니다. 작은 보드는 최소 주문 단위가 있어 한 장만 사도 장당 값이 조금 비쌉니다. 여기에 PCB 제작비와 조립비는 넣지 않았습니다. 모터 드라이버 DRV8244처럼 재고가 모자란 부품은 다른 곳에서 사거나 대체품으로 바꿉니다. (전환)""",
    [('팀 PCB 제작 비용 비교 (2026-10-28, 로봇 저장소 docs/references/team-hardware/2026-10-28/pcb-cost-comparison.md, 로컬 전용)', '설계별 5장, USD, 1 USD = 1,400원 가정, 견적 전 추정; 합계(부품 + SMT 현재 양면 Standard + PCB): Motor Board $558.91 + PCB(100 × 100 mm 초과, 견적 필요, 장당 약 $111.8), MT_DS $75.53(약 $15.1), KTH7801 $89.72(약 $17.9), STDS $112.89(약 $22.6), 4종 약 $837 + Motor PCB(약 117만 원); Motor 부품값 5장 $402.11 · 1장만 $110.42; 작은 보드 3종 A 따로 주문(양면) 약 $278, B 따로 + 앞면 배치 약 $170, C V-cut 패널 약 $172 + 다른 설계 추가 요금; JLC 재고(2026-10-28 조회) DRV8244 20개 필요 · 재고 3(Mouser 33개), LMR604403 · TPS26630 등 재고 0 → 대체품'),
     ('사용자 (2026-10-28)', 'PCB 가격도 넣어; 부품 가격으로 적고 SMT 조립비는 넣지 말 것'),
     ('계산', '부품값 5장 $402.11 + $13.08 + $25.83 + $46.32 = $487.34(× 1,400 = 약 68.2만 원); 1장만 $110.42 + $4.93 + $7.62 + $11.73 = $134.70')],
    '표: 팀 PCB 제작 비용 비교 문서의 부품값 (LCSC, 5장 · 1장)')

# ----------------------------------------------------------------- 5
ADP_ROWS = [
    ('구멍 지름', '3.25 mm'),
    ('마운트 외경', '5 mm → 6 mm'),
    ('다음 단계', '외경 6 mm 재출력 → 자석 부착 → 엔코더 신호 확인'),
]
add('엔코더 자석 마운트', '06  엔코더 자석 마운트', 50, f"""
<h2 class="headline">3 mm 바퀴 모터 뒤 축에 끼워 본 결과 구멍 3.25 mm 마운트 치수 확정</h2>
<div class="adp9 grow">
{img('h05_print.jpg', '책상 위의 1차 출력물. 회색 PLA 링 아홉 개와 구멍 여섯 개가 뚫린 맞춤 시험 막대', '1차 출력 링과 시험 막대')}
{img('h05_mounted.jpg', '바퀴 모터 뒷면. 가운데 축에 회색 링이 끼워져 있고 양옆으로 노란색, 초록색 전원선', '바퀴 모터 축에 끼운 모습')}
</div>
{table(['항목', '내용'], ADP_ROWS, 'comparison h7 adpt9')}
""",
    """엔코더 자석 마운트입니다. 바퀴 모터 뒤쪽으로 나온 축에 엔코더 자석을 붙여야 하는데, 축을 재 보니 지름 3밀리미터에 2밀리미터 정도만 튀어나와 있어 자석을 바로 붙일 자리가 없습니다. 그래서 축에 끼우는 링을 PLA로 출력해 그 윗면에 자석을 붙입니다. 링 높이는 1.6밀리미터로, 끼웠을 때 윗면이 축 끝과 같은 높이가 되고 아래는 모터 면과 0.4밀리미터 떨어집니다. 3D 프린터로 뽑은 구멍은 설계보다 작게 나오기 때문에, 구멍 지름을 3.00밀리미터부터 3.25밀리미터까지 0.05밀리미터씩 여섯 가지로 뽑고 맞춤 시험 막대도 같이 뽑았습니다. 왼쪽이 그 출력물이고, 실제 축에 끼워 보니 가장 큰 3.25밀리미터가 딱 맞았습니다. 오른쪽이 모터 축에 끼운 모습입니다. 이번 출력은 지름 5밀리미터 자석용이었는데 실제로 붙일 자석은 6밀리미터라서, 바깥 지름을 6밀리미터로 바꿔 다시 출력한 뒤 자석을 붙이고 회전과 엔코더 신호를 확인하겠습니다. (전환)""",
    [('사용자 (2026-10-28)', '모터 축 3 mm, shaft3mm 폴더의 구멍 3.00–3.25 mm 가운데 가장 큰 3.25 mm 가 딱 맞음(실측); 1차 출력은 자석 5 mm 용이라 자석 6 mm 에 맞춰 외경 6.00 mm 로 다시 출력 예정'),
     ('lightminn/forklift artifacts/cad/motor-shaft-magnet-adapter (git 미추적, README · build_adapter.py)', 'shaft3mm/: collar_OD5_H1.6_bore3.00–3.25(0.05 간격), fit_test_bar_bore3.00-3.25; SHAFT_H 2.0(대략 실측) − GAP 0.4 = 높이 1.6, 윗면이 축 끝과 같은 높이; FDM 구멍은 작게 나옴'),
     ('사진', '팀 촬영 2026-10-26 (휴대폰 사진 두 장, 방향 바로잡고 잘라 다시 인코딩)')],
    '사진: 1차 출력물과 모터 축에 끼운 모습 (2026-10-26 팀 촬영)')

# ----------------------------------------------------------------- 5b mount install (user, 2026-10-28)
INSTALL_NOTE = '원통 안지름이 마운트·자석 지름과 같아 둘의 중심이 함께 축에 맞음'
add('자석 장착 방식', '07  자석 장착 방식', 45, f"""
<h2 class="headline">마운트와 자석을 같은 지름의 원통 하나로 감싸 축 중심에 맞춰 붙임</h2>
<div class="sleeve9 grow">
{video('h06_sleeve.mp4', '3D 애니메이션. 모터 축에 끼운 초록색 마운트 위로 단면이 잘린 주황색 원통이 내려와 씌워지고, 빨강과 파랑으로 나뉜 자석이 원통 안으로 내려와 마운트 위에 앉은 뒤, 원통이 위로 빠져나가 마운트와 자석만 남음')}
<div class="stack sleeve9r">
{lgd(('box', '#f2a33a', '중심 맞춤 원통'), ('split', ('#d9534f', '#3d63b8'), '자석'), ('box', '#1f9e4a', '마운트'), ('box', '#8f979f', '모터'))}
<div class="phase-flow vert"><span><b>①</b> 마운트 위에 원통을 씌움</span><span><b>②</b> 원통 안으로 자석을 넣어 접착</span><span><b>③</b> 굳으면 원통을 위로 빼냄</span></div>
</div>
</div>
{band(INSTALL_NOTE + '니다')}
""",
    """자석을 붙이는 방법입니다. 자석이 축 중심에서 벗어나면 엔코더가 읽는 각도에 오차가 생기기 때문에, 마운트와 자석의 중심을 축에 맞추는 것이 중요합니다. 먼저 마운트를 축에 끼우고 평평한 판으로 눌러, 판이 축 끝에 닿을 때 멈춥니다. 그러면 마운트 윗면이 축 끝과 같은 높이가 되고 모터 면과는 틈이 남습니다. 다음으로 자석과 같은 지름의 구멍이 뚫린 원통을 마운트 위에 씌웁니다. 마운트와 자석의 지름이 같아서 이 원통 하나로 둘의 중심을 함께 맞출 수 있습니다. 원통 안으로 자석을 넣는데, 접착제는 가운데에만 조금 발라 원통 벽에 붙지 않게 하고, 원통 옆 창으로 테두리에 접착제가 새지 않았는지 봅니다. 굳으면 원통을 위로 빼내면 됩니다. 영상은 축 3밀리미터, 마운트와 자석 6밀리미터 기준으로 만든 3D 애니메이션이고, 원통은 안이 보이도록 앞쪽 절반을 잘라 그렸습니다. 원통도 이 지름에 맞춰 출력합니다. (전환)""",
    [('lightminn/forklift artifacts/cad/motor-shaft-magnet-adapter (git 미추적) README · install_guide.html', '장착 순서: 평판으로 눌러 칼라 윗면 = 축 끝(모터 면과 0.4 mm 틈), 젤형 순간접착제로 칼라 고정, 중심 맞춤 관(magnet_centring_tube_id5.20 · id5.30)을 칼라에 1.2 mm 걸쳐 씌움, 접착제는 가운데에만(관에 붙지 않게, 창으로 테두리 확인), 굳으면 관을 위로 뺌; 칼라와 자석이 같은 지름이라 한 구멍으로 둘 다 맞춤, 중심 어긋남 여유 0.2 mm(5.20 관)'),
     ('영상', 'week-09/tools/sleeve_anim.html(three.js r128)을 헤드리스 Chromium 에서 8 s 녹화(MediaRecorder) → H.264; 축 Ø3, 마운트 외경 6 · 구멍 3.25 · 높이 1.6, 모터 면 틈 0.4, 자석 Ø6, 원통 구멍 6.2 · 걸침 1.2(1차 설계값); 자석 두께 2.5 · 원통 벽은 그림용 값, 원통은 앞쪽 절반을 잘라 보임'),
     ('사용자 (2026-10-28)', '장착 방식(원통으로 맞추는 것)도 보여 달라')],
    '영상: 장착 순서 3D 애니메이션')

# ----------------------------------------------------------------- 6
LOC_ROWS = [
    ('방식', '지도를 만들며<br>위치 찾기', '<b>만들어 둔 지도에서<br>위치만 찾기</b>'),
    ('위치 오차', '9–12 cm', '<b>3–4 cm</b>'),
    ('1시간 운행', 'SLAM 끊김', '<b>끊김 없음</b>'),
]
add('미리 만든 지도 위치 추정', '08  미리 만든 지도 위치 추정', 60, f"""
<h2 class="headline">지도를 먼저 만들어 두고 그 위에서 위치를 찾게 바꿔 위치 오차 9–12 cm → 3–4 cm</h2>
<div class="loc9 grow">
{video('l06_prebuilt_map.mp4', '위에서 본 Isaac 랜덤 배치 장면. 지게차가 미리 만든 지도 위에서 위치를 찾으며 왼쪽 적재 구역의 팔레트 세 개를 차례로 집어 오른쪽 하역 구역의 세 칸에 내려놓음', '만들어 둔 지도로 팔레트 3개 연속 운반')}
<div class="stack loc9r">
<figure class="chart9">{error_chart()}<figcaption>1시간 운행 위치 오차</figcaption></figure>
{lgd(('line', ORANGE, '기존'), ('line', BLUE, '지금'))}
{table(['', '기존', '지금'], LOC_ROWS, 'comparison h7 loct9')}
</div>
</div>
<div class="phase-flow map9"><span><b>① 첫 주행</b> 지게차가 LiDAR로 지도 작성</span><span class="arrow">→</span><span><b>② 작업</b> 그 지도에서 위치만 찾기</span><span class="sep9">지도는 따로 받지 않고, 배치가 바뀌면 다시 주행</span></div>
""",
    """소프트웨어입니다. 지금까지는 지게차가 운행하면서 SLAM으로 지도를 만들고, 동시에 그 지도 위에서 자기 위치를 찾았습니다. 그러면 지도 자체가 계속 바뀌어 위치가 흔들립니다. 이번 주에는 방식을 바꿔, 처음 한 번 주행해 지도를 만들어 두고 실제 작업 때는 그 고정된 지도 위에서 위치만 찾게 했습니다. 왼쪽 영상은 지금 방식으로 Isaac에서 팔레트 세 개를 차례로 옮기는 장면입니다. 오른쪽 위 그래프는 같은 장면을 한 시간 동안 운행하며 잰 위치 오차입니다. 주황색인 기존 방식은 10에서 20센티미터를 오르내리다가, 지도가 커지면서 계산이 1초 안에 끝나지 못해 56분쯤 SLAM이 끊겼습니다. 파란색인 지금 방식은 65분 내내 3에서 4센티미터를 유지했습니다. 지도는 누가 미리 주는 것이 아닙니다. 새 장소에서 처음 한 번 주행할 때 지게차가 LiDAR로 직접 지도를 만들어 저장하고, 그다음부터의 작업은 그 지도 위에서 위치만 찾습니다. 선반이나 벽 같은 배치가 바뀌면 그 장소를 다시 한 번 주행해 지도를 새로 만듭니다. 시뮬레이션에서는 이 첫 주행도 평소 작업처럼 팔레트를 옮기며 했고, 실차에서 첫 주행을 어떻게 할지는 아직 정하는 중입니다. 여러 번 돌린 결과로 보면 위치 오차 중앙값이 9에서 12센티미터에서 3에서 4센티미터로 줄었고, 하역 칸에 맞춰 들어갈 때 옆으로 치우치는 정도도 최대 22센티미터에서 1.2센티미터로 줄었습니다. (전환)""",
    [(SLAM_PLAN, '5b 1차 확인(ws1 s3conf_874e44a4, 장면 line_m · random_m × seed 1 · 2): 적용 위치 오차 중앙 L 0.029–0.038 m · R 0.089–0.119 m, L 은 SLAM 끊김 없음; 5d 2차 확인(s3conf2_3a37e216): R line_m 두 실행 slam_link_failed 3,371 · 3,610 s(해당 scan 응답 1.149 · 1.096 s 로 1 s 기한 초과, 지도 그래프 증가 유형), L 네 실행 SLAM 끊김 없음; 사용자 결정(2026-10-27) (b) 예외 채택으로 live 기본 A 전환, 받아들인 한계 셋은 5d'),
     (REMEASURE, '하역 도킹 1회차 estimate_vs_truth_at_match |dy| 최대: A 0.012 m(36개) 대 mapping rh 0.219 m(9개); 두 배치는 seed · 스냅숏 · 목적지 구성이 달라 기술 비교'),
     ('그래프', 'ws1 test_runs/live/s3conf2_3a37e216 의 s3b_R_line_m_s3 · s3b_L_line_m_s3 spool/slam.control 행 [t, 적용 후축 x, y, yaw, 참값 x, y, yaw] 에서 |적용 − 참| 위치를 1분 구간 중앙값으로 (시뮬 시간, team-spec 오도메트리, D7_HOLD 끔)'),
     ('영상', 'ws1 test_runs/live/dk9a_36b9b7de/dk9a_random_m_s0 (잡 12032, 2026-10-28): random_m 대기열 P-4:D-1, P-5:D-2, P-3:D-3, seed 0, 등록부 지도(random_m_team_spec_quantized_0facac3eea66) 위 위치 추정, D7_HOLD 켬, 3/3 완료; transport.mp4 탑뷰를 1160 × 660 at x 110 으로 잘라 12배속. 스냅숏 dk9v_36b9b7de 는 trf_36b9b7de 에서 record_video_overlay(t) 한 줄만 stamp 로 바꾼 렌더용 사본'),
     ('지도 만드는 법', 'console/README.md「SLAM 지도」: 조사 에폭(slam_survey.sbatch, live 미션을 지도 작성 모드로 돔)으로 묶음을 만들고 수락 검사 뒤 등록부에 올림, 배치가 바뀌면 다시 조사; 실차 지도의 수락 · 조사 주행 방법은 미정(계획 6장), 자율 조사는 보류(사용자 결정, S-P1 뒤)'),
     ('운용 흐름', '조사 에폭(slam_survey.sbatch)으로 장면별 지도 묶음을 만들어 등록부(config/slam_map_bundles.yaml)에 올리고, 콘솔 live 는 그 묶음 위에서 위치 추정')],
    '영상: Isaac Sim 탑뷰 (12배속), 그림: S3 2차 확인 일자 배치 seed 3 두 실행의 위치 오차 (1분 중앙값)')

# ----------------------------------------------------------------- 7
FMS_ITEMS = [
    ('c07_queue.png', '콘솔 차량 상세의 대기열. 남은 팔레트 전부 항목이 진행 중 M-0002, P-02에서 D-B로 실행 중이고 끝낸 항목 완료 1',
     '작업 대기열과 운반 버튼', '쌓아 둔 작업을 차례로 내고 이상이 생기면 멈춤 (MiR, OTTO 참고)'),
    ('c07_health.png', '콘솔 상태·경보 화면. 제어 연결, 미디어 연결, 상태 수신, 위치, 영상, 스캔, 지도, 차량 피드백, 정지, 구동 허가, 장면, 세션이 모두 초록 정상이고 경보 없음',
     '장비 상태와 경보 화면', '연결과 센서 이상 여부를 한 화면에서 확인 (MiR, SARICS 참고)'),
    ('c07_summary.png', '콘솔 미션 결과 요약. 완료 2, 실패 0, 취소 0, 완료율 100 퍼센트, 팔레트별 P-01 1/1, P-02 1/1',
     '운행 실적 요약 화면', '세션의 완료율과 실패 사유를 모아 확인 (OTTO, MiR 참고)'),
]


def fms_cap(src, alt, title, desc):
    return (f'<figure class="shot"><img class="media" src="assets/{src}" alt="{escape(alt, quote=True)}">'
            f'<figcaption><b>{title}</b><br>{desc}</figcaption></figure>')


add('콘솔과 상용 FMS 비교', '09  콘솔과 상용 FMS 비교', 55, f"""
<h2 class="headline">상용 관제 7종을 참고해 작업 대기열, 장비 상태·경보, 실적 요약 화면 추가</h2>
<div class="caps9 grow">
{''.join(fms_cap(*it) for it in FMS_ITEMS)}
</div>
{band('여러 대를 관제할 때는 중앙 서버가 차량마다의 작업 단위 API를 그대로 중계하는 구조이고, 지금은 1대와 1:1로 연결합니다')}
""",
    """운용 콘솔을 상용 FMS와 비교한 결과입니다. FMS에는 정해진 표준이 없어서, 피드백에서 말씀하신 시스콘로보틱스의 SARICS를 포함해 OTTO, MiR, BlueBotics, Seegrid, AGILOX, VisionNav 일곱 제품의 공개 자료를 보고 기능을 비교했습니다. 지도 위 차량 표시, 작업 지시, 진행 단계 표시, 수동 조종은 8주차에 이미 있었습니다. 이번에 넣은 것은 세 가지입니다. 첫째는 작업 대기열입니다. 작업을 쌓아 두면 하나씩 차례로 내고, 남은 팔레트를 전부 옮기는 항목은 차량이 다음 팔레트와 하역 칸을 골라 줍니다. 실패나 취소, 연결 끊김 같은 이상이 생기면 대기열이 멈추고 운용자가 다시 재개할 때까지 다음 작업을 내지 않습니다. 둘째는 연결과 각 센서 수신 상태를 한 화면에서 정상, 주의, 위험으로 보여 주고 이상을 경보 목록에 남기는 화면이고, 셋째는 완료, 실패, 취소 수와 팔레트별 실적을 보여 주는 요약입니다. 여러 대로 넓힐 때는 중앙 관제 서버가 각 차량의 같은 작업 단위 API를 중계하면 되도록 만들었고, 지금은 Jetson이 공유기가 되어 콘솔과 1:1로 연결합니다. 차량 배정이나 차량끼리의 교통 순서 같은 여러 대 전용 기능과, 금지 구역, 배터리 표시는 아직 없습니다. 화면은 콘솔 개발용 모의 차량으로 찍은 것입니다. (전환)""",
    [(FMS, '2절 제품별 기능(SARICS · OTTO · MiR · BlueBotics · Seegrid · AGILOX · VisionNav), 3절 공통 기능과 콘솔, 4절 도입 후보 1–3, 5절 1대 구성에 맞지 않아 뺀 것(차량 배정, 교통 관제, 함대 대시보드 등); 금지 · 감속 구역은 OTTO · MiR · SARICS, 배터리 · 충전은 OTTO · Seegrid · BlueBotics · SARICS'),
     (CONSOLE, '대기열과 저장된 운반, 남은 팔레트 전부(capabilities.next_pick), 이상 시 멈춤 정책; 상태 · 경보(정상 · 주의 · 위험 · 모름 · 해당 없음, 0.5 s 이어지면 경보); 실적 요약(이 세션의 결과 기록부, 최근 100건)'),
     ('lightminn/forklift docs/design/2026-10-13-operator-console.md 2절', '망: 1단계는 Jetson AP 1:1, 여러 대가 되면 중앙 서버 경유(사용자 결정); 게이트웨이는 ROS 토픽이 아니라 작업 단위 API'),
     (MOCK, '「남은 팔레트 전부 옮기기」 → 재개(2단계 확인) → P-01 → D-A, P-02 → D-B 완료; 대기열 · 상태·경보 · 요약 자세히 화면을 잘라 냄')],
    '그림: 콘솔 화면 캡처 세 장 (모의 차량)')

# ----------------------------------------------------------------- 8
END_ROWS = [
    ('하드웨어', '<b>메인보드</b>', '회로도와 PCB 배치 완료 → 메인보드 제작'),
    ('하드웨어', '<b>엔코더 마운트</b>', '축 구멍 3.25 mm 맞춤 확인 → 외경 6 mm 출력·장착 뒤 신호 확인'),
    ('소프트웨어', '<b>리보틱스 시연 장면</b>', '남은 제안 상황에 맞춰 코드 계속 수정'),
    ('소프트웨어', '<b>위치 추정</b>', '사전 지도 위 오차 3–4 cm → 전역 재위치 추가'),
]
add('결론과 다음 주 계획', '10  결론과 다음 주 계획', 55, f"""
<h2 class="headline">다음 주는 메인보드·마운트를 제작하고 리보틱스 시연 장면과 재위치를 보완</h2>
{table(['구분', '대상', '현재 → 다음 단계'], END_ROWS, 'comparison h7 endt9 grow', merge_first=True)}
""",
    """결론과 다음 주 계획입니다. 이번 주에는 피드백대로 하드웨어를 앞으로 당겨, H743 코어 보드와 Jetson 전원까지 들어간 메인보드의 회로도와 PCB 배치를 마쳤고 엔코더 자석 마운트의 축 끼워맞춤을 확인했습니다. 소프트웨어에서는 미리 만든 지도 위에서 위치를 추정해 오차를 3에서 4센티미터로 줄였고, 콘솔에 대기열과 상태, 경보, 실적 요약을 넣었습니다. 다음 주에는 메인보드를 제작하고, 마운트를 6밀리미터 자석에 맞춰 다시 출력해 모터에 단 뒤 엔코더 신호가 제대로 나오는지 확인하겠습니다. 소프트웨어에서는 리보틱스가 제안한 시연 상황 가운데 아직 안 되는 장면들에 맞춰 코드를 계속 고치겠습니다. 또 지금 방식은 위치를 크게 잃으면 지도 위에서 스스로 다시 찾지 못해서, 다시 찾는 전역 재위치를 만들겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [(SLAM_PLAN, 'D7: slam_toolbox 위치 추정에는 전역 재위치가 없다'),
     ],
    '표: 하드웨어 · 소프트웨어 다음 단계')


TITLE = '9주차 자율 지게차 개발'
TOTAL = 540


def build():
    assert len(slides) == 11, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-10-28. 8주차 피드백에 답하는 구성이다. 메인보드는 회로도와 PCB 배치까지이고 제작 · 측정 전이다. '
              '위치 추정 수치는 Isaac 시뮬레이션 값이고, 콘솔 화면은 모의 차량으로 찍었다(SOURCES.md). '
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
                   '', s['notes'], '']   # no [Sources] blocks in the script (user, 2026-10-14); SOURCES.md and the speaker notes keep them
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
