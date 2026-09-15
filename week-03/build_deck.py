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
    """이번 주에는 팔레트의 두 포켓을 찾고, 위치와 포크 삽입 방향을 로봇 기준 좌표로 나타내는 기능을 구현하였다. 포켓은 포크가 들어가는 구멍이다. 합성 장면의 평가 결과와 한계, 다음 작업을 보고한다.""",
    [(M2, '포켓 인식 검증 기록'), (E6, 'EPAL 6 캡처와 평가')], '측정 결과 보고')

# ----------------------------------------------------------------- 2
add('개발 진행 현황', '01  개발 진행 현황', 47, """
<h2 class="headline">개발 단계별 진행 현황</h2>
<div class="pipeline grow"><article class="pipeline-step done"><h3>① 포켓 인식</h3><p>깊이 영상에서<br>팔레트·포켓 검출</p><p class="state">합성 평가 완료</p></article><article class="pipeline-step done"><h3>② 좌표 산출</h3><p>포켓 위치·방향을<br>로봇 기준으로 표시</p><p class="state">구현 완료</p></article><article class="pipeline-step wait"><h3>③ 경로 생성</h3><p>장애물을 피하며<br>팔레트에 접근</p><p class="state">차체 입고 후</p></article><article class="pipeline-step now"><h3>④ 삽입·적재</h3><p>포켓 추적 후<br>포크 삽입</p><p class="state">추적: 다음 주<br>삽입: 차체 입고 후</p></article><article class="pipeline-step wait"><h3>⑤ 이송·하역</h3><p>목적지까지<br>운반·하역</p><p class="state">삽입 구현 후</p></article></div>
<div class="takeaway">이번 주: ①·② 구현 | 합성 센서 관측 161회(32초) 기록·재생 일치 확인</div>
""",
    """과제의 작업 절차는 포켓 인식부터 운반·하역까지 다섯 단계이다. 이번 주에는 1단계 포켓 인식과 2단계 포켓 위치·방향의 로봇 기준 좌표 산출을 구현하였다. 3단계 경로 생성과 실제 포크 삽입·적재는 차체의 주행 특성이 필요하므로 입고 뒤 착수할 예정이다. 4단계 중 차체 없이 시험할 수 있는 포켓 위치 추적은 다음 주 합성 환경에서 시작한다. 센서 측정값은 합성 환경에서 32초 동안 161회 기록하였고, 새 프로세스에서 재생하여 같은 값이 읽히는 것을 확인하였다.""",
    [(BRIEF, '과제 원문 7쪽의 다섯 단계'), (MAP, '개발 로드맵')], '출처: 과제 설명자료 7쪽')

# ----------------------------------------------------------------- 3
add('2D LiDAR 관측 범위', '02  2D LiDAR 관측 범위', 66, f"""
<h2 class="headline">설치 높이 0.50 m에서 팔레트 측정점 0개</h2>
{figure('21_lidar_plane.png', '옆에서 본 거리 측정 높이와 같은 높이에서 수평 360도 방향의 측정점. 팔레트 측정점은 0개', '')}
<div class="takeaway">센서 역할: 2D LiDAR는 주변 장애물 측정, RGB-D는 팔레트·포켓 인식</div>
""",
    """2D LiDAR는 센서가 설치된 높이의 수평면에서 물체까지의 거리를 잰다. MuJoCo에서 설치 높이를 바닥 기준 0.50미터로 설정하여 수평 360도 방향을 측정하였다. 이 조건에서 벽·기둥·상자에서는 거리 측정점 298개가 나왔지만, 높이가 144밀리미터인 유럽형 EPAL 6 팔레트에서는 0개였다. 제작 예정인 축소 T11의 높이도 90밀리미터로 관측면보다 낮다. 그래서 현재 설계에서는 LiDAR를 주변 장애물 측정에, 컬러 영상과 깊이 정보를 함께 얻는 RGB-D 카메라를 팔레트 인식에 사용한다. 다른 LiDAR 설치 높이까지 일반화한 결과는 아니다. 로봇 이동량을 계산하는 오도메트리가 없으므로 지도 작성과 로봇 위치 추정도 아직 구현하지 않았다.""",
    [(SB, '센서 기준선 — 실시간 161회 / 32.0초, 기록 재생 일치'),
     (MAP, '지도 작성·위치 추정은 차체 입고 후 단계')], '지도 작성·로봇 위치 추정(SLAM) 미구현')

# ----------------------------------------------------------------- 4
add('포켓 인식 처리 과정', '03  포켓 인식 처리 과정', 49, f"""
<h2 class="headline">깊이 영상에서 두 포켓을 찾는 네 단계</h2>
{figure('20_pipeline_stages.png', '깊이 영상, 팔레트 앞면, 받침목과 빈 공간, 판정된 포켓 위치의 네 단계', '')}
<div class="takeaway">검출 조건: 받침목·빈 공간·윗판·아랫판이 영상에 보여야 함</div>
""",
    """포켓 검출에는 학습 모델 대신 팔레트의 치수와 형상 규칙을 사용하였다. 그림은 Gazebo에서 만든 한 장면을 처리한 실제 중간 결과이다. 깊이 영상은 각 화소에 물체까지의 거리를 기록한다. 이 장면의 측정점 약 30만 7천 개 중 작업 범위에 속한 2만 454개를 남기고, 그 안에서 팔레트 앞면에 해당하는 수직 평면을 추렸다. 다음으로 앞면을 세로 칸으로 나누어 팔레트를 받치는 받침목 후보 37칸과 빈 공간 2구간을 구분하였다. 빈 공간의 폭은 두 곳 모두 220밀리미터로, 규격이 허용하는 207.5~247.5밀리미터 안에 들었다. 마지막으로 빈 공간의 폭과 윗판·아랫판의 관측 여부를 확인하여 두 포켓의 중심과 포크 삽입 방향을 계산하였다. 포켓 주변 구조가 화면 밖으로 나가면 이 방법만으로 검출하기 어렵다.""",
    [(M2, '검출기 설계와 단계 정의'), (EV, '측정 리그와 단계별 증거')], '대상 장면: 촬영 세트 s003')

# ----------------------------------------------------------------- 5
add('시험용 팔레트 선정', '04  시험용 팔레트 선정', 47, f"""
<h2 class="headline">차체 조건을 고려한 시험용 팔레트 결정</h2>
{figure('15_pallet_choice.png', '팔레트 후보 다섯 종을 같은 축척으로 놓고 길이 420밀리미터인 포크의 도달 범위를 비교', '후보 5종 비교 · 포크 길이 420 mm · 잠정 차체 적재 한도 10 kg')}
<div class="takeaway">제작 결정: T11 규격을 0.6배로 축소한 660 × 660 × 90 mm 팔레트</div>
""",
    """시험용 팔레트는 잠정 차체의 적재 한도와 포크 길이를 고려하여 결정하였다. 카탈로그상 적재 한도는 10킬로그램이고 포크 길이는 420밀리미터이다. 조사한 국내 표준 대여 품목에는 한 변이 1,000밀리미터보다 짧은 규격이 없었다. 조사한 시장 제품의 가장 짧은 변도 740밀리미터였다. 그림의 EPAL 6은 팔레트 자체 무게가 9에서 10킬로그램이어서 화물을 더 싣기 어렵다. 이에 국내 표준 T11의 치수를 0.6배로 줄인 660 × 660 × 90밀리미터 팔레트를 시험용으로 제작하기로 결정하였다. 아직 제작하지 않았으며, 인식 프로그램은 원래 규격과 축소 규격을 모두 다룰 수 있어야 한다.""",
    [(ADR, '팔레트 규격 결정과 무게·도달률 근거')], '출처: ADR 0002')

# ----------------------------------------------------------------- 6
add('초기 설정의 한계', '05  초기 설정의 한계', 52, f"""
<h2 class="headline">아랫판 증거 문턱 100개에 EPAL 6은 38개</h2>
{figure('22_lower_deck.png', '같은 자세를 두 팔레트로 촬영한 비교. 아랫판 윗면 ±6 mm 띠 안의 측정점이 12,686개와 38개', '')}
<div class="takeaway">초기 EPAL 6 합성 시험: 자세 125개 중 12개 검출 | 문턱 100개는 아랫판 50 mm 기준</div>
""",
    """검출기는 포켓으로 판정하기 전에 아랫판이 실제로 보이는지 확인한다. 아랫판 윗면 높이에서 위아래 6밀리미터 띠에 든 측정점을 세고, 그 개수가 문턱을 넘어야 한다. 문턱 100개는 아랫판이 50밀리미터이던 초기 팔레트에서 정한 값이다. EPAL 6의 아랫판은 22밀리미터, 제작 예정인 축소 T11은 15밀리미터여서 띠가 얇고 측정점도 적다. 그림은 같은 자세를 두 팔레트로 촬영한 것으로, 초기 팔레트는 12,686개, EPAL 6은 38개였다. 문턱을 넘지 못하면 받침목과 윗판이 아무리 잘 보여도 포켓으로 판정하지 않는다. 이 설정에서 EPAL 6 모델의 위치와 방향을 바꾼 합성 자세 125개 중 12개에서만 포켓을 찾았다. 바닥에서 20밀리미터까지의 측정점을 일괄 제외하던 설정도 이 얇은 띠를 함께 깎고 있어 나중에 같이 고쳤다. 다만 촬영 장면 101개로 확인하니 그 항만 고쳐서는 검출 수가 바뀌지 않았고, 결과를 바꾼 것은 문턱이었다.""",
    [(WK3, '같은 자세 s099 의 아랫판 증거 12,686개 대 38개, 문턱 100개'),
     (M2, '고정값 적용 시 자세 125개 중 12개'),
     (EV, '아랫판 증거대와 게이트 항')], '출처: 측정 기록 2026-09-15')

# ----------------------------------------------------------------- 7
add('기준값 산출 방식', '06  기준값 산출 방식', 57, f"""
<h2 class="headline">팔레트 치수에 맞춘 기준값과 검출 결과</h2>
{figure('04_frozen_vs_derived.mp4', '같은 합성 접근 장면 101개를 두 설정으로 비교. 왼쪽 고정 기준 0개, 오른쪽 치수 기반 기준 97개 검출', 'Gazebo 합성 접근 자세 101개 · 고정 0개 / 치수 기반 97개 검출')}
<div class="swap"><div><b>아랫판 증거 문턱</b><span>100개 <i>→</i> 15개</span></div></div>
<div class="takeaway">축소 T11 합성 자세: 0/60 → 58/60 검출 | 최대 위치 오차 509.1 mm 1건</div>
""",
    """고정된 숫자 대신 팔레트 치수에서 판정 기준을 계산하도록 변경하였다. 바닥에서 측정점을 버리는 높이는 바닥판 두께의 3분의 1로 두어 20밀리미터에서 7.3밀리미터가 되었고, 같은 면으로 묶는 두께는 축소 비율에 맞춰 20밀리미터에서 7.8밀리미터로 줄었다. 필요한 측정점 수는 관측 면적에 맞춰 축소 비율의 제곱을 적용하여 문턱을 100개에서 15개로 낮추었다. 영상은 동일한 Gazebo 합성 접근 자세 101개를 두 설정으로 처리한 결과이다. 고정 기준에서는 포켓 검출이 0개였고, 치수 기반 기준에서는 97개였다. 제작 예정인 축소 T11 모델의 별도 합성 자세 60개에서도 검출 수가 0개에서 58개로 늘었다. 다만 검출된 자세 중 위치 오차가 509.1밀리미터인 사례가 한 건 있었다. 따라서 검출 수가 늘었다는 결과와 좌표 정확도는 구분해야 한다.""",
    [(WK3, '항별 분리 측정: 문턱만 고쳐도 50/101, 바닥 제외만 고치면 0/101'),
     (WK3, '재측정: 축소 T11 자세 60개 중 0 → 58, 최악 오위치 509 mm'),
     (PLAN, '유도 공식과 기준점 선택'),
     (E6, '촬영 세트 101자세')], '화면 생성: Gazebo 촬영 장면')

# ----------------------------------------------------------------- 8
add('접근 동작 확인', '07  접근 동작 확인', 50, f"""
<h2 class="headline">비스듬한 위치에서 정렬하며 접근할 때의 검출</h2>
<div class="split grow" style="grid-template-columns:1.4fr 1fr">
{figure('11_gazebo_approach.mp4', 'Gazebo 카메라 시점에서 포켓 검출 결과를 보인 합성 접근', '합성 카메라 시점 · Gazebo Harmonic', video=True, cls='')}
{figure('14_external_approach.mp4', 'MuJoCo 잠정 차체 모델로 같은 접근 자세를 밖에서 본 영상', '잠정 차체의 카메라 시야 참고 영상 · MuJoCo', video=True, cls='')}
</div>
<div class="takeaway">왼쪽: 포켓 검출 성공·실패 | 오른쪽: 같은 자세의 외부 시점 | 실제 주행 아님</div>
""",
    """팔레트를 비스듬히 바라보다 정렬하며 가까워지는 합성 자세를 순서대로 확인하였다. 카메라–팔레트 앞면 거리를 2.95미터에서 0.95미터까지 20밀리미터씩 바꾼 101개 자세 중, 왼쪽 Gazebo 장면에서는 97개에서 포켓을 검출하였다. 초록은 정답 위치, 자홍은 검출 위치이다. 오른쪽은 같은 자세를 잠정 차체 모델 밖에서 보여 주며 주황색 선으로 카메라가 볼 수 있는 범위를 표시한다. 오른쪽에는 프레임별 판정을 표시하지 않는다. 검출 결과는 왼쪽 영상에서만 읽는다. 두 영상 모두 실제 주행이나 경로 제어 시연이 아니다.""",
    [(E6, 'Gazebo 촬영 파이프라인'), (PLAN, '자세 범위와 검출 판정')], '화면 생성: Gazebo Harmonic · MuJoCo')

# ----------------------------------------------------------------- 9
add('평가 결과', '08  평가 결과', 70, f"""
<h2 class="headline">EPAL 6 합성 장면 100개의 포켓 인식 평가</h2>
<p class="small muted">검출 대상 60장면(60/60 검출) · 비검출 대상 40장면(잘못 검출 0/40)</p>
{figure('03_scene_variety.png', '먼 거리, 가까운 거리, 비스듬한 자세, 가림, 유사 물체, 팔레트 없음', '')}
<div class="scores">
  <div><b>검출 대상 장면</b><span class="hit">100 %</span><i>초기 목표 95 % 이상</i></div>
  <div><b>위치 오차 p95</b><span class="hit">8.17 mm</span><i>초기 목표 20 mm 이하</i></div>
  <div><b>방향 오차 p95</b><span class="hit">0.053°</span><i>초기 목표 2° 이하</i></div>
</div>
<div class="takeaway">p95: 오차 95 %가 이 값 이하 | 합성 결과로, 실센서 오차·축소 T11 미반영</div>
""",
    """EPAL 6 모델로 만든 합성 장면 100개를 평가하였다. 포켓을 검출해야 하는 장면 60개는 모두 검출하였고, 검출 대상이 아닌 40개에서는 잘못된 검출이 0개였다. 검출 대상 60개에는 개발용 42개와 별도로 나눈 평가용 18개가 포함된다. 포켓 위치 오차 p95는 8.17밀리미터, 방향 오차 p95는 0.053도였다. p95는 오차의 95퍼센트가 해당 값 이하라는 뜻이다. 수치상 초기 개발 로드맵의 제안 목표인 검출률 95퍼센트 이상, 위치 오차 20밀리미터 이하, 방향 오차 2도 이하에 들었다. 그러나 실물 합격 기준을 검증한 결과는 아니다. 거리 2.5미터에서 약 50밀리미터로 알려진 실제 센서의 깊이 오차를 합성 평가에 넣지 않았고, 축소 T11도 이 장면 세트에는 포함하지 않았다.""",
    [(E6, '개발용 42/42, 평가용 18/18, 위치 p95 8.17 / 5.98 mm, 위양성 0'),
     (MAP, '개발 로드맵의 초기 목표')], '화면 생성: Gazebo Harmonic')

# ----------------------------------------------------------------- 10
add('카메라 설치 높이', '09  카메라 설치 높이', 59, f"""
<h2 class="headline">카메라를 높일수록 가까운 포켓을 먼저 놓침</h2>
{figure('13_camera_mount.png', '카메라 높이 0.27, 0.50, 0.90 m에서 같은 거리에 둔 팔레트와 각 높이의 수직 관측 범위', '적색 점이 카메라 위치')}
<div class="takeaway">합성 비교: 0.6~2.3 m 구간의 자세 35개 중 22 / 20 / 4개 검출 | 실제 설치 높이 미확정</div>
""",
    """카메라 높이가 근거리 포켓 검출에 미치는 영향을 합성 환경에서 비교하였다. 바닥 기준 높이 0.27, 0.50, 0.90미터에서 카메라–팔레트 전면 거리 0.6미터부터 2.3미터까지를 5센티미터 간격으로 훑어 검출 여부를 세었다. 자세 35개 중 검출된 것은 각각 22, 20, 4개였다. 이번 조건에서는 카메라가 높을수록 이 구간에서 포켓을 보는 자세가 줄었다. 검출이 끊기는 한 점을 한계 거리로 적지는 않았다. 검출 구간이 연속이 아니어서 그 값이 측정 간격에 따라 달라지기 때문이다. 같은 조건에서 간격을 1센티미터로 줄이면 0.50미터 높이의 가장 가까운 검출 거리가 1.05미터에서 0.84미터로 바뀐다. 0.90미터는 과제 설명자료의 마스트 상단 설치안이며, 마스트는 포크를 올리는 수직 구조물이다. 실제 카메라 위치는 차체가 입고된 뒤 실측하여 결정할 예정이다.""",
    [(WK3, '재측정: 0.6~2.3 m 구간 검출 22 / 20 / 4, 간격에 따른 최근접 변동'),
     (BRIEF, '과제 원문 4쪽 — 마스트 상단 카메라')],
    '기준: 카메라에서 팔레트 전면까지의 거리')

# ----------------------------------------------------------------- 11
add('삽입 구간 관측 한계', '10  삽입 구간 관측 한계', 66, f"""
<h2 class="headline">가까워지면 팔레트 앞면이 화면 아래로 사라짐</h2>
{figure('06_near_field_blind.png', '1.20 m 에서는 전면과 포켓이 관측되고 0.60 m 에서는 상판만 관측된다', '')}
<div class="takeaway">다음 작업: 이전 포켓 위치 추적과 관측 중단 시 삽입 정지 조건</div>
""",
    """앞 장은 설치 높이에 따른 차이였다. 이번에는 현재 합성 평가 기준인 0.50미터 높이에서 검출이 끊기는 이유를 확인하였다. 카메라 화면의 아래 경계는 전방 0.97미터 지점에서 바닥과 만난다. 그보다 가까운 바닥은 화면에 들어오지 않는다. 팔레트 앞면은 높이가 있어 위쪽 일부가 조금 더 가까이까지 남지만, 포켓 입구는 아래쪽이라 바닥과 함께 화면에서 밀려난다. 측정 리그의 정면 장면에서 카메라–팔레트 전면 거리 1.20미터에서는 앞면과 포켓을 검출했지만, 0.60미터에서는 윗판만 보이고 포켓은 검출하지 못했다. 따라서 매 영상에서 새로 포켓을 찾는 기능만으로는 삽입 구간의 위치 정보를 유지할 수 없다. 다음 주에는 이전에 검출한 위치를 추적하고, 관측이 끊겼을 때 삽입을 정지하는 조건을 합성 환경에서 시험할 계획이다. 이 결과는 실제 카메라 영상이나 실제 삽입 주행이 아니다.""",
    [(WK3, '카메라 0.50 m 에서 최근접 바닥 0.97 m, 그 앞뒤 판정'),
     (EV, '근접 미검출은 검출기가 아니라 카메라 화각'),
     (PLAN, '접근 방식별 검출 구간')], '화면 생성: 측정 리그')

# ----------------------------------------------------------------- 12
add('향후 추진 계획', '11  향후 추진 계획', 37, f"""
<h2 class="headline">다음 주 작업과 차체 입고 후 검증</h2>
<div class="split grow" style="grid-template-columns:1.15fr 1fr">
{figure('09_docking_preview.mp4', '접촉과 화물 하중을 반영하지 않은 MuJoCo 잠정 차체의 포크 삽입 시각화', 'MuJoCo 동작 시각화 · 실제 삽입 검증 아님', video=True, cls='')}
<div class="roadmap"><article class="done"><h3>이번 주까지</h3><p>포켓 인식·좌표 산출<br>합성 장면 평가</p><p class="state">완료</p></article><article class="now"><h3>다음 주</h3><p>포켓 위치 추적·<br>관측 중단 시 정지 조건</p><p class="state">합성 시험 예정</p></article><article class="wait"><h3>차체 입고 후</h3><p>차체 실측·시험용 팔레트 제작<br>실센서 재측정</p><p class="state">계획</p></article><article class="wait"><h3>그 이후</h3><p>지도·주행 제어<br>실제 삽입·이송·하역</p><p class="state">계획</p></article></div>
</div>
<div class="takeaway">현재 수치는 합성 조건의 인식 결과이며 실제 지게차 성능은 재측정 필요</div>
""",
    """다음 주에는 합성 환경에서 포켓 위치 추적과 관측 중단 시 정지 조건을 시험할 계획이다. 영상은 접촉·하중·실제 주행 제어를 반영하지 않은 잠정 모델의 시각화이다. 차체 입고 후 치수와 카메라 위치를 실측하고, 축소 T11을 제작해 실제 센서로 평가하겠다. 이후 지도 작성, 주행 제어, 실제 삽입·이송·하역을 진행할 계획이다. 이번 수치는 실제 지게차 성능을 검증한 결과가 아니다.""",
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
        notes = (f"권장 {s['seconds']}초\n\n{s['notes']}\n\n"
                 f"[Sources]\n{s['foot']}\n{source_lines}\n[/Sources]")
        if i == 1:
            component = (f'<x-import component-from-global-scope="UOSSlideDS.TitleSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}" '
                         f'subtitle="임베디드구동 및 실습 · 팔레트 핸들링 경로 생성 및 제어"></x-import>')
        else:
            # 출처·쪽번호 줄은 본문 아래 한 줄을 통째로 먹으면서 화면에서는
            # 읽히지 않는다. 그 높이를 그림과 본문에 돌리고, 출처는 위의
            # 발표자 노트에 남긴다.
            component = (f'<x-import component-from-global-scope="UOSSlideDS.ContentSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}">'
                         f'<div class="slide-body">{s["body"]}</div></x-import>')
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
