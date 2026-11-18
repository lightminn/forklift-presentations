"""Build the week 12 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 12 (rebuilt 2026-11-18 for the talk, 7-8 minutes): answers the week 11 feedback (try the real equipment, test
the self-localization more widely, read papers) and shows how simulation failures since the last deck were fixed.
Order: feedback -> real devices (one slide: the STM32H743 board, the Jetson, the D435i, the A2M12 not yet there) ->
the four fixes in one table (path display line in the camera, loose near arrival, return stop 0.1 mm past the
tolerance, the rigid four-point truck model replaced by a compliant tyre) -> the camera before/after -> the tyre
model (static wheel loads and the S-curve clip) -> start relocalization (table and map) -> narrow aisle -> next week.
Screen text is agy's (Gemini 4 Hydrogen High), written for an audience that does not know the project's history
(project memory deck-self-explanatory-for-outsiders); the narration is written directly (script-md-no-agy).
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
slides = []

ROBOT = 'lightminn/forklift main'
HWDAY = f'{ROBOT} docs/validation/2026-11-17-hw-day.md'
HWRAW = f'{ROBOT} docs/validation/assets/hw-day-2026-11-17/'
FEEDBACK = f'{ROBOT} docs/references/week11_feedback.md (로컬 전용, 저장소 밖 미추적 파일)'
BP1B = f'{ROBOT} docs/validation/2026-10-29-b-p1b-search-budget.md'
BP2D = f'{ROBOT} docs/validation/2026-10-29-b-p2d-start-relocalization.md'
ROM = f'{ROBOT} docs/validation/2026-11-16-reloc-observe-move.md'
ACS = f'{ROBOT} docs/validation/2026-11-16-aisle-short-cusp-arc.md'
ACS_PLAN = f'{ROBOT} docs/plans/2026-11-16-aisle-short-cusp-arc.md'
PFB = f'{ROBOT} docs/validation/2026-11-15-post-fix-baseline.md'
PDI = f'{ROBOT} docs/validation/2026-11-14-path-display-impact.md'
RHT = f'{ROBOT} docs/validation/2026-11-17-return-home-timeout.md'
GBC = f'{ROBOT} docs/validation/2026-11-17-goal-band-cusp-retry.md'
FRAG = f'{ROBOT} docs/validation/2026-11-15-baseline-fragility-summary.md'
F2I = f'{ROBOT} docs/validation/2026-11-18-f2-i-reregistration.md (#575, main 460b3578, 문서 커밋 ec888ef1)'
F2I_RAW = 'ws1 /home/projects/forklift/test_runs/f2i/batch_f2i_22fe89be/ (스냅숏 f2i_22fe89be, 결정 모드, 시뮬-물성 세션)'
SYM = f'{ROBOT} docs/validation/2026-11-17-model-symmetry-check.md (#573) 3 절'
R12 = 'ws1 /home/projects/forklift/test_runs/render12_f7566ed4/ (isaac_array 19683, 스냅숏 r12_f7566ed4, 결정 모드, 시뮬-물성 세션 렌더)'

# overlay colours of the Isaac renders (src/forklift_core/mission/core.py show_path) and the drop ring
C_APPROACH, C_TRANSPORT, C_RETURN, C_DROP, C_OBSERVE = '#0d73ff', '#ffa60a', '#8c33d9', '#22e022', '#33cccc'
MAP_GREEN, MAP_BLUE, MAP_RED, RING = '#22a050', '#2f74c0', '#d64541', '#d64541'

# Screen text of slides 01-08, written by agy (Gemini 4 Hydrogen High, 2026-11-18) from per-slide raw material for an
# audience that does not know the development history; one round sent back (the tyre model's default is "decided", not
# applied yet; "공장 배치 A/B" spelled out); facts checked against the result documents. Speaker keywords inserted 2026-11-18 (user: "기존 덱과 거의 같게 하되 핵심 키워드 몇 개만"): agy, no emphasis, changed keys only.
TXT = {'S01_TITLE': '지난주 피드백과 진행', 'S01_HEADLINE': '실제 장비 첫 연결을 진행하고 공장 장면에서 시작 위치 찾기 시험', 'S01_HEAD': '피드백 | 이번 주 진행 | 쪽', 'S01_ROW1': '모터 등 실제 장비를 사서<br>직접 연결해 볼 것 | 하위 제어 보드, Jetson, 카메라 연결<br>모터와 2D LiDAR는 도착 뒤 연결 | 02', 'S01_ROW2': 'SLAM 자기 위치 찾기를<br>다양한 조건으로 정확히 시험 | 새 공장 배치에서 켜서 출발까지와<br>앞뒤 이동으로 시작 위치 찾기 시험 | 06', 'S01_NOTE': '피드백 외에 03–05쪽은 시뮬레이션 실패 해결, 07쪽은 좁은 통로 개선입니다', 'S02_TITLE': '실제 장비 첫 연결', 'S02_HEADLINE': '하위 제어 보드, Jetson, 카메라 첫 연결에서 통신·제때 응답 확인', 'S02_M_NAME': '하위 MCU STM32H743', 'S02_M_L1': '모터 4개 제어 펌웨어 첫 탑재 (잠금)', 'S02_M_L2': '노트북, Jetson 10분 연결 누락 0', 'S02_M_L3': '명령 왕복 시간 최대 약 10 ms', 'S02_J_NAME': 'Jetson Orin Nano Super', 'S02_J_L1': '팔레트 인식과 경로 계획용 컴퓨터', 'S02_J_L2': '6코어 최대 부하 5분, 20 ms 명령 간격', 'S02_J_L3': '최대 29.6 ms (80 ms 미만 통과)', 'S02_D_NAME': 'RealSense D435i', 'S02_D_L1': '팔레트 찾는 카메라와 관성 센서', 'S02_D_L2': 'Jetson에 연결해 2분간 기록', 'S02_D_L3': '자이로 400, 가속도 200 Hz 수신', 'S02_L_NAME': 'RPLIDAR A2M12', 'S02_L_L1': '주변 모양 읽는 2D LiDAR 센서', 'S02_L_L2': '장비 미도착으로 아직 연결 못 함', 'S02_L_L3': '도착하면 노트북과 Jetson에 연결', 'S02_BAND': '모터와 엔코더 연결은 메인보드와 부품이 11월 20일에 발송된 뒤 진행합니다.', 'S03_TITLE': '시뮬레이션 실패 해결', 'S03_HEADLINE': '시뮬레이션 실패 세 가지의 원인을 찾아 고치고 같은 조건에서 개선 확인', 'S03_CAPTION': '세 사례 모두 수정 전후를 같은 장면과 조건으로 다시 돌려 비교', 'S03_HEAD': '지난번 실패 | 원인 | 고친 것 | 같은 조건 전후', 'S03_ROW1': '팔레트 바로 앞에서<br>다시 볼 때 인식 실패 | 계획 경로 표시선이<br>카메라 영상에 찍힘 | 표시선을 운용 화면에만<br>그려 카메라에서 제외 | 40회 중 완주 34→36회<br>인식 실패 1→0회', 'S03_ROW3': '복귀 목표 8.1 mm 옆에서<br>34초 넘게 서다 시간 초과 | 8 mm 안이어야 도착인데 0.1 mm<br>차로 안 됐고 대처 규칙 없음 | 이런 정지를 감지해<br>그 자리서 경로 다시 계획 | 확인한 장면 1곳에서<br>시간 초과가 완주로 바뀜', 'S03_ROW4': 'S자 운반 중 경로 이탈<br>방향 전환 시 각도 어긋남 | 네 바퀴 한 점 접촉 모형이라<br>무게 쏠리고 덜 돎 | 무게에 눌리는 순응 타이어<br>모형으로 바꿔 기본 적용 완료 | 13가지 중 완주 10→13<br>하역 오차 16.0→4.5 mm', 'S04_TITLE': '인식 카메라 전후 비교', 'S04_HEADLINE': '카메라 영상에 찍히던 경로 표시선을 빼 팔레트 인식 방해를 없앰', 'S04_LEFT': '고치기 전, 선이 찍혀 입구 폭 오인', 'S04_RIGHT': '고친 뒤, 선이 빠져 팔레트만 보임', 'S04_LEG_RING': '찍힌 계획 경로 표시선', 'S05_TITLE': '순응 타이어 차체 모형', 'S05_HEADLINE': '순응 타이어 모형으로 네 바퀴 무게를 고르게 해 S자 경로 이탈 해결', 'S05_LEFT': '이전 모형, 111초에 경로 벗어남', 'S05_RIGHT': '순응 타이어, 118초쯤 하역 도착', 'S05_END_LEFT': '경로 이탈', 'S05_END_RIGHT': '하역 도착', 'S05_CHART_TITLE': '빈차 정지 때 네 바퀴가 받는 힘 (N)', 'S05_GROUP_OLD': '이전 모형', 'S05_GROUP_NEW': '순응 타이어', 'S05_WHEEL_FL': '앞왼', 'S05_WHEEL_FR': '앞오', 'S05_WHEEL_RL': '뒤왼', 'S05_WHEEL_RR': '뒤오', 'S05_NOTE1': '이전은 대각선으로 쏠렸고 순응 타이어는 좌우 고름', 'S05_NOTE2': '실제 회전이 명령에 더 가까워짐', 'S05_LEG_TRANSPORT': '운반 경로', 'S05_LEG_APPROACH': '접근 경로', 'S05_LEG_OBSERVE': '팔레트 관측 경로', 'S05_LEG_DROP': '하역 위치', 'S05_BAND': '순응 타이어는 시뮬레이션 기본 적용을 마쳤으며, 눌림 정도는 11월 20일 실제 차량 측정으로 확인합니다.', 'S06_TITLE': '시작 위치 찾기 시험', 'S06_HEADLINE': '라이다로 시작 위치 스스로 찾아 84곳 중 68곳(81 %) 성공, 잘못 찾은 곳 0곳', 'S06_FIG_CAPTION': '앞뒤 이동 시험, 못 찾은 곳은 짐이 반복되는 아래쪽', 'S06_LEG_GREEN': '제자리에서 스스로 찾음 67곳', 'S06_LEG_BLUE': '앞뒤로 움직여 찾음 2곳', 'S06_LEG_RED': '못 찾아 사람이 골라 줌 14곳', 'S06_HEAD': '시험 | 어떻게 시험했나 | 스스로 위치 찾음 | 잘못 찾음', 'S06_ROW2': '켜서 출발까지 | 어디인지 알려 주지 않고 켠 뒤<br>라이다로 스스로 위치를 찾고<br>맞는지 확인한 뒤 출발까지 진행 | 84곳 중 68곳 (81 %)<br>오차 중앙값 2 cm | 0곳', 'S06_ROW3': '앞뒤 이동 | 제자리에서 못 찾으면 앞뒤로<br>30 cm 움직여 주변을 다시 봄<br>(20초 더 걸려 기본으로는 안 씀) | 16곳 중 2곳 더 찾음<br>(67곳 → 69곳) | 0곳', 'S06_BAND': '실제 차량은 좌표와 방향을 지도에 미리 등록한 정해 둔 시작 자리에서 출발합니다.', 'S07_TITLE': '좁은 통로 경로 개선', 'S07_HEADLINE': '방향 전환점 앞 짧은 곡선을 피하게 해 운반 중 다시 계획을 절반으로', 'S07_VID_TOP': '기존 경로', 'S07_VID_BOTTOM': '개선 경로', 'S07_VID_CAPTION': '기존은 짧은 곡선에서 두 번 다시 계획, 개선은 한 번 통과', 'S07_HEAD': '항목 | 기존 | 개선', 'S07_ROW1': '전환점 앞 0.6 m 미만 곡선 | 90개 | 18개', 'S07_ROW2': '운반 중 경로 다시 계획 | 16회 | 8회', 'S07_ROW3': '무작위 배치 10가지 완주 | 9회 | 9회', 'S07_NOTE1': '짧은 곡선을 피하는 설정은 검증한 좁은 통로 장면에서만 기본으로 켬', 'S07_LEG_APPROACH': '접근 경로', 'S07_LEG_TRANSPORT': '운반 경로', 'S07_LEG_RETURN': '복귀 경로', 'S07_LEG_DROP': '하역 위치', 'S08_TITLE': '다음 주 계획', 'S08_HEADLINE': '11월 20일 실제 차량을 측정하고 LiDAR 연결과 모터 구동을 시험', 'S08_HEAD': '구분 | 할 일', 'S08_ROW1': '실제 차량 측정 | 직진 틀어짐, 조향량, 재출발을 센서와 줄자로 재어 타이어 모형 맞춤', 'S08_ROW2': '2D LiDAR 연결 | RPLIDAR A2M12 오면 노트북과 Jetson에 연결해 스캔 확인', 'S08_ROW3': '모터 구동 시험 | 메인보드와 부품 도착 후 모터, 엔코더를 하위 제어 보드로 구동', 'S06_TABLE_INTRO': '지게차를 켰을 때 라이다로 주변을 보고 지도에서 자기 위치를 찾는 시험 (개발에 쓰지 않은 새 공장 배치)', 'S04_FAIL_INTRO': '고친 뒤 40회 중 남은 실패 4회 원인 (모두 무작위 물건 배치 장면)', 'S04_FAIL_HEAD': '무엇이 왜 실패했나 | 그 뒤', 'S04_FAIL_ROW1': 'S자 운반 중 바퀴 한 점 접촉으로 덜 돌아 경로 이탈 | 순응 타이어로 바꿔 완주 (05장)', 'S04_FAIL_ROW2': '팔레트 가까이 다시 보러 가다 시간 초과, 원인은 모름 | 타이어 바꾼 뒤 완주 (원인 확인 못함)', 'S04_FAIL_ROW3': '복귀 목표 8.1 mm 옆에서 8 mm 기준에 못 들어 시간 초과 | 정지 감지 재계획으로 완주 (03장)', 'S04_FAIL_ROW4': '운반 중 방향 바꿀 자리가 장애물 칸과 겹쳐 경로 다시 짜기 거부 | 아직 고치지 못함'}


def T(k):
    return TXT[k]


def cells(k):
    return tuple(c.strip() for c in TXT[k].split(' | '))


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def img(src, alt, cap=None, cls='shot'):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="{cls}"><img class="media" src="assets/{src}" '
            f'alt="{escape(alt, quote=True)}">{c}</figure>')


def lgd(*items):
    """Legend: (kind, colour, text), kind line / ring / dash / dot."""
    out = []
    for kind, colour, text in items:
        if kind == 'ring':
            sw = f'<span class="sw ring" style="border-color:{colour}"></span>'
        elif kind == 'dash':
            sw = f'<span class="sw dash" style="border-color:{colour}"></span>'
        elif kind == 'dot':
            sw = f'<span class="sw dt" style="background:{colour}"></span>'
        else:
            sw = f'<span class="sw ln" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="lgd7">{"".join(out)}</div>'


def table(head, rows, cls='comparison h7'):
    h = ''.join(f'<th>{x}</th>' for x in head)
    body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'


def device(src, alt, key, cls=''):
    lines = [T(f'{key}_L{i}') for i in (1, 2, 3) if T(f'{key}_L{i}') != '없음']
    body = ''.join(f'<p>{x}</p>' for x in lines)
    return f'<div class="dev12{cls}">{img(src, alt, None, "shot")}<h3>{T(key + "_NAME")}</h3>{body}</div>'


LOADS_OLD, LOADS_NEW = (115.3, 33.0, 30.6, 76.1), (74.4, 73.9, 53.2, 53.5)   # FL, FR, RL, RR floor force on each tyre, N


def load_chart():
    """Static floor force on each tyre, rigid four-point model vs compliant tyre (empty truck, flat floor, 1 s mean)."""
    names = (T('S05_WHEEL_FL'), T('S05_WHEEL_FR'), T('S05_WHEEL_RL'), T('S05_WHEEL_RR'))
    W, H, base, top, bw, gap = 560, 230, 170, 26, 44, 12
    scale = (base - top) / 120.0
    p = [f'<line x1="20" y1="{base}" x2="{W - 10}" y2="{base}" stroke="#8c97a3" stroke-width="2"/>']
    for g, (vals, col, gname) in enumerate(((LOADS_OLD, '#9aa3ad', T('S05_GROUP_OLD')), (LOADS_NEW, '#2f74c0', T('S05_GROUP_NEW')))):
        x0 = 40 + g * 270
        for i, v in enumerate(vals):
            x = x0 + i * (bw + gap)
            h = v * scale
            p.append(f'<rect x="{x}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="3" fill="{col}"/>'
                     f'<text x="{x + bw / 2}" y="{base - h - 7:.1f}" text-anchor="middle" font-size="17" font-weight="700" fill="#1b1f24">{v:.0f}</text>'
                     f'<text x="{x + bw / 2}" y="{base + 20}" text-anchor="middle" font-size="15" fill="#3c4650">{names[i]}</text>')
        p.append(f'<text x="{x0 + 2 * (bw + gap) - gap / 2}" y="{base + 46}" text-anchor="middle" font-size="19" font-weight="700" fill="{col}">{gname}</text>')
    aria = (f'네 바퀴가 받는 힘 막대그래프. {T("S05_GROUP_OLD")}: 앞왼 115, 앞오 33, 뒤왼 31, 뒤오 76 N. '
            f'{T("S05_GROUP_NEW")}: 앞왼 74, 앞오 74, 뒤왼 53, 뒤오 54 N')
    return (f'<svg class="diagram ldc12" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(aria, quote=True)}">'
            f'<g font-family="var(--uos-font)">{"".join(p)}</g></svg>')

# ----------------------------------------------------------------- cover
add('개발 진행 보고', '12주차\n자율 지게차 개발', 15, '',
    """안녕하십니까. 12주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 지난주 피드백에 대한 답으로 실제 장비를 처음 연결한 결과와 시작 위치 찾기 시험을 말씀드리고, 그사이 시뮬레이션에서 실패한 사례를 어떻게 고쳤는지 말씀드리겠습니다. (전환)""",
    [(FEEDBACK, '11주차 피드백 원문')], '진행 보고')

# ----------------------------------------------------------------- 1
add(T('S01_TITLE'), '01  ' + T('S01_TITLE'), 30, f"""
<h2 class="headline">{T('S01_HEADLINE')}</h2>
{table(cells('S01_HEAD'), [cells(f'S01_ROW{i}') for i in (1, 2)], 'comparison h7 fb12')}
<p class="note12 fbn12">{T('S01_NOTE')}</p>
""",
    """지난주 발표 뒤 받은 피드백 가운데 두 가지를 이번 주에 진행했습니다. 장비를 실제로 사서 써 볼 것, 그리고 SLAM으로 자기 위치를 찾는 기능을 더 다양하게 시험할 것입니다. 첫째는 하위 제어 보드와 Jetson, 카메라를 실제로 연결한 결과로 2쪽에서, 둘째는 시작 위치 찾기를 조건을 바꿔 시험한 결과로 6쪽에서 말씀드립니다. 그 사이 3쪽부터 5쪽은 시뮬레이션에서 실패한 사례를 고친 내용입니다. (전환)""",
    [(FEEDBACK, '「각종 장비들(ex, 모터) 실제로 사서 뚜다해보고 써볼것 / SLAM을 통한 자기 위치 판정 정확하게등등 다양하게 더 정확하게 테스트 하기」 (나머지 한 항목은 이번 주 진행이 없어 덱에서 뺌 — 사용자 2026-11-18)')],
    '표: 피드백별 이번 주 진행과 해당 장')

# ----------------------------------------------------------------- 2
add(T('S02_TITLE'), '02  ' + T('S02_TITLE'), 70, f"""
<h2 class="headline">{T('S02_HEADLINE')}</h2>
<div class="devs12 dev4 grow">
{device('hw_h743.jpg', 'WeAct STM32H743 코어 보드 윗면. 가운데 STM32H743 칩, 아래쪽에 USB-C 단자, 양옆에 핀 헤더', 'S02_M')}
{device('hw_jetson.jpg', 'NVIDIA Jetson Orin Nano 개발 키트 보드. 검은 방열판과 팬', 'S02_J')}
{device('hw_d435.jpg', 'Intel RealSense 깊이 카메라를 작은 삼각대에 올린 사진', 'S02_D')}
{device('hw_lidar.jpg', 'SLAMTEC RPLIDAR A2 2D 라이다', 'S02_L', ' off12')}
</div>
<div class="takeaway">{T('S02_BAND')}</div>
""",
    """첫 번째 피드백인 실제 장비입니다. 왼쪽부터 하위 제어 보드, 상위 제어 컴퓨터, 카메라, LiDAR입니다. 하위 제어 보드 STM32H743은 상위 컴퓨터가 보낸 목표값을 받아 바퀴와 조향, 포크 승강 모터 네 개를 직접 돌릴 보드입니다. 사진은 팀이 이번에 연결한 보드이고, 우리가 짠 펌웨어를 모터 출력을 잠근 상태로 처음 올렸습니다. 노트북과 Jetson에 각각 10분씩 연결했더니, 10밀리초마다 보내는 상태 메시지를 6만 개 가까이 받는 동안 빠진 것이 하나도 없었고, 명령을 보내고 결과가 돌아오기까지 가장 길어도 10밀리초 남짓이었습니다. 상위 제어 컴퓨터 Jetson은 20밀리초마다 하위 보드로 명령을 보내야 하는데, CPU 여섯 코어 모두에 부하를 걸어도 명령 간격이 가장 길 때 29.6밀리초로, 미리 정한 기준 80밀리초보다 짧았습니다. 카메라 RealSense D435i는 Jetson에 연결해 안에 든 관성 센서를 2분 동안 기록했고 측정이 빠짐없이 들어왔습니다. 2D LiDAR는 아직 장비가 없어 연결하지 못했습니다. 모터와 엔코더는 메인보드와 부품이 11월 20일에 발송되면 연결합니다. (전환)""",
    [(HWDAY, '「H743 링크」: HIL 이미지(출력 잠금), 노트북 600 s · STATE 60,000 · seq 틈 0 · 왕복 p50 9.3 / 최대 10.15 ms · 리셋 0, Jetson 600 s · STATE 59,999 · seq 틈 0 · 왕복 3.97 / 10.26 ms · 리셋 0; 「다리 정체」 MAXN_SUPER 각 300 s: 정지 최대 21.9 ms, 부하(모든 코어) 최대 29.6 ms, 기준 80 ms 미만; 「D435i IMU」 120.2 s 자이로 399.8 Hz · 가속도 200.1 Hz · dropped 0; A2M12 미실시'),
     (f'{HWRAW}jetson/h743_link.txt · jetson/stall/{{idle,load}}/verdict.txt · jetson/imu.txt', '판정 줄로 위 값 확인(2026-11-17)'),
     ('사진', 'hw_h743.jpg 사용자 촬영(EXIF 지움), hw_jetson.jpg NVIDIA 제품 페이지 이미지(© NVIDIA), hw_d435.jpg Wikimedia Commons Marc Auledas CC BY-SA 4.0(D435, 겉모양 D435i 와 같음), hw_lidar.jpg 과제 브리프 3쪽 — SOURCES.md'),
     ('사용자 (2026-11-10)', '메인보드 · 부품 11월 20일 발송 예정')],
    '사진: 팀 촬영(MCU) · 제품 사진, 값: 2026-11-17 실제 장비 측정')

# ----------------------------------------------------------------- 3 the four fixes
add(T('S03_TITLE'), '03  ' + T('S03_TITLE'), 70, f"""
<h2 class="headline">{T('S03_HEADLINE')}</h2>
<p class="panel-h">{T('S03_CAPTION')}</p>
{table(cells('S03_HEAD'), [cells(f'S03_ROW{i}') for i in (1, 3, 4)], 'comparison h7 fx12 fx4')}
""",
    """다음은 시뮬레이션에서 임무가 실패한 사례를 어떻게 고쳤는지입니다. 세 가지 모두 고치기 전과 후를 같은 장면, 같은 조건으로 다시 돌려 비교했습니다. 첫째, 좁은 통로에서 팔레트 바로 앞까지 가서 카메라가 팔레트를 인식하지 못한 실패는, 운용 화면에 보여 주려고 그린 경로 표시선이 카메라 영상에도 찍혀서였습니다. 표시선을 카메라에서 빼자 40번 중 완주가 34번에서 36번으로 늘고 인식 실패가 없어졌습니다. 둘째, 출발점으로 돌아오는 마지막에 목표에서 8.1밀리미터 떨어져 멈춘 채 시간이 초과되던 것은, 8밀리미터 안이어야 도착으로 인정하는데 0.1밀리미터 차이로 인정되지 않았고 이렇게 멈춘 경우를 처리하는 규칙이 없어서였습니다. 이런 정지를 감지해 다시 계획하게 해서 완주로 바뀌었는데, 장면 하나에서 확인한 결과입니다. 셋째는 시뮬레이터 자체의 문제였습니다. 차체가 네 바퀴의 한 점씩으로만 바닥에 닿는 모형이라 무게가 한쪽 대각선으로 쏠려 조향이 덜 됐고, 순응 타이어 모형으로 바꿔 같은 조건 13가지의 완주가 10가지에서 13가지가 되었습니다. (전환)""",
    [(PFB, '3.3 R vs S: 같은 스냅숏에서 표시 prim 이 인식 카메라에 안 보임 / 보임, 같은 장면 · seed 40 짝, 결정 모드: 완주 36/40 대 34/40, perception 실패 0 대 1(aisle_rack s2)'),
     (PDI, '표시선 · 목적지 고리가 렌더되는 장면 prim 이라 인식 카메라에 찍힘(#509), 수정 #512; 표시만 끈 진단에서 근접 캡처 거부 → 채택 2/2'),
     (RHT, 'random_1 s24 복귀 끝 옆 8.100 mm(허용 8 mm)에서 약 34.5 s 정지 → 시간 초과'),
     (GBC, '결정 모드 짝 s24: 끔 시간 초과, --goal-creep-band on 완주; riib 런처 기본 켬(#571), 근거 seed 1'),
     (F2I, '덱 목록 13 짝(random_1 s0 · 5 · 7 · 8 · 9 · 12 · 19 · 23, aisle_rack s1 · 2 · 4 · 17 · 18): 완주 10/13 → 13/13, 하역 오차 중앙(두 팔 완주 10 짝) 16.0 → 4.5 mm; 끔 실패 s8(운반 경로 이탈) · s4(좁은 통로 전환점) · s12(관측 시간 초과, 원인 미확인); 나머지 10 짝은 끔에서도 완주(지금 main 에서 재현 안 됨)'),
     (f'{ROBOT} PR #576 (머지 09448ca2)', '순응 타이어(F2) 접촉을 riib · 라이브 런처 기본 켬(러너 기본은 끔, 사용자 결정); smoke riib 3 장면 완주 · 라이브 3/3 (총괄 2026-11-18)'),
     ('재확인', '06 장 세 사례(표시선 aisle_rack s2, 복귀 정체 s24)는 지금 main 에서 모두 완주(F2I 3.3 절); 11주차 연속 이송 랜덤 배치 1 회 실패는 지금 main 라이브 1 회에서 재현 안 됨(고친 사례로 쓰지 않음)')],
    '표: 고치기 전후를 같은 장면 · 같은 조건으로 다시 돌린 비교 (Isaac 시뮬레이션)')

# ----------------------------------------------------------------- 4 camera before/after
add(T('S04_TITLE'), '04  ' + T('S04_TITLE'), 45, f"""
<h2 class="headline">{T('S04_HEADLINE')}</h2>
<div class="cam12 cam4">
{img('s04_cam_before.png', '고치기 전 인식 카메라 화면. 노란 벽 앞 바닥에 팔레트, 화면 아래 가운데에 파란 짧은 선이 찍혀 있고 빨간 동그라미로 표시됨', T('S04_LEFT'), 'shot camf12')}
{img('s04_cam_after.png', '고친 뒤 인식 카메라 화면. 같은 장면, 파란 선이 없음', T('S04_RIGHT'), 'shot camf12')}
</div>
{lgd(('ring', RING, T('S04_LEG_RING')))}
<div class="fail12"><p>{T('S04_FAIL_INTRO')}</p>
{table(cells('S04_FAIL_HEAD'), [cells(f'S04_FAIL_ROW{i}') for i in (1, 2, 3, 4)], 'comparison h7 fl12')}</div>
""",
    """첫 번째 사례를 화면으로 보면 이렇습니다. 왼쪽이 고치기 전, 오른쪽이 고친 뒤의 인식 카메라 화면입니다. 고치기 전에는 빨간 동그라미 안에 계획 경로 표시선이 찍혀 있고, 이 선이 팔레트 앞에 걸리면 팔레트 입구 폭을 잘못 읽어 인식을 거부한 경우가 있었습니다. 고친 뒤에는 선이 보이지 않습니다. 고친 뒤에도 40번 중 4번은 실패했고, 넷 다 무작위로 물건을 놓은 장면이었습니다. 첫째는 S자로 운반하다 경로를 벗어난 경우로, 차체 모형이 덜 돌았기 때문이고 뒤에서 볼 순응 타이어로 바꾼 뒤 완주했습니다. 둘째는 팔레트를 가까이서 다시 보러 가다 시간이 다 된 경우인데, 원인은 아직 확인하지 못했습니다. 순응 타이어로 다시 돌리니 완주했지만 그것이 원인이라는 근거는 없습니다. 셋째는 앞 표 둘째 행의 복귀 끝 정지로, 정지를 감지해 다시 계획하게 고쳤습니다. 넷째는 운반 중 방향을 바꿀 자리가 장애물 칸과 겹쳐 경로를 다시 짜지 못한 경우로, 아직 고치지 못했습니다. (전환)""",
    [(R12, 'pdBefore_aisle_rack_s2(표시선이 카메라에 보이는 진단 설정) · pdAfter_aisle_rack_s2(기본)의 run/perception_capture_2_rgb.png(근접 캡처) — 두 실행 모두 완주, 그림은 선이 찍히는 모양을 보이는 것'),
     (PDI, '표시가 있을 때 근접 캡처 opening_width_mismatch 거부 — 원고의 「입구 폭을 잘못 읽어」'),
     ('편집', '(160, 140)–(560, 330) 을 잘라 2 배 확대, 고치기 전 그림에 빨간 동그라미(선 자리)'),
     (PFB, '남은 실패 표: 40 짝 집합 R 36/40, 실패 분류 planning 1 · tracking 3, 모두 random_1(30/30 중 26) — 짝 차이 표의 random_1 s11 scene_replan_refused:cusp_pose:blocked:occupied(운반), s24 Tracking timeout in return_home'),
     (f'{ROBOT} docs/plans/2026-11-18-f2-i-reregistration.md 1 절', '#539 R 의 나머지 실패: s8 Tracking failed in transport(cross_track), s12 Tracking timeout in observe, s11 · s49 cusp_pose:blocked:occupied, s24 return_home 시간 초과(목표 크리프, #571) — s49 는 40 짝 밖'),
     (F2I, '이후: s8 O 실패 · F2 완주 1.8 mm, s12 O 실패(같은 사유) · F2 완주 3.4 mm 원인 미확인(조향 S 자 아님), s24 는 RHT · GBC 의 정지 감지 재계획(--goal-creep-band, riib 기본 #571); s11 은 고친 기록 없음')],
    '그림: Isaac Sim 인식 카메라 근접 캡처, 왼쪽 고치기 전 · 오른쪽 고친 뒤')

# ----------------------------------------------------------------- 5 tyre model
add(T('S05_TITLE'), '05  ' + T('S05_TITLE'), 55, f"""
<h2 class="headline">{T('S05_HEADLINE')}</h2>
<div class="ty5 grow">
<figure class="shot vw12b"><video class="media" src="assets/s05_tyre.mp4" poster="assets/s05_tyre_poster.jpg" autoplay loop muted playsinline aria-label="위에서 본 두 영상. 팔레트를 실은 지게차가 주황 운반 경로를 따라 S자로 휘어 오른쪽 위 하역 칸으로 감. 왼쪽 이전 모형은 마지막 굽이에서 경로 바깥으로 밀려나 111초에 멈춤, 오른쪽 순응 타이어 모형은 경로대로 돌아 하역 칸에 도착"></video></figure>
<div class="stcap12 ty5c"><span>{T('S05_LEFT')}</span><span>{T('S05_RIGHT')}</span></div>
<div class="ty5b">
<div class="stack ty5chart"><p class="panel-h">{T('S05_CHART_TITLE')}</p>{load_chart()}</div>
<div class="stack ty5n"><p>{T('S05_NOTE1')}</p><p>{T('S05_NOTE2')}</p>
{lgd(('line', C_TRANSPORT, T('S05_LEG_TRANSPORT')), ('line', C_APPROACH, T('S05_LEG_APPROACH')), ('line', C_OBSERVE, T('S05_LEG_OBSERVE')), ('ring', C_DROP, T('S05_LEG_DROP')))}</div>
</div>
</div>
<div class="takeaway">{T('S05_BAND')}</div>
""",
    """세 번째 사례인 차체 모형입니다. 위 영상은 같은 장면을 같은 조건으로 돌린 것으로, 왼쪽이 이전 모형, 오른쪽이 순응 타이어 모형입니다. 팔레트를 실은 지게차가 주황색 경로를 따라 S자로 휘어 하역 칸으로 가는데, 이전 모형은 마지막 왼쪽 굽이에서 경로 바깥으로 밀려나 111초에 실패하고, 순응 타이어 모형은 경로대로 돌아 118초쯤 하역 칸에 도착합니다. 아래 그래프가 그 이유입니다. 차를 세워 두었을 때 이전 모형은 앞왼쪽과 뒤오른쪽 바퀴에 무게가 쏠렸고, 순응 타이어 모형은 좌우가 고르게 받습니다. 조향을 끝까지 꺾었을 때 실제로 도는 정도도 비교할 수 있는 12가지 모두 명령에 더 가까워졌습니다. 다만 이 조향 비교는 초속 0.4미터보다 느린 구간에서만 확인한 것이고, 조향 조건 12가지 중 3가지는 여전히 명령의 95퍼센트에 못 미치게 덜 돕니다. 순응 타이어는 시뮬레이션 실행의 기본 설정으로 적용을 마쳤고, 적용 뒤 확인 실행도 모두 완주했습니다. 타이어가 눌리는 정도는 추정값이라 11월 20일 실제 차량 측정으로 확인하겠습니다. 실시간으로 돌린 관찰에서도 이전 모형은 세 번 중 한 번 S자 구간에서 벗어났고 순응 타이어는 세 번 모두 완주했지만, 이것은 판정용 시험은 아닙니다. (전환)""",
    [(F2I, '3.3 · 4 절: 덱 목록 13 짝 조향 포화 구간 달성 곡률 비 12 짝(s12 제외) 0.851–0.955 → 0.918–0.964, 12 짝 모두 개선, 켬 중앙 0.960, 켬에서 0.95 미만 3 짝(s9 · s19 · s23); 고속 층(0.4 m/s 이상) 노출 0 s — 저속 포화 구간 한정(assets/f2i-reregistration/mechanism_deckset.json.gz md5 27feb5f2… 로 재계산)'),
     (SYM, '이전 모형 정지 하중 D0: 앞왼 115.3 · 앞오 33.0 · 뒤왼 30.6 · 뒤오 76.1 N (빈차, 평평한 바닥, 구동 정지 · 조향 고정, 1 s 평균, 합 약 255 N = 26 kg)'),
     (F2I, '4 절 탐침: 순응 타이어 74.4 · 73.9 · 53.2 · 53.5 N, 반복 같음; 타이어 강성 140 kN/m 는 추정값'),
     (F2I_RAW, 'video/f2iw_O_random_1_s8/run/transport.mp4 (111.3 s, sha256 8cb8c30eedc098240b288e2e621efb0e2d2bedb22d82719570ef85e08ca2aa34, 운반 중 경로 이탈) · video/f2iw_F2_random_1_s8/run/transport.mp4 (165.3 s, sha256 3d276fd13363e3051d9cf0a26926abbe8496dc61f1d8d41f808d2afaa86aa5ac, 완주), 결정 모드 · VIDEO=off 짝과 궤적 같음; 시뮬 40 s 부터 잘라 좌우로 붙여 4 배속, 시뮬 시각과 끝 라벨(agy 문구) 겹침'),
     (f'{ROBOT} PR #576 (머지 09448ca2)', 'riib · 라이브 런처 기본 켬, smoke riib 3 장면 완주 · 라이브 3/3'), ('총괄 (2026-11-18)', '운영(실시간) 모드 비용 측정 관찰: 이전 모형 3 번 중 1 번 S 자 이탈, 순응 타이어 3/3 완주 — 판정 아님')],
    '영상: Isaac Sim 탑뷰(4배속), 그래프: 시뮬 정지 하중(빈차)')

# ----------------------------------------------------------------- 6 start relocalization
add(T('S06_TITLE'), '06  ' + T('S06_TITLE'), 60, f"""
<h2 class="headline">{T('S06_HEADLINE')}</h2>
<div class="rel12 rel6 grow">
<div class="map12">
{img('s06_map.png', 'SLAM으로 만든 홀 지도. 검은 벽과 회색 네모 짐 더미 사이에 출발점이 색 점으로 찍혀 있음. 초록 점이 대부분이고, 파란 점 두 개, 빨간 점 14개는 모두 지도 아래쪽 절반에 있음', None, 'shot mapf12')}
<div class="maplg12"><p>{T('S06_FIG_CAPTION')}</p>
{lgd(('dot', MAP_GREEN, T('S06_LEG_GREEN')), ('dot', MAP_BLUE, T('S06_LEG_BLUE')), ('dot', MAP_RED, T('S06_LEG_RED')))}</div>
</div>
<div class="stack">
<p class="rlin12">{T('S06_TABLE_INTRO')}</p>
{table(cells('S06_HEAD'), [tuple(c.replace(' 2 cm', ' 2&nbsp;cm') for c in cells(f'S06_ROW{i}')) for i in (2, 3)], 'comparison h7 rl12 rl6')}
</div>
</div>
<div class="takeaway">{T('S06_BAND')}</div>
""",
    """두 번째 피드백인 SLAM 자기 위치 찾기입니다. 지게차는 SLAM으로 미리 만든 지도 위에서, LiDAR로 본 주변 모양을 지도와 맞춰 자기 위치를 찾습니다. 시험한 장면은 개발에 쓰지 않은 새 공장 배치입니다. 지게차를 출발점 84곳에 놓고 어디인지 알려 주지 않은 채 켰습니다. 지게차가 스스로 위치를 찾고 맞는지 확인한 뒤 출발까지, 실제로 켜서 출발하는 순서 그대로 해 봤고 68곳에서 위치를 정했습니다. 위치를 정한 곳의 오차는 중앙값 2센티미터입니다. 이번 주에는 여기에 제자리에서 못 찾으면 앞뒤로 30센티미터 움직여 주변을 다시 보는 동작을 더했는데, 제자리에서 못 찾은 16곳 중 2곳만 더 찾았고 20초가 더 걸려 기본으로는 쓰지 않습니다. 지도의 파란 점이 이 두 곳입니다. 두 시험은 그 사이 다른 설정이 바뀌어서 68과 67을 서로 비교하지는 않습니다. 두 시험 모두 틀린 위치를 맞다고 정한 경우는 없었습니다. 왼쪽 지도에서 빨간 점, 즉 끝내 위치를 정하지 못한 곳은 모두 비슷한 짐 더미와 선반이 반복되는 아래쪽에 모여 있습니다. 그래서 실차는 바닥에 시작 자리를 표시하고 그 좌표와 방향을 지도에 등록해 둔 뒤, 그 자리에서 출발하도록 정했습니다. (전환)""",
    [(BP1B, '(화면에서 뺌, 사용자 2026-11-18) 공장 배치 seed 4 새 조사 지도, 유효 84 곳, 성공 69 (82 %), 틀린 확정 0 · 부정확 0 — 기록 스캔으로 정합기 평가(차 움직이지 않음)'),
     (BP2D, '공장 배치 seed 5, Isaac 출발 재위치: 유효 84, 성공 68 (81.0 %), 틀림 0, 위치 오차 중앙값 2.0 cm'),
     (ROM, '같은 지도 · 출발 목록, 유효 84: 제자리 67 → 이동 69, 틀린 확정 0, 이동 비용 중앙값 20.9 s, 승격 안 함 · 실차는 정해 둔 시작 자리(known start); B-P2d 와 설정 차이(1 절)로 68 과 67 을 비교하지 않음'),
     ('지도 그림', 'B-P2d 조사 지도 hall_s5b_G0 (map 3edf24b0, Drive ws1-cleanup-20261110-an/an_f1.tar.zst 에서 grid.npz · manifest.json 만 꺼냄) 위에 val_s5.json 출발 자세와 reloc-observe-move/compare.json 결과(make_map.py): 제자리 67, 이동 뒤 2, 미확정 14, val4_092 제외'),
     ('총괄 (2026-11-17)', '「정해 둔 시작 자리」 = 바닥에 시작 자리를 표시하고 좌표 · 방향을 지도에 등록, 재위치 탐색 없이 시작')],
    '그림: SLAM 지도 위 출발점별 결과(이동 시험), 표: 시작 위치 찾기 두 시험 (Isaac 시뮬레이션)')

# ----------------------------------------------------------------- 7 narrow aisle
add(T('S07_TITLE'), '07  ' + T('S07_TITLE'), 50, f"""
<h2 class="headline">{T('S07_HEADLINE')}</h2>
<div class="cu12 grow">
<figure class="shot vw12"><div class="vbox12"><video class="media" src="assets/s07_cusp.mp4" poster="assets/s07_cusp_poster.jpg" autoplay loop muted playsinline aria-label="좁은 통로 장면을 위에서 본 두 영상. 위는 기존 계획으로 팔레트를 꺼낸 직후 짧은 곡선에서 앞뒤로 여러 번 움직이며 다시 계획함. 아래는 개선한 계획으로 더 긴 곡선으로 빠져나와 한 번에 운반함"></video>
<span class="vl12 top">{T('S07_VID_TOP')}</span><span class="vl12 bot">{T('S07_VID_BOTTOM')}</span></div>
<figcaption>{T('S07_VID_CAPTION')}</figcaption></figure>
<div class="stack cu12r">
{table(cells('S07_HEAD'), [cells(f'S07_ROW{i}') for i in (1, 2, 3)], 'comparison h7 ct12')}
<p class="note12">{T('S07_NOTE1')}</p>
{lgd(('line', C_APPROACH, T('S07_LEG_APPROACH')), ('line', C_TRANSPORT, T('S07_LEG_TRANSPORT')), ('line', C_RETURN, T('S07_LEG_RETURN')), ('ring', C_DROP, T('S07_LEG_DROP')))}
</div>
</div>
""",
    """리보틱스가 보낸 좁은 통로 장면에서는 팔레트를 꺼낸 뒤 후진과 전진을 바꾸는 방향 전환점을 지나야 합니다. 경로 계획기가 전환점 바로 앞에 0.6미터보다 짧은 곡선을 자주 넣었고, 지게차는 그 짧은 구간에서 방향을 다 맞추지 못해 멈추고 다시 계획해야 했습니다. 그래서 계획할 때 방향을 바꾸기 직전에 짧은 곡선이 생기는 경로를 덜 좋게 쳐서, 계획기가 그런 경로를 되도록 피하게 했습니다. 영상은 같은 장면을 같은 조건으로 돌린 것으로, 위의 기존은 짧은 곡선에서 앞뒤로 여러 번 움직이며 두 번 다시 계획하고, 아래의 개선은 한 번에 빠져나옵니다. 무작위 배치 10가지로 비교하니 짧은 곡선이 90개에서 18개로, 운반 중 다시 계획한 횟수가 16번에서 8번으로 줄었고, 완주는 9번으로 같았습니다. (전환)""",
    [(ACS, '2 절: aisle_rack seed 0–9 × 끔 / 켬(--short-cusp-arc 0.6,1.0), 결정 모드; 운반 cusp 실패 뒤 재계획 16 → 8, 완주 9 = 9, 운반 짧은 곡선 cusp 다리(0.6 m 미만) 90 → 18; aisle_rack 한정 기본 켬(#566)'),
     (ACS_PLAN, '0.6 m 미만 곡선 다리가 cusp 바로 앞에 오면 비용을 더함'),
     (F2I, '남은 실패 aisle_rack s4: 이전 모형 실패(운반 전환점, 재계획 2 회 뒤) → 순응 타이어 완주 5.7 mm — 다른 스냅숏(f2i_22fe89be)이라 표의 짝(acs_d45bb1e1)과 섞지 않음'),
     ('영상', 'ws1 test_runs/acs/render_acs_d45bb1e1/acsAv_aisle_rack_s1 · acsBv_aisle_rack_s1/run/transport.mp4 (sha256 9b3bc418… · e53ef020…), 시뮬 40–245 s, 위아래로 붙여 8 배속')],
    '영상: Isaac Sim 탑뷰(8배속), 위 기존 · 아래 개선')

# ----------------------------------------------------------------- 8 next week
add(T('S08_TITLE'), '08  ' + T('S08_TITLE'), 30, f"""
<h2 class="headline">{T('S08_HEADLINE')}</h2>
{table(cells('S08_HEAD'), [cells(f'S08_ROW{i}') for i in (1, 2, 3)], 'comparison h7 endt12')}
""",
    """다음 주 계획입니다. 11월 20일에 실제 차량으로 직진할 때 방향이 얼마나 틀어지는지, 조향 명령에 비해 얼마나 도는지, 멈췄다 다시 출발할 때 어떻게 반응하는지를 차의 센서와 줄자로 재고, 그 값으로 시뮬레이션의 타이어 모형도 맞춰 보겠습니다. LiDAR가 오면 노트북과 Jetson에 연결해 확인하고, 메인보드와 부품이 오면 모터와 엔코더를 하위 제어 보드로 실제로 돌려 보겠습니다. 이상으로 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [('총괄 (2026-11-17 · 18)', '11-20 실차 측정(직진 방향 드리프트, 조향 대 실제 곡률, 재출발 응답), A2M12 연결, 타이어 강성 확인'),
     ('사용자 (2026-11-16, 총괄 전달)', '측정은 차의 센서와 줄자로 cm · 도 단위, 시행 수 적게')],
    '표: 다음 주 할 일')


TITLE = '12주차 자율 지게차 개발'
TOTAL = 425


def build():
    assert len(slides) == 9, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-11-18 (발표용 재구성). 2쪽은 2026-11-17 실제 장비 측정이고 모터 · 엔코더는 아직 연결하지 않았다. 3–7쪽은 Isaac 시뮬레이션 결과이고, 3–5쪽의 전후 비교는 같은 장면 · 같은 조건의 짝 비교만 썼다(SOURCES.md). '
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
