# 리보틱스 중간 미팅 자료 출처

쪽 번호는 2026-10-12 재구성 순서(본 발표 17장 + 부록 2장: 2 과제 제안서 대조, 4–7 하드웨어, 13 접근 상황 A–D, 위치 추정 두 장은 부록 18 · 19쪽) 기준이다.

수치는 로봇 저장소(`forklift/`)의 실행 기록 · 설정 · 검증 문서와 외부 원문에서 가져왔다. 시뮬레이션 결과는 Isaac Sim 합성 장면의 결과이고 실제 장비 성능이 아니다. 쪽별 세부 출처는 `SCRIPT.md` 의 `[Sources]` 에도 있다.

## 실행

| 이름 | 무엇 | 쓴 곳 |
|---|---|---|
| S4b | forklift b66271f, ws1 `artifacts/20261011_s4b/smoke/seed_1_v0.055` (Slurm 2297). 실측 차체(dls08_measured) · SLAM 위치 · LiDAR 1대 장애물 지도 · `--d7-planner --d7-docking` · 근접 추적(보정점 1.0 / 0.6 m) · 포켓 깊이 확인(D5) 끔 · 녹화 끔. 완주, 하역 6.74 mm, 진입 323.5 / 322.2 mm, 금지 접촉 0 | 2 · 10 · 14쪽 |
| 녹화 실행 | 같은 스냅숏(`p5_s4b_b66271f`)으로 D7 비교 d7 팔(`artifacts/20261008_d7_isaac/d7_isaac.sbatch`)의 인자 + `--video --robot-camera`, 근접 추적 끔(측정 계약이 녹화 끔 조건). ws1 `artifacts/20261011_meeting_video/seed_{1,5}_d7` (Slurm 2303 · 2304, `meeting_video.sbatch`) | 3 · 8쪽 |
| 6주차 l8_measured | forklift df109cf · bc4cc64, ws1 `artifacts/20261005_p5_l3/l8_measured`. 실측 차체 · LiDAR 1대, D7 이전(Dubins 목표 연결). 11쪽 영상의 실행 | 11쪽 |
| 12쪽 상자 장면 재실행 | 6주차 l8_measured `seed_5_n1`(스냅숏 `p5_df109cf`, run_transport.py sha256 03d59564… 일치)을 기록된 인자 그대로 + 고정 시점 `--extra-views quarter --quarter-eye=-2.0,-0.4,9.0 --quarter-target=1.8,-0.4,0.0 --quarter-focal=2.2`. ws1 `artifacts/20261012_meeting_chase/q67_seed_5_n1` (Slurm 2386, `meeting_quarter_w6.sbatch`). success complete, 하역 22 mm. 상자 위치는 6주차 실행과 같고(3.35, −1.37), 재계획은 1.75 m 후진(6주차 원래 실행은 1.25 m). 눈 높이 7 m 짝 실행 `q50_seed_5_n1` 은 같은 궤적 | 12쪽 |
| 접근 상황 A–D | ws1 `artifacts/20261012_meeting_ad` (Slurm 2389 · 2391 · 2397 · 2395, `meeting_ad.sbatch`): 녹화 실행과 같은 현재 설정(d7 팔, 실측 차체, LiDAR 1대, SLAM, 복귀 포함)으로 seed 5 에서 관측 후보 하나(상황별 인식 자리)만 바꿈, 고정 시점 녹화. 스냅숏 `p5_s4b_b66271f_worldbox` = b66271f + 월드 좌표 상자(`new_obstacles.py` 에 `frame: world` 추가, `WORLDBOX_PATCH.txt`). 쓴 실행 case_A · case_B4 · case_C · case_D2, 모두 success complete · 금지 접촉 0. 인식 실패로 끝난 B 자세 3개(카메라–앞면 4.57 · 4.09 · 4.29 m)와 쓰지 않은 B3 · D 는 같은 디렉터리에 보존 | 2 · 13쪽 |
| D7 v2 | ws1 `artifacts/20261008_d7_isaac/v2/d7` (현재 설정: Reeds–Shepp 목표 연결 · 도킹). 9회 모두 success complete, 하역 3.0–22.6 mm, 상자 장면 4개 포함 | 2 · 11 · 14쪽 |
| 6주차 S3 | forklift 5de6c3a, ws1 `artifacts/20261004_slam_s3/seed_1` (사진 추정 차체, 장애물은 시뮬레이터 정답). 358 s SLAM 4.0 cm 대 바퀴 회전만 340 cm, 끝 방향 −24.3° | 부록 2 (19쪽) |

## 화면을 만든 것

| 만든 것 | 쪽 | 원본 |
|---|---|---|
| `61_insert_depth.mp4` | 10 | S4b `run/pocket_frames/` 506장(10 Hz, 30.38–80.88 s)을 ws1 `artifacts/20261011_meeting_video/depth_clip/render_depth.py` 로 색 지도(0.25–3.0 m, turbo) 입힌 `depth_raw.mp4` → `prepare_clips.py depth` 가 `run/near_tracking.json` 사건(근접 추적 시작 44.3 s · 1.0 m 보정 54.03 s · 0.6 m 보정 61.73 s · 포크 끝 보호 70.62 s · 삽입 끝 80.69 s)에 글자, 마지막 장면 3.2 s 정지, 2배속 |
| `assets/55_reverse_box.mp4` · `_poster.jpg` | 12 | 위 '12쪽 상자 장면 재실행'의 `view_quarter.mp4`(1280 × 720 · 30 fps)에 `prepare_reverse_clip.py` 가 바닥 그림을 겹침: 따라가던 운반 경로(운반 시작의 마지막 live 계획, 노랑 — 실행기가 장면에 그린 가는 노란 선과 같은 길), 재계획 순간 가장 작게 꺾어 돌 때 짐 실은 차체가 쓸고 가는 띠(빨강, 회전 중심에서 3.05–4.15 m), 재계획의 후진(주황) · 전진(파랑). 카메라는 실행의 고정 시점 값(초점 22 mm · 수평 조리개 20.955 mm)으로 투영하고 상자 윤곽이 화면과 겹치는 것을 확인, 차체 · 상자에 가려지는 부분은 그리지 않음. 2배속, 재계획 순간 2.5 s 정지, 1080 × 720 으로 자름 |
| `assets/56_case_{a,b,c,d}.mp4` · `_poster.jpg` | 13 | `prepare_ad_clips.py`: 위 A–D 실행의 `view_quarter.mp4`(눈 0.6, −5.0, 7.0 · 대상 0.6, 1.1, 0 · 초점 22 mm)에서 인식(관측 후 첫 계획)부터 들기 1 s 뒤까지, 2배속, 진행 중인 계획의 남은 부분을 전진 파랑 · 후진 주황으로 바닥에 겹침(차체 · 상자에 가려지는 부분 제외), 1040 × 372 로 자름. 단계 자막은 frames.jsonl 의 단계와 속도 부호 |
| `assets/53_goal_fix.png` | 12 | `tests/unit/planning/test_d7_planner_options.py` 의 실측 차체 사례(목표 1 cm 앞 · 0.023 rad)를 forklift b66271f 의 `plan_hybrid_astar` 로 다시 계획(`git archive b66271f src`): 전진만 21.68 m, `D7_PLANNER_OPTIONS`(Reeds–Shepp · 상한 4 m) 0.99 m = 전진 0.50 + 후진 0.49 m. 왼쪽은 원 전체, 오른쪽은 같은 자리 확대(각각 축척 막대, 확대 칸의 두 움직임은 겹치지 않게 차체 위아래로 나눠 그림). matplotlib (`prepare_figures.py`) |
| `20_pipeline_stages_crop.png` | 9 | 3주차 `week-03/assets/20_pipeline_stages.png` 에서 위 제목 띠와 아래 단계 설명을 잘라 냄(세로 98–410 px, `prepare_figures.py stages`). 단계명과 색 범례는 HTML 로 다시 쓰고, 그림 안의 작은 글씨는 정리했다(화살표 설명 삭제, 시점 표시 19 → 26 px) |
| `assets/41_structure.png` | 부록 1 (18쪽) | `prepare_figures.py` structure (matplotlib) — slam_pose · slam_link · obstacle_grid · drive_permission · planning_memory · scan_match · scan_docking 의 데이터 흐름을 위치 · 장애물 · 경로 · 하역 네 줄로 |
| `assets/40_system.png` | 4 | `prepare_figures.py` system (matplotlib) — 하드웨어 기록과 5주차 회로 초안의 부품 · 상태. 모터 칸은 5주차 역분석 보고의 재사용 목록대로 "주행 · 리프트 (기존) · 조향 · 12 V 배터리" |
| `assets/44_waveforms.png` | 6 | `prepare_figures.py hardware` — 5주차 `week-05/assets/data_la_edges.json`(DSLogic Pro 1 MHz 2채널, 주행 · 승강 · 조향)을 다시 그림. 숫자는 한 선이 켜져 있던 시간(10 ms 미만은 접점 튐), 짧은 세로선은 누르는 순간 두 선이 2.95–3.43 ms 같이 켜진 것 |
| `assets/43_la_setup.jpg` | 6 | 5주차 `37_la_setup.jpg`(2026-09-29–30 측정 사진, EXIF 제거)에서 릴레이 기판과 탐침 부분만 자름(사람이 찍힌 아래쪽 제외) |
| `assets/45_sch_drv_channel.png` | 7 | 5주차 팀 회로 초안 `40_sch_drv8244.png` 의 L 채널(DRV8244 한 개)을 잘라 2배 확대 |
| `30_chassis_pallet.jpg` | 5 | 5주차 자산 그대로(2026-09-30 실물 사진, EXIF 제거) |
| `45_slam_error.mp4` · `46_new_obstacle_single.mp4` | 부록 2 · 11 | 6주차 자산 그대로 (week-06/prepare_clips.py) |

## 수치

| 쪽 | 수치 | 출처와 정의 |
|---|---|---|
| 5 | 회전 반경 약 2.5 m (계산, 사진 추정의 약 1.9배) | 0.66 / tan 15° = 2.46 m, 사진 추정 0.64 / tan 0.45 = 1.32 m (뒤차축, 자전거 모델), 비 1.86. 회전 원은 실측 전(`sim/models/dls08_measured/README.md`) |
| 5 | EPAL 6 삽입 목표 33 cm (계산) | min(EPAL 6 깊이 600 × 0.6 = 360, 캐리지 한계 346 − 예비 16 = 330) mm — forklift CLAUDE.md. 규칙의 결과이고 캐리지 한계는 추정 위에 선 값 |
| 8 | LiDAR · 깊이 카메라 · 잡음 · 마찰 | LiDAR A2M12 카탈로그(1,600빔 · 10 Hz · 0.2–12 m), 잡음 σ 0.02 m (`config/obstacle_layer_single.yaml`); 깊이 640 × 480, fx 465.74 → 수평 69.0° (D435i RGB 시야를 흉내 낸 합성 설정, 깊이 화각 87° 아님), 1 mm 양자화 · 잡음 없음 (S4b `pocket_camera`); 정지 · 운동 마찰 계수 0.8 / 0.7 (`config/isaac_transport.yaml`) |
| 9 | 대상 60개 모두 검출 · 95 %가 8.2 mm 이하 | `docs/validation/2026-09-14-epal6-capture-and-evaluation.md`: EPAL 6 Gazebo 100장면 = positive 60 · occluded 20 · negative 20, 2.0–4.0 m, dev p95 8.17 mm. 음성 0/20 의 단측 95 % 상한 13.9 % 라 오검출 성능은 쓰지 않음 |
| 10 | 포크 약 32 cm | S4b `insertion_measured` 323.5 / 322.2 mm (하역 오차는 3 · 13쪽에서만 씀) |
| 18 | 0.45 m · 0.5 rad 이동마다 보정 · 장애물 칸 0.3 s | `slam_link.py` KeyframeGate (0.447 m · 0.5 rad · 0.5 s), 삽입 중 고정 `slam_feedback.hold_phases`; `occupied_max_age_s` 0.3 (빔이 지나간 칸은 0.2 s 이내 스캔에서 FREE) |
| 6 | 한 선만 켜짐 · PWM 아님 · 릴레이 | `week-05/assets/data_la_edges.json`: 명령 구간 안 레벨 변화 0개(1 µs 튐 제외); 팀 리버스 엔지니어링 보고(2026-09-30): 릴레이 on/off, 속도 조절 기능 없음, RF 메인보드 통합, 재활용 전원 스위치 · 주행 모터 · 리프트 모터 |
| 7 | 47 mΩ · 0.76 V/A · 약 4.4 A | DRV8244-Q1 데이터시트 SLVSG24C: RON 47 mΩ(VQFN-HR, 비교한 DRV8873 150 · DRV8876 700 mΩ), AIPROPI 4750 A/A → 회로 초안 IPROPI 3.6 kΩ 에서 3600 / 4750 = 0.758 V/A, 3.3 V ↔ 4.35 A (계산). 연속 전류는 방열이 정하므로 모터 전류 실측 뒤 확정 |
| 11 | 현재 설정에서 상자 장면 모두 완주 | ws1 `artifacts/20261008_d7_isaac/v2/d7`: 9회 모두 success complete, 하역 3.0–22.6 mm; 상자 장면 seed_1_n1 · 1_n2 · 3_n1 · 5_n1. 영상은 D7 이전(Dubins 목표 연결) 6주차 실행 |
| 12 | 상자 앞 2 m · 오른쪽 0.6 m · 후진 1.75 m (원고) | 12쪽 상자 장면 재실행 `plan_history.json`(`prepare_reverse_clip.py` 출력): 재계획 83.9 s, 멈춘 뒤차축 기준 상자 앞 2.03 m · 오른쪽 0.64 m; 따라가던 경로는 멈춘 위치에서 2.5 cm, 상자 중심에서 0.7 cm, 4 m 동안 가장 작게 꺾는 원호(반경 1 / 0.29 = 3.45 m)에서 4.6 cm 이내; 그 원호의 차체 휩쓸림 띠 3.05–4.15 m 안에 상자 중심 3.46 m; 재계획 후진 1.75 m(주행 1.752 m) → 전진, 상자 중심까지 최소 1.63 m |
| 13 | 인식 약 3.6 m · 곡선 구간 약 1 m · 상자와 0.3 m | 인식: 성공 3.55 m(A) · 3.64 m(B4), 실패 4.09 · 4.29 · 4.57 m(no_opening_pattern, 깊이 잡음 없는 합성 영상) — 검출기 설정 상한 5.0 m 보다 짧음. 정렬 직진 시작의 카메라는 앞면에서 0.11 + 1.29 + 2.1 − 0.959 = 2.54 m → 곡선 구간 약 1 m, 반경 3.45 m 원호 1 m 의 옆 이동 약 0.15 m. B4 인식 자리는 축에서 0.17 m · 17° 비킴. D2 차체(−0.51…0.95 m, 폭 0.63 m)–상자 최소 0.314 m(정렬 시작 도착 75.0 s, frames.jsonl 정답 자세). 하역 A 16.9 · B4 28.7 · C 28.7 · D2 24.2 mm, 진입 0.316–0.334 m |
| 12 | 후진 1.3배 · 전환 1 m | 실행 기록의 `planner_config`: reverse_penalty 1.3, gear_change_penalty_m 1.0, curvature_limit_inv_m 0.29 (계획 회전 반경 3.45 m, 차체 한계 2.46 m 에 추종 여유) |
| 12 | 21.7 m 한 바퀴 · 지름 약 7 m · 1.3° | 2π × 3.448 = 21.67 m, 2 × 3.448 = 6.9 m, 0.023 rad = 1.32° |
| 12 (원고) | 한 바퀴 경로가 모두 사라짐 | forklift 1e3cdeb D7 CPU 판정: 운반 목표 고리 1,686 → 0 (목표당 2,376 계획), 길이 중앙값 21.69 → 1.03 m |
| 14 | 실격 기준 20 cm (하역 · 덜 삽입), 낙하 · 밀림, 포크 높이 20–30 cm 유지 (50 cm 초과 실격), 틸트 조작 | 한국산업인력공단 「[공개문제] 지게차운전기능사」 코스운전 및 작업, 2025-12-22 등록: https://www.q-net.or.kr/cst006.do?artlSeq=5211260&brdId=Q006&code=1204&gId=&gSite=Q&id=cst00602 — 요구사항 가–다, 유의사항 7, 실격 (8) 낙하 (9) 파손 (10) 포크로 드럼통 터치 (14) 50 cm 초과 (15) 하역 20 cm 초과 (16)(17) 밀림 (18) 덜 삽입 20 cm 초과. 팔레트에 닿는 것 자체는 실격이 아니다. 도면 치수는 D(좌우 최외측 타이어 바깥 간 거리)의 배수. 저작물이라 도면은 싣지 않음. 시험 시간 4분은 비교에서 제외 |
| 14 | 하역 오차 약 3 cm 이하 (기준의 약 1/7) | 현재 설정 완주 실행: D7 v2 9회 3.0–22.6 mm, 녹화 장면 5 · 1 19.4 · 27.0 mm, S4b dev9(smoke 와 같은 스크립트 · 설정) 완주 8회 5.8–29.4 mm → 29.4 / 200 = 14.7 %. D7 이전 6주차 실행(8.0 · 23.8 · 64.9 mm)은 뺐다 |
| 14 | 덜 넣은 정도 약 2–4 cm · 포크 약 19–22 cm | 캐리지 앞면–팔레트 간격(`insertion_measured`): D7 v2 20.4–26.1 mm, 녹화 장면 5 · 1 25.6 · 35.5 mm, dev9 21.7–37.4 mm (S4b smoke 22.1 mm); S4b 운반 중 승강 관절 0.165 m (명령 `lift_target_m` 0.2 에 못 미침) + 포크 중심 높이 0.04 ± 두께 0.025 / 2 → 밑면 0.193 · 윗면 0.218 m |
| 16 | 기간 | `docs/plans/2026-09-11-development-roadmap.md` §4 달력 대응. 하드웨어 일정은 팀 계획(6주차 8쪽 다음 작업)으로, 확정 일정이 아님 |
| 17 | T11 진입구 235 / 350 mm | forklift CLAUDE.md, `docs/design/2026-09-17-t11-test-article-drawing.md` — 두 해석 모두 미채택 |
