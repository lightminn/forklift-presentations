# 7주차 자율 지게차 개발 · 발표 원고

12장 · 시간 배분 합계 10분 40초. 쪽별 배정 시간은 발표 연습 후 조정한다.

기준일: 2026-10-14. 하드웨어만 다룬다. 보드는 회로와 PCB 설계 단계이며 아직 제작 · 측정하지 않았다. 칩 수치는 데이터시트 값이고, 클럭 한계와 전압 여유는 그 값으로 계산한 최악값이다. 원고는 발표자 문체(합니다체)로 썼고, (전환)은 다음 쪽으로 넘기는 자리다.

## 1쪽 · 개발 진행 보고 (00:00–00:25, 25초)

안녕하십니까. 7주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 주에는 하드웨어만 다루겠습니다. 전원과 제어 구성을 먼저 보이고, 모터 드라이버와 엔코더를 MCU에 잇는 보드 네 종류의 회로와 PCB, 엔코더 신호를 케이블로 멀리 보내기 위해 차동 전송을 고른 근거와 클럭 속도 계산, 전원과 커넥터를 말씀드린 뒤, 결론과 향후 작업으로 마치겠습니다. (전환)

[Sources]
diagram · mainboard_1 · mt6701_1–3 · kth7801_1–3 · stds_1–3: 팀 EasyEDA 자료 (2026-10-14)
[/Sources]

## 2쪽 · 전원과 제어 구성 (00:25–01:20, 55초)

전체 전원과 제어 구성입니다. 차량의 주 전원은 12볼트 납축 배터리입니다. 아래쪽 모터 구동 전원은 12볼트를 그대로 DRV8244 네 개에 넣고, 드라이버가 바퀴 두 개와 조향, 승강 모터를 구동합니다. 위쪽 제어와 센서 전원은 먼저 벅 컨버터로 12볼트를 5볼트로 낮춰 MCU 보드인 Nucleo STM32H533RE에 주고, 같은 5볼트를 케이블로 센서 보드까지 보내 각 보드의 LDO에서 3.3볼트로 한 번 더 낮춥니다. 엔코더 네 개는 모두 자석의 회전을 재는 자기식이고, 바퀴는 ABZ 펄스, 조향과 승강은 SPI로 MCU에 각도를 알려 줍니다. MCU는 PWM과 방향 신호, SPI 설정, 출력 차단 신호로 드라이버를 제어합니다. (전환)

[Sources]
기계차 전력 계통 및 제어 블록 다이어그램 — 12 V 납축 배터리, 12 V → 5 V 벅, 5 V → 3.3 V LDO, Nucleo STM32H533RE, 엔코더 MT6701 · KTH7801, DRV8244/DRV8245, 구동 · 조향 모터: 팀 EasyEDA 자료 (2026-10-14) diagram.png
「TKH7801」→ KTH7801; KTH7801은 광학식이 아니라 홀 소자 자기식 (KTH7801 데이터시트 「Hall magnetic encoders」); 피드백에서 PWM 제외 (두 보드 모두 PWM 핀 미사용); 드라이버는 회로도대로 DRV8244 × 4; 모터에 승강 추가 (채널 H): 다시 그리며 고친 곳
DRV8244SQRYJRQ1 × 4 (L · R · M · H), 커넥터 5V 공급: 팀 EasyEDA 자료 (2026-10-14) mainboard_1.png
「16-bit Programmable non-contact Hall magnetic encoders」: https://shop.mev-elektronik.com/wp-content/uploads/KTH7801_datasheet_EN.pdf
[/Sources]

## 3쪽 · 보드 구성과 신호 경로 (01:20–02:15, 55초)

보드 사이의 연결입니다. 왼쪽은 메인보드 회로도의 모터와 센서 쪽 1쪽입니다. 바퀴 두 개에 단 MT6701 보드는 1.27밀리미터 2열 4핀 케이블로 메인보드에 바로 이어지고, A, B, Z 펄스와 그 반전 신호를 메인보드의 RS-422 수신기 AM26LV32가 받아 MCU 타이머의 엔코더 모드로 셉니다. 차동 수신기는 두 선의 전압 차이만 보므로, 모터 잡음처럼 두 선에 똑같이 실린 잡음은 빼기에서 사라집니다. 조향과 승강에 단 KTH7801 보드는 SPI로 각도 값을 내보내는데, SPI는 원래 한 보드 안에서 쓰는 단일 종단 신호라 먼 거리를 못 갑니다. 그래서 바로 옆에 STDS 보드를 두어 SPI 네 선을 LVDS 차동 신호로 바꾸고, RJ50 케이블로 메인보드에 보냅니다. 메인보드는 SN65LVDS31로 클럭과 데이터를 보내고 SN65LVDS32로 돌아오는 데이터를 받습니다. 전원은 모든 케이블에 5볼트로 실어 보내고 센서 쪽 보드에서 3.3볼트로 낮춥니다. (전환)

[Sources]
DRV8244SQRYJRQ1 × 4 (L · R · M · H 신호 이름), AM26LV32EIPWR U3 · U5, HX JN1.27-2x4P CN1 · CN2 (5 V · AGND · L/R_DA · DB · DZ와 반전), SN74LVC1G125DBVR U9 · U10, SN65LVDS31DR U6 · U7, SN65LVDS32DR U8, 5558067-1 RJ1 · RJ2: 팀 EasyEDA 자료 (2026-10-14) mainboard_1.png
센서 쪽 TLV70233DBVR (VCC → 3V3), CN1 HX JN1.27-2x4P, STDS RJ1 5558067-1: 팀 EasyEDA 자료 (2026-10-14) mt6701_3 · kth7801_3 · stds_1
차동 신호 기반 통신, 5 V로 보내 3.3 V LDO로 강하, RJ50 선택: 사용자 (2026-10-14)
[/Sources]

## 4쪽 · 모터 드라이버 4채널 (02:15–03:05, 50초)

모터 드라이버입니다. 지난번 초안은 세 채널이었는데, 바퀴를 왼쪽과 오른쪽으로 나눠 L, R, 조향 M, 승강 H의 네 채널로 늘렸습니다. 드라이버는 5주차에 고른 TI의 DRV8244 SPI형이고, 왼쪽 회로가 그중 L 채널입니다. 네 채널은 회로가 같고, 설정과 결함 확인에 쓰는 SPI의 MISO, MOSI, 클럭은 네 개가 함께 쓰며 칩 선택 CS만 채널마다 따로 둡니다. 모터의 방향과 속도는 IN1, IN2에 PWM을 넣어 정하고, DRVOFF 핀은 출력을 바로 끊는 핀이라 비상정지와 연결합니다. nFAULT로 결함을 알리고, IPROPI 핀으로 모터 전류를 전압으로 바꿔 MCU의 ADC로 읽습니다. (전환)

[Sources]
DRV8244SQRYJRQ1 × 4: 공유 MISO · MOSI · CLK, 채널별 x_CS(2.2 kΩ 풀업) · x_IN1 · x_IN2 · x_DRVOFF · x_SLEEP · x_FAULT(2.2 kΩ 풀업) · x_IPROPI(10 nF), VM 10 µF + 100 nF: 팀 EasyEDA 자료 (2026-10-14) mainboard_1.png
채널 L · R 바퀴, M 조향, H 승강: 사용자 (2026-10-14)
DRV8244-Q1 SLVSG24C — SPI 설정 · 진단, DRVOFF, IPROPI 전류 출력: https://www.ti.com/lit/ds/symlink/drv8244-q1.pdf
DRVOFF를 무선 비상정지와 연동할 예정: week-07-1 15쪽
[/Sources]

## 5쪽 · 엔코더 배치와 칩 선정 (03:05–04:00, 55초)

엔코더 배치입니다. 5주차에는 MT6701 한 칩으로 증분과 절대를 모두 하려 했는데, 절대 엔코더는 KTH7801로 바꿨습니다. 바퀴 두 개에는 MT6701을 달아 한 바퀴에 1,024개 나오는 A, B 펄스를 MCU 타이머로 세어 속도와 이동 거리를 잽니다. 조향과 승강에는 KTH7801을 다는데, 전원을 켜자마자 현재 각도를 SPI로 읽을 수 있어 원점을 찾는 동작이 필요 없습니다. 데이터시트의 비선형 오차 대표값은 MT6701이 ±1도, KTH7801이 ±0.35도로, 조향각처럼 각도 값 자체를 쓰는 곳에 KTH7801이 더 맞습니다. 쓰는 KTH7801 품번은 CRC가 붙는 판이라, SPI로 읽을 때 12비트 각도와 4비트 검사값이 함께 옵니다. (전환)

[Sources]
「absolute는 KTH7801 이거쓸거임」, MT6701 · KTH7801 보드 구별: 사용자 (2026-10-14)
MT6701 Rev.1.5 — INL ±1.0° 대표 · ±1.5° 최대, 14비트, ABZ 1–1024 PPR: https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf
MT6701 1.9판(2024-05) 주문 정보 — MT6701QT-ACD: AB 1,024펄스/회전, Z 1 LSB, UVW = -A-B-Z: https://atta.szlcsc.com/upload/public/pdf/source/20260616/FEB700C1922508565884FF0A90656B50.pdf
KTH7801 Series (2024-09-27) — 16비트 절대각, 비선형 오차 ±0.35°(대표), SOP-8 = SPI · PWM, KTH7801-X-C-SOP8 = CRC 판, 5.6절 SPI CRC 프레임 12비트 각도 + CRC-4: https://shop.mev-elektronik.com/wp-content/uploads/KTH7801_datasheet_EN.pdf
5주차 엔코더 선정: MT6701로 증분 · 절대 모두: week-05/build_deck.py 6쪽
[/Sources]

## 6쪽 · 엔코더 보드 두 종 (04:00–05:00, 60초)

엔코더 보드 두 종류의 회로도입니다. 왼쪽은 바퀴에 다는 MT6701 보드입니다. 칩은 QFN 패키지의 MT6701QT-ACD인데, 이 품번은 공장에서 U, V, W 핀이 A, B, Z의 반전 신호를 내도록 설정되어 나오므로, 따로 프로그래밍하지 않아도 세 쌍의 차동 신호가 나오고 보드에 차동 드라이버 칩을 둘 필요가 없습니다. 오른쪽은 조향과 승강에 다는 KTH7801 보드로, SOP-8 칩 하나와 레귤레이터만 있고 SPI 네 선과 전원, 접지만 커넥터로 나갑니다. KTH7801의 SPI는 클럭이 쉴 때 High인 모드 3이고, 한 번에 16비트를 주고받는데 이 품번은 그중 12비트가 각도, 4비트가 CRC입니다. 칩 선택 선은 2.2킬로옴으로 풀업해 MCU가 켜지기 전에는 선택되지 않게 했습니다. 두 보드 모두 뒷면에 커넥터와 레귤레이터가 있어, 케이블로 받은 5볼트를 3.3볼트로 낮춰 칩에 줍니다. (전환)

[Sources]
MT_DS V1.0.0: U1 MT6701QT-ACD(VQFN16) — 6 A · 7 B · 8 Z, 11 U → A\, 12 V → B\, 9 W → Z\, 14 MODE → GND, 13 VDD 3V3, C3 1 µF · C1 100 nF; U2 TLV70233DBVR VCC → 3V3, C2 · C4 1 µF; CN1 HX JN1.27-2x4P 1 VCC · 2 GND · 3 A · 4 A\ · 5 B · 6 B\ · 7 Z · 8 Z\: 팀 EasyEDA 자료 (2026-10-14) mt6701_1–3
KTH_Enc V1.1.2: U2 KTH7801-X-C-SOP8 — 1 TEST NC, 2 MOSI, 3 CS(R4 2.2 kΩ → 3V3), 4 MISO, 5 GND, 6 PWM NC, 7 SCLK, 8 VDD(C1 100 nF · C2 1 µF); U1 TLV70233DBVR; CN1 1 VCC · 2 CS · 4 CLK · 6 MOSI · 7 GND · 8 MISO, 3 · 5 NC: 팀 EasyEDA 자료 (2026-10-14) kth7801_1–3
QFN-16 핀 표: ABZ Differential 열 — 9 -Z, 11 -A, 12 -B (UVW_MUX = 1): https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf
주문 정보: MT6701QT-ACD UVW = -A-B-Z 출고 설정: https://atta.szlcsc.com/upload/public/pdf/source/20260616/FEB700C1922508565884FF0A90656B50.pdf
Table 2 SOP-8 핀 (TEST 띄움), SPI CPOL = 1 · CPHA = 1 · 16비트 프레임, 5.6절 CRC 프레임 12비트 각도 + CRC-4: https://shop.mev-elektronik.com/wp-content/uploads/KTH7801_datasheet_EN.pdf
[/Sources]

## 7쪽 · 차동 전송이 필요한 이유 (05:00–05:55, 55초)

차동 전송을 고른 근거입니다. TI가 SPI를 LVDS로 보내는 레퍼런스 디자인에서, 케이블에 1볼트 피크 투 피크 잡음을 주파수를 바꿔 가며 넣고 SPI로 받은 ADC 값의 신호 대 잡음비를 잰 결과입니다. 회색은 보통 SPI, 파란색은 LVDS입니다. 0.5미터에서는 잡음이 없을 때 둘 다 101데시벨이지만, 잡음 주파수가 10메가헤르츠까지 올라가면 보통 SPI는 31데시벨, LVDS는 52데시벨로 차이가 커집니다. 더 중요한 것은 3미터입니다. 빨간 X처럼 보통 SPI는 잡음이 없어도 3미터에서는 통신 자체가 되지 않았고, LVDS는 잡음이 있어도 45데시벨 이상을 유지했습니다. 차체에서 메인보드와 조향, 승강 축 사이에 케이블이 지나가고 모터 잡음도 있으므로, SPI는 LVDS로, 바퀴 엔코더는 RS-422 수신기로 받는 차동 방식으로 정했습니다. (전환)

[Sources]
TI TIDA-060017 (TIDUED8, 2018-07) 3.2.1.1 Noise Immunity Test · Table 4 — 1 Vpp 잡음, ADS8910B를 SPI 슬레이브로 2 kHz 사인 입력의 SNR, CAT5 케이블, SN65LVDS31/33 EVM; 단일 종단 3 m는 모든 행 Fail「Single-ended SPI application cannot support 3m cable length」: https://www.ti.com/lit/ug/tidued8/tidued8.pdf
spi.png(같은 표) 참고, 「노이즈가 없다고 가정해도 3M만 가도 신호 전송이 거의 안되는 것을 확인」: 사용자 (2026-10-14)
[/Sources]

## 8쪽 · STDS 보드와 메인보드 LVDS (05:55–06:55, 60초)

KTH7801 바로 옆에 두는 STDS 보드입니다. STDS는 단일 종단 신호를 차동 신호로 바꾼다는 뜻의 Single-ended To Differential Signal을 줄인 이름입니다. 메인보드에서 LVDS로 오는 클럭, MOSI, 칩 선택 세 쌍을 SN65LVDS32 수신기가 받아 보통 SPI 신호로 바꿔 KTH7801에 넘기고, KTH7801이 내는 MISO는 SN65LVDS1 송신기가 다시 LVDS로 바꿔 돌려보냅니다. 메인보드 쪽은 SN65LVDS31이 센서마다 클럭, MOSI, 칩 선택을 보내고, 돌아오는 MISO 두 쌍은 SN65LVDS32가 받습니다. MCU의 MISO 핀은 하나라서, 버퍼 SN74LVC1G125의 출력 허용 핀에 칩 선택을 연결해 선택된 센서의 MISO만 통과시킵니다. 수신 쪽 차동 선 사이에는 100옴 종단 저항을 답니다. 선 길이가 신호 파장의 10분의 1을 넘으면 전송선로로 보고 끝에서 반사되지 않게 임피던스를 맞춰야 하는데, 꼬임쌍 케이블에서 신호는 나노초에 약 20센티미터를 가므로 클럭 10메가헤르츠 기준으로는 2미터가 경계입니다. 하지만 KTH7801 출력의 상승 시간 10나노초를 흔히 쓰는 0.35 나누기 상승 시간으로 환산하면 약 35메가헤르츠라, 약 0.6미터부터 전송선로입니다. (전환)

[Sources]
STDS = Single-ended To Differential Signal (사용자 2026-10-14); STDS V1.0.0: U8 SN65LVDS32DR (1A/1B CLK, 2A/2B MOSI, 4A/4B CS → CLK · MOSI · CS), R1–R3 100 Ω (D–D\ 사이), U2 SN65LVDS1DBVR (MISO → MISO_D · MISO_D\), U1 TLV70233DBVR, CN1 HX JN1.27-2x4P, RJ1 5558067-1: 팀 EasyEDA 자료 (2026-10-14) stds_1–3
U6 · U7 SN65LVDS31DR: KTH_CLK · KTH_MOSI · KTH_CS1/2 → 차동; U8 SN65LVDS32DR: KTH_MISO1/2_D → KTH_MISO1/2; U9 · U10 SN74LVC1G125DBVR: OE ← KTH_CS1 · KTH_CS2 (2.2 kΩ 풀업), Y → KTH_MISO: 팀 EasyEDA 자료 (2026-10-14) mainboard_1.png
SN65LVDS32 — 4채널 LVDS 수신, 내부 종단 없음(외부 100 Ω): https://www.ti.com/lit/ds/symlink/sn65lvds32.pdf
SN65LVDS1 — 1채널 LVDS 송신, 100 Ω 선로용: https://www.ti.com/lit/ds/symlink/sn65lvds1.pdf
SN74LVC1G125 — OE Low일 때 출력, High면 고임피던스: https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf
전기적 길이 = 주파수 × 선 길이 / 전파 속도, 0.1(λ/10) 초과 시 전송선로; 꼬임쌍 약 20 cm/ns; 10 MHz · 2 m → 0.1: 사용자 메모 (2026-10-14)
KTH7801 TR 10 ns(Table 9) → 0.35 / tr ≈ 35 MHz → λ/10 ≈ 0.57 m (경험식): 계산
[/Sources]

## 9쪽 · MISO 왕복 지연과 최대 SCLK (06:55–07:55, 60초)

그러면 클럭은 얼마까지 올릴 수 있을까요. MOSI와 칩 선택은 클럭과 같은 방향으로 함께 가므로, 네 쌍의 선 길이를 맞춰 도착 시간 차이만 줄이면 됩니다. 문제는 MISO입니다. MCU가 클럭을 보내면 그 클럭이 케이블을 지나 센서에 닿고, 센서가 데이터를 내면 그 데이터가 다시 케이블을 지나 돌아와야 합니다. KTH7801은 모드 3이라 MCU는 클럭 반 주기 뒤에 MISO를 읽으므로, 이 왕복이 반 주기 안에 끝나야 합니다. 왼쪽 표는 이 경로의 칩마다 데이터시트 최대 지연을 더한 것으로, 칩만 65.3나노초이고 그중 50나노초가 KTH7801의 출력 지연입니다. 케이블은 1미터당 왕복 10나노초씩 늘어납니다. 이렇게 계산하면 케이블이 없어도 약 7.7메가헤르츠, 1미터에서 약 6.6, 3미터에서 약 5.2메가헤르츠가 한계입니다. SPI를 멀리 보내는 전용 칩인 아날로그 디바이스의 LTC4332도 10미터에서 클럭을 2메가헤르츠로 잡고 있습니다. 모두 최악값 기준이고 MCU의 입력 준비 시간은 빠져 있으므로, 실제 케이블 길이를 정한 뒤 이보다 낮게 잡고 실측으로 확인하겠습니다. (전환)

[Sources]
Table 9 TDV ≤ 50 ns (MISO 유효, 20 pF), SPI CPOL = 1 · CPHA = 1: https://shop.mev-elektronik.com/wp-content/uploads/KTH7801_datasheet_EN.pdf
SN65LVDS31 8.8 Switching (SN65LVDSxxxx) tPHL 최대 2.5 ns: https://www.ti.com/lit/ds/symlink/sn65lvds31.pdf
SN65LVDS32 8.8 tPLH · tPHL 최대 3 ns: https://www.ti.com/lit/ds/symlink/sn65lvds32.pdf
SN65LVDS1 6.7 Driver Switching tPLH · tPHL 최대 3.1 ns: https://www.ti.com/lit/ds/symlink/sn65lvds1.pdf
SN74LVC1G125 5.6 tpd 최대 3.7 ns (3.3 V ± 0.3 V, 15 pF): https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf
칩 합 65.3 ns, 케이블 20 cm/ns → 왕복 10 ns/m, f_max = 1 / (2 × (칩 합 + 왕복)) → 0 m 7.66 MHz, 1 m 6.64 MHz, 2 m 5.86 MHz, 3 m 5.25 MHz, 5 m 4.34 MHz (MCU 입력 준비 시간 제외, 최악값): 계산
Analog Devices LTC4332 SPI 연장 칩 — 「2MHz SCK Over 10m, Operation Up to 1200m」 (사용자가 보낸 기능 목록과 같음): https://www.analog.com/en/products/ltc4332.html
MOSI · MISO · SCLK · nCS 길이를 맞춰 skew 최소화, MISO는 역방향이라 왕복 지연이 최대 속도를 제한: 사용자 메모 (2026-10-14)
[/Sources]

## 10쪽 · 전원과 커넥터 (07:55–08:50, 55초)

전원과 커넥터입니다. 센서 칩은 MT6701과 KTH7801 모두 최저 3.0볼트에서 동작합니다. 3.3볼트를 메인보드에서 그대로 보내면 케이블과 커넥터에서 0.3볼트만 떨어져도 최저 전압에 닿습니다. 그래서 전원은 5볼트로 보내고 각 센서 보드의 LDO 레귤레이터 TLV70233에서 3.3볼트로 낮춥니다. 이 레귤레이터는 최대 부하 300밀리암페어에서도 입력이 출력보다 0.375볼트만 높으면 되므로, 1.3볼트 가까이 떨어져도 센서에는 3.3볼트가 일정하게 갑니다. KTH7801 쪽 케이블에는 차동 네 쌍과 5볼트, 접지까지 열 가닥이 필요한데, 랜선의 RJ45는 8핀이라 전원 자리가 없고, 일반 핀 헤더는 차동 신호용이 아니어서 커넥터 구간의 임피던스를 따로 따져야 합니다. 그래서 RJ45를 10핀으로 늘린 같은 계열의 RJ50을 골랐고, 왼쪽 아래 표처럼 1번부터 8번까지 네 쌍, 9번에 5볼트, 10번에 접지를 두었습니다. (전환)

[Sources]
「3.3V 역시 길게 가면 전압 강하가 예상되므로 5V로 보내서 3.3V LDO로 강하」, 「다른 선들은 솔직히 차동신호용으로 개발된것도 아니여서 커낵터의 임피던스를 고려해봐야하는데 … RJ45의 확장판으로 나온 RJ50」: 사용자 (2026-10-14)
RJ1 · RJ2 5558067-1: 1/2 KTH_CLK_D · D\, 3/4 KTH_MOSI_D · D\, 5/6 KTH_CSx_D · D\, 7/8 KTH_MISOx_D · D\, 9 5V, 10 GND, 11 · 12 GND: 팀 EasyEDA 자료 (2026-10-14) mainboard_1.png
TLV70233DBVR VCC → IN · EN, OUT 3V3, C 1 µF × 2 (세 보드 같은 구성); STDS RJ1 같은 핀 배정: 팀 EasyEDA 자료 (2026-10-14) mt6701_3 · kth7801_3 · stds_1
TLV702 — IOUT 0–300 mA, VDO 최대 375 mV (300 mA): https://www.ti.com/lit/ds/symlink/tlv702.pdf
MT6701 VDD 3.0–5.5 V: https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf
KTH7801 Table 7 동작 전압 최소 3.0 V (3.3 V 판): https://shop.mev-elektronik.com/wp-content/uploads/KTH7801_datasheet_EN.pdf
3.3 − 3.0 = 0.3 V; 5 − 3.3 − 0.375 ≈ 1.3 V: 계산
[/Sources]

## 11쪽 · 커넥터 핀 간격 질문 (08:50–09:45, 55초)

여쭤보고 싶은 것이 있습니다. 엔코더 보드의 커넥터 핀 간격입니다. 위는 KTH7801 보드를 2.54밀리미터 커넥터로 그린 이전 판이고, 아래는 1.27밀리미터로 바꾼 판입니다. 2.54밀리미터 판은 뒷면 커넥터가 보드보다 크게 튀어나와 있습니다. 1.27밀리미터로 바꾸면 커넥터가 가로세로 절반 정도로 줄어 보드를 작게 만들 수 있고, 지금 최종 파일은 모두 1.27밀리미터로 그렸습니다. 다만 납땜이 까다롭고 맞는 케이블의 선택지가 적습니다. 2.54밀리미터는 크지만 손납땜이 쉽고 박스 헤더용 납작 케이블을 쉽게 구할 수 있습니다. 실차에 달 때 어느 쪽이 나은지 의견 부탁드립니다. (전환)

[Sources]
KTH7801 보드 2.54 mm 판 앞 · 뒷면, 1.27 mm 판(V1.0.1, 실크 KTH_Enc) 3D 앞면과 배치도 — 사용자 확인: 두 판 모두 KTH7801 보드: 팀 PCB 3D 렌더 (2026-10-14, 팀원 공유)
최종 파일 MT_DS V1.0.0 · KTH_Enc V1.1.2 · STDS V1.0.0 · 메인보드 모두 HX JN1.27-2x4P: 팀 EasyEDA 자료 (2026-10-14)
「교수님에게 2.54 VS 1.27 물어보죠」: 팀 메시지 (2026-10-14)
2.54 vs 1.27 그림까지 넣어 질문 유지: 사용자 (2026-10-14)
1.27 mm 는 2.54 mm 의 절반 간격 — 같은 핀 수면 커넥터 가로 · 세로가 약 절반 (기하 계산, 하우징 두께 제외): 비교 표
[/Sources]

## 12쪽 · 결론 및 향후 작업 (09:45–10:40, 55초)

결론과 향후 작업입니다. 이번 주에는 전원과 제어 구성을 정해 모터는 12볼트를 바로 쓰고 MCU와 센서는 5볼트와 3.3볼트로 나눠 받게 했고, 모터 드라이버는 DRV8244 네 채널로 바퀴 두 개와 조향, 승강을 구동합니다. 엔코더는 바퀴에 MT6701 증분 엔코더, 조향과 승강에 KTH7801 절대 엔코더를 쓰고, 신호는 바퀴 펄스는 RS-422로, SPI는 STDS 보드에서 LVDS로 바꿔 차동으로 보냅니다. 앞으로는 모터 전류를 실측해 드라이버의 전류 제한을 정하고, 메인보드 PCB를 배치해 중간고사 뒤에 제작하겠습니다. 엔코더 쪽 보드는 핀 간격을 정한 뒤 제작하고, 자석과 칩의 축을 맞추는 브래킷을 함께 만들겠습니다. SPI 클럭은 케이블 길이를 정한 뒤 오늘 계산한 한계보다 낮게 잡고 실제로 재 보겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.

[Sources]
10/16–22 모터 전류 실측 · PCB 설계, 10/30–11/12 구동 보드 제작: week-07-1 17쪽 일정
자석과 칩의 축 어긋남 0.3 mm 이하, 간격 0.5–2 mm를 지키는 브래킷 설계: week-05/build_deck.py 6쪽
케이블 길이별 최대 SCLK (최악값): 9쪽 계산
[/Sources]
