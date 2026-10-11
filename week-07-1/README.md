# 리보틱스 중간 미팅 발표자료 (7주차 별도 발표)

리보틱스 중간 미팅(2026-10-14, 형식은 중간 발표)용 기술 점검 자료. 14장 · 870초. 7주차 주간 발표는 따로 `week-07/` 에 만든다. `week.json` 의 `part: 1` 로 목록에는 `07-1` 로 보이고, `latest/` 는 주간 발표만 가리킨다. 구성과 근거는 [PLAN.md](PLAN.md), 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처. `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다.
- `prepare_figures.py`: 9쪽 경로 도식(`figures/*.svg`). 로봇 저장소의 실행 기록과 플래너로 그린다 — `python prepare_figures.py /path/to/forklift` (numpy 필요, conda base). 도식은 `build_deck.py` 가 페이지에 직접 넣는다(덱 글꼴 적용).
- `prepare_clips.py`: 6쪽 근접 깊이 클립(`depth`)과 10쪽 운반 임무 영상(`mission`)을 자른다(ffmpeg). 입력 위치는 파일 첫머리 설명.
- 6주차에서 그대로 쓰는 영상: `45_slam_error.mp4`(7쪽), `46_new_obstacle_single.mp4`(8쪽).

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
