# 2주차 · 자율 지게차 개발 계획

발표 주소: https://lightminn.github.io/forklift-presentations/week-02/

UOS 공식 템플릿을 사용한 13장·10분 45초의 개발 제안 발표이다. 과제 개요, 하드웨어 구성, ROS 2 SLAM, 팔레트 인식·경로 생성·삽입 제어, A–D 접근 조건, 평가 계획 및 개발 일정으로 구성한다.

- [build_deck.py](build_deck.py): 본문·원고·시간 배분의 편집 원본.
- [SCRIPT.md](SCRIPT.md): 장별 한국어 발표 원고와 출처.
- [SOURCES.md](SOURCES.md): 자료 출처와 제안·확정 사항의 구분.
- [VALIDATION.md](VALIDATION.md): 이 자료의 검증 기록.
- `index.html`, `SCRIPT.md`, `slide-metadata.json`: 생성 파일. 직접 수정하지 않는다.
- `week.json`: 주차별 목록에 표시할 제목·요약·공개 상태.

이 폴더에서 `python3 build_deck.py`로 2주차만 재생성할 수 있다. 레포 루트의 `python3 build_deck.py`는 모든 주차와 목록을 재생성한다.

레포 루트에서 `bash present.sh`를 실행한 후 `http://127.0.0.1:8765/week-02/`를 연다. `F`는 전체화면, 방향키는 슬라이드 이동, `Home`·`End`는 처음·마지막 장, `1`–`9`·`0`은 1–10쪽 이동이다. 발표 원고는 `SCRIPT.md`를 별도로 열어 사용한다.

7·8쪽은 원본 구글 슬라이드의 개별 지게차·팔레트 이미지로 A–D 접근 동작을 자동 반복한다. 재생 제어 버튼은 없다. 10쪽은 원문 근거가 없는 시험 횟수·목표 성공률을 제외한 평가 계획이다. 자료는 로봇 구현 또는 성능 실측 결과를 의미하지 않는다.

다음 주 자료는 이 폴더를 덮어쓰지 않고 [레포의 주차 추가 절차](../README.md)에 따라 생성한다.
