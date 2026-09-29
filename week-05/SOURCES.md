# 5주차 자료 출처

수치는 로봇 저장소(`forklift/`)의 검증 기록과 계획 문서, 공식 사양에서 가져왔다.

## 화면을 만든 것

| 만든 것 | 쓰인 곳 | 성격 |
|---|---|---|
| 자리 표시 | 차체 실측 · 포크·동봉 팔레트 · 조종기 버튼별 신호 | 실측 자료가 들어오면 교체 |
| **스캔 영상** | 2D LiDAR 스캔 | `prepare_videos.py scan`: Isaac 기록 `20260926_factory_slam_v3/survey_seed_0` 의 `slam_log.npz` 스캔을 정답 레이저 자세에 그리고, 물체 윤곽은 `meta.json` 배치(아랫면 ≤ 1.05 m ≤ 윗면이면 진한 색). 경로 앞 55 %를 약 7배속 |
| 개념도 · 수치 도표 | LiDAR 장착 높이 | 개념도는 축척 아님. 도표는 `build_deck.py` 안의 기록값 |
| **Isaac 기록 + slam_toolbox 재생** | 2D LiDAR 지도 작성(조감·지도 두 칸, 8배속) | 2026-09-26 Isaac 기록을 2026-09-28 ws1 에서 다시 재생(`20260928_week05_replay`)하고 `tools/compose_slam_video.py` 로 합성(색만 바꾼 사본: 실제 경로 회색 · SLAM 파랑, ws1 Slurm 585 `20260929_week05_videos`). 제어는 시뮬레이터 정답 자세 |
| **지도 비교 영상** | 위치 추정에 따른 지도 차이 | `prepare_videos.py map`: 같은 스캔을 `20260928_week05_replay/survey_seed_0_clean` 의 `odometry.csv`(바퀴·조향) 와 `slam/slam_trajectory.csv`(SLAM) 자세에 놓아 누적. 두 궤적 모두 출발 자세만 정답에 맞춤. slam_toolbox 가 만든 점유 지도가 아니다 |
| **데이터 도표** | 위치 추정 오차(경로 애니메이션) | `prepare_data.py` 가 뽑은 `assets/data_survey_seed0.json` |
| 표 | 중간 미팅 확인 사항 | 4주차 피드백 §1 |

## 수치

| 수치 | 값 | 출처와 정의 |
|---|---|---|
| 작업장 크기 | 약 30 × 31 m | `docs/plans/2026-09-26-factory-hall-and-isaac-slam.md` 홀 계획 경계 30.3 × 31.2 m |
| 배치 구성 | 팔레트 55–63 · 상자 394–563 · 작업장 물품 23 | `docs/validation/2026-09-26-factory-hall-and-isaac-slam.md` §1, seed 0–19 |
| 자기 차체 가림 | 0.55 m 60 % · 0.65 m 18.8 % · 0.75 m 9.5 % · 1.05 m 0 % | 같은 문서 §1. 잠정 모델 URDF 충돌 상자에 광선 400개, base_link x = −0.12 m. 실물 아님 |
| 위치 추정 오차 (재생 1회 = 출발 자세 정렬 RMSE) | SLAM 10회 평균 0.040 / 0.055 m · 바퀴만 0.773 / 0.782 m | 같은 문서 §6 (2026-09-28 재실행 12회가 소수 셋째 자리까지 같고, 바퀴만 seed 2 한 값만 0.806 대 0.807), 재생 10회(배치 5 × 잡음 없음·합성 잡음), 출발 자세 정렬 ATE, 116 m · 0.5 m/s |
| 거리·회전 | 115.92 대 115.98 m · 9.54 대 9.43 rad | 같은 문서 §4, seed 0 잡음 없음. 원인 미확정 |
| 합성 LiDAR | 1,600빔 · 0.225° 간격 · 10 Hz · 0.2–12 m · 장착 높이 1.05 m | `config/isaac_slam_lidar.yaml`, 기록 `meta.json` 의 `laser`. A2M12 카탈로그 값 기준 합성 센서, 실측 아님 |
| 합성 잡음 | 거리 σ 0.02 m · 뒷바퀴 σ 0.2 rad/s · 조향 σ 0.005 rad | 같은 문서 §4. 가정값이며 센서 사양이 아니다 |
| 잠정 모델 치수 | 표의 오른쪽 열 | `sim/models/dls08_provisional/parameters.yaml` — 카탈로그 값과 사진 비례 추정 |
