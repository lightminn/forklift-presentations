# 11주차 발표자료 초안 (수업 주간 발표)

11주차 수업 발표 초안(2026-11-10, 10주차 발표 없음). 9주차를 복사해(`tools/new_week.py 11`) 새로 썼다. 구성은 사용자 승인 개요: 이번 주에 달라진 것(썸네일 셋) → 시작 위치를 스스로 찾음 → 인식·SLAM 켠 연속 이송 → 리보틱스 트레일러 장면 완주 → 막혀도 다시 계획함 → 부품·PCB 발주 완료 → 다음 주. 표지 + 7장 · 380초. 상태 `published`. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처. 화면 문구와 원고는 직접 썼다(프로젝트 메모리 script-md-no-agy). 아직 없는 Isaac 영상은 `placeholder()` 상자(주황 점선, "영상 자리")로 두었다. 영상을 자르면 `placeholder(...)` 를 `video(...)` 로 바꾸고 1쪽 `thumb()` 도 포스터 그림으로 바꾼다.
- `assets/t04_trailer.mp4` · `t05_replan.mp4`(+ `_poster.jpg`, `t04_trailer_thumb.jpg`): 보관본에서 꺼낸 Isaac 탑뷰(1280 × 720, 60 fps)를 로컬 ffmpeg 로 잘라 다시 인코딩했다. 트레일러는 `rx_6e6d8e1c/rx_B_trailer_s0/run/transport.mp4`(md5 be3f7bb0…) 전체를 `crop=520:640:420:0,setpts=PTS/4,fps=30,scale=-2:540 -crf 27`(26.8 s), 통로 재계획은 `rc_95e61a74/rc_G_aisle_rack_s11/run/transport.mp4`(md5 6bba6542…) 의 198–242 s(복귀 재계획 221 s)를 `crop=720:420:560:170,setpts=PTS/3,…`(14.7 s). 포스터는 18 s · 8 s 프레임, 1쪽 썸네일은 트레일러 72 s 프레임을 `crop=1060:603:220:0` 으로 가로로 자름.
- `assets/h03_layout_top.jpg`: 9주차 자산 그대로(팀 메인보드 PCB 배치도 앞면).

## 영상 (모두 넣음)

| 자리 | 파일 | 원본 (md5) | 편집 |
|---|---|---|---|
| 02 | `r02_reloc.mp4` (32.9 s) | ws1 /home/projects/forklift/test_runs/live/deck11/r_bcb21c87/s/d11_reloc_auto/epoch_1/run/transport.mp4 (c903495b938dbfd702d0809afba8ca1a, 1280 × 720, 시뮬 247 s) | `crop=420:570:560:120,setpts=PTS/8,fps=30,tpad=start_duration=2:start_mode=clone,scale=-2:540` (8배속, 처음 2 s 정지) |
| 02 | `r02_console.mp4` (32.9 s) | ws1 /home/projects/forklift/test_runs/live/deck11/r_bcb21c87/s/d11_reloc_auto/console_rec/console.mp4 (de4b0265c02e1f7adffb2ff5816872fd, 1600 × 950, 1 fps 927 장) | `crop=1064:810:196:130,setpts=PTS/30,…,tpad=2 s` — 1 장이 벽시계 1 s(시뮬 약 0.27 s)라 30 배면 탑뷰 8배속과 거의 같음, 첫 장(지도 위 LiDAR 점이 겹친 위치 확정 화면)을 2 s 보임 |
| 02 | `r02_candidates.png` | ws1 /home/projects/forklift/test_runs/live/deck11/r_bcb21c87/retry/s/d11_reloc_pick2/console_rec/console.mp4 (266ff57def789354ff7c690e9002af26) 28 s 프레임 | `crop((208,140,1248,790))` → 780 px |
| 03 | `t03_queue.mp4` (38.9 s) | ws1 /home/projects/forklift/test_runs/live/deck11/r_bcb21c87/s/d11_queue_line/live/epoch_1/run/transport.mp4 (43a5a03e10e0e5cbb18ff5e21ac2d5a6, 시뮬 466 s) | `crop=1000:720:180:0,setpts=PTS/12` (12배속) |
| 04 | `t04_trailer.mp4` (26.8 s) | 위 (be3f7bb0…) | 4배속 |
| 05 | `t05_replan.mp4` (12.8 s) · `t05_overview.jpg` · `t05_key1–4.jpg` | 위 (6bba6542…) + 같은 실행의 `plan_history.json` | `make_replan.py`: Isaac 겹침선은 복귀 경로를 한 색으로 그려서, 204.7 s 계획(앞 전환점부터)을 주황, 221.1 s 새 계획을 하늘색으로 다시 그림(재계획 뒤 주황은 흐리게). 확대 범위 480 × 270 at (560, 220) → 960 × 540, 200–236 s 중 219–224 s 는 실제 속도 · 나머지 4배속; 장면 전체 그림에 확대 범위 흰 사각형; 핵심 장면 218.6 · 221.0 · 221.45 · 223.0 s 에 모서리 번호 |

렌더: ws1 잡 17491(18:44–19:11, 세 실행 모두 ended, 임무 4/4 done)과 후보 화면 재시도 17526(val4_077, 19:29 끝), 스냅숏 `snapshots/deck11_bcb21c87`. 첫 후보 실행(val4_002)은 녹화기 Chrome 이 늦게 붙어 후보 화면을 놓쳤다 — 재시도에서 Chrome 을 먼저 띄우고 탐침이 후보를 본 뒤 30 s 기다렸다 놓게 했다(`reloc_place2`).

ws1 `test_runs/live/deck11/`: `submit.sh`(스냅숏 `snapshots/deck11_<main sha8>` 를 `git archive` 로 만들고, `make_runs.py` 로 목록, `isaac_bundle.py check`, `sizes live --runs 3 --run-min 45`; `SUBMIT=1` 일 때만 sbatch), `deck11_session.sh`(세 모드 래퍼, `REC=1` 이면 콘솔 녹화), `record_console.py`(헤드리스 Chrome 이 콘솔을 보기만 하며 1 fps 로 찍어 mp4). 02 렌더는 F1 차단을 개발 설정으로 끈 실행(`F1_AUTONOMY=allow`, 총괄 2026-11-10)이다.

자르기는 9주차와 같은 방식(`ffmpeg -vf crop,setpts=PTS/N,fps=30,scale=-2:540 -crf 27`, 포스터는 대표 프레임)으로 한다.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.

- `make_replan.py`: 05 장 영상 · 그림을 만드는 스크립트(conda base, PIL · numpy · ffmpeg). `python make_replan.py <transport.mp4> <plan_history.json> <출력 폴더>`. 화면 좌표 `u = 576 − 76 (y − y_e)`, `v = 368 − 76 (x − x_e)` 는 Isaac 경로 픽셀(225 s 프레임)에 맞춘 값이다(중앙 오차 0.6 px). 원자료는 `gdrive:forklift-archive/ws1-cleanup-20261110-n/n_rc.tar.zst` 에서 꺼낸 사본(ws1 `~/archive-work/deck11b/`).
- `assets/h02_board_top.jpg`: 9주차 자산 그대로(메인보드 3D 렌더 앞면).
