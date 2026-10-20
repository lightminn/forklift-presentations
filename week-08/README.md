# 8주차 발표자료 (수업 주간 발표)

8주차 수업 발표용 자료(2026-10-20). 앞 절반은 운용 콘솔(하는 일, 연결 구조, 화면 구성, 작업 지정과 진행, 직접 운전), 뒤 절반은 중간 미팅 뒤 리보틱스에서 받은 시연 시나리오의 분석과 구현 전략(시나리오 다섯 가지, 우리 차체로 축척 환산, 시나리오별 판단, Isaac 자율 임무 재현 영상과 시나리오별 Isaac 결과, 구현 순서, 리보틱스 확인 요청)이다(사용자 지시 2026-10-20 재구성, 같은 날 Isaac 재현 두 장 추가). 표지 + 12장 · 670초. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처와 구조도(SVG). `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다.
- `prepare_figures.py`: 콘솔 화면 캡처와 리보틱스 시나리오 PDF 에서 `assets/a*` · `assets/s*` 를 잘라 만든다(conda base Python, PIL, `pdftoppm`). `python prepare_figures.py <캡처 폴더> <시나리오 PDF>`. 캡처 원본과 PDF 는 저장소에 넣지 않았다.
- 콘솔 그림 일부는 가짜 차량(`console.mock_vehicle`)으로 찍었다(SOURCES.md).
- 시나리오 PDF 그림을 공개 덱에 넣는 것은 사용자가 확인했다(2026-10-20).
- `assets/i09_line.mp4` · `assets/i09_random.mp4`: ws1 `test_runs/riibotics/r4_line_1_s1` · `r4_random_2` 의 `transport.mp4`(Isaac 탑뷰 1280 × 720)를 장면 부분만 잘라(850 × 720 at x 200 / 1150 × 640 at x 120) 6배속 · 540 px 높이 · H.264 CRF 27 로 다시 인코딩했다(`ffmpeg -vf crop,setpts=PTS/6,fps=30,scale`). 포스터는 12 s 프레임.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
