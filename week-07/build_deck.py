"""Build the week 7 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 7 (class, 2026-10-14) reports the multi-forklift traffic work on ws1
(robot repository branch feat/fleet-five, plans and validation records
2026-10-08 to 10-12). The encoder board PCB slide (team 3D renders of the KTH7801 absolute board, 2026-10-14) asks the professor
about the connector pitch, 2.54 vs 1.27 mm (team message). Every fleet result is simulation with the simulator's pose (no SLAM)
on generated factories. The clips are cut by prepare_clips.py on ws1.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
BRANCH = 'forklift feat/fleet-five c24548f'
FIVE = 'docs/plans/2026-10-08-fleet-five-forklifts.md'
WORLDS_PLAN = 'docs/plans/2026-10-09-fleet-random-worlds.md'
WORLDS = 'docs/validation/2026-10-09-fleet-random-worlds.md'
TARA = 'docs/validation/2026-10-10-fleet-ta-ra.md'
WINDOWS = 'docs/validation/2026-10-11-fleet-time-windows.md'
W = 'ws1 artifacts/20261009_fleet_worlds'
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


def rgb(t):
    return '#%02x%02x%02x' % t


def legend(*items):
    """A graphic legend: swatches drawn in the clip's own colours, each with its term.
    items: (kind, colour, text) with kind line / dash / dots / band / ring / diamond / dot / num."""
    out = []
    for kind, colour, text in items:
        if kind == 'band':
            sw = f'<span class="sw band" style="background:{colour}73;border-color:{colour}"></span>'
        elif kind in ('ring', 'diamond'):
            sw = f'<span class="sw {kind}" style="border-color:{colour}"></span>'
        elif kind == 'dots':
            sw = f'<span class="sw dots" style="color:{colour}"></span>'
        elif kind == 'num':
            sw = f'<span class="sw num" style="background:{colour}">1</span>'
        else:
            sw = f'<span class="sw {kind}" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="legend">{"".join(out)}</div>'


# Clip colours, from the scripts that drew them (compose_fleet_video.py,
# compose_world_video.py, explain_tablets.py on feat/fleet-five).
TRUCK = rgb((60, 140, 230))          # truck 1's colour, standing for "each truck's colour"
WAIT = rgb((255, 70, 70))            # wait ring / line
PERSON = rgb((255, 80, 140))
TA_WAIT = rgb((255, 185, 40))        # wait ring once a truck has been held 20 s (detour search)


# ----------------------------------------------------------------- charts
def bars(rows, xmax, unit, aria):
    """Horizontal bars: rows = (label, value, colour)."""
    left, width, row = 190, 300, 74
    parts = []
    for i, (name, value, colour) in enumerate(rows):
        y = 36 + i * row
        w = max(4, value / xmax * width)
        parts.append(f'<text x="{left - 12}" y="{y + 8}" text-anchor="end" font-size="22" fill="#1b1f24">{name}</text>'
                     f'<rect x="{left}" y="{y - 22}" width="{w:.1f}" height="44" rx="3" fill="{colour}"/>'
                     f'<text x="{left + w + 12:.1f}" y="{y + 10}" font-size="28" font-weight="700" fill="#1b1f24">{value:,}{unit}</text>')
    return (f'<svg class="diagram" viewBox="0 0 600 {12 + row * len(rows)}" role="img" aria-label="{escape(aria, quote=True)}">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '7주차\n자율 지게차 개발', 20, '',
    """안녕하십니까. 7주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 주에는 두 가지를 말씀드리겠습니다. 첫째는 지게차 여러 대가 한 공장에서 서로 부딪히거나 막히지 않고 다니게 하는 교통 관리이고, 둘째는 하드웨어 쪽 엔코더 보드 PCB입니다. 교통 관리 결과는 모두 시뮬레이션입니다. (전환)""",
    [(FIVE, '5대 동시 운반 계획'), (WINDOWS, '교차 시간 창 실행 기록')], '진행 보고')

# ----------------------------------------------------------------- 2
add('이번 주 요약', '01  이번 주 요약', 40, f"""
<h2 class="headline">지게차 여러 대가 막히지 않고 다니는 교통 관리와 엔코더 보드 PCB</h2>
<div class="split grow" style="grid-template-columns:1.05fr 1fr;gap:28px">
<figure class="shot"><img class="media" src="assets/73_rack.jpg" alt="무작위로 만든 랙 창고를 위에서 본 모습. 지게차 8대가 각자 색 띠로 앞길을 예약하고 다님"></figure>
<table class="comparison t7 sum7 grow">
<tr><th>구분</th><th>이번 주 내용</th><th>상태</th></tr>
<tr><td>다중 지게차</td><td>NVIDIA 창고 5대에서 무작위 공장 3종, 최대 20대로</td><td class="blue"><b>겹침과 교착 없음</b><br><span class="muted small">(시뮬레이션)</span></td></tr>
<tr><td>교통 규칙</td><td>앞길 예약 → 막히면 우회 → 교차 지점 순서 정하기</td><td>긴 대기 약 1/3로</td></tr>
<tr><td>하드웨어</td><td>절대각 엔코더 보드 PCB (KTH7801)</td><td>3D 설계</td></tr>
</table>
</div>
<div class="takeaway">실제 현장은 여러 대가 같은 통로를 쓰므로 리보틱스 미팅에서도 동시 투입 대수와 중앙 관제를 묻습니다</div>
""",
    """먼저 이번 주 요약입니다. 지금까지는 지게차 한 대가 팔레트를 집어 옮기는 것을 만들었는데, 실제 현장에서는 여러 대가 같은 통로를 함께 씁니다. 그래서 리보틱스 미팅에서도 현장에 몇 대가 동시에 들어가는지, 중앙에서 관리하는 서버가 있는지를 여쭤보기로 했습니다. 이번 주에는 이것을 시뮬레이션으로 먼저 해 봤습니다. NVIDIA 창고에서 5대로 시작해서, 무작위로 만든 공장 세 종류에서 최대 20대까지 늘렸습니다. 교통 규칙은 앞길을 예약하는 방식에서 시작해, 막히면 돌아가는 규칙과 교차 지점의 통과 순서를 정하는 규칙을 차례로 더했습니다. 하드웨어는 엔코더 보드 PCB를 뒤에서 말씀드리겠습니다. (전환)""",
    [('week-07-1 18쪽', '리보틱스 미팅 질문 — 다중 차량: 현장 동시 투입 대수 · 중앙 관제 서버 유무'),
     (FIVE, 'NVIDIA 창고 5대'), (WORLDS_PLAN, '무작위 공장 3종 · 트럭 5 · 10 · 20대'),
     (WINDOWS, '7절 판정: 트럭 겹침 0 · 60 s 넘는 서로 기다림 · gridlock 0 (seed 600–604, 119 칸)')],
    '그림: tw24_rack600 조감 영상 450 s 프레임의 지도 칸 (prepare_clips.py)')

# ----------------------------------------------------------------- 3
add('왜 교통 관리', '02  왜 교통 관리가 필요한가', 60, f"""
<h2 class="headline">회전 반경 3.45 m, 통로 폭 약 3.5 m라 통로에서 마주치면 비켜설 수 없음</h2>
<div class="split grow" style="grid-template-columns:1.55fr 1fr;gap:26px">
<div class="m7-media">{video('71_warehouse5.mp4', 'NVIDIA 창고를 위에서 본 지게차 5대. 각자 랙 통로 끝의 팔레트를 집어 후진으로 나와 출하장에 내리고 주차장으로 돌아옴')}
{legend(('line', TRUCK, '트럭별 최근 30 s 이동 경로'), ('ring', WAIT, '다른 트럭이 지나갈 때까지 대기'))}</div>
<table class="comparison t7">
<tr><th>항목</th><th>값</th></tr>
<tr><td>공장</td><td>NVIDIA 창고 31.6 × 53.8 m</td></tr>
<tr><td>지게차</td><td>5대 동시 운반 (실측 차체 모델)</td></tr>
<tr><td>랙 통로 폭</td><td>2.85–3.74 m</td></tr>
<tr><td>최소 회전 반경</td><td>3.45 m (조향각 15°)</td></tr>
<tr><td>결과</td><td class="blue"><b>5대 모두 겹치지 않고 완주</b></td></tr>
</table>
</div>
<div class="takeaway">마주친 뒤 한 대가 비키는 방식은 쓸 수 없어, 마주치기 전에 중앙에서 순서를 정해야 합니다</div>
""",
    """왜 교통 관리가 필요한지부터 말씀드리겠습니다. 영상은 NVIDIA가 제공하는 창고에서 5대가 동시에 팔레트를 옮기는 장면입니다. 트럭마다 랙 통로 끝에 있는 팔레트를 집고, 통로를 후진으로 빠져나와 아래쪽 출하장에 내린 뒤 주차장으로 돌아옵니다. 문제는 지난주에 잰 실제 차체의 조향각이 15도라서 최소 회전 반경이 3.45미터라는 점입니다. 랙 사이 통로 폭이 3.5미터 안팎이라 통로 안에서는 돌아설 수도 없고, 두 대가 마주치면 옆으로 비켜설 수도 없습니다. 그래서 마주친 다음에 피하는 방식은 쓸 수 없고, 중앙에서 각 트럭의 경로를 보고 마주치기 전에 순서를 정해 줘야 합니다. 빨간 고리가 다른 트럭이 지나가기를 기다리는 트럭입니다. 이 방식으로 5대 모두 서로 겹치지 않고 임무를 끝냈습니다. (전환)""",
    [(FIVE, '창고 실측: 실내 31.6 × 53.8 m, 통로 폭 3.56 · 3.71 · 3.74 · 3.53 · 2.85 · 3.57 m, 실측 차체 계획 곡률 0.29 1/m (최소 회전 반경 3.45 m), 통로 하나 = 트럭 하나'),
     ('ws1 artifacts/20261008_fleet/runs/f2d_truth_seed0/result.json', 'success · completed 5 · violation_count 0 · route_conflicts 0 · 시뮬레이션 517 s, 위치 = 시뮬레이터 정답 (job 1916)'),
     (BRANCH, 'tools/compose_fleet_video.py — 트럭 색 선: 최근 30 s 실제 궤적, 빨간 고리: 교통 대기')],
    '영상: f2d_truth_seed0_overlay.mp4 지도 칸, 4배속 (prepare_clips.py)')

# ----------------------------------------------------------------- 4
add('교통 규칙', '03  교통 규칙', 70, f"""
<h2 class="headline">앞길을 미리 예약하고, 다른 트럭이 지나갈 자리에는 서지 않는 교통 규칙</h2>
<div class="rule7 grow">
<div class="m7-media">{video('72_close_a.mp4', '랙 창고를 가까이 본 Isaac 렌더. 청록 트럭의 다음 구간이 노랑 트럭의 예약 구간과 겹쳐, 노랑 트럭이 지나갈 때까지 그 앞에서 기다림')}<p class="rcap"><b>①</b> 다음 구간이 다른 트럭의 예약과 겹치면 그 앞에서 대기</p></div>
<div class="m7-media">{video('72_close_b.mp4', '랙 창고를 가까이 본 Isaac 렌더. 연두 트럭이 들어가면 먼저 지나갈 파랑 트럭의 길 위에 서게 되므로, 진입 전에 기다림')}<p class="rcap"><b>②</b> 들어가면 먼저 지나갈 트럭의 길 위에 서게 되므로 진입 전에 대기</p></div>
{legend(('band', TRUCK, '예약 구간 (그 트럭만 달릴 수 있음)'), ('dots', TRUCK, '남은 경로'), ('diamond', TRUCK, '교차 지점 (색은 먼저 지나갈 트럭)'), ('ring', TA_WAIT, '대기 (선은 기다리는 상대로)'))}
</div>
<div class="takeaway">기다리는 트럭은 늘 앞서 갈 트럭의 길 밖에 서 있으므로, 앞선 트럭부터 차례로 지나가 교착이 생기지 않습니다</div>
""",
    """규칙은 크게 두 가지입니다. 첫째, 트럭은 자기 경로의 앞부분을 중앙 관리자에게 예약받고, 그 예약 구간 안에서만 달립니다. 색 띠가 예약 구간으로, 차체보다 0.3미터 넓게 잡아 위치 오차를 덮습니다. 왼쪽처럼 다음 구간이 다른 트럭의 예약과 겹치면 그 앞에서 멈춰 기다립니다. 둘째, 경로가 서로 교차하는 지점마다 어느 트럭이 먼저 지나갈지를 미리 정합니다. 마름모가 교차 지점이고, 색이 먼저 지나갈 트럭입니다. 오른쪽에서 연두 트럭은 그대로 들어가면 먼저 지나갈 파랑 트럭의 길 위에 서게 되므로, 끝까지 지나갈 수 있을 때까지 들어가지 않고 기다립니다. 즉 기다리는 자리는 다른 트럭이 지나갈 길 위가 아니어야 합니다. 철도에서 한 구간에 열차 한 대만 들어가게 하는 것과 같은 생각입니다. 이렇게 하면 기다리는 트럭은 늘 앞서 갈 트럭의 길 밖에 서 있으므로, 앞선 트럭부터 차례로 지나가고 서로 막혀 아무도 못 움직이는 교착이 생기지 않습니다. (전환)""",
    [(FIVE, '교통 관리 v2: 구간 점유(여유 0.3 m), 고정 순번, 정차 규정, 교착 없음 논증과 전제'),
     (WINDOWS, '교차 시간 창(v24): 교차마다 통표(먼저 지나갈 트럭), 발급 30 s · 여유 10 s'),
     ('ws1 ~/w7deck/exp/runs/close_rack600', '같은 실행(tw24_rack600: 랙 seed 600 · 트럭 8 · 사람 8 · 고장 · 시간 창 · 꾸민 장면)을 카메라만 (47, 40.4) m 위 36 m 폭으로 옮겨 405 s 까지 다시 렌더 (source_v27 + 카메라 인자 2 개, job 2568) — 트럭 궤적이 원래 실행과 0.0 m 차이로 같음'),
     ('tools/explain_tablets.py (job 2564)', '대기 장면과 이유: ① T5 가 T2 의 통표와 겹쳐 대기(236.3–277.9 s) · ② T7 이 들어가면 T1 의 남은 경로 위에 서게 되어 대기(정차 규정, 349.8–399.5 s)'),
     (BRANCH, 'tools/compose_world_video.py — 색 띠: 점유 구간, 점: 남은 경로, 마름모: 교차 통표, 고리: 대기')],
    '영상: close_rack600 합성 영상(compose_world_video.py --speed 1)의 두 대기 장면, 3배속 (prepare_clips.py)')

# ----------------------------------------------------------------- 5
COND = [
    ('기본', '트럭 5 · 10 · 20대'),
    ('고장', '트럭 고장과 쏟아진 짐'),
    ('통신', '0.5 s 지연과 20 % 손실'),
    ('위치 오차', '최대 0.17 m'),
    ('사람', '10명이 걸어 다님'),
    ('전부', '위 네 가지 동시'),
]
cond_head = ''.join(f'<th>{a}</th>' for a, _ in COND)
cond_cells = ''.join(f'<td>{b}</td>' for _, b in COND)
add('시험 환경', '04  시험 환경', 50, f"""
<h2 class="headline">무작위로 만든 공장 3종에서 6가지 상황으로 30분씩 연속 운반</h2>
<div class="env7 grow">
<figure class="shot"><img class="media" src="assets/73_rack.jpg" alt="랙 창고"><figcaption>랙 창고 82 × 58 m</figcaption></figure>
<figure class="shot"><img class="media" src="assets/73_shop.jpg" alt="기계가 흩어진 공정 공장"><figcaption>공정 공장 76 × 75 m</figcaption></figure>
<figure class="shot"><img class="media" src="assets/73_multi.jpg" alt="두 홀을 문으로 이은 복합동"><figcaption>복합동 92 × 51 m</figcaption></figure>
</div>
<table class="comparison t7 cond7"><tr>{cond_head}</tr><tr>{cond_cells}</tr></table>
<div class="takeaway">공장 배치를 바꿔 가며 120회를 CPU로 계산하고, 대표 장면은 Isaac Sim 물리 시뮬레이션으로 확인했습니다</div>
""",
    """시험 환경입니다. 창고 하나로는 부족해서 공장을 무작위로 만드는 생성기를 만들었습니다. 구조는 랙이 늘어선 창고, 기계가 흩어진 공정 공장, 그리고 두 홀을 문과 좁은 통로로 이은 복합동 세 가지이고, 실행할 때마다 크기와 배치, 트럭 출발 위치, 팔레트 위치가 바뀝니다. 그림은 그중 한 배치입니다. 상황은 여섯 가지입니다. 기본 상황에서 트럭 수를 5대, 10대, 20대로 늘리고, 트럭이 고장 나거나 통로에 짐이 쏟아지는 경우, 통신이 늦거나 끊기는 경우, 트럭이 아는 위치가 SLAM 오차만큼 틀린 경우, 교통 관리가 모르는 사람이 돌아다니는 경우, 그리고 이것을 모두 합친 경우를 넣었습니다. 각 실행은 30분 동안 작업을 계속 받아 운반합니다. 공장 배치를 다섯 개씩 바꿔서 모두 120번을 CPU 계산으로 돌렸고, 대표 장면은 Isaac Sim 물리 시뮬레이션으로 다시 확인했습니다. (전환)""",
    [(WORLDS_PLAN, 'W0 구조 3 종(랙 70–110 × 45–70 m, 공정 60–100 × 50–80 m, 복합동 = 홀 2–3 개 + 문 · 한 차로 연결 통로), W3 장애, W4 보행자 1.2 m/s, W5 행렬 C0–C5 · 1,800 s'),
     (f'{W}/runs/tw24_{{rack,shop,multi}}600/result.json', 'seed 600 크기: 랙 82.34 × 58.22, 공정 75.74 × 74.88, 복합동 91.65 × 51.1 m'),
     (WINDOWS, '7절: seed 600–604, 120 칸 중 multi_604_C0_20 은 출발 배치 생성 실패로 제외 → 119 칸')],
    '그림: tw24_*600 조감 영상 450 s 프레임의 지도 칸 (prepare_clips.py)')

# ----------------------------------------------------------------- 6
DEAD = bars([('앞길 예약만', 15, ORANGE), ('+ 막히면 우회', 0, BLUE)], 20, '회',
            '영영 막힌 실행 수. 앞길 예약만 15회, 막히면 우회를 더하면 0회 (119회 중)')
LONG = bars([('+ 막히면 우회', 1542, GREY), ('+ 교차 순서', 576, BLUE)], 1800, '번',
            '60초 넘게 기다린 횟수. 막히면 우회까지 1,542번, 교차 순서를 더하면 576번 (119회 합)')
add('막힘 줄이기', '05  막힘 줄이기', 80, f"""
<h2 class="headline">막히면 우회하고 교차 지점 순서를 정해 영영 막힌 실행 15회 → 0회, 긴 대기 약 1/3로</h2>
<div class="phase-flow steps3"><b>① 앞길 예약과 순번</b><span class="arrow">→</span><b>② 20 s 막히면 다른 길로 우회</b><span class="arrow">→</span><b>③ 교차 지점마다 지나갈 순서와 시각 예약</b></div>
<div class="split grow" style="gap:30px">
<div class="chart7"><p class="panel-h">영영 막힌 실행 <span class="muted">(119회 중, 평가 배치 A)</span></p>{DEAD}</div>
<div class="chart7"><p class="panel-h">60 s 넘게 기다린 횟수 <span class="muted">(119회 합, 평가 배치 B)</span></p>{LONG}</div>
</div>
<div class="takeaway">모든 실행에서 트럭끼리 겹친 적은 없고, 남은 긴 대기는 고장 났거나 사람 앞에 선 트럭 때문입니다</div>
""",
    """그런데 이 시험에서 처음 규칙만으로는 막히는 경우가 나왔습니다. 고장이나 쏟아진 짐 때문에 트럭이 경로를 다시 짜면 순번이 바뀌는데, 이때 앞 장의 전제, 즉 기다리는 트럭이 앞 순번 트럭의 길 밖에 선다는 조건이 깨집니다. 그래서 공장 배치 다섯 개로 돌린 119번 중 15번은 서로를 기다리며 끝까지 풀리지 않았습니다. 그래서 규칙을 두 단계 더했습니다. 먼저 20초 넘게 막히면 다른 길로 돌아가고, 60초 넘게 기다리면 상대의 남은 경로를 벽으로 보고 비켜 가는 규칙입니다. 이것을 더하자 같은 119번에서 영영 막힌 실행이 0이 됐습니다. 다음으로 앞 장에서 본 교차 지점 규칙, 즉 교차 지점마다 어느 트럭이 먼저, 언제 지나갈지를 미리 정하고 그 시간 안에 오지 못하면 순서를 바꾸는 규칙을 더했습니다. 다른 공장 배치 다섯 개로 견주었을 때 60초 넘게 기다린 횟수가 1,542번에서 576번으로 약 3분의 1이 됐고, 영영 막힌 실행은 여전히 0이었습니다. 두 비교는 각각 같은 배치끼리 견준 값입니다. 모든 실행에서 트럭끼리 겹친 적은 없었고, 남은 긴 대기는 고장 난 트럭이나 사람 앞에 선 트럭 때문으로, 교통 규칙이 다루는 범위 밖입니다. (전환)""",
    [(TARA, '3절 평가 seed 300–304 (119 칸, gate1 1004674 · 1004880): 「영영 안 풀리는 교착」(60 s 넘는 서로 기다림 또는 gridlock) v14 15 칸 → v18 0 칸, 트럭 겹침 0 · 0'),
     (WINDOWS, '7절 평가 seed 600–604 (119 칸): 60 s 이상 대기 v18y 1,542 → v24 576, 300 s 이상 60 → 11, 가장 긴 서로 기다림 20 → 1 s, 트럭 겹침 0. v18y = v24 와 같은 코드에서 시간 창만 끈 판(순번 + 비켜 주기), v18 1,539'),
     (TARA, 'TA: 20 s 막히면 우회 경로 · RA: 60 s 기다리면 선순위 남은 경로를 벽(20 m)으로 보고 우회'),
     (WINDOWS, '교차 시간 창: 발급 30 s · 여유 10 s, 만료하면 순서 다시 정함; 사람 접촉 판정은 세 판 모두 미달(166–193 표본, 대부분 rack_601_C5_10)')],
    '그래프: 각 비교는 같은 평가 배치 · 같은 119 칸끼리 (판 이름 v14 · v18 · v24 는 화면에서 생략)')

# ----------------------------------------------------------------- 7
ISAAC = [
    ('랙 창고', '16건', '0', '0', '0'),
    ('공정 공장', '15건', '0', '0', '1회'),
    ('복합동 A', '9건', '0', '0', '0'),
    ('복합동 B', '14건', '0', '0', '0'),
]
isaac_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td class="blue"><b>{c}</b></td><td class="blue"><b>{d}</b></td><td>{e}</td></tr>' for a, b, c, d, e in ISAAC)
add('물리 시뮬레이션', '06  물리 시뮬레이션 확인', 60, f"""
<h2 class="headline">트럭 8대와 사람 8명, 고장 1대가 있는 공장에서 20분 동안 겹침과 교착 없이 운반</h2>
<div class="split grow" style="grid-template-columns:1.25fr 1fr;gap:24px">
<div class="m7-media">{video('74_rack600.mp4', '무작위 랙 창고를 위에서 본 지게차 8대와 사람 8명. 트럭마다 색 띠로 앞길을 예약하고, 교차 지점의 마름모가 지나갈 순서를 표시함')}
{legend(('band', TRUCK, '예약 구간'), ('diamond', TRUCK, '교차 지점'), ('ring', WAIT, '대기'), ('ring', TA_WAIT, '20 s 넘게 대기'), ('dot', PERSON, '사람'))}</div>
<div class="stack" style="gap:12px">
<table class="comparison t7 isaac7"><tr><th>공장</th><th>완료</th><th>트럭 겹침</th><th>교착</th><th>사람 접촉</th></tr>{isaac_rows}</table>
<p class="small muted">실측 차체 모델로 Isaac Sim에서 20분 운용</p>
</div>
</div>
<div class="takeaway">위치는 시뮬레이터 정답을 썼고, 공장은 생성기가 만든 배치입니다 (실제 도면 아님)</div>
""",
    """같은 규칙을 Isaac Sim 물리 시뮬레이션에서도 확인했습니다. 실측 차체 모델 8대가 사람 8명이 돌아다니는 공장에서 20분 동안 작업을 계속 받아 운반하고, 중간에 한 대가 60초 동안 고장으로 멈추고 통로에 짐이 한 번 쏟아집니다. 영상은 랙 창고이고, 색 띠가 앞 장에서 말씀드린 예약 구간, 마름모가 교차 지점에서 먼저 지나갈 트럭입니다. 공장 네 곳에서 돌린 결과가 오른쪽 표입니다. 네 곳 모두 트럭끼리 겹치거나 영영 막힌 적이 없었습니다. 공정 공장에서 움직이는 트럭이 사람과 한 번 닿았는데, 이것은 다음 장의 한계에서 말씀드리겠습니다. 다만 위치는 시뮬레이터가 알려 주는 정답 위치를 썼고, 공장은 생성기가 만든 것이라 실제 도면은 아닙니다. (전환)""",
    [(WINDOWS, '8절 Isaac 대표(v24, ws1 source_v27, 트럭 8 · 사람 8 · 일시 고장 60 s · 쏟아진 짐 1 · 1,200 s): 랙 600 작업 16 · 공정 600 15 · 복합동 600 9 · 복합동 200 14, 트럭 겹침 0, 60 s 넘는 서로 기다림 0 (공정 600 의 4 번은 최장 40 s), 움직이는 트럭-사람 접촉 공정 600 1 표본(0.1 s)'),
     (WINDOWS, '복합동 600 팔레트 접촉 3,574 표본 = 운반 중 빠진 팔레트를 다른 트럭이 밂 (교통 규칙 밖)'),
     (f'{W}/videos/tw24_rack600.mp4', 'ws1 job 2441 실행 · 2442 합성, 영상 400 s = 시뮬레이션 1,200 s')],
    '영상: tw24_rack600.mp4 지도 칸, 5배속 (prepare_clips.py); 표의 복합동 A = seed 600, B = seed 200')

# ----------------------------------------------------------------- 8
LIMITS = [
    ('위치', '시뮬레이터 정답', '5대가 각자 SLAM 위치로 달린 시험에서 대기 중 멈춤 (원인 분석 전)'),
    ('사람', '움직이는 트럭과 접촉 남음', '보호 영역이 앞쪽뿐이라 옆이나 모서리로 오는 사람을 못 봄 (추정)'),
    ('운반 중 팔레트', '포크 위에서 미끄러져 떨어지는 경우', '원인을 아직 모르고, 떨어진 팔레트를 장애물로 못 봄'),
    ('경로 계산', '복합동에서 계산이 길고 실패 많음', '경로 탐색 한도와 계산 시간 개선'),
    ('통신과 서버', '지연과 손실은 모의로만 넣음', '실제 무선망과 중앙 서버 구성 (6주차 피드백)'),
]
limit_rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in LIMITS)
add('남은 한계', '07  남은 한계', 60, f"""
<h2 class="headline">SLAM 위치로 여러 대 동시 주행, 사람 감지 범위, 운반 중 팔레트가 남은 과제</h2>
<table class="comparison t7 lim7 grow"><tr><th>항목</th><th>현재</th><th>원인과 다음 단계</th></tr>{limit_rows}</table>
<div class="takeaway">중앙 서버가 모든 트럭의 위치와 경로를 바로 안다고 가정했습니다 (실물 통신 미구현)</div>
""",
    """남은 한계입니다. 첫째, 위치는 아직 시뮬레이터의 정답 위치입니다. 트럭마다 SLAM을 하나씩 돌려 5대를 동시에 움직이는 시험도 한 번 해 봤는데, 교통 대기 중에 차들이 멈춘 채 끝나서 원인을 분석해야 합니다. 둘째, 움직이는 트럭이 사람과 닿는 경우가 남았습니다. 사람을 보고 멈추는 보호 영역을 진행 방향 앞쪽에만 두어서, 옆이나 모서리로 다가오는 사람을 못 보는 것으로 보입니다. 셋째, 물리 시뮬레이션에서 운반 중에 포크 위 팔레트가 미끄러져 떨어지는 경우가 있었고, 떨어진 팔레트를 다른 트럭이 장애물로 보지 못했습니다. 넷째, 복합동처럼 큰 공장에서는 경로 계산이 오래 걸리고 실패도 많습니다. 마지막으로, 지금은 중앙 서버가 모든 트럭의 위치와 경로를 바로 안다고 가정했고, 통신 지연과 손실도 모의로만 넣었습니다. 지난주 피드백에서 무선 통신을 아직 고려하지 않았다고 말씀드렸는데, 실제 무선망과 서버 구성은 이 부분과 함께 정하겠습니다. (전환)""",
    [('ws1 artifacts/20261008_fleet/runs/f3_slam_seed5 · f3b_slam_seed5', 'pose_source "slam on travel stages", success false, completed 1, stopped "gridlock: no truck moved for 120 s" (515 · 555 s), violation_count 0'),
     (WORLDS, '3절: 움직이며 사람 접촉 — v14 보호 영역이 진행 방향 띠라 옆면 · 모서리 빈틈(추정); 4절: 운반 중 팔레트 회전 · 빠짐, 원인 미정, 진짜 팔레트는 보호 영역에서 「아는 물체」로 빠짐'),
     (WINDOWS, '7절: 사람 접촉 v24 166 표본; 복합동 계획 실패 대부분 expansion_limit; 8절 복합동 600 팔레트 빠짐'),
     (WORLDS_PLAN, 'W3 통신: 지연 0.5 s · 허가 손실 20 % (CPU 모형)'),
     ('docs/references/week6_feedback.md', '5절 무선 통신: 지게차–PC · 지게차–지게차 미고려')],
    '출처: 다중 지게차 계획 · 실행 기록')

# ----------------------------------------------------------------- 9 PCB
add('엔코더 보드 PCB', '08  엔코더 보드 PCB', 70, """
<h2 class="headline">KTH7801 (SOP-8) 절대각 엔코더 보드를 2×4 박스 헤더로 MCU 보드와 SPI 연결</h2>
<div class="pcb7 grow">
<div class="pcbimgs">
<p class="rl">2.54 mm</p>
<figure class="shot"><img class="media" src="assets/75_enc_top.jpg" alt="KTH7801 보드 2.54 mm 판 앞면. 왼쪽에 8핀 칩 U2(KTH7801)와 고정 구멍 두 개, 가운데 C1 · C3 · R4, 오른쪽에 2열 4핀 단자"><figcaption>앞면</figcaption></figure>
<figure class="shot"><img class="media" src="assets/75_enc_bottom.jpg" alt="KTH7801 보드 2.54 mm 판 뒷면. 2열 4핀 박스 헤더가 보드보다 크게 나와 있음"><figcaption>뒷면 (박스 헤더)</figcaption></figure>
<p class="rl">1.27 mm</p>
<figure class="shot"><img class="media" src="assets/75_enc127_top.jpg" alt="KTH7801 보드 1.27 mm 판(V1.0.1) 앞면. 같은 부품 배치에 2열 4핀 단자가 촘촘해짐"><figcaption>앞면</figcaption></figure>
<figure class="shot"><img class="media" src="assets/75_enc127_layout.jpg" alt="KTH7801 보드 1.27 mm 판(V1.0.1) PCB 배치도. 2열 4핀 커넥터 CN1 에 3V3, CS, CLK, MOSI, MISO, GND 가 배정되어 있고 실크에 KTH_Enc V1.0.1"><figcaption>배치도 (CN1 핀 배정)</figcaption></figure>
</div>
<table class="comparison t7 pcbq7">
<tr><th>핀 간격</th><th>2.54 mm</th><th>1.27 mm</th></tr>
<tr><td>커넥터 크기</td><td>보드보다 큼</td><td class="blue"><b>가로와 세로 약 절반</b></td></tr>
<tr><td>납땜</td><td class="blue"><b>손납땜 쉬움</b></td><td>정밀 납땜 필요</td></tr>
<tr><td>케이블 구하기</td><td class="blue"><b>납작 케이블 흔함</b></td><td>선택지 적음</td></tr>
</table>
</div>
<div class="takeaway">엔코더 커넥터 핀 간격은 2.54 mm (납땜이 쉬움)와 1.27 mm (보드가 작아짐) 중 어느 쪽이 나을까요?</div>
""",
    """하드웨어는 엔코더 보드 PCB입니다. 절대각 엔코더 칩은 5주차에 말씀드린 MT6701 대신 자석식 각도 센서 KTH7801로 정했습니다. 이 장의 두 판이 KTH7801 보드로, SOP-8 패키지 칩을 올리고 2열 4핀 박스 헤더로 MCU 보드와 SPI로 연결합니다. 위가 2.54밀리미터 커넥터 판, 아래가 1.27밀리미터 커넥터로 바꾼 판입니다. 아래 오른쪽은 1.27밀리미터 판의 배치도로, 커넥터 여덟 핀에 전원과 SPI 신호를 배정했습니다. 2.54밀리미터 판은 뒷면 커넥터가 보드보다 크게 튀어나와 있습니다. 그래서 두 판을 모두 그려 봤고, 어느 쪽으로 갈지 여쭤보고 싶습니다. 1.27밀리미터로 바꾸면 커넥터가 가로세로 절반 정도로 줄어 보드를 작게 만들 수 있지만, 납땜이 까다롭고 맞는 케이블의 선택지가 적습니다. 2.54밀리미터는 크지만 손납땜이 쉽고 박스 헤더용 납작 케이블을 쉽게 구할 수 있습니다. 실차에 달 때 어느 쪽이 나은지 의견 부탁드립니다. (전환)""",
    [('팀 PCB 3D 렌더 (2026-10-14, 팀원 공유)', 'KTH7801 절대각 엔코더 보드 앞면 · 뒷면 — U2(KTH7801, SOP-8; 2.54 mm 판과 1.27 mm 판 모두 KTH7801 보드, 사용자 확인 2026-10-14, 1.27 mm 판 배치도 실크 KTH_Enc V1.0.1) · C1 · C3 · R4 · 2×4 박스 헤더 · 고정 구멍 2개; 같은 날 커넥터를 1.27 mm 로 줄인 판(V1.0.1)의 3D 앞면과 PCB 배치도 — CN1 핀 1 3V3 · 2 CS · 4 CLK · 6 MOSI · 7 GND · 8 MISO'),
     ('week-05/build_deck.py 8쪽', '5주차 회로 초안: MT6701 증분판(ABZ) · 절대각판(SSI), 같은 2.54 mm 2×4 헤더'),
     ('사용자 (2026-10-14)', '절대각 엔코더는 KTH7801 사용, MT6701 보드와 KTH7801 보드를 구별해 넣을 것 (MT6701 보드 그림은 받으면 추가)'),
     ('KTH7801 제품 자료 (MEV Elektronik · LCSC C22459044)', 'CONNTEK 자석식 각도 센서, SOP-8 판은 SPI · PWM'),
     ('팀 메시지 (2026-10-14)', '「교수님에게 2.54 VS 1.27 물어보죠」'),
     ('비교 표', '1.27 mm 는 2.54 mm 의 절반 간격 — 같은 핀 수면 커넥터 가로 · 세로가 약 절반 (기하 계산, 하우징 두께 제외)')],
    '그림: 팀 KTH7801 보드 PCB 자료 네 장 — 2.54 mm 판 앞 · 뒷면 3D, 1.27 mm 판(V1.0.1) 앞면 3D와 배치도 (배경만 잘라 냄)')

# ----------------------------------------------------------------- 10
NEXT_ROWS = [
    ('다중 지게차', '위치는 시뮬레이터 정답', '트럭마다 SLAM 위치로 동시 주행'),
    ('다중 지게차', '보호 영역이 진행 방향 앞쪽뿐', '차체 둘레 전체로 넓혀 사람 접촉 없애기'),
    ('다중 지게차', '중앙 서버와 통신은 가정', '리보틱스 답변(투입 대수, 관제)을 보고 범위 확정'),
    ('1대 운반', '포크 간격을 실측 범위(0.37 m)로 바꿈', '삽입 중 위치 추적 다시 검증'),
    ('하드웨어', '엔코더 보드 PCB 3D 설계', '커넥터 핀 간격 결정 후 제작'),
]


def _next_table():
    rows, seen, done = [], {}, set()
    for g, a, b in NEXT_ROWS:
        seen[g] = seen.get(g, 0) + 1
    for g, a, b in NEXT_ROWS:
        head = '' if g in done else f'<td class="grp" rowspan="{seen[g]}">{g}</td>'
        done.add(g)
        rows.append(f'<tr>{head}<td class="cur">{a}</td><td class="arrow">→</td><td class="nxt">{b}</td></tr>')
    return ''.join(rows)


add('다음 작업', '09  다음 작업', 50, f"""
<h2 class="headline">SLAM 위치로 여러 대 동시 주행, 사람 감지 범위 넓히기, 엔코더 보드 제작</h2>
<table class="comparison plan6 grow"><tr><th class="c1">구분</th><th class="c2">현재</th><th class="c3"></th><th class="c4">다음 단계</th></tr>{_next_table()}</table>
<div class="takeaway">다음 목표는 시뮬레이터 정답 위치 없이 여러 대를 운용하고 엔코더 보드를 만드는 것입니다</div>
""",
    """정리하겠습니다. 이번 주에는 지게차 여러 대가 같은 공장에서 겹치거나 막히지 않고 다니는 교통 관리를 시뮬레이션으로 만들었습니다. 다음 단계는 시뮬레이터의 정답 위치 대신 트럭마다 SLAM으로 추정한 위치로 여러 대를 함께 움직이는 것이고, 사람을 보는 보호 영역을 차체 둘레 전체로 넓혀 사람과 닿는 경우를 없애겠습니다. 중앙 서버와 통신을 어느 정도까지 만들지는 리보틱스 미팅에서 현장 투입 대수와 관제 서버 답변을 듣고 정하겠습니다. 한 대 운반 쪽은 포크 간격을 실측 범위 안의 0.37미터로 바꿨기 때문에, 포크를 넣는 동안의 위치 추적을 다시 검증하고 있습니다. 하드웨어는 커넥터 핀 간격을 정한 뒤 엔코더 보드를 제작하겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [('forklift d47d4d0', 'dls08_measured fork_spacing_m 0.29 → 0.3725 (실측 범위 안의 수동 설정값)'),
     ('forklift 7f07659', 'D5 v11 계획 6판 — 삽입 중 추적 재검증'),
     ('week-07-1 18쪽', '리보틱스 미팅 질문 — 현장 동시 투입 대수 · 중앙 관제 서버')],
    '출처: 다중 지게차 실행 기록 · 로봇 저장소 이력')

TITLE = '7주차 자율 지게차 개발'
TOTAL = 560


def build():
    assert len(slides) == 10, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-10-14. 다중 지게차 결과는 모두 시뮬레이션(CPU 운동학 · Isaac Sim 합성 장면)이며, 위치는 시뮬레이터 정답, '
              '공장은 생성기가 만든 가상 배치다. 실제 장비 성능이 아니다. '
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
