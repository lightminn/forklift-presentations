# 7주차 발표자료 (수업 주간 발표)

7주차 수업 발표(2026-10-14)용 자료. 다중 지게차 교통 관리(시뮬레이션)와 구동 보드 PCB. 10장 · 580초. 같은 주의 리보틱스 중간 미팅 자료는 [`../week-07-1/`](../week-07-1/)에 따로 있다. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처. `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다.
- `prepare_clips.py`: 다중 지게차 Isaac 렌더에서 지도 칸만 잘라 영상 · 정지 화면을 만든다(ffmpeg). 렌더가 있는 ws1 에서 `python3 prepare_clips.py /home/projects/forklift/artifacts <out>` 로 돌리고 결과를 `assets/` 로 가져온다. 입력은 파일 첫머리 설명.
- 9쪽(구동 보드 PCB)은 팀 자료를 받은 뒤 채운다. 그 전까지 `week.json` 은 `draft`.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
