# 11-1 발표자료 출처

| 장 | 내용 | 출처 |
|---|---|---|
| 표지 · 01 | 행사 일정 · 장소 · 규모 (11월 4–7일, 고양 킨텍스 1전시장 3–5홀, 402개 기업 1,198개 부스) | inews24 「개막 22일 앞둔 '2026 로보월드'」 https://inews24.com/view/2014979 , kidd.co.kr 보도 |
| 02 | 형태별 작업공간 Ast: 카운터 밸런스 타입 SE 3,150 mm · E 4,100 mm, 3방향 K 1,750 mm | Multiway Robotics 부스 벽면 사진(팀 촬영 11-06) |
| 02 | 로보월드 출품 O20(360도 회전 · 횡행 · 사행, 협소한 작업장용), K16(3방향, 랙 사이 1,750 mm) | kidd.co.kr 「[2026 로보월드] 멀티웨이 로보틱스, 무인지게차로 물류 현장의 안전·인력난 해소 지원」 2026-11-07 https://kidd.co.kr/news/248067 |
| 02 | 레이저 SLAM + 비전 위치 추정, 팔레트 크기에 맞춘 포크 간격 자동 조절 (MW-Q20) | Forkliftaction 「Multiway Robotics: A Smarter Alternative to Manual Forklifts」 2026-05-21 https://www.forkliftaction.com/news/newsdisplay.aspx?nwid=31563 — **광고 기사(업체 제공 문구)** |
| 02 | 우리 지게차 최대 조향각 15° · 최소 회전 반경 약 2.5 m · 포크 간격 5.5–38 cm 수동 조절, 한 간격으로 EPAL 6 · T11 동시 대응 불가 | week-07-1 `build_deck.py` 차체 실측 표 · 원고, 로봇 저장소 T11 Isaac 결과(PR #82 · #85) |
| 03 | 6상 모터를 쓰는 이유(작은 모터에 엔코더를 넣기 어려워 홀 센서만 쓰고 상을 늘림), 3상 드론 모터 업체가 6상 개발 중 | 팀 인터뷰 메모(로봇 저장소 `docs/roboworld/인터뷰 생각나는대로.txt`, 로컬 전용) |
| 03 | 포스터 항목(고장 허용 · 토크 안정 · 진동 감소 · 이중 채널 · 열 분산, ESC A · B 가 A1 B1 C1 · A2 B2 C2 를 나눠 구동) | H3R 부스 포스터 사진(팀 촬영 11-06) |
| 03 | 바퀴 모터 축 지름 3 mm, 축에 끼운 PLA 링 위 자석 + MT6701 | week-09 `build_deck.py` 06 장 · `assets/h05_mounted.jpg` |
| 04 | AK 모터 CAN 동시 연결 문제, 내년 초 하드웨어 변경 · 내년 중 CAN FD 출시 예정 | 팀 인터뷰 메모 |
| 04 | FASTECH Ezi-Pos 의 EtherCAT · Ethernet · CC-Link IE TSN · PROFINET 드라이버와 maxon 모터 | 팀 인터뷰 메모(maxon 모터 합본 판매, 이더넷 · 이더캣 드라이버), 부스 사진(팀 촬영 11-07) |
| 04 | 우리 구조: H743 이 DRV8244 4개를 직접 구동, Jetson ↔ MCU 전송로 미정(USB CDC 또는 UART) | 로봇 저장소 `docs/interfaces/2026-10-22-mcu-link-contract.md`, week-11 `build_deck.py` 09 장 |

부스 답변은 현장에서 들은 말을 메모로 옮긴 것이며 업체의 공식 자료로 확인한 값이 아니다. 인터뷰 메모의 "모터 드라이버 회사" 항목은 내용이 비어 있어 넣지 않았다.
