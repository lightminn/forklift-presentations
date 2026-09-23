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
STATUS = 'docs/plans/2026-09-17-project-status-and-next-steps.md'
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
VIEWS = 'docs/validation/2026-09-23-isaac-multiview-recording.md'
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


# ----------------------------------------------------------------- visuals
# Hand-authored diagrams. Photographs keep their pixel coordinates (the marks
# sit in the image's own viewBox, so they move with the picture); schematics are
# labelled 개념도 and carry no dimensions except the ones stated in the text.


def annotated(src, width, height, alt, marks):
    """Photo with numbered markers placed in the image's own pixel space."""
    dots = ''.join(
        f'<g><circle cx="{x}" cy="{y}" r="58" fill="#fff" stroke="#0b3c8c" stroke-width="12"/>'
        f'<text x="{x}" y="{y + 26}" text-anchor="middle" font-size="74" font-weight="700" '
        f'fill="#0b3c8c" font-family="var(--uos-font)">{n}</text></g>'
        for n, x, y in marks)
    return (f'<figure class="annot" style="aspect-ratio:{width}/{height}">'
            f'<img src="assets/{src}" alt="{escape(alt, quote=True)}">'
            f'<svg viewBox="0 0 {width} {height}" aria-hidden="true">{dots}</svg></figure>')


def marklist(items):
    rows = ''.join(f'<li><span class="mk">{n}</span><span>{t}</span></li>' for n, t in items)
    return f'<ol class="marklist">{rows}</ol>'


CHASSIS_MARKS = [(1, 676, 1196), (2, 820, 1330), (3, 905, 1950), (4, 1040, 1700),
                 (5, 330, 1330)]
CHASSIS_ITEMS = [
    (1, '<b>마스트</b> — 포크를 올리는 수직 구조물'),
    (2, '<b>포크 캐리지</b> — 마스트를 따라 포크와 함께 오르내리는 판'),
    (3, '포크 2개'), (4, '흑색 플라스틱 팔레트 (동봉)'), (5, '바퀴 4개')]


# Signal path of the delivered chassis. Solid = observed on the part labels and
# the remote; dotted = the cockpit controls, whose wiring is not traced yet.
CONTROL_PATH = """
<svg class="diagram grow" viewBox="0 0 720 520" role="img" aria-label="무선 조종기의 신호를 좌석 아래 제어기가 받아 주행·조향·승강을 구동하는 현재 신호 경로. 배터리는 12V 표기">
<defs><marker id="ah4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#44505c"/></marker></defs>
<g font-family="var(--uos-font)" fill="#1b1f24">
<rect x="10" y="4" width="320" height="284" rx="12" fill="#fff" stroke="#8c959e" stroke-width="2"/>
<image href="assets/05_remote.jpg" x="22" y="14" width="296" height="164" preserveAspectRatio="xMidYMid slice"/>
<text x="170" y="210" text-anchor="middle" font-size="25" font-weight="700">무선 조종기 T07D-DGN</text>
<text x="170" y="240" text-anchor="middle" font-size="18" fill="#44505c">전진·후진 · 상승·하강</text>
<text x="170" y="266" text-anchor="middle" font-size="18" fill="#44505c">좌·우회전 · 속도 조절 · 제동</text>
<rect x="10" y="330" width="320" height="184" rx="12" fill="#eef3fa" stroke="#0b3c8c" stroke-width="3"/>
<image href="assets/04_controller_label.jpg" x="22" y="340" width="296" height="112" preserveAspectRatio="xMidYMid slice"/>
<text x="170" y="482" text-anchor="middle" font-size="25" font-weight="700">제어기 J6 D-CC-12V</text>
<text x="170" y="506" text-anchor="middle" font-size="18" fill="#44505c">좌석 아래</text>
<rect x="372" y="446" width="150" height="62" rx="12" fill="#fff" stroke="#8c959e" stroke-width="2"/>
<text x="447" y="486" text-anchor="middle" font-size="23" font-weight="700">배터리 12V</text>
<g font-size="30" font-weight="700" text-anchor="middle">
<rect x="540" y="60" width="170" height="80" rx="12" fill="#fff" stroke="#0b3c8c" stroke-width="3"/><text x="625" y="111">주행</text>
<rect x="540" y="190" width="170" height="80" rx="12" fill="#fff" stroke="#0b3c8c" stroke-width="3"/><text x="625" y="241">조향</text>
<rect x="540" y="320" width="170" height="80" rx="12" fill="#fff" stroke="#0b3c8c" stroke-width="3"/><text x="625" y="371">승강</text>
</g>
<g stroke="#44505c" stroke-width="4" fill="none">
<path d="M170,290 L170,326" stroke-dasharray="4 8" stroke-linecap="round" marker-end="url(#ah4)"/>
<path d="M332,360 C440,360 440,100 536,100" marker-end="url(#ah4)"/>
<path d="M332,380 C440,380 440,230 536,230" marker-end="url(#ah4)"/>
<path d="M332,400 C440,400 440,360 536,360" marker-end="url(#ah4)"/>
<path d="M370,477 L334,477" marker-end="url(#ah4)"/>
</g>
<text x="184" y="316" font-size="19" fill="#44505c" font-weight="700">무선</text>
</g></svg>
"""


# Side-view concept of a counterbalance forklift with the mounting cases.
# Not to scale except the ifm band, which uses the pallet's own 144 mm
# (0.28 px/mm) so that 23-36 cm sits where it would against that pallet.
MOUNT_CASES = """
<svg class="diagram grow" viewBox="0 0 800 430" role="img" aria-label="지게차 측면 개념도 위에 실제 사례의 팔레트 검출 카메라 장착 위치를 번호로 표시">
<g font-family="var(--uos-font)">
<line x1="20" y1="400" x2="790" y2="400" stroke="#8c959e" stroke-width="3"/>
<rect x="70" y="245" width="400" height="120" rx="22" fill="#d8dce1"/>
<rect x="250" y="208" width="70" height="40" rx="8" fill="#b9c0c8"/>
<g stroke="#5d6670" stroke-width="9" stroke-linecap="round"><line x1="140" y1="248" x2="160" y2="92"/><line x1="440" y1="248" x2="455" y2="92"/><line x1="130" y1="90" x2="470" y2="90"/></g>
<circle cx="150" cy="366" r="36" fill="#50585f"/><circle cx="400" cy="366" r="36" fill="#50585f"/>
<rect x="480" y="70" width="20" height="316" fill="#8a939c"/>
<rect x="500" y="180" width="16" height="200" fill="#6b747d"/>
<rect x="500" y="376" width="250" height="10" fill="#3d444b"/>
<g fill="#b98b54"><rect x="590" y="360" width="200" height="9"/><rect x="590" y="369" width="12" height="31"/><rect x="684" y="369" width="12" height="31"/><rect x="778" y="369" width="12" height="31"/></g>
<rect x="517" y="299" width="70" height="37" fill="#9cc3ec" opacity="0.55"/>
<g fill="#0b3c8c">
<rect x="520" y="311" width="18" height="13" rx="2"/><polygon points="538,317 586,304 586,330" opacity="0.35"/>
<rect x="517" y="255" width="18" height="13" rx="2"/><polygon points="535,261 600,256 596,300" opacity="0.35"/>
<rect x="517" y="186" width="18" height="13" rx="2"/><polygon points="535,192 610,150 610,250" opacity="0.25"/>
</g>
<g font-size="22" font-weight="700" fill="#fff" text-anchor="middle">
<circle cx="610" cy="318" r="16" fill="#d9822b"/><text x="610" y="325">①</text>
<circle cx="622" cy="266" r="16" fill="#d9822b"/><text x="622" y="273">②</text>
<circle cx="632" cy="176" r="16" fill="#d9822b"/><text x="632" y="183">③</text>
</g>
<text x="640" y="345" font-size="18" fill="#0b3c8c" font-weight="700">23~36 cm</text>
</g></svg>
"""

MOUNT_ITEMS = """<table class="comparison cases">
<tr><th></th><th>이름</th><th>장착</th><th>특징</th></tr>
<tr><td><span class="mk">①</span></td><td>ifm PDS</td><td>바닥 위 23~36 cm<br>정면 수직</td><td>팔레트 인식 전용 3D 카메라</td></tr>
<tr><td><span class="mk">②</span></td><td>Crown 특허</td><td>포크 캐리지</td><td>포크와 함께 승강<br>포크 끝이 화면 아래쪽</td></tr>
<tr><td><span class="mk">③</span></td><td>Toyota·AIST</td><td>백레스트</td><td>어안 카메라<br>포크와 함께 이동</td></tr>
<tr><td><span class="mk">④</span></td><td>ADAPT</td><td>카메라와<br>근거리 센서 분리</td><td>마지막 접근은<br>근거리 센서</td></tr></table>"""


# Concept of the blind-zone insertion: observe once while stopped, keep the
# pocket estimate fixed in the world, then drive in on the robot's own pose
# without looking again. insert-sync.js drives it from 11_insert_view.mp4 via
# data-sync (clip seconds: estimate shown, approach, insertion, end); the CSS
# keyframes in deck.css are the same timeline over the clip's 15.53 s loop.
INSERT_FLOW = """
<svg class="diagram grow" data-sync="0.99,2.49,9.83,14.32" viewBox="0 0 800 340" role="img" aria-label="위에서 본 개념도: 멈춰서 관측해 포켓 위치를 추정하고, 카메라를 다시 보지 않고 그 추정 위치로 이동해 포크를 넣는다">
<g font-family="var(--uos-font)">
<rect x="600" y="100" width="170" height="220" fill="#f1ede6" stroke="#b98b54" stroke-width="2"/>
<g fill="#e3d6c3"><rect x="600" y="140" width="170" height="44"/><rect x="600" y="236" width="170" height="44"/></g>
<g class="ins-est" fill="none" stroke="#d61fb4" stroke-width="5"><rect x="600" y="140" width="40" height="44"/><rect x="600" y="236" width="40" height="44"/></g>
<text class="ins-est" x="685" y="90" text-anchor="middle" font-size="21" fill="#b0128f" font-weight="700">저장한 포켓 위치</text>
<polygon class="ins-cone" points="150,210 600,70 600,350" fill="#2f74c0" opacity="0.2"/>
<g class="ins-move">
<rect x="30" y="130" width="100" height="160" rx="10" fill="#c9cfd6"/>
<rect x="130" y="130" width="16" height="160" fill="#6b747d"/>
<rect x="146" y="152" width="140" height="20" fill="#3d444b"/><rect x="146" y="248" width="140" height="20" fill="#3d444b"/>
<rect x="138" y="198" width="16" height="24" rx="3" fill="#0b3c8c"/>
<circle cx="80" cy="210" r="9" fill="none" stroke="#0b3c8c" stroke-width="3"/><line x1="66" y1="210" x2="94" y2="210" stroke="#0b3c8c" stroke-width="3"/><line x1="80" y1="196" x2="80" y2="224" stroke="#0b3c8c" stroke-width="3"/>
<text x="80" y="318" text-anchor="middle" font-size="20" fill="#0b3c8c" font-weight="700">차 위치</text>
</g>
</g></svg>"""


# Fork-tip error at the end of insertion in this run, split along the
# insertion axis (Codex cross-check 2026-09-23): lateral -1.34 (estimate)
# -0.78 (rear axle) -3.58 (yaw 2.77 mrad x 1.29 m rear axle to fork tip)
# = -5.70 mm; depth 7.54 mm short of the 360 mm target. Lateral scale
# 0-50 mm at 14 px/mm from x=230; depth scale 300-420 mm at 5.8 px/mm.
ERROR_BUDGET = """
<svg class="budget" viewBox="0 0 1180 160" role="img" aria-label="삽입이 끝났을 때: 포크 끝이 옆으로 빗나간 거리 5.7 mm로 구멍 벽까지 45 mm 안, 포크가 들어간 깊이 352 mm로 목표 360 mm보다 조금 덜 들어감">
<g font-family="var(--uos-font)">
<text x="0" y="26" font-size="21" font-weight="700" fill="#1b1f24">포크 끝이 포켓 중심에서 옆으로 빗나간 거리 <tspan fill="#0b3c8c">5.7 mm</tspan></text>
<rect x="0" y="38" width="700" height="28" fill="#f3f4f6"/>
<rect x="0" y="38" width="19" height="28" fill="#d61fb4"/>
<rect x="19" y="38" width="11" height="28" fill="#0b3c8c"/>
<rect x="30" y="38" width="50" height="28" fill="#2f74c0"/>
<line x1="630" y1="30" x2="630" y2="74" stroke="#c0392b" stroke-width="4"/>
<text x="640" y="58" font-size="19" fill="#c0392b" font-weight="700">포켓 벽까지 45 mm</text>
<text x="0" y="92" font-size="21" font-weight="700" fill="#1b1f24">포크가 팔레트에 들어간 깊이 <tspan fill="#0b3c8c">352 mm</tspan></text>
<rect x="0" y="104" width="1030" height="28" fill="#f3f4f6"/>
<rect x="0" y="104" width="857" height="28" fill="#0b3c8c"/>
<line x1="876" y1="98" x2="876" y2="134" stroke="#1d7a3a" stroke-width="4"/>
<line x1="988" y1="98" x2="988" y2="134" stroke="#c0392b" stroke-width="4"/>
<text x="876" y="93" text-anchor="middle" font-size="18" fill="#1d7a3a" font-weight="700">목표 360</text>
<text x="988" y="93" text-anchor="middle" font-size="18" fill="#c0392b" font-weight="700">최대 406</text>
<text x="1180" y="152" text-anchor="end" font-size="17" fill="#c0392b">최대 406 mm: 더 넣으면 포크 뿌리가 팔레트에 닿음</text>
</g></svg>"""


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '4주차\n자율 지게차 개발', 20, '',
    """이번 주에는 지게차 차체가 입고되어 구조 조사를 시작하였고, 3주차에 받은 카메라 장착에 관한 지적에 실제 지게차 사례로 답한다. 사진은 입고한 실물이고, 수치는 모두 컴퓨터로 만든 장면에서 잰 값이다.""",
    [(INTAKE, '차체 입고와 초기 구조 조사'), (IFM, '카메라 장착 사례')], '진행 보고')

# ----------------------------------------------------------------- 2
add('개발 진행 현황', '01  개발 진행 현황', 45, """
<h2 class="headline">다섯 단계의 현재 위치와 이번 주 작업</h2>
<div class="pipeline grow"><article class="pipeline-step done"><h3>① 팔레트 인식</h3><img class="step-thumb" src="assets/t1_detect.jpg" alt=""><p>깊이 영상에서<br>팔레트·포켓 검출</p><p class="state">구현</p></article><article class="pipeline-step done"><h3>② 좌표 변환</h3><img class="step-thumb" src="assets/t2_depth.jpg" alt=""><p>포켓 위치·방향을<br>로봇 기준으로 표시</p><p class="state">구현</p></article><article class="pipeline-step now"><h3>③ 경로 생성</h3><img class="step-thumb" src="assets/t3_path.jpg" alt=""><p>장애물을 피하며<br>팔레트에 접근</p><p class="state">시뮬레이션 연결</p></article><article class="pipeline-step now"><h3>④ 삽입·적재</h3><img class="step-thumb" src="assets/t4_insert.jpg" alt=""><p>포크를 넣고<br>들어 올림</p><p class="state">시뮬레이션 연결</p></article><article class="pipeline-step now"><h3>⑤ 이송·하역</h3><img class="step-thumb" src="assets/t5_transport.jpg" alt=""><p>목적지까지<br>운반·하역</p><p class="state">시뮬레이션 연결</p></article></div>
<div class="takeaway">실물: 차체 입고 · 전장과 조작 축 확인 · 카메라 장착 조건 조사</div>
""",
    """과제의 작업 절차는 팔레트 인식부터 이송·하역까지 다섯 단계이다. 3주차에는 1단계 인식과 2단계 좌표 변환을 구현하였다. 이후 3단계부터 5단계를 시뮬레이션 안에서 연결하여, 카메라가 추정한 팔레트 위치로 접근해 포크를 넣고 들어 올려 운반한 뒤 내려놓는 임무를 수행하였다. 아래 줄은 실물 작업이다. 차체가 입고되어 구성과 조작 경로를 확인하였고, 카메라 장착 조건을 조사하였다.""",
    [(BRIEF, '과제 원문 7쪽의 다섯 단계'), (STATUS, '현재 진행 상태'), (VIEWS, '카드 사진 — Isaac Sim 다중 시점 녹화')],
    '출처: 과제 설명자료 7쪽 · 카드 사진은 Isaac Sim')

# ----------------------------------------------------------------- 3
add('차체 입고', '02  차체 입고', 55, f"""
<h2 class="headline">지게차 차체 입고 · 플라스틱 팔레트 1장 동봉</h2>
<div class="split grow" style="grid-template-columns:0.72fr 1.28fr">
{annotated('01_chassis_and_pallet.jpg', 1300, 2076, '조립을 마친 지게차 차체와 함께 들어 있던 흑색 플라스틱 팔레트, 부위별 번호 표시', CHASSIS_MARKS)}
{marklist(CHASSIS_ITEMS)}
</div>
<div class="takeaway">다음 주 실측: 치수 · 무게 · 승강 범위 | 시험 팔레트: EPAL 6 · 축소 T11 유지</div>
""",
    """이번 주에 지게차 차체가 들어와 조립하였다. 바퀴는 네 개이고, 앞쪽에 포크를 올리는 수직 구조물인 마스트가 있다. 포크 두 개는 마스트를 따라 오르내리는 판인 포크 캐리지에 달려 있으며, 이 캐리지는 뒤에서 카메라 장착 후보로 다시 다룬다. 구성품에는 흑색 플라스틱 팔레트 한 장이 함께 들어 있었다. 시험용 팔레트는 앞서 정한 EPAL 6과 축소 T11을 그대로 쓰고, 동봉 팔레트는 치수를 잰 뒤 두 규격과 비교한다. 차체의 치수와 무게, 승강 범위는 다음 주에 실측한다.""",
    [(INTAKE, '입고 구성과 관찰 범위'), (ADR2, '시험용 팔레트 규격 결정')],
    '화면 생성: 실물 사진 2026-09-23')

# ----------------------------------------------------------------- 4
add('기존 전장과 조작 축', '03  기존 전장과 조작 축', 60, f"""
<h2 class="headline">주행 · 조향 · 승강 모두 무선 조종기 입력</h2>
<div class="split grow" style="grid-template-columns:0.9fr 1.1fr">
{figure('03_electronics_bay.jpg', '좌석 아래에 나란히 고정된 제어기와 12V 표기가 있는 배터리, 백색 커넥터로 연결된 하네스', '좌석 아래 — 왼쪽이 제어기, 오른쪽이 배터리', cls='')}
{CONTROL_PATH}
</div>
""",
    """좌석 아래에 제어기와 배터리가 나란히 고정되어 있고, 색으로 구분한 심선이 백색 커넥터로 연결된다. 제어기 라벨은 J6 D-CC-12V이고 배터리에도 12볼트 표기가 있다. 함께 들어 있는 무선 조종기 T07D-DGN에는 전진과 후진, 상승과 하강, 좌회전과 우회전, 속도 조절과 제동 버튼이 있다. 조종기의 무선 신호를 제어기가 받아 주행과 조향, 승강 세 축을 움직이는 구조이다. 다음 주에는 배선을 따라가 제어기의 신호 형식과 모터 정격을 확인한다.""",
    [(INTAKE, '제어기·조종기·배터리의 표기'), (MAP, '로드맵 H1 전장과 피드백 조사')],
    '화면 생성: 실물 사진 2026-09-23')

# ----------------------------------------------------------------- 5
add('카메라 장착 사례', '04  카메라 장착 사례', 65, f"""
<h2 class="headline">실제 지게차의 팔레트 인식 카메라 장착 위치</h2>
<div class="split grow" style="grid-template-columns:1.15fr 1fr">
{MOUNT_CASES}
{MOUNT_ITEMS}
</div>
<div class="takeaway">공통점: 포켓 높이 가까이 · 포크와 함께 움직이는 자리</div>
""",
    """3주차에 실제 지게차는 카메라를 어디에 다는지 확인하고 우리 차체에 맞추어 보라는 지적을 받았다. 그림은 지게차 옆모습에 사례별 위치를 표시한 것이다. 첫째, ifm의 팔레트 인식 전용 3차원 카메라 PDS는 바닥에서 23에서 36센티미터 높이에 정면을 수직으로 보도록 단다. 둘째, 지게차 제조사 Crown의 특허는 포크 캐리지에 카메라를 달아 포크와 함께 오르내리게 하고, 포크 끝이 화면 아래쪽에 보이게 한다. 셋째, 도요타와 일본 산업기술종합연구소의 자율 지게차는 포크 뒤 백레스트에 어안 카메라를 달아 포크와 함께 움직이게 했다. 넷째, 자율 지게차 연구 ADAPT는 멀리서는 카메라로 찾고 마지막 접근은 근거리 전용 센서에 맡긴다. 공통점은 포켓 높이 가까이, 포크와 함께 움직이는 자리에 단다는 것이다.""",
    [(IFM, 'ifm 팔레트 검출 시스템 통합 안내 — 지면 위 23~36 cm, 바닥·팔레트면에 수직'),
     (CROWN, 'Crown 특허 US9990535B2 — 포크 캐리지 장착, 포크를 시야 하단에'),
     (AIST, 'AIST·도요타 리치트럭 (Sensors 2026) — 백레스트 어안 장착, 카메라와 포크는 강체'),
     (ADAPT, 'ADAPT 자율 지게차 (arXiv 2503.14331) — 최종 접근은 근거리 전용 센서가 담당')],
    '출처: 제조사 안내 · 특허 · 논문')

# ----------------------------------------------------------------- 6
add('관측과 경로 계획', '05  관측과 경로 계획', 55, f"""
<h2 class="headline">깊이 영상 포켓 검출에서 경로 계획까지</h2>
{figure('12_observe_steps.mp4', '왼쪽은 지게차 카메라의 컬러·깊이 영상, 오른쪽은 탑뷰. 관측 지점에 멈춰 촬영하면 포켓이 자홍색으로 표시되고 곧이어 접근·운반 경로선이 나타난다', '', cls='grow')}
<div class="phase-flow"><b>① 관측 지점에 정지해 촬영</b><span class="arrow">→</span><b>② 깊이 영상에서 포켓 검출</b><span>(자홍색)</span><span class="arrow">→</span><b>③ 접근·운반 경로 계획</b><span>(파랑 · 노랑)</span></div>
""",
    """지게차가 관측 지점까지 가서 멈추고 사진을 찍는 장면이다. 왼쪽은 지게차에 달린 카메라의 컬러 영상과 깊이 영상이고, 오른쪽은 같은 순간을 위에서 내려다본 화면이다. 멈춰서 찍은 깊이 영상에서 팔레트 전면과 두 포켓을 찾으면 왼쪽에 자홍색 사각형이 나타난다. 이 위치를 로봇 기준 좌표로 바꾸어 목표로 삼고, 장애물을 피하는 경로를 계획한다. 오른쪽에 나타나는 파란 선이 팔레트로 가는 접근 경로, 노란 선이 팔레트를 든 뒤 목적지로 가는 운반 경로이다.""",
    [(VIEWS, '관측 캡처와 계획 경로 — Isaac Sim 다중 시점 녹화'), (STATUS, '관측·계획 단계의 구성')],
    '화면 생성: Isaac Sim 인식 카메라 · 탑뷰, 같은 실행의 같은 프레임')

# ----------------------------------------------------------------- 7
add('삽입 추정', '06  삽입 추정', 60, f"""
<h2 class="headline">한 번 찾은 포켓 위치를 저장해 끝까지 넣는 삽입</h2>
<div class="split grow" style="grid-template-columns:1.55fr 1fr">
{INSERT_FLOW}
{figure('11_insert_view.mp4', '지게차 카메라 화면에 저장한 포켓 위치를 매 순간 차 위치에 맞춰 옮겨 그린 영상. 팔레트가 화면 밖으로 나갈 때까지 자홍색 표시가 포켓에 맞게 따라간다', '', cls='')}
</div>
<div class="phase-flow steps3"><b class="ins-s1">① 멈춰서 보고 포켓 위치 저장</b><span class="arrow">→</span><b class="ins-s2">② 카메라 없이 차 위치만으로 이동</b><span class="arrow">→</span><b class="ins-s3">③ 목표 깊이까지 삽입</b></div>
""",
    """3주차에 가까워지면 카메라가 포켓을 볼 수 없다는 점을 확인하고, 마지막 관측을 이어 쓰는 방법을 다음 목표로 잡았다. 지금 방식은 멀리서 멈춰 한 번 관측한 포켓 위치를 작업장 좌표에 고정하고, 그 뒤로는 카메라를 다시 보지 않고 차 위치만으로 그 목표까지 경로를 따라가 포크를 넣는 것이다. 왼쪽 그림이 그 흐름이다. 오른쪽은 지게차 카메라 화면에 저장한 포켓 위치를 매 순간 차 위치에 맞춰 옮겨 그린 것으로, 팔레트가 화면 밖으로 나갈 때까지 자홍색 표시가 포켓에 맞게 따라간다. 차 위치는 지금은 시뮬레이터가 알려 준다. 결과와 오차는 다음 장에서 본다.""",
    [(VIEWS, '실행 20260923T0515Z_views2_seed2 — 삽입 끝 포크 끝 오차: 좌우 5.7 mm(추정 1.3 · 후륜축 0.8 · 방향 2.77 mrad × 1.29 m = 3.6), 깊이 7.5 mm 부족'),
     (ADR3, 'EPAL 6 포켓 벽까지 45 mm · 캐리지 한계 406 mm (잠정 차체 모델)'),
     (STATUS, '삽입 중 재관측 없음, 로봇 위치는 시뮬레이터 값')],
    '화면 생성: 움직이는 개념도 · Isaac Sim 인식 카메라 · 막대는 이 실행의 측정값, 45 mm·406 mm는 잠정 모델')

# ----------------------------------------------------------------- 7b
add('삽입 결과', '07  삽입 결과와 오차 원인', 60, f"""
<h2 class="headline">삽입이 끝난 순간의 포크 끝 오차와 그 원인</h2>
{ERROR_BUDGET}
<table class="comparison causes">
<tr><th>오차 항목</th><th>크기</th><th>원인</th></tr>
<tr><td><span class="sw" style="background:#d61fb4"></span>카메라가 잰 팔레트 위치</td><td>1.3 mm</td><td>깊이 영상의 점 간격 단위로 포켓 가장자리를 찾으며 생긴 차이</td></tr>
<tr><td><span class="sw" style="background:#0b3c8c"></span>차가 멈춘 자리</td><td>0.8 mm</td><td>계획한 경로를 따라가다 멈춘 자리가 옆으로 조금 벗어남</td></tr>
<tr><td><span class="sw" style="background:#2f74c0"></span>차가 비스듬히 선 각도</td><td>3.6 mm</td><td>차가 0.16° 비스듬히 멈춰, 1.3 m 앞 포크 끝에서는 옆으로 3.6 mm가 됨</td></tr>
<tr><td><span class="sw" style="background:#9aa3ad"></span>덜 들어간 깊이</td><td>7.5 mm</td><td>목표까지 8 mm 안에 들면 도착으로 보도록 설정해 두어, 감속하다 그 안에서 멈춤</td></tr></table>
<div class="takeaway">시뮬레이션 한 번의 결과 · 실물에서는 차가 자기 위치를 스스로 계산하며 생기는 오차가 더해짐</div>
""",
    """삽입이 끝난 순간 포크 끝의 오차와 그 원인이다. 포크 끝은 팔레트 구멍 중심에서 옆으로 5.7밀리미터 빗나갔다. 이 가운데 1.3밀리미터는 카메라가 팔레트 위치를 잰 차이로, 깊이 영상의 점 간격 단위로 포켓 가장자리를 찾으면서 생긴다. 0.8밀리미터는 차가 계획한 경로를 따라가며 멈춘 자리가 옆으로 조금 벗어난 것이다. 가장 큰 3.6밀리미터는 차가 0.16도쯤 비스듬히 선 채 멈추어, 1.3미터 앞에 있는 포크 끝이 옆으로 밀린 것이다. 포크와 포켓 벽 사이가 45밀리미터이므로 닿지는 않는다. 깊이는 목표보다 7.5밀리미터 덜 들어갔는데, 목표까지 8밀리미터 안에 들면 도착으로 보도록 설정해 두었고, 끝에서 감속하다 그 안에서 멈추었기 때문이다. 이것은 시뮬레이션 한 번의 결과이고, 차 위치를 시뮬레이터가 알려 주므로 그 오차가 빠져 있다. 실물에서는 차가 바퀴와 관성 센서로 자기 위치를 스스로 계산해야 하므로 그 오차가 더해진다.""",
    [(VIEWS, '실행 20260923T0515Z_views2_seed2 — 포크 끝 좌우 5.7 mm(추정 1.3 · 후륜축 0.8 · 방향 2.77 mrad × 1.29 m = 3.6), 깊이 7.5 mm 부족'),
     (ADR3, 'EPAL 6 구멍 벽까지 45 mm · 포크 뿌리 한계 406 mm (잠정 차체 모델)'),
     (STATUS, '삽입 도착 판정 8 mm · 로봇 위치는 시뮬레이터 값')],
    '화면 생성: 이 실행의 측정값 · 원인은 코드와 실행 기록으로 확인(Codex 교차검증)')

# ----------------------------------------------------------------- 8
add('운반 임무', '08  운반 임무', 65, f"""
<h2 class="headline">카메라 추정 위치를 목표로 관측부터 하역까지</h2>
<div class="split grow" style="grid-template-columns:1.9fr 1fr">
{figure('10_mission_seed17.mp4', '위에서 내려다본 임무 전체 영상. 왼쪽 위 작은 화면은 지게차 카메라, 오른쪽 위에 현재 단계 표시', '', cls='')}
<div class="stack" style="gap:14px">
<table class="comparison"><tr><th>입력</th><th>출처</th></tr>
<tr><td style="white-space:nowrap">팔레트 위치</td><td class="blue"><b>카메라 추정</b></td></tr>
<tr><td style="white-space:nowrap">로봇 위치</td><td>시뮬레이터</td></tr>
<tr><td style="white-space:nowrap">장애물</td><td>시뮬레이터</td></tr>
<tr><td>목적지</td><td>시뮬레이터</td></tr></table>
</div>
</div>
""",
    """임무 전체를 위에서 내려다본 영상을 2배속으로 보인다. 오른쪽 위 표시가 현재 단계이고, 왼쪽 위 작은 화면은 지게차 카메라가 보는 장면이다. 지게차는 관측 지점에서 팔레트를 찾은 뒤 계획한 경로를 따라 접근해 포크를 넣고 들어 올린다. 팔레트를 든 채 후진해 빠져나온 뒤 목적지로 운반해 초록 원 안에 내려놓고, 포크를 뺀 다음 출발 자리로 돌아간다. 오른쪽 표처럼 카메라가 추정하는 것은 팔레트 위치이고, 로봇 위치와 장애물, 목적지는 시뮬레이터 값을 쓴다. 이 부분은 실물 단계에서 2D LiDAR로 바꾼다.""",
    [(VIEWS, '임무 전체 영상 — ws1 `20260923_camera_inset_v2/seed_17`, 단계 표시는 그 실행의 result.json 전환 시각'), (STATUS, '삽입 깊이 360 mm와 사용 입력의 구분')],
    '화면 생성: Isaac Sim 조감 녹화(카메라 인셋 포함) · 2배속 · 단계는 실행 기록 기준')

# ----------------------------------------------------------------- 9
add('향후 추진 계획', '09  향후 추진 계획', 70, """
<h2 class="headline">실 차체 기반 하드웨어 구축</h2>
<div class="roadmap grow"><article class="now"><h3>차체 파라미터 실측</h3><p>치수·무게·축간 거리<br>포크 치수·승강 범위<br>최소 회전 반경</p></article><article class="now"><h3>제어 회로 분석</h3><p>배선·제어기 신호 형식<br>모터 정격·구동 방식<br>속도·조향각·포크 높이 신호</p></article><article class="wait"><h3>자율주행용 개조</h3><p>컴퓨터 명령 입력 경로<br>주행·조향·승강 상태 피드백<br>전원·배선 정리</p></article><article class="wait"><h3>센서 부착</h3><p>RGB-D 카메라 장착점·브래킷<br>2D LiDAR 장착 위치·높이<br>센서 좌표 변환 보정</p></article></div>
<div class="takeaway">실측한 차체와 센서 위치를 시뮬레이션 모델과 좌표 변환에 반영</div>
""",
    """이제 실제 차체가 들어왔으므로 다음 작업은 하드웨어에 집중한다. 첫째, 차체의 치수와 무게, 축간 거리, 포크 치수와 승강 범위, 최소 회전 반경을 잰다. 지금 시뮬레이션은 상품 사진으로 만든 잠정 모델을 쓰고 있어 이 값들로 바꾸어야 한다. 둘째, 제어 회로를 분석한다. 배선을 따라가 제어기의 신호 형식과 모터의 정격과 구동 방식을 확인하고, 속도와 조향각, 포크 높이를 알려 주는 신호가 있는지 찾는다. 셋째, 그 결과를 바탕으로 컴퓨터가 명령을 넣고 주행과 조향, 승강 상태를 읽을 수 있도록 자율주행에 맞게 개조한다. 넷째, 실제 센서를 붙인다. RGB-D 카메라는 포크 캐리지의 장착점과 브래킷을 정하고, 2D LiDAR는 장착 위치와 높이를 정한 뒤 두 센서의 좌표 변환을 보정한다. 실측한 차체와 센서 위치는 시뮬레이션 모델과 좌표 변환에 다시 반영한다.""",
    [(MAP, '로드맵 H0 실측 · H1 전장과 피드백 조사'),
     (INTAKE, '다음 조사 항목'), (HW, '센서 선정 — RGB-D 카메라 D435i, 2D LiDAR')],
    '출처: 개발 로드맵')

TITLE = '4주차 자율 지게차 개발'
TOTAL = 555


def build():
    assert len(slides) == 10, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'10장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
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
<script src="vendor/react.production.min.js"></script><script src="vendor/react-dom.production.min.js"></script><script src="./support.js"></script><script src="insert-sync.js" defer></script></head>
<body><x-dc><helmet><meta name="viewport" content="width=device-width, initial-scale=1"><title>{TITLE}</title>
<link rel="stylesheet" href="vendor/uos-slide-template/fonts/fonts.css"><link rel="stylesheet" href="vendor/uos-slide-template/_ds_bundle.css"><link rel="stylesheet" href="vendor/uos-slide-template/styles.css"><link rel="stylesheet" href="deck.css"><script src="vendor/uos-slide-template/_ds_bundle.js"></script></helmet>
<x-import component-from-global-scope="deck-stage" from="./deck-stage.js" width="1280" height="720" hint-size="100%,100%">
''' + '\n\n'.join(sections) + '\n</x-import></x-dc></body></html>\n'
    for name in ('deck.css', 'insert-sync.js'):
        revision = sha256((ROOT/name).read_bytes()).hexdigest()[:12]
        html = html.replace(f'"{name}"', f'"{name}?v={revision}"')
    (ROOT/'index.html').write_text(html, encoding='utf-8')
    (ROOT/'SCRIPT.md').write_text('\n'.join(script), encoding='utf-8')
    (ROOT/'slide-metadata.json').write_text(
        json.dumps([{k: v for k, v in s.items() if k != 'body'} for s in slides],
                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(slides)} slides; timing {elapsed}s; '
          f'Korean script {sum(len(s["notes"]) for s in slides)} characters.')


if __name__ == '__main__':
    build()
