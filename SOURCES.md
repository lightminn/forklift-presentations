# 자료와 출처

확인일: 2026-09-08.

## 1. 과제 원문

원래 지게차 작업 폴더의 `quest.txt`에 들어 있는 [「서울시립대 과제 — 주변 장애물을 고려한 최적의 팔레트 핸들링 경로 생성 및 제어」](https://docs.google.com/presentation/d/1BjoJLWmwd07ZJujZp4BPZrwBhx5tsnfmBpWdLMy2YrQ/edit).

Google Slides의 TXT와 11쪽 PDF를 다시 내려받아 확인했습니다. 센서 그림, Riibotics 배치 그림, A–D 접근 그림도 직접 확인했습니다.

| 과제 원문 | 반영 내용 | 새 발표자료 |
|---|---|---|
| 1·6쪽 | 주변 장애물 고려, 충돌 없는 빠른 경로, 삽입 중 포켓 지속 추적 | 1·2·6·9쪽 |
| 2·3쪽 | Gemini 335Le, 2D RPLIDAR A2 | 5쪽 |
| 4쪽 | Riibotics 마스트 중앙 카메라·포크 배치 참고 | 2쪽 |
| 5쪽 | 장난감 지게차 개조 또는 모바일 로봇 + 포크 | 3쪽 |
| 7쪽 | 인식 → 로봇 기준 위치 → 경로 → 삽입·적재 → 운반·하역 | 4쪽 |
| 8·9쪽 | 정면 직진 A, 충분한 거리에서 곡선 진입 B | 7쪽 |
| 10·11쪽 | 공간 확보를 위한 후진 C, 후방 장애물이 있는 D | 8쪽 |

## 2. 이미지

다음 자료는 과제 PDF의 이미지 객체 또는 그림 영역을 추출한 것입니다. 팀이 제작한 하드웨어나 실제 실험 결과로 표현하지 않았습니다. 사진 속 상표와 원래 설명은 유지했습니다.

| 파일 | 출처·처리 |
|---|---|
| `assets/riibotics-reference.jpeg` | 원문 4쪽의 이미지 객체 추출 |
| `assets/gemini-335le.jpeg` | 원문 2쪽의 이미지 객체 추출 |
| `assets/rplidar-a2.jpeg` | 원문 3쪽의 이미지 객체 추출 |
| `assets/case-a.png` | 원문 8쪽, 그림 영역 (110, 130, 445, 355) pt, 3배 렌더 |
| `assets/case-b.png` | 원문 9쪽, 그림 영역 (110, 75, 490, 342) pt, 3배 렌더 |
| `assets/case-c.png` | 원문 10쪽, 오른쪽 동작 영역 (352, 74, 486, 361) pt, 3배 렌더 |
| `assets/case-d.png` | 원문 11쪽, 두 대안 영역 (175, 75, 699, 347) pt, 3배 렌더 |

## 3. 후보 플랫폼

원래 지게차 작업 폴더의 `forklift_store_link.txt`에 들어 있는 [전동 지게차 판매 링크](https://smartstore.naver.com/skybaesong/products/11789657592)를 참고했습니다. 상품 상세 페이지를 조회하지 못했습니다. 링크의 검색어가 가리키는 어린이용 전동 지게차를 후보로만 다루었으며, 가격·배터리·허용 적재량·크기·조향 방식·구매 완료를 확정하지 않았습니다.

## 4. 기술 선택의 보조 근거

- [Orbbec Gemini 335Le 공식 제품 자료](https://www.orbbec.com/gemini-335le/): 스테레오 RGB-D 카메라 및 Ethernet/PoE 제품 구분을 확인했습니다. 이번 발표에서 수치 사양이나 근거리 측정 성능을 실측 결과처럼 사용하지 않았습니다.
- [SLAMTEC RPLIDAR A2 공식 자료](https://www.slamtec.com/en/lidar/a2/): 주변의 2D 거리 스캔 역할을 확인했습니다. A2 세부 모델별 차이를 고려해 거리·주파수 수치를 고정하지 않았습니다.
- [Nav2 공식 Navigation Plugins 문서](https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/navigation_plugins/setup_navigation_plugins/): Smac Hybrid A*가 회전반경과 차체 형상을 고려하는 계획기라는 점을 확인했습니다. 이를 조향 차량에 대한 검토 후보로 제안했으며, ROS 버전·플랫폼·시뮬레이터·최종 알고리즘을 선정하거나 구현하지 않았습니다.

## 5. 발표를 위해 작성한 개발 제안

다음 내용은 과제 원문에 명시된 확정 사양이 아닙니다.

- 상위 컴퓨터의 인식·계획과 MCU의 구동·승강·정지 분담
- 엔코더·조향각·포크 높이·리미트 스위치 등 추가 피드백 검토
- 규격 팔레트의 기하·깊이 검증부터 시작하는 인식 개발 순서
- 준비 자세까지의 경로 계획과 마지막 저속 삽입 제어의 분리
- 포켓 관측 소실 시 정지, 재관측 후 재정렬, 삽입 깊이 확인 뒤 승강
- A–D 각각 10회, 상황별 삽입·적재 성공 ≥ 9/10, 비의도 접촉 0회라는 초기 제안 목표
- 장비 확보 뒤 8주라는 예시 일정과 역할 분담

2D LiDAR만으로 모든 높이의 장애물을 보장할 수 없습니다. 포켓 추적의 가림·최소 관측 거리, 포크와 팔레트의 간극, 이동하는 카메라 좌표 변환, 적재 후 차체 외곽은 실제 하드웨어에서 확인해야 합니다. 최단거리나 Hybrid A* 채택만으로 전역 최소 작업 시간이 보장되지 않으므로, 작업 시간은 동일 조건의 반복 실험으로 비교하도록 제안했습니다.

## 6. 템플릿과 실행 코드

`zetin-drone-presentations/docs/presentations/ai-startup-camp-drone-10min/`의 `support.js`, `deck-stage.js`, `vendor/uos-slide-template/`를 재사용했습니다. 이 파일들은 참고 레포와 바이트 단위로 동일합니다. 드론 레포 자체는 수정하지 않았습니다.

- UOS 템플릿: 공식 `UOS_PTformat_B`, 1280 × 720, UOS 블루·로고·대각선 표지·본문 탭
- 한국어 글꼴: 템플릿에 포함된 Noto Sans CJK KR Regular/Medium/Bold
- React 18.3.1 및 ReactDOM 18.3.1: 로컬 `vendor/`에 포함, 각 MIT LICENSE 파일 동봉
- 새 본문 디자인·한국어 원고·생성기·실행 안내: 이번 발표자료를 위해 작성
