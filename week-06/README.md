# 6주차 발표자료

소프트웨어(시뮬레이션) 진행 보고. 7장 · 345초. 하드웨어 이야기는 넣지 않는다(사용자 지시 2026-10-06). 구성과 검토 기록은 [PLAN.md](PLAN.md).

- `build_deck.py`: 본문·원고·출처. `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다.
- `prepare_clips.py`: 4·6·7쪽 영상과 2쪽 카메라 화면을 로봇 저장소의 Isaac 렌더에서 잘라 만든다(ffmpeg).
  `python prepare_clips.py /path/to/forklift`
- `assets/21_slam_map_pair.mp4`: 5주차에 만든 지도 작성 영상(ws1 Slurm 585, 3쪽).
- `SOURCES.md`, `VALIDATION.md`: 출처와 검증 기록.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
