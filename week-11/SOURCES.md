# 11주차 출처

쪽별 출처의 전체 목록은 `build_deck.py` 의 각 장 `sources` 와 발표자 노트의 [Sources] 블록이다(`SCRIPT.md` 에는 넣지 않는다).

장 번호: 2026-11-11 에 06 장(전력 · 제어 계통)을 넣어, 발주 장과 다음 주 장이 06 · 07 에서 07 · 08 이 되었다. 아래 번호는 지금 번호다.

## 로봇 저장소 (lightminn/forklift, main bcb21c87 기준)

| 자료 | 쓴 곳 |
|---|---|
| `docs/validation/2026-10-29-b-p2d-start-relocalization.md` 3–4절 | 02 장 표: 유효 84(시작 93 중 무효 9), 사람 개입 없이 확정 68/84 = 81.0 %, 틀림 · 부정확 0/0(시작 68), 원고의 위치 오차 중앙값 2.0 cm, 운용자 요청 16, 반복 선반 구역 |
| `docs/validation/2026-11-06-ct-status-survey.md` 요약 2 | 03 장 표: 운영 팔 O6 3/4 · O0 4/4(일자 line_m 4/4, 랜덤 random_m 3/4), 원고의 막은 실패(O6 random_m s0 두 번째 임무 근접 캡처) — 결정 모드 D · D′ 는 넣지 않음 |
| `docs/validation/2026-10-31-riib-default-batch2.md` (PR #237) | 04 장 표: trailer B 5/5 완주(seed 0–4) |
| `docs/validation/2026-10-31-riib-exit-prefix-default-batch.md` | 04 장 영상 후보 rx_B_trailer_s0(같은 설정의 앞 배치, trailer B 5/5, ws1 `tss_diag/rx_sum.json`) |
| `docs/validation/2026-11-04-return-cusp-replan-reregistration-results.md` | 05 장: 복귀 cusp 재계획 PASS, riib 기본 2 회 |
| `docs/validation/2026-11-02-return-cusp-replan-batch.md`, ws1 `test_runs/riibotics/tss_diag/rc_sum.json` | 05 장 영상 후보 rc_G_aisle_rack_s11(운반 124 s · 복귀 221 s 재계획, 완주) |

## 이전 주차

| 자료 | 쓴 곳 |
|---|---|
| `week-08/build_deck.py` 07 · 09 장 | 03 장 8주차 칸(③ 일자 5회 중 2회, ④ 랜덤 4회 중 1회 완주, 팔레트 하나 임무), 04 장 8주차 칸(⑤ 트레일러 꺼낸 뒤 운반 중 정지) |
| `week-09/assets/h03_layout_top.jpg` | 07 장 그림 |

## 사용자 · 총괄 전달

- 2026-11-10 승인 개요(쪽 구성, HW 는 "부품·PCB 발주 완료"만).
- 2026-11-10: 05 장은 넣는다, 07 장(발주) 일정은 "11월 20일 발송 예정"(도착일 아님).
- 2026-11-10 사용자 요청(게시 뒤): 07 장은 9주차에 설계한 보드 4종을 모두 발주(수량은 적지 않음) — 3D 렌더 · PCB 배치도와 보드별 하는 일 · 크기 표; 08 장은 보드가 다음 발표 전에 오지 않으므로 코어 보드로 펌웨어 먼저; 05 장은 재계획이 어디에서 어떻게 작동하는지 보이게.
- 2026-11-10 총괄: 02 장 시연 렌더는 F1 차단을 개발 설정으로 끈 실행(`F1_AUTONOMY=allow`, 시뮬 개발 실행 한정)이다. 화면 문구 "시작 위치를 스스로 찾고 출발"은 그대로 둔다. 스캔 겹침은 새 합성 없이 콘솔 화면 녹화(지도 위 LiDAR 점)로 대신하고, 후보 화면은 다시 찍는다.

## 영상

| 파일 | 원본 |
|---|---|
| `t04_trailer.mp4` | ws1 riib 배치 `rx_6e6d8e1c` 의 `rx_B_trailer_s0`(완주) `transport.mp4`, 보관본 `gdrive:forklift-archive/ws1-cleanup-20261031-a/t_mp4.tar.zst` 에서 꺼냄(md5 be3f7bb08a7826c04490d87581132191), 4배속 |
| `t05_replan.mp4` · `t05_overview.jpg` · `t05_key1–4.jpg` | ws1 riib 배치 `rc_95e61a74` 의 `rc_G_aisle_rack_s11`(완주; 복귀 cusp 대기 220.82 s, 위치 오차 0.020 m · 방향 오차 0.099 rad; 재계획 221.11 s, 계획 0.57 s) `transport.mp4`(md5 6bba6542ebf3b1039c3659f54de93f8a)와 `plan_history.json` · `result.json`, 보관본 `gdrive:forklift-archive/ws1-cleanup-20261110-n/n_rc.tar.zst` 에서 꺼냄. 기존 경로(204.7 s 계획, 주황)와 새 경로(221.1 s 계획, 하늘색)는 `make_replan.py` 가 다시 그린 선이다 |
| `r02_reloc.mp4` · `r02_console.mp4` | ws1 렌더 잡 17491 `d11_reloc_auto`: B-P2d seed 5 시작 val4_008 에서 사람 없이 위치 확정 뒤 P-1:D-1 done(시뮬 247 s). F1 차단을 개발 설정으로 끈 실행(`F1_AUTONOMY=allow`). 원본 md5 c903495b… · de4b0265… |
| `r02_candidates.png` | ws1 잡 17526 `d11_reloc_pick2`: val4_077(B-P2d 에서 운용자 요청), 후보 4개 화면(md5 266ff57d…) |
| `t03_queue.mp4` | ws1 잡 17491 `d11_queue_line`: line_m 대기열 세 임무 모두 done(시뮬 466 s), 원본 md5 43a5a03e… |

## 화면에 쓰지 않은 사실

- 03 장 8주차 수치는 riib 장면(line_1–3 · random_1–3)의 팔레트 하나 임무이고, 이번 수치는 line_m · random_m 세 임무 세션이다. 단위가 달라 표에 "1개씩" · "3개 연속"으로 나눠 적었다.
- 02 장의 시작 위치 찾기 검증(84곳)은 확정 뒤 10 s 정지까지이고, 출발 장면은 따로 찍는 시연 렌더다.

## 06 장 전력 · 제어 계통 (2026-11-11 사용자 요청 추가)

| 자료 | 쓴 곳 |
|---|---|
| 팀 EasyEDA 프로젝트 `Forklift` 의 Motor Board 회로도 — 온라인 프로젝트의 로컬 백업(2026-10-27 06:03 판)에서 POWER · JETSON_19V · MOTOR&SENSOR · STM32 쪽의 부품 · 네트 이름 · 설계자 주석을 읽음. 9주차에 받은 회로도(10-28 전달본, 9주차 SOURCES.md)와 같은 구성 | 전원 띠(12 V 배터리 → 메인보드 전원부 → 12 V 모터 드라이버 · 5 V STM32H743 코어 보드와 센서 보드 · 19 V Jetson), 드라이버 4채널(L · R 바퀴, M 조향, H 승강), MCU 로 드나드는 신호(PWM · 방향, 전류 · 고장, 엔코더 펄스 · SPI 각도) |
| 로봇 저장소 `docs/interfaces/2026-10-22-mcu-link-contract.md` (초안, 실기기 미검증) | Jetson → MCU 목표값(좌우 바퀴 각속도, 조향각, 승강 위치), MCU → Jetson 측정값 · 상태(엔코더, 조향각, 승강 위치, 모터 전류, 결함), 명령 마감이 지나면 정지, 전송로(USB CDC 또는 UART) 미정 |
| 로봇 저장소 `docs/design/2026-10-22-mcu-firmware-core.md`, `firmware/README.md` | 하위 제어가 맡는 일(바퀴 속도 제어, 조향 · 승강 위치 제어), 지금은 보드 무관 C 코어와 호스트 시험만 있음(띠의 진행 상태) |
| 로봇 저장소 `docs/hardware.md` | RealSense D435i, RPLIDAR A2M12, Jetson, STM32H743VIT6 (WeAct Studio MiniSTM32H7xx) |
| `week-07/build_deck.py` 01 · 02 장 | 계통도 문법(전압별 색, 점선 = 측정값), 채널과 엔코더 종류 |
| `week-08/build_deck.py` 02 장 | 운용 콘솔은 Jetson 이 Wi-Fi AP 가 되어 연결 |
| `week-09/build_deck.py` 04 장 | 9주차에 이미 발표한 전원 경로와 보호 회로 — 이 장에는 세 갈래 분배만 두고 세부는 되풀이하지 않음(사용자 2026-11-11: 지난 발표와 겹치지 않게) |

화면에 쓰지 않은 것: 퓨즈 · 입력 보호 문턱 · 전류 제한 값(9주차 04 장에 있음), 펌웨어 상태기의 단계 이름, 제어 주기(설정값이고 정해지지 않음). 카메라와 LiDAR 의 전원 · 인터페이스는 실기 확인 전이라 전압 배지를 달지 않았다. EasyEDA 백업은 2026-10-27 판이고, 그 뒤 발주(11-10)까지 회로가 바뀌었는지는 확인하지 못했다 — 발주 장(07 장)이 "9주차에 설계한 보드 4종"이라고 적은 것을 따랐다.

## 07 · 08 장 발주 · 다음 주 (2026-11-10 사용자 요청 수정)

| 자료 | 쓴 곳 |
|---|---|
| `week-09/build_deck.py` 02–05 장 | 07 장 표: 메인보드 구성(H743 코어 보드, DRV8244 4채널, 12 V · 5 V · Jetson 19 V 전원), 보드 크기(메인보드 114.2 × 91.6, MT6701 · KTH7801 22.8 × 10.4, STDS 32.6 × 18.4 mm) |
| `week-07/build_deck.py` | 07 장: STDS 보드가 KTH7801 의 SPI 를 LVDS 로 메인보드까지 전송 |
| 로봇 저장소 `docs/references/team-hardware/2026-10-28/` (로컬 전용) | 07 장 그림의 원본(3D 렌더 · PCB 배치도), 보드 4종 |
| 로봇 저장소 PR #84 | 08 장 펌웨어: 보드 무관 C 코어 · mcu-link/1, 보드 HAL · 툴체인은 시작 전 |
| `week-08/build_deck.py` 06 장 | 08 장: 남은 리보틱스 장면(① 좁은 통로 rack, ② 컨베이어) |
| `docs/validation/2026-11-06-ct-status-survey.md` | 08 장: 랜덤 배치 남은 실패(두 번째 팔레트 앞 근접 캡처 후보 없음) |
