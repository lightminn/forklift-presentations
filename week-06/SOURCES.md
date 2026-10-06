# 6주차 자료 출처

수치는 로봇 저장소(`forklift/`)의 검증 기록·계획 문서와 실행 결과(`result.json`, `plan_history.json`)에서 가져왔다. 모든 결과는 Isaac Sim 합성 장면과 CPU 합성 시험(2쪽 12/12)의 결과이고, 쪽마다 조건 줄에 무엇이 시뮬레이터 정답이고 무엇이 센서 추정인지 적었다.

## 화면을 만든 것

| 만든 것 | 쓰인 곳 | 원본 |
|---|---|---|
| 카메라 화면 2장 (`43_camera_far.jpg`·`43_camera_near.jpg`) + 기존 장착 비교 2장 (`43_before_far.jpg`·`43_before_near.jpg`, `artifacts/20261003_render/seed_2001/camera_rgb.mp4` 16 s·19.5 s, 장착 선택 기능 이전의 고정 장착) | 2쪽 | `videos-from-ws1/20261006T1124Z_p5_slam_seed1_n1_planning_memory_no_pocket_check/camera_rgb.mp4` 39 s·43 s (캐리지 하단 장착, ws1 `l5_video14_nopc`, Slurm 1324) |
| 지도 작성 영상 (`21_slam_map_pair_fast.mp4`) | 3쪽 | 2026-09-26 Isaac 기록을 2026-09-28 ws1 에서 slam_toolbox 로 재생(`20260928_week05_replay`), `tools/compose_slam_video.py` 합성, 조감·지도 두 칸 8배속 (Slurm 585), 이를 `prepare_clips.py` 가 2.5배 더 빠르게(약 12초). 주행은 시뮬레이터 정답 자세 |
| SLAM 임무 영상 (`40_slam_mission.mp4`) | 4쪽 | ws1 `artifacts/20261004_slam_s3/seed_1/slam_online_three_panel.mp4` (Slurm 808, 코드 5de6c3a) 전체 360 s 를 8배속 |
| 새 장애물 영상 (`41_new_obstacle.mp4`) | 6쪽 | 1124Z N1 `slam_online_three_panel.mp4` 66–102 s 를 1.5배속 (Slurm 1324·1327, 코드 4147136) |
| 기억 비교 영상 (`42_memory_compare.mp4`) | 7쪽 | 조감 칸만 잘라 나란히: 왼쪽 `videos-from-ws1/20261006T0431Z_p5_slam_seed1_n2_new_obstacle` 247–252.5 s(코드 f454062, 기억 없음, 삽입 통로 깊이 확인 켬), 오른쪽 1124Z N2 222–227.5 s(코드 4147136, 기억·SLAM 지도 사용, 삽입 통로 깊이 확인 해제) |
| 평면 높이 도표·LiDAR 배치도 | 5쪽 | `build_deck.py` 의 표 값(아래)과 시뮬레이션 차체 모델 치수(`sim/models/dls08_provisional/parameters.yaml`)로 그림 |

## 수치

| 쪽 | 수치 | 출처와 정의 |
|---|---|---|
| 2 | 기존 장착 0.50 m·수평 → 마지막 약 0.25 m 무관측 | `docs/plans/2026-10-03-near-field-pocket-tracking.md` 86–90행 |
| 2 | 높이 0.27 m·틸트 0.10 rad(약 6°), 12/12 인계, 진입 뒤 오차 ≤ 20 mm | `docs/validation/2026-10-03-near-field-mount-study.md` 16·88–98행. CPU 합성 시험: 잡음·가림 없음, 정렬 자세, 승강 0, 윗판 높이·이동량 정답 사용(`tools/nearfield_mount_study.py`) |
| 4 | 3/3 장면 완주, 하역 7.8–22.4 mm, 충돌 0 | `docs/validation/2026-10-04-online-slam-closed-loop.md` 122–137행. 정답 위치로 완주한 장면 {1,3,5} 기준(장면 0 은 정답 위치로도 실패, 2·4 미실행). 경로 계획 장애물은 정답, 하역은 사전 스캔 정합 |
| 4 | 9 cm · 340 cm | 같은 기록 146–152행: 영상 장면 위치 RMSE 0.088 m, 358 s 에서 바퀴 오도메트리만 340 cm |
| 4 | 정답 위치 30/30 | `docs/validation/2026-10-03-fifth-frozen-evaluation.md` 45행 (원고에만) |
| 5 | 1.05 m 평면 43–47 % | `docs/plans/2026-10-04-lidar-obstacle-map.md` 29–34행: 장면 1·3·5 의 바닥 장애물 90·87·87 개 중 42·37·38 개. 높이 겹침만 본 상한(사각형 기둥 근사, 가림 미고려) |
| 5 | 93.8 % 이상 | 같은 계획 266–273행: 기록 경로의 정지 범위 관측 비율, 첫 점유 앞까지 셈, 0.03 m 미만 돌출 제외 |
| 6 | 하역 15.8 mm, 정지 구역 침범 0, 충돌 0, 정지 → 재계획 | 1124Z N1 `result.json` (하역 0.01579 m, `unpermitted_entries` 0, `forbidden_pocket_contacts` 0), `plan_history.json` 새 상자 출현 73.2 s · 그 상자에 대한 재계획 83.6 s (140.0 s 재계획은 상자와 약 4.3 m 떨어진 다른 이유) |
| 7 | 0.00 → 0.73 m | 복귀 첫 계획(0431Z 246.5 s, 1124Z 221.6 s)의 경로점(뒤차축)과 그 시각 전까지 기록된 LiDAR 점유 칸(`obstacle_grid_frames.npz`)의 칸 중심까지 최소 거리(0431Z 0.0022 m, 1124Z 0.7277 m). 차체 외곽과 실제 장애물의 간격이 아니다 |
