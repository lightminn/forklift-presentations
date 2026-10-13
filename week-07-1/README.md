# 리보틱스 중간 미팅 발표자료 (7주차 별도 발표)

리보틱스 중간 미팅(2026-10-14, 형식은 중간 발표)용 기술 점검 자료. 본 발표 18장 · 1,025초 + 부록 2장, 요약 → 소프트웨어 → 하드웨어(소프트웨어의 실차 구현) → 결론(개발 일정) → 질의응답 순(2026-10-12). 7주차 주간 발표는 따로 `week-07/` 에 만든다. `week.json` 의 `part: 1` 로 목록에는 `07-1` 로 보이고, `latest/` 는 주간 발표만 가리킨다. 구성과 근거는 [PLAN.md](PLAN.md), 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처. `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다.
- `QNA.md`: 발표자용 예상 질문과 답변 (장별, 출처 기록의 사실만). 덱 화면 · 원고와 수치가 바뀌면 같이 고친다.
- `prepare_figures.py`: 그림(PNG, matplotlib) — 시스템 · 구조도 · 목적지 방향 맞춤(`python prepare_figures.py /path/to/forklift`), `stages` · `hardware` · `brief` · `thumbs`(2쪽 단계 그림 조각). 모드별 설명은 파일 첫머리. 2 · 3 · 4 · 7 · 17쪽의 단계 카드 · 흐름 · 계기판 · 거리 그림 · 간트 차트는 `build_deck.py` 가 HTML 로 그린다.
- `prepare_clips.py`: 7쪽 근접 깊이 클립(`depth`), 3쪽 운반 임무(`mission`), 8쪽 새 장애물(`obstacle`), 부록 2 SLAM(`slam`) 영상을 자른다(ffmpeg). 입력 위치는 파일 첫머리 설명. 후진 장면(9쪽)은 `prepare_reverse_clip.py`, 접근 상황 A–D(10 · 11쪽)는 `prepare_ad_clips.py`.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
