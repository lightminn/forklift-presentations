# 5주차 자율 지게차 개발 · 발표 원고

9장 · 시간 배분 합계 10분 10초. 쪽별 배정 시간은 발표 연습 후 조정한다.

기준일: 2026-09-29. 하드웨어 발표이다. 실측·파형 쪽은 팀 측정 결과이고, 부품 선정 쪽의 사양은 제조사 데이터시트 값이다.

## 1쪽 · 개발 진행 보고 (00:00–00:20, 20초)

이번 주에는 하드웨어를 다룬다. 입고한 차체와 포크, 동봉 팔레트를 실측하고, 4주차 피드백에 따라 조종기 버튼별 신호를 로직 애널라이저로 측정해 기존 제어 신호를 역으로 분석하였다. 마지막으로 컴퓨터가 차체를 직접 구동하고 상태를 읽기 위한 부품으로 모터 드라이버와 엔코더를 선정한 근거를 보인다.

[Sources]
입고 조사: docs/validation/2026-09-23-chassis-intake.md
4주차 피드백 §2: docs/references/week4_feedback.md
[/Sources]

## 2쪽 · 차체 실측 (00:20–01:30, 70초)

[작성 예정] 차체 실측 결과를 보인다. 측정 대상과 기준점, 측정값을 표로 정리하고, 지금까지 시뮬레이션에 쓴 잠정 모델 값과 비교한다. 잠정 모델은 상품 사진과 카탈로그로 만든 것이므로 실측값으로 바꾼다. 최소 회전 반경은 주행 시험이 필요해 정적 실측과 따로 표시한다.

[Sources]
잠정 모델 치수 — 카탈로그 값과 사진 비례 추정: sim/models/dls08_provisional/parameters.yaml
입고 때 미측정 항목: docs/validation/2026-09-23-chassis-intake.md
[/Sources]

## 3쪽 · 포크·동봉 팔레트 (01:30–02:30, 60초)

[작성 예정] 포크의 폭과 두께, 두 포크의 간격, 최저·최고 높이를 잰 결과를 보인다. 오른쪽은 차체와 함께 온 팔레트의 외형과 포켓 개구이다. 포크 치수와 포켓 개구의 차이가 삽입할 때의 좌우·상하 여유가 되므로, 이 값이 시험 팔레트 제작과 삽입 목표의 기준이 된다.

[Sources]
입고 때 관찰한 포크·동봉 팔레트: docs/validation/2026-09-23-chassis-intake.md
잠정 모델 포크 치수 — 사진 추정: sim/models/dls08_provisional/parameters.yaml
[/Sources]

## 4쪽 · 조종기 측정 구성 (02:30–03:30, 60초)

[작성 예정] 측정 대상은 무선 조종기와 좌석 아래 제어기이다. 조종기의 무선 신호를 제어기가 받아 주행, 조향, 승강 모터를 구동한다. 오른쪽은 로직 애널라이저를 연결한 모습으로, 어느 지점에 탐침을 대고 채널을 어떻게 나눴는지, 샘플링 속도는 얼마로 했는지 보인다. 버튼을 하나씩 누르며 각 채널의 신호가 어떻게 바뀌는지 기록하였다.

[Sources]
조종기·제어기 표기와 사진: docs/validation/2026-09-23-chassis-intake.md
§2 로직 애널라이저로 버튼별 신호 측정: docs/references/week4_feedback.md
[/Sources]

## 5쪽 · 주행·조향 파형 (03:30–05:00, 90초)

[작성 예정] 주행과 조향 버튼을 하나씩 눌렀을 때의 파형이다. 모든 파형은 같은 시간축에 채널별로 한 줄씩 놓아, 버튼에 따라 어느 채널이 어떻게 바뀌는지 비교한다. 전진과 후진에서 신호가 방향만 바뀌는지, 속도가 듀티로 표현되는지, 조향이 좌우 두 신호로 나뉘는지를 확인한다.

[Sources]
§2 버튼별 신호 측정: docs/references/week4_feedback.md
[/Sources]

## 6쪽 · 승강·기타 파형 (05:00–06:20, 80초)

[작성 예정] 승강과 속도 조절, 제동 버튼의 파형이다. 상승과 하강이 승강 모터의 방향 신호로 나타나는지, 속도 조절 버튼이 주행 신호의 듀티나 전압을 바꾸는지, 제동이 어떤 신호로 전달되는지 확인한다.

[Sources]
§2 버튼별 신호 측정: docs/references/week4_feedback.md
[/Sources]

## 7쪽 · 신호 해석 (06:20–07:40, 80초)

[작성 예정] 파형을 버튼별로 정리한 표이다. 버튼마다 어느 신호선이 바뀌는지, 그 신호가 단순 켜짐·꺼짐인지 PWM인지 직렬 통신인지, 그리고 그것이 무엇을 뜻하는지 적는다. 오른쪽 도식은 조종기에서 모터까지의 신호 경로와, 컴퓨터가 명령을 넣을 수 있는 지점을 보인다. 이 결과에 따라 기존 제어기를 살려 신호만 넣을지, 모터 드라이버로 제어기를 대체할지 정한다.

[Sources]
§2 리버스 엔지니어링: docs/references/week4_feedback.md
[/Sources]

## 8쪽 · 모터 드라이버 선정 (07:40–09:00, 80초)

모터 드라이버로는 TI의 DRV8244-Q1 SPI형을 골랐다. 왼쪽은 비교한 후보이다. 완성 보드인 VNH5019나 MD13S는 바로 쓸 수 있지만, 우리가 원하는 것은 컴퓨터가 모터 전류를 읽고 드라이버의 상태를 확인하는 것이다. DRV8244는 전류에 비례하는 신호를 IPROPI 핀으로 내보내므로, 션트 저항 없이 MCU의 ADC로 모터 전류를 읽을 수 있다. 이 값으로 바퀴가 막히거나 포크가 끝에 닿은 것을 알아낼 수 있다. SPI형은 전류 제한 크기와 과전류 임계값, 출력 전압이 바뀌는 속도를 설정할 수 있고, 어떤 결함이 났는지 레지스터로 읽을 수 있다. 전원은 4.5에서 35볼트까지라 12볼트 차체에 여유가 있다. 표에서 연속 전류와 보호 전류는 다른 값이다. DRV8244의 연속 전류는 TI가 85도 환경, 4층 기판, PWM 구동으로 계산한 열 해석값 4암페어로, 기판 방열에 따라 달라진다. 그래서 이 선정은 차체 모터의 전류를 잰 뒤 확정하며, 그 전류에 맞춰 전류 제한과 기판 방열을 설계한다.

[Sources]
DRV8244-Q1 데이터시트 SLVSG24C — 4.5–35 V, RON 47 mΩ(VQFN-HR), 출력 전류 Internally limited, OCP 21–40/15–31/10.5–24 A, ITRIP 7단계, fPWM ≤ 25 kHz, AIPROPI 4750 A/A, 표 7-1 DC 4.0 A (PWM, 85 °C, 40×40 mm 4층 2 oz), 주문 표 DRV8244SQRYJRQ1 = VQFN-HR(RYJ) 16: https://www.ti.com/lit/ds/symlink/drv8244-q1.pdf
BTS7960 제품 요약 — 전류 제한 43 A typ: https://www.infineon.com/dgdl/bts7960b-pb-final.pdf?fileId=db3a30431ed1d7b2011efe782ebd6b60
Pololu VNH5019 — 5.5–24 V, 12 A 연속, 30 A 최대, 약 140 mV/A: https://www.pololu.com/product/1451
Cytron MD13S — 6–30 V, 13 A 연속, 30 A 10 s: https://courses.ideate.cmu.edu/16-375/f2026/text/electronics/cy-md13s-driver.html
DRV8871 — 6.5–45 V, 3.6 A 피크: https://www.ti.com/lit/ds/symlink/drv8871.pdf
[/Sources]

## 9쪽 · 엔코더 선정 (09:00–10:10, 70초)

엔코더로는 자석식 각도 센서인 MT6701을 골랐다. 축 끝에 자석을 붙이고 그 위에 칩을 두면 접촉 없이 회전각을 잰다. 가장 큰 이유는 한 칩이 절대각과 증분 출력을 모두 낸다는 점이다. 조향축에 달면 전원을 켜자마자 현재 조향각을 알 수 있어 원점을 찾는 동작이 필요 없고, 바퀴 쪽에 달면 ABZ 출력을 MCU 타이머의 엔코더 모드로 바로 세어 속도를 잰다. 값도 1에서 2달러 수준이다. 비슷한 기능의 AS5047P가 정확도는 조금 낫지만, MT6701은 I2C와 아날로그 출력까지 있고 영점을 칩에 저장할 수 있다. 4주차에 엔코더 분해능은 10비트면 충분하다는 피드백을 받았다. MT6701은 14비트로 충분하고, 실제 성능은 분해능보다 최대 1.5도의 정확도와 자석을 얼마나 바르게 붙이는지가 좌우한다. 그래서 자석과 칩의 축 어긋남 0.3밀리미터 이하, 간격 0.5에서 2밀리미터를 지키는 브래킷을 설계한다. 어느 축에 몇 개를 달지는 조종기 신호 분석과 모터 구조를 확인한 뒤 정한다.

[Sources]
MT6701 데이터시트 Rev.1.5 — 14 bit, I2C·SSI·ABZ(≤1024 PPR)·UVW·아날로그·PWM, INL ±1.5° max, 자석 Ø6×2.5 mm·간격 0.5–2.0 mm·축 어긋남 ≤0.3 mm, 영점 EEPROM: https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf
LCSC 가격 $1.43–2.04: https://www.lcsc.com/product-detail/Angle-Linear-Position-Sensors_Magn-Tek-MT6701CT-STD_C2856764.html
AS5047P — 14 bit, SPI·ABI·UVW·PWM, 온도 포함 ±1°: https://www1.futureelectronics.com/doc/ams/AS5047P-ATSM.pdf
AS5048A/B — 14 bit, 온도 포함 ±1.2°: https://media.digikey.com/pdf/Data%20Sheets/Austriamicrosystems%20PDFs/AS5048A,B.pdf
AS5600 — 12 bit, 시스템 INL ±1°: https://files.seeedstudio.com/wiki/Grove-12-bit-Magnetic-Rotary-Position-Sensor-AS5600/res/Magnetic%20Rotary%20Position%20Sensor%20AS5600%20Datasheet.pdf
§4 엔코더 분해능 10 bit면 충분: docs/references/week4_feedback.md
[/Sources]
