"""Build the week 12 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 12 answers the week 11 feedback (robot repository docs/references/week11_feedback.md): buy and try the real
equipment, test the self-localization more widely, read more papers. It shows the first connection of the real
devices (2026-11-17: the WeAct STM32H743 board with the firmware's locked-output HIL build talking to the laptop and
the Jetson for 10 minutes, the Jetson Orin Nano Super's command-cycle check under full CPU load, the D435i IMU on the
Jetson; the A2M12 was not there), the start relocalization tested over two load layouts and with a short forward/back
move, and the narrow-aisle short-arc cost (Isaac render, off above / on below). Motors and encoders are not connected
yet (the boards ship on 11-20) -- the slides say so. No new papers this week; the paper search is in next week's plan.
Screen text and narration were written directly (project memory script-md-no-agy).
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
slides = []

ROBOT = 'lightminn/forklift main f7566ed4'
HWDAY = f'{ROBOT} docs/validation/2026-11-17-hw-day.md'
HWRAW = f'{ROBOT} docs/validation/assets/hw-day-2026-11-17/'
FEEDBACK = f'{ROBOT} docs/references/week11_feedback.md (로컬 전용, 저장소 밖 미추적 파일)'
BP1B = f'{ROBOT} docs/validation/2026-10-29-b-p1b-search-budget.md'
BP2D = f'{ROBOT} docs/validation/2026-10-29-b-p2d-start-relocalization.md'
ROM = f'{ROBOT} docs/validation/2026-11-16-reloc-observe-move.md'
ACS = f'{ROBOT} docs/validation/2026-11-16-aisle-short-cusp-arc.md'
ACS_PLAN = f'{ROBOT} docs/plans/2026-11-16-aisle-short-cusp-arc.md'

# overlay colours of the Isaac render (sim/isaac/run_transport.py add_path_display) and the drop ring
C_APPROACH, C_TRANSPORT, C_RETURN, C_DROP = '#0d73ff', '#ffa60a', '#8c33d9', '#22e022'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def img(src, alt, cap=None, cls='shot'):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="{cls}"><img class="media" src="assets/{src}" '
            f'alt="{escape(alt, quote=True)}">{c}</figure>')


def lgd(*items):
    """Legend: (kind, colour, text), kind line / ring / dash (week 11's helper)."""
    out = []
    for kind, colour, text in items:
        if kind == 'ring':
            sw = f'<span class="sw ring" style="border-color:{colour}"></span>'
        elif kind == 'dash':
            sw = f'<span class="sw dash" style="border-color:{colour}"></span>'
        else:
            sw = f'<span class="sw ln" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="lgd7">{"".join(out)}</div>'


def table(head, rows, cls='comparison h7'):
    h = ''.join(f'<th>{x}</th>' for x in head)
    body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'


# ----------------------------------------------------------------- cover
add('개발 진행 보고', '12주차\n자율 지게차 개발', 20, '',
    """안녕하십니까. 12주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 발표는 지난주에 주신 피드백 세 가지에 답하는 순서로 준비했습니다. 실제 장비를 처음 연결해 본 결과와 시작 위치 찾기를 조건을 넓혀 다시 시험한 결과를 먼저 말씀드리고, 이어서 지난 발표 이후 시뮬레이션에서 실패했던 사례를 어떻게 고쳐 성공률을 높였는지 같은 조건 비교 결과로 말씀드린 뒤 다음 주 계획으로 마치겠습니다. (전환)""",
    [(FEEDBACK, '11주차 피드백 원문')], '진행 보고')

# ----------------------------------------------------------------- 1
FB_ROWS = [
    ('장비를 실제로 사서 써 볼 것', 'MCU 보드, Jetson, 카메라를 실제로 연결해 통신과 성능 확인', '02 · 03'),
    ('SLAM 자기 위치를 다양하게, 더 정확하게 시험', '짐 배치 2가지에서 시작 위치 84곳씩, 앞뒤 이동까지 추가해 시험', '04'),
    ('논문 더 찾아보기', '이번 주에는 하지 못함, 다음 주 조사 항목으로 계획', '07'),
]
add('지난주 피드백과 이번 주 진행', '01  지난주 피드백과 이번 주 진행', 35, f"""
<h2 class="headline">지난주 피드백 세 가지에 맞춘 이번 주 진행</h2>
{table(['지난주 피드백', '이번 주 진행', '쪽'], FB_ROWS, 'comparison h7 fb12')}
""",
    """지난주 발표 뒤에 세 가지 피드백을 받았습니다. 첫째, 모터 같은 장비를 실제로 사서 직접 써 보라는 것, 둘째, SLAM으로 자기 위치를 판정하는 기능을 더 다양하게, 더 정확하게 시험하라는 것, 셋째, 논문을 더 찾아보라는 것이었습니다. 첫째는 이번 주에 MCU 보드와 Jetson, 카메라를 실제로 연결해 본 결과로 2쪽과 3쪽에서 말씀드립니다. 둘째는 시작 위치 찾기를 짐 배치와 시험 방식을 바꿔 다시 확인한 결과로 4쪽에서 말씀드립니다. 셋째는 이번 주에 새로 찾은 논문이 없어서, 다음 주 계획에 조사 항목으로 넣었습니다. (전환)""",
    [(FEEDBACK, '「각종 장비들(ex, 모터) 실제로 사서 뚜다해보고 써볼것 / SLAM을 통한 자기 위치 판정 정확하게등등 다양하게 더 정확하게 테스트 하기 / 논문 더 찾아보기」'),
     ('총괄 (2026-11-17)', '이번 주 새로 찾은 논문 없음 — 지어내지 않고 다음 주 계획으로 돌림')],
    '표: 피드백별 이번 주 진행과 해당 쪽')

# ----------------------------------------------------------------- 2
LINK_ROWS = [
    ('10분 동안 받은 상태 메시지', '60,000개, 빠짐 0', '59,999개, 빠짐 0'),
    ('명령 왕복 시간 (중앙값 · 최대)', '9.3 · 10.2 ms', '4.0 · 10.3 ms'),
    ('상태 수신 간격 최대', '20.9 ms', '10.7 ms'),
]
add('MCU 보드 첫 연결', '02  MCU 보드 첫 연결', 65, f"""
<h2 class="headline">실제 MCU 보드에 펌웨어를 올려 노트북 · Jetson과 10분 통신, 빠진 메시지 0</h2>
<div class="hw12 grow">
{img('hw_h743.jpg', 'WeAct STM32H743 코어 보드 윗면. 가운데 STM32H743 칩, 아래쪽에 USB-C 단자와 microSD 슬롯, 양옆에 핀 헤더 두 줄', 'STM32H743 코어 보드 (팀 촬영)', 'shot ph12')}
<div class="stack hw12r">
<div class="phase-flow link12"><b>연결</b><span>노트북 또는 Jetson ↔ USB ↔ STM32H743 (모터 출력을 잠근 시험용 펌웨어)</span></div>
{table(['', '노트북', 'Jetson'], LINK_ROWS, 'comparison h7 lk12')}
<p class="note12">MCU는 10 ms마다 상태를 보내고, 10분 동안 보드 리셋 0회</p>
</div>
</div>
<div class="takeaway">모터와 엔코더는 아직 연결하지 않았습니다. 메인보드와 부품이 11월 20일에 발송되면 이어서 연결합니다.</div>
""",
    """첫 번째 피드백에 대한 답입니다. 지금까지 PC에서만 시험하던 MCU 펌웨어를 실제 STM32H743 보드에 처음 올렸습니다. 사진이 이번에 연결한 코어 보드입니다. 모터 출력을 잠근 시험용 펌웨어를 굽고, 노트북과 Jetson에 각각 USB로 연결해 10분씩 명령과 상태를 주고받았습니다. MCU는 10밀리초마다 상태를 보내는데, 10분 동안 노트북은 6만 개, Jetson은 5만 9천 999개를 받았고 중간에 빠진 메시지는 하나도 없었습니다. 명령을 보내고 그 명령이 반영된 상태가 돌아오기까지의 왕복 시간은 노트북이 중앙값 9.3밀리초, Jetson이 4.0밀리초였고, 둘 다 최대 10밀리초 남짓이었습니다. 상태를 받는 간격도 Jetson에서는 최대 10.7밀리초로, MCU가 보내는 주기를 거의 그대로 따라갔습니다. 다만 이번에 확인한 것은 통신까지입니다. 모터와 엔코더는 메인보드와 부품이 도착해야 연결할 수 있고, 11월 20일에 발송될 예정입니다. (전환)""",
    [(HWDAY, '「H743 링크」 표: HIL 이미지 forklift-mcu hil locked 65f252a5c4b6, DFU 굽기 검증; 노트북 600 s · STATE 60,000 · seq 틈 0 · 프레임 오류 0 · MCU 주기 10.0 ms · 호스트 간격 최대 20.917 ms · 왕복 p50 9.3 / 최대 10.15 ms · 리셋 0; Jetson 600 s · STATE 59,999 · seq 틈 0 · 호스트 간격 최대 10.661 ms · 왕복 3.97 / 10.26 ms · 리셋 0; 둘 다 PASS'),
     (f'{HWRAW}jetson/h743_link.txt · laptop_h743/BUILD.txt', 'Jetson 판정 줄과 굽힌 이미지 식별(위 값과 같음, 2026-11-17 확인)'),
     ('사진', '사용자 촬영(2026-11-17, WeAct STM32H743VIT6 코어 보드 윗면) — 보드 주변만 잘라 180° 돌리고 EXIF 를 지움'),
     (HWDAY, '연결: H743 은 노트북 USB(USB CDC), 그 뒤 Jetson USB; 모터 · 엔코더 미연결 — 메인보드 · 부품 11월 20일 발송 예정(11주차 10 장)')],
    '사진: 이번에 연결한 STM32H743 코어 보드 (팀 촬영), 표: 2026-11-17 측정')


# ----------------------------------------------------------------- 3
def cycle_chart():
    """Max command-cycle gap on the Jetson, idle and full CPU load, against the 80 ms pass line (hw-day plan)."""
    left, width, xmax = 112, 360, 100
    rows = (('정지', 21.9, '#2f74c0'), ('부하', 29.6, '#2f74c0'))
    p = []
    for i, (name, v, col) in enumerate(rows):
        y = 26 + i * 50
        w = v / xmax * width
        p.append(f'<text x="{left - 12}" y="{y + 7}" text-anchor="end" font-size="19" fill="#1b1f24">{name}</text>'
                 f'<rect x="{left}" y="{y - 16}" width="{w:.1f}" height="32" rx="3" fill="{col}"/>'
                 f'<text x="{left + w + 10:.1f}" y="{y + 8}" font-size="21" font-weight="700" fill="#1b1f24">{v} ms</text>')
    xl = left + 80 / xmax * width
    p.append(f'<line x1="{xl:.1f}" y1="0" x2="{xl:.1f}" y2="98" stroke="#d64541" stroke-width="3" stroke-dasharray="7 5"/>'
             f'<text x="{xl:.1f}" y="118" text-anchor="middle" font-size="16" fill="#d64541" font-weight="700">기준 80 ms</text>')
    return (f'<svg class="diagram cyc12" viewBox="0 0 500 124" role="img" aria-label="Jetson에서 MCU로 명령을 보내는 주기의 최대 간격. '
            f'정지 21.9 ms, 모든 코어 부하 29.6 ms, 기준 80 ms 미만"><g font-family="var(--uos-font)">{"".join(p)}</g></svg>')


def device(src, alt, name, lines, extra='', cls=''):
    body = ''.join(f'<p>{x}</p>' for x in lines)
    return (f'<div class="dev12{cls}">{img(src, alt, None, "shot")}<h3>{name}</h3>{body}{extra}</div>')


add('Jetson과 센서 첫 연결', '03  Jetson과 센서 첫 연결', 65, f"""
<h2 class="headline">Jetson 전 코어 부하에서도 명령 주기 최대 30 ms, 카메라 IMU 빠진 측정 0</h2>
<div class="devs12 grow">
{device('hw_jetson.jpg', 'NVIDIA Jetson Orin Nano Developer Kit 보드. 검은 방열판과 팬, 왼쪽에 USB와 이더넷 단자', 'Jetson Orin Nano Super',
        ['MCU로 명령을 보내는 주기 20 ms', '5분씩 측정한 최대 간격'], cycle_chart())}
{device('hw_d435.jpg', 'Intel RealSense D435 깊이 카메라를 작은 삼각대에 올린 사진', 'RealSense D435i (Jetson에 연결)',
        ['IMU 2분 기록', '자이로 400 Hz, 가속도 200 Hz', '빠진 측정 <b>0</b>'])}
{device('hw_lidar.jpg', 'SLAMTEC RPLIDAR A2 2D 라이다', 'RPLIDAR A2M12',
        ['장비가 아직 없어 연결하지 못함', '도착하면 노트북과 Jetson에 연결 예정'], '', ' off12')}
</div>
""",
    """두 번째로 상위 제어기인 Jetson과 센서입니다. 이번에 쓴 Jetson은 새로 받은 Orin Nano Super이고, 최대 성능 모드로 설정했습니다. Jetson은 주행 중에 20밀리초마다 MCU로 명령을 보내야 합니다. 그래서 아무 일도 시키지 않았을 때와 CPU 여섯 코어 모두에 부하를 걸었을 때 각각 5분 동안, 명령을 보내는 간격이 얼마까지 벌어지는지 쟀습니다. 정지 상태에서는 최대 21.9밀리초, 부하를 건 상태에서도 최대 29.6밀리초로, 미리 정해 둔 기준인 80밀리초보다 훨씬 짧았습니다. 인식과 SLAM이 함께 돌아도 명령이 끊기지 않을 여유가 있다는 뜻입니다. 가운데는 RealSense D435i 카메라입니다. Jetson에 연결해 카메라 안의 IMU를 2분 동안 기록했고, 자이로는 초당 400번, 가속도는 초당 200번 측정이 빠짐없이 들어왔습니다. 오른쪽 2D LiDAR인 RPLIDAR A2M12는 이번에는 장비가 없어 연결하지 못했고, 도착하면 같은 방식으로 확인하겠습니다. (전환)""",
    [(HWDAY, '「Jetson 기록」: Orin Nano Super Developer Kit, JetPack R39.2.1, Ubuntu 24.04, 6 코어 · 7.4 GiB, MAXN_SUPER + jetson_clocks; 「다리 정체」 각 300 s: 정지 14,954 주기 p50 20.1 · 최대 21.9 ms, 부하(모든 코어) 14,678 주기 p50 20.1 · p99 23.8 · 최대 29.6 ms, 80 ms 이상 0, 기준은 정지 40 ms 넘는 간격 0 · 부하 80 ms 이상 간격 0 (리허설 다리, 모형 MCU)'),
     (f'{HWRAW}jetson/stall/{{idle,load}}/verdict.txt', '두 판정 ALL PASS, 값은 위와 같음(2026-11-17 확인)'),
     (HWDAY, '「D435i IMU」 정지 120.2 s: 자이로 48,071 표본 399.8 Hz, 가속도 24,060 표본 200.1 Hz, dropped 0 (Jetson 에서 librealsense v2.59.2 소스 빌드 뒤); 「A2M12」 장비가 없어 미실시'),
     ('사진 hw_jetson.jpg', 'NVIDIA Jetson Orin Nano Super Developer Kit 제품 페이지 이미지 jetson-orin-nano-super-developer-kit-bbm-d@2x.jpg 를 보드 부분만 자름 (© NVIDIA, 제품 소개용 이미지)'),
     ('사진 hw_d435.jpg', 'Wikimedia Commons, File:Intel Realsense depth camera D435.jpg — Marc Auledas, CC BY-SA 4.0; 같은 계열의 D435(IMU 없는 모델)이며 겉모양은 D435i 와 같음'),
     ('사진 hw_lidar.jpg', '과제 브리프 3쪽의 RPLIDAR A2 이미지(이 저장소 week-02/assets/rplidar-a2.jpeg)')],
    '사진: 제품 사진 (출처는 SOURCES.md), 그래프: 2026-11-17 Jetson 측정')

# ----------------------------------------------------------------- 4
REL_ROWS = [
    ('짐 배치 A', '저장된 LiDAR 스캔으로 위치 계산', '69곳 (82 %)', '0'),
    ('짐 배치 B', 'Isaac에서 실제 출발까지 수행', '68곳 (81 %)', '0'),
    ('짐 배치 B', '제자리에서 못 찾으면 앞뒤 0.3 m 이동', '67곳 → <b>69곳</b>', '<b>0</b>'),
]
add('시작 위치 찾기 시험 확대', '04  시작 위치 찾기 시험 확대', 75, f"""
<h2 class="headline">짐 배치와 시험 방식을 바꿔도 시작 위치 약 80 % 스스로 확정, 틀린 위치 확정 0</h2>
<div class="rel12 grow">
<div class="stack">
<p class="panel-h">SLAM으로 미리 만든 지도에서 시작 위치 찾기 (같은 홀, 시작 위치 84곳씩)</p>
{table(['짐 배치', '시험 방식', '스스로 확정', '틀린 위치'], REL_ROWS, 'comparison h7 rl12')}
</div>
{img('s04_candidates.png', '운용 콘솔 지도 화면. 같은 모양 선반 사이에 출발 위치 후보 네 개가 표시되고, 위쪽 창에 지도에 놓기와 다시 시도 버튼이 있음', '같은 모양 선반 앞에서는 후보가 여럿 나옴', 'shot cand12')}
</div>
<div class="takeaway">남은 실패는 모두 같은 모양 선반이 반복되는 구역에서 나왔습니다. 실차는 정해 둔 시작 자리에서 출발하도록 정했습니다.</div>
""",
    """두 번째 피드백인 SLAM 자기 위치 판정입니다. 지게차는 SLAM으로 미리 만든 지도 위에서, LiDAR로 본 주변 모양을 지도와 맞춰 자기 위치를 찾습니다. 지난주에는 한 가지 짐 배치에서만 결과를 보여 드렸는데, 이번에는 조건을 넓혀 세 가지로 정리했습니다. 첫째는 짐 배치를 바꾼 홀에서 시작 위치 84곳의 LiDAR 스캔을 저장해 두고 위치를 계산한 시험으로, 69곳, 82퍼센트를 스스로 확정했습니다. 둘째는 다른 짐 배치에서 Isaac으로 지게차를 실제로 놓고 위치를 찾아 출발까지 한 시험으로, 84곳 중 68곳이었고 확정한 위치의 오차는 중앙값 2센티미터였습니다. 셋째는 이번 주에 새로 한 시험입니다. 제자리에서 위치를 정하지 못하면 앞뒤로 0.3미터씩 움직여 다시 보게 했더니, 제자리에서 확정한 67곳이 69곳으로 두 곳 늘었습니다. 세 시험 모두 틀린 위치를 맞다고 확정한 경우는 한 번도 없었습니다. 남은 실패는 오른쪽 그림처럼 같은 모양의 선반이 반복되는 구역에서, 후보가 여러 개 나와 하나로 정하지 못한 경우입니다. 앞뒤로 움직여도 두 곳만 풀렸기 때문에, 이동 기능은 기본으로 켜지 않고, 실차는 바닥에 표시해 두고 지도에 등록한 시작 자리에 놓고 출발하도록 정했습니다. (전환)""",
    [(BP1B, '결론: 새 세계(공장 배치 seed 4) 새 조사 지도, 유효 시작 84 곳, 성공 69 (82 %), 틀린 확정 0 · 부정확 0, 요청 15(경쟁 후보 8, 반복 구조 5, 탐색 상한 2); 기록 스캔으로 정합기 평가(tools/global_match_eval.py); 범위는 같은 홀 조건부'),
     (BP2D, 'seed 5 홀, Isaac 출발 재위치: 유효 84(시작 93 중), 성공 68 (81.0 %), 틀림 0, 시작 시점 위치 오차 중앙값 2.0 cm; 실패 16 곳 모두 홀 남쪽 반복 선반 구역 (11주차 02 장 수치)'),
     (ROM, '같은 지도 · 출발 목록(93 개), 유효 84: 제자리 A 67 (79.8 %) → 이동 B 69 (82.1 %), 틀린 확정 0, 구제 2 · 악화 0, 이동 비용 중앙값 20.9 s; 남은 실패는 남쪽 반복 선반 칸; 총괄 결정 승격 안 함, 실차는 정해 둔 시작 자리(known start) 운용'),
     ('총괄 (2026-11-17)', '「정해 둔 시작 자리」 = 바닥에 시작 자리를 표시하고 그 좌표 · 방향을 지도에 등록, 그 자리에서 재위치 탐색 없이 시작(런처 START_POSE_KNOWN, 러너 --start-known)'),
     ('그림', '11주차 assets/r02_candidates.png (B-P2 콘솔 렌더 val4_077 의 후보 선택 화면)를 그대로 씀'),
     ('범위', '세 시험 모두 같은 홀 시뮬레이션이고 짐 배치만 다름(seed 4 · seed 5); 둘째와 셋째는 같은 출발 목록이지만 설정이 달라 성공 수를 직접 비교하지 않음 (ROM 1 절)')],
    '표: 시작 위치 찾기 세 시험, 그림: 후보 선택 콘솔 화면 (11주차 렌더)')

# ----------------------------------------------------------------- 5 failures since week 11 that were fixed (lead, 2026-11-17: user feedback)
PFB = f'{ROBOT} docs/validation/2026-11-15-post-fix-baseline.md'
PDI = f'{ROBOT} docs/validation/2026-11-14-path-display-impact.md'
K1R = f'{ROBOT} docs/validation/2026-11-15-k1-recheck.md'
K1C = f'{ROBOT} docs/validation/2026-11-14-k1-comparison.md'
RHT = f'{ROBOT} docs/validation/2026-11-17-return-home-timeout.md'
GBC = f'{ROBOT} docs/validation/2026-11-17-goal-band-cusp-retry.md'
FRAG = f'{ROBOT} docs/validation/2026-11-15-baseline-fragility-summary.md'
FIX_ROWS = [  # screen text written by agy (Gemini 4 Hydrogen High, 2026-11-17) from the raw material; facts checked
    ('좁은 통로에서<br>팔레트 바로 앞 인식 실패', '계획 경로 표시선과 고리가<br>인식 카메라 영상에 찍힘', '경로 표시선은 운용 화면에만<br>그리고 인식 카메라에서 뺌', '인식 실패 1회 → 0회<br>40회 중 완주 34회 → 36회'),
    ('다시 관측 뒤 포크 넣기 직전<br>옆 어긋남 허용 한도 초과', '다시 관측 자리 도착 허용이<br>느슨해 5.6, 6.2 cm도 인정', '다시 관측 자리 도착 허용을<br>5 cm · 0.05 rad로 좁힘', '옆 어긋남 8 cm 초과 4회 → 0회<br>40회 중 완주 36회 = 36회'),
    ('복귀 끝 목표 바로 옆에 멈춰<br>도착 못 하고 시간 초과 실패', '허용 8 mm를 0.1 mm 넘어 미도착<br>정지 대응 규칙이 없었음', '정지를 감지해 그 자리에서<br>경로를 다시 계획하게 함', '34초 정지로 시간 초과 실패<br>→ 고친 뒤 완주'),
]
add('지난 발표 이후 고친 실패', '05  지난 발표 이후 고친 실패', 80, f"""
<h2 class="headline">실패 3건을 고쳐 인식 실패와 큰 어긋남은 0회로, 복귀 멈춤도 완주로 바꿈</h2>
<p class="panel-h">Isaac Sim에서 같은 장면과 seed로 전후를 짝지어 비교한 결과</p>
{table(['지난번 실패', '원인', '고친 것', '같은 조건 전후'], FIX_ROWS, 'comparison h7 fx12')}
""",
    """지난 발표 이후 시뮬레이션에서 실패한 사례를 원인부터 찾아 고친 것을 정리했습니다. 효과는 모두 같은 장면, 같은 seed를 고치기 전과 후로 짝지어 비교한 결과만 적었습니다. 첫째, 좁은 통로에서 팔레트 바로 앞까지 가서 팔레트를 찾지 못한 실패가 있었습니다. 원인을 따라가 보니, 운용 화면에 보여 주려고 그린 계획 경로 표시선이 시뮬레이션 안의 물체로 그려져 인식 카메라 영상에도 찍히고 있었습니다. 표시선을 카메라 영상에서 빼고, 같은 코드에서 표시선만 보이게 한 경우와 40번씩 비교했더니 완주가 34번에서 36번으로 늘고 인식 실패가 없어졌습니다. 둘째, 팔레트 앞에서 가까이 다시 보는 자리에 옆으로 5에서 6센티미터 어긋난 채 도착해도 도착으로 받아 주다 보니, 포크를 넣기 직전에 옆 어긋남이 커지는 경우가 있었습니다. 그 자리의 도착 허용치를 5센티미터, 0.05라디안으로 좁혔더니 40번 중 8센티미터 넘게 어긋난 경우가 4번에서 0번이 되었고, 완주는 36번으로 같았습니다. 셋째, 출발점으로 돌아오는 마지막에 목표에서 옆으로 8.1밀리미터 떨어진 채 멈춰 시간이 초과된 실패가 있었습니다. 허용치가 8밀리미터라 0.1밀리미터 차이로 도착 판정이 나지 않았는데, 이런 정지를 받아 주는 규칙이 없었습니다. 이런 정지를 감지해 경로를 다시 계획하게 했고, 같은 장면과 seed에서 실패가 완주로 바뀌었습니다. 둘째는 어긋난 사례가 네 번뿐이고 셋째는 장면 하나에서 확인한 결과라, 실차 측정 뒤 다시 확인하겠습니다. (전환)""",
    [(PFB, '3.3 R vs S: 같은 스냅숏 2bea23e5, 표시 prim 이 인식 카메라에 안 보임(R) / 보임(S), 같은 장면 · seed 40 짝, 결정 모드; 완주 36/40 대 34/40, 실패 분류 perception 0 대 1(aisle_rack s2 near_capture no_expected_candidate); 바뀐 짝 5(R 만 완주 3, S 만 완주 1, s24 는 둘 다 실패 · S 는 렌더 동기 실패) — 계획 3.3 대로 #512 전후 차이의 표시선 몫이 아니라 지금 코드 위의 누출 몫'),
     (PDI, '1 절: 표시만 끈 진단 4 실행(aisle_rack s0 · s1 × B0 · R)에서 R 팔 근접 캡처 거부 → 채택 2/2; 결함은 표시선과 목적지 고리가 렌더되는 장면 prim 이라 인식 카메라에 찍힌 것(#509), 수정 #512'),
     (K1R, '등록 판정 「K1 이 나음」: 결정 모드 riib 40 짝, B0(NEAR_OBSERVE_ARRIVAL=off) 대 K1(--near-observe-arrival 0.05,0.05); 완주 36 · 36, |횡 오프셋| > 0.08 m 실행 B0 4 · K1 0, 새 악화 0; 노출 4 는 기준을 겨우 채운 약한 근거(s19 는 −80.099 mm); riib 런처 기본 유지(#499)'),
     (FRAG, '② 근접 문턱 근처 거부: random_1 두 건은 느슨한 도착(5.6 · 6.2 cm)을 받아들인 뒤 횡 한도 0.10 m 를 5 · 7 mm 넘음'),
     (RHT, 'random_1 seed 24: 복귀 경로 끝 옆 8.100 mm(허용 8 mm), 앞뒤 −0.15 mm 에서 34.5 s 정지 → Tracking timeout in return_home; #117 크리프 규칙 R1 · R2 와 정체 재계획 조건이 모두 받지 못한 사각 띠(소프트웨어 쪽); 옆 오차의 출처(plant)는 실측 없이 정하지 않음'),
     (GBC, '결정 모드 짝: s24 끔 = 시간 초과(기준선 재현), --goal-creep-band on = 완주(띠 고정 → 정체 재계획 0.89 m); 총괄 결정 riib 런처 기본 켬(#571), 근거 seed 1 개; Isaac smoke 3 실행 완주')],
    '표: 수정 전후 같은 장면 · seed 짝 비교 (Isaac 시뮬레이션)')

# ----------------------------------------------------------------- 6
CU_ROWS = [
    ('전환점 앞 짧은 곡선 (운반)', '90개', '<b>18개</b>'),
    ('운반 중 재계획', '16회', '<b>8회</b>'),
    ('완주', '10회 중 9회', '10회 중 9회'),
]
add('좁은 통로 방향 전환 경로 개선', '06  좁은 통로 방향 전환 경로 개선', 65, f"""
<h2 class="headline">방향 전환점 앞 짧은 곡선을 줄여 좁은 통로 운반 중 재계획 16 → 8회, 완주는 유지</h2>
<div class="cu12 grow">
<figure class="shot vw12"><div class="vbox12"><video class="media" src="assets/s05_cusp.mp4" poster="assets/s05_cusp_poster.jpg" autoplay loop muted playsinline aria-label="좁은 통로 장면을 위에서 본 두 영상. 위는 기존 계획으로, 팔레트를 꺼낸 직후 전환점 앞 짧은 곡선에서 앞뒤로 여러 번 움직이며 다시 계획함. 아래는 개선한 계획으로, 더 긴 곡선으로 빠져나와 한 번에 운반함"></video>
<span class="vl12 top">기존</span><span class="vl12 bot">개선</span></div>
<figcaption>같은 장면 · 같은 조건, 위아래 동시 재생</figcaption></figure>
<div class="stack cu12r">
{table(['', '기존', '개선'], CU_ROWS, 'comparison h7 ct12')}
<p class="note12">리보틱스 좁은 통로 장면, 10회씩 같은 조건 비교</p>
{lgd(('line', C_APPROACH, '접근 경로'), ('line', C_TRANSPORT, '운반 경로'), ('line', C_RETURN, '복귀 경로'), ('ring', C_DROP, '하역 위치'))}
</div>
</div>
""",
    """다음은 지난주 5쪽에서 보여 드린 방향 전환점 사례입니다. 지난주에는 전환점에 어긋난 채 도착하면 그 자리에서 경로를 다시 계획해 이어 가는 복구를 보여 드렸는데, 이번에는 어긋나는 원인 자체를 줄였습니다. 리보틱스 좁은 통로 장면에서는 팔레트를 꺼낸 뒤 후진과 전진을 바꾸는 전환점을 지나야 합니다. 그런데 경로 계획기가 전환점 바로 앞에 아주 짧은 곡선 구간을 자주 넣었고, 지게차는 그 짧은 구간 안에서 방향을 다 맞추지 못해 전환점에 어긋난 채 도착했습니다. 그러면 멈추고 경로를 다시 계획해야 했습니다. 그래서 0.6미터보다 짧은 곡선 구간에 비용을 더해, 계획기가 가능하면 더 긴 곡선을 고르게 했습니다. 영상은 같은 장면을 같은 조건으로 돌린 두 실행이고, 위가 기존, 아래가 개선한 경우입니다. 위에서는 팔레트를 꺼낸 직후 짧은 곡선에서 앞뒤로 여러 번 움직이며 두 번 다시 계획하고, 아래에서는 한 번에 빠져나와 운반합니다. 10번씩 비교했을 때 운반 경로의 짧은 곡선은 90개에서 18개로, 운반 중 다시 계획한 횟수는 16번에서 8번으로 줄었고, 완주는 양쪽 모두 10번 중 9번으로 같았습니다. 다른 장면에서는 아직 확인하지 않았기 때문에, 이 설정은 좁은 통로 장면에서만 기본으로 켰습니다. (전환)""",
    [(ACS, '2 절 판정: aisle_rack seed 0–9 × 끔 / 켬(--short-cusp-arc 0.6,1.0), 결정 모드; 운반 cusp 실패 뒤 재계획 합 16 → 8, 완주 9 = 9, 최종 실패 1 = 1, 계획 벽시계 최대 710 → 687 s; 짧은 곡선 cusp 다리(0.6 m 미만) 운반 90 → 18; 총괄 결정: riib 런처 aisle_rack 장면 한정 기본 켬(#566)'),
     (ACS_PLAN, '0.6 m 미만 곡선 다리가 cusp 바로 앞에 오면 비용을 더함(--short-cusp-arc 길이 0.6 m, 비용 1.0)'),
     ('영상', 'ws1 test_runs/acs/render_acs_d45bb1e1/acsAv_aisle_rack_s1/run/transport.mp4 (끔, sha256 9b3bc418…, 시뮬 297 s, 운반 cusp 재계획 2 회 101 · 113 s) 와 acsBv_aisle_rack_s1 (켬, sha256 e53ef020…, 277 s, 재계획 0) — 결정 모드 렌더로 비교 실행과 같은 궤적, 둘 다 완주; 두 영상을 같은 시뮬 시각 40–245 s 로 잘라 위아래로 붙이고 8배속'),
     ('겹침선 색', 'sim/isaac/run_transport.py add_path_display: 접근 (0.05, 0.45, 1.0), 운반 (1.0, 0.65, 0.04), 복귀 (0.55, 0.2, 0.85); 초록 원은 하역 칸')],
    '영상: Isaac Sim 탑뷰 (8배속), 위 기존 · 아래 개선')

# ----------------------------------------------------------------- 7
END_ROWS = [
    ('실차 측정 (11월 20일)', '직진 중 방향 틀어짐, 조향 명령 대비 실제 회전, 재출발 반응을 차의 센서와 줄자로 측정'),
    ('LiDAR 연결', 'RPLIDAR A2M12가 도착하면 노트북과 Jetson에 연결해 스캔 확인'),
    ('측정값 반영', '실측값을 시뮬레이션에 넣어 운반 경로 이탈과 팔레트 앞 접근 개선'),
    ('논문 조사', '사전 지도에서 시작 위치 찾기, 좁은 통로 방향 전환 경로 계획 관련 논문'),
]
add('다음 주 계획', '07  다음 주 계획', 45, f"""
<h2 class="headline">11월 20일 실차 측정과 LiDAR 연결, 측정값으로 시뮬레이션 보정</h2>
{table(['구분', '할 일'], END_ROWS, 'comparison h7 endt12')}
""",
    """다음 주 계획입니다. 11월 20일에 실제 차량으로 세 가지를 잽니다. 똑바로 가라고 했을 때 방향이 얼마나 틀어지는지, 조향 명령에 비해 실제로 얼마나 도는지, 그리고 멈췄다가 다시 출발할 때 어떻게 반응하는지를 차에 달린 센서와 줄자로 측정합니다. LiDAR가 도착하면 이번 주와 같은 방식으로 노트북과 Jetson에 연결해 확인하겠습니다. 측정한 값은 시뮬레이션에 넣어, 지금 시뮬레이션에서 남아 있는 운반 중 경로 이탈과 팔레트 앞 접근 문제를 실제 차량 기준으로 다시 다루겠습니다. 그리고 지난주 피드백대로, 사전 지도에서 시작 위치를 찾는 방법과 좁은 통로에서 방향을 바꾸는 경로 계획에 관한 논문을 찾아 지금 방식과 비교해 보겠습니다. 이상으로 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [('총괄 (2026-11-17)', '다음 계획: 11-20 실차 측정(직진 방향 드리프트, 조향 대 실제 곡률, 재출발 응답), A2M12 연결, 실측 뒤 운반 이탈 · 근접 개선; 논문은 이번 주 없음'),
     ('사용자 (2026-11-16, 총괄 전달)', '측정은 차의 센서와 줄자로 cm · 도 단위, 시행 수 적게'),
     (HWDAY, 'A2M12 전 단계(노트북 10 분 + Jetson 3 분)는 장비가 오면 함')],
    '표: 다음 주 할 일')


TITLE = '12주차 자율 지게차 개발'
TOTAL = 450


def build():
    assert len(slides) == 8, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-11-17. 2–3쪽은 2026-11-17 실제 장비 측정이고 모터 · 엔코더는 아직 연결하지 않았다. 4–6쪽은 Isaac 시뮬레이션 결과이고, 5–6쪽의 전후 비교는 같은 장면 · seed 짝 비교만 썼다(SOURCES.md). '
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
