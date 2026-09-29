"""Build the week 5 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 5 is a hardware report: chassis, fork and pallet measurements, the
logic-analyser reverse engineering of the remote control, and the choice of
motor driver (DRV8244-Q1) and encoder (MT6701). The measurement and waveform
slides are placeholders until the team's data arrives. The LiDAR simulation
slides drafted here on 2026-09-29 moved to week-06/ for next week.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
MAP = 'docs/plans/2026-09-11-development-roadmap.md'
INTAKE = 'docs/validation/2026-09-23-chassis-intake.md'
MODEL = 'sim/models/dls08_provisional/parameters.yaml'
FEEDBACK = 'docs/references/week4_feedback.md'
slides = []



def add(label, title, seconds, body, notes, sources, foot='측정 결과'):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def figure(src, alt, caption, *, video=None, cls='wide'):
    if video is None:
        video = src.rsplit('.', 1)[-1].lower() in {'mp4', 'webm'}
    poster = src.rsplit('.', 1)[0].replace('_seed16', '') + '_poster.jpg'
    poster_attr = f' poster="assets/{poster}"' if (ROOT / 'assets' / poster).exists() else ''
    tag = (f'<video class="media" src="assets/{src}"{poster_attr} autoplay loop muted playsinline '
           f'aria-label="{escape(alt, quote=True)}"></video>' if video else
           f'<img class="media" src="assets/{src}" alt="{escape(alt, quote=True)}">')
    cap = f'<figcaption class="small muted">{caption}</figcaption>' if caption else ''
    return f'<figure class="shot {cls}">{tag}{cap}</figure>'


def placeholder(what, detail, cls='grow'):
    """A visible slot for material that does not exist yet."""
    return (f'<div class="placeholder {cls}"><b>{what}</b>'
            f'<span>{detail}</span></div>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '5주차\n자율 지게차 개발', 20, '',
    """이번 주에는 하드웨어를 다룬다. 입고한 차체와 포크, 동봉 팔레트를 실측하고, 4주차 피드백에 따라 조종기 버튼별 신호를 로직 애널라이저로 측정해 기존 제어 신호를 역으로 분석하였다. 마지막으로 컴퓨터가 차체를 직접 구동하고 상태를 읽기 위한 부품으로 모터 드라이버와 엔코더를 선정한 근거를 보인다.""",
    [(INTAKE, '입고 조사'), (FEEDBACK, '4주차 피드백 §2')], '진행 보고')

# ----------------------------------------------------------------- 3 (placeholder)
MEASURE_ROWS = [
    ('전장 × 전폭 × 전고', '1.46 × 0.63 × 1.01 m (카탈로그)'),
    ('질량', '24 kg (카탈로그)'),
    ('축간 거리 · 윤거', '0.64 · 0.51 m (사진 추정)'),
    ('바퀴 반지름', '0.135 m (사진 추정)'),
    ('포크 길이 · 폭 · 두께', '420 · 55 · 24 mm (사진 추정)'),
    ('포크 중심 간격', '290 mm (사진 추정)'),
    ('승강 범위', '280 mm (사진 추정)'),
    ('최소 회전 반경', '— (주행 시험 필요)'),
]
measure_table = ''.join(f'<tr><td>{k}</td><td class="pending">—</td><td class="muted">{v}</td></tr>'
                        for k, v in MEASURE_ROWS)
add('차체 실측', '01  차체 실측', 70, f"""
<h2 class="headline">차체 실측값과 잠정 모델 비교 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:0.8fr 1.2fr">
{placeholder('치수선 사진', '측정 기준점·치수선 표시')}
<table class="comparison measure"><tr><th>항목</th><th>실측 (예정)</th><th>잠정 모델</th></tr>{measure_table}</table>
</div>
<div class="takeaway">반영 계획: 실측값으로 시뮬레이션 모델·좌표 변환 갱신</div>
""",
    """[작성 예정] 차체 실측 결과를 보인다. 측정 대상과 기준점, 측정값을 표로 정리하고, 지금까지 시뮬레이션에 쓴 잠정 모델 값과 비교한다. 잠정 모델은 상품 사진과 카탈로그로 만든 것이므로 실측값으로 바꾼다. 최소 회전 반경은 주행 시험이 필요해 정적 실측과 따로 표시한다.""",
    [(MODEL, '잠정 모델 치수 — 카탈로그 값과 사진 비례 추정'), (INTAKE, '입고 때 미측정 항목')],
    '화면 생성: 실물 사진 (작성 예정)')

# ----------------------------------------------------------------- 3 (placeholder)
add('포크·동봉 팔레트', '02  포크 · 동봉 팔레트', 60, f"""
<h2 class="headline">포크·동봉 팔레트 실측 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:1fr 1fr">
{placeholder('포크 사진 · 치수선', '폭 · 두께 · 간격 · 최저·최고 높이')}
{placeholder('동봉 팔레트 사진 · 치수선', '외형 · 포켓 개구 폭·높이 · 포크와의 여유')}
</div>
<div class="takeaway">포크 치수: 시험 팔레트 제작과 삽입 여유 계산의 기준</div>
""",
    """[작성 예정] 포크의 폭과 두께, 두 포크의 간격, 최저·최고 높이를 잰 결과를 보인다. 오른쪽은 차체와 함께 온 팔레트의 외형과 포켓 개구이다. 포크 치수와 포켓 개구의 차이가 삽입할 때의 좌우·상하 여유가 되므로, 이 값이 시험 팔레트 제작과 삽입 목표의 기준이 된다.""",
    [(INTAKE, '입고 때 관찰한 포크·동봉 팔레트'), (MODEL, '잠정 모델 포크 치수 — 사진 추정')],
    '화면 생성: 실물 사진 (작성 예정)')

# ----------------------------------------------------------------- 4 remote setup
add('조종기 측정 구성', '03  조종기 신호 측정 구성', 60, f"""
<h2 class="headline">무선 조종기 → 제어기 신호를 로직 애널라이저로 측정 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:0.9fr 0.9fr 1.2fr">
{figure('05_remote.jpg', '무선 조종기 T07D-DGN. 전진·후진, 상승·하강, 좌회전·우회전, 속도 조절과 제동 버튼', '무선 조종기 T07D-DGN', cls='')}
{figure('04_controller_label.jpg', '좌석 아래 제어기의 라벨 J6 D-CC-12V', '제어기 J6 D-CC-12V', cls='')}
{placeholder('측정 구성 사진', '탐침 연결 지점 · 채널 배정 · 샘플링 속도')}
</div>
<div class="takeaway">측정: 버튼을 하나씩 눌러 제어기 입력·모터 출력 신호를 기록</div>
""",
    """[작성 예정] 측정 대상은 무선 조종기와 좌석 아래 제어기이다. 조종기의 무선 신호를 제어기가 받아 주행, 조향, 승강 모터를 구동한다. 오른쪽은 로직 애널라이저를 연결한 모습으로, 어느 지점에 탐침을 대고 채널을 어떻게 나눴는지, 샘플링 속도는 얼마로 했는지 보인다. 버튼을 하나씩 누르며 각 채널의 신호가 어떻게 바뀌는지 기록하였다.""",
    [(INTAKE, '조종기·제어기 표기와 사진'), (FEEDBACK, '§2 로직 애널라이저로 버튼별 신호 측정')],
    '화면 생성: 실물 사진(2026-09-23 입고) · 측정 구성 사진(작성 예정)')

# ----------------------------------------------------------------- 5 waveforms drive/steer
add('주행·조향 파형', '04  버튼별 파형 · 주행 · 조향', 90, f"""
<h2 class="headline">주행·조향 버튼별 로직 애널라이저 파형 <span class="draft">작성 중</span></h2>
<div class="stack grow">
{placeholder('전진 · 후진', '같은 시간축에 채널별 파형을 한 줄씩 · 버튼 누름 구간 표시')}
{placeholder('좌회전 · 우회전', '같은 시간축 · 방향에 따라 바뀌는 채널 강조')}
</div>
""",
    """[작성 예정] 주행과 조향 버튼을 하나씩 눌렀을 때의 파형이다. 모든 파형은 같은 시간축에 채널별로 한 줄씩 놓아, 버튼에 따라 어느 채널이 어떻게 바뀌는지 비교한다. 전진과 후진에서 신호가 방향만 바뀌는지, 속도가 듀티로 표현되는지, 조향이 좌우 두 신호로 나뉘는지를 확인한다.""",
    [(FEEDBACK, '§2 버튼별 신호 측정')],
    '화면 생성: 로직 애널라이저 캡처 (작성 예정)')

# ----------------------------------------------------------------- 6 waveforms lift/other
add('승강·기타 파형', '05  버튼별 파형 · 승강 · 속도 · 제동', 80, f"""
<h2 class="headline">승강·속도 조절·제동 버튼별 파형 <span class="draft">작성 중</span></h2>
<div class="stack grow">
{placeholder('상승 · 하강', '같은 시간축 · 승강 모터 채널')}
{placeholder('속도 조절 · 제동', '속도 단계별 변화 · 제동 시 신호')}
</div>
""",
    """[작성 예정] 승강과 속도 조절, 제동 버튼의 파형이다. 상승과 하강이 승강 모터의 방향 신호로 나타나는지, 속도 조절 버튼이 주행 신호의 듀티나 전압을 바꾸는지, 제동이 어떤 신호로 전달되는지 확인한다.""",
    [(FEEDBACK, '§2 버튼별 신호 측정')],
    '화면 생성: 로직 애널라이저 캡처 (작성 예정)')

# ----------------------------------------------------------------- 7 reverse engineering summary
SIGNAL_ROWS = ['전진', '후진', '좌회전', '우회전', '상승', '하강', '속도 조절', '제동']
signal_table = ''.join(f'<tr><td>{b}</td><td class="pending">—</td><td class="pending">—</td><td class="pending">—</td></tr>' for b in SIGNAL_ROWS)
add('신호 해석', '06  리버스 엔지니어링 결과', 80, f"""
<h2 class="headline">버튼별 신호 형식과 컴퓨터 명령 입력 지점 <span class="draft">작성 중</span></h2>
<div class="split grow" style="grid-template-columns:1.1fr 0.9fr">
<table class="comparison measure"><tr><th>버튼</th><th>신호선</th><th>형식 (레벨 · PWM · 직렬)</th><th>해석</th></tr>{signal_table}</table>
{placeholder('신호 경로 도식', '조종기 → 수신부 → 제어기 → 모터 · 컴퓨터가 끼어들 지점 표시')}
</div>
<div class="takeaway">다음 작업: 명령 입력 지점에 모터 드라이버 연결 · 기존 제어기 대체 여부 결정</div>
""",
    """[작성 예정] 파형을 버튼별로 정리한 표이다. 버튼마다 어느 신호선이 바뀌는지, 그 신호가 단순 켜짐·꺼짐인지 PWM인지 직렬 통신인지, 그리고 그것이 무엇을 뜻하는지 적는다. 오른쪽 도식은 조종기에서 모터까지의 신호 경로와, 컴퓨터가 명령을 넣을 수 있는 지점을 보인다. 이 결과에 따라 기존 제어기를 살려 신호만 넣을지, 모터 드라이버로 제어기를 대체할지 정한다.""",
    [(FEEDBACK, '§2 리버스 엔지니어링')],
    '화면 생성: 측정 결과 정리 (작성 예정)')

# ----------------------------------------------------------------- 8 motor driver
DRV_DS = 'https://www.ti.com/lit/ds/symlink/drv8244-q1.pdf'
MT_DS = 'https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf'
# Continuous current and protection limit kept in separate columns: they are
# different ratings (DRV8244's continuous figure is TI's thermal simulation).
PICK = ' class="pick"'
DRIVER_ROWS = [
    ('DRV8244-Q1 (선정)', '4.5–35 V', 'DC 4.0 A *', 'OCP 10.5–40 A 선택', 'IPROPI 내장'),
    ('BTS7960 (IBT-2)', '—', '—', '전류 제한 43 A (typ)', 'IS 핀'),
    ('VNH5019 (Pololu)', '5.5–24 V', '12 A', '30 A 최대', '약 140 mV/A'),
    ('Cytron MD13S', '6–30 V', '13 A', '30 A (10 s)', '—'),
    ('DRV8871', '6.5–45 V', '—', '3.6 A 피크', '없음'),
]
driver_table = ''.join(
    f'<tr{PICK if i == 0 else ""}><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>'
    for i, (a, b, c, d, e) in enumerate(DRIVER_ROWS))
add('모터 드라이버 선정', '07  하드웨어 선정 · 모터 드라이버', 80, f"""
<h2 class="headline">모터 드라이버: DRV8244-Q1 SPI형 (DRV8244SQRYJRQ1) 선정</h2>
<div class="split grow" style="grid-template-columns:1.5fr 0.62fr">
<div class="stack" style="justify-content:center;gap:8px">
<table class="comparison select"><tr><th>후보</th><th>전원</th><th>연속 전류</th><th>보호·최대</th><th>전류 측정</th></tr>{driver_table}</table>
<p class="chart-cap">* TI 열 해석값: PWM 구동 · 주위 85 °C · 40 × 40 mm 4층 기판. 다른 후보는 제조사 연속 정격</p>
</div>
<div class="stack reasons">
<article><h3>전류 측정 내장</h3><p>IPROPI 핀 → MCU ADC로 모터 전류<br>막힘·포크 끝단 감지에 활용</p></article>
<article><h3>SPI 설정·진단</h3><p>전류 제한·과전류 임계·슬루율 설정<br>결함 종류를 레지스터로 확인</p></article>
<article class="warn"><h3>조건: 모터 전류 실측 후 확정</h3><p>연속 전류는 방열이 결정<br>→ 실측 전류에 맞춰 전류 제한·방열 기판 설계</p></article>
</div>
</div>
""",
    """모터 드라이버로는 TI의 DRV8244-Q1 SPI형을 골랐다. 왼쪽은 비교한 후보이다. 완성 보드인 VNH5019나 MD13S는 바로 쓸 수 있지만, 우리가 원하는 것은 컴퓨터가 모터 전류를 읽고 드라이버의 상태를 확인하는 것이다. DRV8244는 전류에 비례하는 신호를 IPROPI 핀으로 내보내므로, 션트 저항 없이 MCU의 ADC로 모터 전류를 읽을 수 있다. 이 값으로 바퀴가 막히거나 포크가 끝에 닿은 것을 알아낼 수 있다. SPI형은 전류 제한 크기와 과전류 임계값, 출력 전압이 바뀌는 속도를 설정할 수 있고, 어떤 결함이 났는지 레지스터로 읽을 수 있다. 전원은 4.5에서 35볼트까지라 12볼트 차체에 여유가 있다. 표에서 연속 전류와 보호 전류는 다른 값이다. DRV8244의 연속 전류는 TI가 85도 환경, 4층 기판, PWM 구동으로 계산한 열 해석값 4암페어로, 기판 방열에 따라 달라진다. 그래서 이 선정은 차체 모터의 전류를 잰 뒤 확정하며, 그 전류에 맞춰 전류 제한과 기판 방열을 설계한다.""",
    [(DRV_DS, 'DRV8244-Q1 데이터시트 SLVSG24C — 4.5–35 V, RON 47 mΩ(VQFN-HR), 출력 전류 Internally limited, OCP 21–40/15–31/10.5–24 A, ITRIP 7단계, fPWM ≤ 25 kHz, AIPROPI 4750 A/A, 표 7-1 DC 4.0 A (PWM, 85 °C, 40×40 mm 4층 2 oz), 주문 표 DRV8244SQRYJRQ1 = VQFN-HR(RYJ) 16'),
     ('https://www.infineon.com/dgdl/bts7960b-pb-final.pdf?fileId=db3a30431ed1d7b2011efe782ebd6b60', 'BTS7960 제품 요약 — 전류 제한 43 A typ'),
     ('https://www.pololu.com/product/1451', 'Pololu VNH5019 — 5.5–24 V, 12 A 연속, 30 A 최대, 약 140 mV/A'),
     ('https://courses.ideate.cmu.edu/16-375/f2026/text/electronics/cy-md13s-driver.html', 'Cytron MD13S — 6–30 V, 13 A 연속, 30 A 10 s'),
     ('https://www.ti.com/lit/ds/symlink/drv8871.pdf', 'DRV8871 — 6.5–45 V, 3.6 A 피크')],
    '출처: 제조사 데이터시트 · 제품 페이지')

# ----------------------------------------------------------------- 9 encoder
ENCODER_ROWS = [
    ('MT6701 (선정)', '14 bit', 'I2C · SSI · ABZ · UVW · 아날로그 · PWM', '절대 + 증분', '±1.5° (max)'),
    ('AS5600', '12 bit', 'I2C · 아날로그 · PWM', '절대', '±1° (시스템 INL)'),
    ('AS5048A/B', '14 bit', 'SPI 또는 I2C · PWM', '절대', '±1.2° (온도 포함)'),
    ('AS5047P', '14 bit', 'SPI · ABI · UVW · PWM', '절대 + 증분', '±1° (온도 포함)'),
    ('모터축 쿼드러처', '제품별', 'A/B(Z)', '증분', '원점 복귀 필요'),
]
encoder_table = ''.join(
    f'<tr{PICK if i == 0 else ""}><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>'
    for i, (a, b, c, d, e) in enumerate(ENCODER_ROWS))
add('엔코더 선정', '08  하드웨어 선정 · 엔코더', 70, f"""
<h2 class="headline">엔코더: MT6701 선정 — 절대각과 증분 출력을 한 칩에</h2>
<div class="split grow" style="grid-template-columns:1.5fr 0.62fr">
<table class="comparison select"><tr><th>후보</th><th>분해능</th><th>출력</th><th>방식</th><th>정확도</th></tr>{encoder_table}</table>
<div class="stack reasons">
<article><h3>조향각: 절대각</h3><p>전원을 켜자마자 각도 확인<br>원점 복귀 동작 불필요</p></article>
<article><h3>바퀴 속도: ABZ 증분</h3><p>MCU 타이머 엔코더 모드로 직접 계수<br>비접촉 자석식 · 1–2달러대</p></article>
<article class="note"><h3>4주차 피드백: 분해능</h3><p>"10 bit면 충분" → 14 bit로 충분<br>성능은 정확도(±1.5°)와 자석 정렬이 좌우</p></article>
</div>
</div>
<div class="takeaway">장착 조건: 자석 축 어긋남 ≤ 0.3 mm · 간격 0.5–2 mm → 브래킷 설계 필요</div>
""",
    """엔코더로는 자석식 각도 센서인 MT6701을 골랐다. 축 끝에 자석을 붙이고 그 위에 칩을 두면 접촉 없이 회전각을 잰다. 가장 큰 이유는 한 칩이 절대각과 증분 출력을 모두 낸다는 점이다. 조향축에 달면 전원을 켜자마자 현재 조향각을 알 수 있어 원점을 찾는 동작이 필요 없고, 바퀴 쪽에 달면 ABZ 출력을 MCU 타이머의 엔코더 모드로 바로 세어 속도를 잰다. 값도 1에서 2달러 수준이다. 비슷한 기능의 AS5047P가 정확도는 조금 낫지만, MT6701은 I2C와 아날로그 출력까지 있고 영점을 칩에 저장할 수 있다. 4주차에 엔코더 분해능은 10비트면 충분하다는 피드백을 받았다. MT6701은 14비트로 충분하고, 실제 성능은 분해능보다 최대 1.5도의 정확도와 자석을 얼마나 바르게 붙이는지가 좌우한다. 그래서 자석과 칩의 축 어긋남 0.3밀리미터 이하, 간격 0.5에서 2밀리미터를 지키는 브래킷을 설계한다. 어느 축에 몇 개를 달지는 조종기 신호 분석과 모터 구조를 확인한 뒤 정한다.""",
    [(MT_DS, 'MT6701 데이터시트 Rev.1.5 — 14 bit, I2C·SSI·ABZ(≤1024 PPR)·UVW·아날로그·PWM, INL ±1.5° max, 자석 Ø6×2.5 mm·간격 0.5–2.0 mm·축 어긋남 ≤0.3 mm, 영점 EEPROM'),
     ('https://www.lcsc.com/product-detail/Angle-Linear-Position-Sensors_Magn-Tek-MT6701CT-STD_C2856764.html', 'LCSC 가격 $1.43–2.04'),
     ('https://www1.futureelectronics.com/doc/ams/AS5047P-ATSM.pdf', 'AS5047P — 14 bit, SPI·ABI·UVW·PWM, 온도 포함 ±1°'),
     ('https://media.digikey.com/pdf/Data%20Sheets/Austriamicrosystems%20PDFs/AS5048A,B.pdf', 'AS5048A/B — 14 bit, 온도 포함 ±1.2°'),
     ('https://files.seeedstudio.com/wiki/Grove-12-bit-Magnetic-Rotary-Position-Sensor-AS5600/res/Magnetic%20Rotary%20Position%20Sensor%20AS5600%20Datasheet.pdf', 'AS5600 — 12 bit, 시스템 INL ±1°'),
     (FEEDBACK, '§4 엔코더 분해능 10 bit면 충분')],
    '출처: 제조사 데이터시트 · 판매처 가격')

TITLE = '5주차 자율 지게차 개발'
TOTAL = 610
N_SLIDES = 9


def build():
    assert len(slides) == N_SLIDES, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{N_SLIDES}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-09-29. 하드웨어 발표이다. 실측·파형 쪽은 팀 측정 결과이고, 부품 선정 쪽의 사양은 제조사 데이터시트 값이다.', '']
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
