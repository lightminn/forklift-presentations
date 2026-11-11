"""Build the week 11-1 UOS web deck (RoboWorld 2026 visit report) and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

A part deck of week 11: what the team saw at RoboWorld 2026 (KINTEX, 2026-11-04..07; visited 11-06 and 11-07)
and how it compares with this forklift. Booths: Multiway Robotics (unmanned forklift lineup), H3R (6-phase drone
motor), CubeMars (AK actuators over CAN) and FASTECH Ezi-Pos (servo drives with maxon motors). Photos are the
team's own (prepare_photos.py crops them and drops EXIF); booth answers come from the team's interview notes
(robot repository docs/roboworld/, local only). Screen text and narration were written directly (project memory
script-md-no-agy).
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
slides = []

NOTES = '팀 인터뷰 메모 (로봇 저장소 docs/roboworld/인터뷰 생각나는대로.txt, 로컬 전용)'
PHOTO = '팀 촬영 사진 (로봇 저장소 docs/roboworld/, Galaxy, 2026-11-06 · 07 촬영 — prepare_photos.py 로 자르고 EXIF 제거)'
EVENT = 'inews24 「개막 22일 앞둔 \'2026 로보월드\'」 https://inews24.com/view/2014979 · kidd.co.kr 보도 (일정 11-04–07, 킨텍스 1전시장 3–5홀, 402개 기업 1,198개 부스)'
HW = '로봇 저장소 sim/models/dls08_measured/README.md (승강 범위 0.28 m 실측), week-07-1/build_deck.py (최대 적재 하중 10 kg, 카탈로그)'
WHEEL = 'week-09/build_deck.py 06 장 · assets/h05_mounted.jpg (바퀴 모터 축 지름 3 mm, 축에 끼우는 PLA 링 위에 자석)'
LINK = '로봇 저장소 main docs/interfaces/2026-10-22-mcu-link-contract.md (Jetson ↔ MCU 전송로 USB CDC 또는 UART, 미정), week-11/build_deck.py 09 장 (H743 이 DRV8244 4개를 직접 구동)'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def img(src, alt, cap=None, cls='shot'):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="{cls}"><img class="media" src="assets/{src}" '
            f'alt="{escape(alt, quote=True)}">{c}</figure>')


def table(head, rows, cls='comparison h7'):
    h = ''.join(f'<th>{x}</th>' for x in head)
    body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'


# ----------------------------------------------------------------- cover
add('견학 보고', '2026 로보월드\n견학 보고', 20, '',
    """안녕하십니까. 2026 로보월드 견학 내용을 보고드릴 김광민이라고 합니다. 저희 팀은 지게차 하드웨어를 만들고 있어서, 무인 지게차와 모터, 모터 드라이버를 다루는 부스를 중심으로 둘러보고 저희 설계와 관련된 질문을 했습니다. 본 것과 들은 답을 저희 지게차와 비교해서 말씀드리겠습니다. (전환)""",
    [(EVENT, '행사'), (NOTES, '부스 질의')], '견학 보고')

# ----------------------------------------------------------------- 1
VISIT_ROWS = [
    ('Multiway Robotics', '무인 지게차', '작업 통로 폭 · 최대 하중별 지게차 8종'),
    ('H3R', '드론 모터 · ESC', '6상 모터와 3상 ESC 두 개를 묶은 구동계'),
    ('CubeMars', '로봇 관절 모터 (AK 시리즈)', 'CAN 연결 문제와 CAN FD 출시 계획'),
    ('FASTECH (Ezi-Pos)', '서보 모터 드라이버', 'maxon 모터 겸용 EtherCAT · Ethernet 드라이버'),
]
add('견학 개요', '01  견학 개요', 40, f"""
<h2 class="headline">2026 로보월드에서 무인 지게차 · 모터 · 모터 드라이버 4개 업체 부스 조사</h2>
{table(['업체', '분야', '살펴본 것'], VISIT_ROWS, 'comparison h7 vt111')}
<p class="ev111">2026 로보월드 · 고양 킨텍스 1전시장 · 11월 4–7일 · 402개 기업 참가 (견학 11월 6–7일)</p>
""",
    """로보월드는 11월 4일부터 7일까지 킨텍스에서 열렸고 402개 기업이 참가했습니다. 저희는 6일과 7일에 다녀왔습니다. 로봇 전체를 보기보다 저희 지게차를 만드는 데 직접 관련된 부스를 골라 네 곳을 자세히 봤습니다. 무인 지게차를 만드는 Multiway Robotics, 드론 모터를 만드는 H3R, 로봇 관절 모터인 AK 시리즈를 파는 CubeMars, 그리고 maxon 모터와 함께 쓰는 서보 드라이버를 파는 FASTECH입니다. 차례로 말씀드리겠습니다. (전환)""",
    [(EVENT, '일정 · 장소 · 규모'), (PHOTO, '견학일 (사진 촬영일 11-06 · 11-07)'), (NOTES, '부스별 질의 내용')],
    '표: 견학한 부스')

# ----------------------------------------------------------------- 2
FORK_ROWS = [
    ('형태', '카운터밸런스 · 리치 · 3방향 등 8종', '카운터밸런스 형태'),
    ('최대 하중', '1,500–8,000 kg', '10 kg'),
    ('들어 올리는 높이', '최대 16.5 m 랙', '0.28 m'),
]
add('무인 지게차 제품군', '02  무인 지게차 제품군 (Multiway Robotics)', 60, f"""
<h2 class="headline">상용 무인 지게차, 작업 통로 폭 1.75–4.1 m · 최대 하중 1.5–8 t 에 따라 8종으로 구분</h2>
<div class="vis111 grow">
{img('v02_multiway.jpg', 'Multiway Robotics 부스 벽면. 16.5 m 하이랙 · 8톤 장척물 이송이라는 제목 아래 높이 눈금과 함께 랙 옆에 선 지게차 8종, 아래에 종류마다 작업공간 폭과 최대 하중, 시리즈 이름', 'Multiway Robotics 부스의 제품군 안내')}
<div class="stack vr111">
{img('d02_truck.jpg', '팀 지게차 차체. 빨간 좌석과 지붕이 있는 어린이용 전동 지게차, 앞에 검은 포크 두 개', '우리 차체', 'shot truck111')}
{table(['', 'Multiway 제품군', '우리 차체'], FORK_ROWS, 'comparison h7 ft111')}
</div>
</div>
""",
    """첫 번째는 무인 지게차 업체 Multiway Robotics입니다. 부스 벽면에 제품 여덟 종을 랙 높이와 함께 늘어놓았는데, 종류마다 맨 먼저 적은 것이 작업 통로 폭과 최대 하중이었습니다. 통로 폭은 1.75미터에서 4.1미터, 하중은 1.5톤에서 8톤까지입니다. 눈에 띈 점은 카운터밸런스형이 3.15미터와 4.1미터로 통로를 가장 넓게 쓴다는 것입니다. 포크만 옆으로 돌리는 3방향 지게차는 1.75미터면 되지만, 카운터밸런스형은 차체 전체를 돌려 팔레트를 마주해야 하기 때문입니다. 저희 차체도 카운터밸런스 형태라서 같은 제약이 있고, 리보틱스의 좁은 통로 장면에서 전진과 후진을 바꿔 가며 방향을 맞추는 것도 이 때문입니다. 크기는 하중 10킬로그램, 들어 올리는 높이 0.28미터로 상용 제품과 비교할 수 없이 작지만, 형태가 정하는 움직임의 제약은 같습니다. (전환)""",
    [(PHOTO, 'v02_multiway.jpg: 부스 벽면 (11-06 촬영), 작업공간 Ast 1,750–4,100 mm, 최대 하중 1,500–8,000 kg, 카운터 밸런스 타입 SE 3,150 mm · E 4,100 mm, 3방향 K 1,750 mm; 고객사 로고 아래쪽은 잘라 냄'),
     (HW, '우리 차체 하중 · 승강 범위'),
     ('week-09/assets/d02_truck.jpg', '팀 차체 사진 (5주차)'),
     ('week-08/build_deck.py 06 장 · week-11/build_deck.py 05 장', '리보틱스 좁은 통로 장면, 방향 전환 지점')],
    '사진: Multiway Robotics 부스 (팀 촬영)와 팀 차체')

# ----------------------------------------------------------------- 3
MOTOR_ROWS = [
    ('모터', '3상 BLDC (6상 개발 중)', '브러시 DC, 축 지름 3&nbsp;mm'),
    ('회전 감지', '엔코더 없이 홀 센서만 사용', '축 끝 자석 + MT6701 자기 엔코더'),
    ('센서 장착', '작은 모터라 엔코더 자리 부족', '축에 끼운 출력 링에 자석 부착'),
]
add('6상 드론 모터', '03  6상 드론 모터 (H3R)', 60, f"""
<h2 class="headline">소형 모터는 엔코더 넣을 자리가 부족해 홀 센서만 쓰는 6상 모터로 대응</h2>
<div class="vis111 grow">
{img('v03_h3r.jpg', 'H3R 부스 포스터. 6-PHASE MOTOR & DUAL 3-PHASE ESC 제목 아래 하늘색 모터와 ESC, 오른쪽에 고장 허용 · 토크 안정 · 진동 감소 · 이중 채널 · 열 분산 항목, 아래에 6상 단면도와 ESC A · ESC B 두 개가 모터의 A1 B1 C1, A2 B2 C2 를 나눠 구동하는 도식', 'H3R 부스 포스터')}
<div class="stack vr111">
{img('h05_mounted.jpg', '우리 바퀴 모터 뒷면. 가운데 축에 회색 링이 끼워져 있고 양옆으로 노란색, 초록색 전원선', '우리 바퀴 모터 축에 끼운 자석 링', 'shot truck111')}
{table(['', 'H3R 드론 모터', '우리 바퀴 모터'], MOTOR_ROWS, 'comparison h7 ft111')}
</div>
</div>
""",
    """두 번째는 드론 모터 업체 H3R입니다. 지금은 3상 드론 모터를 만들고 있고, 포스터처럼 6상 모터를 개발하고 있었습니다. 요즘 6상 모터가 많이 보이는 이유를 물었더니, 모터가 작아지면서 엔코더를 넣기 어려워져 엔코더 없이 홀 센서만 쓰고 대신 상을 늘리는 방식으로 대응한다는 답을 들었습니다. 포스터에는 6상을 3상 ESC 두 개로 나눠 구동해 한쪽이 고장 나도 돌 수 있고 토크와 진동이 안정된다는 장점도 적혀 있었습니다. 저희도 비슷한 문제를 겪었습니다. 바퀴 모터는 축 지름이 3밀리미터인 작은 브러시 DC 모터라 엔코더를 달 자리가 없어서, 축에 끼우는 링을 3D 프린터로 뽑아 그 위에 자석을 붙이고 MT6701 자기 엔코더로 회전을 읽습니다. 작은 모터에서는 회전을 어떻게 잴지가 설계의 큰 부분이라는 점을 업체에서도 확인했습니다. (전환)""",
    [(NOTES, '드론 모터 회사: 6상이 많은 이유 → 모터가 작아지면서 엔코더를 넣기 힘들어 상을 늘리는 방식으로 대응; 3상 드론 모터 회사, 홀 센서만 쓰려고 6상 개발 중'),
     (PHOTO, 'v03_h3r.jpg: H3R 포스터 (11-06 촬영) — Electric Propulsion System with Built-in Redundancy, FAULT-TOLERANT · STABLE TORQUE · REDUCED VIBRATION · DUAL-CHANNEL POWER HANDLING · THERMAL LOAD SHARING, ESC A (A1 B1 C1) · ESC B (A2 B2 C2) + Synchronization'),
     (WHEEL, '우리 바퀴 모터와 자석 링'),
     ('메모리: 하드웨어 사실 (2026-10-12)', 'MT6701 은 뒤 좌우 바퀴 엔코더; DRV8244 는 브러시 DC 모터 드라이버')],
    '사진: H3R 부스 포스터 (팀 촬영)와 팀 바퀴 모터 (9주차)')

# ----------------------------------------------------------------- 4
BUS_ROWS = [
    ('CubeMars AK 모터', 'CAN', '여러 대 동시 연결 시 통신 불량, 내년 CAN FD 제품 출시 예정'),
    ('FASTECH Ezi-Pos', 'EtherCAT · Ethernet 등', 'maxon 등 여러 모터를 한 드라이버 계열로 제어'),
    ('우리 지게차', '모터 버스 없음', 'H743 이 모터 드라이버 4개를 직접 구동'),
]
add('여러 모터를 묶는 통신', '04  여러 모터를 묶는 통신 (CubeMars · FASTECH)', 60, f"""
<h2 class="headline">CAN 동시 연결 한계, CubeMars 는 CAN FD · FASTECH 은 EtherCAT 으로 대응</h2>
<div class="vis111 bus111 grow">
{img('v04_ezipos.jpg', 'FASTECH Ezi-Pos 부스 진열대. 왼쪽에 AGV/AMR 구동부, 가운데에 노란 서보 드라이버 여러 대와 maxon 모터 여덟 개, 오른쪽 선반에 CC-Link IE TSN · Profinet · EtherCAT · Ethernet 드라이버와 여러 모터', 'FASTECH Ezi-Pos 부스')}
{table(['', '통신', '확인한 내용'], BUS_ROWS, 'comparison h7 bt111')}
</div>
""",
    """세 번째와 네 번째는 모터 여러 개를 묶는 통신입니다. CubeMars의 AK 모터는 CAN으로 명령을 받는데, 여러 대를 한 버스에 동시에 물리면 잘 동작하지 않는 경우가 있어서 몇 대까지 가능한지 물었습니다. 동시에 많이 쓰는 것은 어렵다는 답이었고, 내년 초에 하드웨어를 바꾼 제품이 나오고 내년 중에 CAN FD를 지원하는 제품이 나와 연결 문제가 나아질 것이라고 했습니다. FASTECH은 Ezi-Pos라는 서보 드라이버에 maxon 모터를 묶어 파는 업체인데, 사진처럼 EtherCAT과 Ethernet 등 산업용 네트워크로 여러 축을 묶는 드라이버를 내세웠습니다. 저희 지게차는 지금 모터 버스가 없습니다. 메인보드의 H743이 모터 드라이버 네 개를 직접 구동하고, Jetson과는 한 줄로만 연결합니다. 그래서 CAN 동시 연결 문제는 지금 구조와는 관계가 없지만, 나중에 모터를 지능형 액추에이터로 바꾸거나 축을 늘린다면 이 부분을 먼저 따져야 한다는 것을 알게 되었습니다. 이상으로 로보월드 견학 보고를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [(NOTES, 'AK 모터: CAN 동시에 여러 개 쓰면 잘 안 됨 → 동시에 많이 사용하면 안 될 것, 내년 초 하드웨어 변경, 내년 CAN FD; 큐브마스: CAN FD 내년 중 출시 예정, 기존 CAN 연결 불량 해결 기대; maxon 모터 합본 판매 회사: 이더넷 · 이더캣 기반 모터 드라이버'),
     (PHOTO, 'v04_ezipos.jpg: FASTECH Ezi-Pos 부스 (11-07 촬영) — 선반 표기 CC-Link IE TSN · Profinet · EtherCAT · Ethernet, maxon 모터 진열, 안내판의 FASTECH 표기'),
     (LINK, '우리 지게차 구조')],
    '사진: FASTECH Ezi-Pos 부스 (팀 촬영)')


TITLE = '2026 로보월드 견학 보고'
SUBTITLE = '고양 킨텍스 · 2026년 11월 6–7일 견학'
TOTAL = 240


def build():
    assert len(slides) == 5, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-11-11. 부스 답변은 팀 인터뷰 메모, 사진은 팀 촬영이다(SOURCES.md). '
              '원고는 발표자 문체(합니다체)로 썼고, (전환)은 다음 쪽으로 넘기는 자리다.', '']
    elapsed = 0
    for i, s in enumerate(slides, 1):
        source_lines = '\n'.join(f'{label}: {url}' for url, label in s['sources'])
        notes = (f"권장 {s['seconds']}초\n\n{s['notes']}\n\n"
                 f"[Sources]\n{s['foot']}\n{source_lines}\n[/Sources]")
        if i == 1:
            component = (f'<x-import component-from-global-scope="UOSSlideDS.TitleSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}" '
                         f'subtitle="{escape(SUBTITLE, quote=True)}"></x-import>')
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
