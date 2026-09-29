"""Build the week 5 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 5 is a hardware report: chassis, fork and pallet measurements, the
logic-analyser reverse engineering of the remote control, and the choice of
motor driver (DRV8244-Q1) and encoder (MT6701). The measurement and waveform
slides are placeholders until the team's data arrives. The LiDAR simulation
slides drafted here on 2026-09-29 moved to week-06/ for next week.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
MAP = 'docs/plans/2026-09-11-development-roadmap.md'
INTAKE = 'docs/validation/2026-09-23-chassis-intake.md'
MODEL = 'sim/models/dls08_provisional/parameters.yaml'
FEEDBACK = 'docs/references/week4_feedback.md'
slides = []



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


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '5주차\n자율 지게차 개발', 20, '',
    """이번 주에는 하드웨어를 다룬다. 입고한 차체와 포크, 동봉 팔레트를 실측하고, 4주차 피드백에 따라 조종기와 제어기를 로직 애널라이저로 역분석하여, 기존 제어기가 릴레이로 모터를 켜고 끄기만 한다는 것을 확인하였다. 이어서 컴퓨터가 차체를 직접 구동하고 상태를 읽기 위한 부품으로 모터 드라이버와 엔코더를 선정한 근거를 보인다. 끝으로 우리 임무 절차를 지게차 표준 운용 절차와 대조하고, 리보틱스 중간 미팅 질문을 정리한다.""",
    [(INTAKE, '입고 조사'), (FEEDBACK, '4주차 피드백 §2')], '진행 보고')

# ----------------------------------------------------------------- 3 (placeholder)
HOT = ' class="hot"'
MEASURE_ROWS = [  # item, measured, provisional model
    ('축간 거리 · 윤거', '0.66 · 0.53 m', '0.64 · 0.51 m (사진 추정)'),
    ('바퀴 반지름', '0.125 m', '0.135 m (사진 추정)'),
    ('최대 조향각', '15°', '25.8° (0.45 rad, 추정)'),
    ('최소 회전 반경 (계산)', '약 2.5 m', '약 1.3 m'),
    ('포크 길이 · 폭 · 두께', '360 · 55 · 25 mm', '420 · 55 · 24 mm (사진 추정)'),
    ('포크 중심 간격', '55–380 mm 조절', '290 mm 고정 (사진 추정)'),
    ('전장 × 전폭 × 전고 · 질량', '측정 예정', '1.46 × 0.63 × 1.01 m · 24 kg (카탈로그)'),
    ('승강 범위', '측정 예정', '280 mm (사진 추정)'),
]
measure_table = ''.join(
    f'<tr{HOT if k.startswith(("최대 조향각", "최소 회전")) else ""}><td>{k}</td><td><b>{m}</b></td><td class="muted">{v}</td></tr>'
    for k, m, v in MEASURE_ROWS)
add('차체 실측', '01  차체 실측', 65, f"""
<h2 class="headline">최대 조향각 15° → 최소 회전 반경 약 2.5 m, 잠정 모델의 약 2배</h2>
<div class="split grow" style="grid-template-columns:0.8fr 1.2fr">
{figure('30_chassis_pallet.jpg', '입고한 지게차 차체와 앞에 놓인 동봉 플라스틱 팔레트', '차체와 동봉 팔레트 (2026-09-30 촬영)', cls='')}
<div class="stack" style="gap:8px;justify-content:center"><table class="comparison measure chassis"><tr><th>항목</th><th>실측</th><th>잠정 모델</th></tr>{measure_table}</table><p class="chart-cap">회전 반경 = 축간 거리 ÷ tan(최대 조향각), 뒤차축 중심 기준 계산값</p></div>
</div>
<div class="takeaway">반영: 실측값으로 시뮬레이션 모델 갱신 · 회전 반경 증가로 접근·후진 경로 다시 계획</div>
""",
    """차체를 직접 잰 결과를, 지금까지 시뮬레이션에 쓴 잠정 모델과 비교한 표이다. 잠정 모델은 상품 사진과 카탈로그로 만든 것이다. 축간 거리와 윤거, 바퀴 반지름은 1에서 2센티미터 차이로 잠정값과 비슷했다. 가장 큰 차이는 최대 조향각이다. 실측은 15도로 잠정 모델의 약 26도보다 훨씬 작다. 축간 거리 0.66미터를 이 각도로 나누어 계산하면 최소 회전 반경이 약 2.5미터로, 잠정 모델의 약 1.3미터의 두 배 가까이 된다. 그래서 팔레트에 비스듬히 다가가거나 가까이서 방향을 바꾸는 경로가 훨씬 넓은 공간을 필요로 하며, 접근과 후진 경로를 실측값으로 다시 계획한다. 포크는 길이 36센티미터로 잠정값보다 6센티미터 짧고, 두 포크의 간격을 5.5에서 38센티미터까지 조절할 수 있다. 회전 반경은 계산값이므로 주행 시험으로 확인하고, 전장과 질량, 승강 범위는 이어서 잰다.""",
    [('팀 실측 (2026-09-30)', '윤거 53 cm, 축간 거리 66 cm, 바퀴 반지름 12.5 cm, 포크 길이 36 · 폭 5.5 · 두께 2.5 cm, 포크 중심 간격 최대 38 · 최소 5.5 cm(중간 공간 없음), 최대 조향각 15°'),
     (MODEL, '잠정 모델 — steering_limit_rad 0.45, fork_spacing 0.29 m, wheel_track 0.51 m, wheel_radius 0.135 m'),
     ('계산', '최소 회전 반경 = L / tan δ: 0.66 / tan 15° = 2.46 m, 잠정 0.64 / tan 0.45 = 1.32 m (뒤차축 중심, 자전거 모델)')],
    '화면 생성: 실물 사진(2026-09-30, EXIF 제거) · 팀 실측값')

# ----------------------------------------------------------------- 3 (placeholder)
PALLET_ROWS = [
    ('외형 (길이 × 폭)', '약 42 × 30 cm', '길이는 다리 바깥 기준'),
    ('전체 높이', '약 8.5 cm', ''),
    ('상판 두께', '약 2 cm', ''),
    ('포크 진입 높이', '약 6.5 cm', '바닥 ~ 상판 아래'),
    ('구조', '다리 9개 (3 × 3)', '네 방향 진입'),
    ('포크 폭 · 두께', '5.5 · 2.5 cm', '진입 높이 대비 상하 여유 약 4 cm'),
    ('포크 중심 간격', '5.5–38 cm 조절', ''),
]
pallet_table = ''.join(f'<tr><td class="step">{a}</td><td><b>{b}</b></td><td class="muted">{c}</td></tr>' for a, b, c in PALLET_ROWS)
add('포크·동봉 팔레트', '02  포크 · 동봉 팔레트', 40, f"""
<h2 class="headline">동봉 팔레트 약 42 × 30 × 8.5 cm · 포크 진입 높이 약 6.5 cm</h2>
<div class="split grow" style="grid-template-columns:0.95fr 1.05fr">
{figure('32_pallet_on_forks.jpg', '포크 위에 올린 동봉 팔레트', '포크 위에 올린 동봉 팔레트', cls='')}
<div class="stack" style="gap:10px">
<table class="comparison select pallet"><tr><th>항목</th><th>값</th><th>비고</th></tr>{pallet_table}</table>
<div class="thumbs"><img src="assets/33_pallet_length.jpg" alt="줄자로 잰 팔레트 길이"><img src="assets/34_pallet_height.jpg" alt="줄자로 잰 팔레트 높이"><img src="assets/35_pallet_width.jpg" alt="줄자로 잰 팔레트 폭"></div>
<p class="chart-cap">팔레트 값은 줄자 사진 눈금 판독 · 포크는 팀 실측</p>
</div>
</div>
""",
    """차체와 함께 온 플라스틱 팔레트를 줄자로 쟀다. 외형은 약 42 곱하기 30센티미터이고, 전체 높이는 약 8.5센티미터, 상판 두께는 약 2센티미터이다. 따라서 포크가 들어갈 수 있는 높이는 바닥에서 상판 아래까지 약 6.5센티미터이다. 다리는 3 곱하기 3으로 아홉 개라 네 방향 어디서든 포크를 넣을 수 있다. 왼쪽처럼 포크 위에 올려 크기를 맞춰 보았다. 포크는 폭 5.5센티미터, 두께 2.5센티미터라 진입 높이 6.5센티미터에 대해 위아래로 약 4센티미터의 여유가 있다. 두 포크의 간격은 5.5에서 38센티미터까지 조절되므로 팔레트 다리 사이에 맞춰 정한다.""",
    [('팀 실측 사진 (2026-09-30)', '팔레트 길이·높이·폭 줄자 사진 3장 — 값은 사진 눈금 판독, 길이는 다리 바깥 기준'),
     (MODEL, '잠정 모델 포크 치수 — 사진 추정')],
    '화면 생성: 실물 사진(2026-09-30, EXIF 제거)')

# ----------------------------------------------------------------- 4-7 remote reverse engineering
# Traces are drawn from assets/data_la_edges.json (prepare_la.py): the level
# changes of three DSLogic Pro captures, 1 MHz, two channels.
LA = json.loads((ROOT / 'assets/data_la_edges.json').read_text())
LA_ROWS = [  # capture, title, command name per channel (CH0, CH1)
    ('drive', '주행 · 앞 → 뒤 → 앞 → 뒤', ('앞', '뒤')),
    ('lift', '승강 · 상승 → 하강 → 상승 → 하강', ('하강', '상승')),
    ('steer', '조향 · 왼쪽 (내보낸 구간에 명령 1회)', ('왼쪽', '오른쪽')),
]
CH_COLOURS = ('#1f5fae', '#c26a1a')
GLITCH_S = 0.01   # shorter than this = contact/ground bounce, not a command


def la_segments(key):
    """(channel, start, end) for each run where exactly one channel is high."""
    e = LA[key]['edges'] + [[LA[key]['end_s'], 0, 0]]
    runs = []
    for (t, a, b), (t2, _, _) in zip(e, e[1:]):
        if a + b == 1:
            runs.append((0 if a else 1, t, t2))
    return runs


def la_commands(key):
    return [r for r in la_segments(key) if r[2] - r[1] >= GLITCH_S]


def la_traces():
    W, left, lane, gap = 1180, 150, 52, 26
    rows_h = []
    parts = []
    y = 10
    for key, title, names in LA_ROWS:
        cap = LA[key]
        t0, t1 = cap['start_s'], cap['end_s']
        sx = lambda t: left + (t - t0) / (t1 - t0) * (W - left - 10)
        parts.append(f'<text x="0" y="{y + 16}" font-size="21" font-weight="700" fill="#1b1f24">{title}</text>')
        y += 28
        for ch in (0, 1):
            base = y + lane * (ch + 1) - 6
            parts.append(f'<text x="{left - 14}" y="{base - 6}" text-anchor="end" font-size="17" fill="{CH_COLOURS[ch]}">CH{ch}</text>')
            pts, level = [], 0
            for t, a, b in cap['edges']:
                v = (a, b)[ch]
                x = sx(t)
                pts.append(f'{x:.1f},{base - level * 22}')
                pts.append(f'{x:.1f},{base - v * 22}')
                level = v
            pts.append(f'{sx(t1):.1f},{base - level * 22}')
            parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{CH_COLOURS[ch]}" stroke-width="2.5"/>')
        for ch, a, b in la_commands(key):
            base = y + lane * (ch + 1) - 6
            parts.append(f'<text x="{(sx(a) + sx(b)) / 2:.1f}" y="{base - 27}" text-anchor="middle" font-size="16" font-weight="700" fill="{CH_COLOURS[ch]}">{names[ch]} {b - a:.2f} s</text>')
        y += lane * 2 + gap
    return (f'<svg class="diagram grow" viewBox="0 0 {W} {y}" role="img" aria-label="주행·승강·조향 명령별 두 채널의 로직 애널라이저 파형. '
            f'명령마다 한 채널만 켜지고, 누르는 동안 신호가 바뀌지 않는다"><g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


def la_zoom(key='drive', centre=5.0906, span=0.008):
    """Press edge of one command, a few milliseconds wide."""
    W, H, left = 560, 250, 70
    cap = LA[key]
    t0, t1 = centre - span / 2, centre + span / 2
    sx = lambda t: left + (min(max(t, t0), t1) - t0) / (t1 - t0) * (W - left - 10)
    parts = []
    for ch in (0, 1):
        base = 90 + ch * 90
        parts.append(f'<text x="{left - 12}" y="{base - 6}" text-anchor="end" font-size="17" fill="{CH_COLOURS[ch]}">CH{ch}</text>')
        level = 0
        for t, a, b in cap['edges']:
            if t <= t0:
                level = (a, b)[ch]
        pts = [f'{sx(t0):.1f},{base - level * 40}']
        for t, a, b in cap['edges']:
            if t0 < t < t1:
                v = (a, b)[ch]
                pts += [f'{sx(t):.1f},{base - level * 40}', f'{sx(t):.1f},{base - v * 40}']
                level = v
        pts.append(f'{sx(t1):.1f},{base - level * 40}')
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{CH_COLOURS[ch]}" stroke-width="3"/>')
    both = next((t, t2) for (t, a, b), (t2, _, _) in zip(cap['edges'], cap['edges'][1:]) if a and b and t0 < t < t1)
    parts.append(f'<rect x="{sx(both[0]):.1f}" y="30" width="{sx(both[1]) - sx(both[0]):.1f}" height="160" fill="#c0392b" opacity="0.10"/>'
                 f'<text x="{(sx(both[0]) + sx(both[1])) / 2:.1f}" y="222" text-anchor="middle" font-size="17" fill="#c0392b">두 채널 동시 High {(both[1] - both[0]) * 1000:.1f} ms</text>'
                 f'<text x="{left}" y="244" font-size="15" fill="#6b7785">{span * 1000:.0f} ms 구간 · 누르는 순간</text>')
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="누르는 순간 두 채널이 약 3 ms 동시에 High가 된 뒤 한 채널만 남는 파형">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


add('측정 구성', '03  조종기·제어기 리버스 엔지니어링', 50, f"""
<h2 class="headline">무선 조종기·제어기 신호를 로직 애널라이저로 측정</h2>
<div class="split grow" style="grid-template-columns:0.9fr 0.9fr 1.2fr">
{figure('37_la_setup.jpg', '메인보드에 로직 애널라이저 DSLogic Pro 탐침을 연결한 측정 구성', '메인보드 ↔ DSLogic Pro 연결', cls='')}
{figure('36_board_voltage.jpg', '멀티미터로 메인보드 전원 전압 12.23 V를 잰 모습', '메인보드 전원 12.23 V (멀티미터)', cls='')}
<table class="comparison select setup"><tr><th colspan="2">측정 구성</th></tr>
<tr><td>장비</td><td>DSLogic Pro · 멀티미터</td></tr>
<tr><td>샘플링</td><td>1 MHz · 2채널 (CH0 · CH1)</td></tr>
<tr><td>전원</td><td>메인보드 12.23 V</td></tr>
<tr><td>주행</td><td>앞 → 뒤 → 앞 → 뒤</td></tr>
<tr><td>승강</td><td>상승 → 하강 → 상승 → 하강</td></tr>
<tr><td>조향</td><td>왼쪽 → 오른쪽 → 왼쪽 → 오른쪽</td></tr></table>
</div>
<div class="takeaway">4주차 피드백: 버튼별 신호를 로직 애널라이저로 측정 · 기존 제어기 리버스 엔지니어링</div>
""",
    """4주차 피드백에 따라 조종기와 제어기를 역으로 분석하였다. 장비는 DSLogic Pro 로직 애널라이저와 멀티미터이다. 왼쪽은 메인보드에 로직 애널라이저를 연결한 모습이고, 가운데는 멀티미터로 잰 메인보드 전원 12.23볼트이다. 로직 애널라이저는 1메가헤르츠로 두 채널을 기록했고, 주행은 앞과 뒤, 승강은 상승과 하강, 조향은 왼쪽과 오른쪽을 번갈아 두 번씩 눌렀다. 제어기에는 무선 수신 회로까지 모두 한 보드에 들어 있다.""",
    [(INTAKE, '조종기·제어기 표기와 사진'), (FEEDBACK, '§2 로직 애널라이저로 버튼별 신호 측정, 리버스 엔지니어링'),
     ('forklift-presentations/week-05/assets/data_la_edges.json', 'DSLogic 캡처 3개 (1 MHz, 2채널) — prepare_la.py 로 추출')],
    '화면 생성: 실물 사진(2026-09-23 입고) · 팀 측정 기록')

add('명령별 파형', '04  명령별 로직 애널라이저 파형', 70, f"""
<h2 class="headline">명령마다 한 채널만 켜짐: 방향은 채널, 동작 시간은 누른 시간</h2>
{la_traces()}
""",
    """세 번의 측정 파형이다. 주행에서는 앞 버튼을 누르면 CH0가, 뒤 버튼을 누르면 CH1이 켜지고, 버튼을 누른 시간만큼 켜져 있다. 승강도 같은 구조로 상승은 CH1, 하강은 CH0이다. 즉 두 선 가운데 어느 쪽에 전압을 거느냐로 모터의 회전 방향이 바뀐다. 조향 파일은 내보낸 구간에 왼쪽 명령 한 번만 들어 있어 나머지 명령은 다시 확인한다.""",
    [('forklift-presentations/week-05/assets/data_la_edges.json', '엣지 목록 — 주행 19 · 승강 28 · 조향 31개, 조향 CSV 는 7.72–16.69 s 구간만 포함'),
     ('forklift-presentations/week-05/prepare_la.py', 'DSLogic CSV → 엣지 추출')],
    '화면 생성: DSLogic 캡처 엣지로 그린 파형 (명령 옆 숫자 = 켜진 시간)')

drive_cmds = la_commands('drive') + la_commands('lift')
add('PWM 없음', '05  파형 해석', 60, f"""
<h2 class="headline">측정한 두 선은 켜짐·꺼짐뿐, 회로 조사 결과 릴레이 구동</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
<div class="stack" style="justify-content:center">{la_zoom()}<p class="chart-cap">누르는 순간 약 3 ms 두 채널 동시 High (주행 4회 모두) · 팀 판단: 전환 순간 접지 튐, 추가 확인</p></div>
<div class="fb-cards licence" style="align-self:center;grid-template-columns:1fr;grid-template-rows:auto">
<article><h3>파형 (측정한 두 선)</h3><p>명령 {len(drive_cmds)}회, 켜진 동안 1 MHz 샘플에서 변화 0회 → PWM 신호 아님</p></article>
<article><h3>회로 조사 (팀)</h3><p>릴레이로 모터 켜짐·꺼짐 · 정·역 전환만<br>속도 조절 기능 자체가 없음</p></article>
<article class="key"><h3>의미</h3><p>모터를 켜고 끄는 열린 루프 · 속도·위치 제어 불가</p></article>
</div>
</div>
""",
    """파형과 회로 조사를 합친 해석이다. 먼저 파형에서 직접 확인한 것은, 측정한 두 선이 명령이 켜져 있는 동안 1메가헤르츠 샘플에서 한 번도 바뀌지 않았다는 것이다. PWM이라면 켜짐과 꺼짐이 빠르게 반복되어야 하므로 이 두 선은 PWM 신호가 아니라 켜짐과 꺼짐 레벨이다. 왼쪽은 누르는 순간을 몇 밀리초로 확대한 것으로, 주행 명령 네 번 모두 약 3밀리초 동안 두 채널이 함께 켜졌다가 한 채널만 남는다. 팀은 전환 순간 접지가 튄 것으로 보고 있으며, 모터 단자를 함께 재서 확인한다. 회로를 따라가 보니 모터는 릴레이로 켜고 끄며 방향만 바꾸고, 조종기에 속도 버튼이 있지만 속도 조절 기능 자체가 없었다. 결국 기존 제어기로는 속도나 위치를 제어할 수 없다.""",
    [('forklift-presentations/week-05/assets/data_la_edges.json', '명령 구간 내 엣지 0개 (1 µs 튐 제외), 주행 누름 순간 두 채널 동시 High 2.95–3.43 ms 4회 — 원인은 팀 판단(접지 튐), 미확정'),
     ('팀 리버스 엔지니어링 보고 (2026-09-30)', '릴레이 구동, 속도 조절 기능 없음 (회로 조사)'),
     (FEEDBACK, '§2 버튼별 신호 확인')],
    '화면 생성: DSLogic 캡처 엣지 확대')

RE_ROWS = [
    ('전원 스위치', '+ 와 V 를 직접 연결하는 단순 스위치', '재활용'),
    ('무선 수신', 'RF 회로가 메인보드에 통합', '분리 불가 → 사용 안 함'),
    ('모터 구동', '릴레이 켜짐·꺼짐 · 정·역 전환만', '대체'),
    ('속도 조절', 'PWM·전압 제어 없음 · 기능 자체 없음', '새로 구현'),
    ('주행 모터 (양쪽 바퀴)', '—', '재활용'),
    ('리프트 모터', '—', '재활용 · 높이 센서 필요'),
]
re_table = ''.join(f'<tr><td class="step">{a}</td><td>{b}</td><td><b>{c}</b></td></tr>' for a, b, c in RE_ROWS)
add('리버싱 결론', '06  리버스 엔지니어링 결과', 60, f"""
<h2 class="headline">결론: 기존 제어기를 쓰지 않고 DRV8244 SPI형으로 새로 개발</h2>
<table class="comparison select practice grow"><tr><th>대상</th><th>관측</th><th>처리</th></tr>{re_table}</table>
<div class="takeaway">남은 질문: 리프트 높이 조절 → 엔코더 또는 높이 센서 필요</div>
""",
    """리버스 엔지니어링의 결론이다. 전원 스위치는 플러스와 V 단자를 직접 잇는 단순한 스위치이고, 무선 수신 회로는 메인보드에 통합되어 있다. 모터는 릴레이로 켜고 끄며 방향만 바꾸고, 속도 조절은 없다. 여기에 컴퓨터 명령을 끼워 넣어도 켜고 끄는 것 이상은 할 수 없으므로, 기존 제어기를 쓰지 않고 DRV8244 SPI형 모터 드라이버로 제어기를 새로 만든다. 전원 스위치와 주행 모터, 리프트 모터는 그대로 쓴다. 남은 질문은 리프트 높이 조절이다. 포크를 원하는 높이에 세우려면 엔코더나 높이 센서가 필요하다.""",
    [('팀 리버스 엔지니어링 보고 (2026-09-30)', '전원 스위치 +·V 직결, RF 메인보드 통합, 릴레이 구동·PWM 없음, 속도 조절 기능 없음, 결론 DRV8244 SPI 신규 개발, 재활용: 전원 스위치·주행 모터·리프트 모터')],
    '출처: 팀 측정 보고')

# ----------------------------------------------------------------- 8 motor driver
DRV_DS = 'https://www.ti.com/lit/ds/symlink/drv8244-q1.pdf'
MT_DS = 'https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf'
# Continuous current and protection limit kept in separate columns: they are
# different ratings (DRV8244's continuous figure is TI's thermal simulation).
PICK = ' class="pick"'
DRIVER_ROWS = [
    ('DRV8244-Q1 (선정)', '4.5–35 V', 'DC 4.0 A *', 'OCP 10.5–40 A 선택', 'IPROPI 내장'),
    ('BTS7960 (IBT-2)', '—', '—', '전류 제한 43 A (typ)', 'IS 핀'),
    ('VNH5019 (Pololu)', '5.5–24 V', '12 A', '30 A 최대', '약 140 mV/A'),
    ('Cytron MD13S', '6–30 V', '13 A', '30 A (10 s)', '—'),
    ('DRV8871', '6.5–45 V', '—', '3.6 A 피크', '없음'),
]
driver_table = ''.join(
    f'<tr{PICK if i == 0 else ""}><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>'
    for i, (a, b, c, d, e) in enumerate(DRIVER_ROWS))
add('모터 드라이버 선정', '07  하드웨어 선정 · 모터 드라이버', 65, f"""
<h2 class="headline">모터 드라이버: DRV8244-Q1 SPI형 (DRV8244SQRYJRQ1) 선정</h2>
<div class="split grow" style="grid-template-columns:1.5fr 0.62fr">
<div class="stack" style="justify-content:center;gap:8px">
<table class="comparison select"><tr><th>후보</th><th>전원</th><th>연속 전류</th><th>보호·최대</th><th>전류 측정</th></tr>{driver_table}</table>
<p class="chart-cap">* TI 열 해석값: PWM 구동 · 주위 85 °C · 40 × 40 mm 4층 기판. 다른 후보는 제조사 연속 정격</p>
</div>
<div class="stack reasons">
<article><h3>전류 측정 내장</h3><p>IPROPI 핀 → MCU ADC로 모터 전류<br>막힘·포크 끝단 감지에 활용</p></article>
<article><h3>SPI 설정·진단</h3><p>전류 제한·과전류 임계·슬루율 설정<br>결함 종류를 레지스터로 확인</p></article>
<article class="warn"><h3>조건: 모터 전류 실측 후 확정</h3><p>연속 전류는 방열이 결정<br>→ 실측 전류에 맞춰 전류 제한·방열 기판 설계</p></article>
</div>
</div>
""",
    """모터 드라이버로는 TI의 DRV8244-Q1 SPI형을 골랐다. 왼쪽은 비교한 후보이다. 완성 보드인 VNH5019나 MD13S는 바로 쓸 수 있지만, 우리가 원하는 것은 컴퓨터가 모터 전류를 읽고 드라이버의 상태를 확인하는 것이다. DRV8244는 전류에 비례하는 신호를 IPROPI 핀으로 내보내므로, 션트 저항 없이 MCU의 ADC로 모터 전류를 읽을 수 있다. 이 값으로 바퀴가 막히거나 포크가 끝에 닿은 것을 알아낼 수 있다. SPI형은 전류 제한 크기와 과전류 임계값, 출력 전압이 바뀌는 속도를 설정할 수 있고, 어떤 결함이 났는지 레지스터로 읽을 수 있다. 전원은 4.5에서 35볼트까지라 12볼트 차체에 여유가 있다. 표에서 연속 전류와 보호 전류는 다른 값이다. DRV8244의 연속 전류는 TI가 85도 환경, 4층 기판, PWM 구동으로 계산한 열 해석값 4암페어로, 기판 방열에 따라 달라진다. 그래서 이 선정은 차체 모터의 전류를 잰 뒤 확정하며, 그 전류에 맞춰 전류 제한과 기판 방열을 설계한다.""",
    [(DRV_DS, 'DRV8244-Q1 데이터시트 SLVSG24C — 4.5–35 V, RON 47 mΩ(VQFN-HR), 출력 전류 Internally limited, OCP 21–40/15–31/10.5–24 A, ITRIP 7단계, fPWM ≤ 25 kHz, AIPROPI 4750 A/A, 표 7-1 DC 4.0 A (PWM, 85 °C, 40×40 mm 4층 2 oz), 주문 표 DRV8244SQRYJRQ1 = VQFN-HR(RYJ) 16'),
     ('https://www.infineon.com/dgdl/bts7960b-pb-final.pdf?fileId=db3a30431ed1d7b2011efe782ebd6b60', 'BTS7960 제품 요약 — 전류 제한 43 A typ'),
     ('https://www.pololu.com/product/1451', 'Pololu VNH5019 — 5.5–24 V, 12 A 연속, 30 A 최대, 약 140 mV/A'),
     ('https://courses.ideate.cmu.edu/16-375/f2026/text/electronics/cy-md13s-driver.html', 'Cytron MD13S — 6–30 V, 13 A 연속, 30 A 10 s'),
     ('https://www.ti.com/lit/ds/symlink/drv8871.pdf', 'DRV8871 — 6.5–45 V, 3.6 A 피크')],
    '출처: 제조사 데이터시트 · 제품 페이지')

# ----------------------------------------------------------------- 9 encoder
ENCODER_ROWS = [
    ('MT6701 (선정)', '14 bit', 'I2C · SSI · ABZ · UVW · 아날로그 · PWM', '절대 + 증분', '±1.5° (max)'),
    ('AS5600', '12 bit', 'I2C · 아날로그 · PWM', '절대', '±1° (시스템 INL)'),
    ('AS5048A/B', '14 bit', 'SPI 또는 I2C · PWM', '절대', '±1.2° (온도 포함)'),
    ('AS5047P', '14 bit', 'SPI · ABI · UVW · PWM', '절대 + 증분', '±1° (온도 포함)'),
    ('모터축 쿼드러처', '제품별', 'A/B(Z)', '증분', '원점 복귀 필요'),
]
encoder_table = ''.join(
    f'<tr{PICK if i == 0 else ""}><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>'
    for i, (a, b, c, d, e) in enumerate(ENCODER_ROWS))
add('엔코더 선정', '08  하드웨어 선정 · 엔코더', 60, f"""
<h2 class="headline">엔코더: MT6701 선정 — 절대각과 증분 출력을 한 칩에</h2>
<div class="split grow" style="grid-template-columns:1.5fr 0.62fr">
<table class="comparison select"><tr><th>후보</th><th>분해능</th><th>출력</th><th>방식</th><th>정확도</th></tr>{encoder_table}</table>
<div class="stack reasons">
<article><h3>조향각: 절대각</h3><p>전원을 켜자마자 각도 확인<br>원점 복귀 동작 불필요</p></article>
<article><h3>바퀴 속도: ABZ 증분</h3><p>MCU 타이머 엔코더 모드로 직접 계수<br>비접촉 자석식 · 1–2달러대</p></article>
<article class="note"><h3>4주차 피드백: 분해능</h3><p>"10 bit면 충분" → 14 bit로 충분<br>성능은 정확도(±1.5°)와 자석 정렬이 좌우</p></article>
</div>
</div>
<div class="takeaway">장착 조건: 자석 축 어긋남 ≤ 0.3 mm · 간격 0.5–2 mm → 브래킷 설계 필요</div>
""",
    """엔코더로는 자석식 각도 센서인 MT6701을 골랐다. 축 끝에 자석을 붙이고 그 위에 칩을 두면 접촉 없이 회전각을 잰다. 가장 큰 이유는 한 칩이 절대각과 증분 출력을 모두 낸다는 점이다. 조향축에 달면 전원을 켜자마자 현재 조향각을 알 수 있어 원점을 찾는 동작이 필요 없고, 바퀴 쪽에 달면 ABZ 출력을 MCU 타이머의 엔코더 모드로 바로 세어 속도를 잰다. 값도 1에서 2달러 수준이다. 비슷한 기능의 AS5047P가 정확도는 조금 낫지만, MT6701은 I2C와 아날로그 출력까지 있고 영점을 칩에 저장할 수 있다. 4주차에 엔코더 분해능은 10비트면 충분하다는 피드백을 받았다. MT6701은 14비트로 충분하고, 실제 성능은 분해능보다 최대 1.5도의 정확도와 자석을 얼마나 바르게 붙이는지가 좌우한다. 그래서 자석과 칩의 축 어긋남 0.3밀리미터 이하, 간격 0.5에서 2밀리미터를 지키는 브래킷을 설계한다. 어느 축에 몇 개를 달지는 조종기 신호 분석과 모터 구조를 확인한 뒤 정한다.""",
    [(MT_DS, 'MT6701 데이터시트 Rev.1.5 — 14 bit, I2C·SSI·ABZ(≤1024 PPR)·UVW·아날로그·PWM, INL ±1.5° max, 자석 Ø6×2.5 mm·간격 0.5–2.0 mm·축 어긋남 ≤0.3 mm, 영점 EEPROM'),
     ('https://www.lcsc.com/product-detail/Angle-Linear-Position-Sensors_Magn-Tek-MT6701CT-STD_C2856764.html', 'LCSC 가격 $1.43–2.04'),
     ('https://www1.futureelectronics.com/doc/ams/AS5047P-ATSM.pdf', 'AS5047P — 14 bit, SPI·ABI·UVW·PWM, 온도 포함 ±1°'),
     ('https://media.digikey.com/pdf/Data%20Sheets/Austriamicrosystems%20PDFs/AS5048A,B.pdf', 'AS5048A/B — 14 bit, 온도 포함 ±1.2°'),
     ('https://files.seeedstudio.com/wiki/Grove-12-bit-Magnetic-Rotary-Position-Sensor-AS5600/res/Magnetic%20Rotary%20Position%20Sensor%20AS5600%20Datasheet.pdf', 'AS5600 — 12 bit, 시스템 INL ±1°'),
     (FEEDBACK, '§4 엔코더 분해능 10 bit면 충분')],
    '출처: 제조사 데이터시트 · 판매처 가격')

# ----------------------------------------------------------------- 10 standard practice vs our mission
LAW_SAFETY = 'https://www.law.go.kr/법령/산업안전보건기준에관한규칙'
KOSHA_EDU = 'https://oshri.kosha.or.kr/kosha/data/business/serviceSafetyBusinessData.do?mode=download&articleNo=399205&attachNo=222048'
TRANSPORT_CFG = 'config/isaac_transport.yaml'
TRANSPORT_RUN = 'sim/isaac/run_transport.py'
OK_, PART, DIFF = 'ok', 'part', 'diff'
PRACTICE_ROWS = [
    ('접근', '화물 앞에서 감속 · 일단 정지 → 정면에서 천천히', '0.6 m/s 접근 → 삽입 시작점 정렬·정지 → 0.055 m/s 삽입', OK_, '—'),
    ('삽입', '백레스트에 닿을 때까지 끝까지', '360 mm = min(깊이 × 0.6, 차체 한계) · EPAL 6은 60 %, 축소 T11은 차체 한계', DIFF, '삽입 깊이 기준 재검토'),
    ('들기', '5–10 cm 들어 당기고 내린 뒤 재삽입 → 들기', '한 번에 20 cm 들기', DIFF, '재삽입 단계 필요성 검토'),
    ('운반 자세', '포크 바닥 위 약 15–20 cm · 마스트 후경', '포크 20 cm 유지 · 틸트 없음 (잠정 모델)', PART, '틸트 유무는 차체 확인'),
    ('속도', '구내 10 km/h 이하 · 모퉁이·사람 근처 감속·경고음', '접근 0.6 · 운반 0.3 m/s · 감속 구역·경고음 없음', PART, '감속 구역 · 경고음 추가'),
    ('후진', '충돌 위험 시 후진경보기·경광등 또는 후방감지기', '후방 확인 수단 없음', DIFF, '후방 확인 수단 추가'),
    ('작업 종료', '운전위치 이탈 시 포크 최저 위치', '하역 후 포크를 바닥까지 → 복귀', OK_, '—'),
]
MARK = {OK_: '<span class="mk ok">일치</span>', PART: '<span class="mk part">부분</span>', DIFF: '<span class="mk diff">차이</span>'}
practice_table = ''.join(
    f'<tr><td class="step">{st}</td><td>{std}</td><td>{ours}</td><td>{MARK[m]}</td><td><b>{act}</b></td></tr>'
    for st, std, ours, m, act in PRACTICE_ROWS)
add('표준 운용 절차 대조', '09  표준 운용 절차 대조', 80, f"""
<h2 class="headline">표준 운용 절차와 우리 임무 절차 대조: 7단계 중 5단계 보완 필요</h2>
<table class="comparison select practice grow"><tr><th>단계</th><th>표준 운용 절차 (KOSHA · 산업안전보건기준)</th><th>우리 임무 절차 (현재 시뮬레이션)</th><th>대조</th><th>조치</th></tr>{practice_table}</table>
<p class="chart-cap">표준 수치는 사람이 타는 실제 지게차 기준 · 우리 차체에 적용할 비율은 실측 후 결정</p>
""",
    """4주차에 사람이 운전하는 방식과 비슷하게 움직여야 보는 사람이 덜 불안하다는 피드백을 받았다. 지금까지 우리가 정한 임무 절차는 팀이 임의로 정한 것이어서, 한국산업안전보건공단 교육자료와 산업안전보건기준에 있는 표준 운용 절차를 찾아 단계별로 대조하였다. 팔레트 앞에서 멈춰 정렬한 뒤 천천히 넣는 접근과, 작업 종료 때 포크를 내리는 것은 표준과 같다. 그리고 운반 중 포크 높이와 속도 상한은 맞지만 마스트 후경과 감속 구역이 빠져 있다. 나머지 세 단계는 다르다. 표준은 백레스트에 닿을 때까지 끝까지 넣지만, 우리는 팔레트 깊이의 60퍼센트와 차체 한계 가운데 작은 값인 360밀리미터만 넣는다. 표준은 조금 들어 당겼다가 내리고 다시 끝까지 넣은 뒤 드는데, 우리는 한 번에 20센티미터를 든다. 또 표준은 사람과 부딪힐 위험이 있으면 후진경보기와 경광등, 또는 후방감지기로 뒤를 확인하도록 하는데, 우리 임무에는 후방 확인 수단이 없다. 오른쪽 열처럼 삽입 깊이 기준, 재삽입 단계, 마스트 후경, 감속 구역과 경고음, 후방 확인 수단을 임무 절차에 반영할지 검토한다. 표준 수치는 실제 지게차 기준이므로 우리 차체에 줄여 적용할 비율은 실측 후 정한다.""",
    [(KOSHA_EDU, 'KOSHA 지게차 교육자료 — 감속·일단 정지, 정면 삽입, 5–10 cm 들기, 10–20 cm 당김 후 내림, 재삽입, 운반 시 포크 약 15–20 cm·마스트 후경, 구내 10 km/h 이하, 모퉁이·사람 근처 감속·경고음'),
     (LAW_SAFETY, '산업안전보건기준에 관한 규칙 제98·99·179조 — 제한속도, 운전위치 이탈 시 포크 최저, 제179조 제2항 충돌 위험 시 후진경보기·경광등 또는 후방감지기 (대안 관계)'),
     (TRANSPORT_CFG, '우리 임무: 접근 0.60 · 삽입 0.055 · 운반 0.30 m/s, 들기 목표 0.20 m (시뮬레이터 설정)'),
     (TRANSPORT_RUN, '우리 임무 단계: 관측 → 접근 → 삽입 → 들기 → 인출 → 운반 → 내리기 → 빼기 → 복귀. 접근 추적기는 속도 0·측정 속도 0.012 m/s 이하에서 도착 판정 후 삽입으로 전환. 틸트 관절 없음(잠정 URDF)'),
     ('forklift/CLAUDE.md', '삽입 깊이 규칙 min(깊이 × 0.6, 406 − 46 mm) = 360 mm'),
     (FEEDBACK, '§3 사람의 운전 방식과 비슷하게')],
    '출처: KOSHA 교육자료 · 법령 · 우리 시뮬레이션 설정')

# ----------------------------------------------------------------- 12 meeting questions
add('리보틱스 미팅 질문', '10  리보틱스 중간 미팅 질문', 40, """
<h2 class="headline">리보틱스 중간 미팅에서 확인할 사항</h2>
<table class="comparison select meeting grow"><tr><th>구분</th><th>항목</th></tr><tr><td rowspan="4" class="grp">확인할 것</td><td class="item">최종 시연 장소 · 바닥 (실내·실외)</td></tr><tr><td class="item">평가 기준 (성공률 · 시간 · 정밀도)</td></tr><tr><td class="item">시험 팔레트 (EPAL 6 · 축소 T11) · 적재 하중</td></tr><tr><td class="item">다우테크놀로지 사례 (작업 공간 · 험지)</td></tr><tr><td rowspan="3" class="grp">요청할 것</td><td class="item">주행·승강 모터 사양서 (있다면)</td></tr><tr><td class="item">주행·조향·승강 모터 정격 (전압 · 전류)</td></tr><tr><td class="item">실제 지게차 운용 영상 · 데이터</td></tr><tr><td rowspan="5" class="grp">함께 정할 것</td><td class="item">기존 제어기 교체 (DRV8244 신규 제어기) 승인</td></tr><tr><td class="item">리프트 높이 조절 요구 (범위 · 정밀도)</td></tr><tr><td class="item">시험 공간 · 허용 속도</td></tr><tr><td class="item">안전 정지 요구 (비상정지 · 기울기 · 과적)</td></tr><tr><td class="item">동봉 팔레트 활용</td></tr></table>
""",
    """마지막으로 리보틱스와의 중간 미팅에서 확인할 사항이다. 먼저 최종 시연 장소와 바닥 상태, 평가 기준이 성공률과 시간, 정밀도 가운데 무엇인지, 시험 팔레트와 적재 하중을 확인하고, 추천받은 다우테크놀로지 사례의 작업 공간과 험지 여부를 묻는다. 요청할 자료는 모터 사양서와 정격 전압·전류, 실제 지게차의 운용 영상과 데이터이다. 특히 모터 전류는 오늘 본 모터 드라이버의 전류 제한과 방열 설계에 필요하다. 함께 정할 것은 기존 제어기를 DRV8244 기반 새 제어기로 바꾸는 것에 대한 승인, 리프트 높이를 어느 범위와 정밀도로 조절해야 하는지, 시험 공간과 허용 속도, 비상정지와 기울기·과적 감지 같은 안전 정지 요구, 그리고 동봉 팔레트의 활용이다.""",
    [(FEEDBACK, '§1 중간 미팅 준비 — 궁금한 것 · 제공 요청 · 결정 요청, 팀 메모 기울기·과적 정지'),
     (DRV_DS, '모터 전류 → 전류 제한·방열 설계 (7쪽)')],
    '출처: 4주차 피드백 · 이번 주 하드웨어 작업')

TITLE = '5주차 자율 지게차 개발'
TOTAL = 610
N_SLIDES = 11


def build():
    assert len(slides) == N_SLIDES, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{N_SLIDES}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-29. 하드웨어 발표이다. 실측·파형 쪽은 팀 측정 결과이고, 부품 선정 쪽의 사양은 제조사 데이터시트 값이다.', '']
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
