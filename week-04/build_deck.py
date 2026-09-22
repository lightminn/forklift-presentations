"""Build the week 4 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.
Week 4 mixes three kinds of screen and each slide's speaker note names which
one it is: 실물 사진 (photographs of the delivered chassis, 2026-09-23),
Isaac Sim renders, and diagrams drawn from measured numbers.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
BRIEF = 'https://docs.google.com/presentation/d/1BjoJLWmwd07ZJujZp4BPZrwBhx5tsnfmBpWdLMy2YrQ/edit'
INTAKE = 'docs/validation/2026-09-23-chassis-intake.md'
G1 = 'docs/validation/2026-09-21-g1-calibration-run.md'
STATUS = 'docs/plans/2026-09-17-project-status-and-next-steps.md'
HOOK = 'docs/validation/2026-09-19-perception-isaac-hookup.md'
HW = 'docs/hardware.md'
MAP = 'docs/plans/2026-09-11-development-roadmap.md'
ADR2 = 'docs/decisions/0002-test-pallet-and-geometry-generality.md'
W3M = 'docs/validation/2026-09-15-week-03-deck-measurements.md'
ADR3 = 'docs/decisions/0003-target-selection-and-blind-zone-insertion.md'
EPAL = 'config/pallet_geometry_epal6.yaml'
T11 = 'config/pallet_geometry_t11_06.yaml'
IFM = 'https://www.ifm.com/gb/en/shared/technologies/o3d/pallet-detection-system-pds/integration-of-the-pds'
CROWN = 'https://patents.google.com/patent/US9990535B2/en'
AIST = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12788346/'
ADAPT = 'https://arxiv.org/html/2503.14331v1'
D435I = 'https://www.realsenseai.com/products/depth-camera-d435i/'
RSTUNE = 'https://dev.realsenseai.com/docs/tuning-depth-cameras-for-best-performance/'
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
    cap = f'<figcaption class="small muted">{caption}</figcaption>' if caption else ''
    return f'<figure class="shot {cls}">{tag}{cap}</figure>'


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '4주차\n자율 지게차 개발', 20, '',
    """이번 주에는 지게차 차체가 입고되어 구조 조사를 시작하였고, 3주차에 받은 카메라 장착에 관한 지적에 실제 지게차 사례로 답한다. 사진은 입고한 실물이고, 수치는 모두 컴퓨터로 만든 장면에서 잰 값이다.""",
    [(INTAKE, '차체 입고와 초기 구조 조사'), (IFM, '카메라 장착 사례')], '진행 보고')

# ----------------------------------------------------------------- 2
add('개발 진행 현황', '01  개발 진행 현황', 45, """
<h2 class="headline">다섯 단계의 현재 위치와 이번 주 작업</h2>
<div class="pipeline grow"><article class="pipeline-step done"><h3>① 팔레트 인식</h3><p>깊이 영상에서<br>팔레트·포켓 검출</p><p class="state">구현</p></article><article class="pipeline-step done"><h3>② 좌표 변환</h3><p>포켓 위치·방향을<br>로봇 기준으로 표시</p><p class="state">구현</p></article><article class="pipeline-step now"><h3>③ 경로 생성</h3><p>장애물을 피하며<br>팔레트에 접근</p><p class="state">시뮬레이션 연결</p></article><article class="pipeline-step now"><h3>④ 삽입·적재</h3><p>포크를 넣고<br>들어 올림</p><p class="state">시뮬레이션 연결</p></article><article class="pipeline-step now"><h3>⑤ 이송·하역</h3><p>목적지까지<br>운반·하역</p><p class="state">시뮬레이션 연결</p></article></div>
<div class="takeaway">실물: 차체 입고 · 전장과 조작 축 확인 · 카메라 장착 조건 조사</div>
""",
    """과제의 작업 절차는 팔레트 인식부터 이송·하역까지 다섯 단계이다. 3주차에는 1단계 인식과 2단계 좌표 변환을 구현하였다. 이후 3단계부터 5단계를 시뮬레이션 안에서 연결하여, 카메라가 추정한 팔레트 위치로 접근해 포크를 넣고 들어 올려 운반한 뒤 내려놓는 임무를 수행하였다. 아래 줄은 실물 작업이다. 차체가 입고되어 구성과 조작 경로를 확인하였고, 카메라 장착 조건을 조사하였다.""",
    [(BRIEF, '과제 원문 7쪽의 다섯 단계'), (STATUS, '현재 진행 상태')],
    '출처: 과제 설명자료 7쪽')

# ----------------------------------------------------------------- 3
add('차체 입고', '02  차체 입고', 55, f"""
<h2 class="headline">승용형 차체 입고 · 플라스틱 팔레트 1장 동봉</h2>
<div class="split grow" style="grid-template-columns:0.78fr 1.22fr">
{figure('01_chassis_and_pallet.jpg', '조립을 마친 지게차 차체와 함께 들어 있던 흑색 플라스틱 팔레트', '실물 사진 2026-09-23', cls='')}
<table class="comparison"><tr><th>관찰한 구성</th></tr>
<tr><td>운전석 보호 지붕 · 좌석 · 운전대</td></tr>
<tr><td>바퀴 4개</td></tr>
<tr><td><b>마스트</b> — 포크를 올리는 수직 구조물</td></tr>
<tr><td><b>포크 캐리지</b> — 마스트를 따라 포크와 함께 오르내리는 판</td></tr>
<tr><td>포크 2개</td></tr>
<tr><td>흑색 플라스틱 팔레트 1장 동봉</td></tr></table>
</div>
<div class="takeaway">다음 주 실측: 치수 · 무게 · 승강 범위 | 시험 팔레트: EPAL 6 · 축소 T11 유지</div>
""",
    """이번 주에 지게차 차체가 들어와 조립하였다. 운전석 위 보호 지붕과 좌석, 운전대를 갖춘 승용형이고 바퀴는 네 개이다. 앞쪽에는 포크를 올리는 수직 구조물인 마스트가 있고, 포크 두 개는 마스트를 따라 오르내리는 판인 포크 캐리지에 달려 있다. 이 캐리지는 뒤에서 카메라 장착 후보로 다시 다룬다. 구성품에는 흑색 플라스틱 팔레트 한 장이 함께 들어 있었다. 시험용 팔레트는 앞서 정한 EPAL 6과 축소 T11을 그대로 쓰고, 동봉 팔레트는 치수를 잰 뒤 두 규격과 비교한다. 차체의 치수와 무게, 승강 범위는 다음 주에 실측한다.""",
    [(INTAKE, '입고 구성과 관찰 범위'), (ADR2, '시험용 팔레트 규격 결정')],
    '화면 생성: 실물 사진 2026-09-23')

# ----------------------------------------------------------------- 4
add('기존 전장과 조작 축', '03  기존 전장과 조작 축', 60, f"""
<h2 class="headline">주행 · 조향 · 승강 모두 무선 조종기 입력</h2>
<div class="split grow" style="grid-template-columns:1.08fr 1fr">
{figure('03_electronics_bay.jpg', '좌석 아래에 나란히 고정된 제어기와 12V 표기가 있는 배터리, 백색 커넥터로 연결된 하네스', '좌석 아래 — 왼쪽이 제어기, 오른쪽이 배터리 · 실물 사진 2026-09-23', cls='')}
<div class="stack">
{figure('04_controller_label.jpg', '제어기 라벨을 확대한 사진 — J6, D-CC-12V, 3F81E C0054, ZHT BSJ TianJin5.0', '제어기 라벨', cls='')}
{figure('05_remote.jpg', '무선 조종기 T07D-DGN 의 전진·후진·상승·하강·좌회전·우회전 버튼', '무선 조종기', cls='')}
</div></div>
<div class="takeaway">자율 명령 연결 후보: 제어기 교체 · 조종기 신호 자리에 입력 · 유선 조작부 활용 — 배선 조사 후 선택</div>
""",
    """좌석 아래에 제어기와 배터리가 나란히 고정되어 있고, 색으로 구분한 심선이 백색 커넥터로 연결된다. 제어기 라벨은 J6 D-CC-12V이고 배터리에도 12볼트 표기가 있다. 함께 들어 있는 무선 조종기 T07D-DGN에는 전진과 후진, 상승과 하강, 좌회전과 우회전, 속도 조절과 제동 버튼이 있다. 주행과 조향, 승강 세 축이 모두 이 조종기의 무선 입력으로 움직인다. 따라서 컴퓨터의 명령을 넣는 방법은 세 갈래이다. 제어기를 우리 구동 회로로 바꾸거나, 조종기 신호가 들어가는 자리에 우리 신호를 넣거나, 운전석의 유선 조작 경로를 쓰는 것이다. 다음 주에 배선을 따라가 모터 정격과 신호 형식을 확인하고, 속도와 조향각, 포크 높이를 읽을 경로와 함께 하나를 고른다.""",
    [(INTAKE, '제어기·조종기·배터리의 표기'), (MAP, '로드맵 H1 전장과 피드백 조사')],
    '화면 생성: 실물 사진 2026-09-23')

# ----------------------------------------------------------------- 5
add('카메라 장착 사례', '04  카메라 장착 사례', 65, """
<h2 class="headline">실제 지게차의 팔레트 검출 센서 장착 위치</h2>
<table class="comparison grow"><tr><th>사례</th><th>장착 위치</th><th>센서와 역할</th></tr>
<tr><td>ifm 팔레트 검출 시스템</td><td>차체 전면 하부, <b>지면 위 23~36 cm</b>, 바닥·팔레트면에 수직</td><td>3D 카메라 · 팔레트 자동 검출</td></tr>
<tr><td>Crown 특허</td><td><b>포크 캐리지</b>, 포크가 시야 아래쪽에 오도록</td><td>카메라 · 포크와 함께 승강</td></tr>
<tr><td>AIST·도요타 리치트럭</td><td>캐리지와 한 몸인 <b>백레스트</b></td><td>어안 카메라 · 포크와 강체</td></tr>
<tr><td>ADAPT 자율 지게차</td><td>원거리 인식과 별도의 <b>근거리 전용 센서</b></td><td>마지막 접근 담당</td></tr></table>
<div class="takeaway">공통점: 포켓 높이 가까이 · 포크와 함께 움직이는 자리 | 후방·포크 안쪽 카메라는 운전자 보조용이라 제외</div>
""",
    """3주차에 실제 지게차의 카메라 장착을 확인하고 우리 차체에 맞추어 보라는 지적을 받았다. 후진 카메라나 포크 안쪽 카메라는 운전자가 보는 화면용이므로 제외하고, 컴퓨터가 팔레트를 찾는 센서만 모았다. ifm의 팔레트 검출 시스템은 3차원 카메라를 지면 위 23에서 36센티미터, 바닥과 팔레트 면에 수직으로 달도록 안내한다. Crown의 특허는 카메라를 포크 캐리지에 달아 포크가 시야 아래쪽에 들어오게 하고, AIST와 도요타의 리치트럭 연구는 캐리지와 한 몸인 백레스트에 어안 카메라를 달았다. ADAPT 자율 지게차는 마지막 접근을 별도의 근거리 센서에 맡긴다. 공통점은 포켓 높이에 가깝게, 포크와 함께 움직이는 자리에 단다는 것이다.""",
    [(IFM, 'ifm 팔레트 검출 시스템 통합 안내 — 지면 위 23~36 cm, 바닥·팔레트면에 수직'),
     (CROWN, 'Crown 특허 US9990535B2 — 포크 캐리지 장착, 포크를 시야 하단에'),
     (AIST, 'AIST·도요타 리치트럭 (Sensors 2026) — 백레스트 어안 장착, 카메라와 포크는 강체'),
     (ADAPT, 'ADAPT 자율 지게차 (arXiv 2503.14331) — 최종 접근은 근거리 전용 센서가 담당')],
    '출처: 제조사 안내 · 특허 · 논문')

# ----------------------------------------------------------------- 6
add('설치 높이 조건', '05  설치 높이 조건', 55, """
<h2 class="headline">팔레트 높이와 카메라 설치 높이</h2>
<svg class="height-chart grow" viewBox="0 0 1160 430" role="img" aria-label="팔레트 높이, ifm 장착 높이 안내, 3주차 측정 리그의 카메라 높이별 포켓 검출 수 비교">
<rect x="120" y="254" width="1000" height="52" fill="#e2f0fc"/>
<line x1="120" y1="18" x2="120" y2="398" stroke="#666" stroke-width="2"/>
<line x1="120" y1="398" x2="1120" y2="398" stroke="#666" stroke-width="2"/>
<g fill="#555" font-size="17" font-family="var(--uos-font)">
<text x="75" y="403">0</text><text x="69" y="323">200</text><text x="69" y="243">400</text><text x="69" y="163">600</text><text x="69" y="83">800</text><text x="67" y="29">mm</text>
</g>
<g stroke="#888" stroke-width="1"><line x1="112" y1="318" x2="120" y2="318"/><line x1="112" y1="238" x2="120" y2="238"/><line x1="112" y1="158" x2="120" y2="158"/><line x1="112" y1="78" x2="120" y2="78"/></g>
<rect x="205" y="340.4" width="155" height="57.6" fill="#d8dce1" stroke="#8c959e"/>
<rect x="410" y="362" width="155" height="36" fill="#d8dce1" stroke="#8c959e"/>
<g fill="#222" font-size="19" font-family="var(--uos-font)"><text x="215" y="333">EPAL 6 · 144 mm</text><text x="410" y="354">축소 T11 · 90 mm</text><text x="220" y="277">ifm 안내 23~36 cm (자사 센서 기준)</text></g>
<g fill="var(--uos-blue)" font-size="20" font-family="var(--uos-font)">
<circle cx="825" cy="290" r="7"/><text x="846" y="297">0.27 m · 22/35</text>
<circle cx="825" cy="198" r="7"/><text x="846" y="205">0.50 m · 20/35</text>
<circle cx="825" cy="38" r="7"/><text x="846" y="45">0.90 m · 4/35</text>
</g>
<text x="140" y="417" fill="#444" font-size="17" font-family="var(--uos-font)">3주차 측정 리그 · 0.6~2.3 m 구간에서 포켓을 검출한 자세 수(35개 중)</text>
</svg>
<div class="takeaway">낮을수록 가까운 포켓을 오래 봄 | 설치 높이는 캐리지 실측 후 포켓 높이 가까운 후보로 시험</div>
""",
    """사례의 수치를 그대로 옮기기 전에 우리 조건과 비교하였다. 팔레트는 차체와 함께 줄지 않는다. EPAL 6은 실물 규격 그대로 높이가 144밀리미터이고, 축소 T11은 90밀리미터이다. ifm의 23에서 36센티미터는 자사 센서와 표준 팔레트를 기준으로 한 값이어서 우리 카메라에 그대로 옮기지는 않는다. 다만 방향은 3주차 측정과 같다. 같은 장면에서 카메라를 0.27, 0.50, 0.90미터 높이에 두고 0.6에서 2.3미터 구간을 훑었을 때, 35개 자세 중 포켓을 검출한 수는 22, 20, 4개였다. 낮을수록 가까운 포켓을 오래 본다. 그래서 설치 높이는 포크 캐리지의 장착점을 실측한 뒤, 포켓 높이에 가까운 후보를 시험하여 정한다.""",
    [(EPAL, 'EPAL 6 전체 높이 144 mm'), (T11, '축소 T11 전체 높이 90 mm'),
     (IFM, 'ifm 설치 안내 — 23~36 cm'), (W3M, '설치 높이별 구간 검출 수 22 / 20 / 4')],
    '화면 생성: 규격 치수와 3주차 측정 리그 결과로 그린 도식')

# ----------------------------------------------------------------- 7
add('근거리 측정 한계', '06  근거리 측정 한계', 55, f"""
<h2 class="headline">D435i 근거리 측정 한계와 포크 길이</h2>
{figure('09_d435i_limits.png', '해상도별 최소 측정 거리와 권장 측정 범위, 그리고 팔레트 전면 800밀리미터가 가로 화각에 들어오는 최소 거리', '')}
<div class="swap"><div><b>포크 끝 접촉 시</b><span>약 420 mm &lt; 448 mm</span></div><div><b>360 mm 삽입 시</b><span>약 60 mm &lt; 280 mm</span></div></div>
<div class="takeaway">가정: 카메라가 포크 뿌리 위치의 캐리지에 정면으로 장착 | 마지막 삽입 구간은 카메라 하나로 끝까지 보지 못함</div>
""",
    """거리 조건은 팔레트가 아니라 센서가 정하고, 차체를 줄여도 함께 줄지 않는다. D435i는 가장 높은 해상도에서 280밀리미터보다 가까우면 깊이를 내지 못한다. 폭 800밀리미터인 EPAL 6 전면이 가로 화각에 모두 들어오려면, 두 렌즈 사이의 기선을 보정하여 계산하면 448밀리미터 이상 떨어져야 한다. 카메라를 포크 뿌리 위치의 캐리지에 정면으로 단다고 가정하면, 잠정 모델의 포크 길이 420밀리미터만큼 다가가 포크 끝이 팔레트에 닿는 순간 이미 전면 전체를 볼 수 없다. 360밀리미터를 넣으면 거리는 약 60밀리미터로 최소 측정 거리 안에 들어간다. 따라서 마지막 삽입 구간은 카메라 하나로 끝까지 볼 수 없으며, 앞 장의 근거리 전용 센서 사례가 다루는 것과 같은 문제이다. 이 구간을 잇는 방법은 장착점을 잰 뒤 정한다.""",
    [(D435I, 'Intel RealSense D435i 공식 사양 — 깊이 화각 87° × 58°, 권장 범위 0.3~3 m'),
     (RSTUNE, 'RealSense 튜닝 문서 — 해상도별 최소 측정 거리, 깊이 오차는 거리의 제곱에 비례'),
     (ADR3, '잠정 모델의 포크 길이 420 mm와 사용 가능 삽입량 406 mm'),
     (INTAKE, '카메라 장착을 위해 먼저 재야 할 항목')],
    '화면 생성: 공식 사양 도식 · 448 mm 는 기선 보정으로 직접 계산')

# ----------------------------------------------------------------- 8
add('카메라 모형 교정', '07  카메라 모형 교정', 55, f"""
<h2 class="headline">시뮬레이션 카메라의 화소 중심 기준 통일</h2>
{figure('07_half_pixel.png', '왼쪽은 정수 인덱스와 반정수 화소 중심의 0.5화소 차이, 오른쪽은 그 때문에 거리에 비례해 커지는 높이 편향', 'Isaac 교정 장면의 측정값으로 그린 도식')}
<div class="takeaway">Isaac 입력 단계에서 기준 변환 · 공통 검출기와 실제 카메라 경로는 그대로 | 복원 높이 편향 평균 +0.0002 mm</div>
""",
    """장착 후보를 바꿔 가며 시뮬레이션에서 시험하려면, 시뮬레이션 카메라가 사양대로 계산되어야 한다. 그래서 위치를 아는 교정판을 여러 거리에서 촬영해 복원 좌표를 확인하는 교정 단계를 두었다. 깊이 영상에서 삼차원 좌표를 복원하려면 영상 중심의 화소 위치가 필요한데, Isaac Sim은 화소 한 칸의 한가운데를, 우리 검출기는 칸의 번호를 기준으로 쓴다. 두 기준은 반 화소 다르고, 맞추지 않으면 오른쪽 그림처럼 복원한 높이가 거리에 비례해 밀린다. 기준 변환은 공통 검출기가 아니라 Isaac 입력 단계에 두어 실제 카메라 경로는 건드리지 않았다. 교정 장면에서 복원한 높이의 편향은 평균 0.0002밀리미터이다.""",
    [(G1, '반 화소 기준 차이와 Isaac 입력 어댑터에서의 변환'),
     (G1, '복원 높이 편향 평균 +0.0002 mm')],
    '화면 생성: 측정값 도식 · 왼쪽은 기준 모식도')

# ----------------------------------------------------------------- 9
add('임무 입력 구성', '08  임무 입력 구성', 45, """
<h2 class="headline">임무 입력별 정보원과 교체 계획</h2>
<table class="comparison grow"><tr><th>입력</th><th>현재 정보원</th><th>실물 단계의 정보원</th></tr>
<tr><td>팔레트 위치·방향</td><td class="blue"><b>카메라 추정</b> — 깊이 영상에서 포켓 검출</td><td>실제 D435i 영상</td></tr>
<tr><td>로봇 위치·방향</td><td>시뮬레이터 좌표</td><td>바퀴·조향 피드백 + 2D LiDAR 위치 추정</td></tr>
<tr><td>장애물 지도</td><td>시뮬레이터 배치</td><td>2D LiDAR 지도</td></tr>
<tr><td>목적지</td><td>시뮬레이터 좌표</td><td>지도 위 지정 좌표</td></tr>
<tr><td>삽입 중 간섭 검사</td><td>시뮬레이터 자세·형상</td><td>실물용 정지 조건 별도 설계</td></tr></table>
<div class="takeaway">검출 실패 시 다음 관측 지점에서 재관측 · 후보가 모두 떨어지면 중단</div>
""",
    """다음 영상이 무엇을 입력으로 쓰는지 표로 정리하였다. 카메라가 추정하는 것은 집으러 갈 팔레트의 위치와 방향이다. 로봇 자신의 위치, 장애물 지도, 목적지, 그리고 삽입 중 간섭 검사는 시뮬레이터의 좌표와 형상을 쓴다. 오른쪽 열은 실물 단계에서 각 입력을 대신할 정보원이며, 로봇 위치와 지도는 바퀴와 조향의 피드백, 그리고 2D LiDAR로 바꾼다. 간섭 검사는 이것과 별도로 실물용 정지 조건을 설계한다. 검출에 실패하면 정답 위치로 되돌아가지 않고 다음 관측 지점에서 다시 보며, 후보가 모두 떨어지면 중단한다.""",
    [(STATUS, '현재 운반 코드가 사용하는 입력의 구분'), (HOOK, '인식 연결 실측 기록')],
    '범위 구분')

# ----------------------------------------------------------------- 10
add('운반 임무', '09  운반 임무', 80, f"""
<h2 class="headline">카메라 추정 위치를 목표로 관측부터 하역까지</h2>
{figure('08_mission_seed2.mp4', '위에서 내려다본 시점에서 지게차가 관측·접근·삽입·운반·하역을 수행하는 영상', 'Isaac Sim · 3배속 · 초록 원이 내려놓을 목적지')}
<div class="swap"><div><b>임무 시간</b><span>75.4초</span></div><div><b>삽입 깊이</b><span>360 mm</span></div><div><b>종점 오차 · 계획 대비</b><span>7.65 mm</span></div></div>
""",
    """영상은 카메라가 추정한 팔레트 위치를 목표로 임무 전체를 수행한 한 사례이며, 위에서 내려다본 Isaac Sim 화면을 3배속으로 재생한다. 초록색 원이 내려놓을 목적지이다. 지게차는 관측 지점으로 이동해 정지한 상태에서 깊이 영상을 찍고, 검출한 포켓 위치로 경로를 만들어 접근한다. 이어 포크를 넣어 들어 올리고, 목적지까지 운반해 내려놓은 뒤 포크를 뺀다. 임무 시간은 75.4초였다. 삽입 깊이는 팔레트 깊이의 0.6배와 포크 캐리지 한계에서 정한 운영 목표 360밀리미터이다. 삽입 구간의 종점 오차 7.65밀리미터는 계획한 종점과 실제 도달 지점의 차이이다. 삽입하고 빼는 동안에는 검사 시점마다 포크와 팔레트 사이가 2밀리미터 넘게 떨어져 있는지 확인하고, 그보다 가까워지면 즉시 멈춘다. 여러 조건에서의 성공률은 다음 주에 다시 측정한다.""",
    [(STATUS, '임무 실행 단계별 실측 — 75.4초, 종점 오차 7.65 mm / 2.83 mrad'),
     (HOOK, '인식 연결 실행의 기록과 안전 검사 범위')],
    '화면 생성: Isaac Sim · 전 구간을 3배속으로')

# ----------------------------------------------------------------- 11
add('향후 추진 계획', '10  향후 추진 계획', 75, """
<h2 class="headline">차체 실측과 카메라 장착 확정</h2>
<div class="roadmap grow"><article class="now"><h3>차체 실측</h3><p>치수·무게·승강 범위<br>캐리지 장착점 좌표·기울기<br>카메라 시야 가림 확인</p><p class="state">다음 주</p></article><article class="now"><h3>제어 연결</h3><p>배선 종단·모터 정격<br>명령 입력 방식 선택<br>속도·조향각·포크 높이 취득 경로</p><p class="state">다음 주</p></article><article class="now"><h3>시뮬레이션</h3><p>여러 조건 임무 재실행<br>성공률과 실패 원인 정리<br>근접 포켓 추적 · 관측 소실 시 정지</p><p class="state">다음 주 → 그다음</p></article><article class="now"><h3>3주차 피드백 후속</h3><p>지게차 표준 운용 방법<br>시험용 팔레트 제작 방법<br>동봉 팔레트 실측·대조</p><p class="state">다음 주 보고</p></article></div>
<div class="takeaway">장착점 실측 → 카메라 위치 확정 → 좌표 변환과 시뮬레이션 장면에 반영</div>
""",
    """다음 작업은 네 갈래이다. 첫째, 차체의 치수와 무게, 승강 범위를 재고, 포크 캐리지에서 카메라를 달 자리의 좌표와 기울기를 잰다. 포크나 차체가 카메라 시야를 가리는지도 이때 확인한다. 캐리지에 달면 포크 높이에 따라 카메라 위치가 바뀌므로 좌표 변환도 함께 만든다. 둘째, 배선을 따라가 모터 정격과 신호 형식을 확인하여 명령을 넣을 방법을 고르고, 속도와 조향각, 포크 높이를 읽을 경로를 찾는다. 셋째, 시뮬레이션에서 여러 조건의 임무를 다시 돌려 성공률과 실패 원인을 정리하고, 이어서 삽입 중 포켓을 계속 보며 위치를 갱신하고 관측이 끊기면 멈추는 기능을 만든다. 넷째, 3주차에 받은 나머지 두 지적인 지게차의 표준 운용 방법과 시험용 팔레트 제작 방법을 조사하고, 동봉 팔레트를 재어 두 시험 규격과 비교하여 보고한다.""",
    [(MAP, '로드맵의 다음 단계와 실물 조사 경로'),
     (INTAKE, '다음 조사 항목'), (STATUS, '권장 작업 순서')],
    '출처: 개발 로드맵')

TITLE = '4주차 자율 지게차 개발'
TOTAL = 610


def build():
    assert len(slides) == 11, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'11장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-23. 사진은 입고한 실물을 찍은 것이고, 수치는 모두 컴퓨터로 만든 장면에서 '
              '측정한 값이다. 실제 장비의 성능은 별도 시험이 필요하다. 각 쪽의 발표자 노트에 그 화면을 '
              '만든 것(실물 사진 · Isaac Sim · 측정값 도식)을 표기하였다.', '']
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
            # 출처·쪽번호 줄은 본문 아래 한 줄을 통째로 먹으면서 화면에서는
            # 읽히지 않는다. 그 높이를 그림과 본문에 돌리고, 출처는 위의
            # 발표자 노트에 남긴다.
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
