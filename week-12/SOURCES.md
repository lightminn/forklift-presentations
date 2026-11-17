# 12주차 출처

**발표용 재구성(2026-11-18) 장 번호**: 01 피드백, 02 실제 장비(옛 02 · 03), 03 시뮬레이션 실패 해결(옛 06 표 + 옛 09 차체 모형 행), 04 인식 카메라 전후(옛 07), 05 순응 타이어(옛 09 그래프 + 옛 10 영상), 06 시작 위치(옛 04 표 + 옛 05 지도), 07 좁은 통로(옛 11), 08 다음 주(옛 12). 옛 08 장(복귀 정체 영상)과 03 장 막대 그래프(명령 간격)는 뺐고 수치는 표 · 장비 칸에 남겼다. 아래 표의 장 번호는 쓴 당시 번호이고, 지금 장의 출처 세부는 build_deck.py 의 각 장 sources 다. 자산 이름: s04_map.png → s06_map.png, s06_before/after.png → s04_cam_before/after.png, s05_cusp.* → s07_cusp.*, s10_tyre.* → s05_tyre.*(라벨을 새 문구로 다시 자름), s07_stall.* 은 지움.

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
| `docs/validation/2026-11-16-aisle-short-cusp-arc.md` 2 절 | 08 장 표: 운반 cusp 재계획 16 → 8, 완주 9 = 9, 운반 짧은 곡선 cusp 다리 90 → 18; aisle_rack 한정 기본 켬(#566) |
| `docs/plans/2026-11-16-aisle-short-cusp-arc.md` | 08 장 원고: 0.6 m 미만 곡선 다리에 비용 |
| `sim/isaac/run_transport.py` `add_path_display` | 08 장 범례 (07 장 범례는 `src/forklift_core/mission/core.py` `show_path` 의 복귀 · 접근 · 관측 색) 색(접근 · 운반 · 복귀) |

비교 주의: 04 장 2 · 3행은 같은 지도 · 출발 목록이지만 그 사이 런처 기본값이 바뀌어 성공 수를 직접 비교하지 않는다(`2026-11-16-reloc-observe-move.md` 1 절). 3행 안의 67 → 69 는 같은 세션의 단계별 비교다.

## 사진 · 그림

| 파일 | 출처 | 라이선스 · 편집 |
|---|---|---|
| `hw_h743.jpg` | 사용자 촬영(2026-11-17), WeAct STM32H743VIT6 코어 보드 윗면. 원본은 사용자 Downloads 에 그대로 둠 | 팀 자료. 보드 주변만 잘라 180° 돌림(실크 글자가 바로 읽히게), EXIF 지움 |
| `hw_jetson.jpg` | NVIDIA Jetson Orin Nano Super Developer Kit 제품 페이지 <https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/> 의 이미지 `jetson-orin-nano-super-developer-kit-bbm-d@2x.jpg` | © NVIDIA 제품 소개 이미지(Commons 에 Orin Nano 사진이 없어 총괄 지시대로 공식 이미지 사용). 보드 부분(가로 2300–4100 px)만 잘라 800 px 로 줄임 |
| `hw_d435.jpg` | Wikimedia Commons, File:Intel Realsense depth camera D435.jpg — Marc Auledas (Own work) | CC BY-SA 4.0. EXIF 방향대로 세운 뒤 카메라 부분만 자름, EXIF 지움. D435 는 IMU 없는 같은 계열 모델이고 겉모양은 D435i 와 같음 |
| `hw_lidar.jpg` | 과제 브리프 3쪽 RPLIDAR A2 이미지(이 저장소 `week-02/assets/rplidar-a2.jpeg`) | 회전 화살표와 로고 띠를 빼고 자름, 화면에서 흐리게(미연결 표시) |
| `s04_map.png` | B-P2d 조사 지도 `hall_s5b_G0`(map 3edf24b0e981…, SLAM 점유 격자 843 × 639 · 0.05 m) — Drive `gdrive:forklift-archive/ws1-cleanup-20261110-an/an_f1.tar.zst` 에서 `test_runs/live/bp2d_survey/hall_s5b_G0/bundle/{grid.npz,manifest.json}` 만 스트림으로 꺼냄(노트북 임시 사본은 그림을 만든 뒤 지움) | `make_map.py`: 점유 ≥ 50 은 진회색, 빈 칸 흰색, 미관측 회색, 홀 위쪽 바깥 110 행(미관측 · 문밖 LiDAR 흔적)은 잘라 냄; 출발 자세는 로봇 저장소 `docs/validation/assets/b-p2d/val_s5.json`, 결과는 `reloc-observe-move/compare.json` 의 짝(제자리 확정 67 초록, 이동 뒤 확정 2 파랑, 미확정 14 빨강, 위치 추정 기록이 없는 val4_092 는 뺌); 5 m 축척 막대 |
| `s06_before.png` · `s06_after.png` (06 장) | ws1 `/home/projects/forklift/test_runs/render12_f7566ed4/pdBefore_aisle_rack_s2/run/perception_capture_2_rgb.png`(진단 stage, sha256 e2056717…) · `pdAfter_aisle_rack_s2/…`(overlay 기본, sha256 ba9500b0…) — 시뮬-물성 세션 렌더(isaac_array 19683, 스냅숏 r12_f7566ed4, 결정 모드), 두 실행 모두 완주 | (160, 140)–(560, 330) 을 잘라 2배 확대, 고치기 전 그림에 빨간 동그라미(선 자리) |
| `s07_stall.mp4` · `s07_stall_poster.jpg` (07 장) | 같은 렌더의 `gcbOff_random_1_s24/run/view_quarter.mp4`(sha256 b50b428d85d11e967377f1a0113fc16f0f7eb9a597bb642e1cd726f795384719, 234.48 s, 시간 초과) · `gcbOn_random_1_s24/run/view_quarter.mp4`(sha256 2d2142738129c7198946e5334c77c0641d366c9f7e95d9eb45ce1ec0c943ae2b, 217.17 s, 완주) — 받은 뒤 sha256 대조 일치 | README 영상 절 |
| `s10_tyre.mp4` · `s10_tyre_poster.jpg` (10 장) | ws1 `/home/projects/forklift/test_runs/f2i/batch_f2i_22fe89be/video/f2iw_O_random_1_s8/run/transport.mp4`(지금 모형, sha256 8cb8c30eedc098240b288e2e621efb0e2d2bedb22d82719570ef85e08ca2aa34, 운반 중 경로 이탈) · `f2iw_F2_random_1_s8/run/transport.mp4`(순응 타이어, sha256 3d276fd13363e3051d9cf0a26926abbe8496dc61f1d8d41f808d2afaa86aa5ac, 완주) — 시뮬-물성 세션 렌더, 결정 모드, VIDEO=off 실행과 궤적 같음 | README 영상 절 |
| `s05_cusp.mp4` · `s05_cusp_poster.jpg` (11 장) | ws1 `/home/projects/forklift/test_runs/acs/render_acs_d45bb1e1/acsAv_aisle_rack_s1/run/transport.mp4`(끔, sha256 9b3bc418c331e94aae338a99ddc6c50539a7f57951fbe4518a1213fc626a8477) 와 `acsBv_aisle_rack_s1/run/transport.mp4`(켬, sha256 e53ef0207876499be622cfc11258859d5269917c7b6c87e8d460e400de4a2463). 결정 모드 렌더, 비교 실행과 같은 궤적; 끔은 운반 cusp 재계획 2 회(101 · 113 s), 켬은 0 회, 둘 다 완주 | README.md 영상 절 |

## 사용자 · 총괄 전달

- 2026-11-18 사용자(총괄 전달): "이제 발표 임박했으니까 지금까지 한 거 기준으로 덱 다시 만들어" — 비슷한 장을 합쳐 7–8 분으로. 바뀐 사실: 순응 타이어는 사용자 결정으로 시뮬 전체 기본 켬(화면은 「기본 적용 결정」까지, 런처 PR · Isaac smoke 진행 중은 원고에만), 11주차 연속 이송 근접 촬영 실패는 지금 main 라이브 1 회에서 재현 안 됨(고친 사례로 쓰지 않고 출처에만), 운영(실시간) 모드 관찰에서 이전 모형 3 번 중 1 번 S 자 이탈 · 순응 타이어 3/3 완주(판정 아님, 원고에만).

- 장 번호(2026-11-18 지금): 04 시작 위치 찾기 시험(표), 05 시작 위치 판정 지도와 대응(지도), 06 시뮬레이션 실패 수정, 07 사례 1 전후 화면, 08 사례 3 전후 화면, 09 시뮬레이터 차체 모형 수정, 10 S자 운반 전후 비교, 11 좁은 통로 경로 개선, 12 다음 주 계획. 위 표의 장 번호는 쓴 당시 번호다.
- 2026-11-18 사용자(총괄 전달): "저번 주차 발표자료에 있었던 실패 사례들부터 돌려봐. 발표자료에 이거 고친 것도 반영하게." — 09 · 10 장(순응 타이어 모형 재실행, 시뮬-물성 세션), 11 장 한 줄. 시뮬 결과이고 순응 타이어는 아직 기본값 아님(등록 판정 진행 중), 타이어 강성 140 kN/m 는 추정값. 출처 세부는 build_deck.py 09 · 10 장 sources.
- 2026-11-18 사용자(총괄 전달): 화면은 개발 과정을 모르는 청중이 대본 없이 보고 이해할 수 있게 — 화면 문구 전체를 agy 로 다시 씀(VALIDATION.md).

- 2026-11-17 총괄: 이번 주 덱은 11주차 피드백에 답하는 구성 권장, 재료 1–6(실제 장비 첫 연결, 좁은 통로 짧은 곡선 비용, 시작 위치 검증, 선택 재료, 논문은 새로 찾은 것 없음, 다음 계획).
- 2026-11-17 총괄 용어 정정: 「출발 위치 표시 운용」은 known start — 바닥에 시작 자리를 표시하고 그 좌표 · 방향을 지도에 등록, 그 자리에 놓고 재위치 탐색 없이 시작. 화면에는 「정해 둔 시작 자리에서 출발」로 쓴다.
- 2026-11-17 사용자(총괄 전달): H743 사진 제공, 나머지 장비는 인터넷 사진을 조합, Jetson 은 Orin Nano Super 사진(Commons 없으면 출처를 밝힐 수 있는 공식 이미지).
- 2026-11-17 사용자(총괄 전달): "전 자료에서 실패했던 케이스들을 어떻게 고쳤고 어떻게 성공률 높였는지" — 05 장을 넣음. 전후 근거는 같은 장면 · seed 짝 비교만(짝이 아닌 두 배치의 성공률 비교는 쓰지 않음).
- 2026-11-17 사용자 정정(총괄 전달): 고치지 못했거나 효과가 없던 사례(운반 S 자 이탈, 전환점 재계획 재시도, 적재 횡 치우침 등)는 덱에 넣지 않는다. 고친 사례의 근거 한계는 원고에 한 줄만.
- 2026-11-18 사용자(총괄 전달): 04 장 「짐 배치 A/B」를 「공장 배치 A/B」로(A = factory layout seed 4, B = seed 5, 같은 건물에 물건을 다르게 놓은 두 장면).
- 2026-11-17 사용자(총괄 전달): "5페이지 사진이 뭘 의미하는건지 잘 안보임" — 04 장 그림을 11주차 후보 화면에서 SLAM 지도 위 출발점별 결과로 바꿈(지도 원자료는 Drive 보관본에서 꺼냄, CSS · SVG 도식 아님).
- 2026-11-17 사용자(총괄 전달): "6페이지에도 비교 영상 넣어서 어떤 점이 달라진건지 시각적으로" — 05 장 사례 ① · ③ 의 고치기 전후 화면을 06 · 07 장으로 넣음(② 는 화면 차이가 작아 표만, 총괄 합의). 렌더는 시뮬-물성 세션.
- 11주차가 남긴 연속 이송 랜덤 배치 1 회 실패(random_m s0 두 번째 임무 근접 캡처 「예상 후보 없음」)는 화면에 넣지 않았다. 시뮬-물성 세션이 지금 main · 같은 설정(학습 인식 + 당시 운영 기본)의 라이브 1 세션으로 다시 돌려 세 임무가 모두 완료됐다(하역 26.7 · 12.8 · 34.2 mm, 두 번째 임무 근접 캡처는 2 번째 시도에서 통과). 비결정 1 회라 「지금 main 에서 재현 안 됨(1 회)」으로만 적는다 — 고쳤다는 근거가 아니고, 순응 타이어와 무관한 인식 쪽 사례. 출처: 로봇 저장소 docs/validation/2026-11-18-f2-i-reregistration.md 3.3 절(PR #575).
