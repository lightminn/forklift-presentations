# 12주차 출처

쪽별 출처의 전체 목록은 `build_deck.py` 의 각 장 `sources` 와 발표자 노트의 [Sources] 블록이다(`SCRIPT.md` 에는 넣지 않는다).

## 로봇 저장소 (lightminn/forklift, main f7566ed4 기준)

| 자료 | 쓴 곳 |
|---|---|
| `docs/references/week11_feedback.md` (로컬 전용 미추적 파일) | 01 장 피드백 세 줄 |
| `docs/validation/2026-11-17-hw-day.md` 「H743 링크」 | 02 장 표: 노트북 600 s · STATE 60,000 · seq 틈 0 · 왕복 p50 9.3 / 최대 10.15 ms · 호스트 간격 최대 20.917 ms, Jetson 600 s · STATE 59,999 · seq 틈 0 · 왕복 3.97 / 10.26 ms · 호스트 간격 최대 10.661 ms, 둘 다 리셋 0 · PASS; HIL 이미지 `forklift-mcu hil locked 65f252a5c4b6` |
| 같은 문서 「Jetson 기록」 「다리 정체」 | 03 장: Orin Nano Super, MAXN_SUPER + `jetson_clocks`; 리허설 다리 5 분씩 정지 최대 21.9 ms · 부하(모든 코어) 최대 29.6 ms, 기준 80 ms 미만(부하) |
| 같은 문서 「D435i IMU」 「A2M12」 | 03 장: 120.2 s, 자이로 399.8 Hz · 가속도 200.1 Hz, dropped 0; A2M12 미실시 |
| `docs/validation/assets/hw-day-2026-11-17/` 의 `jetson/h743_link.txt`, `jetson/imu.txt`, `jetson/stall/{idle,load}/verdict.txt`, `laptop_h743/BUILD.txt` | 위 값을 판정 줄에서 다시 확인(2026-11-17) |
| `docs/validation/2026-10-29-b-p1b-search-budget.md` 결론 | 04 장 1행: 공장 배치 seed 4, 유효 84, 성공 69 (82 %), 틀린 확정 0 (기록 스캔 정합 평가) |
| `docs/validation/2026-10-29-b-p2d-start-relocalization.md` | 04 장 2행: seed 5, 유효 84, 성공 68 (81.0 %), 틀림 0, 위치 오차 중앙값 2.0 cm (원고) |
| `docs/validation/assets/reloc-observe-move/compare.json`, `assets/b-p2d/val_s5.json` | 04 장 지도 그림의 출발점별 결과(83 짝) |
| `docs/validation/2026-11-16-reloc-observe-move.md` | 04 장 3행: 같은 지도 · 출발 목록, 제자리 67 → 이동 69 (84 기준), 틀린 확정 0, 남은 실패는 남쪽 반복 선반 칸, 총괄 결정(승격 안 함 · 실차는 정해 둔 시작 자리) |
| `docs/validation/2026-11-15-post-fix-baseline.md` 3.3 | 05 장 1행: 같은 스냅숏에서 표시선이 인식 카메라에 안 보임(R) / 보임(S), 같은 장면 · seed 40 짝, 완주 36 대 34, 인식 실패 0 대 1(aisle_rack s2) |
| `docs/validation/2026-11-14-path-display-impact.md` 1 절 | 05 장 1행 원인: 표시선 · 목적지 고리가 렌더되는 장면 prim 이라 인식 카메라에 찍힘, 표시만 끈 진단에서 근접 캡처 거부 → 채택 2/2 (수정 #512) |
| `docs/validation/2026-11-15-k1-recheck.md` 2 절, `2026-11-15-baseline-fragility-summary.md` ② | 05 장 2행: 느슨한 도착 5.6 · 6.2 cm, K1(근거리 관측 도착 0.05 m · 0.05 rad) 40 짝 등록 판정 「나음」, 횡 오프셋 0.08 m 초과 4 → 0, 완주 36 = 36 (노출 기준을 겨우 채운 약한 근거 — 원고에 한 줄) |
| `docs/validation/2026-11-17-return-home-timeout.md`, `2026-11-17-goal-band-cusp-retry.md` | 05 장 3행: random_1 s24 복귀 끝 옆 8.100 mm(허용 8 mm) 정지로 시간 초과, 결정 모드 짝 끔 = 시간 초과 · `--goal-creep-band on` = 완주, riib 런처 기본 켬(#571), 근거 seed 1 개(원고에 한 줄) |
| `docs/validation/2026-11-16-aisle-short-cusp-arc.md` 2 절 | 06 장 표: 운반 cusp 재계획 16 → 8, 완주 9 = 9, 운반 짧은 곡선 cusp 다리 90 → 18; aisle_rack 한정 기본 켬(#566) |
| `docs/plans/2026-11-16-aisle-short-cusp-arc.md` | 06 장 원고: 0.6 m 미만 곡선 다리에 비용 |
| `sim/isaac/run_transport.py` `add_path_display` | 06 장 범례 색(접근 · 운반 · 복귀) |

비교 주의: 04 장 2 · 3행은 같은 지도 · 출발 목록이지만 그 사이 런처 기본값이 바뀌어 성공 수를 직접 비교하지 않는다(`2026-11-16-reloc-observe-move.md` 1 절). 3행 안의 67 → 69 는 같은 세션의 단계별 비교다.

## 사진 · 그림

| 파일 | 출처 | 라이선스 · 편집 |
|---|---|---|
| `hw_h743.jpg` | 사용자 촬영(2026-11-17), WeAct STM32H743VIT6 코어 보드 윗면. 원본은 사용자 Downloads 에 그대로 둠 | 팀 자료. 보드 주변만 잘라 180° 돌림(실크 글자가 바로 읽히게), EXIF 지움 |
| `hw_jetson.jpg` | NVIDIA Jetson Orin Nano Super Developer Kit 제품 페이지 <https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/> 의 이미지 `jetson-orin-nano-super-developer-kit-bbm-d@2x.jpg` | © NVIDIA 제품 소개 이미지(Commons 에 Orin Nano 사진이 없어 총괄 지시대로 공식 이미지 사용). 보드 부분(가로 2300–4100 px)만 잘라 800 px 로 줄임 |
| `hw_d435.jpg` | Wikimedia Commons, File:Intel Realsense depth camera D435.jpg — Marc Auledas (Own work) | CC BY-SA 4.0. EXIF 방향대로 세운 뒤 카메라 부분만 자름, EXIF 지움. D435 는 IMU 없는 같은 계열 모델이고 겉모양은 D435i 와 같음 |
| `hw_lidar.jpg` | 과제 브리프 3쪽 RPLIDAR A2 이미지(이 저장소 `week-02/assets/rplidar-a2.jpeg`) | 회전 화살표와 로고 띠를 빼고 자름, 화면에서 흐리게(미연결 표시) |
| `s04_map.png` | B-P2d 조사 지도 `hall_s5b_G0`(map 3edf24b0e981…, SLAM 점유 격자 843 × 639 · 0.05 m) — Drive `gdrive:forklift-archive/ws1-cleanup-20261110-an/an_f1.tar.zst` 에서 `test_runs/live/bp2d_survey/hall_s5b_G0/bundle/{grid.npz,manifest.json}` 만 스트림으로 꺼냄(노트북 임시 사본은 그림을 만든 뒤 지움) | `make_map.py`: 점유 ≥ 50 은 진회색, 빈 칸 흰색, 미관측 회색, 홀 위쪽 바깥 110 행(미관측 · 문밖 LiDAR 흔적)은 잘라 냄; 출발 자세는 로봇 저장소 `docs/validation/assets/b-p2d/val_s5.json`, 결과는 `reloc-observe-move/compare.json` 의 짝(제자리 확정 67 초록, 이동 뒤 확정 2 파랑, 미확정 14 빨강, 위치 추정 기록이 없는 val4_092 는 뺌); 5 m 축척 막대 |
| `s05_cusp.mp4` · `s05_cusp_poster.jpg` (06 장) | ws1 `/home/projects/forklift/test_runs/acs/render_acs_d45bb1e1/acsAv_aisle_rack_s1/run/transport.mp4`(끔, sha256 9b3bc418c331e94aae338a99ddc6c50539a7f57951fbe4518a1213fc626a8477) 와 `acsBv_aisle_rack_s1/run/transport.mp4`(켬, sha256 e53ef0207876499be622cfc11258859d5269917c7b6c87e8d460e400de4a2463). 결정 모드 렌더, 비교 실행과 같은 궤적; 끔은 운반 cusp 재계획 2 회(101 · 113 s), 켬은 0 회, 둘 다 완주 | README.md 영상 절 |

## 사용자 · 총괄 전달

- 2026-11-17 총괄: 이번 주 덱은 11주차 피드백에 답하는 구성 권장, 재료 1–6(실제 장비 첫 연결, 좁은 통로 짧은 곡선 비용, 시작 위치 검증, 선택 재료, 논문은 새로 찾은 것 없음, 다음 계획).
- 2026-11-17 총괄 용어 정정: 「출발 위치 표시 운용」은 known start — 바닥에 시작 자리를 표시하고 그 좌표 · 방향을 지도에 등록, 그 자리에 놓고 재위치 탐색 없이 시작. 화면에는 「정해 둔 시작 자리에서 출발」로 쓴다.
- 2026-11-17 사용자(총괄 전달): H743 사진 제공, 나머지 장비는 인터넷 사진을 조합, Jetson 은 Orin Nano Super 사진(Commons 없으면 출처를 밝힐 수 있는 공식 이미지).
- 2026-11-17 사용자(총괄 전달): "전 자료에서 실패했던 케이스들을 어떻게 고쳤고 어떻게 성공률 높였는지" — 05 장을 넣음. 전후 근거는 같은 장면 · seed 짝 비교만(짝이 아닌 두 배치의 성공률 비교는 쓰지 않음).
- 2026-11-17 사용자 정정(총괄 전달): 고치지 못했거나 효과가 없던 사례(운반 S 자 이탈, 전환점 재계획 재시도, 적재 횡 치우침 등)는 덱에 넣지 않는다. 고친 사례의 근거 한계는 원고에 한 줄만.
- 2026-11-17 사용자(총괄 전달): "5페이지 사진이 뭘 의미하는건지 잘 안보임" — 04 장 그림을 11주차 후보 화면에서 SLAM 지도 위 출발점별 결과로 바꿈(지도 원자료는 Drive 보관본에서 꺼냄, CSS · SVG 도식 아님).
- 11주차가 남긴 연속 이송 랜덤 배치 1 회 실패는 같은 설정의 재실행 짝이 없어 05 장에 넣지 않았다.
