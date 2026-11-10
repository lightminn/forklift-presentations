# 11주차 출처

쪽별 출처의 전체 목록은 `build_deck.py` 의 각 장 `sources` 와 발표자 노트의 [Sources] 블록이다(`SCRIPT.md` 에는 넣지 않는다).

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
| `week-09/assets/h03_layout_top.jpg` | 06 장 그림 |

## 사용자 · 총괄 전달

- 2026-11-10 승인 개요(쪽 구성, HW 는 "부품·PCB 발주 완료"만).
- 2026-11-10: 05 장은 넣는다, 06 장은 "PCB·부품 발주 완료"와 "11월 20일 발송 예정"(도착일 아님)만 둔다(목록 · 수량 없음).
- 2026-11-10 총괄: 02 장 시연 렌더는 F1 차단을 개발 설정으로 끈 실행(`F1_AUTONOMY=allow`, 시뮬 개발 실행 한정)이다. 화면 문구 "시작 위치를 스스로 찾고 출발"은 그대로 둔다. 스캔 겹침은 새 합성 없이 콘솔 화면 녹화(지도 위 LiDAR 점)로 대신하고, 후보 화면은 다시 찍는다.

## 영상

| 파일 | 원본 |
|---|---|
| `t04_trailer.mp4` | ws1 riib 배치 `rx_6e6d8e1c` 의 `rx_B_trailer_s0`(완주) `transport.mp4`, 보관본 `gdrive:forklift-archive/ws1-cleanup-20261031-a/t_mp4.tar.zst` 에서 꺼냄(md5 be3f7bb08a7826c04490d87581132191), 4배속 |
| `t05_replan.mp4` | ws1 riib 배치 `rc_95e61a74` 의 `rc_G_aisle_rack_s11`(완주, 운반 재계획 124 s · 복귀 재계획 221 s) `transport.mp4`, 보관본 `gdrive:forklift-archive/ws1-cleanup-20261110-n/n_rc.tar.zst` 에서 꺼냄(md5 6bba6542ebf3b1039c3659f54de93f8a), 198–242 s 3배속 |
| `r02_reloc.mp4` · `r02_console.mp4` | ws1 렌더 잡 17491 `d11_reloc_auto`: B-P2d seed 5 시작 val4_008 에서 사람 없이 위치 확정 뒤 P-1:D-1 done(시뮬 247 s). F1 차단을 개발 설정으로 끈 실행(`F1_AUTONOMY=allow`). 원본 md5 c903495b… · de4b0265… |
| `r02_candidates.png` | ws1 잡 17526 `d11_reloc_pick2`: val4_077(B-P2d 에서 운용자 요청), 후보 4개 화면(md5 266ff57d…) |
| `t03_queue.mp4` | ws1 잡 17491 `d11_queue_line`: line_m 대기열 세 임무 모두 done(시뮬 466 s), 원본 md5 43a5a03e… |

## 화면에 쓰지 않은 사실

- 03 장 8주차 수치는 riib 장면(line_1–3 · random_1–3)의 팔레트 하나 임무이고, 이번 수치는 line_m · random_m 세 임무 세션이다. 단위가 달라 표에 "1개씩" · "3개 연속"으로 나눠 적었다.
- 02 장의 시작 위치 찾기 검증(84곳)은 확정 뒤 10 s 정지까지이고, 출발 장면은 따로 찍는 시연 렌더다.
