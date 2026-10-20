"""Build the week 8 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 8 (class) is half the operator console and half the demo scenarios
Riibotics sent after the midterm meeting (user, 2026-10-20 restructure): what
the console does, how it connects, the screen layout, ordering a mission and
driving by hand; then the five scenarios, their scale to our truck, what each
needs, the implementation order and the questions for Riibotics. The console
half shows function and practical use rather than the safety design. The user
approved putting the scenario PDF's figures in the public deck (2026-10-20).

Figures are crops of console screenshots made by prepare_figures.py. Those
taken on the Isaac live runner are marked as such in SOURCES.md; the ones
from the fake vehicle are listed in SOURCES.md; the "임시 화면" tag (temp=True)
was dropped at publication (user, 2026-10-20 "배포").
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
slides = []

BLUE = '#2f74c0'
GRID, SCAN, PATH, REV, TELE = '#4a72e0', '#e05a4f', '#7d848c', '#f2a33a', '#a78bfa'   # the console's own map colours

ROBOT = 'lightminn/forklift main 4b65404'
DESIGN = f'{ROBOT} docs/design/2026-10-13-operator-console.md'
README = f'{ROBOT} console/README.md'
PR61 = 'lightminn/forklift PR #61 (상시 운용 콘솔, 2026-10-19 머지)'
MOCK_REC = '콘솔 조작 녹화 — 가짜 차량 console.mock_vehicle, 헤드리스 Chromium 1600 × 900 (폰 400 × 860), 2026-10-21; 흰 점은 녹화에 덧그린 클릭 위치'
SCEN_PDF = 'Riibotics 「서울시립대 과제 시연 시나리오」 PDF (2026-10-19 메일 재발송본, 환경 수치 포함)'
SCEN_MAIL = 'Riibotics 정진용 CTO 메일 (2026-10-19, 중간 발표 자료 회신)'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def img(src, alt, cap=None, cls='shot', temp=False):
    t = '<span class="tmp8">임시 화면</span>' if temp else ''
    c = f'<figcaption>{cap or ""}{t}</figcaption>' if (cap or temp) else ''
    return (f'<figure class="{cls}"><img class="media" src="assets/{src}" '
            f'alt="{escape(alt, quote=True)}">{c}</figure>')


def video(src, alt, cap=None):
    """A looping muted clip in a figure, its poster frame when one exists (week 6's helper)."""
    poster = src.rsplit('.', 1)[0] + '_poster.jpg'
    pa = f' poster="assets/{poster}"' if (ROOT / 'assets' / poster).exists() else ''
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="shot"><video class="media" src="assets/{src}"{pa} autoplay loop muted playsinline '
            f'aria-label="{escape(alt, quote=True)}"></video>{c}</figure>')


def table(head, rows, cls='comparison h7'):
    h = ''.join(f'<th>{x}</th>' for x in head)
    body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'


def lgd(*items):
    """Legend in the console's colours: (kind, colour, text), kind box / line / dot / dash."""
    out = []
    for kind, colour, text in items:
        if kind == 'line':
            sw = f'<span class="sw ln" style="background:{colour}"></span>'
        elif kind == 'dash':
            sw = f'<span class="sw dash" style="border-color:{colour}"></span>'
        elif kind == 'dot':
            sw = f'<span class="sw dot" style="background:{colour}"></span>'
        elif kind == 'ring':
            sw = f'<span class="sw ring" style="border-color:{colour}"></span>'
        else:
            sw = f'<span class="sw" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="lgd7">{"".join(out)}</div>'


# ----------------------------------------------------------------- figures
def structure_diagram():
    """Browser -> gateway -> robot stack -> real truck (Jetson, STM32 board, chassis) or Isaac, with photos:
    the console as it looks on a laptop and a phone (our recordings), the boards (Wikimedia Commons, SOURCES.md),
    our chassis photo and an Isaac render."""
    W, H = 1400, 430
    a = lambda c: f'marker-end="url(#{c})"'

    def pic(src, x, y, w, h, r=8, stroke='#c3cad3'):
        cid = f'c8_{src.split(".")[0]}_{x}_{y}'
        return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>'
                f'<image href="assets/{src}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{stroke}" stroke-width="1.5"/>')

    def label(x, y, t, sub=None, anchor='middle', size=22):
        out = f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="700" fill="#1b1f24">{t}</text>'
        if sub:
            out += f'<text x="{x}" y="{y + 26}" text-anchor="{anchor}" font-size="17" fill="#44505c">{sub}</text>'
        return out

    def box(x, y, w, h, t, sub):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#eef4fb" stroke="{BLUE}" stroke-width="2.5"/>'
                + label(x + w / 2, y + h / 2 - 4, t, sub))

    parts = [f'<defs><marker id="ah8" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
             f'<marker id="ah8g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="#9aa3ad"/></marker></defs>']
    # the browsers: the console on a laptop and a phone (frames of our recordings)
    parts.append('<rect x="10" y="100" width="240" height="150" rx="9" fill="#1b1f24"/>'
                 + pic('v03_layout_poster.jpg', 18, 108, 224, 126, 3, '#1b1f24')
                 + '<polygon points="0,252 260,252 246,268 14,268" fill="#c3cad3"/>'
                 '<rect x="186" y="150" width="80" height="168" rx="13" fill="#1b1f24"/>'
                 + pic('v03_phone_poster.jpg', 192, 160, 68, 146, 4, '#1b1f24'))
    parts.append(label(133, 356, '폰 · 노트북 브라우저', '설치 없음'))
    # Wi-Fi, then the gateway and the robot stack
    parts.append(f'<line x1="276" y1="215" x2="346" y2="215" stroke="{BLUE}" stroke-width="4" {a("ah8")}/>'
                 + ''.join(f'<path d="M{311 - r},{182 - 0.0} A{r},{r} 0 0 1 {311 + r},182" fill="none" stroke="{BLUE}" stroke-width="3.5" '
                           f'stroke-linecap="round" transform="rotate(0 311 182)"/>' for r in (8, 16, 24))
                 + f'<circle cx="311" cy="186" r="3.5" fill="{BLUE}"/>'
                 f'<text x="311" y="245" text-anchor="middle" font-size="17" fill="{BLUE}">Wi-Fi</text>')
    parts.append(box(352, 160, 168, 110, '게이트웨이', '작업 단위 API'))
    parts.append(f'<line x1="520" y1="215" x2="572" y2="215" stroke="{BLUE}" stroke-width="4" {a("ah8")}/>'
                 f'<text x="546" y="201" text-anchor="middle" font-size="17" fill="{BLUE}">ROS 2</text>')
    parts.append(box(576, 150, 206, 130, 'ROS 2 로봇 스택', '미션, 위치 추정, 경로'))
    # the drive side: the real truck (later) and Isaac Sim
    parts.append('<rect x="832" y="4" width="564" height="422" rx="12" fill="none" stroke="#c3cad3" stroke-width="2" stroke-dasharray="8 6"/>'
                 '<text x="1388" y="416" text-anchor="end" font-size="16" fill="#5d6670">구동부만 바뀜</text>')
    parts.append(f'<polyline points="782,195 810,195 810,110 850,110" fill="none" stroke="#9aa3ad" stroke-width="4" stroke-dasharray="10 7" {a("ah8g")}/>'
                 f'<polyline points="782,235 810,235 810,322 850,322" fill="none" stroke="{BLUE}" stroke-width="4" {a("ah8")}/>')
    parts.append(pic('d02_jetson.jpg', 856, 48, 170, 122)
                 + f'<line x1="1030" y1="110" x2="1060" y2="110" stroke="#9aa3ad" stroke-width="3.5" {a("ah8g")}/>'
                 + pic('d02_stm32.jpg', 1066, 40, 120, 140)
                 + f'<line x1="1190" y1="110" x2="1220" y2="110" stroke="#9aa3ad" stroke-width="3.5" {a("ah8g")}/>'
                 + pic('d02_truck.jpg', 1226, 16, 152, 185))
    parts.append(label(941, 200, 'Jetson', size=19) + label(1126, 206, 'STM32 구동 보드', size=19)
                 + label(1302, 226, '실차 (추후 연결)', size=19))
    parts.append(pic('d02_isaac.jpg', 856, 246, 232, 157)
                 + label(1110, 318, 'Isaac Sim', 'ws1 실시간 실행기', anchor='start', size=24))
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="폰과 노트북 브라우저가 Wi-Fi로 게이트웨이에, '
            f'게이트웨이가 ROS 2로 로봇 스택에 붙고, 로봇 스택 아래 구동부가 실차(Jetson, STM32 구동 보드, 차체, 추후 연결) 또는 Isaac Sim">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


def layout_figure():
    """Full console screenshot with numbered region markers (positions in % of the 1600 x 900 shot)."""
    marks = [(1, 30.5, 3.5), (2, 50.0, 30.0), (3, 34.5, 70.0), (4, 88.5, 9.0), (5, 6.5, 13.5)]
    m = ''.join(f'<span class="mk8" style="left:{x}%;top:{y}%">{n}</span>' for n, x, y in marks)
    return ('<figure class="shot lay8fig"><div class="frame8"><video class="media" src="assets/v03_layout.mp4" '
            'poster="assets/v03_layout_poster.jpg" autoplay loop muted playsinline '
            f'aria-label="임무 중인 운용 콘솔 넓은 화면. 위 상태 줄, 왼쪽 메뉴, 가운데 지도에서 지게차가 움직이고 왼쪽 아래 전방 카메라 창, 오른쪽 차량 상세"></video>{m}</div></figure>')


STAGES = ['관찰', '접근', '삽입', '들기', '빼기', '운반', '내리기', '후퇴', '복귀']


# ----------------------------------------------------------------- cover
add('개발 진행 보고', '8주차\n자율 지게차 개발', 20, '',
    """안녕하십니까. 8주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 주에는 두 가지를 말씀드리겠습니다. 앞부분은 지게차를 무선으로 다루는 운용 콘솔입니다. 콘솔이 하는 일과 연결 구조, 화면 구성, 미션 지시, 직접 운전을 보이겠습니다. 뒷부분은 중간 미팅 뒤 리보틱스에서 받은 시연 시나리오입니다. 시나리오를 우리 지게차 크기로 환산해 시나리오별로 실현 가능성을 따져 보고, 구현 순서와 리보틱스에 확인할 점으로 마치겠습니다. (전환)""",
    [(ROBOT, '운용 콘솔 console/ · 설계 문서 · PR #61–#65'), (SCEN_PDF, '시연 시나리오 다섯 가지')], '진행 보고')

# ----------------------------------------------------------------- 1
add('콘솔이 하는 일', '01  운용 콘솔이 하는 일', 50, f"""
<h2 class="headline">지게차 한 대를 브라우저 화면으로 보고, 지시하고, 직접 운전</h2>
<div class="trio8 grow">
{video('v01_watch.mp4', '임무 중인 콘솔 지도. 지게차가 팔레트로 가서 집고 하역 위치로 옮기며 전방 카메라 창이 함께 바뀜', '상태 보기 (지도, LiDAR, 카메라)')}
{video('v01_order.mp4', '작업 지정 창에서 작업 종류, 팔레트와 하역 위치를 고르고 작업을 시작함', '작업 지시 (팔레트, 하역 위치)')}
{video('v01_drive.mp4', '수동 조종 탭에서 누르고 있기 버튼이 켜지고 속도와 곡률 명령 막대가 움직임', '직접 운전 (조이스틱, 게임패드, 키보드)')}
</div>
""",
    """이번 주에 만든 운용 콘솔입니다. 6주차 발표에서 무선 통신을 고려하지 않았다는 피드백을 받았습니다. 지금까지는 연구실 워크스테이션 터미널에서 명령을 넣고, 결과 영상은 미션이 끝난 뒤에 받아 봤습니다. 실제 현장에서는 지게차 옆에서 폰이나 노트북으로 바로 다뤄야 하므로 브라우저로 쓰는 콘솔을 만들었습니다. 콘솔이 하는 일은 세 가지입니다. 왼쪽처럼 지도와 LiDAR, 전방 카메라로 지게차 상태를 보고, 가운데처럼 옮길 팔레트와 내려놓을 위치를 골라 작업을 지시하고, 오른쪽처럼 조이스틱이나 게임패드로 직접 운전합니다. (전환)""",
    [('lightminn/forklift docs/references/week6_feedback.md 5절', '무선 통신 미고려 — 콘솔 설계의 계기'),
     (DESIGN, '1절 목적: 상태 감시, 작업 지시, 수동 조종 (육안 · 영상)'),
     (MOCK_REC, '왼쪽 임무 진행(6배속), 가운데 작업 지정, 오른쪽 수동 조종(키보드 Space · W · A · D)')],
    '영상: 콘솔 조작 녹화 (가짜 차량)')

# ----------------------------------------------------------------- 2
add('시스템 구조', '02  콘솔 연결 구조', 55, f"""
<h2 class="headline">브라우저가 지게차의 게이트웨이에 붙고, 실차와 Isaac은 같은 로봇 스택을 공유</h2>
<div class="sys8 sys8p grow">{structure_diagram()}</div>
{table(['입력', '무선 연결'], [('터치, 키보드, 게임패드', 'Jetson이 Wi-Fi AP (지게차와 1:1)')], 'comparison h7 nwall sys8t')}
""",
    """연결 구조입니다. 폰이나 노트북의 브라우저가 Wi-Fi로 지게차에 있는 게이트웨이에 접속합니다. 앱을 따로 설치하지 않고, 입력은 터치, 키보드, 게임패드를 모두 받습니다. 게이트웨이는 팔레트 운반 같은 작업 단위로 요청을 받아 ROS 2 로봇 스택에 넘기고, 로봇 스택이 미션 실행, 위치 추정, 경로 계획을 맡습니다. 실차와 Isaac 시뮬레이션은 이 로봇 스택을 같이 쓰고 맨 아래 구동부만 바뀝니다. 그래서 지금 Isaac에서 쓰는 화면을 실차에서도 그대로 쓸 수 있습니다. 실차에서는 Jetson이 직접 Wi-Fi 공유기 역할을 해서 콘솔 기기와 일대일로 연결할 계획이고, 실차 연결은 아직 하지 않았습니다. 브라우저를 고른 이유는 폰에 ROS를 설치할 수 없기 때문이고, 게이트웨이가 ROS 토픽이 아니라 작업 단위 API를 주므로 나중에 여러 대를 관제하는 서버가 생겨도 같은 API를 그대로 중계하면 됩니다. (전환)""",
    [(DESIGN, '2절 결정: 로봇 쪽 전용 게이트웨이 + 웹 앱(A안), 웹 클라이언트(폰에 ROS 설치 불가, Gamepad API), 1단계 망 Jetson AP 1:1, 실차와 Isaac 이 같은 ROS 2 스택; 3절 구조도'),
     (README, 'web/ 빌드 없는 브라우저 콘솔, gateway/ 관찰 전용 게이트웨이(ROS 2 컨테이너)'),
     (PR61, 'Isaac 실시간 실행기와 콘솔 연결; 실차 연결(설계 6절 C4)은 미착수')],
    '그림: 설계 문서 3절 구조도를 사진과 함께 다시 그림 (안전 계층은 생략, 보드 사진은 Wikimedia Commons)')

# ----------------------------------------------------------------- 3
add('화면 구성', '03  화면 구성', 55, f"""
<h2 class="headline">가운데 지도와 그 위 카메라 창, 오른쪽 차량 상세로 나눈 차량 관제 화면 형식</h2>
<div class="lay8 grow">
{layout_figure()}
{table(['', '영역'], [
    ('①', '연결 대상, 운행 모드, 조종 권한'),
    ('②', '지도 (격자, LiDAR, 경로)'),
    ('③', '전방 카메라'),
    ('④', '차량 상세와 수동 조종 탭'),
    ('⑤', '모니터링, 이벤트 기록, 통신')], 'comparison h7 nwall mk8t')}
<figure class="shot phone8"><video class="media" src="assets/v03_phone.mp4" poster="assets/v03_phone_poster.jpg" autoplay loop muted playsinline aria-label="폰 폭 화면을 아래로 넘기면 전방 카메라, 수동 조종, 지도, 차량 상세가 차례로 나오고 STOP은 아래에 고정"></video><figcaption>폰 화면</figcaption></figure>
</div>
""",
    """화면 구성입니다. 물류 현장의 차량 관제 화면, 흔히 FMS라고 부르는 형식을 따랐습니다. 맨 위 1번 줄에는 연결 대상과 운행 모드, 조종 권한이 있습니다. 가운데 2번은 지도로, 점유 격자와 LiDAR 점, 계획 경로를 그립니다. 그 위에 3번 전방 카메라 창이 떠 있고, 오른쪽 4번에는 차량 상세와 수동 조종 탭이 있습니다. 왼쪽 5번 메뉴로 모니터링, 이벤트 기록, 통신 화면을 오갑니다. 오른쪽은 같은 화면을 폰 폭으로 연 모습입니다. 좁은 화면에서는 카메라, 수동 조종, 지도 순서로 세로로 쌓이고 정지 버튼은 아래에 고정됩니다. (전환)""",
    [(README, 'web/ 화면은 FMS 형식: 왼쪽 메뉴(모니터링 · 이벤트 기록 · 통신), 가운데 지도와 그 위 전방 카메라 창, 오른쪽 차량 상세와 수동 조종 탭'),
     (DESIGN, '8절: 폰에서는 카메라 → 수동 조종 → 지도 → 작업 지시 순서로 세로, STOP 하단 고정'),
     (MOCK_REC, '넓은 화면 임무 진행(6배속), 폰 화면 400 × 860 을 아래로 넘김')],
    '영상: 콘솔 조작 녹화 (가짜 차량, 번호는 덱에서 덧붙임)')

# ----------------------------------------------------------------- 4
add('작업 지정과 진행', '04  작업 지정과 진행', 55, f"""
<h2 class="headline">작업 종류, 대상, 확인 세 단계로 지시하면 미션 진행을 단계별로 표시</h2>
<div class="steps8 two8 grow">
{video('v01_order.mp4', '작업 지정 창. 작업 종류, 대상 설정, 확인 세 단계를 거쳐 작업 시작', '작업 종류 → 대상 설정 → 확인')}
{video('v04_progress.mp4', '임무 패널. 실행 중 단계와 진행률이 접근, 삽입, 운반으로 바뀌고 현재 목적지가 팔레트에서 하역 위치로 바뀜', '진행 표시')}
</div>
<div class="phase-flow stages8">{'<span class="arrow">→</span>'.join(f'<span>{s}</span>' for s in STAGES)}</div>
""",
    """미션을 지시하는 방법입니다. 작업 지정 창은 세 단계입니다. 먼저 작업 종류를 고릅니다. 지금은 팔레트 운반 하나이고, 차량이 지원한다고 알린 작업만 보입니다. 다음으로 옮길 팔레트와 내려놓을 하역 위치를 고르고, 마지막으로 확인하고 작업을 시작합니다. 지도에서 팔레트를 직접 눌러도 그 팔레트가 골라진 채로 대상 설정이 바로 열립니다. 작업이 시작되면 아래 띠처럼 관찰, 접근, 삽입, 들기, 빼기, 운반, 내리기, 후퇴, 복귀의 아홉 단계 중 지금 어디까지 왔는지 화면에 표시되고, 끝나면 결과 기록에 남습니다. (전환)""",
    [(README, "작업은 '작업 지정' 창에서 작업 종류 → 대상 설정 → 확인 세 단계, capabilities 에 밝힌 작업만, console/1 은 '팔레트 운반' 하나, 지도에서 팔레트를 누르면 2단계가 열림"),
     (PR61, '결과 기록부(D13), 미션 진행 단계 표시'),
     ('콘솔 화면 작업 진행 막대', '관찰 · 접근 · 삽입 · 들기 · 빼기 · 운반 · 내리기 · 후퇴 · 복귀'),
     (MOCK_REC, '왼쪽 작업 지정 창, 오른쪽 임무 패널(6배속)')],
    '영상: 콘솔 조작 녹화 (가짜 차량)')

# ----------------------------------------------------------------- 5
add('직접 운전', '05  직접 운전', 50, f"""
<h2 class="headline">조이스틱이나 게임패드로 몰고, 갈 경로를 지도와 카메라 바닥에 미리 표시</h2>
<div class="hw7 wide grow">
{video('v05_teleop.mp4', '수동 조종 중인 콘솔. 키보드로 전진하며 좌우로 꺾고 후진한 뒤 포크를 올림. 지도와 카메라 바닥에 보라색 점선 예상 궤적이 따라 움직임')}
{table(['구분', '방식'], [
    ('입력', '화면 조이스틱, 게임패드, 키보드'),
    ('미리 보기', '지도와 카메라 바닥에 예상 경로'),
    ('포크', '올리기, 내리기 버튼'),
    ('조종 방식', '눈으로 보며, 영상만 보며')], 'comparison h7 nwall t8')}
</div>
{lgd(('dash', TELE, '조종 예상 궤적'))}
""",
    """직접 운전입니다. 수동 조종 탭에서 화면 조이스틱이나 게임패드, 키보드로 지게차를 몹니다. 조이스틱을 움직이면 지금 명령대로 가면 지나갈 경로를 지도에 보라색 점선으로 그리고, 같은 경로를 카메라 영상의 바닥에도 겹쳐 보여 줍니다. 그래서 영상만 보고 운전할 때도 차가 어디로 갈지 미리 알 수 있습니다. 포크는 올리기와 내리기 버튼으로 움직입니다. 자동 주행 중에도 일시정지하고 수동 조종으로 바꿔 차를 옮길 수 있습니다. (전환)""",
    [(DESIGN, '1절 수동 조종(육안 · 영상), 5.3 영상 조종, 5.5 입력 장치(터치 · 키보드 · 게임패드), 8절 지도 · 카메라의 수동 조종 예상 궤적'),
     ('콘솔 화면 수동 조종 탭', '키보드 Space 누르고 있기 · WS 속도 · AD 조향 · RF 포크, ▲ 올리기 / ▼ 내리기'),
     (MOCK_REC, '수동 조종 시작 → 조종 준비 → Space 누른 채 W 전진, A · D 조향, S 후진 → ▲ 올리기'),
     ('미확인 (2026-10-20)', 'Isaac 실행기의 수동 포크 승강 구동 — 10-17 미구동, 10-19 출력 방식 합의; 일시정지 뒤 수동 조종 전환은 녹화 때 확인')],
    '영상: 콘솔 조작 녹화 (가짜 차량)')

# ----------------------------------------------------------------- 6
SCEN = [('s03_aisle.mp4', '① 좁은 통로 rack에서 꺼내 다른 칸에 적치', '위에서 본 좁은 통로. 지게차가 rack 줄의 한 칸에서 팔레트를 꺼내 아래 구역 사이 간격에서 방향을 바꾼 뒤 같은 줄 다른 빈칸에 넣고 돌아옴'),
        ('s04_conveyor.mp4', '② 높이 약 70 cm 컨베이어 사이 이송', '위에서 본 컨베이어 두 대. 지게차가 왼쪽 컨베이어 끝의 팔레트를 집어 오른쪽 컨베이어 끝에 내려놓음 (높이는 그리지 않음)'),
        ('s05_line.mp4', '③ 일자로 놓인 팔레트 모두 이송', '위에서 본 일자 배치. 왼쪽 줄의 팔레트 세 개를 앞에서부터 하나씩 집어 오른쪽 줄 안쪽 칸부터 내려놓음'),
        ('s06_random.mp4', '④ 랜덤 배치(10° 이내) 차례로 이송', '위에서 본 랜덤 배치. 조금씩 틀어진 팔레트 세 개를 차례로 집어 하역 구역에 한 줄로 내려놓음'),
        ('s07_trailer.mp4', '⑤ 좌우가 막힌 트레일러에서 꺼내기, 넣기', '위에서 본 트레일러. 입구로 곧게 들어가 앞줄 팔레트를 꺼내 옆 하역 자리에 내려놓고 돌아옴')]
add('시연 시나리오', '06  리보틱스 시연 시나리오', 55, f"""
<h2 class="headline">리보틱스가 실제 현장 작업에 맞춰 보낸 시연 시나리오 다섯 가지</h2>
<div class="scen8 grow">
{''.join(video(src, alt, cap) for src, cap, alt in SCEN)}
</div>
<div class="takeaway">남은 기간에 모두 하기는 어려우니 구현할 수 있는 범위에서 골라 진행하자는 제안을 함께 받았습니다</div>
""",
    """여기부터는 중간 미팅 뒤에 리보틱스에서 받은 시연 시나리오와 그 분석입니다. 리보틱스가 실제 현장에서 하는 작업 방식에 맞춰 다섯 가지를 보내 주었습니다. 화면의 영상은 각 시나리오를 우리 지게차 크기로 줄인 장면에서 경로 계획기로 움직여 본 것입니다. 첫째는 좁은 통로의 rack에서 팔레트를 꺼내 다른 칸에 넣는 것, 둘째는 높이 약 70센티미터 컨베이어 사이에서 옮기는 것, 셋째는 일자로 놓인 팔레트를 모두 옮기는 것, 넷째는 넓은 공간에 10도 이내로 틀어져 놓인 팔레트를 차례로 옮기는 것, 다섯째는 좌우가 벽으로 막힌 트레일러에서 꺼내고 넣는 것입니다. 여기에는 리보틱스가 내부적으로 개발하려는 동작도 섞여 있어서, 남은 기간에 구현할 수 있는 범위에서 골라 진행하자는 제안을 받았습니다. (전환)""",
    [(SCEN_PDF, '3–7쪽 그림과 설명 (좁은 통로 3.8 m · 구역 간격 3.4 m · 컨베이어 약 70 cm · 틀어짐 10° 이내 · 트레일러 2.6 m); 영상 장면은 이 그림의 배치를 우리 축척으로 옮긴 것'),
     ('lightminn/forklift feat/riibotics-scenarios tools/riibotics_cpu_video.py', 'CPU 경로 계획 애니메이션: Isaac 임무 설정(곡률 0.29, 여유 0.10, 정렬 2.1 m, 하역 1.5 m, D7)으로 관측 구간과 운반 · 복귀를 계획하고 단계 속도 사다리꼴로 그림(시뮬레이션 아님, 8배속); ③ ④ 는 세 팔레트를 차례로, ② 는 컨베이어 높이를 넣지 않은 바닥 움직임만'),
     (SCEN_MAIL, '구현 가능한 범위에서 진행 제안, 내부 개발 예정 동작 포함')],
    '영상: 시나리오 배치를 우리 축척으로 옮긴 장면의 CPU 경로 계획 (② 컨베이어 높이는 미반영)')

# ----------------------------------------------------------------- 7
SCALE_ROWS = [
    ('지게차 길이 × 폭', '2.8 × 1.13 m', '<b>1.46 × 0.63 m</b> (우리 차체)'),
    ('좁은 통로 폭', '3.8 m', '1.98–2.12 m'),
    ('구역 사이 간격', '3.4 m', '1.77–1.90 m'),
    ('트레일러 안쪽 폭', '2.6 m', '1.36–1.45 m'),
    ('컨베이어 높이', '약 0.7 m', '0.37–0.39 m'),
]
add('축척 환산', '07  우리 지게차 크기로 환산', 55, f"""
<h2 class="headline">길이 비율 0.52, 폭 비율 0.56으로 줄이면 통로 폭 약 2 m, 트레일러 폭 약 1.4 m</h2>
<div class="hw7 scale8 grow">
{img('s02_truck.png', '리보틱스 실제 지게차 평면도. 길이 2.8 m, 폭 1.13 m', '리보틱스 지게차')}
{table(['항목', '시나리오', '우리 축척 (×0.52–0.56)'], SCALE_ROWS, 'comparison h7 nwall t8')}
</div>
""",
    """시나리오는 실제 환경 크기로 적혀 있고, 실제 지게차와 우리 지게차의 크기 비율에 맞게 환경을 줄이라고 되어 있습니다. 리보틱스 지게차는 길이 2.8미터, 폭 1.13미터이고 우리 차체는 1.46미터에 0.63미터라서, 길이로는 0.52배, 폭으로는 0.56배입니다. 이 비율로 줄이면 좁은 통로는 약 2미터, 아래 구역 사이 간격은 1.8에서 1.9미터, 트레일러 안쪽 폭은 1.4미터 안팎, 컨베이어 높이는 약 0.37에서 0.39미터가 됩니다. 두 비율이 7퍼센트 정도 달라서, 어느 쪽을 기준으로 할지는 리보틱스에 확인하려고 합니다. (전환)""",
    [(SCEN_PDF, '2쪽 실제 지게차 2.8 × 1.13 m, 크기 비율에 맞게 환경 설정; 3 · 4 · 7쪽 치수'),
     ('lightminn/forklift sim/models/dls08_measured/README.md', '전장 × 전폭 1.46 × 0.63 m (실측)'),
     ('계산', '1.46 / 2.8 = 0.521, 0.63 / 1.13 = 0.558; 각 치수 × 두 비율')],
    '그림: 시나리오 PDF 2쪽의 지게차 평면도')

# ----------------------------------------------------------------- 8
JUDGE_ROWS = [
    ('③ 일자 배치', '앞 팔레트를 옮긴 뒤 다음 팔레트 다시 찾기', '<b>1차 목표</b>'),
    ('④ 랜덤 배치', '다음 팔레트 고르기, 하역 칸 배정', '<b>1차 목표</b>'),
    ('① 좁은 통로', '구역 사이 간격 위 칸끼리 경로 확보 (전후진 전환 14–29회)', '일부 조건 확보'),
    ('⑤ 트레일러', 'EPAL 6 1열은 꺼내기와 넣기 확보, T11 2열은 경로 미확보', '1열 조건 확보'),
    ('② 컨베이어', '포크 최고 높이 0.32 m, 축소 높이는 0.37 m', '높이 협의'),
]
add('시나리오별 판단', '08  시나리오별 실현 가능성', 60, f"""
<h2 class="headline">일자·랜덤 배치는 1차 목표, 좁은 공간은 조건부로 경로 확보, 컨베이어는 높이 협의</h2>
{table(['시나리오', '걸리는 점', '판단 (경로 계획 기준)'], JUDGE_ROWS, 'comparison h7 concl7 judge8 grow')}
<div class="takeaway">LiDAR가 1.05 m 높이라 바닥 팔레트와 낮은 rack 부재는 카메라와 미리 받은 배치로 보완해야 합니다</div>
""",
    """시나리오별로 지금 시스템에서 걸리는 점을 정리했습니다. 일자 배치와 랜덤 배치는 지금 하고 있는 팔레트 하나 운반의 연장이라 1차 목표로 잡았습니다. 다만 일자 배치는 앞 팔레트를 옮긴 뒤 뒤 팔레트를 다시 찾아야 하고, 랜덤 배치는 다음에 옮길 팔레트를 고르고 하역 구역의 어느 칸에 내려놓을지 정해야 합니다. 좁은 통로와 트레일러는 축소한 장면을 만들어 경로 계획기로 확인했습니다. 좁은 통로는 우리 차의 최소 회전 반경이 2.73미터라 약 2미터 통로에서 한 번에 90도 꺾어 들어갈 수 없습니다. 이웃 팔레트 간격과 정렬 거리 등을 바꾼 144개 조합을 계산해 보니, 집는 칸과 놓는 칸이 모두 구역 사이 간격 위에 있는 일부 조건에서 복귀까지 경로가 나왔고, 계산된 경로의 전진 후진 전환은 14에서 29번이었습니다. 트레일러는 EPAL 6 팔레트를 가운데 한 줄로 놓으면 꺼내기와 넣기, 복귀 경로가 모두 나왔고 전환은 5에서 7번이었습니다. 반면 T11 팔레트를 두 줄로 놓으면 차체와 포크, 팔레트를 감싼 사각형과 여유 거리 때문에 접근 또는 적재 진입 자세에서 막혔습니다. 여기까지는 경로 계획 결과이고, 실제 주행은 다음 장에서 Isaac으로 확인했습니다. 컨베이어는 축소해도 0.37미터인데 우리 포크는 0.32미터까지밖에 안 올라가서 스테이션 높이를 낮출 수 있는지 협의해야 합니다. 공통으로, LiDAR가 1.05미터 높이에 있어서 바닥에 놓인 팔레트나 낮은 rack 부재는 보지 못하므로, 카메라와 미리 받은 배치 정보로 보완해야 합니다. (전환)""",
    [('lightminn/forklift sim/models/dls08_measured/parameters.yaml', 'fork_center_height_m 0.04 + lift_travel_m 0.28 = 포크 중심 최고 0.32 m (최저 높이는 실측 전)'),
     ('lightminn/forklift config/isaac_transport_measured.yaml', '기구 곡률 한계 0.3665 1/m → 뒤차축 최소 회전 반경 2.73 m'),
     ('lightminn/forklift config/isaac_slam_lidar.yaml', 'LiDAR 평면 1.05 m, 그보다 낮은 물체는 보지 못함'),
     ('트레일러 계산', 'T11 0.66 m × 2열, 안쪽 1.36–1.45 m → 균등 간격 12–44 mm'),
     ('lightminn/forklift tools/riibotics_scenario_paths.py (77b7e2d, UBAI job 1026078, 264건)', '통로 144건 성공 14 (간격 위 → 간격 위, 복귀 포함, 전환 14–29회 · 기본 설정만 17–29회); 간격 위 → 구역 위 5건은 복귀 검색에서만 실패; 트레일러 EPAL 6 중앙 1열 행간 0.20 m 에서 a–d 성공(standard footprint 전환 5–7회), T11 2열 60건 전부 실패(접근 직선 · 목표 자세 · 적재 predelivery 거부). CPU 경로 계획 결과, 주행 미검증'),
     ('Codex 교차검증 (2026-10-20)', '시나리오 분석 2회 수렴; 장면 가정 검토 P2 반영')],
    '표: 시나리오별 판단 (좁은 공간 두 줄은 CPU 경로 계획 결과)')

# ----------------------------------------------------------------- 9 (Isaac)
RIIB = 'lightminn/forklift feat/riibotics-scenarios 827e757'
ISAAC_ROWS = [
    ('③ 일자 배치', '5회 중 2회 완주', '3개 연속 완료', '삽입 전 재관측 실패 2회'),
    ('④ 랜덤 배치', '4회 중 1회 완주', '5개 연속 완료 (그림 기울기면 1개만)', '뒤 팔레트 겹침으로 재관측 어긋남'),
    ('⑤ 트레일러', '꺼낸 뒤 운반 중 정지', '한 줄 3개 연속 완료', '위치 추정 오차 16 cm에서 허가 차단'),
    ('① 좁은 통로', '재관측이 옆 칸 팔레트를 인식', '실행 안 함', '이웃 팔레트 구분'),
    ('② 컨베이어', '만들지 않음', '1개 완료 (높이 미반영)', '포크 0.32 m, 컨베이어 0.37 m'),
]
TEAM = 'ws1 artifacts/20261020_demo_scenarios/isaac/runs (팀원 shanghun, fleet 시뮬레이터 run_world, source_v34)'

add('Isaac 재현', '09  Isaac 자율 임무 재현', 60, f"""
<h2 class="headline">Isaac에서 일자·랜덤 배치 팔레트를 인식해 하역하고 복귀까지 자율 주행</h2>
<div class="vid9 grow">
{video('i09_line.mp4', '위에서 본 일자 배치 장면. 왼쪽 적재 구역의 첫 번째 팔레트를 집어 오른쪽 하역 구역의 가장 안쪽 칸에 내려놓고 출발 위치로 돌아옴', '③ 일자 배치, 첫 번째 팔레트')}
{video('i09_random.mp4', '위에서 본 랜덤 배치 장면. 적재 구역의 두 번째 팔레트를 집어 하역 구역 가운데 칸에 내려놓고 돌아옴', '④ 랜덤 배치, 두 번째 팔레트 (첫 번째는 옮겨 둔 상태)')}
</div>
{lgd(('line', '#8fd0dc', '접근 경로'), ('line', '#e8dc78', '운반 경로'), ('line', '#cdb6dd', '복귀 경로'), ('ring', '#33ef63', '하역 위치'))}
""",
    """경로가 나온 장면을 Isaac에 그대로 만들어, 인식부터 하역과 복귀까지 실제 자율 임무로 돌려 보았습니다. 축소한 장면을 창고 바닥에 놓고, 팔레트는 정해진 칸에서 몇 센티미터와 몇 도씩 어긋나게, 랜덤 배치는 그림대로 10도까지 기울여 두었습니다. 카메라로 팔레트를 찾고, SLAM으로 위치를 추정하며, 삽입 직전에 한 번 더 관측한 뒤 들어갑니다. 바닥에 놓인 이웃 팔레트는 LiDAR 높이 아래라 보이지 않으므로, 칸 배치는 미리 알고 있다고 두었습니다. 왼쪽은 일자 배치의 첫 번째 팔레트, 오른쪽은 랜덤 배치의 두 번째 팔레트이고, 둘 다 하역한 뒤 출발 위치로 돌아왔습니다. 연속 이송은 아직 아니고, 앞 팔레트를 옮겨 둔 장면을 따로 만들어 한 번씩 돌린 것입니다. (전환)""",
    [(f'{RIIB} sim/isaac/run_transport.py --layout scene · tools/riibotics_isaac_scenes.py', '리보틱스 장면 8종(축척 0.521, EPAL 6, 남쪽 홀 배치); 집을 팔레트는 명목 칸에서 3–8 cm · 2–3° 어긋남, 랜덤은 그림 기울기 10° 이내'),
     ('ws1 test_runs/riibotics/riib.sbatch', '인식 · SLAM · 장애물 층 · D7 도킹 · 원거리 인식(YOLO11s) 설정 = 10-19 원거리 인식 임무 설정에서 격자 계획만 끔(바닥 팔레트는 장면 배치를 사전 지도로); 하역 판정 8 cm'),
     ('ws1 test_runs/riibotics/r4_* · r5_aisle_out (2026-10-20, 12회)', 'line_1 3회(2 완주) · line_2 1 · line_3 1(하역 9.8 cm) · random_1 2 · random_2 1(완주, 하역 6.0 cm) · random_3 1(하역 9.5 cm) · trailer 1(운반 중 허가 제한, SLAM 최대 0.163 m) · aisle 1(랙 뒤 여유 가정으로 계획 실패, 표에서 제외) · aisle_out 1(근접 캡처가 0.91 m 옆 팔레트)'),
     ('영상', 'r4_line_1_s1 · r4_random_2 transport.mp4 탑뷰, 장면 부분만 잘라 6배속'),
     ('Codex 교차검증 (2026-10-20)', '장면 모드 설계 3회 수렴(정답 팔레트 좌표를 계획에 쓰지 않음); 결과 해석 · 안전 여유 판단 3회 수렴')],
    '영상: Isaac Sim 탑뷰 (6배속)')

add('Isaac 연속 이송', '10  정답 위치로 본 연속 이송', 50, f"""
<h2 class="headline">위치를 정답으로 주면 일자·랜덤·트레일러는 Isaac에서 연속 이송까지 접촉 없이 완료</h2>
<div class="team10 grow">
{video('t10_conveyor.mp4', '위에서 본 컨베이어 장면. 지게차가 왼쪽 컨베이어 끝 팔레트를 집어 오른쪽 컨베이어 끝에 내려놓음', '② 컨베이어 (높이 미반영)')}
{video('t10_line.mp4', '위에서 본 일자 배치 장면. 한 줄로 놓인 팔레트 세 개를 차례로 집어 반대편 칸에 내려놓음', '③ 일자 배치, 세 개 연속')}
{video('t10_random.mp4', '위에서 본 랜덤 배치 장면. 4–7° 기울어진 팔레트 다섯 개를 차례로 하역 칸에 옮김', '④ 랜덤 배치, 다섯 개 연속 (기울기 4–7°)')}
{video('t10_trailer.mp4', '위에서 본 트레일러 장면. 한 줄로 실린 팔레트 세 개를 차례로 꺼내 하역 칸에 옮김', '⑤ 트레일러 한 줄, 세 개 연속')}
</div>
""",
    """같은 Isaac 지게차 모델로, 팔레트와 지게차 위치를 정답으로 주고 경로 계획과 경로 추종만 돌린 팀원의 연속 이송 결과입니다. 카메라 인식과 SLAM은 쓰지 않았습니다. 일자 배치는 세 개, 기울기 4에서 7도인 랜덤 배치는 다섯 개, 트레일러 한 줄은 세 개를 차례로 옮겼고, 팔레트나 벽에 닿은 적은 없었습니다. 컨베이어는 높이를 넣지 않고 바닥 움직임만 본 것입니다. 다만 그림대로 10도까지 기울인 랜덤 배치는 아홉 작업 중 하나만 경로가 나왔습니다. (전환)""",
    [(TEAM, 'I1_p4 1/1 · J1_p5_line 3/3 · J5_p6_random26_5d 5/5 (기울기 −4.3 – −7.3°) · J2_p7_dims_1col 3/3 (안쪽 1.36 m) · 접촉 0; J6_p6_drawn_tilt_5d (그림 기울기 0 · 8 · −10 · 6°) 9건 중 1건 완료 · J3_p7_drawn_2col (그림 비율 2.30 m, 두 줄) 4/4'),
     ('같은 실행 job.txt', '정답 위치 · 경로 추종(인식 · SLAM 없음), 이웃 팔레트 금지 폭 --keep-m 0.2, --free-empty; 컨베이어는 바닥에 놓인 팔레트'),
     ('영상', '각 overview.mp4 를 isaac_spec.crop 으로 바닥만 잘라 마지막 작업 4 s 뒤에서 자르고 10 · 20 · 30 · 20배속 (ws1 test_runs/riibotics/team_clips.sbatch)')],
    '영상: 팀원 Isaac 실행 (정답 위치로 경로 추종)')

add('Isaac 결과', '11  시나리오별 Isaac 결과', 50, f"""
<h2 class="headline">정답 위치로는 대부분 완주하므로, 막힌 곳은 삽입 전 재관측과 위치 추정</h2>
{table(['시나리오', '우리 자율 스택', '정답 위치 경로 추종', '막힌 점'], ISAAC_ROWS, 'comparison h7 concl7 isaac9 isaac11 grow')}
""",
    """두 결과를 나란히 놓으면, 정답 위치로는 연속 이송까지 되는 장면에서 우리 자율 스택이 막힌 곳이 인식과 위치 추정이라는 것이 드러납니다. 일자 배치는 다섯 번 중 두 번, 랜덤 배치는 네 번 중 한 번 하역 오차 8센티미터 안으로 완주했습니다. 실패의 대부분은 삽입 직전 재관측이었습니다. 팔레트 아래판이 잘 안 보이거나, 뒤 팔레트가 겹쳐 보여 방향이 틀어지거나, 좁은 통로에서는 옆 칸 팔레트를 인식했습니다. 하역 구역이 넓게 비어 있어 LiDAR로 위치를 맞출 기준이 없어서, 하역 오차가 위치 추정 오차를 따라 9센티미터를 넘은 경우도 있었습니다. 트레일러는 팔레트를 꺼낸 뒤 나오는 중에 위치 추정 오차가 16센티미터까지 커지면서 벽 옆에서 멈췄습니다. (전환)""",
    [('ws1 test_runs/riibotics/r4_* · r5_aisle_out (2026-10-20, 12회)', '완주 = 하역 오차 8 cm 이내 + 복귀; 표의 횟수는 같은 장면을 시드만 바꿔 돌린 것과 순차 장면을 합친 것'),
     ('같은 실행 result.json slam_summary', '임무 전체 SLAM 위치 오차 최대 0.14 m (일자 1번 시드 2), 0.163 m (트레일러); 하역 LiDAR 정합은 열린 하역 구역에서 모두 start_rejected:degenerate'),
     ('같은 실행 near_capture · detection_diagnostics', '재관측 실패: 아래판 증거 4 < 15 (일자), 새 직선 횡 6.7–9.8 cm · 3.8–6.0° (랜덤), 0.91 m 옆 팔레트 (통로)')],
    '표: 시나리오별 Isaac 결과 (② 컨베이어는 높이 협의로 재현하지 않음)')

# ----------------------------------------------------------------- 10
PLAN_ROWS = [
    ('1단계', '③ 일자, ④ 랜덤', '삽입 전 재관측 안정화, 다음 팔레트 선택과 하역 칸 배정'),
    ('2단계', '① 좁은 통로, ⑤ 트레일러', '이웃 팔레트 구분, 위치 추정 오차 줄이기'),
    ('3단계', '실차', '같은 장면을 바닥에 표시해 실차로 시연'),
    ('보류', '② 컨베이어', '스테이션 높이를 0.23 m 이하로 협의'),
]
add('구현 전략', '12  구현 전략', 55, f"""
<h2 class="headline">일자·랜덤 배치 연속 이송을 먼저 완성하고, 좁은 공간은 이웃 팔레트 구분 뒤 진행</h2>
{table(['단계', '대상', '할 일'], PLAN_ROWS, 'comparison h7 concl7 plan8 grow')}
""",
    """구현 순서입니다. 1단계는 일자 배치와 랜덤 배치의 연속 이송입니다. 앞에서 보인 운용 콘솔은 이미 한 세션에서 미션을 연달아 받으므로, 여기에 다음 팔레트를 고르는 순서, 하역 구역의 칸 배정, 이미 옮긴 팔레트를 다음 경로의 장애물로 넣는 기능을 더하면 됩니다. 그보다 먼저 앞 장에서 실패가 가장 많았던 삽입 직전 재관측을 먼저 안정화합니다. 2단계는 좁은 통로와 트레일러입니다. Isaac 재현에서 통로는 옆 칸 팔레트를 잘못 인식했고, 트레일러는 위치 추정 오차가 커지면서 벽 옆에서 멈췄으므로, 이웃 팔레트를 구분하고 위치 추정 오차를 줄이는 일을 하겠습니다. 3단계는 같은 장면을 바닥에 테이프로 표시해 실차로 시연하는 것입니다. 컨베이어는 우리 포크로 팔레트를 들어 올릴 수 있는 스테이션 높이가 약 0.23미터 이하라서, 높이를 낮출 수 있는지 협의한 뒤에 진행하겠습니다. (전환)""",
    [(PR61, '한 세션에서 미션 연속 지시 · 취소 뒤 재지시 · 실린 팔레트 재지시'),
     ('lightminn/forklift src/forklift_core/perception/pallet_model.py · fork_fit.py', '현재 모델에서 들기 시작할 수 있는 스테이션 높이 상한 EPAL 6 약 0.233 m, T11 약 0.273 m (Codex 재계산)'),
     ('Codex 교차검증 (2026-10-20)', '전체 자동 이송이면 옮긴 · 남은 팔레트 구분, 가림을 빈칸으로 오판하지 않기, 적치 순서, 실패 뒤 목록 재정렬이 필요')],
    '표: 구현 단계')

# ----------------------------------------------------------------- 10
CONCL = [
    ('운용 콘솔', '브라우저 하나로 미션 지시, 상태 보기, 직접 운전'),
    ('시연 시나리오', 'Isaac에서 일자·랜덤 배치 완주, 막힌 곳은 삽입 전 재관측과 위치 추정'),
    ('다음 목표', '일자·랜덤 배치 연속 이송을 인식과 SLAM까지 포함해 완주'),
]
add('결론', '13  결론', 35, f"""
<h2 class="headline">운용 콘솔로 Isaac 지게차를 지시하고 운전, 시연 시나리오는 일자·랜덤 배치부터</h2>
{table(['구분', '내용'], CONCL, 'comparison h7 concl7 concl13 grow')}
""",
    """결론입니다. 이번 주에는 지게차를 브라우저로 다루는 운용 콘솔을 만들어 Isaac 지게차에 연결했고, 화면 하나로 미션을 지시하고 상태를 보고 직접 운전할 수 있게 했습니다. 리보틱스 시연 시나리오는 Isaac에서 일자 배치와 랜덤 배치를 인식부터 복귀까지 완주했고, 막힌 곳은 삽입 직전 재관측과 위치 추정이었습니다. 다음 목표는 일자 배치와 랜덤 배치의 연속 이송을 인식과 SLAM까지 포함해 완주하는 것입니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [('이번 덱 각 장', '1–5쪽 운용 콘솔, 9–11쪽 Isaac 결과, 12쪽 구현 단계')],
    '출처: 이번 덱 각 장')


TITLE = '8주차 자율 지게차 개발'
TOTAL = 705


def build():
    assert len(slides) == 14, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-10-20. 앞 절반은 운용 콘솔, 뒤 절반은 리보틱스 시연 시나리오 분석과 구현 전략이다. '
              '콘솔 화면 일부(작업 지정 창, 계획 경로 지도, 수동 조종, 폰, 결과 기록)는 가짜 차량으로 찍었다(SOURCES.md). '
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
