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
    """이번 주에는 지게차 차체가 입고되어 조립하고 구조를 조사하였다. 시뮬레이션에서는 팔레트 인식에 쓰는 카메라 설정값의 기준이 어긋난 것을 찾아 고쳤다. 실물 제어 연결과 반복 검증은 다음 단계이다. 사진은 실물이고, 수치는 모두 컴퓨터로 만든 장면에서 잰 값이다.""",
    [(INTAKE, '차체 입고와 초기 구조 조사'), (G1, '카메라 교정 관문 실측 기록')], '진행 보고')

# ----------------------------------------------------------------- 2
add('개발 진행 현황', '01  개발 진행 현황', 45, """
<h2 class="headline">다섯 단계의 현재 위치와 이번 주 작업</h2>
<div class="pipeline grow"><article class="pipeline-step done"><h3>① 포켓 인식</h3><p>깊이 영상에서<br>팔레트·포켓 검출</p><p class="state">평가 1회<br>재평가 예정</p></article><article class="pipeline-step done"><h3>② 좌표 산출</h3><p>포켓 위치·방향을<br>로봇 기준으로 표시</p><p class="state">구현 완료</p></article><article class="pipeline-step now"><h3>③ 경로 생성</h3><p>장애물을 피하며<br>팔레트에 접근</p><p class="state">시뮬레이션 연결</p></article><article class="pipeline-step now"><h3>④ 삽입·적재</h3><p>포크를 넣고<br>들어 올림</p><p class="state">시뮬레이션 연결<br>근접 추적 미구현</p></article><article class="pipeline-step now"><h3>⑤ 이송·하역</h3><p>목적지까지<br>운반·하역</p><p class="state">시뮬레이션 연결</p></article></div>
<div class="takeaway">이번 주: 차체 입고·구조 조사 | 시뮬레이션 인식 입력의 기준 오류 수정</div>
""",
    """과제의 작업 절차는 포켓 인식부터 운반·하역까지 다섯 단계이다. 3주차에는 1단계 포켓 인식과 2단계 좌표 산출까지 구현하였다고 보고하였다. 그 뒤 3단계부터 5단계까지를 시뮬레이션 안에서 이어 붙여, 카메라가 추정한 팔레트 위치를 목표로 접근하고 포크를 넣어 들어 올린 뒤 운반하고 내려놓는 동작을 한 사례에서 확인하였다. 이번 주에는 차체가 입고되어 조립과 구조 조사를 시작하였고, 시뮬레이션 인식이 쓰는 카메라 설정값의 기준 오류를 찾아 고쳤다. 무엇을 추정치로 쓰고 무엇을 정답으로 쓰는지는 뒤에서 따로 밝힌다.""",
    [(BRIEF, '과제 원문 7쪽의 다섯 단계'), (STATUS, '현재 진행 상태와 사용 입력의 구분')],
    '출처: 과제 설명자료 7쪽')

# ----------------------------------------------------------------- 3
add('차체 입고와 구조 확인', '02  차체 입고와 구조 확인', 55, f"""
<h2 class="headline">승용형 차체 입고 · 플라스틱 팔레트 1장 동봉</h2>
<div class="split grow" style="grid-template-columns:0.78fr 1.22fr">
{figure('01_chassis_and_pallet.jpg', '조립을 마친 지게차 차체와 함께 들어 있던 흑색 플라스틱 팔레트', '실물 사진 2026-09-23', cls='')}
<table class="comparison"><tr><th style="width:46%">눈으로 확인한 것</th><th>아직 재지 않은 것</th></tr>
<tr><td style="width:46%">운전석 보호 지붕 · 좌석 · 운전대<br>바퀴 4개<br>마스트와 포크 2개<br>전면 <b>DLS</b> 각인<br><b>플라스틱 팔레트 1장 동봉</b></td>
<td>전체 길이 · 폭 · 높이<br>축간 거리 · 포크 치수 · 승강 범위<br>무게 · 적재 한도 · 최소 회전 반경<br>구동축과 조향축의 배정<br>동봉 팔레트의 치수</td></tr></table>
</div>
<div class="takeaway">확인: 눈으로 본 구성 | 미측정: 치수 · 무게 · 회전 반경 | 동봉 팔레트는 기존 규격 결정을 대신하지 않음</div>
""",
    """이번 주에 지게차 차체가 들어와 조립하였다. 운전석 위 보호 지붕과 좌석, 운전대를 갖춘 승용형이고 바퀴는 네 개이다. 포크를 올리는 수직 구조물인 마스트와 포크 두 개가 달려 있다. 전면에는 DLS 라는 각인이 있는데, 우리가 상품 사진으로 만들어 둔 잠정 차체 모델과 같은 이름이다. 다만 같은 제품인지는 확인하지 않았고 그 모델의 치수는 여전히 카탈로그 값이다. 예상하지 못한 구성품으로 흑색 플라스틱 팔레트 한 장이 함께 들어 있었다. 이번 조사는 눈으로 보고 부품 표기를 읽은 것까지이고, 자를 대어 잰 치수는 하나도 없다. 오른쪽 표의 오른쪽 칸이 아직 재지 않은 항목이다. 동봉 팔레트도 재기 전이므로 앞서 정한 시험용 팔레트 규격을 대신하지 않는다.""",
    [(INTAKE, '입고 구성과 확인·미확인 항목'), (HW, '하드웨어 확정 상태'),
     (ADR2, '시험용 팔레트 규격 결정')], '화면 생성: 실물 사진 2026-09-23')

# ----------------------------------------------------------------- 4
add('기존 전장과 제어 경로', '03  기존 전장과 제어 경로', 60, f"""
<h2 class="headline">주행 · 조향 · 승강 모두 무선 조종기 입력</h2>
<div class="split grow" style="grid-template-columns:1.08fr 1fr">
{figure('03_electronics_bay.jpg', '좌석 아래에 나란히 고정된 제어기와 12V 표기가 있는 배터리, 백색 커넥터로 연결된 하네스', '좌석 아래 — 왼쪽이 제어기, 오른쪽이 배터리 · 실물 사진 2026-09-23', cls='')}
<div class="stack">
{figure('04_controller_label.jpg', '제어기 라벨을 확대한 사진 — J6, D-CC-12V, 3F81E C0054, ZHT BSJ TianJin5.0', '제어기 라벨', cls='')}
{figure('05_remote.jpg', '무선 조종기 T07D-DGN 의 전진·후진·상승·하강·좌회전·우회전 버튼', '무선 조종기', cls='')}
</div>
</div>
<div class="takeaway">확인: 부품 표기 · 배치 | 미확인: 핀 배치 · 통신 방식 · 모터 정격 · 상태를 읽을 경로</div>
""",
    """차체에 원래 들어 있는 전장을 확인하였다. 좌석 아래 공간에 제어기와 배터리가 나란히 붙어 있고, 색으로 구분한 심선 여러 가닥이 백색 커넥터로 연결된다. 제어기 라벨은 J6 D-CC-12V 이고 배터리에도 12볼트 표기가 있다. 함께 들어 있는 무선 조종기에서 주행과 승강에 관계된 버튼은 전진과 후진, 상승과 하강, 좌회전과 우회전, 그리고 속도 조절과 제동이다. 즉 주행과 조향과 승강 세 가지가 모두 무선 조종기의 입력으로 움직인다. 이번에 한 것은 표기를 읽고 배치를 본 것까지이다. 통전 시험이나 분해 계측은 하지 않았으므로 제어기의 핀 배치와 통신 방식, 모터가 견디는 전압과 전류, 그리고 속도나 조향각이나 포크 높이를 밖에서 읽을 경로가 있는지는 확인하지 못하였다.""",
    [(INTAKE, '제어기·조종기·배터리의 표기와 확인 범위')], '화면 생성: 실물 사진 2026-09-23')

# ----------------------------------------------------------------- 5
add('자율 제어에 필요한 정보', '04  자율 제어에 필요한 정보', 55, """
<h2 class="headline">넣어야 하는 명령 3가지 · 읽어야 하는 상태 3가지</h2>
<table class="comparison grow"><tr><th>축</th><th>넣어야 하는 명령</th><th>읽어야 하는 상태</th><th>현재</th></tr>
<tr><td>주행</td><td>전진·후진 속도</td><td>실제 속도</td><td>경로 미확인</td></tr>
<tr><td>조향</td><td>조향각</td><td>실제 조향각</td><td>경로 미확인</td></tr>
<tr><td>승강</td><td>포크 상승·하강</td><td>포크 높이</td><td>경로 미확인</td></tr></table>
<div class="choice" style="grid-template-columns:repeat(3,1fr)">
<div><b>후보 ① 제어기 교체</b><span>기존 제어기를 떼고 우리 구동 회로를 붙인다</span><i>모터 정격을 먼저 확인해야 한다</i></div>
<div><b>후보 ② 무선 신호 자리 입력</b><span>조종기가 신호를 넣는 자리에 우리 신호를 넣는다</span><i>제어기가 받는 신호 형식을 알아야 한다</i></div>
<div><b>후보 ③ 기존 조작부 활용</b><span>운전석의 유선 조작 경로를 그대로 쓴다</span><i>배선 종단을 따라가야 한다</i></div>
</div>
<div class="takeaway">명령 3 · 상태 3 중 경로가 확인된 것 0 | 셋은 조사 후보이지 비교표가 아니다</div>
""",
    """자율 주행을 하려면 컴퓨터가 명령을 넣고 그 결과를 읽어야 한다. 넣을 것이 셋, 읽을 것이 셋인데 지금까지 확인한 범위에서는 여섯 가지 모두 경로가 확인되지 않았다. 특히 읽는 값이 없으면 로봇이 얼마나 움직였는지 계산할 수 없고, 지도 위에서 자기 위치를 갱신할 수 없다. 조사할 방향은 앞 장에서 좁혀진다. 무선 조종기가 세 축을 모두 제어하고 있으므로, 그 신호를 우리가 대신 넣거나, 제어기를 통째로 바꾸거나, 운전석의 유선 조작 경로를 그대로 쓰는 세 갈래가 나온다. 어느 쪽이 가능한지는 배선을 따라가고 모터가 견디는 전압과 전류를 확인해야 알 수 있으므로, 지금은 비교표가 아니라 조사 후보이다. 다음 주에 이 확인을 진행한다.""",
    [(INTAKE, '미확인 항목과 다음 조사 항목'), (MAP, '로드맵 H1 전장과 피드백 조사')],
    '조사 후보 · 확정된 설계가 아니다')

# ----------------------------------------------------------------- 6
add('카메라 장착 조건', '05  카메라 장착 조건', 70, f"""
<h2 class="headline">자동 검출용은 포켓 높이에 낮게 · 축척으로는 정할 수 없음</h2>
<div class="split grow" style="grid-template-columns:0.88fr 1.12fr">
<table class="comparison wide-key"><tr><th>장착 위치</th><th>실제 사례에서 확인한 것</th></tr>
<tr><td>차체 전면 하부</td><td>한 제조사는 <b>지면 위 23~36 cm</b> · 바닥과 팔레트면에 수직으로 규정한다. 카메라 앞을 가리지 않아야 한다</td></tr>
<tr><td>포크 캐리지</td><td>포크와 함께 움직여 포켓을 끝까지 본다. 대신 차체 기준 좌표가 고정되지 않는다</td></tr>
<tr><td>후방 카메라</td><td>포크 안쪽 카메라와 함께 <b>운전자 시야 보조용이고 포켓 검출용이 아니다</b></td></tr></table>
{figure('09_d435i_limits.png', '해상도별 최소 측정 거리와 권장 측정 범위, 그리고 팔레트 전면 800밀리미터가 가로 화각에 들어오는 최소 거리', '', cls='')}
</div>
<div class="takeaway">지면 위 23~36 cm 규정 · 최소 측정 거리 280 mm · 전면 800 mm 가 화각에 들려면 448 mm</div>
""",
    """3주차 발표에서 실제 지게차의 RGB-D 카메라 장착을 확인하고 우리 차체에 맞추어 보라는 지적을 받았다. 먼저 구분할 것이 있다. 후진 카메라나 포크 안쪽 카메라는 운전자가 보라고 단 것이고, 포켓을 찾는 카메라는 컴퓨터가 쓰는 것이다. 둘의 장착 방식을 섞으면 안 된다. 자동 검출용은 낮게 단다. 한 제조사는 지면 위 23에서 36센티미터 사이, 바닥과 팔레트 면에 수직으로 규정한다. 포크가 달려 오르내리는 판인 포크 캐리지에 다는 방식도 쓰이는데, 포켓을 끝까지 보는 대신 포크가 오르내릴 때마다 차체 기준 좌표가 달라진다. 다만 실제 지게차의 높이에 차체 축척을 곱해서는 정할 수 없다. 오른쪽이 그 이유이다. 우리 카메라는 가장 높은 해상도에서 28센티미터보다 가까우면 깊이를 내지 못하고, 팔레트 전면 800밀리미터가 가로 화각에 들어오려면 448밀리미터 이상 떨어져야 한다. 이 값들은 차체를 줄인다고 함께 줄지 않는다. 그래서 장착점의 좌표와 기울기, 포크 끝과 포켓의 상대 위치, 그 자리가 고정된 마스트인지 캐리지인지를 직접 재어 정한다.""",
    [(IFM, 'ifm 팔레트 검출 시스템 통합 안내 — 지면 위 23~36 cm, 바닥·팔레트면에 수직'),
     (CROWN, 'Crown 특허 US9990535B2 — 포크 캐리지 장착, 포크를 시야 하단에'),
     (AIST, 'AIST·도요타 리치트럭 (Sensors 2026) — 백레스트 어안 장착, 카메라와 포크는 강체'),
     (ADAPT, 'ADAPT 자율 지게차 (arXiv 2503.14331) — 최종 접근은 근거리 전용 센서가 담당'),
     (D435I, 'Intel RealSense D435i 공식 사양 — 깊이 화각 87° × 58°, 권장 범위 0.3~3 m'),
     (RSTUNE, 'RealSense 튜닝 문서 — 해상도별 최소 측정 거리, 깊이 오차는 거리의 제곱에 비례'),
     (INTAKE, '카메라 장착을 위해 먼저 재야 할 항목'),
     (MAP, '로드맵 H0 센서 배치 검토 — 승강부 장착 시 좌표 변환 갱신')],
    '화면 생성: 공식 사양에서 그린 도식 · 448 mm 는 직접 계산')

# ----------------------------------------------------------------- 7
add('현재 실행이 쓰는 입력', '06  현재 실행이 쓰는 입력', 55, """
<h2 class="headline">카메라 추정으로 쓰는 값은 팔레트 위치 하나</h2>
<table class="comparison grow"><tr><th style="width:42%">계획에 들어가는 값</th><th>어디서 오는가</th></tr>
<tr><td style="width:42%">집으러 갈 <b>팔레트의 위치와 방향</b></td><td class="blue"><b>카메라 추정</b> — 깊이 영상에서 포켓을 찾아 계산한다</td></tr>
<tr><td>로봇 자신의 위치와 방향</td><td>시뮬레이터 정답</td></tr>
<tr><td>주변 장애물 지도</td><td>시뮬레이터 정답 — 2D LiDAR 지도 작성·위치 추정은 미연결</td></tr>
<tr><td>내려놓을 목적지</td><td>시뮬레이터 정답</td></tr>
<tr><td>실행 중 중단을 판정하는 검사</td><td>시뮬레이터 정답</td></tr></table>
<div class="takeaway">추정 1 · 정답 4 | 검출 실패 시 다음 관측 지점으로 재관측, 후보가 소진되면 중단</div>
""",
    """다음 두 장을 보기 전에, 지금 시뮬레이션이 무엇을 입력으로 쓰는지 밝힌다. 카메라가 추정한 값을 쓰는 것은 집으러 갈 팔레트의 위치와 방향 하나이다. 로봇 자신의 위치와 방향, 주변 장애물 지도, 내려놓을 목적지, 그리고 실행 중에 멈출지를 판정하는 검사는 모두 시뮬레이터가 알려주는 정답을 쓴다. 2D LiDAR 로 지도를 만들고 위치를 추정해 이 정답을 대체하는 일은 아직 연결하지 않았다. 검출에 실패했을 때 정답 위치로 되돌아가는 예외 경로는 두지 않았고, 대신 다음 관측 지점으로 옮겨 다시 본다. 후보가 모두 떨어지면 중단한다. 따라서 이어지는 두 장의 결과는 인식으로 목표를 정했다는 뜻이지, 센서만으로 도는 자율 주행이라는 뜻이 아니다.""",
    [(STATUS, '현재 운반 코드가 사용하는 입력의 구분'),
     (HOOK, '인식 연결 실측 기록')], '범위 구분')

# ----------------------------------------------------------------- 8
add('카메라 기준값 오류', '07  카메라 기준값 오류', 70, f"""
<h2 class="headline">반 화소 기준 차이가 만든 높이 편향 2.996 mm</h2>
{figure('07_half_pixel.png', '왼쪽은 정수 인덱스와 반정수 화소 중심의 0.5화소 차이, 오른쪽은 그 때문에 거리에 비례해 커지는 높이 편향', 'Isaac 교정 장면의 측정값으로 그린 도식')}
<div class="swap">
<div><b>높이 편향</b><span>+2.996 <i>→</i> +0.0002 mm</span></div>
<div><b>거리 구간 검사</b><span>0/285 <i>→</i> 285/285</span></div>
<div><b>성공 5건 재계산</b><span>2.58 <i>→</i> 2.53 mm</span></div>
</div>
<div class="takeaway">이 수정이 검출률이나 위치 오차를 개선한다는 증거는 없다 — 세 번째 칸이 그 확인이다</div>
""",
    """임무를 다시 돌리기 전에 시뮬레이션 안의 카메라가 사양대로 붙어 있는지 먼저 재기로 하였다. 그 과정에서 한 방향으로 일정하게 생기는 계통 오류를 찾았다. 깊이 영상에서 삼차원 좌표를 복원하려면 영상 중심의 위치가 필요하다. 화소는 영상을 이루는 한 칸인데, 시뮬레이터는 그 칸의 한가운데를 기준으로 이 값을 주고 우리 검출기는 칸의 번호를 기준으로 쓰고 있었다. 두 기준이 반 화소 다르다. 왼쪽 그림이 그 차이이고, 오른쪽처럼 복원한 높이를 거리에 비례해 밀어 올린다. 수정 전 편향의 평균은 2.996밀리미터, 수정 후에는 0.0002밀리미터이다. 이 오류가 오래 보이지 않은 것은 검출기가 포켓 높이를 팔레트 규격에서 가져와 덮어쓰기 때문이다. 다만 이 수정이 검출률이나 위치 오차를 개선한다는 증거는 없다. 기존 성공 사례 다섯 건을 두 기준으로 다시 계산하면 평균 위치 오차가 2.58밀리미터에서 2.53밀리미터로 거의 그대로였다.""",
    [(G1, '반 화소 기준 차이와 수정 — 높이 편향 2.996 → 0.0002 mm, 게이트 0/285 → 285/285'),
     (G1, '이 편향이 설명하지 않는 것 — 성공 5건 재계산 2.58 → 2.53 mm')],
    '화면 생성: 측정값 도식 · 왼쪽은 기준 모식도')

# ----------------------------------------------------------------- 9
add('임무 한 사례', '08  임무 한 사례', 75, f"""
<h2 class="headline">카메라 추정 위치를 목표로 관측부터 하역까지</h2>
{figure('08_mission_seed2.mp4', '위에서 내려다본 시점에서 지게차가 관측·접근·삽입·운반·하역을 수행하는 영상', 'Isaac Sim 시뮬레이션 · 3배속 · 임무 시간 75.4초 · 초록 원이 내려놓을 목적지')}
<div class="swap">
<div><b>임무 시간</b><span>75.4초</span></div>
<div><b>삽입 깊이</b><span>360 mm</span></div>
<div><b>삽입 종점 오차</b><span>7.65 mm</span></div>
</div>
<div class="takeaway">임무 75.4초 · 삽입 360 mm · 종점 오차 7.65 mm | 한 사례이고 성공률은 다음 장</div>
""",
    """영상은 카메라가 추정한 팔레트 위치를 목표로 삼아 임무 전체를 수행한 한 사례이다. Isaac Sim 시뮬레이션이고, 위에서 내려다본 시점이며 초록색 원이 내려놓을 목적지이다. 시뮬레이션에서 75.4초 걸린 주행을 3배속으로 돌린 것이다. 관측 지점으로 이동해 정지한 상태에서 촬영하고, 검출한 위치로 경로를 만들고, 접근하여 포크를 넣고, 들어 올려 운반한 뒤 내려놓고 포크를 뺀다. 삽입 깊이는 팔레트 깊이의 0.6배와 포크 캐리지의 한계에서 계산한 360밀리미터인데, 이것은 운영 목표이고 실물에서 확인한 안전 여유가 아니다. 삽입 구간의 종점 오차는 7.65밀리미터였고, 이 값은 계획한 종점과 실제 도달 지점의 차이이지 포켓을 기준으로 잰 정밀도가 아니다. 삽입하고 빼는 동안에는 검사 시점마다 포크와 팔레트가 2밀리미터 넘게 떨어져 있는지 확인하고, 그보다 가까워지면 즉시 멈춘다. 다만 이것은 검사 시점의 확인이며 접촉하는 힘을 재거나 검사 사이를 증명한 것은 아니다.""",
    [(STATUS, '임무 실행 단계별 실측 — 75.4초, 종점 오차 7.65 mm / 2.83 mrad'),
     (HOOK, '인식 연결 실행의 기록과 안전 검사 범위')],
    '화면 생성: Isaac Sim · 전 구간을 3배속으로')

# ----------------------------------------------------------------- 10
add('증명되지 않은 항목', '09  증명되지 않은 항목', 45, """
<h2 class="headline">이번 주 결과가 증명하지 않는 것</h2>
<table class="comparison grow"><tr><th>항목</th><th>현재 상태</th></tr>
<tr><td>성공률</td><td>인식 입력이 바뀌어 이전 성적은 다시 재야 하고, 아직 돌리지 않았다</td></tr>
<tr><td>로봇 위치·지도</td><td>시뮬레이터 정답을 쓴다. 2D LiDAR 지도 작성과 위치 추정은 미연결</td></tr>
<tr><td>근접 포켓 추적</td><td>없다. 접근을 시작할 때 추정한 위치로 끝까지 간다</td></tr>
<tr><td>실물</td><td>치수·정격을 하나도 재지 않았고 실제 센서도 붙이지 않았다</td></tr></table>
<div class="takeaway">이번 주 수치는 전부 컴퓨터로 만든 장면의 값 | 실물 측정값은 0개</div>
""",
    """이번 주 결과가 무엇을 증명하지 않는지 정리한다. 첫째, 여러 조건에서의 성공률이 없다. 앞 장의 기준 수정이 검출에 들어가는 입력을 바꾸었으므로 이전에 낸 성적은 다시 재야 하고 아직 돌리지 않았다. 둘째, 삽입하는 동안 포켓을 다시 보며 위치를 갱신하는 기능이 없다. 접근을 시작할 때 추정한 위치로 끝까지 간다. 셋째, 실물은 아직 치수도 정격도 재지 않았고 실제 센서를 붙이지도 않았다. 표의 둘째 줄처럼 로봇 위치와 지도도 여전히 정답을 쓴다.""",
    [(STATUS, '지금 되는 것과 안 되는 것'), (G1, '수정으로 이전 성적이 무효가 된 범위')],
    '범위 구분')

# ----------------------------------------------------------------- 11
add('향후 추진 계획', '10  향후 추진 계획', 60, """
<h2 class="headline">실물 조사와 시뮬레이션 재검증을 함께 진행</h2>
<div class="roadmap grow"><article class="now"><h3>실물 조사</h3><p>치수·무게 실측<br>배선 종단과 정격 확인<br>상태를 읽을 경로 확인<br>카메라 장착점 실측</p><p class="state">다음 주</p></article><article class="now"><h3>시뮬레이션 재검증</h3><p>여러 조건의 임무 재실행<br>성공률과 실패 원인 정리</p><p class="state">다음 주</p></article><article class="wait"><h3>근접 포켓 추적</h3><p>삽입 중 위치 갱신<br>관측이 끊기면 정지</p><p class="state">그다음</p></article><article class="wait"><h3>팔레트와 나머지 피드백</h3><p>동봉 팔레트 실측·대조<br>표준 운용 방법 조사<br>팔레트 제작 방법 조사</p><p class="state">그다음</p></article></div>
<div class="takeaway">실물 제어 연결 전까지 시뮬레이션 결과는 실물 성능이 아님</div>
""",
    """다음 작업은 네 갈래이다. 첫째는 실물 조사를 이어가는 것이다. 차체의 치수와 무게를 재고, 배선을 따라가 모터와 배터리의 정격을 확인하며, 속도와 조향각과 포크 높이를 밖에서 읽을 수 있는지 확인한다. 카메라를 달 자리의 좌표와 기울기도 이때 잰다. 둘째는 시뮬레이션에서 여러 조건의 임무를 다시 돌려 성공률과 실패 원인을 정리하는 것이다. 셋째는 삽입하는 동안 포켓을 계속 보며 위치를 갱신하고, 관측이 끊기면 멈추는 기능이다. 넷째는 동봉된 팔레트를 재어 앞서 정한 시험용 규격과 비교하는 것이다. 3주차에 받은 나머지 두 가지 지적, 지게차의 표준 운용 방법과 시험용 팔레트를 만드는 방법은 이 실측과 함께 조사하여 보고한다.""",
    [(MAP, '로드맵의 다음 단계와 실물 조사 경로'),
     (INTAKE, '다음 조사 항목'), (STATUS, '권장 작업 순서')], '출처: 개발 로드맵')


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
