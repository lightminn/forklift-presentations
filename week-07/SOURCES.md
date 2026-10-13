# 7주차 출처

쪽별 출처의 전체 목록은 `build_deck.py` 의 각 장 `sources` 와 `SCRIPT.md` 의 [Sources] 블록이다. 다중 지게차 결과의 정본은 로봇 저장소 `feat/fleet-five`(c24548f) 의 계획 · 검증 문서다.

| 문서 | 내용 |
|---|---|
| `docs/plans/2026-10-08-fleet-five-forklifts.md` | NVIDIA 창고 5대, 구간 점유 · 고정 순번 · 정차 규정, 창고 실측(통로 폭, 회전 반경 3.45 m) |
| `docs/plans/2026-10-09-fleet-random-worlds.md` | 무작위 공장 3종, 상황 C0–C5, 판정 |
| `docs/validation/2026-10-09-fleet-random-worlds.md` | v14 평가, 사람 접촉 · 운반 중 팔레트 빠짐 |
| `docs/validation/2026-10-10-fleet-ta-ra.md` | TA/RA(막히면 우회): 영영 안 풀리는 교착 15 → 0 칸 (seed 300–304, 119 칸) |
| `docs/validation/2026-10-11-fleet-time-windows.md` | 교차 시간 창(v24): 60 s 이상 대기 1,542 → 576 (seed 600–604, 119 칸, v18y 대비), Isaac 대표 4 실행 |

## 자산

| 파일 | 쪽 | 만든 방법 |
|---|---|---|
| `assets/71_warehouse5.mp4` | 3 | ws1 `artifacts/20261008_fleet/runs/f2d_truth_seed0_overlay.mp4`(job 1916, 5대 완주 · 위반 0) 지도 칸, 4배속 |
| `assets/72_close_a.mp4`, `72_close_b.mp4` | 4 | 같은 실행(tw24_rack600)을 카메라만 두 대기 지점 위로 옮겨 다시 렌더(ws1 `~/w7deck/exp/runs/close_rack600`) 한 합성 영상에서 두 대기 장면을 자름 |
| `assets/73_{rack,shop,multi}.jpg` | 2, 5 | ws1 `artifacts/20261009_fleet_worlds/videos/tw24_*600.mp4` 150 s(시뮬레이션 450 s) 프레임의 지도 칸 |
| `assets/75_enc_top.jpg`, `75_enc_bottom.jpg` | 9 | 팀 엔코더 보드 PCB 3D 렌더 두 장(2026-10-14 팀원 공유, LCEDA) — 알파 배경을 검정으로, 여백만 잘라 900 px 로 줄임. 칩은 MT6701 SOP-8(사용자 확인) |
| `assets/74_rack600.mp4` | 7 | `tw24_rack600.mp4`(ws1 job 2441 · 2442) 지도 칸, 5배속 |

범례 색은 합성 스크립트(`tools/compose_fleet_video.py`, `tools/compose_world_video.py`)의 색 그대로다.
