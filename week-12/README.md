# 12주차 발표자료 (수업 주간 발표)

12주차 수업 발표(2026-11-17). 11주차를 복사해(`tools/new_week.py 12 --from 11`) 새로 썼다. 구성은 11주차 피드백(장비를 실제로 써 볼 것 · SLAM 자기 위치를 다양하게 시험 · 논문)에 답하는 순서다: 피드백과 이번 주 진행 → MCU 보드 첫 연결 → Jetson과 센서 첫 연결 → 시작 위치 찾기 시험 확대 → 좁은 통로 방향 전환 경로 개선 → 다음 주 계획. 표지 + 6장 · 370초. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처. 화면 문구와 원고는 직접 썼다(프로젝트 메모리 script-md-no-agy).
- 02 · 03 장은 2026-11-17 실제 장비 측정이고, 모터 · 엔코더는 아직 연결하지 않았다(메인보드 · 부품 11월 20일 발송). 04 · 05 장은 Isaac 시뮬레이션 결과다.
- 03 장 막대 그래프는 `build_deck.py` 의 `cycle_chart()` 가 그리는 SVG 다.
- 사진의 출처 · 라이선스 · 편집은 SOURCES.md 「사진 · 그림」.

## 영상

| 자리 | 파일 | 원본 (sha256) | 편집 |
|---|---|---|---|
| 05 | `s05_cusp.mp4` (25.6 s, 700 × 690) | ws1 `/home/projects/forklift/test_runs/acs/render_acs_d45bb1e1/acsAv_aisle_rack_s1/run/transport.mp4` (9b3bc418…, 1280 × 720 · 60 fps, 297 s) 와 `acsBv_aisle_rack_s1/run/transport.mp4` (e53ef020…, 277 s) | 두 영상 모두 시뮬 40–245 s 를 `crop=700:340:160:130` 으로 자르고 위(끔) · 아래(켬)로 붙임(사이 10 px 흰 띠), `setpts=PTS/8,fps=30`, `-crf 27`. 포스터는 9 s 프레임. 「기존 · 개선」 글자는 영상에 굽지 않고 화면에서 겹침 |

받는 법: ws1 공유 연결(`-o ControlMaster=no -o ControlPath=$HOME/.ssh/cm-%C`)로 `scp` 한 파일씩, 받은 뒤 sha256 대조(두 값 모두 총괄이 준 값과 일치).

```bash
ffmpeg -ss 40 -t 205 -i A.mp4 -ss 40 -t 205 -i B.mp4 -filter_complex \
  "[0:v]crop=700:340:160:130,pad=700:350:0:0:white[a];[1:v]crop=700:340:160:130[b];[a][b]vstack=inputs=2,setpts=PTS/8,fps=30" \
  -an -c:v libx264 -crf 27 -preset slow -pix_fmt yuv420p -movflags +faststart s05_cusp.mp4
```

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
