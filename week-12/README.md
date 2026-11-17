# 12주차 발표자료 (수업 주간 발표)

12주차 수업 발표(2026-11-17). 11주차를 복사해(`tools/new_week.py 12 --from 11`) 새로 썼다. 구성은 11주차 피드백(장비를 실제로 써 볼 것 · SLAM 자기 위치를 다양하게 시험 · 논문)에 답하는 순서다: 피드백과 이번 주 진행 → MCU 보드 첫 연결 → Jetson과 센서 첫 연결 → 시작 위치 찾기 시험 확대 → 시작 위치 판정 지도와 대응 → 시뮬레이션 실패 수정(사용자 요청, 같은 장면 · 조건 전후 비교) → 사례 1 전후 화면 → 사례 3 전후 화면 → 좁은 통로 경로 개선 → 다음 주 계획. 표지 + 10장 · 550초. 화면 문구는 2026-11-18 부터 agy 가 쓴다(`build_deck.py` 의 `TXT`), 원고는 직접 쓴다. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처. 화면 문구와 원고는 직접 썼다(프로젝트 메모리 script-md-no-agy).
- 02 · 03 장은 2026-11-17 실제 장비 측정이고, 모터 · 엔코더는 아직 연결하지 않았다(메인보드 · 부품 11월 20일 발송). 04–09 장은 Isaac 시뮬레이션 결과다.
- 03 장 막대 그래프는 `build_deck.py` 의 `cycle_chart()` 가 그리는 SVG 다.
- 05 장 지도 그림 `assets/s04_map.png` 는 `make_map.py` 가 만든다: `/home/light/anaconda3/bin/python -I make_map.py <grid.npz> <val_s5.json> <compare.json> s04_map.png`. `grid.npz` 는 Drive `gdrive:forklift-archive/ws1-cleanup-20261110-an/an_f1.tar.zst` 의 `test_runs/live/bp2d_survey/hall_s5b_G0/bundle/grid.npz` (`rclone cat … | zstd -dc | tar -xf - <경로>`), 나머지 둘은 로봇 저장소 `docs/validation/assets/{b-p2d,reloc-observe-move}/`.
- 사진의 출처 · 라이선스 · 편집은 SOURCES.md 「사진 · 그림」.

## 영상

| 자리 | 파일 | 원본 (sha256) | 편집 |
|---|---|---|---|
| 08 | `s07_stall.mp4` (22.8 s, 1412 × 420) | ws1 `/home/projects/forklift/test_runs/render12_f7566ed4/gcbOff_random_1_s24/run/view_quarter.mp4` (b50b428d…, 1280 × 720 · 60 fps, 234.48 s) 와 `gcbOn_random_1_s24/run/view_quarter.mp4` (2d214273…, 217.17 s) | 두 영상의 시뮬 195 s 부터 `crop=700:420:300:40`, 끔은 끝에 6 s · 켬은 끝 뒤 마지막 프레임을 이어 붙여 같은 길이로, 좌우로 붙임(사이 12 px 흰 띠), `setpts=PTS/2,fps=30`, `-crf 26`. 각 칸 왼쪽 위 시뮬 시각(`%{eif:min(195+t,234 또는 217):d} s`)과 끝 모서리 라벨(agy 문구, drawtext `textfile`)을 넣음. 포스터 8 s |
| 09 | `s05_cusp.mp4` (25.6 s, 700 × 690) | ws1 `/home/projects/forklift/test_runs/acs/render_acs_d45bb1e1/acsAv_aisle_rack_s1/run/transport.mp4` (9b3bc418…, 1280 × 720 · 60 fps, 297 s) 와 `acsBv_aisle_rack_s1/run/transport.mp4` (e53ef020…, 277 s) | 두 영상 모두 시뮬 40–245 s 를 `crop=700:340:160:130` 으로 자르고 위(끔) · 아래(켬)로 붙임(사이 10 px 흰 띠), `setpts=PTS/8,fps=30`, `-crf 27`. 포스터는 9 s 프레임. 「기존 · 개선」 글자는 영상에 굽지 않고 화면에서 겹침 |

받는 법: ws1 공유 연결(`-o ControlMaster=no -o ControlPath=$HOME/.ssh/cm-%C`)로 `scp` 한 파일씩, 받은 뒤 sha256 대조(두 값 모두 총괄이 준 값과 일치).

```bash
ffmpeg -ss 40 -t 205 -i A.mp4 -ss 40 -t 205 -i B.mp4 -filter_complex \
  "[0:v]crop=700:340:160:130,pad=700:350:0:0:white[a];[1:v]crop=700:340:160:130[b];[a][b]vstack=inputs=2,setpts=PTS/8,fps=30" \
  -an -c:v libx264 -crf 27 -preset slow -pix_fmt yuv420p -movflags +faststart s05_cusp.mp4
```

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
