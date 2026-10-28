# 9주차 출처

쪽별 출처의 전체 목록은 `build_deck.py` 의 각 장 `sources` 와 발표자 노트의 [Sources] 블록이다(`SCRIPT.md` 에는 넣지 않는다).

## 팀 메인보드 자료 (2026-10-28 사용자 전달, 원본은 로봇 저장소 `docs/references/team-hardware/2026-10-28/` 에 로컬 전용)

| 자료 | 쓴 곳 |
|---|---|
| 3D 렌더 앞면 (실크 V1.0.0) | 2쪽 그림 (`h02_board_top.jpg`) |
| PCB 배치도 앞면 (외곽 114.173 × 91.567 mm, 헤더 간격 33.0 mm) | 3쪽 그림 (`h03_layout_top.jpg`), 2쪽 헤드라인 크기 |
| 3D 렌더 뒷면 · PCB 배치도 뒷면 | 쓰지 않음 (설계자 실크) |
| 회로도 1쪽 MOTOR&SENSOR (2026-10-27) | DRV8244SQRYJRQ1 × 4 (L · R · M · H), XT30 모터 커넥터 CN3–CN6, AM26LV32 · HX JN1.27 (바퀴 엔코더), SN65LVDS31/32 · SN74LVC1G125 · RJ1/RJ2 5558067-1 (절대 엔코더) — 7주차와 같은 회로 |
| 회로도 2쪽 STM32 (2026-10-21) | 3쪽 핀 배정 표 (헤더 U2 · U4 HC-PM254-8.5H-2x22PZ) |
| 회로도 3쪽 POWER (2026-10-20, 갱신 10-27) | 4쪽 입력 보호(LM74801, CSD18510Q5B × 2, UVLO 11.33 / 10.41 V, OVP ~16 V, SMBJ18CA, 외부 50 A 퓨즈, SW1), 5 V (LMR60440, 5.016 V), 배터리 감시 VCC/11 (ADC 핀 미배정) |
| 회로도 5쪽 JETSON_19V (2026-10-21) | 4쪽 19 V 승압(LM5122, 약 3 A 목표 · 5 A 전력단), TPS26630(전류 제한 ~3.2 A), TLV6700 19.5 V OVP · 5 V 연동, J2 Jetson 원형 잭 5.5/2.5 mm; 「Prototype review required」 메모 → 4쪽 띠 |
| 회로도 4쪽 | 받지 않음 |

MCU 코어 보드는 사용자가 준 AliExpress 링크(1005006632336183)를 열 수 없어, 로봇 저장소 `docs/design/2026-10-22-h743-pinmap-draft-review.md` 의 보드 이름(WeAct Studio MiniSTM32H7xx, STM32H743VIT6)을 썼다. 사양은 ST STM32H743VI 제품 페이지(Cortex-M7 480 MHz, 2 MB 플래시, 1 MB RAM). G474 170 MHz, H533RE 250 MHz 는 ST 제품 정보.

## 로봇 저장소 (lightminn/forklift, main f60da30a 기준)

| 자료 | 쓴 곳 |
|---|---|
| `docs/references/week8_feedback.md` | 1쪽 피드백 네 줄 (UWB 는 다른 팀 이야기라 뺌) |
| `artifacts/cad/motor-shaft-magnet-adapter/` (git 미추적) README · `build_adapter.py` · `shaft3mm/` | 5쪽: 축 3 mm 판 칼라(외경 5, 높이 1.6 = 축 돌출 2.0 − 틈 0.4), 구멍 3.00–3.25 mm 0.05 간격 6종과 맞춤 시험 막대; 사용자 실측(2026-10-28) 3.25 mm 가 맞음, 자석 6 mm 에 맞춰 외경 6.00 mm 로 다시 출력 예정 |
| `docs/plans/2026-10-26-slam-localization-default.md` 5b · 5d | 08 장 표 위치 오차 중앙값(1차 확인 L 0.029–0.038 m, R 0.089–0.119 m), SLAM 끊김(2차 확인 R line_m 두 실행 slam_link_failed, 응답 1.149 · 1.096 s), 띠의 1 s 기한; 사용자 결정(2026-10-27)으로 기준 미충족 셋을 받아들인 예외 채택 |
| `docs/plans/2026-10-27-slam-a-return-start-remeasure.md` (PR #179) | 08 장 하역 도킹 옆 치우침 최대 0.012 대 0.219 m (seed · 스냅숏 · 목적지 구성이 다른 기술 비교) |
| `docs/design/2026-10-22-fms-case-survey.md` (PR #87) | 09 장 캡처 설명의 참고 제품, 띠(1대 구성에서 뺀 기능, 아직 없는 금지 구역 · 배터리 표시) |
| `console/README.md` (PR #90 · #93 · #95) | 09 장 콘솔 세 기능 |
| branch `diag/transport-start-stall` `docs/validation/2026-10-27-transport-start-stall.md` | 10 장 출발 정지 원인, 실제 간격 기둥 0.181–0.215 m · 벽 0.205–0.208 m |
| branch `feat/escape-presteer` `docs/plans/2026-10-27-escape-presteer.md` 2판 (b38048da) | 10 장 수정 방향(출발 띠 해제 + 출발 전 조향 0) |

## 08 장 위치 오차 그래프

ws1 `test_runs/live/s3conf2_3a37e216` 의 `s3b_R_line_m_s3`(지도 작성 동시, 3,371 s 에 slam_link_failed) · `s3b_L_line_m_s3`(등록부 지도 위 위치 추정, 3,933 s 세션 끝) `spool/slam.control` 의 행 `[t, 적용 후축 x, y, yaw, 참값 x, y, yaw]` 에서 위치 차의 크기를 1분 구간 중앙값으로 그렸다(시뮬 시간, team-spec 오도메트리, D7_HOLD 끔). 표의 세 수치는 다른 배치에서 나온 값이라 그래프의 56분 · 65분은 표에 쓰지 않았다.

## 08 장 영상

ws1 `test_runs/live/dk9a_36b9b7de/dk9a_random_m_s0` (잡 12032, 2026-10-28) — `ct1_queue.sbatch`, random_m 대기열 P-4:D-1 · P-5:D-2 · P-3:D-3, seed 0, 등록부 지도(random_m_team_spec_quantized_0facac3eea66) 위 위치 추정, D7_HOLD 켬, team-spec, 3/3 완료. `transport.mp4` 를 1160 × 660 at x 110 으로 잘라 12배속 · 540 px. 스냅숏 `dk9v_36b9b7de` 는 `trf_36b9b7de`(main 36b9b7de)에서 `record_video_overlay(t)` 한 줄만 `stamp` 로 바꾼 렌더용 사본.

## 07 장 장착 방식 애니메이션

`tools/sleeve_anim.html`(three.js) 로 그린 3D 애니메이션 `h06_sleeve.mp4`(원통은 앞쪽 절반을 잘라 보임). 장착 순서는 로봇 저장소 `artifacts/cad/motor-shaft-magnet-adapter/` README · `install_guide.html`(git 미추적): 마운트를 끼우고 판으로 눌러 높이 맞춤, 자석과 같은 지름의 중심 맞춤 관을 마운트에 걸쳐 씌움, 자석을 넣어 가운데만 접착, 굳으면 관을 위로 뺌. 치수는 축 Ø3, 마운트 외경 6 · 구멍 3.25 · 높이 1.6, 모터 면 틈 0.4, 자석 Ø6; 자석 두께 · 관 벽 두께는 그림용 값, 관 걸침 1.2 mm 는 1차 설계값.

## 05 장 보드 부품값

로봇 저장소 `docs/references/team-hardware/2026-10-28/pcb-cost-comparison.md`(팀 문서, 로컬 전용) 2.1절의 부품값 열: LCSC 실시간 가격(MOQ · 주문 단위 · 수량 구간 반영), 5장 Motor $402.11 · MT_DS $13.08 · KTH7801 $25.83 · STDS $46.32(합 $487.34, × 1,400 = 약 68.2만 원), 1장만 $110.42 · $4.93 · $7.62 · $11.73(합 $134.70). 조립비 · PCB 제작비는 넣지 않았다(사용자 2026-10-28).

## 콘솔 캡처 (09 장)

가짜 차량 `console.mock_vehicle`(콘솔 코드 = main f60da30a, `git archive` 사본), 헤드리스 Chromium 3200 × 1800 · 페이지 zoom 2(1600 × 900 배치를 두 배 해상도로), 2026-10-28. 조종 권한 → 「남은 팔레트 전부 옮기기」 → 대기열 재개(2단계 확인) → P-01 → D-A, P-02 → D-B 완료. 대기열 진행(`c07_queue.png`), 상태·경보 위쪽 열 줄(`c07_health.png`), 요약의 결과 줄과 팔레트별 표(`c07_summary.png`)만 잘라 냈다.

## 사진

5쪽 `h05_print.jpg` · `h05_mounted.jpg`: 팀 촬영(2026-10-26) 1차 출력물과 모터 축에 끼운 모습, 원본은 로봇 저장소 `docs/references/team-hardware/2026-10-26-adapter-print/`(로컬 전용). 방향을 바로잡고 잘라 다시 인코딩해 EXIF 를 지웠다.


| 파일 | 원본 | 라이선스 |
|---|---|---|
| `d02_jetson.jpg` | Wikimedia Commons, File:NVIDIA Jetson Nano Developer Kit (47616885631) (cropped).jpg — SparkFun Electronics (Flickr). 우리가 쓸 Orin Nano 와 모양이 비슷한 다른 모델 | CC BY 2.0 |
| `d02_truck.jpg` | 5주차 `30_chassis_pallet.jpg` (2026-09-30 실물 사진, EXIF 제거)를 잘라 씀 | 팀 촬영 |

## 화면에 쓰지 않은 사실

- 재접근 동안 SLAM 보정 보류(PR #155, V5: 실패 39 → 25, 재접근 정체 30 → 0)는 사용자와 상의해 뺐다(내부 처리 설명이 길고, 검증이 위치 추정 전환 전 방식에서 이루어짐).
- 팔레트 인식(하판 없는 · 동봉 팔레트, 선반 구분, 학습 모델), 자율 조사 보류, ws1 자원 · 시험 인프라는 이번 덱 범위 밖이다(총괄 지시).
