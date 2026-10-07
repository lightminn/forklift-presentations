"""Build the week 6 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 6 is a software (simulation) week only: no hardware topics (user,
2026-10-06). The plan and its three reviews are in PLAN.md. Every result comes
from a different run with different inputs, so each slide carries a condition
line saying which of position, obstacles and pallet pose came from the
simulator's ground truth and which from sensing. The clips are cut by
prepare_clips.py; the LiDAR map clip is week 5's (prepare_videos.py).
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
NEARMOUNT = 'docs/validation/2026-10-03-near-field-mount-study.md'
NEARPLAN = 'docs/plans/2026-10-03-near-field-pocket-tracking.md'
CROWN = 'https://patents.google.com/patent/US9990535B2/en'
FACTORY = 'docs/validation/2026-09-26-factory-hall-and-isaac-slam.md'
SLAM = 'docs/validation/2026-10-04-online-slam-closed-loop.md'
LIDAR = 'docs/plans/2026-10-04-lidar-obstacle-map.md'
LAYER = 'config/obstacle_layer.yaml'
N1 = 'videos-from-ws1/20261006T1124Z_p5_slam_seed1_n1_planning_memory_no_pocket_check'
N2 = 'videos-from-ws1/20261006T1124Z_p5_slam_seed1_n2_planning_memory_no_pocket_check'
N2_OLD = 'videos-from-ws1/20261006T0431Z_p5_slam_seed1_n2_new_obstacle'
slides = []

SIM = 'Isaac Sim 합성 장면'
BLUE, ORANGE, GREY = '#2f74c0', '#c26a1a', '#9aa3ad'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def video(src, alt, cls='media'):
    poster = src.rsplit('.', 1)[0] + '_poster.jpg'
    poster_attr = f' poster="assets/{poster}"' if (ROOT / 'assets' / poster).exists() else ''
    return (f'<video class="{cls}" src="assets/{src}"{poster_attr} autoplay loop muted playsinline '
            f'aria-label="{escape(alt, quote=True)}"></video>')




# ----------------------------------------------------------------- charts
# Floor obstacles of the planner (props, stored pallets, clutter) whose height
# range meets a scan plane, from the S2 v3.8f records of layout seeds 1/3/5
# (LIDAR plan, section "현재 상태" ①). An upper bound: occlusion is ignored.
PLANE_REACH = {           # plane height label: reached per seed (1, 3, 5)
    '0.10–0.18 m': (90, 87, 87),
    '0.25 m': (74, 67, 70),
    '0.50 m': (64, 56, 59),
    '0.75 m': (47, 42, 45),
    '1.05 m': (42, 37, 38),
}
PLANE_TOTAL = (90, 87, 87)


def plane_chart():
    """One bar per plane height: the three layouts' share as dots on a bar
    to their mean; the current 1.05 m plane and the added 0.08 m planes marked."""
    left, width, top, row = 150, 400, 30, 62
    def x(p):
        return left + p / 100 * width
    parts = []
    for tick in (0, 50, 100):
        parts.append(f'<line x1="{x(tick):.1f}" y1="{top - 6}" x2="{x(tick):.1f}" y2="{top + row * 5 - 10}" stroke="#e3e6ea" stroke-width="1.5"/>'
                     f'<text x="{x(tick):.1f}" y="{top + row * 5 + 14}" text-anchor="middle" font-size="18" fill="#44505c">{tick} %</text>')
    for i, (name, reach) in enumerate(PLANE_REACH.items()):
        y = top + 22 + i * row
        shares = [100 * r / t for r, t in zip(reach, PLANE_TOTAL)]
        mean = sum(shares) / 3
        colour = ORANGE if name == '1.05 m' else (BLUE if name.startswith('0.10') else GREY)
        weight = '700' if colour != GREY else '400'
        parts.append(f'<text x="{left - 14}" y="{y + 7}" text-anchor="end" font-size="20" font-weight="{weight}" fill="#1b1f24">{name}</text>')
        parts.append(f'<rect x="{left}" y="{y - 18}" width="{x(mean) - left:.1f}" height="36" rx="3" fill="{colour}" opacity="0.35"/>')
        for s in shares:
            parts.append(f'<circle cx="{x(s):.1f}" cy="{y}" r="5" fill="{colour}" stroke="#fff" stroke-width="1.2"/>')
        lo, hi = min(shares), max(shares)
        txt = f'{lo:.0f}–{hi:.0f} %' if round(lo) != round(hi) else f'{hi:.0f} %'
        parts.append(f'<text x="{x(hi) + 12:.1f}" y="{y + 7}" font-size="20" font-weight="{weight}" fill="#1b1f24">{txt}</text>')
    return (f'<svg class="diagram" viewBox="0 0 640 {top + row * 5 + 24}" role="img" aria-label="LiDAR 설치 높이별로 레이저에 걸리는 바닥 장애물 비율. '
            f'1.05 m 43–47 %, 0.10–0.18 m 100 %"><g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


# Why wheel-only odometry drifts on the S3 seed 1 run (recomputed 2026-10-06
# from slam_log.npz joint samples: turn samples with model yaw rate > 0.05 rad/s;
# shortfall = 1 - sum(true*model)/sum(model^2)). Unloaded 0.998, loaded 0.925.
TURN_SHORTFALL = [('빈 차', 0.2), ('팔레트 적재', 7.5)]


def shortfall_chart():
    left, width, xmax = 150, 380, 8.0
    parts = []
    for i, (name, pct) in enumerate(TURN_SHORTFALL):
        y = 34 + i * 58
        colour = ORANGE if pct > 1 else GREY
        parts.append(f'<text x="{left - 14}" y="{y + 7}" text-anchor="end" font-size="21" font-weight="700" fill="#1b1f24">{name}</text>')
        parts.append(f'<rect x="{left}" y="{y - 18}" width="{max(4, pct / xmax * width):.1f}" height="36" rx="3" fill="{colour}"/>')
        parts.append(f'<text x="{left + max(4, pct / xmax * width) + 12:.1f}" y="{y + 8}" font-size="22" font-weight="700" fill="#1b1f24">{pct:.1f} %</text>')
    return (f'<svg class="diagram" viewBox="0 0 620 120" role="img" aria-label="회전할 때 바퀴·조향으로 계산한 것보다 실제로 덜 돈 비율. 빈 차 0.2 %, 팔레트 적재 7.5 %">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '6주차\n자율 지게차 개발', 20, '',
    """안녕하십니까. 6주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 주 결과는 모두 시뮬레이션이고, 하드웨어는 마지막 장에서 다음 작업으로만 말씀드리겠습니다. 지난주까지 지게차는 시뮬레이터가 알려 주는 정답 위치로 움직였는데, 이번 주에는 LiDAR로 추정한 위치로 운반 임무를 끝까지 했습니다. (전환)""",
    [(SLAM, '온라인 SLAM 폐루프 실행 기록'), (LIDAR, 'LiDAR 장애물 지도 계획')], '진행 보고')


# ----------------------------------------------------------------- sim settings
# Basis of the simulation's basic parameters (sources checked 2026-10-06; the
# full table with file:line is in SOURCES.md). kind: spec / photo / test / assume.
# Values taken as-is from a catalogue, standard or datasheet share one row
# (user, 2026-10-07: they were presented last week and need no itemising).
SIM_PARAMS = [
    ('규격이 있는 값', '차체 외형·무게 · 팔레트 · LiDAR · 카메라', 'spec', '카탈로그 · EPAL 6 규격 · 데이터시트 수치 그대로'),
    ('축간 · 바퀴 · 조향각', '0.66 m · 0.125 m · 15°', 'measure', '5주차 실측 차체 값'),
    ('바닥 장애물', 'LiDAR 높이 (1.05 m) 이상만', 'assume', '운용 가정 · 더 낮은 소품은 장면에서 뺌'),
    ('바퀴 · 팔레트 마찰', '정지 0.8 · 운동 0.7', 'assume', '고무–콘크리트 일반 범위 (약 0.6–0.9) 안의 값'),
    ('구동 토크', '바퀴당 3 N·m (네 바퀴)', 'assume', '적재 34 kg을 0.3 m/s²로 가속하는 힘의 약 9배'),
    ('운반 속도', '0.3 m/s', 'assume', '카탈로그 최고 5 km/h (1.4 m/s)의 약 1/5'),
    ('센서 잡음', '바퀴 0.2 rad/s · 조향 0.005 rad · 거리 2 cm', 'assume', '센서 실측 전 가정값 (실측 후 교체)'),
]
KIND = {'spec': ('규격·사양', '#2f74c0'), 'test': ('시험으로 선택', '#2e9a6b'), 'measure': ('실측', '#6a4fb3'), 'assume': ('가정', '#c26a1a')}
param_rows = ''.join(
    f'<tr><td>{a}</td><td>{v}</td><td><span class="kind" style="background:{KIND[k][1]}">{KIND[k][0]}</span> {why}</td></tr>'
    for a, v, k, why in SIM_PARAMS)
add('시뮬레이션 설정', '01  시뮬레이션 설정과 근거', 70, f"""
<h2 class="headline">시뮬레이션에 넣은 값과 그 근거</h2>
<table class="comparison params6 grow"><tr><th>항목</th><th>값</th><th>근거</th></tr>{param_rows}</table>
<div class="takeaway">실측으로 먼저 바꿀 가정값: 바퀴 마찰 · 센서 잡음 (위치 추정에 직접 영향)</div>
""",
    """오늘 보여 드리는 결과는 모두 시뮬레이션이라서, 먼저 시뮬레이션에 넣은 값과 그 근거부터 말씀드리겠습니다. 차체 외형과 무게, 팔레트, LiDAR와 카메라처럼 카탈로그나 데이터시트에 정확한 수치가 있는 값은 그대로 넣었습니다. 축간 거리와 바퀴 반지름, 최대 조향각은 지난주에 잰 실측값(조향각 15도)을 넣었습니다. 주황색은 가정값입니다. 바닥에는 LiDAR 높이보다 낮은 장애물이 없다고 가정하고, 그런 소품은 시뮬레이션 장면에서 뺐습니다. 바퀴 마찰은 고무와 콘크리트 사이의 일반적인 마찰 범위 안에서 잡았고, 구동 토크는 팔레트를 실은 34킬로그램을 정한 가속도로 움직이기에 충분하도록, 운반 속도는 카탈로그 최고 속도의 5분의 1 정도로 잡았습니다. 센서 잡음은 센서를 실제로 측정하기 전이라 가정값을 넣었습니다. 바퀴 마찰은 뒤에서 보실 바퀴 계산 위치의 오차를 좌우하므로, 센서 잡음과 함께 실측값이 나오면 먼저 바꿀 항목입니다. (전환)""",
    [('sim/models/dls08_measured/README.md', '실측 축간 0.66 m · 윤거 0.53 m · 바퀴 반지름 0.125 m · 최대 조향각 15° (이번 3–6쪽 실행에 쓴 모델, config/isaac_transport_measured.yaml)'),
     ('docs/decisions/0002-*.md', 'EPAL 6 실물 9–10 kg, DLS08 적재 능력 10 kg (카탈로그 12쪽)'),
     ('config/pallet_geometry_epal6.yaml', 'EPAL 6 공식 제품 시트'),
     ('config/isaac_slam_lidar.yaml', 'RPLIDAR A2M12 카탈로그 1,600빔·10 Hz·0.2–12 m'),
     ('config/isaac_perception_camera.yaml', 'hfov 1.204 rad(69°) — D435i 컬러 화각, 보정값 아님'),
     ('src/forklift_core/perception/pocket_clearance.py', '깊이 σ = 0.0036 z² (가정; 데이터시트 식 유도값 0.00344)'),
     ('config/isaac_transport.yaml', '시뮬레이터 전용 가정값 — 마찰 0.8/0.7(지게차·팔레트 충돌 형상에만 적용), 바퀴 토크 3 N·m, 운반 0.3 m/s'),
     ('src/forklift_core/localization/slam_pose.py', '오도메트리·거리 잡음 — 센서 사양 아닌 가정값'),
     ('ws1 artifacts/20261004_slam_s3/seed_1/run/slam_log.npz', '2026-10-06 재적분: 바퀴·조향 잡음 0·1·3·5배(조향 최대 0.025 rad ≈ 1.4°) → 끝 위치 오차 평균 346·346·351·359 cm (seed 5개)'),
     ('docs/plans/2026-10-04-lidar-obstacle-map.md', '장애물 LiDAR 배치 D_008 — 후보 비교 시험')],
    '근거 조사: 저장소 설정·결정·검증 문서 (2026-10-06)')

# ----------------------------------------------------------------- 2
add('캐리지 하단 카메라', '02  캐리지 하단 카메라', 65, f"""
<h2 class="headline">카메라를 캐리지 하단으로 옮겨 삽입 중에도 팔레트가 화면 안에</h2>
<div class="cam6 grow">
<div class="cam6-grid">
<p class="ch">기존 장착</p><p class="ch now">변경 장착</p>
<figure class="shot"><img class="media" src="assets/43_before_far.jpg" alt="기존 장착 카메라로 팔레트에 다가가는 화면. 팔레트와 두 포켓이 보임"><figcaption class="small muted">접근 중</figcaption></figure>
<figure class="shot"><img class="media" src="assets/43_camera_far.jpg" alt="새 장착 카메라로 팔레트에 다가가는 화면. 팔레트와 두 포켓을 찾은 표시"><figcaption class="small muted">접근 중</figcaption></figure>
<figure class="shot"><img class="media" src="assets/43_before_near.jpg" alt="기존 장착 카메라로 포크를 넣는 중의 화면. 팔레트가 화면 아래로 빠져 벽과 바닥만 보임"><figcaption class="small muted">삽입 중</figcaption></figure>
<figure class="shot"><img class="media" src="assets/43_camera_near.jpg" alt="새 장착 카메라로 포크를 넣는 중의 화면. 팔레트 윗판이 화면 안에 있음"><figcaption class="small muted">삽입 중</figcaption></figure>
</div>
<div class="stack" style="gap:0">
<table class="comparison t6">
<tr><th>항목</th><th>기존</th><th>변경</th></tr>
<tr><td>장착 위치</td><td>차체 앞 높은 곳</td><td class="blue"><b>캐리지 하단</b></td></tr>
<tr><td>기울기</td><td>수평</td><td class="blue"><b>아래로 약 6°</b></td></tr>
<tr><td>삽입 중 화면</td><td>마지막 약 0.25 m 화면 밖</td><td class="blue"><b>끝까지 화면 안 (포켓 → 윗판)</b></td></tr>
</table>
<p class="cap6" style="text-align:left;margin-top:10px">4주차 장착 사례 ② Crown 특허 방식 참고</p>
</div>
</div>
<div class="takeaway">좋아진 점: 포크를 넣는 동안에도 팔레트가 화면에 남음 → 넣으면서 위치를 다시 보고 바로잡을 수 있음 (추후 적용)</div>
""",
    """먼저 카메라 위치입니다. 왼쪽 열이 4주차까지 쓴 카메라로, 차체 앞 높은 곳에 수평으로 달려 있었습니다. 다가갈 때는 팔레트가 잘 보이지만, 포크를 넣기 시작하면 왼쪽 아래처럼 팔레트가 화면 아래로 빠져서 벽과 바닥만 보입니다. 그래서 4주차에 소개한 Crown 특허처럼 카메라를 캐리지(포크를 올리고 내리는 부분) 아래로 옮기고 살짝 아래로 숙였습니다. 오른쪽 열이 바꾼 카메라입니다. 다가갈 때는 포켓이 보이고, 포크를 넣는 동안에도 팔레트 윗판이 화면에 남습니다. 그래서 과제가 요구한 삽입 중 포켓 추적을 할 수 있는 화면을 확보했습니다. 다만 이번 시뮬레이션에서는 아직 팔레트 약 2미터 앞에서 한 번 더 본 위치로 넣고 있고, 넣는 동안 카메라로 다시 보고 바로잡는 기능은 다음 단계에서 넣겠습니다. (전환)""",
    [(CROWN, 'Crown 특허 US9990535B2 — 포크 캐리지 하단 장착 (4주차 장착 사례 ②)'),
     (NEARPLAN, '기존 장착(0.75, 0, 0.50 m · 틸트 0)의 마지막 약 0.25 m 무관측'),
     (NEARMOUNT, '장착 연구 — 높이 0.27 m · 틸트 0.10 rad, 12 장면 인계, 오차 ≤ 20 mm (잡음 0 · 정렬 · 승강 0)'),
     ('videos-from-ws1/20261007_l8_measured_seed1_m', 'camera_rgb.mp4 43 s(접근, 1.32 m) · 51 s(삽입 중) 프레임 — 실측 차체 · LiDAR 1대 실행, carriage_low_measured 장착'),
     ('forklift sim/isaac/run_transport.py', '이번 임무는 마지막 2.1 m 직진 시작에서 한 번 더 관측(near_capture) 후 그 위치로 삽입, 삽입 중 윗판 추적은 미연결 (근접 계획 보류)')],
    '화면 생성: 실측 차체 장면 1 임무의 로봇 카메라 프레임 (prepare_clips.py)')

# ----------------------------------------------------------------- 3
add('지도 작성', '03  2D LiDAR 지도 작성', 35, f"""
<h2 class="headline">LiDAR 스캔을 겹쳐 지도를 만들며 그 안에서 자기 위치 추정</h2>
<figure class="shot grow">{video('48_map_single.mp4', '왼쪽은 공장 홀을 위에서 본 지게차 주행, 오른쪽은 같은 순간까지 slam_toolbox가 만든 지도와 추정 경로')}<figcaption class="small muted">노랑: 계획 경로 · 빨강: SLAM 추정 · 파랑: 실제 경로 · 주황: LiDAR 장애물 칸 · 초록 원: 목적지</figcaption></figure>
<div class="takeaway">지도는 주행하면서 실시간으로 만들고, 위치 추정과 경로 계획에 바로 사용</div>
""",
    """다음은 위치를 추정하는 방법입니다. 지게차가 움직이면서 LiDAR로 주변 거리를 재면, slam_toolbox(공개 SLAM 패키지)가 이 스캔을 겹쳐 지도를 만들면서 그 지도 안에서 자기 위치를 찾습니다. 오른쪽처럼 움직일수록 지도가 넓어지고, 빨간 추정 경로가 파란 실제 경로를 따라갑니다. 이 지도는 주행하면서 실시간으로 만들어지고, 뒤에서 보실 위치 추정과 경로 계획에 그대로 쓰입니다. (전환)""",
    [('videos-from-ws1/20261007_l8_measured_seed1_m', '실측 차체 · LiDAR 1대 장면 1 임무, 온라인 slam_toolbox 지도와 추정 경로 (정답 위치 미사용)'),
     ('forklift bc4cc64', '1.15 m 미만 소품 제거 장면')],
    '화면 생성: ws1 l8_measured/seed_1_m 3분할 영상 처음 120 s 의 조감·SLAM 지도 두 칸 8배속 (prepare_clips.py single)')

# ----------------------------------------------------------------- 4
add('SLAM 위치로 운반', '04  SLAM 위치로 운반 임무', 50, f"""
<h2 class="headline">SLAM 위치 · LiDAR 1대 장애물 지도로 운반 임무 완주</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr;gap:32px">
<figure class="shot">{video('47_mission_single.mp4', '공장 홀을 위에서 본 지게차. 팔레트를 인식해 들고, 목적지에 내린 뒤 출발점으로 돌아온다')}</figure>
<div class="stack">
<table class="comparison t6">
<tr><th>입력</th><th>4주차</th><th>6주차</th></tr>
<tr><td>팔레트 위치</td><td>카메라 추정</td><td>카메라 추정</td></tr>
<tr><td>로봇 위치</td><td>시뮬레이터</td><td class="blue"><b>SLAM 추정</b></td></tr>
<tr><td>장애물</td><td>시뮬레이터</td><td class="blue"><b>LiDAR 1대 + SLAM 지도</b></td></tr>
<tr><td>목적지</td><td>시뮬레이터</td><td>시뮬레이터</td></tr>
</table>
</div>
</div>
<div class="takeaway">결과: 팔레트 인식부터 복귀까지 완주 · 하역 오차 8–65 mm (완주한 실행) · 포크 · 팔레트 충돌 없음</div>
""",
    """이번 주 가장 큰 진전입니다. 오른쪽 표처럼 4주차와 달라진 것은 로봇 위치와 장애물입니다. 시뮬레이터가 알려 주던 정답 위치 대신 slam_toolbox가 실시간으로 추정한 위치로 지게차를 움직이고, 경로를 짤 때 장애물은 LiDAR 한 대로 만든 장애물 지도와 SLAM 지도만 씁니다. 영상은 팔레트를 인식해 들어 올리고, 목적지에 내린 뒤 출발점으로 돌아오는 임무 전체를 위에서 본 것입니다. 정답 위치 없이 임무를 끝까지 마쳤고, 포크와 팔레트 충돌은 없었으며 팔레트를 내려놓은 위치 오차는 완주한 실행에서 8에서 65밀리미터였습니다. 목적지에서는 미리 등록해 둔 위치의 LiDAR 스캔과 맞춰 내려놓습니다. (전환)""",
    [('videos-from-ws1/20261007_l8_measured_seed1_m', 'result.json — success, 하역 23.8 mm, 재계획 0, 포켓 금지 접촉 0 (새 상자 없음)'),
     ('ws1 artifacts/20261005_p5_l3/l8_measured', '실측 차체 · LiDAR 1대 5회: 완주 3 (장면 1 임무 23.8 · 장면 1 복귀 중 상자 8.0 · 장면 5 운반 중 상자 64.9 mm → 8–65 mm), 실패 2 (장면 1 운반 중 상자 obstacle_no_progress · 장면 3 운반 중 상자 docking_unaligned)'),
     ('forklift bc4cc64', 'LiDAR 1대(1.05 m) 장애물 지도 + SLAM 지도로 경로 계획, 1.15 m 미만 소품 제거, 포켓 깊이 확인 끔, 잠정 차체 모델')],
    '화면 생성: ws1 l8_measured/seed_1_m 3분할 영상의 조감 칸만 12배속 (prepare_clips.py single)')

# ----------------------------------------------------------------- 4b
add('SLAM 위치 정확도', '05  SLAM 위치 정확도', 90, f"""
<h2 class="headline">끝 시점 위치 오차: 바퀴 회전만 계산하면 3.4 m → SLAM은 약 4 cm</h2>
<div class="split grow" style="grid-template-columns:0.85fr 1.15fr">
<figure class="shot">{video('45_slam_error.mp4', '이전 SLAM 운반 실행에서 slam_toolbox가 만든 지도와 추정 경로. 아래 숫자는 SLAM 위치 오차와 바퀴 회전만으로 계산한 위치의 오차')}<figcaption class="small muted">빨강: SLAM · 주황: 바퀴 회전만 · 파랑: 실제</figcaption></figure>
<div class="stack" style="gap:26px">
<table class="comparison t6 causes6">
<tr><th>위치 추정</th><th>오차</th><th>이유</th></tr>
<tr><td>바퀴 회전만 계산</td><td>3.4 m<br>(끝 시점)</td><td>팔레트를 싣고 돌 때 계산보다 덜 돌아 방향이 24° 틀어짐 (주행 거리 오차는 93 m 중 0.7 m)</td></tr>
<tr><td>SLAM</td><td>약 4 cm<br>(끝 시점)</td><td>LiDAR 스캔을 지도와 맞춰 방향 · 위치를 계속 보정 (임무 전체 평균 9 cm)</td></tr>
</table>
<div class="why6"><p class="panel-h">회전할 때 계산보다 실제로 덜 돈 비율</p>{shortfall_chart()}</div>
</div>
</div>
<div class="takeaway">덜 도는 원인: 짐을 싣고 돌 때 바퀴 옆 미끄러짐 (추정 · 바퀴 마찰 가정값에 좌우) · 바퀴 · 조향 잡음을 꺼도 오차 거의 같음</div>
""",
    """SLAM 위치가 얼마나 정확한지는 이전 SLAM 운반 실행으로 보여 드리겠습니다. 왼쪽 지도에서 빨간 SLAM 추정 경로는 파란 실제 경로를 거의 그대로 따라가지만, 주황색으로 그린 바퀴 회전만으로 계산한 경로는 갈수록 벗어납니다. 아래 숫자를 보시면, 임무가 끝날 때 바퀴 회전만으로 계산한 위치는 3.4미터 어긋나고 SLAM은 약 4센티미터입니다. 왜 이만큼 어긋나는지 따져 보면, 달린 거리는 93미터 중 0.7미터만 틀렸고 대부분은 방향이 24도 틀어진 탓입니다. 방향은 팔레트를 싣고 돌 때 틀어졌습니다. 빈 차일 때는 계산한 만큼 돌지만, 팔레트를 실으면 실제로는 계산보다 7.5퍼센트 덜 돕니다. 팔레트 무게가 실리면 바퀴가 옆으로 미끄러지기 때문으로 보이고, 이 미끄러짐은 앞에서 말씀드린 가정값인 바퀴 마찰에 따라 달라집니다. 바퀴와 조향 잡음을 꺼도 오차가 거의 같아서, 잡음 탓은 아닙니다. 반면 SLAM은 LiDAR 스캔을 지도와 맞춰 방향과 위치를 계속 바로잡기 때문에 임무 전체 평균으로도 약 9센티미터였습니다. 실물에서도 짐을 실으면 같은 일이 생길 수 있어서, SLAM이 필요하다고 판단했습니다. (전환)""",
    [(SLAM, 'S3 장면 1 — 위치 RMSE 0.088 m · 최대 0.190 m, 358 s 에서 SLAM 4.0 cm 대 바퀴 오도메트리만 340 cm'),
     ('ws1 artifacts/20261004_slam_s3/seed_1/run/slam_log.npz', '2026-10-06 재계산: 거리 92.9 대 93.6 m, 끝 방향 오차 −24.3°, 잡음 끔 346 cm · −25.2°, 회전 시 실제/계산 비 빈 차 0.998 · 운반 0.925'),
     ('config/isaac_transport.yaml', '시뮬레이터 전용 가정값 — 팔레트 10 kg, 정지 0.8 · 동마찰 0.7 (차체 24 kg 은 카탈로그)')],
    '화면 생성: S3 seed 1 3분할 영상을 --draw-odometry 로 다시 합성(forklift df109cf), SLAM 지도 칸 12배속, 개발용 글자 가림 (prepare_clips.py)')

# ----------------------------------------------------------------- 6
S5N1 = 'videos-from-ws1/20261007_l8_measured_seed5_n1'
S1N2 = 'videos-from-ws1/20261007_l8_measured_seed1_n2'
add('새 장애물 재계획', '06  새 장애물 감지와 재계획', 50, f"""
<h2 class="headline">LiDAR 1대 장애물 지도로 운반 중 나타난 상자 감지 → 정지 → 새 경로로 재개</h2>
<div class="split grow" style="grid-template-columns:1.75fr 1fr;gap:28px">
<figure class="shot">{video('46_new_obstacle_single.mp4', '팔레트를 들고 운반하던 중 경로 위에 상자가 나타나자 멈추고, 새 경로로 바꿔 돌아가는 장면. 왼쪽은 위에서 본 주행, 오른쪽은 SLAM 지도와 LiDAR 장애물 칸')}<figcaption class="small muted">노랑: 현재 경로 · 회색: 직전 경로 (재계획 직후) · 주황: LiDAR 장애물 칸</figcaption></figure>
<div class="phase-flow vert"><b>① LiDAR가 경로 위 상자 감지</b><span class="arrow">↓</span><b>② 정지</b><span class="arrow">↓</span><b>③ 멈춘 자리에서 새 경로 계획</b><span class="arrow">↓</span><b>④ 후진 후 새 경로로 운반 재개</b></div>
</div>
<div class="takeaway">결과: 운반 중 · 복귀 중 나타난 상자 (높이 1.3 m) 모두 피해서 완주</div>
""",
    """다음은 임무 중에 새 장애물이 나타나는 경우입니다. 영상은 팔레트를 들고 운반하던 중 경로 위에 키 1.3미터 상자가 새로 나타나는 장면입니다. 지게차는 상자를 보고 바로 멈춘 뒤, 그 자리에서 새 경로를 짜서 조금 후진했다가 다시 출발합니다. 재계획 직후 잠깐 보이는 회색 선이 이전 경로, 노란 선이 바뀐 경로입니다. 복귀하는 길에 상자가 나타난 경우도 같은 방식으로 피해서 임무를 끝까지 마쳤습니다. (전환)""",
    [(S5N1, 'result.json — success, 하역 64.9 mm, 상자 출현 77.2 s · 정지 약 78 s · 재계획 94.3 s 후 후진 (운반 중)'),
     (S1N2, 'result.json — success, 하역 8.0 mm, 상자 출현 226.0 s · 재계획 227.7 s (복귀 중)'),
     ('forklift bc4cc64', '실측 차체(dls08_measured), LiDAR 1대(1.05 m) 장애물 지도 + SLAM 지도로 경로 계획, 1.15 m 미만 소품 제거, 새 상자 0.4 × 0.4 × 1.3 m, 포켓 깊이 확인 끔')],
    '화면 생성: ws1 l8_measured/seed_5_n1 3분할 영상 73–118 s 의 조감·SLAM 지도 두 칸 2배속 (prepare_clips.py single)')

# ----------------------------------------------------------------- 8
# (group, current, next). Hardware rows: week 5 drafts and this deck's assumptions.
NEXT_ROWS = [
    ('소프트웨어', 'LiDAR 1대 장애물 지도로 상자 회피', '여러 장면 · 과제 상황 C · D에서 반복'),
    ('소프트웨어', '실측 조향각 15°: 좁은 곳에서 방향 맞추기 어려움', '제자리에서 앞뒤로 반복하며 방향 맞추는 경로 적극 사용'),
    ('소프트웨어', '약 2 m 앞에서 다시 본 위치로 삽입', '넣는 동안 카메라로 다시 보고 위치 보정'),
    ('소프트웨어', 'EPAL 6 팔레트', 'T11 팔레트 (규격 치수 확정 후)'),
    ('하드웨어', '모터 드라이버 · 엔코더 보드 회로 초안 (5주차)', '모터 전류 실측 → 전류 제한 · 방열 확정 → PCB 제작'),
    ('하드웨어', '바퀴 마찰 · 센서 잡음은 가정값', '실측 후 시뮬레이션 값 교체'),
    ('하드웨어', '센서 위치는 시뮬레이션 값', '실물 브래킷 제작 · 장착 후 좌표 보정'),
]
def _next_table():
    rows, seen = [], {}
    for g, a, b in NEXT_ROWS:
        seen[g] = seen.get(g, 0) + 1
    done = set()
    for g, a, b in NEXT_ROWS:
        head = '' if g in done else f'<td class="grp" rowspan="{seen[g]}">{g}</td>'
        done.add(g)
        rows.append(f'<tr>{head}<td class="cur">{a}</td><td class="arrow">→</td><td class="nxt">{b}</td></tr>')
    return ''.join(rows)
add('다음 작업', '07  남은 과제와 다음 작업', 70, f"""
<h2 class="headline">다음 작업: 여러 장면 반복 검증 · 삽입 중 위치 보정 · 구동부 PCB 제작</h2>
<table class="comparison plan6 grow"><tr><th class="c1">구분</th><th class="c2">현재</th><th class="c3"></th><th class="c4">다음 단계</th></tr>{_next_table()}</table>
<div class="takeaway">다음 목표: 여러 장면에서 같은 임무 반복 확인 → 구동부 실물 제작</div>
""",
    """정리하면, 이번 주에 지게차는 SLAM으로 추정한 위치와 LiDAR 한 대로 만든 장애물 지도로 운반 임무를 끝냈고, 새로 나타난 상자도 피했습니다. 소프트웨어 쪽 다음 단계는 이것을 여러 장면과 과제의 C, D 상황에서 반복해서 확인하는 것입니다. 실측 조향각이 15도로 작아 회전 반경이 크기 때문에, 좁은 곳에서는 제자리에서 앞뒤로 여러 번 움직이며 방향을 맞추는 경로를 적극적으로 쓰도록 바꾸겠습니다. 또 바꾼 카메라로 포크를 넣는 동안 위치를 다시 보고 바로잡게 하고, 두 번째 팔레트 규격인 T11도 치수가 정해지면 같은 방식으로 확인하겠습니다. 하드웨어 쪽은 5주차에 그린 모터 드라이버와 엔코더 보드 회로를 모터 전류를 잰 뒤 전류 제한과 방열까지 확정해서 PCB로 만들겠습니다. 또 시뮬레이션에서 가정으로 둔 바퀴 마찰과 센서 잡음을 실측값으로 바꾸고, 시뮬레이션에서 정한 LiDAR와 카메라 위치대로 실물 브래킷을 만들어 달고 좌표를 보정하겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [('forklift bc4cc64', '--min-obstacle-height-m 1.15 · config/obstacle_layer_single.yaml (LiDAR 1대)'),
     ('CLAUDE.md', 'EPAL 6 과 T11 × 0.6 모두 필수'),
     ('week-05/build_deck.py', 'DRV8244 3채널 드라이버 보드 초안 · 엔코더 보드 두 가지 · "조건: 모터 전류 실측 후 확정"(전류 제한·방열)'),
     ('sim/models/dls08_measured/README.md', '실측 축간 0.66 m · 바퀴 반지름 0.125 m (이번 실행 미반영)'),
     ('docs/hardware.md', 'LiDAR·카메라 실물 장착 위치 미확정')],
    '출처: 5주차 발표 · 하드웨어 기록')

TITLE = '6주차 자율 지게차 개발'
TOTAL = 450


def build():
    assert len(slides) == 8, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-10-07. 모든 결과는 Isaac Sim 합성 장면과 CPU 합성 시험의 결과이며 실제 장비 성능이 아니다. '
              '쪽마다 위치·장애물·팔레트 정보 중 무엇이 시뮬레이터 정답이고 무엇이 센서 추정인지 표와 띠에 적었다. '
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
