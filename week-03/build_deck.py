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
    return (f'<figure class="shot {cls}">{tag}'
            f'<figcaption class="small muted">{caption}</figcaption></figure>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '3주차\n개발 진행 보고', 20, '',
    """이번 주에는 화물을 받치는 팔레트에서 포크를 넣는 구멍인 포켓을 찾고, 그 위치를 로봇 기준으로 계산하는 기능을 구현하였다. 컴퓨터로 만든 장면에서 측정한 인식 결과와 센서 설치 조건을 보고한다.""",
    [(M2, '포켓 인식 검증 기록'), (E6, 'EPAL 6 캡처와 평가')], '측정 결과 보고')

# ----------------------------------------------------------------- 2
add('개발 진행 현황', '01  개발 진행 현황', 47, """
<h2 class="headline">다섯 단계 중 두 단계 완료</h2>
<div class="pipeline grow"><article class="pipeline-step done"><h3>① 팔레트 인식</h3><p>포크 넣을 구멍(포켓) 찾기</p><p class="state">구현·평가 완료</p></article><article class="pipeline-step done"><h3>② 로봇 기준 좌표</h3><p>포켓의 방향·거리 계산</p><p class="state">구현 완료</p></article><article class="pipeline-step wait"><h3>③ 접근 경로</h3><p>장애물 피해 접근</p><p class="state">차체 입고 후</p></article><article class="pipeline-step now"><h3>④ 추적·삽입</h3><p>보면서 포크 넣기</p><p class="state">다음 주 착수</p></article><article class="pipeline-step wait"><h3>⑤ 이송·하역</h3><p>옮기고 내려놓기</p><p class="state">이후</p></article></div>
<div class="takeaway">이번 주 범위: 팔레트 인식과 좌표 계산, 3단계부터는 차체 입고 후</div>
""",
    """과제는 팔레트를 찾는 일부터 목적지에 내려놓는 일까지를 다섯 단계로 제시한다. 이번 주까지 1단계 팔레트 인식과 2단계 좌표 계산을 구현하였다. 2단계는 카메라가 찾은 구멍이 로봇 기준으로 어느 방향에 얼마나 떨어져 있는지 계산하는 일이다. 3단계부터는 실제 차체가 얼마나 돌 수 있고 얼마 만에 서는지를 알아야 하므로 차체를 받기 전에는 착수하지 않는다. 차체를 기다리는 동안 먼저 할 수 있는 일을 한 것이다. 센서 쪽은 가상 실험 환경에서 컬러 영상과 거리 영상, 2D LiDAR 측정값을 32초 동안 161회 받아 기록하고 다시 재생해 같은 값이 나오는 것까지 확인해 두었다. 따라서 이번 보고는 인식 성능과, 인식을 측정하면서 확인한 장비 조건으로 구성한다.""",
    [(BRIEF, '과제 원문 7쪽의 다섯 단계'), (MAP, '개발 로드맵')], '출처: 과제 설명자료 7쪽')

# ----------------------------------------------------------------- 3
add('2D LiDAR 관측 범위', '02  2D LiDAR 관측 범위', 66, f"""
<h2 class="headline">팔레트는 LiDAR 평면 아래에 있다</h2>
{figure('21_lidar_plane.png', '옆에서 본 관측 평면과 그 높이에서 360도 방향의 반사 지점. 팔레트 반사는 0개', '')}
<div class="takeaway">역할 구분: 2D LiDAR는 벽과 장애물, RGB-D 카메라는 팔레트</div>
""",
    """2D LiDAR로는 팔레트를 찾을 수 없다. 이 센서는 설치한 높이에서 수평으로 한 겹만 훑는다. 왼쪽 그림의 하늘색 면이 그 관측 평면이며, 높이 0.5미터에 설치한 경우이다. 팔레트는 전체 높이가 144밀리미터, 제작 예정인 것은 90밀리미터여서 그 면보다 훨씬 낮게 놓인다. 오른쪽은 같은 조건에서 사방으로 빛을 쏘아 되돌아온 지점을 위에서 본 것이다. 벽과 기둥, 상자에서는 298개가 되돌아오는데 팔레트에서는 한 개도 되돌아오지 않는다. 센서를 팔레트보다 낮게 다는 방법은 고려하지 않는다. 2D LiDAR는 벽과 장애물을 보고 지도를 만들기 위한 센서여서 팔레트보다 높게 설치하는 것이 당연한 조건이고, 팔레트가 관측 평면 아래 놓이는 것은 그 결과이다. 따라서 역할을 나눈다. 2D LiDAR는 지도 작성과 장애물 판단에, 팔레트와 포켓은 RGB-D 카메라에 맡긴다. 다음 장이 그 카메라 인식이다. 지도 작성과 로봇 위치 추정은 바퀴 회전으로 이동 거리를 재는 기능과 실제 주행이 있어야 하므로 차체를 받은 뒤의 단계이다.""",
    [(SB, '센서 기준선 — 실시간 161회 / 32.0초, 기록 재생 일치'),
     (MAP, '지도 작성·위치 추정은 차체 입고 후 단계')], '지도 작성·로봇 위치 추정(SLAM) 미구현')

# ----------------------------------------------------------------- 4
add('포켓 인식 처리 과정', '03  포켓 인식 처리 과정', 49, f"""
<h2 class="headline">거리 영상에서 포켓까지, 네 단계</h2>
{figure('20_pipeline_stages.png', '거리 영상, 팔레트 앞면, 받침목과 빈 칸, 확정된 포켓의 네 단계', '')}
<div class="takeaway">판정 조건: 받침목·빈 칸·위아래 판이 함께 보일 것</div>
""",
    """거리 영상은 화면의 각 지점에 카메라에서 물체까지의 거리를 기록한 영상이다. 첫 단계가 그 영상이고, 여기서 팔레트 앞면처럼 바닥에 수직으로 서 있는 평평한 면을 찾는 것이 두 번째 단계이다. 두 번째 그림의 초록은 팔레트가 있을 만한 범위로 남긴 점이고, 주황은 그중에서 실제로 한 장의 수직면을 이루는 점이다. 세 번째 단계에서는 그 면을 세로로 긴 칸으로 잘라 팔레트를 받치는 나무 토막인 받침목이 있는 칸과 빈 칸을 구분한다. 세 번째 그림의 초록 막대가 받침목, 자홍이 빈 칸이다. 빈 칸이 이어진 구간이 포크가 들어갈 구멍의 후보가 된다. 마지막으로 구멍의 폭과 받침목의 폭이 규격에 맞고 위아래 판까지 함께 보이면 포켓으로 확정하고, 네 번째 그림처럼 좌우 구멍의 위치와 포크를 넣을 방향을 표시한다. 많은 예시를 학습시켜 판단하는 모델은 쓰지 않았다. 학습용 자료를 모으기 전에도 동작하고, 실패했을 때 어느 단계에서 왜 틀렸는지 확인할 수 있도록 치수와 모양만 이용하였다.""",
    [(M2, '검출기 설계와 단계 정의'), (EV, '측정 리그와 단계별 증거')], '대상 장면: 촬영 세트 s003')

# ----------------------------------------------------------------- 5
add('시험용 팔레트 선정', '04  시험용 팔레트 선정', 47, f"""
<h2 class="headline">표준 팔레트는 무겁고 크다</h2>
{figure('15_pallet_choice.png', '후보 팔레트 다섯 개를 같은 축척으로 놓고 포크 길이에서 가로선을 그은 비교', '같은 축척 · 갈색이 포크가 닿는 부분')}
<div class="takeaway">제작 사양: 국내 표준 T11의 0.6배, 660 × 660 × 90 mm</div>
""",
    """시험에 사용할 팔레트 규격을 선정하였다. 조사한 국내 표준 대여 품목에는 한 변이 1000 밀리미터 미만인 규격이 없었고, 시장 전체에서도 짧은 변의 최소 길이는 740 밀리미터였다. 차체 카탈로그의 포크 적재 한도는 10 킬로그램이다. 유럽식 하프 팔레트인 EPAL 6은 자체 무게가 9에서 10 킬로그램이어서 화물을 더 실을 여유가 없다. 포크 길이도 420 밀리미터로 표준 팔레트의 절반까지 들어가지 못한다. 따라서 국내 표준 T11의 각 치수를 0.6배로 줄여, 가로·세로·높이가 660 × 660 × 90 밀리미터인 시험용 팔레트를 제작하기로 하였다. 크기만 줄이고 모양의 비율은 유지하므로, 인식 프로그램은 표준 크기와 축소 크기에서 모두 동작해야 한다.""",
    [(ADR, '팔레트 규격 결정과 무게·도달률 근거')], '출처: ADR 0002')

# ----------------------------------------------------------------- 6
add('초기 설정의 한계', '05  초기 설정의 한계', 52, f"""
<h2 class="headline">버린 측정점 안에 판별 근거가 있었다</h2>
<p class="small muted">바닥에서 반사된 점이 팔레트 점과 섞이므로, 바닥에서 일정 높이 아래는 버린다</p>
{figure('22_floor_cut.png', '촬영한 팔레트 화면에 버리는 구간을 색으로 칠한 비교. 왼쪽은 바닥판이 그 안에 들어간다', '')}
<div class="takeaway">초기 결과: 시험 자세 125개 중 12개에서만 포켓 검출</div>
""",
    """인식 프로그램은 바닥 가까이에서 얻은 측정점을 불필요한 정보로 보고 제외하였다. 제거 범위는 바닥에서 20 밀리미터까지로 고정되어 있었다. 초기 장면의 팔레트 바닥판은 두께가 50 밀리미터여서 문제가 없었으나, 유럽 규격의 바닥판은 22 밀리미터이고 제작 예정인 축소 T11은 15 밀리미터이다. 그림의 적색 구간처럼 바닥판의 전부 또는 일부를 함께 제거하면서 인식에 필요한 정보가 사라졌다. 그 결과 유럽 표준 팔레트 모델의 위치와 방향을 바꾼 시험 자세 125개 중 12개에서만 포켓을 찾았다. 정면에서는 시험한 모든 거리에서 찾지 못하였다. 점들을 같은 면으로 인정할 두께 범위와 구조물을 판별할 최소 측정점 개수에도 고정된 기준을 사용하고 있었다. 그림의 초록색 기준은 팔레트 치수에서 계산한 새 기준이며, 다음 장에서 설명한다.""",
    [(EV, '바닥 절단 높이 20 mm 대 유도값, 검출 0/3 대 3/3'),
     (M2, '고정값 적용 시 자세 125개 중 12개')], '출처: 측정 기록 2026-09-14')

# ----------------------------------------------------------------- 7
add('기준값 산출 방식', '06  기준값 산출 방식', 57, f"""
<h2 class="headline">기준값을 치수에서 계산한다</h2>
{figure('04_frozen_vs_derived.mp4', '촬영한 같은 주행을 두 설정으로 나란히 재생. 왼쪽은 버리는 띠가 두꺼워 끝까지 못 찾는다', '같은 주행 101장 · 왼쪽 0장, 오른쪽 97장 검출')}
<div class="swap"><div><b>바닥에서 버리는 높이</b><span>20 mm <i>→</i> 7.3 mm</span></div><div><b>같은 면으로 볼 두께</b><span>20 mm <i>→</i> 7.8 mm</span></div><div><b>팔레트로 인정할 점 개수</b><span>100개 <i>→</i> 15개</span></div></div>
<div class="takeaway">적용 결과: 축소 T11도 시험 자세 60개 중 0개 → 58개</div>
""",
    """앞 장의 고정된 기준값을 팔레트 치수에서 계산하도록 변경하였다. 길이 기준은 팔레트를 줄인 비율만큼 줄인다. 측정점 개수 기준은 보이는 면적에 맞추므로, 길이를 줄인 비율을 두 번 곱하여 적용한다. 바닥 부근의 측정점을 제거하는 높이는 바닥판 두께의 3분의 1로 정하였다. 화면은 촬영한 접근 주행 101장에 두 설정을 각각 적용한 것이다. 앞 장에서 본 버리는 구간을 색으로 칠해 두었다. 왼쪽은 그 띠가 두꺼워 바닥판을 덮고, 101장 모두에서 포켓을 찾지 못한다. 오른쪽은 띠가 얇아 바닥판이 남고, 97장에서 두 포켓을 찾는다. 아래 띠는 장면마다의 성공 여부이다. 팔레트 규격이 바뀌면 코드를 고치는 대신 새 치수를 입력할 수 있다. 제작 예정인 축소 T11 모델도 시험 자세 60개 중 한 개도 찾지 못하던 것이 58개로 늘었다. 다만 받아들인 자세 가운데 위치를 500밀리미터 넘게 잘못 잡은 것이 하나 있어, 잘못 찾은 경우를 걸러내는 조건은 더 손봐야 한다. 제작 후에는 실제로 잰 치수를 입력하여 기준값을 다시 계산한다.""",
    [(WK3, '재측정: 축소 T11 자세 60개 중 0 → 58, 최악 오위치 509 mm'),
     (PLAN, '유도 공식과 기준점 선택'),
     (E6, '촬영 세트 101자세')], '화면 생성: Gazebo 촬영 장면')

# ----------------------------------------------------------------- 8
add('접근 동작 확인', '07  접근 동작 확인', 50, f"""
<h2 class="headline">2.95 m → 0.95 m 연속 접근</h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{figure('11_gazebo_approach.mp4', '카메라 시점에서 두 포켓을 계속 검출하는 연속 접근', '카메라 시점 · Gazebo', video=True, cls='')}
{figure('14_external_approach.mp4', '같은 접근을 3인칭에서 본 장면', '외부 시점 · MuJoCo', video=True, cls='')}
</div>
<div class="takeaway">접근 구간: 2.95 m부터 0.95 m까지 끊김 없이 포켓 유지</div>
""",
    """팔레트에 가까워지는 동안 포켓을 계속 찾을 수 있는지 확인하였다. 좌측은 Gazebo Harmonic으로 만든 카메라 시점이고, 우측은 MuJoCo의 잠정 차체 모델로 같은 접근을 보여 준 화면이다. 카메라와 팔레트 앞면 사이 거리 2.95 미터에서 시작하여 비스듬히 접근하며 방향을 맞추고 0.95 미터까지 이동하였다. 초록은 장면에 설정한 포켓 위치이고 자홍은 인식 프로그램이 계산한 위치로, 화면에서 대부분 겹쳐 보인다. 주황색은 카메라가 위아래로 볼 수 있는 범위이다. 접근 경로를 따라 20 밀리미터 간격으로 촬영하여 연속 영상으로 구성하였다.""",
    [(E6, 'Gazebo 촬영 파이프라인'), (PLAN, '자세 범위와 검출 판정')], '화면 생성: Gazebo Harmonic · MuJoCo')

# ----------------------------------------------------------------- 9
add('평가 결과', '08  평가 결과', 70, f"""
<h2 class="headline">표준 치수 100장면에서 목표를 모두 넘겼다</h2>
<div class="split grow" style="grid-template-columns:1.05fr 1fr">
{figure('03_scene_variety.png', '먼 거리, 가까운 거리, 비스듬한 자세, 가림, 유사 물체, 팔레트 없음', '100장면 중 6가지 조건', cls='')}
{figure('17_targets.png', '검출률 100%, 위치 오차 p95 8.17 mm, 방향 오차 p95 0.053도', '', cls='')}
</div>
<div class="takeaway">판단 범위: 가상 장면에서만 확인, 실제 센서는 재측정 필요</div>
""",
    """지금 확보한 유럽 표준 팔레트 EPAL 6 의 치수로 장면 100개를 만들어 촬영하고 평가하였다. 좌측은 여섯 가지 조건의 예이다. 포켓이 가려져 판단할 수 없는 장면은 인식 결과에서 제외해야 하며, 비슷한 물체나 팔레트가 없는 장면을 포켓으로 잘못 판단해서도 안 된다. 촬영 장면 100개를 모두 확보하였다. 그중 포켓을 찾아야 하는 장면이 60개, 찾으면 안 되는 장면이 40개이며, 찾아야 하는 60개는 전부 검출하였다. 우측은 개발 로드맵에 정한 초기 목표와 이번 측정값이다. 이 목표는 개발을 시작할 때 제안한 값이며 실물 장비의 합격 기준은 아니다. 검출률은 기준 95퍼센트에 대해 100퍼센트였다. p95는 측정 오차를 작은 순서로 놓았을 때 95퍼센트가 이 값 이하인 경계이다. 위치 오차 p95는 기준 20밀리미터에 대해 8.17밀리미터, 방향 오차 p95는 기준 2도에 대해 0.053도였다. 수치상 세 기준을 충족하였으나 실제 장비의 목표 달성으로 판단할 수는 없다. 컴퓨터가 만든 거리 영상이고, 축소 T11과 전체 거리 구간은 평가하지 않았다. 실제 센서에는 물체까지의 거리 2.5미터에서 약 50밀리미터의 거리 측정 오차가 있으며, 이번 평가에는 이 오차를 반영하지 않았다.""",
    [(E6, '개발용 42/42, 평가용 18/18, 위치 p95 8.17 / 5.98 mm, 위양성 0'),
     (MAP, '개발 로드맵의 초기 목표')], '화면 생성: Gazebo Harmonic')

# ----------------------------------------------------------------- 10
add('카메라 설치 높이', '09  카메라 설치 높이', 59, f"""
<h2 class="headline">카메라를 높일수록 가까운 팔레트를 놓친다</h2>
{figure('13_camera_mount.png', '카메라 높이 0.27, 0.50, 0.90 m에서의 화각과 가장 가까운 검출 거리', '적색 점이 카메라')}
<div class="takeaway">설치 판단: 마스트 상단은 1.75 m 이내를 못 봐 낮은 위치로 개발</div>
""",
    """카메라 설치 높이별로 팔레트까지의 정면 거리를 100밀리미터씩 바꾸며 포켓을 찾을 수 있는지 측정하였다. 먼 곳을 볼 수 있는 범위는 비슷하였으나, 높이 설치할수록 가까운 포켓을 먼저 놓쳤다. 마스트는 포크를 위아래로 움직이는 세로 기둥이다. 과제 설명자료처럼 그 상단에 카메라를 설치하면 팔레트까지의 거리 1.75미터 이내에서 포켓을 찾지 못하였고, 검출한 시험 지점 수도 절반으로 줄었다. 화면의 설치 조건별로 인식이 끊기는 순간 포크 끝에서 팔레트까지 남은 거리는 각각 850, 1050, 1550 밀리미터이다. 카메라를 낮추면 포켓을 찾을 수 있는 가장 가까운 거리가 1.05미터로 줄었으나, 개선 폭은 0.2미터 수준이었다. 시험한 상단 설치 조건에서는 가까이 접근하는 구간의 인식이 어려워, 낮은 설치 위치를 기준으로 개발하고 있다. 최종 높이는 실제 마스트 높이와 포크가 위아래로 움직이는 범위를 측정한 후 확정한다.""",
    [(E6, '장착 높이별 검출 구간 측정'),
     (WK3, '포크 끝 잔여 거리 850 / 1050 / 1550 mm'),
     (BRIEF, '과제 원문 4쪽 — 마스트 상단 카메라')],
    '기준: 카메라에서 팔레트 앞면까지의 거리')

# ----------------------------------------------------------------- 11
add('삽입 구간 관측 한계', '10  삽입 구간 관측 한계', 66, f"""
<h2 class="headline">포크를 넣기 직전에 팔레트 앞면이 시야에서 사라진다</h2>
<div class="split grow" style="grid-template-columns:1.75fr 1fr">
{figure('06_near_field_blind.png', '1.20 m에서는 앞면과 포켓이 보이고 0.60 m에서는 윗판만 보인다', '', cls='')}
{figure('09_docking_preview.mp4', '차체 모델이 팔레트에 포크를 넣는 미리보기', '포크가 들어가는 구간', video=True, cls='')}
</div>
<div class="takeaway">필요 기능: 안 보이는 구간을 이어 줄 포켓 추적</div>
""",
    """팔레트에 가까워지면 카메라에는 앞면이 사라지고 윗판만 보인다. 카메라를 바닥에서 0.5미터 높이에 두면 0.97미터보다 가까운 바닥은 화면에 들어오지 않는데, 팔레트 앞면이 바로 그 바닥에 붙어 있기 때문이다. 좌측 그림이 그 비교이다. 앞면이 카메라가 볼 수 있는 범위를 벗어나면 인식 기준값을 바꾸어도 보이지 않는 면을 찾을 수 없다. 앞 장에서 본 낮은 설치 위치에서도 접근 방식에 따라 0.8미터에서 1.3미터 사이에서 인식이 끊겼다. 앞 장의 1.75미터는 마스트 상단에 설치한 경우이므로, 낮게 달아도 끊기는 구간 자체는 남는다는 뜻이다. 포크 길이는 420밀리미터이므로 이 구간은 포크를 넣는 동안 내내 이어진다. 시험한 설치 높이에서는 삽입 완료 구간까지 앞면을 볼 수 없었다. 우측은 그 구간의 동작을 보여 주며 접촉과 무게의 영향은 계산하지 않았다. 중간 거리에서도 인식이 끊기는 구간이 있었다. 따라서 영상 한 장마다 포켓을 새로 찾는 기능에 더해, 이전에 찾은 위치를 이어서 추정하는 추적 기능이 필요하다. 이 기능은 다음 주 작업이다. 과제가 제시한 네 가지 접근 상황 가운데 옆에서 비스듬히 들어가는 경우와 팔레트가 너무 가까운 경우가 모두 이 구간에 걸린다.""",
    [(WK3, '카메라 0.50 m 에서 최근접 바닥 0.97 m, 그 앞뒤 판정'),
     (EV, '근접 미검출은 검출기가 아니라 카메라 화각'),
     (PLAN, '접근 방식별 검출 구간')], '화면 생성: 측정 리그 · MuJoCo')

# ----------------------------------------------------------------- 12
add('향후 추진 계획', '11  향후 추진 계획', 37, """
<h2 class="headline">다음은 추적, 그 다음은 차체</h2>
<div class="roadmap grow"><article class="done"><h3>지금까지</h3><p>포켓 인식 구현·평가</p><p class="state">완료</p></article><article class="now"><h3>다음 주</h3><p>포켓 추적</p><p class="state">착수</p></article><article class="wait"><h3>차체 입고 후</h3><p>실측 · 팔레트 제작 · 실제 센서 재측정</p><p class="state">대기</p></article><article class="wait"><h3>그 이후</h3><p>지도 작성 · 주행 · 삽입 · 이송</p><p class="state">예정</p></article></div>
<div class="takeaway">다음 단계: 포켓 추적 구현, 차체 입고 후 실제 센서로 재측정</div>
""",
    """다음 주에는 차체 없이 할 수 있는 포켓 추적을 진행한다. 카메라가 매 순간 새로 찾는 대신 앞에서 본 위치를 이어서 유지하는 기능이며, 가림이나 지연으로 관측이 끊겼을 때 삽입을 중단하는 동작까지 확인한다. 카메라 높이는 차체를 실측한 뒤 확정하고, 그 높이에 맞추어 장면을 다시 만들어 촬영한다. 차체를 받으면 시험용 팔레트를 제작하고 실제 센서로 같은 항목을 다시 측정한다. 지도 작성과 주행은 그 다음 단계이다. 이번 자료의 수치는 모두 센서의 흔들림을 넣지 않은 조건에서 나온 값이므로 실제 센서로 재확인이 필요하다.""",
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
