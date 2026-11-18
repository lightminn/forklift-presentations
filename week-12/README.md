# 12주차 발표자료 (수업 주간 발표)

12주차 수업 발표(2026-11-18 발표용 재구성). 11주차를 복사해(`tools/new_week.py 12 --from 11`) 새로 썼고, 그 뒤 덧붙인 장들을 발표 직전에 하나의 흐름으로 다시 짰다(사용자: "지금까지 한 거 기준으로 덱 다시 만들어", 목표 7–8 분).

구성(표지 + 8장 · 410초): 01 지난주 피드백과 진행 → 02 실제 장비 첫 연결(MCU · Jetson · 카메라 · LiDAR 한 장) → 03 시뮬레이션 실패 해결(세 사례 한 표) → 04 인식 카메라 전후 비교 → 05 순응 타이어 차체 모형(전후 영상 + 정지 하중) → 06 시작 위치 찾기 시험(표 + 지도) → 07 좁은 통로 경로 개선 → 08 다음 주 계획. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 화면 문구는 `TXT`(agy, Gemini 4 Hydrogen High, 처음 보는 청중 기준 — 프로젝트 메모리 deck-self-explanatory-for-outsiders), 원고와 출처는 직접 썼다(script-md-no-agy).
- 02 장은 2026-11-17 실제 장비 측정이고 모터 · 엔코더는 아직 연결하지 않았다. 03–07 장은 Isaac 시뮬레이션 결과다. 05 장 정지 하중 그래프는 `load_chart()` SVG 다.
- 06 장 지도 그림 `assets/s06_map.png` 는 `make_map.py` 가 만든다: `/home/light/anaconda3/bin/python -I make_map.py <grid.npz> <val_s5.json> <compare.json> s06_map.png`. `grid.npz` 는 Drive `gdrive:forklift-archive/ws1-cleanup-20261110-an/an_f1.tar.zst` 의 `test_runs/live/bp2d_survey/hall_s5b_G0/bundle/grid.npz`(`rclone cat … | zstd -dc | tar -xf - <경로>`), 나머지 둘은 로봇 저장소 `docs/validation/assets/{b-p2d,reloc-observe-move}/`.
- 사진의 출처 · 라이선스 · 편집은 SOURCES.md 「사진 · 그림」.

## 영상

| 자리 | 파일 | 원본 (sha256) | 편집 |
|---|---|---|---|
| 05 | `s05_tyre.mp4` (22.0 s, 1812 × 458) | ws1 `/home/projects/forklift/test_runs/f2i/batch_f2i_22fe89be/video/f2iw_O_random_1_s8/run/transport.mp4` (8cb8c30e…, 111.3 s) 와 `f2iw_F2_random_1_s8/run/transport.mp4` (3d276fd1…, 165.3 s) | 시뮬 40 s 부터 `crop=1180:600:80:20,scale=900:-2`, 이전 모형은 111.3 s 뒤 마지막 프레임 유지 · 순응 타이어는 128 s 까지, 좌우로 붙여(사이 12 px 흰 띠) `setpts=PTS/4`, 칸마다 왼쪽 위 시뮬 시각과 끝 모서리 라벨(agy 문구 「경로 이탈」 · 「하역 도착」, drawtext `textfile`). 포스터 12 s |
| 07 | `s07_cusp.mp4` (25.6 s, 700 × 690) | ws1 `/home/projects/forklift/test_runs/acs/render_acs_d45bb1e1/acsAv_aisle_rack_s1/run/transport.mp4` (9b3bc418…) 와 `acsBv_aisle_rack_s1/run/transport.mp4` (e53ef020…) | 시뮬 40–245 s 를 `crop=700:340:160:130` 으로 자르고 위(기존) · 아래(개선)로 붙여 `setpts=PTS/8,fps=30`, 「기존 경로 · 개선 경로」 라벨은 화면에서 겹침 |

받는 법: ws1 공유 연결(`-o ControlMaster=no -o ControlPath=$HOME/.ssh/cm-%C`)로 `scp` 한 파일씩, 받은 뒤 sha256 대조.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
