# 6주차 발표자료

시뮬레이션 진행 보고. 8장 · 450초. 하드웨어는 마지막 장의 다음 작업으로만 다룬다(사용자 지시 2026-10-07). 센서는 과제 규격(RGB-D 카메라 1대 · 2D LiDAR 1대)만 쓰고, LiDAR 높이보다 낮은 바닥 장애물은 없다고 가정한다. 구성과 검토 기록은 [PLAN.md](PLAN.md)·[VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문·원고·출처. `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다.
- `prepare_clips.py`: 영상·카메라 화면을 로봇 저장소의 Isaac 렌더에서 잘라 만든다(ffmpeg).
  - `python prepare_clips.py /path/to/forklift single`: LiDAR 1대 실행(ws1 `l7_single`, 로봇 저장소 bc4cc64)의 3·4·6쪽 영상
  - 2쪽 카메라 사진과 5쪽 영상은 `main()` 안의 해당 줄(5쪽은 df109cf `--draw-odometry` 재합성 영상)
- `SOURCES.md`, `VALIDATION.md`: 출처와 검증 기록. VALIDATION.md 의 아래쪽(2026-10-07)이 최종 구성이다.

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
