# 11-1 발표자료 (2026 로보월드 견학 보고)

11주차의 별도 발표(`week-11-1/`, `"part": 1`). 11주차 덱을 복사해(`tools/new_week.py 11 --part 1`) 새로 썼다. 구성: 견학 개요 → 무인 지게차(Multiway Robotics, 좁은 통로 대응 · 인식 구성 · 포크 간격 비교) → 6상 드론 모터(H3R) → 여러 모터를 묶는 통신(CubeMars · FASTECH) → 느낀 점. 표지 + 5장 · 290초. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처. 화면 문구와 원고는 직접 썼다(프로젝트 메모리 script-md-no-agy).
- `prepare_photos.py`: 팀이 찍은 부스 사진(로봇 저장소 `docs/roboworld/`, 로컬 전용)을 잘라 `assets/v02_multiway.jpg` · `v03_h3r.jpg` · `v04_ezipos.jpg` 로 저장한다. 저장할 때 EXIF(촬영 기기 · 시각)는 넘기지 않는다. `/home/light/anaconda3/bin/python prepare_photos.py <사진 폴더>`.
- 표지에는 리보틱스 로고를 넣지 않는다(사용자 요청 2026-11-11).
- `assets/h05_mounted.jpg`: 9주차 자산 그대로(바퀴 모터 축에 끼운 자석 링).

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
