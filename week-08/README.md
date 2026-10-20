# 8주차 발표자료 (수업 주간 발표, 초안)

8주차 수업 발표용 초안(2026-10-20). 운용 콘솔을 중심으로 하고 하드웨어는 엔코더 자석 어댑터만 다룬다(사용자 지시 2026-10-20: GUI와 하드웨어, 안전보다 기능 · 실용, 10장 내외, 장당 밀도는 이전 주와 비슷하게). 표지 + 10장 · 530초. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처와 구조도(SVG). `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다.
- `prepare_figures.py`: 콘솔 화면 캡처와 어댑터 미리보기에서 `assets/a*` 를 잘라 만든다(conda base Python, PIL). `python prepare_figures.py <캡처 폴더> <preview.png>`. 캡처 원본은 저장소에 넣지 않았다.
- 화면에 「임시 화면」 표시가 붙은 그림은 가짜 차량(`console.mock_vehicle`)으로 찍은 것이다. Isaac 실시간 실행기 녹화로 바꾼 뒤 표시를 뗀다. 8쪽은 영상 자리표시다.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
