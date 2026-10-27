# 9주차 발표자료 (수업 주간 발표)

9주차 수업 발표용 자료(2026-10-28). 8주차 피드백(로봇 저장소 `docs/references/week8_feedback.md`)에 답하는 구성이다: 피드백 대응표, 메인보드(3D 렌더 · 7주차 대비), MCU 코어 보드와 핀 배정, 전원 구성과 보호, 엔코더 자석 마운트, 미리 만든 지도 위 위치 추정, 콘솔과 상용 FMS 비교, 결론과 다음 주 계획. 표지 + 8장 · 445초. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처와 전원 흐름도 · 위치 오차 그래프(SVG). `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다. 화면 문구는 agy(Gemini 4 Argon)가 원자료로 썼고(전역 글쓰기 규칙), 원고는 직접 썼다(프로젝트 메모리 script-md-no-agy).
- `prepare_figures.py`: 팀 메인보드 그림(앞면 3D 렌더와 앞면 PCB 배치도만, 배치도에 비쳐 보이는 뒷면 실크 글자는 지움), 엔코더 어댑터 미리보기, 콘솔 캡처에서 `assets/h*` · `assets/c*` 를 잘라 만든다(conda base Python, PIL). `python prepare_figures.py <보드 그림 폴더> <preview.png> <캡처 폴더>`. 원본은 저장소에 넣지 않았다.
- 보드 뒷면 그림은 설계자 실크가 있어 쓰지 않는다(사용자 2026-10-28: 설계자는 화면에 표시하지 않음). 회로도 · PCB 를 공개 덱에 넣는 것은 사용자가 확인했다(같은 날).
- `assets/n08_aisle_stall.mp4`: ws1 `test_runs/riibotics/t2d_1b60df21/t2d_c3_aisle_rack_s4/run/view_quarter.mp4` 의 55–135 s 를 `ffmpeg -ss 55 -t 80 -vf setpts=PTS/2,fps=30,scale=960:-2 -crf 27` 로 다시 인코딩했다. 포스터는 39 s 프레임.
- `assets/d02_jetson.jpg` · `assets/d02_truck.jpg`: 8주차와 같은 파일(SOURCES.md).

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
