"""Build the week 11 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 11 (week 10 had no presentation) shows what the truck now does on its own in Isaac: it finds its start on the
prior map from a LiDAR scan, moves three pallets in a row with camera recognition and SLAM on, finishes the
Riibotics trailer scene, and replans where it stands when a direction change goes wrong; the hardware part is the
truck's power and control system on one slide (user, 2026-11-11: STM32H743 below, Jetson above -- the week 7
system diagram redrawn for the boards as ordered, without repeating week 9's power-protection slide) and the
order status. Simulated demos are Isaac renders (user,
2026-10-28). Screen text and narration were written directly (project memory script-md-no-agy).

DRAFT: the Isaac clips are not in assets/ yet. Each one is a labelled placeholder (placeholder()) carrying its
render or restore spec; README.md lists them. Replace placeholder(...) with video(...) once a clip is cut.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
slides = []

ROBOT = 'lightminn/forklift main bcb21c87'
RELOC = f'{ROBOT} docs/validation/2026-10-29-b-p2d-start-relocalization.md'
RELOC_CONSOLE = f'{ROBOT} docs/validation/2026-10-29-b-p2c-console-isaac.md (assets/b-p2c/isaac_awaiting_pick.png)'
CT = f'{ROBOT} docs/validation/2026-11-06-ct-status-survey.md'
WEEK8 = 'week-08/build_deck.py 07 · 09 장 (ISAAC_ROWS: ③ 일자 배치 5회 중 2회 완주, ④ 랜덤 배치 4회 중 1회 완주, ⑤ 트레일러 꺼낸 뒤 운반 중 정지)'
TRAILER = f'{ROBOT} docs/validation/2026-10-31-riib-default-batch2.md (PR #237)'
TRAILER_RX = f'{ROBOT} docs/validation/2026-10-31-riib-exit-prefix-default-batch.md'
CUSP = f'{ROBOT} docs/validation/2026-11-04-return-cusp-replan-reregistration-results.md'
CUSP_RC = f'{ROBOT} docs/validation/2026-11-02-return-cusp-replan-batch.md'
TEAM_PCB = '팀 메인보드 자료 (9주차 SOURCES.md: PCB 배치도 앞면, 외곽 114.173 × 91.567 mm)'
TEAM_EDA = '팀 EasyEDA 프로젝트 Forklift 의 Motor Board 회로도 (온라인 프로젝트 백업 2026-10-27 06:03 판)'
MCU_LINK = f'{ROBOT} docs/interfaces/2026-10-22-mcu-link-contract.md'
FW_CORE = f'{ROBOT} docs/design/2026-10-22-mcu-firmware-core.md'

# line colours of the system diagrams: week 7's 12 V / 5 V / signal colours, 19 V added
P12, P5, P19, SIG, EDGE = '#d64541', '#e08a1e', '#7b4fb5', '#2f74c0', '#8c97a3'


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


def placeholder(name, what, spec, cap=None, ratio='1160 / 660', cls='shot'):
    """DRAFT ONLY: a clearly marked box where an Isaac clip goes (name = the planned assets/ file)."""
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="{cls} ph11"><div class="ph11-box" style="aspect-ratio:{ratio}">'
            f'<b>영상 자리 · {escape(name)}</b><span>{what}</span><small>{spec}</small></div>{c}</figure>')


def lgd(*items):
    """Legend: (kind, colour, text), kind line / ring (week 8's path colours)."""
    out = []
    for kind, colour, text in items:
        if kind == 'ring':
            sw = f'<span class="sw ring" style="border-color:{colour}"></span>'
        elif kind == 'box':
            sw = f'<span class="sw boxo" style="border-color:{colour}"></span>'
        elif kind == 'dash':
            sw = f'<span class="sw dash" style="border-color:{colour}"></span>'
        else:
            sw = f'<span class="sw ln" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="lgd7">{"".join(out)}</div>'


PATHS = (('line', '#8fd0dc', '접근 경로'), ('line', '#e8dc78', '운반 경로'), ('line', '#cdb6dd', '복귀 경로'),
         ('ring', '#33ef63', '하역 위치'))


def table(head, rows, cls='comparison h7'):
    h = ''.join(f'<th>{x}</th>' for x in head)
    body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'


# ----------------------------------------------------------------- cover
add('개발 진행 보고', '11주차\n자율 지게차 개발', 20, '',
    """안녕하십니까. 11주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 발표는 지게차가 시뮬레이션에서 스스로 해내게 된 일을 중심으로 말씀드리겠습니다. 시작 위치를 스스로 찾는 기능, 카메라 인식과 SLAM을 켠 연속 이송, 리보틱스 트레일러 장면, 그리고 계획대로 되지 않았을 때 다시 계획하는 동작을 Isaac 영상으로 보여 드리고, 지게차의 전력·제어 계통과 하드웨어 발주 현황, 다음 주 계획으로 마치겠습니다. (전환)""",
    [(RELOC, '시작 위치 찾기'), (CT, '연속 이송'), (TRAILER, '트레일러 장면')], '진행 보고')

# ----------------------------------------------------------------- 1
THUMBS = [
    ('r02_reloc', '시작 위치 찾기', '아무 곳에 놓아도 사전 지도에서 스스로 위치를 찾음'),
    ('t03_queue', '연속 이송', '팔레트 3개를 사람 손 없이 이어서 옮김'),
    ('t04_trailer', '트레일러 장면', '벽으로 막힌 트레일러에서 꺼내 하역까지 완주'),
]


def thumb(name, title, line):
    cap = f'<figcaption><b>{title}</b><br>{line}</figcaption>'
    pic = next((f'{name}{s}' for s in ('_thumb.jpg', '_poster.jpg') if (ROOT / 'assets' / f'{name}{s}').exists()), None)
    if pic:
        return (f'<figure class="shot th11"><img class="media" src="assets/{pic}" '
                f'alt="{escape(title, quote=True)} 영상의 한 장면">{cap}</figure>')
    return (f'<figure class="shot th11">'
            f'<div class="ph11-box" style="aspect-ratio:1160 / 660"><b>썸네일 · {name}</b><span>뒤 장 영상의 한 프레임</span></div>'
            f'{cap}</figure>')


add('이번 주에 달라진 것', '01  이번 주에 달라진 것', 40, f"""
<h2 class="headline">시작 위치 찾기부터 연속 이송, 트레일러 장면까지 시뮬레이션에서 스스로 수행</h2>
<div class="thumbs11 grow">
{''.join(thumb(*t) for t in THUMBS)}
</div>
""",
    """이번 주에 달라진 것을 먼저 한 장으로 정리했습니다. 첫째, 지게차를 지도 위 아무 곳에 놓아도 LiDAR로 주변을 보고 미리 만든 지도에서 자기 위치를 스스로 찾습니다. 둘째, 카메라 인식과 SLAM을 모두 켠 채로 팔레트 세 개를 사람 손 없이 이어서 옮깁니다. 셋째, 8주차에 운반 중 멈췄던 리보틱스 트레일러 장면을 꺼내기부터 하역까지 끝까지 마칩니다. 하나씩 영상으로 보여 드리겠습니다. (전환)""",
    [(RELOC, '4절 판정'), (CT, '요약 2'), (TRAILER, '① 면제 규칙 2')],
    '그림: 뒤 장 영상의 대표 프레임 (초안: 자리 표시)')

# ----------------------------------------------------------------- 2
RELOC_ROWS = [
    ('시험한 시작 위치', '홀 안 84곳'),
    ('사람 개입 없이 위치 확정', '<b>68곳 (81 %)</b>'),
    ('틀린 위치로 출발', '<b>0곳</b>'),
]
add('시작 위치를 스스로 찾음', '02  시작 위치를 스스로 찾음', 70, f"""
<h2 class="headline">아무 곳에 놓인 지게차가 LiDAR 스캔을 사전 지도에 맞춰 시작 위치를 스스로 찾고 출발</h2>
<div class="reloc11 grow">
{video('r02_reloc.mp4', '위에서 본 seed 5 홀. 홀 오른쪽 가운데 아무 곳에 놓인 지게차가 잠시 서 있다가 위쪽 팔레트로 가서 집은 뒤 아래쪽 하역 칸에 내려놓음', '위에서 본 장면')}
{video('r02_console.mp4', '운용 콘솔 지도 화면. 처음에 사전 지도의 파란 벽과 선반 위로 빨간 LiDAR 점이 겹쳐 지게차 위치가 정해지고, 이어서 확대된 화면에서 계획 경로를 따라 팔레트로 이동함', '같은 순간의 콘솔 화면, 빨간 점은 LiDAR 측정')}
</div>
<div class="reloc11b">
{table(['', '결과'], RELOC_ROWS, 'comparison h7 rt11')}
{img('r02_candidates.png', '운용 콘솔 지도 화면. 위쪽 창에 출발 위치 후보 네 개와 지도에 놓기 · 다시 시도 버튼, 지도 위에 후보 1–4 표시', '후보가 여럿이면 운용자가 고름', 'shot cand11')}
</div>
""",
    """첫 번째는 시작 위치를 스스로 찾는 기능입니다. 지금까지는 지게차를 정해진 출발점에 두고 그 위치를 알려 준 뒤 시작했습니다. 이제는 지게차를 지도 위 아무 곳에 놓아도, LiDAR로 본 주변 모양을 미리 만든 지도와 맞춰 보고 자기 위치를 스스로 정한 다음 출발합니다. 왼쪽은 Isaac에서 위에서 본 장면이고, 오른쪽은 같은 순간의 콘솔 화면입니다. 콘솔 지도 위의 빨간 점이 LiDAR가 본 주변인데, 위치를 찾는 순간 이 점들이 지도의 벽과 선반에 겹치고 지게차가 팔레트를 향해 출발합니다. 같은 홀에서 서로 3미터 이상 떨어진 84곳에 지게차를 놓고 시험했고, 그중 68곳, 81퍼센트에서 사람 도움 없이 위치를 정했습니다. 틀린 위치를 맞다고 믿고 출발한 경우는 한 번도 없었고, 위치를 정한 시점의 오차는 중앙값 2센티미터였습니다. 나머지 16곳은 똑같은 선반이 반복되는 구역이라 후보가 여러 개 나온 경우인데, 이때는 아래 그림처럼 콘솔에 후보를 띄우고 운용자가 하나를 고르게 했습니다. (전환)""",
    [(RELOC, '3절 검증 세계(공장 배치 seed 5, 지도 3edf24b0), 4절 판정: 유효 84(시작 93 중 무효 9), 성공 68/84 = 81.0 %, 틀림 · 부정확 0/0 (시작 68), 운용자 요청 16, 시작 시점 위치 오차 중앙값 2.0 cm · p95 4.3 cm, 실패 16곳 모두 홀 남쪽 반복 선반 구역; 시작 간격 3 m'),
     (RELOC_CONSOLE, '후보 표시 · 두 번 눌러 고르기 화면 (B-P2c 첫 세션, val3_000, 후보 4개; 후보 버튼이 지도 위에 겹치던 첫 판 화면)'),
     ('영상', '시연 렌더는 F1 차단을 개발 설정으로 끈 실행(F1_AUTONOMY=allow, 총괄 2026-11-10 — 시뮬 개발 실행 한정); ws1 test_runs/live/deck11 (README.md 영상 목록)')],
    '영상: Isaac Sim 탑뷰 (8배속)와 운용 콘솔 녹화 (같은 배속), 그림: 후보 선택 화면 (val4_077 렌더)')

# ----------------------------------------------------------------- 3
CT_ROWS = [
    ('일자 배치', '1개씩, 5회 중 2회 완주', '<b>3개 연속, 4회 중 4회</b>'),
    ('랜덤 배치', '1개씩, 4회 중 1회 완주', '<b>3개 연속, 4회 중 3회</b>'),
    ('실행 방식', '팔레트마다 따로 실행', '<b>한 번 실행으로 3개 연속</b>'),
]
add('인식·SLAM 켠 연속 이송', '03  인식·SLAM 켠 연속 이송', 60, f"""
<h2 class="headline">카메라 인식과 SLAM을 켠 채 팔레트 3개 연속 이송, 8회 중 7회 사람 개입 없이 완주</h2>
<div class="ct11 grow">
{video('t03_queue.mp4', '위에서 본 일자 배치 장면. 왼쪽 흰 구역에 놓인 팔레트 세 개를 하나씩 집어 오른쪽 하역 칸의 초록 원 자리에 차례로 내려놓고 매번 출발 위치로 돌아옴')}
<div class="stack tr11r">
{table(['', '8주차', '지금'], CT_ROWS, 'comparison h7 ctt11')}
{lgd(*PATHS)}
</div>
</div>
""",
    """두 번째는 연속 이송입니다. 8주차에는 카메라 인식과 SLAM을 켜면 팔레트 하나를 옮기는 것도 일자 배치에서 다섯 번 중 두 번, 랜덤 배치에서 네 번 중 한 번만 끝까지 갔고, 연속 이송도 팔레트마다 실행을 따로 했습니다. 두 번째 팔레트는 첫 번째가 이미 하역 칸에 놓인 장면을 미리 만들어 두고 거기서 새로 시작하는 식이었습니다. 이번에는 콘솔 작업 대기열에 팔레트 세 개를 넣어 두고, 사람이 손대지 않은 채 인식부터 하역, 복귀까지 세 번을 이어서 하게 했습니다. 일자 배치는 네 번 모두, 랜덤 배치는 네 번 중 세 번 세 개를 다 옮겼습니다. 남은 한 번은 랜덤 배치의 두 번째 팔레트 앞에서 삽입 직전 재관측이 멈춘 경우입니다. 왼쪽 영상은 일자 배치에서 세 개를 차례로 옮기는 장면입니다. (전환)""",
    [(CT, '요약 2: 운영 팔 O6(학습 인식 + 운영 기본 여섯) 4 세션 중 3, O0(라이브 현재 기본) 4 세션 중 4 가 세 임무 완주; 장면 line_m · random_m × seed 0 · 1, 등록 지도 위치 추정, 콘솔 대기열(ct1_queue.sbatch SCENARIO=queue); 막은 실패 O6 random_m s0 P-5:D-2 근접 캡처 후보 없음. 결정 모드 D · D′ 20 세션은 표에 넣지 않음'),
     (WEEK8, '8주차 수치는 riib 장면(line_1–3 · random_1–3)의 팔레트 하나 임무; 이번은 line_m · random_m 세 임무 세션이라 단위가 다름(표의 1개씩 · 3개 연속으로 구분)'),
     ('영상', 'ws1 test_runs/live/deck11/r_bcb21c87/s/d11_queue_line/live/epoch_1/run/transport.mp4 (잡 17491, 스냅숏 deck11_bcb21c87, 세 임무 done) 를 1000 × 720 at x 180 으로 잘라 12배속')],
    '영상: Isaac Sim 탑뷰 (12배속)')

# ----------------------------------------------------------------- 4
TR_ROWS = [
    ('장면', '좌우가 벽으로 막힌 트레일러 안 팔레트 한 줄'),
    ('8주차', '팔레트를 꺼낸 뒤 운반 중 정지'),
    ('지금', '<b>5회 중 5회 하역까지 완주</b>'),
]
add('리보틱스 트레일러 장면 완주', '04  리보틱스 트레일러 장면 완주', 50, f"""
<h2 class="headline">트레일러 안 팔레트를 꺼내 입구를 빠져나와 하역까지 5회 모두 완주</h2>
<div class="tr11 grow">
{video('t04_trailer.mp4', '위에서 본 트레일러 장면. 위쪽 트레일러 안의 팔레트를 집어 후진으로 입구를 빠져나온 뒤 오른쪽 아래 하역 칸에 내려놓고 출발 위치로 돌아옴')}
<div class="stack tr11r">
{table(['', '내용'], TR_ROWS, 'comparison h7 trt11')}
{lgd(*PATHS)}
</div>
</div>
""",
    """세 번째는 리보틱스가 보낸 시연 시나리오 가운데 트레일러 장면입니다. 좌우가 벽으로 막힌 트레일러 안에 팔레트가 한 줄로 실려 있고, 지게차가 들어가 팔레트를 집은 뒤 좁은 입구를 빠져나와 하역 칸까지 옮겨야 합니다. 8주차에는 팔레트를 꺼낸 뒤 입구를 나오는 단계에서 멈췄습니다. 지금은 같은 장면을 다섯 번 돌려 다섯 번 모두 하역과 복귀까지 마쳤습니다. 영상은 팔레트를 싣고 입구를 빠져나와 하역하는 장면입니다. (전환)""",
    [(TRAILER, '① 면제(B) 규칙 2: 완주 trailer B 5 · A 0 (seed 0–4), 안전 지표 0; riib 런처 기본에 --exit-prefix-exempt on'),
     (TRAILER_RX, '같은 설정의 앞 배치 rx_6e6d8e1c: trailer B 5/5 완주(tss_diag/rx_sum.json success), 영상은 이 배치의 rx_B_trailer_s0'),
     (WEEK8, '⑤ 트레일러: 꺼낸 뒤 운반 중 정지'),
     ('영상', 'rx_6e6d8e1c/rx_B_trailer_s0/run/transport.mp4 (gdrive ws1-cleanup-20261031-a/t_mp4.tar.zst 에서 꺼냄, md5 be3f7bb0…) 를 520 × 640 at x 420 으로 잘라 4배속')],
    '영상: Isaac Sim 탑뷰 (4배속)')

# ----------------------------------------------------------------- 5
KEYS = [
    ('t05_key1.jpg', '후진으로 방향 전환 지점에 도착', '지게차가 기존 경로를 따라 후진해 전환 지점으로 들어감'),
    ('t05_key2.jpg', '자세가 어긋나 그 자리에 멈춤', '전환 지점에서 방향이 계획과 어긋난 채 멈춤'),
    ('t05_key3.jpg', '멈춘 자리에서 새 경로 계획', '멈춘 위치에서 시작하는 새 경로가 그려짐'),
    ('t05_key4.jpg', '새 경로로 이어서 주행', '새 경로를 따라 다시 출발함'),
]


def keyframe(src, title, alt):
    return (f'<figure class="shot key11"><img class="media" src="assets/{src}" alt="{escape(alt, quote=True)}">'
            f'<figcaption>{title}</figcaption></figure>')


add('막혀도 다시 계획함', '05  막혀도 다시 계획함', 50, f"""
<h2 class="headline">방향 전환 지점에서 자세가 어긋나면 멈춘 자리에서 새 경로를 계획해 계속 주행</h2>
<div class="cu11b grow">
{video('t05_replan.mp4', '위에서 본 좁은 통로 장면의 확대 영상. 위쪽 칸에 팔레트를 내려놓은 지게차가 주황 기존 경로를 따라 후진해 전환 지점에 멈추고, 하늘색 새 경로가 그려진 뒤 그 경로를 따라 다시 출발함', '확대 영상', 'shot vid11')}
<div class="stack cu11r">
{img('t05_overview.jpg', '좁은 통로 장면 전체를 위에서 본 그림. 위쪽에 하역 칸 줄, 가운데에 랙 블록 셋, 오른쪽 위 하역 칸 앞에 지게차, 흰 사각형이 확대 범위', '장면 전체와 확대 범위', 'shot ov11')}
{lgd(('line', '#ff9628', '기존 경로'), ('line', '#28dcf5', '새 경로'), ('box', '#ffffff', '확대 범위'), ('ring', '#33ef63', '하역 위치'))}
</div>
</div>
<div class="keys11">
{''.join(keyframe(*k) for k in KEYS)}
</div>
""",
    """네 번째는 계획대로 되지 않았을 때의 동작입니다. 오른쪽 위가 리보틱스 좁은 통로 장면 전체이고, 흰 사각형이 왼쪽 확대 영상의 범위입니다. 지게차는 위쪽 칸에 팔레트를 내려놓은 뒤 후진으로 빠져나와 방향을 바꾸는데, 아래 네 장면이 그 순서입니다. 첫째, 주황색 기존 경로를 따라 후진해 전환 지점으로 들어갑니다. 둘째, 이번 주행에서는 전환 지점에 도착했을 때 방향이 계획보다 약 6도 어긋나 있어서, 그대로 가지 않고 그 자리에 멈춥니다. 셋째, 멈춘 위치에서 시작하는 새 경로를 다시 계획하고, 하늘색으로 그려진 것이 그 경로입니다. 계획에는 1초가 채 걸리지 않았습니다. 넷째, 새 경로를 따라 다시 출발해 복귀를 마쳤습니다. 예전에는 이런 경우 임무가 실패로 끝났는데, 지금은 이렇게 이어서 진행합니다. (전환)""",
    [(CUSP, '판정 PASS: 복귀 cusp 재계획(--return-cusp-replans 2) 작동 6 실행 모두 설치 뒤 완주, 복귀 cusp 실패 A 4/59 → G 0/64; riib 런처 기본 RETURN_CUSP_REPLANS=2'),
     (CUSP_RC, 'rc_G_aisle_rack_s11: 복귀 cusp 대기 220.82 s(위치 오차 0.020 m, 방향 오차 0.099 rad), 재계획 221.11 s 성공(계획 0.57 s), 완주 (result.json return_cusp_waits · return_cusp_replans)'),
     ('영상 · 그림', 'rc_95e61a74/rc_G_aisle_rack_s11/run/transport.mp4 (md5 6bba6542…) 와 plan_history.json (gdrive ws1-cleanup-20261110-n/n_rc.tar.zst 에서 꺼냄) — Isaac 겹침선은 복귀 경로를 모두 한 색으로 그리므로, 204.7 s 계획(앞 전환점부터)을 주황, 221.1 s 새 계획을 하늘색으로 다시 그림(make_replan.py, 화면 좌표는 Isaac 경로 픽셀에 맞춘 값). 확대 영상은 200–236 s, 219–224 s 는 실제 속도 · 나머지 4배속; 핵심 장면은 218.6 · 221.0 · 221.45 · 223.0 s')],
    '영상: Isaac Sim 탑뷰 확대 (경로 색을 다시 그림), 그림: 장면 전체와 핵심 장면 네 개')

# ----------------------------------------------------------------- 6 power and control system (user, 2026-11-11)
def _markers(prefix, *colours):
    return '<defs>' + ''.join(
        f'<marker id="{prefix}{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in colours) + '</defs>'


def _box(x, y, w, h, title, sub=None):
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{EDGE}" stroke-width="2"/>'
           f'<text x="{x + w / 2}" y="{y + h / 2 + (-4 if sub else 7)}" text-anchor="middle" font-size="21" font-weight="700" fill="#1b1f24">{title}</text>')
    if sub:
        out += f'<text x="{x + w / 2}" y="{y + h / 2 + 22}" text-anchor="middle" font-size="16" fill="#5d6670">{sub}</text>'
    return out


def _wire(prefix, pts, colour, dashed=False, width=4):
    d = ' '.join(f'{x},{y}' for x, y in pts)
    dash = ' stroke-dasharray="10 7"' if dashed else ''
    return f'<polyline points="{d}" fill="none" stroke="{colour}" stroke-width="{width}"{dash} marker-end="url(#{prefix}{colour[1:]})"/>'


def _note(x, y, text, colour='#1b1f24', size=15, bold=False, anchor='middle'):
    w = ' font-weight="700"' if bold else ''
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}"{w} fill="{colour}">{text}</text>'


def _rail(x, y, text, colour):
    """A small badge on a box's top edge: the supply rail that feeds it (same colours as the power strip)."""
    return (f'<rect x="{x}" y="{y}" width="56" height="22" rx="11" fill="{colour}"/>'
            f'<text x="{x + 28}" y="{y + 16}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">{text}</text>')


def system_diagram():
    """Week 7's power-and-control diagram redrawn for the boards as ordered (STM32H743 below, Jetson above).
    Top: who decides what -- the console and the two sensors feed the Jetson (upper control), the Jetson sends
    targets to the STM32H743 (lower control) and gets measurements back, the H743 drives the four DRV8244 and
    reads the four encoders. Bottom strip: the one 12 V battery and the three rails the main board makes; the
    badges on the boxes say which rail feeds them. The protection details are week 9's slide 04 and stay there."""
    W, H, pre = 1180, 404, 'sy11'
    p = [_markers(pre, P12, P5, P19, SIG)]
    # console and sensors -> Jetson
    p.append(_wire(pre, [(196, 38), (248, 38)], SIG))
    p.append(_wire(pre, [(252, 62), (200, 62)], SIG, dashed=True))
    p.append(_wire(pre, [(196, 141), (248, 141)], SIG, dashed=True))
    p.append(_wire(pre, [(196, 233), (248, 233)], SIG, dashed=True))
    # Jetson <-> STM32H743
    p.append(_wire(pre, [(466, 112), (662, 112)], SIG))
    p.append(_wire(pre, [(666, 196), (470, 196)], SIG, dashed=True))
    p.append(_note(566, 64, '목표값', SIG, 17, True) + _note(566, 84, '바퀴 속도 좌·우') + _note(566, 102, '조향각 · 승강 높이'))
    p.append(_note(566, 148, '측정값 · 상태', SIG, 17, True) + _note(566, 168, '속도 · 각도') + _note(566, 186, '전류 · 고장'))
    p.append(_note(566, 229, 'USB 또는 UART', '#5d6670', 15, True) + _note(566, 248, '(연결 방식 결정 전)', '#5d6670'))
    # STM32H743 <-> drivers, motors, encoders
    p.append(_wire(pre, [(880, 38), (976, 38)], SIG))
    p.append(_wire(pre, [(980, 62), (884, 62)], SIG, dashed=True))
    p.append(_note(930, 28, 'PWM · 방향') + _note(930, 83, '전류 · 고장'))
    p.append(_wire(pre, [(1076, 82), (1076, 105)], P12))
    p.append(f'<line x1="1076" y1="174" x2="1076" y2="200" stroke="{EDGE}" stroke-width="3"/>' + _note(1064, 192, '축 회전', '#5d6670', 15, False, 'end'))
    p.append(_wire(pre, [(980, 233), (884, 233)], SIG, dashed=True))
    p.append(_note(930, 223, '펄스 · 각도'))
    p.append(_box(8, 16, 188, 66, '운용 콘솔', 'Wi-Fi 연결'))
    p.append(_box(8, 108, 188, 66, 'RGB-D 카메라', 'RealSense D435i'))
    p.append(_box(8, 200, 188, 66, '2D LiDAR', 'RPLIDAR A2M12'))
    p.append(_box(980, 16, 192, 66, '모터 드라이버', 'DRV8244 × 4') + _rail(1108, 5, '12 V', P12))
    p.append(_box(980, 108, 192, 66, '모터 4개', '바퀴 좌·우, 조향, 승강'))
    p.append(_box(980, 200, 192, 66, '엔코더 4개', '바퀴 2개, 조향, 승강') + _rail(1108, 189, '5 V', P5))
    for x, name, role, items, rail in ((252, 'Jetson', '상위 제어', ('팔레트 인식', '위치 추정', '경로 계획 · 추종'), ('19 V', P19)),
                                       (666, 'STM32H743', '하위 제어', ('바퀴 속도 제어', '조향 · 승강 위치 제어', '명령 끊기면 정지'), ('5 V', P5))):
        cx = x + 107
        p.append(f'<rect x="{x}" y="16" width="214" height="250" rx="6" fill="#fff" stroke="{SIG}" stroke-width="3"/>'
                 + _note(cx, 54, name, '#1b1f24', 24, True) + _note(cx, 79, role, SIG, 17, True)
                 + f'<line x1="{x + 22}" y1="94" x2="{x + 192}" y2="94" stroke="#d5dbe2" stroke-width="2"/>'
                 + ''.join(_note(cx, 137 + 45 * i, t, '#1b1f24', 19) for i, t in enumerate(items))
                 + _rail(x + 150, 5, *rail))
    # power strip
    p.append('<rect x="4" y="288" width="1172" height="112" rx="10" fill="#f7f9fb" stroke="#c3cad3" stroke-width="2" stroke-dasharray="8 6"/>'
             + _note(22, 350, '전원', '#5d6670', 17, True, 'start'))
    p.append(_wire(pre, [(238, 344), (292, 344)], P12))
    p.append(_box(88, 310, 150, 68, '12 V 배터리', '차량 주 전원'))
    p.append(_box(296, 310, 250, 68, '메인보드 전원부', '입력 보호 · 강압 · 승압'))
    for y, col, volt, who in ((321, P12, '12 V', '모터 드라이버 4개 → 모터 4개'),
                              (344, P5, '5 V', 'STM32H743 코어 보드, 센서 보드 (보드에서 3.3 V로 강압)'),
                              (367, P19, '19 V', 'Jetson')):
        p.append(_wire(pre, [(546, y), (606, y)], col))
        p.append(_note(618, y + 6, volt, col, 16, True, 'start') + _note(668, y + 6, who, '#1b1f24', 16, False, 'start'))
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="전력 계통과 제어 계통. 위쪽 제어: 운용 콘솔과 RGB-D 카메라, 2D LiDAR가 '
            f'상위 제어인 Jetson에 연결되고, Jetson이 하위 제어인 STM32H743에 바퀴 속도와 조향각, 승강 높이의 목표값을 보내고 측정값과 상태를 돌려받음. '
            f'STM32H743은 모터 드라이버 네 개에 PWM과 방향 신호를 주고 전류와 고장 신호를 받으며, 드라이버가 모터 네 개를 구동하고, 엔코더 네 개가 펄스와 각도를 '
            f'STM32H743에 보냄. 아래쪽 전원: 12 V 배터리에서 메인보드 전원부를 거쳐 12 V는 모터 드라이버와 모터로, 5 V는 STM32H743 코어 보드와 센서 보드로, '
            f'19 V는 Jetson으로 공급">'
            f'<g font-family="var(--uos-font)">{"".join(p)}</g></svg>')


add('전력·제어 계통', '06  전력·제어 계통', 85, f"""
<h2 class="headline">전원은 12 V 배터리 하나, 제어는 Jetson과 STM32H743 두 층 구성</h2>
<div class="chart7 sys7 grow">
{system_diagram()}
{lgd(('line', SIG, '명령'), ('dash', SIG, '측정값 · 상태'), ('line', P12, '12 V'), ('line', P5, '5 V'), ('line', P19, '19 V'))}
</div>
<div class="takeaway">진행 상태: 통신 규약과 보드 무관 제어 코드는 PC 시험까지 작성, 보드용 코드와 실기 확인은 시작 전</div>
""",
    """하드웨어입니다. 지게차의 전력 계통과 제어 계통을 한 장으로 정리했습니다. 먼저 아래쪽 전원입니다. 전원은 12볼트 배터리 하나이고, 메인보드 전원부가 이를 세 갈래로 나눕니다. 모터 드라이버에는 12볼트를 그대로, STM32H743과 센서 보드에는 5볼트를, Jetson에는 19볼트를 줍니다. 전원부의 보호 회로는 9주차에 말씀드린 그대로입니다. 위쪽이 제어 계통이고, 두 층으로 나눴습니다. 위층인 Jetson은 RGB-D 카메라와 2D LiDAR로 팔레트를 인식하고 위치를 추정한 뒤 경로를 계획합니다. 앞에서 시뮬레이션으로 보여 드린 기능들이 실차에서는 여기서 돌게 되고, 운용 콘솔도 Wi-Fi로 Jetson에 붙습니다. Jetson은 모터를 직접 돌리지 않고, 좌우 바퀴 속도와 조향각, 승강 높이의 목표값만 아래층으로 보냅니다. 아래층인 STM32H743은 목표값을 받아 모터 드라이버 네 개에 PWM과 방향 신호를 주고, 엔코더 네 개를 읽어 목표를 따라가게 제어하며, 측정값과 고장 상태를 Jetson으로 올려 보냅니다. Jetson의 명령이 일정 시간 오지 않으면 STM32가 스스로 차를 세우도록 설계했습니다. 두 층 사이의 통신 규약과 아래층 제어 코드는 보드와 상관없는 부분을 먼저 짜서 PC에서 시험해 두었고, 실제 보드에서는 아직 돌려 보지 않았습니다. 두 보드를 USB로 이을지 UART로 이을지도 아직 정하지 않았습니다. (전환)""",
    [(MCU_LINK, '상태 「초안, 실기기 미검증」; 전송로(USB CDC 또는 UART)는 미정; DRIVE = left · right_wheel_rad_s, steering_rad, lift_m; STATE = 바퀴 엔코더 카운트 · 각속도, 조향각, 승강 위치, 모터 전류 4개, 듀티, 드라이버 상태, 결함 비트; ARMED 에서 명령 마감이 지나면 STOPPING 을 거쳐 DISARMED'),
     (FW_CORE, '2절 층 구조(Jetson forklift_core.mcu_link ↔ MCU link · app · drive ↔ HAL ↔ DRV8244 × 4 · 엔코더 · KTH7801 SPI · ADC), 6절 바퀴 속도 PI · 조향 · 승강 위치 제어, PH/EN 모드(EN/IN1 = PWM, PH/IN2 = 방향), 「설계 초안, 실기기 없음」— 보드 HAL · 실기 검증은 범위 밖'),
     (f'{ROBOT} firmware/README.md', '「지금은 하드웨어와 무관한 C 코어와 호스트 시험만 있다」'),
     (TEAM_EDA, 'STM32 쪽 헤더 U2 · U4 의 신호: L/R/M/H_IN1 · IN2 · CS · DRVOFF · FAULT · IPROPI, MOSI · MISO · CLK, L/R_ENC_A · B · Z, KTH_CLK · MOSI · MISO · CS1 · CS2, USB_OTG_FS_DM · DP, WIFI_TX · RX · RST; MOTOR&SENSOR 쪽: DRV8244SQRYJRQ1 × 4 (VCC), 바퀴 엔코더 차동 입력(CN1 · CN2)과 절대 엔코더 LVDS(RJ1 · RJ2), 커넥터의 5V; POWER 쪽: 「12V BATTERY INPUT → HIGH-SIDE NMOS SWITCH → VCC」, U12 LMR60440 「5V LOGIC SUPPLY」; JETSON_19V 쪽: U20 LM5122 「12V BATTERY → 19V BOOST → JETSON」'),
     ('week-09/build_deck.py 04 장', '전원 경로와 보호 회로의 세부(퓨즈, 입력 보호 문턱, 전류 제한)는 9주차에 발표 — 이 장은 되풀이하지 않고 세 갈래 분배만 적음; 센서 보드가 각자 3.3 V 로 강압'),
     ('week-07/build_deck.py 01 · 02 장', '전원과 제어 구성 계통도(당시 MCU Nucleo STM32H533RE, Jetson 없음)의 문법을 따름; 바퀴 L · R 은 증분 펄스, 조향 M · 승강 H 는 SPI 각도'),
     (f'{ROBOT} docs/hardware.md', 'RGB-D 카메라 RealSense D435i 확정, 2D LiDAR RPLIDAR A2M12 보유, 상위 제어기 Jetson, 하위 제어 MCU STM32H743VIT6 (WeAct Studio MiniSTM32H7xx)'),
     ('week-08/build_deck.py 02 장', '운용 콘솔은 Jetson 이 Wi-Fi AP 가 되어 1:1 로 연결'),
     ('사용자 (2026-11-11)', '전력 · 제어 계통을 11주차에 추가, 하위 제어 MCU 는 STM32H743, 상위 제어기는 Jetson; 9주차 발표와 겹치지 않게')],
    '그림: 7주차 전원 · 제어 계통도를 발주한 보드 기준으로 다시 그림')

# ----------------------------------------------------------------- 7
HW_ROWS = [
    ('메인보드', 'STM32H743 코어 보드 장착, 모터 드라이버 4개, 12 V · 5 V · Jetson 19 V 전원', '114.2 × 91.6'),
    ('바퀴 엔코더 (MT6701)', '뒤 바퀴 좌우의 회전 측정', '22.8 × 10.4'),
    ('절대 엔코더 (KTH7801)', '조향 · 승강 각도 측정', '22.8 × 10.4'),
    ('STDS 변환 보드', '절대 엔코더의 SPI 신호를 차동(LVDS)으로 바꿔 메인보드까지 전송', '32.6 × 18.4'),
]
add('부품·PCB 발주 완료', '07  부품·PCB 발주 완료', 45, f"""
<h2 class="headline">9주차에 설계한 메인보드와 엔코더 보드 등 4종의 PCB · 부품 발주 완료</h2>
<div class="hw11b grow">
<div class="pcb11">
{img('h02_board_top.jpg', '메인보드 3D 렌더 앞면. 왼쪽 위와 가운데에 2열 22핀 헤더 두 줄, 오른쪽 위에 RJ 잭 두 개, 아래에 모터 드라이버 네 개와 XT30 모터 커넥터 네 개', '메인보드 3D 렌더', 'shot pcbf')}
{img('h03_layout_top.jpg', '메인보드 PCB 배치도 앞면. 외곽 치수 114.173 mm와 91.567 mm, 2열 22핀 헤더 두 줄, 빨간 구리면 위 배선', '메인보드 PCB 배치도', 'shot pcbf')}
</div>
<div class="stack hw11r">
{table(['보드', '하는 일', '크기 (mm)'], HW_ROWS, 'comparison h7 hwt11b')}
<p class="ship11">PCB와 부품은 11월 20일 발송 예정입니다</p>
</div>
</div>
""",
    """이 계통을 이루는 보드의 발주 현황입니다. 9주차에 설계를 보여 드린 보드 네 종류의 PCB와 부품을 모두 발주했습니다. 왼쪽은 메인보드의 3D 렌더와 PCB 배치도입니다. 메인보드에는 STM32H743 코어 보드를 꽂고, 모터 드라이버 네 개와 12볼트, 5볼트, Jetson용 19볼트 전원이 들어갑니다. 나머지 세 장은 센서 보드입니다. MT6701 바퀴 엔코더 보드는 뒤 바퀴 좌우의 회전을 재고, KTH7801 절대 엔코더 보드는 조향과 승강 각도를 잽니다. STDS 변환 보드는 절대 엔코더의 SPI 신호를 LVDS 차동 신호로 바꿔 메인보드까지 보냅니다. PCB와 부품은 11월 20일에 발송될 예정입니다. (전환)""",
    [(TEAM_PCB, '그림 h02_board_top.jpg(3D 렌더 앞면) · h03_layout_top.jpg(PCB 배치도 앞면), 9주차 자산 그대로'),
     ('week-09/build_deck.py 02–05 장', '메인보드 구성(H743 코어 보드 2×22 헤더, DRV8244 4채널, 12 V → 5 V 강압 · 19 V 승압), 보드 크기 표(메인보드 114.2 × 91.6, MT6701 22.8 × 10.4, KTH7801 22.8 × 10.4, STDS 32.6 × 18.4 mm)'),
     ('week-07/build_deck.py', 'STDS 보드가 KTH7801 의 SPI 를 LVDS 로 전송(SN65LVDS32 수신 · SN65LVDS1 송신)'),
     ('로봇 저장소 docs/references/team-hardware/2026-10-28/ (로컬 전용)', '회로도 · PCB 배치도 · 3D 렌더 · 제작 비용 비교'),
     ('사용자 (2026-11-10)', '9주차에 설계한 보드 4종 모두 발주, 수량은 적지 않음; PCB · 부품 11월 20일 발송 예정')],
    '그림: 팀 메인보드 3D 렌더와 PCB 배치도 앞면 (9주차와 같은 그림)')

# ----------------------------------------------------------------- 8
END_ROWS = [
    ('펌웨어', '보드와 무관하게 짜 둔 통신 코어(mcu-link)를 H743 코어 보드에 올려 PC와 명령 · 상태를 주고받는지 확인, 모터 드라이버(DRV8244) · 엔코더 입력 코드 준비'),
    ('보드 도착 뒤', '조립 → 전원 투입 점검 → 모터 · 엔코더 연결 확인'),
    ('리보틱스 장면', '남은 장면(좁은 통로 rack 에서 꺼내 다른 칸에 넣기, 컨베이어 사이 이송)을 Isaac 에서 진행'),
    ('연속 이송', '랜덤 배치의 남은 실패(두 번째 팔레트 앞 삽입 직전 재관측 정지) 원인 정리'),
]
add('다음 주 계획', '08  다음 주 계획', 45, f"""
<h2 class="headline">보드가 오기 전에 H743 코어 보드로 펌웨어를 먼저 올리고 리보틱스 남은 장면 진행</h2>
{table(['구분', '할 일'], END_ROWS, 'comparison h7 endt11b')}
""",
    """다음 주 계획입니다. 보드는 11월 20일에 발송되므로 다음 주 발표 전에는 받지 못합니다. 그래서 먼저 시판 H743 코어 보드로 펌웨어를 시작하겠습니다. 보드와 상관없이 짜 둔 통신 코어인 mcu-link를 코어 보드에 올려 PC와 명령과 상태를 주고받는지 확인하고, 모터 드라이버 DRV8244와 엔코더 입력 코드도 준비해 두겠습니다. 보드가 도착하면 조립하고 전원부터 점검한 뒤 모터와 엔코더 연결을 확인합니다. 시뮬레이션에서는 리보틱스 시연 장면 가운데 남은 장면, 즉 좁은 통로의 rack에서 팔레트를 꺼내 다른 칸에 넣는 장면과 컨베이어 사이 이송을 Isaac에서 진행하고, 연속 이송에서 남은 실패였던 랜덤 배치 두 번째 팔레트 앞 재관측 정지의 원인을 정리하겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [('사용자 (2026-11-10, 총괄 전달)', '보드가 11-20 발송이라 다음 주 발표 전에는 오지 않음, 코어 보드로 펌웨어 먼저'),
     ('lightminn/forklift PR #84', '보드 무관 C 코어 · mcu-link/1 · mcu_link; 보드 HAL · 툴체인은 아직 시작 전'),
     ('week-08/build_deck.py 06 장', '리보틱스 시나리오: ① 좁은 통로 rack 에서 꺼내 다른 칸에 넣기, ② 컨베이어 사이 이송'),
     (CT, '랜덤 배치 남은 실패: O6 random_m s0 두 번째 임무(P-5:D-2) 근접 캡처 후보 없음')],
    '표: 다음 주 할 일')


TITLE = '11주차 자율 지게차 개발'
TOTAL = 465


def build():
    assert len(slides) == 9, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-11-10 (초안), 전력 · 제어 계통 장 추가 2026-11-11. 시뮬레이션 결과는 모두 Isaac 값이다(SOURCES.md). '
              '하드웨어는 발주까지이고 PCB·부품은 11월 20일 발송 예정이다. 전력 · 제어 계통은 설계 내용이고 실제 보드에서 확인한 값이 아니다. '
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
