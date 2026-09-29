# 5주차 · 개발 진행 보고 (초안)

UOS 공식 템플릿을 사용한 9장·10분 10초의 진행 보고이다. 이번 주 핵심 두 가지만 다룬다: 하드웨어 실측
(차체 · 포크·동봉 팔레트 · 조종기 버튼별 신호, 작성 중)과 2D LiDAR 시뮬레이션(스캔 · 지도 작성 ·
지도 비교 · 위치 추정 오차), 마지막에 중간 미팅 확인 사항. 구성의 근거는 [PLAN.md](PLAN.md).

**시뮬레이션 장은 기술 실증이다.** 개발의 큰 그림은 개발 로드맵(실물 H0/H1 → 하위 제어 → M4)을 따르며,
Isaac 공장 홀과 오프라인 slam_toolbox 재생은 M4에 필요한 기술을 미리 확인한 것이지 채택한 구성이 아니다.
해당 장에는 모두 같은 회색 꼬리표(기술 실증 · Isaac Sim 합성 장면 · 로봇 제어는 시뮬레이터 정답 위치)를 붙였다.

- [build_deck.py](build_deck.py): 본문·원고·시간 배분의 편집 원본. 도표는 이 파일의 수치에서 그린다.
- [prepare_videos.py](prepare_videos.py): Isaac 기록에서 스캔 영상과 지도 비교 영상을 그린다(NumPy·Pillow·ffmpeg).
- [SCRIPT.md](SCRIPT.md): 장별 한국어 발표 원고와 출처.
- [SOURCES.md](SOURCES.md): 수치와 화면의 출처.
- [VALIDATION.md](VALIDATION.md): 이 자료의 검증 기록.
- [PLAN.md](PLAN.md): 구성 계획과 교차검증 기록.
- `index.html`, `SCRIPT.md`, `slide-metadata.json`: 생성 파일. 직접 수정하지 않는다.

## 남은 작업

- 2–4쪽: 차체 · 포크·동봉 팔레트 실측과 버튼별 신호 측정 결과로 자리 표시를 교체한다.
