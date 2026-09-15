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
WK3 = 'docs/validation/2026-09-15-week-03-deck-measurements.md'
slides = []


def add(label, title, seconds, body, notes, sources, foot='측정 결과'):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def figure(src, alt, caption, *, video=None, cls='wide'):
    # Infer the tag from the extension. Naming a clip and forgetting the flag
    # silently produced an <img> pointing at an MP4, which renders as nothing.
    if video is None:
        video = src.rsplit('.', 1)[-1].lower() in {'mp4', 'webm'}
    tag = (f'<video class="media" src="assets/{src}" autoplay loop muted playsinline '
           f'aria-label="{escape(alt, quote=True)}"></video>' if video else
           f'<img class="media" src="assets/{src}" alt="{escape(alt, quote=True)}">')
    # 빈 설명글도 줄 높이와 간격을 차지한다. 그림에 이미 적혀 있으면 아예 넣지 않는다.
    cap = f'<figcaption class="small muted">{caption}</figcaption>' if caption else ''
    return f'<figure class="shot {cls}">{tag}{cap}</figure>'


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '3주차\n개발 진행 보고', 20, '',
    """본 보고에서는 팔레트 포켓의 인식 기능과 포켓 위치의 좌표 산출 기능에 대한 구현 및 평가 결과를 보고한다. 포켓은 포크가 삽입되는 팔레트의 구멍을 말한다. 측정은 모두 시뮬레이션 환경에서 수행하였으며, 인식 성능과 함께 측정 과정에서 확인한 센서 설치 조건을 정리한다.""",
    [(M2, '포켓 인식 검증 기록'), (E6, 'EPAL 6 캡처와 평가')], '측정 결과 보고')

# ----------------------------------------------------------------- 2
add('개발 진행 현황', '01  개발 진행 현황', 47, """
<h2 class="headline">개발 단계별 진행 현황</h2>
<div class="pipeline grow"><article class="pipeline-step done"><h3>① 팔레트 인식</h3><p>깊이 영상에서<br>팔레트·포켓 검출</p><p class="state">구현·평가 완료</p></article><article class="pipeline-step done"><h3>② 좌표 변환</h3><p>포켓 위치·방향의<br>로봇 기준 좌표 산출</p><p class="state">구현 완료</p></article><article class="pipeline-step wait"><h3>③ 경로 생성</h3><p>장애물 회피<br>접근 경로 생성</p><p class="state">차체 입고 후</p></article><article class="pipeline-step now"><h3>④ 삽입·적재</h3><p>포켓 추적 및<br>포크 삽입</p><p class="state">다음 주 착수</p></article><article class="pipeline-step wait"><h3>⑤ 이송·하역</h3><p>목적지 주행 후<br>하역</p><p class="state">이후</p></article></div>
<div class="takeaway">구현 범위: 팔레트 인식 및 좌표 산출 완료, 3단계 이후는 차체 입고 후 착수</div>
""",
    """과제에서 제시한 작업 절차는 팔레트 인식부터 하역까지 다섯 단계이다. 이번 주까지 1단계 팔레트 인식과 2단계 좌표 산출을 구현하였다. 2단계는 검출한 포켓의 위치와 방향을 로봇 기준 좌표로 변환하는 단계이다. 3단계 이후는 차체의 최소 회전반경과 제동 특성이 필요하므로 차체 입고 이후에 착수한다. 센서 부분은 시뮬레이션 환경에서 컬러 영상과 깊이 영상, 2D LiDAR 측정값을 32초 동안 161회 기록하고, 기록을 재생하여 동일한 값이 재현되는 것까지 확인하였다. 따라서 이번 보고는 인식 성능과 센서 설치 조건을 중심으로 구성한다.""",
    [(BRIEF, '과제 원문 7쪽의 다섯 단계'), (MAP, '개발 로드맵')], '출처: 과제 설명자료 7쪽')

# ----------------------------------------------------------------- 3
add('2D LiDAR 관측 범위', '02  2D LiDAR 관측 범위', 66, f"""
<h2 class="headline">2D LiDAR 관측 평면과 팔레트 높이</h2>
{figure('21_lidar_plane.png', '옆에서 본 관측 평면과 그 높이에서 360도 방향의 반사 지점. 팔레트 반사는 0개', '')}
<div class="takeaway">역할 구분: 2D LiDAR는 지도 작성·장애물 인식, RGB-D는 팔레트·포켓 인식</div>
""",
    """2D LiDAR로는 팔레트를 검출할 수 없다. 이 센서의 측정 범위는 설치 높이의 수평 평면 하나로 제한된다. 좌측 그림의 하늘색 면이 설치 높이 0.5미터에서의 관측 평면이다. 팔레트의 전체 높이는 유럽 표준 EPAL 6이 144밀리미터, 제작 예정인 시험용 팔레트가 90밀리미터로 관측 평면보다 낮다. 우측은 같은 조건에서 360도로 측정한 반사점을 위에서 본 것이다. 벽과 기둥, 상자에서는 반사점 298개가 측정되었으나 팔레트에서는 한 점도 측정되지 않았다. 센서를 팔레트보다 낮게 설치하는 방안은 검토하지 않는다. 2D LiDAR는 지도 작성과 장애물 인식을 위한 센서이므로 팔레트보다 높은 위치에 설치하는 것이 전제 조건이며, 팔레트가 관측 평면 아래에 놓이는 것은 그 결과이다. 따라서 역할을 구분하여 지도 작성과 장애물 인식은 2D LiDAR가, 팔레트와 포켓 인식은 RGB-D 카메라가 담당한다. 지도 작성과 위치 추정은 주행 오도메트리와 실제 주행이 필요하므로 차체 입고 이후의 단계이다.""",
    [(SB, '센서 기준선 — 실시간 161회 / 32.0초, 기록 재생 일치'),
     (MAP, '지도 작성·위치 추정은 차체 입고 후 단계')], '지도 작성·로봇 위치 추정(SLAM) 미구현')

# ----------------------------------------------------------------- 4
add('포켓 인식 처리 과정', '03  포켓 인식 처리 과정', 49, f"""
<h2 class="headline">깊이 영상 기반 포켓 인식 절차</h2>
{figure('20_pipeline_stages.png', '깊이 영상, 팔레트 전면, 받침목과 빈 칸, 판정된 포켓의 네 단계', '')}
<div class="takeaway">판정 조건: 받침목과 빈 칸, 상하 판이 모두 관측될 것</div>
""",
    """깊이 영상은 화면의 각 지점에 카메라에서 물체까지의 거리를 기록한 영상이다. 이 영상을 입력으로 네 단계를 거쳐 포켓을 검출한다. 먼저 팔레트가 존재할 수 있는 범위의 점만 남기고, 그중에서 바닥에 수직인 평면을 이루는 점을 추출한다. 두 번째 그림의 초록이 남긴 점이고 주황이 팔레트 전면으로 추출한 점이다. 다음으로 추출한 평면을 세로 방향의 칸으로 나누어, 팔레트를 받치는 받침목이 있는 칸과 빈 칸을 구분한다. 세 번째 그림의 초록 막대가 받침목, 자홍이 빈 칸이며, 빈 칸이 연속된 구간을 포켓 후보로 정한다. 마지막으로 포켓 후보의 폭과 받침목의 폭이 규격 범위에 들고 상하 판이 함께 관측되면 포켓으로 판정하고, 네 번째 그림과 같이 좌우 포켓의 중심과 삽입 방향을 산출한다. 학습 모델은 적용하지 않았다. 학습 자료를 확보하기 전에도 동작하고 실패 단계와 원인을 확인할 수 있도록 팔레트의 치수와 형상만을 이용하였다.""",
    [(M2, '검출기 설계와 단계 정의'), (EV, '측정 리그와 단계별 증거')], '대상 장면: 촬영 세트 s003')

# ----------------------------------------------------------------- 5
add('시험용 팔레트 선정', '04  시험용 팔레트 선정', 47, f"""
<h2 class="headline">시험용 팔레트 규격 선정</h2>
{figure('15_pallet_choice.png', '후보 팔레트 다섯 개를 같은 축척으로 놓고 포크 길이에서 가로선을 그은 비교', '동일 축척 · 갈색이 포크 도달 구간')}
<div class="takeaway">제작 사양: 국내 표준 T11의 0.6배 축소, 660 × 660 × 90 mm</div>
""",
    """시험에 사용할 팔레트 규격을 선정하였다. 조사한 국내 표준 대여 품목에는 한 변이 1000밀리미터 미만인 규격이 없었고, 시장 전체에서도 짧은 변의 최소 길이는 740밀리미터였다. 차체 카탈로그의 포크 적재 한도는 10킬로그램이다. 유럽식 하프 팔레트인 EPAL 6은 자체 무게가 9에서 10킬로그램이므로 화물을 추가로 적재할 여유가 없으며, 포크 길이도 420밀리미터로 표준 팔레트 깊이의 절반에 미치지 못한다. 따라서 국내 표준 T11의 각 치수를 0.6배로 축소한 660 × 660 × 90밀리미터 규격으로 시험용 팔레트를 제작하기로 하였다. 형상의 비율은 유지하고 크기만 축소하므로, 인식 프로그램은 표준 규격과 축소 규격에서 모두 동작해야 한다.""",
    [(ADR, '팔레트 규격 결정과 무게·도달률 근거')], '출처: ADR 0002')

# ----------------------------------------------------------------- 6
add('초기 설정의 한계', '05  초기 설정의 한계', 52, f"""
<h2 class="headline">고정 기준값 적용 시의 인식 실패 원인</h2>
<p class="small muted">바닥에서 측정된 점이 팔레트의 점과 섞이므로, 바닥에서 일정 높이까지는 제외한다</p>
{figure('22_floor_cut.png', '촬영 화면에 제외 구간을 표시한 비교. 좌측은 바닥판이 제외 구간에 포함된다', '')}
<div class="takeaway">초기 결과: 시험 자세 125개 중 12개에서만 포켓 검출</div>
""",
    """인식 프로그램은 바닥 부근에서 측정된 점을 불필요한 정보로 보고 제외하였다. 제거 범위는 바닥에서 20밀리미터로 고정되어 있었다. 초기 검증에 사용한 팔레트의 바닥판은 두께가 50밀리미터여서 문제가 없었으나, EPAL 6의 바닥판은 22밀리미터이고 제작 예정인 축소 T11은 15밀리미터이다. 그림의 적색 구간과 같이 바닥판의 전부 또는 일부가 함께 제거되면서 판별에 필요한 정보가 사라졌다. 그 결과 EPAL 6 모델의 위치와 방향을 변경한 시험 자세 125개 중 12개에서만 포켓을 검출하였으며, 정면 자세에서는 시험한 모든 거리에서 검출하지 못하였다. 동일한 평면으로 인정할 두께 범위와 구조물 판별에 필요한 최소 측정점 수에도 고정된 기준값을 사용하고 있었다. 그림의 초록색 기준은 팔레트 치수에서 산출한 기준값이며 다음 장에서 설명한다.""",
    [(EV, '바닥 절단 높이 20 mm 대 유도값, 검출 0/3 대 3/3'),
     (M2, '고정값 적용 시 자세 125개 중 12개')], '출처: 측정 기록 2026-09-14')

# ----------------------------------------------------------------- 7
add('기준값 산출 방식', '06  기준값 산출 방식', 57, f"""
<h2 class="headline">팔레트 치수 기반 기준값 산출</h2>
{figure('04_frozen_vs_derived.mp4', '촬영한 같은 주행을 두 설정으로 나란히 재생. 왼쪽은 버리는 띠가 두꺼워 끝까지 못 찾는다', '동일 주행 101장 · 좌측 0장, 우측 97장 검출')}
<div class="swap"><div><b>바닥에서 제외하는 높이</b><span>20 mm <i>→</i> 7.3 mm</span></div><div><b>같은 면으로 볼 두께</b><span>20 mm <i>→</i> 7.8 mm</span></div><div><b>팔레트로 인정할 점 개수</b><span>100개 <i>→</i> 15개</span></div></div>
<div class="takeaway">적용 결과: 축소 T11 시험 자세 60개 중 0개에서 58개로 증가</div>
""",
    """고정된 기준값을 팔레트 치수에서 산출하도록 변경하였다. 길이에 해당하는 기준값은 팔레트의 축소 비율에 비례하여 축소하고, 측정점 수에 해당하는 기준값은 관측 면적에 비례하므로 축소 비율의 제곱을 적용한다. 바닥 부근의 측정점을 제거하는 높이는 바닥판 두께의 3분의 1로 정하였다. 화면은 촬영한 접근 주행 101장에 두 설정을 각각 적용한 결과이다. 앞 장에서 설명한 제거 구간을 색으로 표시하였다. 좌측은 제거 구간이 두꺼워 바닥판을 포함하며 101장 전부에서 포켓을 검출하지 못하였고, 우측은 제거 구간이 얇아 바닥판이 남아 97장에서 좌우 포켓을 검출하였다. 하단의 띠는 장면별 검출 여부이다. 이 방식에서는 팔레트 규격이 변경되어도 코드를 수정하지 않고 치수만 입력하면 된다. 제작 예정인 축소 T11에서도 시험 자세 60개 중 검출 자세가 0개에서 58개로 증가하였다. 다만 검출한 자세 중 위치 오차가 500밀리미터를 초과한 사례가 한 건 있어 오검출 판별 조건은 추가 보완이 필요하다. 제작 이후에는 실측 치수를 입력하여 기준값을 다시 산출한다.""",
    [(WK3, '재측정: 축소 T11 자세 60개 중 0 → 58, 최악 오위치 509 mm'),
     (PLAN, '유도 공식과 기준점 선택'),
     (E6, '촬영 세트 101자세')], '화면 생성: Gazebo 촬영 장면')

# ----------------------------------------------------------------- 8
add('접근 동작 확인', '07  접근 동작 확인', 50, f"""
<h2 class="headline">연속 접근 구간의 포켓 검출 확인</h2>
<div class="split grow" style="grid-template-columns:1.4fr 1fr">
{figure('11_gazebo_approach.mp4', '카메라 시점에서 두 포켓을 계속 검출하는 연속 접근', '카메라 시점 · Gazebo Harmonic', video=True, cls='')}
{figure('14_external_approach.mp4', '같은 접근을 3인칭에서 본 장면', '외부 시점 · MuJoCo', video=True, cls='')}
</div>
<div class="takeaway">검출 구간: 2.95 m부터 0.95 m까지 포켓 검출 유지</div>
""",
    """팔레트에 접근하는 동안 포켓 검출이 유지되는지 확인하였다. 좌측은 Gazebo Harmonic으로 구성한 카메라 시점이고, 우측은 MuJoCo의 잠정 차체 모델로 동일한 접근을 나타낸 화면이다. 카메라에서 팔레트 전면까지의 거리 2.95미터에서 시작하여 측면에서 방향을 정렬하며 0.95미터까지 접근하였다. 초록은 장면에 설정한 포켓 위치이고 자홍은 인식 프로그램이 산출한 위치이며, 화면에서 대부분 일치한다. 주황은 카메라의 수직 관측 범위이다. 접근 경로를 20밀리미터 간격으로 촬영하여 연속 영상으로 구성하였다.""",
    [(E6, 'Gazebo 촬영 파이프라인'), (PLAN, '자세 범위와 검출 판정')], '화면 생성: Gazebo Harmonic · MuJoCo')

# ----------------------------------------------------------------- 9
add('평가 결과', '08  평가 결과', 70, f"""
<h2 class="headline">촬영 장면 100개의 인식 성능 평가</h2>
{figure('03_scene_variety.png', '먼 거리, 가까운 거리, 비스듬한 자세, 가림, 유사 물체, 팔레트 없음', '')}
<div class="scores">
  <div><b>양성 검출률</b><span class="hit">100 %</span><i>목표 95 % 이상</i></div>
  <div><b>위치 오차 p95</b><span class="hit">8.17 mm</span><i>목표 20 mm 이하</i></div>
  <div><b>방향 오차 p95</b><span class="hit">0.053°</span><i>목표 2° 이하</i></div>
</div>
<div class="takeaway">평가 범위: 시뮬레이션 기준 측정값이며 실제 센서로 재측정 필요</div>
""",
    """현재 확보한 EPAL 6의 치수로 장면 100개를 구성하여 촬영하고 평가하였다. 좌측은 여섯 가지 조건의 예이다. 포켓이 가려져 판별할 수 없는 장면은 인식 결과에서 제외해야 하며, 유사 물체나 팔레트가 없는 장면을 포켓으로 판정해서도 안 된다. 촬영 장면 100개 중 검출 대상이 60개, 비검출 대상이 40개이며 검출 대상 60개는 전부 검출하였다. 우측은 개발 로드맵에 제시한 초기 목표와 이번 측정값이다. 이 목표는 개발 착수 시점에 제안한 값이며 실물 장비의 합격 기준은 아니다. 검출률은 기준 95퍼센트에 대하여 100퍼센트였다. p95는 측정 오차를 오름차순으로 정렬하였을 때 95퍼센트가 그 값 이하인 경계값을 말한다. 위치 오차 p95는 기준 20밀리미터에 대하여 8.17밀리미터, 방향 오차 p95는 기준 2도에 대하여 0.053도였다. 세 기준을 모두 충족하였으나 실물 장비의 목표 달성으로 판단할 수는 없다. 시뮬레이션으로 생성한 깊이 영상이며, 축소 T11과 전체 거리 구간은 평가하지 않았다. 실제 센서는 거리 2.5미터에서 약 50밀리미터의 측정 오차가 있으나 이번 평가에는 반영하지 않았다.""",
    [(E6, '개발용 42/42, 평가용 18/18, 위치 p95 8.17 / 5.98 mm, 위양성 0'),
     (MAP, '개발 로드맵의 초기 목표')], '화면 생성: Gazebo Harmonic')

# ----------------------------------------------------------------- 10
add('카메라 설치 높이', '09  카메라 설치 높이', 59, f"""
<h2 class="headline">카메라 설치 높이별 근거리 인식 한계</h2>
{figure('13_camera_mount.png', '카메라 높이 0.27, 0.50, 0.90 m에서의 화각과 가장 가까운 검출 거리', '적색 점이 카메라 위치')}
<div class="takeaway">설치 방침: 마스트 상단은 1.75 m 이내 미검출, 낮은 위치 기준으로 개발</div>
""",
    """카메라 설치 높이별로 팔레트까지의 정면 거리를 100밀리미터 간격으로 변경하며 포켓 검출 여부를 측정하였다. 원거리 검출 범위는 설치 높이와 무관하게 유사하였으나, 높게 설치할수록 근거리에서 먼저 검출하지 못하였다. 마스트는 포크를 승강시키는 수직 구조물이다. 과제 설명자료와 같이 마스트 상단에 설치하는 경우 팔레트까지 1.75미터 이내에서 포켓을 검출하지 못하였고, 검출한 시험 지점 수도 절반으로 감소하였다. 설치 조건별로 검출이 중단되는 시점에 포크 끝에서 팔레트까지 남는 거리는 각각 850, 1050, 1550밀리미터이다. 카메라를 낮게 설치하면 검출 가능한 최근접 거리가 1.05미터로 줄었으나 개선 폭은 0.2미터 수준이었다. 시험한 상단 설치 조건에서는 근접 구간의 인식이 어려우므로 낮은 설치 위치를 기준으로 개발하고 있다. 최종 설치 높이는 실제 마스트 높이와 포크 승강 범위를 실측한 후 확정한다.""",
    [(E6, '장착 높이별 검출 구간 측정'),
     (WK3, '포크 끝 잔여 거리 850 / 1050 / 1550 mm'),
     (BRIEF, '과제 원문 4쪽 — 마스트 상단 카메라')],
    '기준: 카메라에서 팔레트 전면까지의 거리')

# ----------------------------------------------------------------- 11
add('삽입 구간 관측 한계', '10  삽입 구간 관측 한계', 66, f"""
<h2 class="headline">삽입 구간의 팔레트 전면 관측 한계</h2>
{figure('06_near_field_blind.png', '1.20 m 에서는 전면과 포켓이 관측되고 0.60 m 에서는 상판만 관측된다', '')}
<div class="takeaway">필요 기능: 미관측 구간을 보완하는 포켓 위치 추적</div>
""",
    """팔레트에 근접하면 카메라 영상에서 전면이 사라지고 상판만 관측된다. 카메라를 바닥에서 0.5미터 높이에 설치하면 0.97미터보다 가까운 바닥은 화면에 들어오지 않으며, 팔레트 전면은 그 바닥에 접해 있다. 좌측 그림이 1.2미터와 0.6미터에서의 비교이다. 전면이 관측 범위를 벗어나면 인식 기준값을 조정하여도 검출할 수 없다. 앞 장의 1.75미터는 마스트 상단 설치 조건이며, 낮은 설치 위치에서도 접근 방식에 따라 0.8미터에서 1.3미터 사이에서 검출이 중단되었다. 포크 길이가 420밀리미터이므로 이 구간은 삽입이 완료될 때까지 이어진다. 중간 거리에서도 검출이 중단되는 구간이 확인되었다. 따라서 매 영상마다 포켓을 새로 검출하는 기능에 더하여, 이전 검출 결과를 이용해 위치를 추정하는 추적 기능이 필요하다. 해당 기능은 다음 주 작업이다. 과제에서 제시한 네 가지 접근 상황 중 측면 접근과 근접 상황이 모두 이 구간에 해당한다.""",
    [(WK3, '카메라 0.50 m 에서 최근접 바닥 0.97 m, 그 앞뒤 판정'),
     (EV, '근접 미검출은 검출기가 아니라 카메라 화각'),
     (PLAN, '접근 방식별 검출 구간')], '화면 생성: 측정 리그 · MuJoCo')

# ----------------------------------------------------------------- 12
add('향후 추진 계획', '11  향후 추진 계획', 37, f"""
<h2 class="headline">향후 개발 계획 및 확인 항목</h2>
<div class="split grow" style="grid-template-columns:1.15fr 1fr">
{figure('09_docking_preview.mp4', '차체 모델이 팔레트에 포크를 넣는 미리보기', '다음 주 구현 대상 · 접촉과 하중 미반영', video=True, cls='')}
<div class="roadmap"><article class="done"><h3>지금까지</h3><p>포켓 인식 구현 및 평가</p><p class="state">완료</p></article><article class="now"><h3>다음 주</h3><p>포켓 위치 추적 구현</p><p class="state">착수</p></article><article class="wait"><h3>차체 입고 후</h3><p>차체 실측 · 시험용 팔레트 제작<br>실제 센서 재측정</p><p class="state">대기</p></article><article class="wait"><h3>그 이후</h3><p>지도 작성 · 주행 제어<br>삽입 · 이송</p><p class="state">예정</p></article></div>
</div>
<div class="takeaway">다음 단계: 포켓 위치 추적 구현, 차체 입고 후 실제 센서로 재측정</div>
""",
    """다음 주에는 차체 없이 수행할 수 있는 포켓 위치 추적을 진행한다. 좌측은 추적 기능이 적용될 삽입 구간의 동작이며, 접촉과 화물 하중은 반영하지 않았다. 매 영상마다 새로 검출하는 대신 이전 검출 결과를 이용하여 위치를 유지하는 기능이며, 가림이나 지연으로 관측이 중단되었을 때 삽입을 중지하는 동작까지 확인한다. 카메라 설치 높이는 차체를 실측한 후 확정하고, 확정한 높이에 맞추어 장면을 다시 구성하여 촬영한다. 차체 입고 후에는 시험용 팔레트를 제작하고 실제 센서로 동일 항목을 재측정한다. 지도 작성과 주행은 그 이후 단계이다. 이번 자료의 수치는 센서 잡음을 반영하지 않은 조건의 값이므로 실제 센서로 재확인이 필요하다.""",
    [(MAP, '개발 로드맵의 다음 단계와 실물 조사 경로')], '출처: 개발 로드맵')


TITLE = '3주차 개발 진행 보고'
TOTAL = 620


def build():
    assert len(slides) == 12, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'12장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-15. 인식 결과는 컴퓨터로 만든 장면에서 측정한 값이다. 실제 장비의 성능은 별도 시험이 필요하다. '
              '그림과 영상에는 화면 생성에 사용한 도구(Gazebo · MuJoCo · 측정 리그)를 표기하였다.', '']
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
