# 8주차 출처

쪽별 출처의 전체 목록은 `build_deck.py` 의 각 장 `sources` 와 발표자 노트의 [Sources] 블록이다(`SCRIPT.md` 에는 넣지 않는다).

## 로봇 저장소 (lightminn/forklift, main 4b65404 기준)

| 자료 | 쓴 곳 |
|---|---|
| `docs/design/2026-10-13-operator-console.md` | 1절 목적(감시 · 지시 · 수동 조종), 2절 결정(웹 앱 + 로봇 쪽 게이트웨이, Jetson AP 1:1, 실차와 Isaac 같은 ROS 2 스택), 3절 구조도(2쪽에 안전 계층을 빼고 다시 그림), 8절 화면 요구(폰 세로 배치, 지도 · 차량 상태 항목, 측정 장치 없음 표시) |
| `console/README.md` | FMS 형식 화면 구성, 작업 지정 3단계, 지도 조작(끌기 · 확대 · 따라가기 · 표시 층) |
| PR #61 (2026-10-19 머지) | 상시 운용 콘솔: 한 세션 여러 미션, 취소 · 실패 뒤 생존, 실린 팔레트 재제출 → 운반부터, 결과 기록부 |
| PR #63–#65 | 도킹 중 긴 STOP 뒤 세션 유지(U30), 취소 복구 재시험 |
| `docs/references/week6_feedback.md` 5절 | 무선 통신 미고려 — 콘솔을 만든 계기(1쪽 원고) |
| `sim/models/dls08_measured/` | 전장 × 전폭 1.46 × 0.63 m, 포크 중심 최저 0.04 m(실측 전) + 승강 0.28 m |
| `config/isaac_transport_measured.yaml` · `config/isaac_slam_lidar.yaml` | 기구 곡률 한계 0.3665 1/m(뒤차축 회전 반경 2.73 m), LiDAR 평면 1.05 m |
| `tools/riibotics_scenario_paths.py` (브랜치 feat/riibotics-scenarios) | 좁은 통로 · 트레일러 축소 장면의 경로 확인 |
| `sim/isaac/run_transport.py --layout scene` · `tools/riibotics_isaac_scenes.py` (feat/riibotics-scenarios 827e757) | 8 · 10쪽 Isaac 자율 임무 재현 (장면 8종, 집을 팔레트는 명목 칸에서 3–8 cm · 2–3° 어긋남, 랜덤은 그림 기울기 10° 이내) |

## Isaac 재현 실행 (8 · 10쪽)

ws1 `test_runs/riibotics/riib.sbatch` — 10-19 원거리 인식 임무 설정(인식 · SLAM · 장애물 층 · D7 도킹 · YOLO11s 원거리 인식)에서 격자 계획만 끄고 장면 배치를 사전 지도로 씀(1.05 m LiDAR 가 바닥 팔레트를 못 봄). 완주 = 하역 오차 8 cm 이내 + 복귀.

| 실행 | 결과 |
|---|---|
| r4_line_1 (seed 0) | 근접 캡처 실패(아래판 증거 4 < 15) |
| r4_line_1_s1 · s2 | 완주, 하역 0.076 · 0.055 m, SLAM 최대 0.085 · 0.142 m — 8쪽 왼쪽 영상은 s1 |
| r4_line_2 | 근접 캡처 실패(no_opening_pattern) |
| r4_line_3 | 복귀까지 했으나 하역 0.098 m |
| r4_random_1 · _s1 | 근접 직선 수용 실패(횡 6.7 · 9.8 cm, 3.8 · 6.0°) |
| r4_random_2 | 완주, 하역 0.060 m — 8쪽 오른쪽 영상 |
| r4_random_3 | 복귀까지 했으나 하역 0.095 m |
| r4_trailer | 꺼낸 뒤 운반 중 허가 제한으로 진행 못 함, SLAM 최대 0.163 m |
| r4_aisle | 랙 뒤 여유 가정(0.15 m)에서 꺼내기 직선이 경계에 2.8 mm — 장면 가정 문제라 10쪽 표에서 뺌 |
| r5_aisle_out | 원거리 2.4 cm 정확, 근접 캡처가 0.91 m 옆 팔레트를 잡아 계획 실패 |

하역 LiDAR 정합은 열린 하역 구역이라 모든 실행에서 `start_rejected:degenerate`(SLAM 위치로 하역). 설계와 해석은 Codex 교차검증으로 수렴(장면 모드 3회, 결과 · 안전 여유 3회).

## 리보틱스 자료

| 자료 | 쓴 곳 |
|---|---|
| 「서울시립대 과제 시연 시나리오」 PDF 7쪽 (2026-10-19 메일 재발송본, 환경 수치 포함) | 6쪽 영상 다섯 개의 장면 배치(3–7쪽 그림을 우리 축척으로 옮김), 7쪽 지게차 평면도(2쪽)와 치수(통로 3.8 m, 구역 간격 3.4 m, 트레일러 2.6 m, 컨베이어 약 70 cm, 틀어짐 10° 이내) |
| 정진용 CTO 메일 (2026-10-19) | 구현 가능한 범위에서 진행 제안, Gemini 335 시리즈 대여 제안 |
| 중간 미팅 회의록 (로컬, 2026-10-14) | 하역 약 10 cm · 삽입 약 5 cm · 포크 높이 1 cm (축 미정) |

공개 덱에 PDF 그림을 넣는 것은 사용자 확인(2026-10-20). 원본 PDF 는 저장소에 넣지 않았다.

## 콘솔 화면 캡처

헤드리스 Chromium, 1600 × 900 CSS px(폰 400 × 860, `c3b_transport` 1018 × 880).

| 캡처 | 대상 | 쓴 곳 |
|---|---|---|
| `c3_live_auto.png` | Isaac 실시간 실행기 + 콘솔 (콘솔 세션 C3, 2026-10-17) | 2026-10-21 부터 화면에 안 씀 (녹화로 교체) |
| `01_wizard1` · `02b_wizard2` · `03_wizard3` · `10_run_3s` · `11_done` · `22_teleop_drive` · `30_phone` | 가짜 차량 `console.mock_vehicle` (main 4b65404, 2026-10-20) | 2026-10-21 부터 화면에 안 씀 (녹화로 교체) |
| 녹화 a(작업 지정 → 임무 끝) · b(수동 조종) · c(폰 관찰) | 가짜 차량 `console.mock_vehicle` (콘솔 코드 = main 4b65404), 헤드리스 Chromium 녹화, 2026-10-21 | 1쪽 세 영상, 3쪽 넓은 화면 · 폰, 4쪽 작업 지정 · 진행, 5쪽 수동 조종 (자른 영역과 배속은 README.md) |

## 화면에 쓰지 않은 사실

- 2시간 연속 운용(U16)은 1.5 h 에 SLAM 응답 기한 초과로 세션이 끝나 미충족이다. 11쪽은 미션을 연달아 지시하는 기능만 말하고 장시간 운용은 주장하지 않는다.
- 안전 설계(정지 종류, 재개 절차, 무장 단계, 끊김 정지)는 사용자 지시(2026-10-20)로 화면에서 뺐다. 정지 버튼 문구 「편의 정지 · 비상정지 아님」은 캡처 안에 그대로 보인다.

## 6쪽 시나리오 영상 (CPU 경로 계획 애니메이션)

`tools/riibotics_cpu_video.py` (lightminn/forklift feat/riibotics-scenarios) — PDF 그림의 배치를 우리 축척으로 옮긴 장면(그림 방향 그대로)을 Isaac 임무 설정(곡률 0.29, 여유 0.10, 정렬 2.1 m, 하역 1.5 m, D7)으로 CPU 에서 계획하고, 단계 속도(관측·접근·복귀 0.60, 삽입 0.055, 꺼내기 0.18, 운반 0.30, 후퇴 0.12 m/s, 가속 0.30 m/s², 승강 3.3 s)의 사다리꼴로 그린 8배속 영상. 시뮬레이션이 아니고 계획 시간은 뺐다. ③ ④ 는 세 팔레트를 차례로(앞 팔레트를 옮겨 둔 장면을 이어 붙임), ② 는 컨베이어 높이를 넣지 않고 집기·내리기 칸 둘레(팔레트 반폭 + 0.15 m)를 비운 바닥 움직임만이다(실제로는 포크 높이 0.32 m 가 축소 높이 0.37 m 에 못 미침, 11쪽). 계획된 경로의 전후진 전환: 통로 15, 컨베이어 8, 일자 18(3회), 랜덤 22(3회), 트레일러 4.

## 9쪽 팀원 Isaac 연속 이송 (정답 위치로 경로 추종)

ws1 `artifacts/20261020_demo_scenarios/isaac/runs` (팀원 shanghun, fleet 시뮬레이터 `run_world` · `source_v34`, 2026-10-20). 같은 실측 차체의 PhysX 모델과 경로 추종기이고, 팔레트 · 차량 위치는 정답(카메라 인식 · SLAM 없음), 이웃 팔레트 금지 폭 `--keep-m 0.2`(트레일러 J2 · J3 는 0.1, I 계열은 기본 0.3). 랜덤 배치는 그림 기울기(최대 10°)로 돌린 I2 · I3 · J6 가 1/3 · 1/3 · 1/9, 기울기 0° 칸 간격 1.22 m 의 I4 · I5 가 2/3.

| 실행 | 결과 (`result.json` jobs) | 쓴 곳 |
|---|---|---|
| I1_p4 | 1/1 완료, 접촉 0 (팔레트는 바닥, 컨베이어 높이 미반영) | 9쪽 ② · 10쪽 |
| J1_p5_line | 3/3 완료, 접촉 0 | 9쪽 ③ · 10쪽 |
| J5_p6_random26_5d | 5/5 완료, 접촉 0, 기울기 −4.3 – −7.3° | 9쪽 ④ · 10쪽 |
| J6_p6_drawn_tilt_5d | 그림 기울기(0 · 0 · 8 · −10 · 6°)로 9건 중 1건 완료, 나머지 계획 실패 | 10쪽 ④ 괄호 |
| J2_p7_dims_1col | 안쪽 1.36 m 한 줄 3/3 완료, 접촉 0 | 9쪽 ⑤ · 10쪽 |
| J3_p7_drawn_2col | 그림 비율 2.30 m 두 줄 4/4 (치수와 다른 폭이라 화면에 안 씀) | — |

영상: 마지막 작업 4 s 뒤에서 자르고 바닥만 잘라(`isaac_spec.crop`) 10 · 20 · 30 · 20배속, 960 px.

## 2쪽 구조도 사진

| 파일 | 원본 | 라이선스 |
|---|---|---|
| `d02_jetson.jpg` | Wikimedia Commons, File:NVIDIA Jetson Nano Developer Kit (47616885631) (cropped).jpg — SparkFun Electronics (Flickr). Jetson 계열 개발 키트 사진(우리가 쓸 Orin Nano 와 모양이 비슷한 다른 모델) | CC BY 2.0 |
| `d02_stm32.jpg` | Wikimedia Commons, File:Embedded World 2016, Stm32 Nucleo.jpg — Ordercrazy. STM32 Nucleo 보드 사진(우리 구동 보드는 자체 제작 예정) | CC0 |
| `d02_truck.jpg` | 5주차 `30_chassis_pallet.jpg` (2026-09-30 실물 사진, EXIF 제거)를 잘라 씀 | 팀 촬영 |
| `d02_isaac.jpg` | ws1 `test_runs/riibotics/r4_line_1_s1/run/view_quarter.mp4` 20 s 프레임 | 우리 렌더 |
| 노트북 · 폰 화면 | `v03_layout_poster.jpg` · `v03_phone_poster.jpg` (콘솔 녹화 프레임) | 우리 녹화 |

사진은 모두 다시 인코딩해 EXIF 를 지웠다.
