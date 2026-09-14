"""Build the week 3 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.
Every figure and number comes from the repository's own measurements; the
renderer that produced each figure is named on the slide.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
BRIEF = 'https://docs.google.com/presentation/d/1BjoJLWmwd07ZJujZp4BPZrwBhx5tsnfmBpWdLMy2YrQ/edit'
M2 = 'docs/validation/2026-09-13-pocket-detector-m2.md'
E6 = 'docs/validation/2026-09-14-epal6-capture-and-evaluation.md'
EV = 'docs/validation/2026-09-14-pocket-evidence-measurements.md'
SB = 'docs/validation/2026-09-10-gazebo-sensor-baseline.md'
ADR = 'docs/decisions/0002-test-pallet-and-geometry-generality.md'
PLAN = 'docs/plans/2026-09-13-pocket-evidence-restructure.md'
MAP = 'docs/plans/2026-09-11-development-roadmap.md'
slides = []


def add(label, title, seconds, body, notes, sources, foot='측정 결과'):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def figure(src, alt, caption, *, video=False, cls='wide'):
    tag = (f'<video class="media" src="assets/{src}" autoplay loop muted playsinline '
           f'aria-label="{escape(alt, quote=True)}"></video>' if video else
           f'<img class="media" src="assets/{src}" alt="{escape(alt, quote=True)}">')
    return (f'<figure class="shot {cls}">{tag}'
            f'<figcaption class="small muted">{caption}</figcaption></figure>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '3주차\n개발 진행 보고', 20, '',
    """이번 주에는 과제의 첫 두 단계인 팔레트 포켓 인식과 로봇 기준 좌표 변환을 구현하고 평가하였다. 인식 성능과 함께, 성능을 측정하는 과정에서 확인한 센서 조건을 보고한다.""",
    [(M2, 'M2 포켓 인식 검증 기록'), (E6, 'EPAL 6 캡처와 평가')], '측정 결과 보고')

# ----------------------------------------------------------------- 2
add('개발 진행 현황', '01  개발 진행 현황', 40, f"""
{figure('16_pipeline_status.png', '다섯 단계 진행 상태: 1·2단계 완료, 4단계 다음 주, 3·5단계 차체 대기', '과제 원문의 다섯 단계 및 현재 수행 위치')}
<div class="takeaway">수행 범위: 1·2단계 구현 완료 · 3단계 이후는 차체 입고 후 착수</div>
""",
    """과제가 제시한 다섯 단계 중 1단계 팔레트 인식과 2단계 로봇 기준 좌표 변환을 구현하였다. 3단계 이후는 실제 차체의 조향 특성과 정지 거리가 필요하므로 입고 전에는 착수하지 않는다. 차체 입고 전까지 가능한 작업을 우선 수행한 것이다. 따라서 이번 보고는 인식 성능과, 인식을 측정하며 확인한 하드웨어 조건으로 구성한다.""",
    [(BRIEF, '과제 원문 7쪽의 다섯 단계'), (MAP, '개발 로드맵')], '출처: 과제 설명자료 7쪽')

# ----------------------------------------------------------------- 3
add('2D LiDAR 관측 범위', '02  2D LiDAR 관측 범위', 55, f"""
<h2 class="headline">장애물 관측용 설치 높이에서 팔레트는 관측 평면 아래</h2>
{figure('21_lidar_plane.png', '실제 설치 조건 0.50 m에서 팔레트 반사 0점, 대조 조건 0.10 m에서 53점', '동일 장면·동일 센서 위치, 설치 높이만 변경한 360° 광선 투사')}
<p class="small muted">0.10 m 는 원인 확인용 대조 조건 · 장애물·벽 관측 용도상 팔레트 전고보다 높은 설치가 전제 · SLAM 지도 작성은 미구현</p>
<div class="takeaway">역할 구분: 팔레트 관측은 2D LiDAR 로 불가 · 지도 작성·장애물 판단은 LiDAR, 팔레트·포켓은 RGB-D</div>
""",
    """인식 기능에 앞서 센서 기반을 먼저 확보하였다. Gazebo 환경에서 RGB와 깊이, 2D LiDAR 스캔을 ROS 2로 수신하여 32초 동안 161회 관측하고, 기록한 후 재생하여 동일한 값이 나오는 것까지 확인하였다. 다만 2D LiDAR로는 팔레트를 검출할 수 없다. 이 센서는 설치한 높이의 평면만 관측하는데, 팔레트 전고가 144 밀리미터이고 제작 예정인 규격은 90 밀리미터이므로 관측 평면 아래에 위치한다. 그림은 동일 장면에서 센서 높이만 변경하여 360도 광선을 투사한 결과이다. 실제 설치 조건인 0.5 미터에서는 벽과 기둥, 상자가 298점 관측되는 반면 팔레트 반사는 0점이다. 우측은 원인을 확인하기 위한 대조 조건으로, 팔레트 전고 아래인 0.1 미터에서는 53점이 관측된다. 다만 이 높이는 실제 설치 조건이 아니다. 2D LiDAR는 장애물과 벽을 관측하여 지도를 작성하는 용도이므로 팔레트 전고보다 높은 평면에 설치하는 것이 전제이며, 팔레트가 관측 평면 아래에 놓이는 것은 그 결과로 따라온다. 센서를 바꾸거나 높이를 조정하여 해결할 사항이 아니라 역할을 구분해야 할 사항이다. 2D LiDAR는 지도 작성과 장애물 판단에 사용하고, 팔레트와 포켓은 RGB-D로 인식한다. 다음 장이 해당 RGB-D 인식이다. 지도 작성과 자기 위치 추정은 바퀴 오도메트리와 실제 주행이 필요하므로 차체 입고 후 단계이다.""",
    [(SB, '센서 기준선 — 실시간 161회 / 32.0초, 기록 재생 일치'),
     (MAP, 'SLAM·위치 추정은 M4, 차체 입고 후')], 'SLAM 지도 작성 미구현')

# ----------------------------------------------------------------- 4
add('포켓 인식 처리 과정', '03  포켓 인식 처리 과정', 55, f"""
{figure('20_pipeline_stages.png', '깊이 영상, 작업 영역, 평면 후보, 기둥·빈칸 격자, 포켓 자세의 다섯 단계', '실제 촬영 장면에 검출기를 적용한 단계별 중간 결과')}
<div class="takeaway">인식 방식: 학습 모델 미사용 · 팔레트 규격과 기하만 사용, 실패 시 단계별 사유 기록</div>
""",
    """팔레트 인식은 깊이 영상에서 전면에 해당하는 수직 평면을 탐색하는 것으로 시작한다. 해당 평면을 세로 격자로 분할하면 기둥이 있는 칸과 빈 칸이 구분되며, 빈 칸이 연속된 구간이 포켓 후보가 된다. 네 번째 그림이 그 격자이며 초록이 기둥, 자홍이 빈 칸이다. 후보가 규격의 개구 폭과 중앙 지지대 폭에 부합하고 위아래 덱의 증거가 함께 확인될 때만 유효한 관측으로 판정한다. 학습 모델은 사용하지 않았다. 데이터 확보 이전에 동작해야 하며, 실패 시 어느 단계에서 어떤 이유로 실패했는지 확인할 수 있어야 하기 때문이다.""",
    [(M2, '검출기 설계와 단계 정의'), (EV, '측정 리그와 단계별 증거')], '대상 장면: 촬영 세트 s003')

# ----------------------------------------------------------------- 5
add('시험용 팔레트 선정', '04  시험용 팔레트 선정', 50, f"""
<h2 class="headline">국내 소형 표준 부재 및 적재 능력 10 kg 제약</h2>
{figure('15_pallet_choice.png', '포크를 넣은 채로 EPAL 6과 T11 곱하기 0.6을 나란히 비교', '포크 삽입 상태 · 잠정 차체 모델 (MuJoCo)')}
<div class="rule body">국내 표준 짧은 변 하한 740 mm · EPAL 6 자중 9~10 kg · 포크 길이 420 mm</div>
<div class="takeaway">선정 결과: T11 비율 유지 0.6배 축소 · 660 × 660 × 90 mm 자체 제작</div>
""",
    """개발 대상 팔레트를 먼저 선정하였다. 국내 표준 대여 품목에는 한 변이 1000 밀리미터 미만인 규격이 없으며, 시장 전체로 확대하여도 짧은 변 740 밀리미터가 하한이다. 차체 카탈로그가 제시한 포크 적재 능력은 10 킬로그램인데 유럽식 하프 팔레트는 자중이 9에서 10 킬로그램이므로 화물을 적재할 여유가 없다. 포크 길이도 420 밀리미터여서 표준 팔레트에는 절반도 진입하지 못한다. 따라서 국내 표준 T11의 비율을 유지한 채 0.6배로 축소한 660 × 660 × 90 밀리미터를 시험용으로 제작하기로 하였다. 규격을 표준 비율로 유지하였으므로 검출기는 표준 형상과 축소 형상 모두에서 동작해야 한다.""",
    [(ADR, '팔레트 규격 결정과 무게·도달률 근거')], '출처: ADR 0002')

# ----------------------------------------------------------------- 6
add('초기 파라미터의 한계', '05  초기 파라미터의 한계', 55, f"""
<h2 class="headline">형상에 종속된 고정값이 판별 증거를 함께 제거</h2>
{figure('18_floor_cut.png', '고정값 20 mm 절단선이 두 형상의 바닥판을 지우는 단면도', '팔레트 하부 단면 · 세로 실척 · 적색은 고정값 20 mm 가 제거하던 구간')}
<div class="rule body">고정값 적용 시 실물 규격 자세 125개 중 12개만 유효 · 정면 자세는 전 거리 미검출</div>
<div class="takeaway">원인: 검출 방식이 아닌 개발 초기 형상에 맞춰 고정한 상수</div>
""",
    """검출기의 상수는 개발 초기에 사용한 장면의 형상에 맞추어 고정되어 있었다. 그 상태로 실물 규격 팔레트에 적용하면 자세 125개 중 12개만 유효 관측이 나오며, 정면 자세에서는 어느 거리에서도 검출하지 못한다. 원인을 추적하였다. 검출기는 바닥 잡음을 제거하기 위해 일정 높이 이하의 점을 제외하는데, 그 높이가 20 밀리미터로 고정되어 있었다. 유럽 규격의 바닥판은 22 밀리미터, 제작 예정인 축소 T11은 15 밀리미터이므로, 잡음 제거를 위한 필터가 판별에 필요한 증거까지 제거하고 있었다. 그림의 적색 구간이 제거되던 부분이며 두 형상 모두 바닥판이 그 안에 포함된다. 동일한 형태의 고정값이 평면 두께 허용치와 최소 점 개수에도 있었다.""",
    [(EV, '바닥 절단 높이 20 mm 대 유도값, 검출 0/3 대 3/3'),
     (M2, '고정값 적용 시 자세 125개 중 12개')], '출처: 측정 기록 2026-09-14')

# ----------------------------------------------------------------- 7
add('파라미터 유도', '06  파라미터 유도', 65, f"""
<h2 class="headline">동일 주행·동일 데이터 비교: 고정 0 / 183, 유도 150 / 183</h2>
{figure('04_frozen_vs_derived.mp4', '같은 접근을 고정 파라미터와 유도 파라미터로 나란히 재생', '좌 고정 파라미터 · 우 유도 파라미터 · 하단 띠는 전 구간 검출 여부')}
<div class="rule body">축척 s = 개구 높이 ÷ 200 mm · 길이 항목 s 비례 · 점 개수 s² 비례</div>
<div class="takeaway">적용 범위: 표준 규격과 축소 T11 모두 동작 · 축소 T11 자세 60개 중 16 → 59</div>
""",
    """고정값을 제거하고 팔레트 규격에서 산출하도록 변경하였다. 개구 높이의 비를 축척으로 두고, 길이에 해당하는 값은 축척에 비례하여, 점 개수는 면적에 해당하므로 축척의 제곱에 비례하여 정한다. 바닥 절단 높이만 바닥판 두께의 3분의 1로 별도 규정하였다. 화면은 동일한 접근을 두 설정으로 실행한 것이다. 좌측은 183 프레임 전 구간에서 검출하지 못하고, 우측은 150 프레임에서 두 포켓을 검출한다. 규격을 입력으로 받으므로 표준 형상과 축소 형상에 모두 적용되며, 제작 예정인 축소 T11에서도 자세 60개 중 16개였던 검출이 59개로 증가하였다. 실물 팔레트를 실측한 후에는 그 치수를 입력으로 다시 산출한다.""",
    [(PLAN, '유도 공식과 기준점 선택, 자세 60개 중 16 → 59'),
     (EV, '측정 리그 — 촬영 세트와 비트 단위로 같은 장면')], '렌더: 측정 리그 · 시뮬레이터 아님')

# ----------------------------------------------------------------- 8
add('접근 동작 확인', '07  접근 동작 확인', 60, f"""
<h2 class="headline">팔레트 전면 2.95 m ~ 0.95 m 연속 접근</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{figure('11_gazebo_approach.mp4', '카메라 시점에서 두 포켓을 계속 검출하는 연속 접근', '카메라 시점 · Gazebo Harmonic 렌더', video=True, cls='')}
{figure('14_external_approach.mp4', '같은 접근을 3인칭에서 본 장면', '외부 시점 · 잠정 차체 모델 (MuJoCo)', video=True, cls='')}
</div>
<div class="takeaway">검출 결과: 101 자세 중 97 자세 검출 · 정답(초록)과 추정(자홍) 일치</div>
""",
    """접근 과정에서 인식이 동작하는 방식을 확인한다. 좌측이 카메라 시점, 우측이 동일한 접근을 외부에서 관측한 것이다. 팔레트에서 2.95 미터 떨어진 지점에서 시작하여 비스듬히 접근하며 정렬하고 0.95 미터까지 진입한다. 좌측 화면에서 초록이 정답, 자홍이 인식 결과이며 대부분 겹쳐 하나로 보인다. 101 자세 중 97 자세에서 두 포켓을 검출하였다. 우측의 주황색은 카메라의 상하 화각이다. 개별 장면을 이어 붙인 것이 아니라 20 밀리미터 간격으로 촬영한 연속 접근이다.""",
    [(E6, 'Gazebo 촬영 파이프라인'), (PLAN, '자세 범위와 검출 판정')], '렌더: Gazebo Harmonic · MuJoCo')

# ----------------------------------------------------------------- 9
add('평가 결과', '08  평가 결과', 60, f"""
<div class="split grow" style="grid-template-columns:1.05fr 1fr">
{figure('03_scene_variety.png', '먼 거리, 가까운 거리, 비스듬한 자세, 가림, 유사 물체, 팔레트 없음', '촬영 100장면 중 6개 조건 · Gazebo Harmonic 렌더', cls='')}
{figure('17_targets.png', '검출률 100%, 위치 오차 p95 8.17 mm, 방향 오차 p95 0.053도', '2주차 제시 목표 대비 실측', cls='')}
</div>
<div class="takeaway">검증 범위: 합성 깊이 기준 · 실센서, 축소 T11, 전 거리 구간은 미포함</div>
""",
    """실물 규격 팔레트로 장면 100개를 구성하여 촬영하고 평가하였다. 좌측은 그중 여섯 가지 조건이다. 가림 장면은 검출하지 않고 무효로 거부해야 하며, 유사 물체와 팔레트 없음 조건은 검출하지 않아야 한다. 실패한 장면 없이 100개를 모두 확보하였고 양성은 전부 검출하였다. 우측이 2주차에 제시한 목표와의 비교이다. 검출률은 목표 95퍼센트에 대해 100퍼센트, 위치 오차 p95는 목표 20밀리미터에 대해 8.17밀리미터, 방향 오차 p95는 목표 2도에 대해 0.053도로 세 항목을 모두 충족한다. 다만 목표 달성으로 기록하지 않는다. 시뮬레이터가 생성한 깊이이고 제작 예정인 축소 T11도 아니며 거리 구간도 제한되어 있다. 실센서의 깊이 오차는 2.5미터에서 50밀리미터 수준으로, 본 자료에는 포함되지 않은 오차이다.""",
    [(E6, 'dev 42/42, eval 18/18, 위치 p95 8.17 / 5.98 mm, 위양성 0'),
     (MAP, 'M2 합성 탐색 목표')], '렌더: Gazebo Harmonic')

# ----------------------------------------------------------------- 10
add('카메라 설치 높이', '09  카메라 설치 높이', 60, f"""
<h2 class="headline">설치 높이 상승 시 근거리 인식 구간 우선 상실</h2>
{figure('13_camera_mount.png', '카메라 높이 0.27, 0.50, 0.90 m에서의 화각과 가장 가까운 검출 거리', '잠정 차체 모델 (MuJoCo) · 적색 카메라, 주황 상하 화각')}
<div class="takeaway">적용 기준: 마스트 상단은 1.75 m 이내 미검출 · 저위치 설치를 기준선으로 하며 최종값은 차체 실측 후 확정</div>
""",
    """설치 후보별로 정면 거리를 100밀리미터 간격으로 주사하여 실제 검출 구간을 측정하였다. 원거리는 유사하나 근거리를 먼저 상실한다. 과제 설명자료는 카메라를 마스트 상단에 배치하는데, 그 높이에서는 1.75미터 이내를 관측하지 못하고 검출 지점 수도 절반으로 감소한다. 화면 하단의 수치가 그 결과이다. 인식이 중단되는 시점에 포크 끝에서 팔레트까지 각각 580, 780, 1280 밀리미터가 남는다. 카메라를 낮추면 근거리 한계가 1.05미터까지 감소하나 개선 폭은 0.2미터 수준이다. 마스트 상단 설치로는 접근 구간을 확보할 수 없음이 확인되었으며, 저위치 설치를 기준선으로 개발을 진행하고 있다. 최종 높이는 차체의 마스트 높이와 승강 행정을 실측한 후 확정한다.""",
    [(E6, '장착 높이별 검출 구간 측정'), (BRIEF, '과제 원문 4쪽 — 마스트 상단 카메라')],
    '기준: 카메라에서 팔레트 전면까지의 거리')

# ----------------------------------------------------------------- 11
add('삽입 구간 관측 한계', '10  삽입 구간 관측 한계', 60, f"""
<h2 class="headline">전면이 화각을 벗어나면 평면 추출 불가</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{figure('06_near_field_blind.png', '0.60 m에서 전면이 사라지고 상판만 보이는 화면', '0.60 m · 전면 소실, 상판만 관측 (측정 리그)', cls='')}
{figure('09_docking_preview.mp4', '차체 모델이 팔레트에 포크를 넣는 미리보기', '포크 삽입 구간 · 잠정 차체 모델 (MuJoCo) · 접촉·하중 미모의', video=True, cls='')}
</div>
<div class="takeaway">대응: 포크 길이 420 mm, 근거리 한계 0.8~1.3 m · 삽입 구간은 추적으로 관측 유지</div>
""",
    """팔레트가 근접하면 카메라가 전면이 아니라 상판을 위에서 관측하게 된다. 좌측은 0.6미터 지점이며 전면이 완전히 사라진 상태이다. 전면이 화각에서 벗어나면 어떤 파라미터로도 복구할 수 없다. 접근 방식에 따라 근거리 한계가 0.8미터에서 1.3미터인데 포크 길이는 420밀리미터이므로, 어떤 설치 높이를 선택하여도 삽입이 완료되는 구간은 관측되지 않는다. 우측이 해당 구간이다. 중간 거리에도 검출이 중단되는 구간이 존재한다. 두 결과 모두 같은 결론을 가리킨다. 삽입 구간에서는 매 프레임 새로 인식하는 방식이 성립하지 않으므로, 관측을 연속으로 유지하는 추적이 필요하며 이것이 다음 주 작업이다. 과제의 조건 B와 조건 D가 비스듬하고 근접한 경우이므로 이 구간과 중첩된다.""",
    [(EV, '근접 미검출은 검출기가 아니라 카메라 화각'),
     (PLAN, '접근 방식별 검출 구간')], '렌더: 측정 리그 · MuJoCo')

# ----------------------------------------------------------------- 12
add('향후 추진 계획', '11  향후 추진 계획', 40, f"""
{figure('19_roadmap.png', 'M1과 M2는 완료, M3 진행, H0부터 H2는 차체 입고 대기', '개발 로드맵 상 현재 위치')}
<div class="takeaway">유의 사항: 본 자료의 수치는 무잡음 조건 값 · 실센서 재측정 필요</div>
""",
    """다음 주에는 실물 없이 수행 가능한 포켓 추적을 진행한다. 연속 관측에서 좌우 포켓 대응을 유지하고, 가림이나 지연으로 관측이 중단되었을 때 삽입 허가를 해제하는 상태 전환을 검증한다. 카메라 설치 높이는 차체 실측으로 확정한 후 그 기준으로 장면을 재구성하여 촬영한다. 차체 입고 후에는 시험용 팔레트를 제작하고 실센서에서 동일 항목을 다시 측정한다. 지도 작성과 주행은 그 다음 단계이다. 본 자료의 수치는 모두 무잡음 조건의 값이므로 실센서에서 재확인이 필요하다.""",
    [(MAP, '로드맵 M3 이후와 H 경로')], '출처: 개발 로드맵')


TITLE = '3주차 개발 진행 보고'
TOTAL = 620


def build():
    assert len(slides) == 12, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} — 발표 원고', '',
              f'12장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-15. 모든 수치는 합성 장면 측정값이며 실물 성능이 아니다. '
              '각 화면에는 그것을 만든 렌더러(Gazebo · MuJoCo · 측정 리그)를 표기했다.', '']
    elapsed = 0
    for i, s in enumerate(slides, 1):
        source_lines = '\n'.join(f'{label}: {url}' for url, label in s['sources'])
        notes = f"권장 {s['seconds']}초\n\n{s['notes']}\n\n[Sources]\n{source_lines}\n[/Sources]"
        if i == 1:
            component = (f'<x-import component-from-global-scope="UOSSlideDS.TitleSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}" '
                         f'subtitle="임베디드구동 및 실습 · 팔레트 핸들링 경로 생성 및 제어"></x-import>')
        else:
            footer = (f'<div class="foot"><span>{escape(s["foot"])}</span>'
                      f'<span>{i:02d} / {len(slides)}</span></div>')
            component = (f'<x-import component-from-global-scope="UOSSlideDS.ContentSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}">'
                         f'<div class="slide-body">{s["body"]}{footer}</div></x-import>')
        sections.append(
            f'<section data-label="{escape(s["label"], quote=True)}" data-screen-label="{i:02d}" '
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
