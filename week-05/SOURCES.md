# 5주차 자료 출처

## 화면을 만든 것

| 만든 것 | 쓰인 곳 | 성격 |
|---|---|---|
| 자리 표시 | 차체 실측 · 포크·동봉 팔레트 | 팀 측정 자료가 들어오면 교체 |
| **로직 애널라이저 파형** | 명령별 파형 · 파형 해석 | 팀 DSLogic Pro 캡처 3개(2026-09-30, 1 MHz, 2채널: 주행 앞뒤앞뒤 · 승강 상승하강상승하강 · 조향 왼오왼오)를 `prepare_la.py` 로 엣지만 추출해 그림 |
| 리버스 엔지니어링 결론 | 리버스 엔지니어링 결과 | 팀 보고(2026-09-30): 전원 스위치 +·V 직결, RF 메인보드 통합, 릴레이 구동, PWM·속도 조절 없음, DRV8244 SPI 로 신규 개발 |
| **실물 사진** | 조종기 신호 측정 구성 | 2026-09-23 입고 사진(4주차 `05_remote.jpg`, `04_controller_label.jpg`, EXIF 제거본) |
| 비교 표 | 하드웨어 선정 두 장 | 제조사 데이터시트·제품 페이지 값. 출처는 각 장 원고의 [Sources] |

## 수치

| 수치 | 값 | 출처와 정의 |
|---|---|---|
| 잠정 모델 치수 | 차체 실측 표의 오른쪽 열 | `sim/models/dls08_provisional/parameters.yaml` — 카탈로그 값과 사진 비례 추정 |
| 파형 수치 | 주행 앞 1.02·0.78 s, 뒤 1.24·2.40 s · 승강 상승 0.70·0.75 s, 하강 0.72·0.62 s · 조향 왼쪽 0.56 s · 누름 순간 두 채널 동시 High 2.95–3.43 ms (주행) · 명령 구간 내 엣지 0 | `assets/data_la_edges.json`. 조향 CSV 는 7.72–16.69 s 구간만 포함 |
| DRV8244SQRYJRQ1 | SPI(S)형 · VQFN-HR(RYJ) 16핀 | [데이터시트 SLVSG24C](https://www.ti.com/lit/ds/symlink/drv8244-q1.pdf) 주문 표·표 5-1 |
| DRV8244-Q1 전원·저항 | 4.5–35 V · RON_LS+RON_HS 47 mΩ (VQFN-HR) | 같은 문서 §1·전기 특성 |
| DRV8244-Q1 전류 | 출력 전류 "Internally limited" · OCP 21–40 / 15–31 / 10.5–24 A 선택(SPI형) · ITRIP 7단계 | 같은 문서 절대최대정격·SPI 레지스터. 표 5-1 의 IOUT 21 A 는 제품군 비교값 |
| DRV8244-Q1 연속 전류 | DC 4.0 A (PWM) | 같은 문서 표 7-1: 85 °C 주위, 40 × 40 mm 4층 PCB(외층 2 oz) 열 해석, 접합 150 °C 까지. 실측 아님 |
| DRV8244-Q1 기타 | fPWM ≤ 25 kHz · AIPROPI 4750 A/A (VQFN-HR) | 같은 문서 전기 특성 |
| MT6701 | 14 bit · ABZ ≤ 1024 PPR · INL ±1.5° max · 자석 간격 0.5–2.0 mm · 축 어긋남 ≤ 0.3 mm | [데이터시트 Rev.1.5](https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf). 판마다 값이 달라 최신판 기준 |
| 우리 임무 절차 | 접근 0.60 · 삽입 0.055 · 운반 0.30 m/s · 들기 0.20 m · 삽입 깊이 360 mm · 틸트 관절 없음 | `config/isaac_transport.yaml`, `sim/isaac/run_transport.py` 단계 전환, 잠정 URDF, 삽입 깊이 규칙(로봇 저장소 CLAUDE.md). 시뮬레이터 설정값 |
| 표준 작업 절차 | 들기 5–10 cm · 당김 10–20 cm · 운반 시 포크 약 15–20 cm · 구내 10 km/h 이하 | KOSHA 지게차 교육자료, 산업안전보건기준에 관한 규칙 제98·99·172·173·179조. 사람이 타는 실제 지게차 기준 |
| 비교 후보 | BTS7960 · VNH5019 · MD13S · DRV8871 · AS5600 · AS5048 · AS5047P | 각 장 원고 [Sources] 의 제조사·판매처 자료 |
