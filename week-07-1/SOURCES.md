# 리보틱스 중간 미팅 자료 출처

쪽 번호는 최종 16장 순서(2026-10-11: 운반 임무를 3쪽으로, 포켓 인식 처리 과정 7쪽 · 위치 추정 · 장애물 지도 구조 9쪽 추가) 기준이다.

수치는 로봇 저장소(`forklift/`)의 실행 기록 · 설정 · 검증 문서와 외부 원문에서 가져왔다. 시뮬레이션 결과는 Isaac Sim 합성 장면의 결과이고 실제 장비 성능이 아니다. 쪽별 세부 출처는 `SCRIPT.md` 의 `[Sources]` 에도 있다.

## 실행

| 이름 | 무엇 | 쓴 곳 |
|---|---|---|
| S4b | forklift b66271f, ws1 `artifacts/20261011_s4b/smoke/seed_1_v0.055` (Slurm 2297). 실측 차체(dls08_measured) · SLAM 위치 · LiDAR 1대 장애물 지도 · `--d7-planner --d7-docking` · 근접 추적(보정점 1.0 / 0.6 m) · 포켓 깊이 확인(D5) 끔 · 녹화 끔. 완주, 하역 6.74 mm, 진입 323.5 / 322.2 mm, 금지 접촉 0 | 8 · 13쪽 |
| 녹화 실행 | 같은 스냅숏(`p5_s4b_b66271f`)으로 D7 비교 d7 팔(`artifacts/20261008_d7_isaac/d7_isaac.sbatch`)의 인자 + `--video --robot-camera`, 근접 추적 끔(측정 계약이 녹화 끔 조건). ws1 `artifacts/20261011_meeting_video/seed_{1,5}_d7` (Slurm 2303 · 2304, `meeting_video.sbatch`) | 3 · 6쪽 |
| 6주차 l8_measured | forklift df109cf · bc4cc64, ws1 `artifacts/20261005_p5_l3/l8_measured`. 실측 차체 · LiDAR 1대, D7 이전(Dubins 목표 연결). 11쪽 영상 · 12쪽 왼쪽 그림의 실행 | 11 · 12쪽 |
| D7 v2 | ws1 `artifacts/20261008_d7_isaac/v2/d7` (현재 설정: Reeds–Shepp 목표 연결 · 도킹). 9회 모두 success complete, 하역 3.0–22.6 mm, 상자 장면 4개 포함 | 11 · 13쪽 |
| 6주차 S3 | forklift 5de6c3a, ws1 `artifacts/20261004_slam_s3/seed_1` (사진 추정 차체, 장애물은 시뮬레이터 정답). 358 s SLAM 4.0 cm 대 바퀴 회전만 340 cm, 끝 방향 −24.3° | 10쪽 |

## 화면을 만든 것

| 만든 것 | 쪽 | 원본 |
|---|---|---|
| `61_insert_depth.mp4` | 8 | S4b `run/pocket_frames/` 506장(10 Hz, 30.38–80.88 s)을 ws1 `artifacts/20261011_meeting_video/depth_clip/render_depth.py` 로 색 지도(0.25–3.0 m, turbo) 입힌 `depth_raw.mp4` → `prepare_clips.py depth` 가 `run/near_tracking.json` 사건(근접 추적 시작 44.3 s · 1.0 m 보정 54.03 s · 0.6 m 보정 61.73 s · 포크 끝 보호 70.62 s · 삽입 끝 80.69 s)에 글자, 마지막 장면 3.2 s 정지, 2배속 |
| `assets/52_reverse_obstacle.png` | 12 | 6주차 l8 장면 5 운반 중 상자 `plan_history.json`: 재계획(94.3 s)의 정지 자세 기준 상자 앞 1.97 m · 오른쪽 0.61 m, 재계획 경로 후진 1.25 m → 전진 22.95 m. 원래 경로는 처음 4 m 동안 가장 작게 꺾는 원(뒤차축 반경 1 / 0.29 = 3.45 m)에서 1.7 cm 이내이고 그 원이 상자 중심을 3 mm 차이로 지남(차체가 쓸고 가는 폭 3.05–4.15 m), 후진 뒤에는 상자가 회전 중심에서 4.8 m 라 비켜 감. matplotlib 축척 그림 (`prepare_figures.py`) |
| `assets/53_goal_fix.png` | 12 | `tests/unit/planning/test_d7_planner_options.py` 의 실측 차체 사례(목표 1 cm 앞 · 0.023 rad)를 forklift b66271f 의 `plan_hybrid_astar` 로 다시 계획(`git archive b66271f src`): 전진만 21.68 m, `D7_PLANNER_OPTIONS`(Reeds–Shepp · 상한 4 m) 0.99 m = 전진 0.50 + 후진 0.49 m. 왼쪽은 원 전체, 오른쪽은 같은 자리 확대(각각 축척 막대, 확대 칸의 두 움직임은 겹치지 않게 차체 위아래로 나눠 그림). matplotlib (`prepare_figures.py`) |
| `20_pipeline_stages_crop.png` | 7 | 3주차 `week-03/assets/20_pipeline_stages.png` 에서 위 제목 띠와 아래 단계 설명을 잘라 냄(세로 98–410 px, `prepare_figures.py stages`). 단계명과 색 범례는 HTML 로 다시 쓰고, 그림 안의 작은 글씨는 정리했다(화살표 설명 삭제, 시점 표시 19 → 26 px) |
| `assets/41_structure.png` | 9 | `prepare_figures.py` structure (matplotlib) — slam_pose · slam_link · obstacle_grid · drive_permission · planning_memory · scan_match · scan_docking 의 데이터 흐름을 위치 · 장애물 · 경로 · 하역 네 줄로 |
| `assets/40_system.png` | 4 | `prepare_figures.py` system (matplotlib) — 하드웨어 기록과 5주차 회로 초안의 부품 · 상태 |
| `30_chassis_pallet.jpg` | 5 | 5주차 자산 그대로(2026-09-30 실물 사진, EXIF 제거) |
| `45_slam_error.mp4` · `46_new_obstacle_single.mp4` | 10 · 11 | 6주차 자산 그대로 (week-06/prepare_clips.py) |

## 수치

| 쪽 | 수치 | 출처와 정의 |
|---|---|---|
| 5 | 회전 반경 약 2.5 m (계산, 사진 추정의 약 1.9배) | 0.66 / tan 15° = 2.46 m, 사진 추정 0.64 / tan 0.45 = 1.32 m (뒤차축, 자전거 모델), 비 1.86. 회전 원은 실측 전(`sim/models/dls08_measured/README.md`) |
| 5 | EPAL 6 삽입 목표 33 cm (계산) | min(EPAL 6 깊이 600 × 0.6 = 360, 캐리지 한계 346 − 예비 16 = 330) mm — forklift CLAUDE.md. 규칙의 결과이고 캐리지 한계는 추정 위에 선 값 |
| 6 | LiDAR · 깊이 카메라 · 잡음 · 마찰 | LiDAR A2M12 카탈로그(1,600빔 · 10 Hz · 0.2–12 m), 잡음 σ 0.02 m (`config/obstacle_layer_single.yaml`); 깊이 640 × 480, fx 465.74 → 수평 69.0° (D435i RGB 시야를 흉내 낸 합성 설정, 깊이 화각 87° 아님), 1 mm 양자화 · 잡음 없음 (S4b `pocket_camera`); 정지 · 운동 마찰 계수 0.8 / 0.7 (`config/isaac_transport.yaml`) |
| 7 | 대상 60개 모두 검출 · 95 %가 8.2 mm 이하 | `docs/validation/2026-09-14-epal6-capture-and-evaluation.md`: EPAL 6 Gazebo 100장면 = positive 60 · occluded 20 · negative 20, 2.0–4.0 m, dev p95 8.17 mm. 음성 0/20 의 단측 95 % 상한 13.9 % 라 오검출 성능은 쓰지 않음 |
| 8 | 포크 약 32 cm | S4b `insertion_measured` 323.5 / 322.2 mm (하역 오차는 3 · 13쪽에서만 씀) |
| 9 | 0.45 m · 0.5 rad 이동마다 보정 · 장애물 칸 0.3 s | `slam_link.py` KeyframeGate (0.447 m · 0.5 rad · 0.5 s), 삽입 중 고정 `slam_feedback.hold_phases`; `occupied_max_age_s` 0.3 (빔이 지나간 칸은 0.2 s 이내 스캔에서 FREE) |
| 11 | 현재 설정에서 상자 장면 모두 완주 | ws1 `artifacts/20261008_d7_isaac/v2/d7`: 9회 모두 success complete, 하역 3.0–22.6 mm; 상자 장면 seed_1_n1 · 1_n2 · 3_n1 · 5_n1. 영상은 D7 이전(Dubins 목표 연결) 6주차 실행 |
| 12 | 후진 1.3배 · 전환 1 m | 실행 기록의 `planner_config`: reverse_penalty 1.3, gear_change_penalty_m 1.0, curvature_limit_inv_m 0.29 (계획 회전 반경 3.45 m, 차체 한계 2.46 m 에 추종 여유) |
| 12 | 21.7 m 한 바퀴 · 지름 약 7 m · 1.3° | 2π × 3.448 = 21.67 m, 2 × 3.448 = 6.9 m, 0.023 rad = 1.32° |
| 12 (원고) | 한 바퀴 경로가 모두 사라짐 | forklift 1e3cdeb D7 CPU 판정: 운반 목표 고리 1,686 → 0 (목표당 2,376 계획), 길이 중앙값 21.69 → 1.03 m |
| 13 | 실격 기준 20 cm (하역 · 덜 삽입), 낙하 · 밀림, 포크 높이 20–30 cm 유지 (50 cm 초과 실격), 틸트 조작 | 한국산업인력공단 「[공개문제] 지게차운전기능사」 코스운전 및 작업, 2025-12-22 등록: https://www.q-net.or.kr/cst006.do?artlSeq=5211260&brdId=Q006&code=1204&gId=&gSite=Q&id=cst00602 — 요구사항 가–다, 유의사항 7, 실격 (8) 낙하 (9) 파손 (10) 포크로 드럼통 터치 (14) 50 cm 초과 (15) 하역 20 cm 초과 (16)(17) 밀림 (18) 덜 삽입 20 cm 초과. 팔레트에 닿는 것 자체는 실격이 아니다. 도면 치수는 D(좌우 최외측 타이어 바깥 간 거리)의 배수. 저작물이라 도면은 싣지 않음. 시험 시간 4분은 비교에서 제외 |
| 13 | 하역 오차 약 3 cm 이하 (기준의 약 1/7) | 현재 설정 완주 실행: D7 v2 9회 3.0–22.6 mm, 녹화 장면 5 · 1 19.4 · 27.0 mm, S4b dev9(smoke 와 같은 스크립트 · 설정) 완주 8회 5.8–29.4 mm → 29.4 / 200 = 14.7 %. D7 이전 6주차 실행(8.0 · 23.8 · 64.9 mm)은 뺐다 |
| 13 | 덜 넣은 정도 약 2–4 cm · 포크 약 19–22 cm | 캐리지 앞면–팔레트 간격(`insertion_measured`): D7 v2 20.4–26.1 mm, 녹화 장면 5 · 1 25.6 · 35.5 mm, dev9 21.7–37.4 mm (S4b smoke 22.1 mm); S4b 운반 중 승강 관절 0.165 m (명령 `lift_target_m` 0.2 에 못 미침) + 포크 중심 높이 0.04 ± 두께 0.025 / 2 → 밑면 0.193 · 윗면 0.218 m |
| 15 | 기간 | `docs/plans/2026-09-11-development-roadmap.md` §4 달력 대응. 하드웨어 일정은 팀 계획(6주차 8쪽 다음 작업)으로, 확정 일정이 아님 |
| 16 | T11 진입구 235 / 350 mm | forklift CLAUDE.md, `docs/design/2026-09-17-t11-test-article-drawing.md` — 두 해석 모두 미채택 |
