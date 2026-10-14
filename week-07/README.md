# 7주차 발표자료 (수업 주간 발표)

7주차 수업 발표(2026-10-14)용 자료. 하드웨어만 다룬다(사용자 지시 2026-10-14): 전원과 제어 구성, 메인보드(DRV8244 4채널), MT6701 바퀴 엔코더 보드, KTH7801 절대 엔코더 보드, STDS(Single-ended To Differential Signal) 보드, 차동 전송 근거, 클럭 · 케이블 지연 계산, 5 V 송전과 RJ50, 커넥터 핀 간격 질문. 18장 · 965초. 같은 주의 리보틱스 중간 미팅 자료는 [`../week-07-1/`](../week-07-1/)에 따로 있다. 출처는 [SOURCES.md](SOURCES.md), 확인 기록은 [VALIDATION.md](VALIDATION.md).

- `build_deck.py`: 본문 · 원고 · 출처와 그래프(SVG). `index.html`, `SCRIPT.md`, `slide-metadata.json` 을 만든다. 클럭 한계 계산(칩 지연 합 · 케이블 속도)도 이 파일의 상수에서 나온다.
- `prepare_figures.py`: 팀 EasyEDA 내보내기(PNG)에서 3D 렌더의 검은 여백을 자르고, 회로도를 그린 부분만 남기고, 메인보드 회로도를 블록별로 잘라 `assets/8x_*` 를 만든다(conda base Python, PIL · numpy). `python prepare_figures.py <팀 자료 폴더>`.
- 16쪽 핀 간격 질문의 그림(`assets/75_enc_*`)은 KTH7801 보드의 이전 판(2.54 mm, 1.27 mm V1.0.1)이다.
- 이 주의 다중 지게차 교통 관리 장과 영상은 99fc8b1 까지 있었고 하드웨어 전용으로 바꾸며 뺐다(그 커밋에서 되살릴 수 있다).

전체 생성 및 배포 절차는 [레포 안내](../README.md)를 따른다.
