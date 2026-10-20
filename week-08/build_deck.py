"""Build the week 8 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 8 (class, 2026-10-21 draft) is the operator console first and the one
hardware item of the week after it (user, 2026-10-20): what the console does,
how it connects, the screen layout, ordering a mission, the map, the camera
and vehicle state, driving by hand, and running mission after mission; then
the encoder magnet adapter and the conclusion. The user asked for function
and practical use rather than the safety design (stop kinds, arming), about
ten slides, each as light as the earlier decks.

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
ISAAC_SHOT = '콘솔 화면 캡처 — Isaac 실시간 실행기 연결 (콘솔 세션, 2026-10-17)'
MOCK_SHOT = '콘솔 화면 캡처 — 가짜 차량 console.mock_vehicle (2026-10-20, 임시)'
ADAPTER = 'lightminn/forklift 작업 트리 docs/design/encoder_magnet_adapter/ (README.md · preview.png, 2026-10-17, 미커밋)'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def img(src, alt, cap=None, cls='shot', temp=False):
    t = '<span class="tmp8">임시 화면</span>' if temp else ''
    c = f'<figcaption>{cap or ""}{t}</figcaption>' if (cap or temp) else ''
    return (f'<figure class="{cls}"><img class="media" src="assets/{src}" '
            f'alt="{escape(alt, quote=True)}">{c}</figure>')


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
        else:
            sw = f'<span class="sw" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="lgd7">{"".join(out)}</div>'


# ----------------------------------------------------------------- figures
def structure_diagram():
    """Browser -> gateway -> robot stack -> real truck or Isaac, drawn in the deck's style."""
    W, H = 1180, 360
    boxes = [(0, 120, 230, 120, '폰 · 태블릿 · 노트북', '브라우저 (설치 없음)', False),
             (320, 120, 230, 120, '게이트웨이', '작업 단위 API', False),
             (640, 120, 250, 120, 'ROS 2 로봇 스택', '미션, 위치 추정, 경로', False),
             (980, 20, 200, 120, '실차', 'Jetson ↔ STM32', True),
             (980, 220, 200, 120, 'Isaac Sim', 'ws1 실시간 실행기', False)]
    parts = [f'<defs><marker id="ah8" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
             f'<marker id="ah8g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="#9aa3ad"/></marker></defs>']
    # the part that changes between the real truck and Isaac
    parts.append('<rect x="962" y="4" width="216" height="352" rx="10" fill="none" stroke="#c3cad3" stroke-width="2" stroke-dasharray="8 6"/>'
                 '<text x="1070" y="186" text-anchor="middle" font-size="17" fill="#5d6670">구동부만 바뀜</text>')
    for x, y, w, h, t, sub, later in boxes:
        stroke = '#c3cad3' if later else BLUE
        fill = '#f7f9fb' if later else '#eef4fb'
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>'
                     f'<text x="{x + w / 2}" y="{y + 52}" text-anchor="middle" font-size="24" font-weight="700" fill="#1b1f24">{t}</text>'
                     f'<text x="{x + w / 2}" y="{y + 86}" text-anchor="middle" font-size="18" fill="#44505c">{sub}</text>')
    for x1, x2, lab in ((230, 318, 'Wi-Fi'), (550, 638, 'ROS 2')):
        parts.append(f'<line x1="{x1}" y1="180" x2="{x2}" y2="180" stroke="{BLUE}" stroke-width="4" marker-end="url(#ah8)"/>'
                     f'<text x="{(x1 + x2) / 2}" y="166" text-anchor="middle" font-size="17" fill="{BLUE}">{lab}</text>')
    parts.append('<polyline points="890,160 935,160 935,80 976,80" fill="none" stroke="#9aa3ad" stroke-width="4" stroke-dasharray="10 7" marker-end="url(#ah8g)"/>'
                 f'<polyline points="890,200 935,200 935,280 976,280" fill="none" stroke="{BLUE}" stroke-width="4" marker-end="url(#ah8)"/>')
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="폰, 태블릿, 노트북 브라우저가 Wi-Fi로 게이트웨이에, '
            f'게이트웨이가 ROS 2로 로봇 스택에 붙고, 로봇 스택 아래 구동부가 실차(추후 연결) 또는 Isaac Sim">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


def layout_figure():
    """Full console screenshot with numbered region markers (positions in % of the 1600 x 900 shot)."""
    marks = [(1, 30.5, 3.5), (2, 50.0, 30.0), (3, 34.5, 70.0), (4, 88.5, 9.0), (5, 6.5, 13.5)]
    m = ''.join(f'<span class="mk8" style="left:{x}%;top:{y}%">{n}</span>' for n, x, y in marks)
    return ('<figure class="shot lay8fig"><div class="frame8"><img class="media" src="assets/a03_layout.png" '
            f'alt="운용 콘솔 넓은 화면. 위 상태 줄, 왼쪽 메뉴, 가운데 지도와 왼쪽 아래 전방 카메라 창, 오른쪽 차량 상세">{m}</div></figure>')


STAGES = ['관찰', '접근', '삽입', '들기', '빼기', '운반', '내리기', '후퇴', '복귀']


# ----------------------------------------------------------------- cover
add('개발 진행 보고', '8주차\n자율 지게차 개발', 20, '',
    """안녕하십니까. 8주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 주에는 지게차를 무선으로 다루는 운용 콘솔을 중심으로 말씀드리겠습니다. 콘솔이 하는 일과 연결 구조, 화면 구성을 먼저 보이고, 미션 지시, 지도와 카메라, 직접 운전, 미션을 이어서 처리하는 기능을 차례로 보인 뒤, 하드웨어로는 엔코더 자석 어댑터를 소개하고 결론으로 마치겠습니다. (전환)""",
    [(ROBOT, '운용 콘솔 console/ · 설계 문서 · PR #61–#65'), (ADAPTER, '엔코더 자석 어댑터')], '진행 보고')

# ----------------------------------------------------------------- 1
add('콘솔이 하는 일', '01  운용 콘솔이 하는 일', 50, f"""
<h2 class="headline">지게차 한 대를 브라우저 화면 하나로 보고, 지시하고, 직접 운전</h2>
<div class="trio8 grow">
{img('a01_watch.png', 'Isaac 지게차를 연결한 콘솔의 지도와 전방 카메라. 카메라에 팔레트가 보임', '상태 보기 (지도, LiDAR, 카메라)')}
{img('a01_order.png', '작업 지정 창의 확인 단계. 팔레트 P-01, 하역 위치 D-A, 4단계 목록', '작업 지시 (팔레트, 하역 위치)')}
{img('a01_drive.png', '수동 조종 탭. 누르고 있기 버튼, 조이스틱, 포크 올리기와 내리기, 속도와 곡률 명령 막대', '직접 운전 (조이스틱, 게임패드)')}
</div>
<div class="takeaway">지금까지는 ws1 터미널에서 명령을 넣었지만, 이제는 지게차 옆에서 폰으로 바로 다룹니다</div>
""",
    """이번 주에 만든 운용 콘솔입니다. 6주차 발표에서 무선 통신을 고려하지 않았다는 피드백을 받았습니다. 지금까지는 연구실 워크스테이션 터미널에서 명령을 넣고, 결과 영상은 미션이 끝난 뒤에 받아 봤습니다. 실제 현장에서는 지게차 옆에서 폰이나 노트북으로 바로 다뤄야 하므로 브라우저로 쓰는 콘솔을 만들었습니다. 콘솔이 하는 일은 세 가지입니다. 왼쪽처럼 지도와 LiDAR, 전방 카메라로 지게차 상태를 보고, 가운데처럼 옮길 팔레트와 내려놓을 위치를 골라 작업을 지시하고, 오른쪽처럼 조이스틱이나 게임패드로 직접 운전합니다. (전환)""",
    [('lightminn/forklift docs/references/week6_feedback.md 5절', '무선 통신 미고려 — 콘솔 설계의 계기'),
     (DESIGN, '1절 목적: 상태 감시, 작업 지시, 수동 조종 (육안 · 영상)'),
     (ISAAC_SHOT, '왼쪽 c3_live_auto.png'), (MOCK_SHOT, '가운데 03_wizard3.png, 오른쪽 22_teleop_drive.png')],
    '그림: 콘솔 화면 캡처 세 장 (가운데 · 오른쪽은 가짜 차량, 가짜 차량 화면)')

# ----------------------------------------------------------------- 2
add('시스템 구조', '02  콘솔 연결 구조', 55, f"""
<h2 class="headline">브라우저가 지게차의 게이트웨이에 붙고, 실차와 Isaac은 같은 로봇 스택을 공유</h2>
<div class="hw7 wide grow">
<div class="chart7 sys8">{structure_diagram()}</div>
{table(['구분', '방식'], [
    ('접속 기기', '폰, 태블릿, 노트북'),
    ('설치', '없음 (브라우저)'),
    ('입력', '터치, 키보드, 게임패드'),
    ('무선 연결', 'Jetson이 Wi-Fi AP (1:1)'),
    ('연결 대상', 'Isaac 완료, 실차 예정')], 'comparison h7 nwall t8')}
</div>
<div class="takeaway">시뮬레이션에서 쓰는 화면과 기능을 실차에서도 그대로 쓰도록 맨 아래 구동부만 바꿉니다</div>
""",
    """연결 구조입니다. 폰이나 노트북의 브라우저가 Wi-Fi로 지게차에 있는 게이트웨이에 접속합니다. 앱을 따로 설치하지 않고, 입력은 터치, 키보드, 게임패드를 모두 받습니다. 게이트웨이는 팔레트 운반 같은 작업 단위로 요청을 받아 ROS 2 로봇 스택에 넘기고, 로봇 스택이 미션 실행, 위치 추정, 경로 계획을 맡습니다. 실차와 Isaac 시뮬레이션은 이 로봇 스택을 같이 쓰고 맨 아래 구동부만 바뀝니다. 그래서 지금 Isaac에서 쓰는 화면을 실차에서도 그대로 쓸 수 있습니다. 실차에서는 Jetson이 직접 Wi-Fi 공유기 역할을 해서 콘솔 기기와 일대일로 연결할 계획이고, 실차 연결은 아직 하지 않았습니다. 브라우저를 고른 이유는 폰에 ROS를 설치할 수 없기 때문이고, 게이트웨이가 ROS 토픽이 아니라 작업 단위 API를 주므로 나중에 여러 대를 관제하는 서버가 생겨도 같은 API를 그대로 중계하면 됩니다. (전환)""",
    [(DESIGN, '2절 결정: 로봇 쪽 전용 게이트웨이 + 웹 앱(A안), 웹 클라이언트(폰에 ROS 설치 불가, Gamepad API), 1단계 망 Jetson AP 1:1, 실차와 Isaac 이 같은 ROS 2 스택; 3절 구조도'),
     (README, 'web/ 빌드 없는 브라우저 콘솔, gateway/ 관찰 전용 게이트웨이(ROS 2 컨테이너)'),
     (PR61, 'Isaac 실시간 실행기와 콘솔 연결; 실차 연결(설계 6절 C4)은 미착수')],
    '그림: 설계 문서 3절 구조도를 덱 배치로 다시 그림 (안전 계층은 생략)')

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
{img('a03_phone.png', '폰 폭(400 px) 화면. 상태, 전방 카메라, 수동 조종 순서로 세로로 쌓이고 아래에 STOP 고정', '폰 화면', cls='shot phone8')}
</div>
<div class="takeaway">폰에서는 같은 내용이 카메라, 수동 조종, 지도 순서로 세로로 쌓입니다</div>
""",
    """화면 구성입니다. 물류 현장의 차량 관제 화면, 흔히 FMS라고 부르는 형식을 따랐습니다. 맨 위 1번 줄에는 연결 대상과 운행 모드, 조종 권한이 있습니다. 가운데 2번은 지도로, 점유 격자와 LiDAR 점, 계획 경로를 그립니다. 그 위에 3번 전방 카메라 창이 떠 있고, 오른쪽 4번에는 차량 상세와 수동 조종 탭이 있습니다. 왼쪽 5번 메뉴로 모니터링, 이벤트 기록, 통신 화면을 오갑니다. 오른쪽은 같은 화면을 폰 폭으로 연 모습입니다. 좁은 화면에서는 카메라, 수동 조종, 지도 순서로 세로로 쌓이고 정지 버튼은 아래에 고정됩니다. (전환)""",
    [(README, 'web/ 화면은 FMS 형식: 왼쪽 메뉴(모니터링 · 이벤트 기록 · 통신), 가운데 지도와 그 위 전방 카메라 창, 오른쪽 차량 상세와 수동 조종 탭'),
     (DESIGN, '8절: 폰에서는 카메라 → 수동 조종 → 지도 → 작업 지시 순서로 세로, STOP 하단 고정'),
     (ISAAC_SHOT, '넓은 화면 c3_live_auto.png'), (MOCK_SHOT, '폰 화면 30_phone.png (400 × 860)')],
    '그림: 콘솔 화면 캡처 (번호는 덱에서 덧붙임)')

# ----------------------------------------------------------------- 4
add('작업 지정과 진행', '04  작업 지정과 진행', 55, f"""
<h2 class="headline">작업 종류, 대상, 확인 세 단계로 지시하면 미션 진행을 단계별로 표시</h2>
<div class="steps8 grow">
{img('a04_step1.png', '작업 지정 1단계. 작업 종류 팔레트 운반, 4단계 설명', '① 작업 종류')}
{img('a04_step2.png', '작업 지정 2단계. 팔레트 P-01과 P-02, 하역 위치 D-A와 D-B 선택', '② 대상 설정')}
{img('a04_step3.png', '작업 지정 3단계. 팔레트 P-01, 하역 위치 D-A 확인과 작업 시작 버튼', '③ 확인')}
</div>
<div class="phase-flow stages8">{'<span class="arrow">→</span>'.join(f'<span>{s}</span>' for s in STAGES)}</div>
<div class="takeaway">지도에서 대기 중인 팔레트를 누르면 그 팔레트가 골라진 채로 바로 대상 설정이 열립니다</div>
""",
    """미션을 지시하는 방법입니다. 작업 지정 창은 세 단계입니다. 먼저 작업 종류를 고릅니다. 지금은 팔레트 운반 하나이고, 차량이 지원한다고 알린 작업만 보입니다. 다음으로 옮길 팔레트와 내려놓을 하역 위치를 고르고, 마지막으로 확인하고 작업을 시작합니다. 지도에서 팔레트를 직접 눌러도 그 팔레트가 골라진 채로 대상 설정이 바로 열립니다. 작업이 시작되면 아래 띠처럼 관찰, 접근, 삽입, 들기, 빼기, 운반, 내리기, 후퇴, 복귀의 아홉 단계 중 지금 어디까지 왔는지 화면에 표시되고, 끝나면 결과 기록에 남습니다. (전환)""",
    [(README, "작업은 '작업 지정' 창에서 작업 종류 → 대상 설정 → 확인 세 단계, capabilities 에 밝힌 작업만, console/1 은 '팔레트 운반' 하나, 지도에서 팔레트를 누르면 2단계가 열림"),
     (PR61, '결과 기록부(D13), 미션 진행 단계 표시'),
     ('콘솔 화면 작업 진행 막대', '관찰 · 접근 · 삽입 · 들기 · 빼기 · 운반 · 내리기 · 후퇴 · 복귀'),
     (MOCK_SHOT, '01_wizard1 · 02b_wizard2 · 03_wizard3 (작업 지정 창)')],
    '그림: 작업 지정 창 세 단계 (가짜 차량, 가짜 차량 화면)')

# ----------------------------------------------------------------- 5
add('지도', '05  지도', 45, f"""
<h2 class="headline">SLAM 지도 위에 LiDAR 점과 계획 경로를 겹쳐 실시간 표시</h2>
<div class="pair8 grow">
{img('a05_slam.png', 'Isaac 공장 장면을 SLAM으로 만든 점유 격자 지도. 벽과 선반 윤곽이 파란 칸으로 보이고 아래쪽에 지게차', 'Isaac 공장 장면 SLAM 지도')}
{img('a05_path.png', '가짜 차량 화면의 지도. 지게차에서 팔레트 P-01 앞까지 회색 계획 경로, 주변 장애물 격자와 LiDAR 점', '팔레트까지 계획 경로')}
</div>
{lgd(('box', GRID, '점유 격자'), ('dot', SCAN, 'LiDAR 점'), ('line', PATH, '계획 경로'), ('line', REV, '후진 구간'))}
<div class="takeaway">끌어서 옮기고 확대하거나 차량을 따라가게 할 수 있고, 표시 층은 따로 켜고 끕니다</div>
""",
    """지도입니다. 왼쪽은 Isaac 공장 장면에서 SLAM으로 만든 점유 격자 지도를 콘솔에 띄운 모습입니다. 파란 칸이 벽과 선반 같은 장애물이고, 빨간 점이 지금 LiDAR가 보는 점입니다. 오른쪽처럼 미션 중에는 팔레트까지 가는 계획 경로를 회색 선으로 그리고, 후진하는 구간은 주황색으로 구분합니다. 지도는 끌어서 옮기고, 휠이나 두 손가락으로 확대하고, 차량 따라가기를 켜면 지게차를 화면 가운데에 둡니다. 격자, LiDAR, 경로 같은 표시 층은 따로 켜고 끌 수 있습니다. (전환)""",
    [(README, '지도: 끌기 이동, 휠/두 손가락 확대, 차량 따라가기, 표시 층 선택'),
     (DESIGN, '8절 지도: 점유 격자, LiDAR 점, 계획 경로(후진 구간 구분), 팔레트 · 하역 위치'),
     ('콘솔 화면 캡처 — Isaac 관찰 전용 게이트웨이 (콘솔 세션, 2026-10-15)', '왼쪽 c2a-isaac-live-2.png (공장 장면 SLAM)'),
     (MOCK_SHOT, '오른쪽 10_run_3s.png'),
     ('범례 색', '콘솔 화면 범례의 점유 격자 · LiDAR 점 · 계획 경로 · 후진 구간 색')],
    '그림: 콘솔 지도 두 장 (오른쪽은 가짜 차량, 가짜 차량 화면)')

# ----------------------------------------------------------------- 6
add('카메라와 차량 상태', '06  카메라와 차량 상태', 45, f"""
<h2 class="headline">전방 카메라 영상과 속도, 조향, 포크 높이, 작업 단계를 한 화면에</h2>
<div class="hw7 wide grow">
<div class="duo8">
{img('a06_cam.png', 'Isaac 전방 카메라 창. 벽 앞 바닥에 놓인 팔레트', '전방 카메라')}
{img('a06_state.png', '차량 상세. 속도 -0.29 m/s, 조향 -0.1°, 포크 높이 165 mm, 작업 진행 03 운반', '운반 중 차량 상태')}
</div>
{table(['항목', '표시'], [
    ('속도', '뒤 차축 기준 m/s'),
    ('조향', '조향각 (°)'),
    ('포크 높이', 'mm'),
    ('위치', '지도 좌표와 방향'),
    ('작업 진행', '현재 단계와 남은 단계')], 'comparison h7 nwall t8')}
</div>
<div class="takeaway">운반 중에는 포크 높이와 남은 단계를 보고 진행 상황을 바로 알 수 있습니다</div>
""",
    """카메라와 차량 상태입니다. 왼쪽은 Isaac 지게차의 전방 카메라 영상으로, 앞에 놓인 팔레트가 보입니다. 오른쪽은 팔레트를 들고 운반하는 중의 차량 상세입니다. 뒤 차축 기준 속도와 조향각, 포크 높이를 숫자로 보이고, 아래 막대로 아홉 단계 중 지금 운반 단계에 있다는 것을 보여 줍니다. 이 값들은 차량이 보내는 상태이고, 배터리처럼 아직 잴 장치가 없는 값은 지어내지 않고 측정 장치 없음으로 표시합니다. (전환)""",
    [(DESIGN, '8절 차량 상태: 속도(뒤 차축 기준), 조향, 포크 높이, 자세와 보정 버전, 적재; 측정 수단이 없는 값은 "측정 장치 없음"'),
     (ISAAC_SHOT, '왼쪽 c3_live_auto.png 카메라 창, 오른쪽 c3b_transport.png 차량 상세 (운반 중, 포크 165 mm)')],
    '그림: Isaac 연결 콘솔 화면에서 카메라 창과 차량 상세를 잘라 냄')

# ----------------------------------------------------------------- 7
add('직접 운전', '07  직접 운전', 50, f"""
<h2 class="headline">조이스틱이나 게임패드로 몰고, 갈 경로를 지도와 카메라 바닥에 미리 표시</h2>
<div class="hw7 wide grow">
{img('a07_teleop.png', '수동 조종 중인 콘솔. 지도에 지게차 앞으로 보라색 점선 예상 궤적, 카메라 바닥에도 같은 궤적, 오른쪽에 조이스틱과 속도 · 곡률 명령', None)}
{table(['구분', '방식'], [
    ('입력', '화면 조이스틱, 게임패드, 키보드'),
    ('미리 보기', '지도와 카메라 바닥에 예상 경로'),
    ('포크', '올리기, 내리기 버튼'),
    ('조종 방식', '눈으로 보며, 영상만 보며')], 'comparison h7 nwall t8')}
</div>
{lgd(('dash', TELE, '조종 예상 궤적'))}
<div class="takeaway">자동 주행 중에도 일시정지하고 수동 조종으로 바꿔 차를 옮길 수 있습니다</div>
""",
    """직접 운전입니다. 수동 조종 탭에서 화면 조이스틱이나 게임패드, 키보드로 지게차를 몹니다. 조이스틱을 움직이면 지금 명령대로 가면 지나갈 경로를 지도에 보라색 점선으로 그리고, 같은 경로를 카메라 영상의 바닥에도 겹쳐 보여 줍니다. 그래서 영상만 보고 운전할 때도 차가 어디로 갈지 미리 알 수 있습니다. 포크는 올리기와 내리기 버튼으로 움직입니다. 자동 주행 중에도 일시정지하고 수동 조종으로 바꿔 차를 옮길 수 있습니다. (전환)""",
    [(DESIGN, '1절 수동 조종(육안 · 영상), 5.3 영상 조종, 5.5 입력 장치(터치 · 키보드 · 게임패드), 8절 지도 · 카메라의 수동 조종 예상 궤적'),
     ('콘솔 화면 수동 조종 탭', '키보드 Space 누르고 있기 · WS 속도 · AD 조향 · RF 포크, ▲ 올리기 / ▼ 내리기'),
     (MOCK_SHOT, '22_teleop_drive.png (전진 + 왼쪽 조향)'),
     ('미확인 (2026-10-20)', 'Isaac 실행기의 수동 포크 승강 구동 — 10-17 미구동, 10-19 출력 방식 합의; 일시정지 뒤 수동 조종 전환은 녹화 때 확인')],
    '그림: 가짜 차량 수동 조종 화면 (가짜 차량 화면)')

# ----------------------------------------------------------------- 8
add('이어서 운용하기', '08  이어서 운용하기', 55, f"""
<h2 class="headline">실행기를 한 번 띄워 두고 미션을 연달아 처리, 취소나 실패 뒤에도 다음 미션을 받음</h2>
<div class="hw7 grow">
{img('a08_results.png', '차량 상세. 작업 진행 M-0001 P-01 → D-A 아홉 단계 모두 완료, 작업 지정에 작업을 받을 수 있습니다', '미션 완료 뒤 바로 다음 작업 대기')}
{table(['상황', '콘솔에서 할 수 있는 일'], [
    ('미션 완료', '바로 다음 미션 지시'),
    ('중간 취소', '다른 팔레트, 하역 위치로 다시 지시'),
    ('포크에 팔레트', '다시 지시하면 운반부터 이어 감'),
    ('미션 실패', '수동으로 옮긴 뒤 다시 지시'),
    ('기록', '미션마다 결과 기록에 남음')], 'comparison h7 nwall t8')}
</div>
<div class="takeaway">운반 중 취소해도 포크 위 팔레트를 다시 지시하면 내려놓지 않고 바로 운반합니다</div>
""",
    """이어서 운용하는 기능입니다. 이전에는 미션 하나를 돌리면 시뮬레이션이 끝났습니다. 이제는 실행기를 한 번 띄워 두면 한 세션에서 미션을 연달아 받습니다. 미션이 끝나면 바로 다음 미션을 지시할 수 있고, 중간에 취소하면 다른 팔레트나 하역 위치로 다시 지시할 수 있습니다. 운반 중에 취소해서 팔레트가 포크 위에 있을 때 그 팔레트를 다시 지시하면 내려놓고 다시 집지 않고 운반부터 이어 갑니다. 미션이 실패하면 수동 조종으로 차를 옮긴 뒤 다시 지시하고, 미션마다 결과가 기록에 남습니다. (전환)""",
    [(PR61, '세션 하나에서 미션이 끝나거나 실패 · 취소돼도 실행기가 살아 있고 다음 미션을 받음; 운반 중 취소 뒤 실린 팔레트를 그대로 다시 내면 운반부터(6c); 결과 기록부; 실패 뒤 수동 조종 허용'),
     ('lightminn/forklift PR #63–#65 (2026-10-19/20)', '도킹 중 긴 STOP 뒤 세션 유지(U30), 취소 복구 재개 재시험'),
     ('화면에 쓰지 않은 한계', 'U16 2시간 연속은 1.5 h 에 SLAM 응답 기한 초과로 미충족 — 장시간 운용은 주장하지 않음')],
    '그림: 미션 완료 뒤 차량 상세 (가짜 차량 화면)')

# ----------------------------------------------------------------- 9
add('엔코더 자석 어댑터', '09  엔코더 자석 어댑터', 50, f"""
<h2 class="headline">Ø2 mm 모터 축에 끼워 Ø5 mm 자석 접착면을 만드는 높이 2 mm 링</h2>
<div class="hw7 grow">
<div class="duo8 ad8">
{img('a09_model.png', '어댑터 3D 모델. 가운데 구멍이 뚫린 청록색 링', '3D 모델')}
{img('a09_section.png', '어댑터 중심 단면. 외경 Ø5.00, 내경 Ø2.10, 높이 2.00, 외측 모따기 C0.15, 입구 모따기 C0.20', '중심 단면 (mm)')}
</div>
{table(['항목', '치수와 용도'], [
    ('대상 축', 'DC 모터 축 Ø2 mm, 돌출 2 mm'),
    ('형상', '외경 Ø5 mm, 높이 2 mm, 관통 구멍'),
    ('윗면', '자석을 붙이는 평평한 면'),
    ('시험편 내경', '2.00, 2.10, 2.20, 2.30 mm'),
    ('출력', '3D 프린터, 모따기 면이 바닥')], 'comparison h7 nwall t8')}
</div>
<div class="takeaway">내경이 다른 시험편 네 개를 출력해 축에 가장 잘 맞는 치수를 고를 예정입니다</div>
""",
    """하드웨어는 이번 주에 엔코더 자석 어댑터를 설계했습니다. 자기식 엔코더는 축 끝에 붙인 자석의 회전을 읽는데, 모터 축이 지름 2밀리미터, 돌출 길이 2밀리미터로 짧고 가늘어 자석을 바로 붙이기 어렵습니다. 그래서 축에 끼우는 높이 2밀리미터, 외경 5밀리미터의 링을 만들고, 윗면을 자석을 붙이는 평평한 면으로 했습니다. 축 끝을 더 늘리는 캡이 아니라 구멍이 뚫린 링이라 축에 끝까지 끼울 수 있습니다. 3D 프린터는 구멍 치수가 설계와 다르게 나오기 쉬워서 내경을 2.00부터 2.30밀리미터까지 네 가지로 만들어 두었고, 출력해 보고 축에 가장 잘 맞는 것을 고르겠습니다. 자석 크기와 센서 간격은 자석 규격이 정해지면 맞추겠습니다. (전환)""",
    [(ADAPTER, '사용자 요청(2026-10-17): 약 Ø2 mm, 돌출 2 mm DC 모터 축을 감싸 외경 Ø5 mm, 부품 높이 2 mm 의 자석 접착면 — 캡이 아니라 관통구멍 링; 내경 후보 2.00/2.10/2.20/2.30, 기본 2.10(끼워맞춤 미검증); 아래쪽 입구 C0.20, 바닥 바깥 C0.15; 자석 규격 미정이라 홈 · 턱 없음'),
     ('사용자 (2026-10-20)', '이번 주 하드웨어는 엔코더 자석 어댑터만 진행')],
    '그림: 어댑터 미리보기(preview.png)에서 3D 모델과 단면만 잘라 냄')

# ----------------------------------------------------------------- 10
END_ROWS = [
    ('운용 콘솔', '미션 지시, 지도와 카메라, 직접 운전, 연속 운용', 'Jetson에 게이트웨이 올리고 Wi-Fi 연결'),
    ('엔코더', '자석 어댑터 설계, 시험편 네 개', '시험 출력, 축 끼움 확인, 자석 부착'),
    ('구동 보드', '회로도 (7주차)', 'PCB 배치 → 제작'),
]
add('결론 및 향후 작업', '10  결론 및 향후 작업', 50, f"""
<h2 class="headline">운용 콘솔로 Isaac 지게차를 지시하고 운전, 다음은 실차 연결과 어댑터 시험 출력</h2>
<table class="comparison h7 concl7 grow"><tr><th>구분</th><th>이번 주</th><th>향후 작업</th></tr>
{''.join(f'<tr><td>{g}</td><td>{a}</td><td class="nxt">{b}</td></tr>' for g, a, b in END_ROWS)}</table>
<div class="takeaway">다음 목표는 콘솔을 실차에 연결해 시뮬레이션과 같은 화면으로 운용하는 것입니다</div>
""",
    """결론입니다. 이번 주에는 지게차를 브라우저로 다루는 운용 콘솔을 만들어 Isaac 지게차에 연결했습니다. 화면 하나로 미션을 지시하고, 지도와 카메라로 상태를 보고, 직접 운전하고, 미션을 연달아 처리할 수 있습니다. 하드웨어로는 모터 축에 엔코더 자석을 붙이기 위한 어댑터를 설계했습니다. 앞으로는 콘솔의 게이트웨이를 실차 Jetson에 올려 Wi-Fi로 연결하고, 어댑터 시험편을 출력해 축에 맞는 치수를 고른 뒤 자석을 붙이겠습니다. 구동 보드는 지난주 회로도를 바탕으로 PCB 배치와 제작을 이어 가겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [(DESIGN, '6절 순서: 실차 연결(C4)은 하위 제어와 시험된 정지 뒤'),
     ('week-07 11쪽', '구동 보드 PCB 배치 → 제작, 자석 정렬 브래킷'),
     (ADAPTER, '시험편 출력 후 내경 선정')],
    '출처: 이번 덱 각 장 · 7주차 향후 작업')


TITLE = '8주차 자율 지게차 개발'
TOTAL = 530


def build():
    assert len(slides) == 11, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-10-20. 운용 콘솔을 중심으로 하고 하드웨어는 엔코더 자석 어댑터만 다룬다. '
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
