# 리보틱스 중간 미팅 · 자율 지게차 중간 점검 · 발표 원고

16장 · 시간 배분 합계 16분 20초. 쪽별 배정 시간은 발표 연습 후 조정한다.

기준일: 2026-10-14 (리보틱스 중간 미팅). 결과는 Isaac Sim 합성 장면과 CPU 합성 시험의 결과이며 실제 장비 성능이 아니다. 하드웨어 쪽은 팀 실측 · 역분석 · 회로 초안이고 구동 보드는 아직 제작 전이다. 원고는 발표자 문체(합니다체)로 썼고, (전환)은 다음 쪽으로 넘기는 자리다.

## 1쪽 · 리보틱스 중간 미팅 (00:00–00:20, 20초)

안녕하십니까. '자율 지게차 중간 점검'이라는 주제로 발표할 김광민이라고 합니다. 지금까지 만든 것과 남은 일을 기술 위주로 정리하고, 마지막에 리보틱스 측에 확인을 부탁드릴 내용을 말씀드리겠습니다. (전환)

[Sources]
중간 미팅
과제: 주변 장애물을 고려한 최적의 팔레트 핸들링 경로 생성 및 제어: docs/references/quest.txt (과제 문서)
§1 리보틱스 중간 미팅(형식은 중간 발표), 10/12 교수님 초안 검사 · 10/14 미팅: docs/references/week6_feedback.md
[/Sources]

## 2쪽 · 과제 이해와 진행 현황 (00:20–01:10, 50초)

먼저 과제를 어떻게 이해했고 어디까지 왔는지입니다. 과제 문서의 순서대로 팔레트 인식부터 운반과 하역까지 다섯 단계로 나눴고, 다섯 단계 모두 시뮬레이션에서 한 임무로 이어서 돌아갑니다. 실물은 차체 실측과 기존 제어기 분석을 마치고 구동 보드를 설계하는 단계입니다. 아래 표는 과제의 네 가지 접근 상황입니다. 시뮬레이션에서 A는 확인했고, B는 곡선으로 다가가지만 삽입 전에 한 번 멈춰 다시 봅니다. 과제대로 멈추지 않고 넣는 B와, 먼저 후진해야 하는 C, 뒤에 장애물이 있는 D는 다음 단계에서 반복 평가로 확인합니다. 지금까지 시뮬레이션은 EPAL 6 팔레트로 돌렸습니다. (전환)

[Sources]
출처: 과제 문서 · 로봇 저장소 실행 기록
필수 처리 순서 5단계 · 접근 상황 A–D (8–11쪽): docs/references/quest.txt (과제 문서)
인식(카메라 깊이) → 위치 → LiDAR 1대 장애물 지도 + Hybrid A* → 근접 추적 삽입 → SLAM 위치 운반 · 하역 · 복귀, 한 임무 완주 (2026-10-11): ws1 artifacts/20261011_s4b/smoke/seed_1_v0.055
A–D 를 모든 계획기 · 제어기의 시험 사례로 사용; C · D 는 아직 별도 확인 전: forklift CLAUDE.md
B 는 멈추지 않고 삽입 — 멈춘 뒤 정렬하는 구현은 B 완료로 표시하지 않음(:161); 기능 통과 A–D 각 20회 중 19회(:226). 지금 실행은 정렬 직진 시작(2.1 m)에서 멈춰 다시 관측, EPAL 6 · 장면당 1회: docs/plans/2026-09-11-development-roadmap.md
실물: 차체 실측 · 제어기 역분석 완료, 구동 보드 회로 초안, Jetson 미구매: docs/hardware.md
[/Sources]

## 3쪽 · 운반 임무 전체 (01:10–01:55, 45초)

지금 시뮬레이션에서 처음부터 끝까지 이어서 돌아가는 운반 임무를 먼저 보여 드리겠습니다. 실측 차체 모델로 팔레트를 인식하고, 포크를 넣어 들어 올린 뒤, 목적지에 내려놓고 출발점으로 돌아옵니다. 영상은 12배 빠르게 돌린 것입니다. 이 실행에서 하역 오차는 19밀리미터, 출발점 복귀 오차는 27밀리미터였고, 포크가 팔레트에 닿은 적은 없었습니다. 오른쪽 표의 단계별 구현은 뒤에서 하나씩 말씀드리고, 삽입 중 포켓 추적은 따로 찍은 실행으로 보여 드리겠습니다. 먼저 이 임무가 돌아가는 시스템 구성입니다. (전환)

[Sources]
화면 생성: 위 장면 5 3분할 영상의 조감 칸 12배속 (prepare_clips.py mission)
forklift b66271f 스냅숏, 실측 차체 · SLAM 위치 · LiDAR 1대 · --d7-planner --d7-docking · --video --robot-camera (근접 추적 끔). result.json: success, complete, 하역 19.4 mm, 복귀 2.7 cm · 0.040 rad, 금지 접촉 0, 진입 319.9 / 318.1 mm, 시뮬 219.6 s: ws1 artifacts/20261011_meeting_video/seed_5_d7
같은 조건 장면 1: success, 하역 27.0 mm, 복귀 5.1 cm, 금지 접촉 0, 시뮬 273.8 s: ws1 artifacts/20261011_meeting_video/seed_1_d7
목적지 도킹: 미리 등록한 위치의 LiDAR 스캔 정합 (등록 위치는 시뮬레이터 값): config/isaac_transport_measured.yaml
Depth-only geometric baseline for a known, horizontal pallet shape: src/forklift_core/perception/pocket_detector.py
map<-base = map<-odom(SLAM) × odom<-base(odometry); point-to-line ICP 목적지 도킹: src/forklift_core/localization/slam_pose.py · scan_match.py · scan_docking.py
RearAxlePathTracker — 뒤차축 pure pursuit (곡률 = 2 · 횡오차 / 거리²), 전환점마다 정지: src/forklift_core/control/path_tracking.py
이 녹화 실행은 근접 추적 끔: 정렬 직진 시작(2.1 m)에서 한 번 더 관측(near capture) 후 그 위치로 삽입: sim/isaac/run_transport.py
[/Sources]

## 4쪽 · 시스템 구성 (01:55–02:55, 60초)

전체 시스템 구성입니다. 왼쪽 센서는 과제 규격대로 RGB-D 카메라 한 대와 2D LiDAR 한 대입니다. 가운데 Jetson은 인식과 위치 추정, 경로 계획을 맡습니다. 오른쪽 STM32 보드는 Jetson의 명령을 받아 주행, 조향, 승강 모터를 제어하고, 엔코더로 바퀴 회전과 조향각을 읽습니다. 아래 점선은 이번에 새로 넣은 무선 부분입니다. 감시 PC와는 Wi-Fi로 상태와 지도만 주고받습니다. 무압축 깊이 영상은 초당 약 200메가비트라 Wi-Fi로 보내지 않고 차에서 기록합니다. 비상정지는 Wi-Fi와 따로 두어 신호가 끊기면 바로 멈추게 합니다. 원격 정지를 어느 수준으로 갖춰야 하는지, 여러 대를 함께 운용하는지는 마지막에 여쭤보겠습니다. (전환)

[Sources]
출처: 하드웨어 기록 · 5주차 회로 초안 · 공식 문서 조사 (2026-10-11)
D435i 확정 · RPLIDAR A2 계획(A2M12 유력) · Jetson Orin Nano Super 8GB 권장(미구매) · 개발 기준 ROS 2 Jazzy: docs/hardware.md
DRV8244-Q1 × 3 (L·M·R 채널, SPI 공유, DRVOFF 비상 차단) · MT6701 증분판(바퀴)·절대판(조향) · MCU 핀 배정 초안(Nucleo-64 morpho 2 × 38핀): week-05/build_deck.py
§5 무선 통신 미고려 — 지게차–PC · 지게차–지게차: docs/references/week6_feedback.md
LiDAR 장착 높이 1.05 m (시뮬레이션 값, 실물 브래킷 미제작): config/isaac_slam_lidar.yaml
M.2 Key-E 2230 — "Populated with the included wireless module" (802.11ac 모듈, 포럼 기준 RTL8822CE · AzureWave AW-CB375NF): https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html
ROS 2 Jazzy DDS tuning — 손실 있는 Wi-Fi 에서 큰 메시지의 IP 조각 손실로 연결이 멈춘 것처럼 보임 (계산: 무압축 깊이 848 × 480 · 30 fps 약 195 Mbit/s, LiDAR 스캔 약 1 Mbit/s): https://docs.ros.org/en/jazzy/How-To-Guides/DDS-tuning.html
rmw_zenoh (멀티캐스트 탐색 없이 라우터 사용) — Wi-Fi 구성 후보, 미시험: https://docs.ros.org/en/jazzy/Installation/RMW-Implementations/Non-DDS-Implementations/Working-with-Zenoh.html
산업 사례: 전용 무선 E-stop(FORT), 하트비트가 끊기면 정지, 수신기를 차량 E-stop 회로에 직결: https://store.clearpathrobotics.com/products/wireless-e-stop
무선 제어는 통신 상실 포함 올바른 신호가 없으면 자동 정지: EU 기계지침 2006/42/EC 부속서 I 1.2.1 (2차 자료)
[/Sources]

## 5쪽 · 실물 차체와 구동부 (02:55–04:15, 80초)

실물 쪽입니다. 들어온 차체를 재 보니 가장 큰 차이는 조향각이었습니다. 최대 조향각이 15도라 계산한 최소 회전 반경이 약 2.5미터로, 사진으로 추정한 모델의 두 배 가까이 됩니다. 그래서 좁은 곳에서는 앞뒤로 움직이며 방향을 맞춰야 하고, 이 내용은 뒤에서 다시 말씀드리겠습니다. 포크는 36센티미터라, 시뮬레이션의 EPAL 6 팔레트에서는 삽입 목표를 33센티미터로 잡았습니다. 기존 제어기는 로직 애널라이저로 분석해 보니 릴레이를 켜고 끄기만 해서 속도를 조절할 수 없었고, 그래서 구동 보드를 새로 만듭니다. 모터 드라이버는 비교한 제품 중 온저항이 47밀리옴으로 가장 작은 TI DRV8244를 골랐습니다. 전류 감지와 결함 진단도 칩에 들어 있습니다. 엔코더는 자석식 MT6701로, 한 칩이 절대각과 증분 출력을 모두 내서 조향축과 바퀴에 같이 씁니다. 모터 전류를 잰 뒤 전류 제한과 방열을 정해 PCB로 만듭니다. (전환)

[Sources]
출처: 5주차 실측 · 역분석 · 회로 초안
실측 축간 0.66 m · 윤거 0.53 m · 바퀴 0.125 m · 최대 조향 15° · 포크 360 × 55 × 25 mm: sim/models/dls08_measured/README.md
최소 회전 반경 = L / tan δ: 0.66 / tan 15° = 2.46 m, 사진 추정 0.64 / tan 0.45 = 1.32 m (뒤차축, 자전거 모델): 계산
삽입 깊이 규칙 min(깊이 × 0.6, 캐리지 한계 − 16 mm): dls08_measured 346 − 16 = 330 mm (EPAL 6 깊이 600 × 0.6 = 360 mm 보다 작음): forklift CLAUDE.md
4–9쪽: DSLogic 파형, 릴레이 on/off · 속도 조절 기능 없음, DRV8244-Q1 · MT6701 선정, 회로 초안 (조건: 모터 전류 실측 후 확정): week-05/SCRIPT.md
[/Sources]

## 6쪽 · 시뮬레이션 환경 (04:15–05:15, 60초)

실차 주행 전까지는 Isaac Sim에서 개발합니다. 공장 홀 장면에 실측 차체 값을 넣고 물리는 120헤르츠로 돌립니다. 지게차는 바퀴 토크로 실제로 굴러가고, 팔레트도 고정하지 않고 포크로 들어 올립니다. LiDAR는 A2M12 카탈로그 값으로, 깊이 영상은 D435i 컬러 카메라 화각에 맞춰 합성합니다. SLAM은 ROS 2의 slam_toolbox로 돌리고, 시뮬레이터는 스캔마다 SLAM 결과를 받은 뒤 다음으로 넘어갑니다. 주황색은 가정값입니다. 낮은 바닥 장애물은 없다고 가정했고, 바퀴 마찰과 구동 토크는 일반적인 범위의 값을 넣었습니다. LiDAR 잡음도 가정값이고, 깊이 영상에는 아직 잡음이 없습니다. 이 값들은 실측이 나오면 먼저 바꿉니다. (전환)

[Sources]
출처: 저장소 설정 · 모델 기록 (6주차 1쪽 이어 받음)
실측 반영 모델 dls08_measured (실측하지 않은 항목은 추정값, 필드별 출처): sim/models/dls08_measured/README.md
정지 · 운동 마찰 계수 0.8 / 0.7 (지게차 · 팔레트 충돌 형상, sim/isaac/scene.py configure_drives), 바퀴 토크 3 N·m — 시뮬레이터 전용 가정값: config/isaac_transport.yaml
깊이 640 × 480, fx 465.74 → 수평 화각 69.0° (D435i RGB 시야를 흉내 낸 합성 설정, docs/design/2026-09-11-pocket-observation-and-scene-set.md 사용자 결정 1; D435i 깊이 화각 87° × 58° 아님), depth_quantize_mm 1, 잡음 없음: result.json pocket_camera · perception
LiDAR 잡음 noise_std_m 0.02 (±0.06 m 절단, SLAM 과 같은 스캔): config/obstacle_layer_single.yaml
EPAL 6 공식 제품 시트: config/pallet_geometry_epal6.yaml
EPAL 6 과 T11 × 0.6 모두 필수, T11 정본 치수 미확정: forklift CLAUDE.md
physics_hz 120, physical_wheel_drive true, pallet_fixed_attachment false, pose_teleportation_after_reset false (S4b · 녹화 실행): result.json settings_synthetic
RPLIDAR A2M12 카탈로그 1,600빔 · 10 Hz · 0.2–12 m: config/isaac_slam_lidar.yaml
slam_toolbox online_sync, mapping, 해상도 0.05 m, Ceres, 루프 닫기; Isaac 은 스캔마다 브리지 응답을 기다림 (sim/isaac · slam_link.py): tools/slam_bridge_container.sh · ros2/src/forklift_bringup/config/slam_toolbox_isaac_online.yaml
5.1 (Kit 로그 Isaac-Sim Python/5.1): ws1 Isaac Sim
--min-obstacle-height-m 1.15 — 1.05 m 평면에 닿지 않는 소품 제거 (운용 가정): forklift bc4cc64
[/Sources]

## 7쪽 · 포켓 인식 (05:15–06:25, 70초)

이제 과제 단계별로 보겠습니다. 첫 단계는 팔레트 인식으로, 학습 모델 대신 팔레트 규격의 치수와 형상 규칙을 씁니다. 그림처럼 깊이 영상에서 작업 범위의 점만 남기고, 수직 평면을 찾아 팔레트 앞면으로 삼습니다. 앞면을 세로 칸으로 나눠 받침목과 빈 공간을 가르고, 빈 공간의 폭이 규격 범위 안에 들면 두 포켓의 중심과 삽입 방향을 구합니다. 학습 데이터 없이 EPAL 6과 T11을 치수만 바꿔 같은 코드로 다루기 위해서입니다. EPAL 6 합성 장면에서는 대상 60개를 모두 찾았고, 위치 오차는 95퍼센트가 8.2밀리미터 이하였습니다. 다만 깊이 잡음이 없는 장면이고, 비슷한 모양의 물체를 가려내는 오검출 평가와 T11 평가는 남아 있습니다. 또 포켓 입구가 화면 밖으로 나가면 찾을 수 없어서, 다음 장의 삽입 중 포켓 추적이 이어받습니다. (전환)

[Sources]
화면: 3주차 4쪽 그림 · 근거는 3주차 6 · 8쪽
Depth-only geometric baseline for a known, horizontal pallet shape — 작업 범위 → 앞면 평면 → 세로 칸(받침목 · 빈 공간) → 포켓 중심 · 방향: src/forklift_core/perception/pocket_detector.py
판정 기준을 규격 치수에서 계산 (3주차 6쪽: 길이는 규격 비례, 측정점 수는 관측 면적 비례): src/forklift_core/perception/pallet_geometry.py
4쪽 처리 과정(빈 공간 220 mm, 규격 허용 207.5–247.5 mm): week-03/SCRIPT.md
EPAL 6 Gazebo 장면 100개 = positive 60 · occluded 20 · negative 20, 자세 2.0–4.0 m, 옛 장착 (0.75, 0, 0.5), 깊이 잡음 없음; 대상 60개 모두 검출, 위치 p95 dev 8.17 mm; 음성 0/20 은 단측 95 % 상한 13.9 % 라 오검출 성능은 주장하지 않음 (+ ADR 0004 D6 grounded 형상 결함), 홀드아웃 아님, T11 렌더 평가 없음: docs/validation/2026-09-14-epal6-capture-and-evaluation.md
3주차 그림의 위 제목 띠와 아래 단계 설명을 잘라 내고 단계명은 HTML 로 (Gazebo 장면 s003 의 실제 중간 결과): week-03/assets/20_pipeline_stages.png
[/Sources]

## 8쪽 · 삽입 중 포켓 추적 (06:25–07:55, 90초)

과제가 강조한 삽입 중 포켓 추적입니다. 처음에는 카메라를 차체 앞 높은 곳에 달았는데, 포크를 넣기 시작하면 마지막 약 25센티미터를 보지 못했습니다. 그래서 Crown 특허처럼 카메라를 캐리지 하단으로 옮겼고, 영상처럼 포크를 넣는 동안에도 윗판이 화면에 남습니다. 구현은 표의 다섯 단계입니다. 먼저 시뮬레이터에서 잰 영상 지연 약 0.09초를 반영해, 각 영상을 찍힌 순간의 차 위치에 맞춰 씁니다. 실물에서는 이 지연을 다시 잽니다. 포켓 입구가 화면 밖으로 나가면 윗판 가장자리로 팔레트 위치를 이어서 추적합니다. 포크 끝이 앞면까지 1미터, 0.6미터 남은 지점에서는 멈춰서 다시 보고 남은 직진 경로를 다시 그립니다. 포크 끝이 팔레트 앞면까지 15센티미터 남으면 포크와 포켓 벽 사이 간격을 계속 보고, 관측 오차와 멈추는 거리를 더한 값보다 좁아지면 멈춥니다. 삽입은 캐리지 앞에 1.6센티미터 여유를 남기는 위치를 목표로 끝냅니다. 이 실행에서 포크는 팔레트에 닿지 않고 약 32센티미터 들어갔습니다. 다만 깊이 잡음이 없는 합성 영상이라, 잡음을 넣은 확인이 남아 있습니다. (전환)

[Sources]
화면 생성: 위 실행의 근접 깊이 프레임 506장(10 Hz)을 색 지도로, 사건 시각에 글자, 2배속 (prepare_clips.py depth)
forklift b66271f, 실측 차체 · SLAM 위치 · LiDAR 1대 · 근접 추적(보정점 1.0 / 0.6 m), 포켓 깊이 확인(D5) 끔. result.json: success, 삽입 끝 진입 323.5 / 322.2 mm, 금지 접촉 0, 하역 6.74 mm: ws1 artifacts/20261011_s4b/smoke/seed_1_v0.055
근접 추적 시작 44.3 s, 1.0 m 보정 54.03 s(정지 0.37 s), 0.6 m 보정 61.73 s, 포크 끝 보호 시작 70.62 s(앞면 0.149 m), 삽입 끝 80.69 s: ws1 artifacts/20261011_s4b/smoke/seed_1_v0.055/run/near_tracking.json
기존 장착(높이 0.50 m · 수평)은 삽입 마지막 약 0.25 m 무관측: docs/plans/2026-10-03-near-field-pocket-tracking.md
Crown 특허 US9990535B2 — 포크 캐리지 하단 장착 (4주차 장착 사례 ②): https://patents.google.com/patent/US9990535B2/en
카메라 지연 L = 91.668 ms (11 틱, 120 Hz) — 측정 대역 84.43–98.94 ms, Isaac 렌더 경로의 값 (실물 D435i 는 다시 측정): config/near_field_bounds_measured.json · forklift 2313dc9
윗판 뒤 가장자리로 거리, 판재 · 틈 가장자리로 방향과 좌우 위치, 가려진 포켓은 팔레트 모델로 추정: src/forklift_core/perception/roof_tracking.py
보정점 1.0 / 0.6 m(포크 끝 추정 – 앞면), 정지 후 새 관측으로 직진 다시 그림 + 모의 주행 도착 확인; 보호 구간 0.15 m 부터 포크–벽 간격 < b_t + 정지 휩쓸림 + 0.011 m 면 정지; 캐리지 앞 모서리 여유 0.016 m 에서 삽입 끝: forklift b66271f · sim/isaac/near_tracking.py
접근 속도 0.055 m/s — 관측 주기의 모든 틱에서 정지 예산이 성립하는 가장 큰 0.005 단계: config/near_field_drive_terms.json
추적 프레임에는 깊이 잡음을 넣지 않음 — 잡음 없는 합성 깊이에서의 추적 흐름 실증: memory: D8 범위 (2026-10-10 사용자 결정)
[/Sources]

## 9쪽 · 위치 · 장애물 구조 (07:55–09:20, 85초)

여기까지가 카메라로 팔레트를 찾고 포크를 넣는 부분입니다. 다음은 LiDAR 한 대로 위치를 잡고 장애물을 피하는 부분입니다. 바퀴와 조향 엔코더로 계산한 이동량, 즉 오도메트리로 위치를 계속 계산합니다. LiDAR 스캔은 매번 SLAM 쪽으로 보내고, 지도와 맞춘 보정은 차가 약 0.45미터 움직이거나 30도 가까이 돌 때마다 새로 받습니다. 포크를 넣고 드는 동안에는 위치가 갑자기 바뀌지 않도록 새 보정을 반영하지 않습니다. SLAM 쪽 응답이 0.25초 넘게 끊기면 계산 위치만으로 달리지 않고 멈춥니다. 같은 스캔으로 장애물 격자도 만듭니다. 오래된 스캔일수록 위치 오차만큼 장애물을 크게 잡고, 지금 곡률로 멈췄을 때 지나갈 칸이 모두 비어 있어야 그 속도로 달립니다. 경로 계획에는 장애물 기억과 SLAM 지도를 함께 써서, 지나오며 본 장애물도 기억합니다. 목적지에서는 미리 등록한 스캔과 지금 스캔을 ICP로 맞춰 하역 위치를 보정합니다. (전환)

[Sources]
화면 생성: 코드 구조를 그린 흐름도 (build_deck.py structure_diagram)
map<-base(t) = map<-odom(마지막 SLAM 응답) × odom<-base(t, 오도메트리); 보정이 max_age_s(실행 0.25 s)보다 오래되면 LocalizationStale 로 정지: src/forklift_core/localization/slam_pose.py
Isaac 은 LiDAR 주기마다 스캔을 보내고 같은 스캔의 응답(map<-odom)을 받을 때까지 물리를 진행하지 않음 (lockstep); KeyframeGate: 0.447 m 이동 또는 0.5 rad 회전 + 0.5 s 이상 간격인 스캔만 slam_toolbox 로, 나머지는 직전 보정을 그대로 응답: src/forklift_core/localization/slam_link.py
접근(채택한 관측부터) · 삽입 · 승강 · 빼기 · 내리기 · 물러나기 동안 보정 고정: sim/isaac/run_transport.py slam_feedback.hold_phases
online_sync · mapping · 해상도 0.05 m · Ceres · do_loop_closing true: ros2/src/forklift_bringup/config/slam_toolbox_isaac_online.yaml
점유 칸을 r = e(age) + 2ρ sin(ψ(age)/2) + 센서 한계로 부풀림(오도메트리 표류의 측정값), 점유 칸 유지 occupied_max_age_s 0.3 s, 빔이 지나간 칸은 0.2 s 이내 스캔에서 FREE (config/obstacle_layer_single.yaml): src/forklift_core/perception/obstacle_grid.py
비상정지 원호(현재 곡률로 멈추는 궤적)와 앞 경로의 칸이 FREE 여야 그 속도 허용: src/forklift_core/control/drive_permission.py
경로 계획에만: 칸별 마지막 끝점 · 마지막 FREE 시각 기억 + SLAM 정적 층 (주행 허가는 실시간 관측만): src/forklift_core/perception/planning_memory.py
point-to-line ICP(Gauss–Newton), 여러 초기값이 같은 답일 때만 사용, 벽 하나뿐이면 퇴화로 거부: src/forklift_core/localization/scan_match.py · scan_docking.py
[/Sources]

## 10쪽 · 위치 추정 (09:20–10:25, 65초)

이 구조로 위치를 추정한 결과와 LiDAR를 고른 이유입니다. 왼쪽 영상은 이전 차체 모델로 돌린 운반 실행입니다. 빨간 SLAM 경로는 파란 실제 경로를 따라가지만, 바퀴 회전만 계산한 주황색 오도메트리 경로는 갈수록 벗어납니다. 끝날 때 바퀴 회전만 계산한 위치는 3.4미터 어긋났고 SLAM은 약 4센티미터, 임무 전체 평균으로는 약 9센티미터였습니다. 3.4미터의 대부분은 짐을 싣고 돌 때 계산보다 덜 돌아 방향이 24도 틀어진 탓입니다. 오른쪽 표처럼 카메라는 앞쪽만 보고 멀수록 오차가 커지지만, LiDAR는 12미터까지 360도를 재고 그 지도를 경로 계획에 그대로 씁니다. 과제 문서도 2D LiDAR를 SLAM용으로 지정했으므로, 위치 추정은 LiDAR로 하고 카메라는 팔레트 인식에 집중하도록 나눴습니다. (전환)

[Sources]
화면: 6주차 5쪽 영상 그대로 · 비교표는 데이터시트 · 논문 조사 (2026-10-11)
S3 장면 1 — 358 s 에서 SLAM 4.0 cm 대 바퀴 회전만 340 cm, 위치 RMSE 0.088 m: docs/validation/2026-10-04-online-slam-closed-loop.md
2026-10-06 재계산: 거리 92.9 대 93.6 m, 끝 방향 오차 −24.3°, 회전 시 실제/계산 비 빈 차 0.998 · 운반 0.925: ws1 artifacts/20261004_slam_s3/seed_1/run/slam_log.npz
영상은 이전 S3 실행(사진 추정 차체 dls08_provisional · forklift 5de6c3a, 마찰 가정값, 장애물은 시뮬레이터 정답) — 6주차 5쪽과 같음; 4 cm 는 끝 시점, 임무 전체 RMSE 8.8 cm · 최대 19 cm: week-06/SOURCES.md
RPLIDAR A2M12 데이터시트 rev.1.0 — 0.2–12 m(흰 물체), 360°, 10 Hz · 0.225° (정확도 1/2/2.5 % 는 A2 시리즈 웹 사양표 값): https://cdn.robotshop.com/media/r/rpk/rb-rpk-22/pdf/rplidar-a2m12-360-laser-range-scanner-datasheet.pdf
D400 데이터시트 Rev 023 — 깊이 FOV 87° × 58°, 0.2 m – "3 m 이상, 조명에 따라", RMS ≤ 2 % (≤ 2 m), 반복 패턴은 거짓 깊이 가능: https://www.realsenseai.com/wp-content/uploads/2026/03/RealSense-D400-Series-Datasheet-Mar-2026.pdf
Intel BKM Rev 1.9 — 깊이 오차는 거리의 제곱으로 증가 (848 × 480, 서브픽셀 0.08 가정 시 2 m 약 14 mm · 4 m 약 57 mm, 계산값): https://dev.realsenseai.com/docs/tuning-depth-cameras-for-best-performance
Labbé & Michaud, J. Field Robotics 2019 — 카메라: 흰 벽 · 질감 없음 · 어두운 곳에서 위치 상실, 단거리 LiDAR: 넓은 빈 공간 · 긴 복도에서 문제: https://arxiv.org/abs/2403.06341
SLAM Toolbox (JOSS 2021) — CPU 전용, 2D 점유 격자를 Nav2 에 그대로 사용: https://joss.theoj.org/papers/10.21105/joss.02783
cuVSLAM 기술보고서 부록 B — Orin Nano Super 에서 RGB-D 모드는 424 × 240 에서만 안정 (GPU 가속 비전 SLAM): https://arxiv.org/abs/2506.04359
§4 LiDAR SLAM 과 비전 SLAM 비교 장표 (LiDAR 를 쓰는 근거) · 팀 메모: SLAM 은 깊게 들어가지 않음: docs/references/week6_feedback.md
[/Sources]

## 11쪽 · 새 장애물 대응 (10:25–11:35, 70초)

경로 계획과 추종의 구현입니다. 경로는 Hybrid A*로 짭니다. 차체 한계 2.5미터에 여유를 둔 회전 반경 3.45미터로 0.25미터짜리 전진과 후진 호를 이어 붙이며 길을 찾고, 차체와 짐을 덮는 사각형에 0.1미터 여유를 두고 충돌을 검사합니다. 만든 경로는 뒤차축 기준 pure pursuit로 따라가고, 전진과 후진이 바뀌는 점에서는 멈춥니다. 영상은 운반 중 경로 위에 LiDAR 높이보다 높은 1.3미터 상자가 나타난 경우입니다. 멈추는 궤적이 막히자 지게차가 멈추고, 다시 계획해 조금 후진한 뒤 상자를 피해 갑니다. 지금 설정으로 다시 돌린 운반 중 · 복귀 중 상자 장면도 모두 피해서 완주했습니다. 그런데 왜 바로 돌아가지 않고 후진할까요? (전환)

[Sources]
화면: 6주차 7쪽 영상 그대로 (week-06/prepare_clips.py single)
result.json — success, 하역 64.9 mm, 상자 출현 77.2 s · 정지 약 78 s · 재계획 94.3 s 후 후진 (운반 중): videos-from-ws1/20261007_l8_measured_seed5_n1
result.json — success, 하역 8.0 mm, 상자 출현 226.0 s · 재계획 227.7 s (복귀 중): videos-from-ws1/20261007_l8_measured_seed1_n2
영상: 실측 차체(dls08_measured), LiDAR 1대(1.05 m) 장애물 지도 + SLAM 지도로 경로 계획, 새 상자 0.4 × 0.4 × 1.3 m, 포켓 깊이 확인 끔, 목표 연결 Dubins (D7 이전): forklift bc4cc64
현재 설정(D7: Reeds–Shepp 목표 연결 · 도킹): 9회 모두 success complete, 하역 3.0–22.6 mm; 상자 장면 seed_1_n1 · 1_n2 · 3_n1 · 5_n1 하역 3.0 · 4.6 · 11.6 · 19.9 mm (장면당 1회): ws1 artifacts/20261008_d7_isaac/v2/d7
curvature_limit 0.29, xy 0.2 m, yaw 10°, primitive 0.25 m, clearance 0.1 m, heuristic weight 1.8, reverse ×1.3, gear change 1.0 m, goal_connection reeds_shepp, shot_cap 4 m: result.json travel_planner_config (S4b · 녹화 실행)
Dolgov et al., Practical Search Techniques in Path Planning for Autonomous Driving (2008) 기준, 참고 Nav2 Smac Hybrid-A* — docs/design/2026-09-17-hybrid-astar-transport.md: src/forklift_core/planning/hybrid_astar.py
뒤차축 pure pursuit, 곡률 한계 0.36 /m, 전방 주시 0.28 m(접근), 전환점 정지 허용 0.03 m · 0.05 rad: src/forklift_core/control/path_tracking.py · tracker_configs
비상정지 원호(현재 곡률로 멈추는 궤적)의 칸이 모두 FREE 여야 그 속도 허용 · 앞 경로도 같은 검사: src/forklift_core/control/drive_permission.py
[/Sources]

## 12쪽 · 후진을 고르는 이유 (11:35–13:05, 90초)

답은 큰 회전 반경입니다. 경로 비용을 셀 때 후진한 거리는 1.3배로 치고, 전진과 후진을 바꿀 때마다 1미터를 더하므로, 전진만으로 갈 수 있으면 전진을 고릅니다. 왼쪽은 앞의 상자 장면입니다. 멈춘 자리에서 상자는 앞으로 2미터, 오른쪽으로 0.6미터에 있었고, 원래 경로는 상자 위를 지나고 있었습니다. 회전 반경이 커서 이 거리 안에서는 옆으로 충분히 비킬 수 없으므로, 1.25미터 후진해 거리를 번 뒤 상자 안쪽으로 꺾어 나갑니다. 오른쪽은 앞뒤로 움직일 때의 특성입니다. 목적지 바로 앞에서 방향이 1.3도만 틀어져도, 전진만 쓰면 계획에 쓰는 회전 반경 3.45미터로 지름 약 7미터 원을 한 바퀴, 21.7미터를 돌아야 맞출 수 있습니다. 그래서 목적지에 붙는 마지막 연결에 앞뒤 전환을 허용했습니다. 오른쪽 개념도처럼 한쪽으로 꺾으며 조금 전진한 뒤 반대로 꺾으며 후진하면, 거의 제자리에서 방향만 바뀝니다. 이 경우 0.5미터씩 앞뒤로 움직여 1미터로 끝났고, 다른 목적지 앞 계획에서도 한 바퀴 경로는 나오지 않았습니다. C, D처럼 먼저 물러나야 하는 상황에도 이 계획을 쓸 예정입니다. (전환)

[Sources]
화면 생성: 실행 기록 · 플래너 재실행으로 그린 경로 (prepare_figures.py)
PlannerConfig: reverse_penalty 1.3, gear_change_penalty_m 1.0; D7_PLANNER_OPTIONS = Reeds–Shepp 목표 연결 + 연결 상한 4 m: src/forklift_core/planning/hybrid_astar.py
planner_curvature_inv_m 0.29 (계획 회전 반경 3.45 m, 차체 한계 15° = 2.46 m 에 추종 여유): config/isaac_transport_measured.yaml
재계획 94.3 s: 뒤차축 기준 상자 앞 1.97 m · 오른쪽 0.61 m, 후진 1.25 m → 전진 22.95 m, 원래 경로의 상자 중심 최소 거리 0.01 m (prepare_figures.py): videos-from-ws1/20261007_l8_measured_seed5_n1/plan_history.json
l8_measured 장면 1 + N1 정지 재계획: 목표 1 cm 앞 · 0.023 rad — 전진만 21.68 m, D7 0.99 m (전진 0.50 + 후진 0.49 m, 전환 1회) — prepare_figures.py 가 같은 사례를 다시 계획: tests/unit/planning/test_d7_planner_options.py
D7 CPU 판정: 운반 목표 고리 1,686 → 0 (목표당 2,376 계획), 목표까지 길이 중앙값 21.69 → 1.03 m: forklift 1e3cdeb
§3 Hybrid A* 가 왜 뒤로 가는지 · 앞뒤로 돌 때의 특성: docs/references/week6_feedback.md
[/Sources]

## 13쪽 · 자격시험 기준 비교 (13:05–14:00, 55초)

사람이 운전하는 지게차의 기준과 비교하려고 지게차운전기능사 실기시험과 대조했습니다. 시험은 팔레트를 싣고 코스를 돈 뒤 내려놓는 과제라 작업 흐름이 저희 임무와 비슷합니다. 하역 위치가 20센티미터 넘게 어긋나거나, 포크를 20센티미터 넘게 덜 넣거나, 화물을 떨어뜨리거나 팔레트를 밀면 실격인데, 시뮬레이션 결과는 모두 이 기준 안입니다. 운반 중 포크 높이는 약 20센티미터로 권장 범위의 아래 끝입니다. 마스트를 기울이는 틸트 기구는 없어서, 틸트 없이 운반해도 되는지는 마지막에 여쭤보겠습니다. 시험 기준은 실제 지게차 크기라, 코스 치수가 차폭의 배수인 점을 이용해 저희 차 크기로 줄인 코스를 시뮬레이션 평가에 쓰는 것을 제안드립니다. (전환)

[Sources]
출처: Q-Net 공개문제 원문 (2025) · 실행 기록
「[공개문제] 지게차운전기능사」 코스운전 및 작업 (한국산업인력공단, 2025-12-22 등록) — 유의사항 7 주행 중 포크 20–30 cm 유지, 실격 (8) 화물 · 파렛트 낙하 (9) 파손 (10) 포크로 드럼통 터치 (14) 포크 50 cm 초과 (15) 하역 20 cm 초과 (16)(17) 밀림 (18) 덜 삽입 20 cm 초과; 팔레트에 닿는 것 자체는 실격 아님. 코스 치수는 D(좌우 최외측 타이어 바깥 간 거리)의 배수. 도면은 저작물이라 화면에 싣지 않음: https://www.q-net.or.kr/cst006.do?artlSeq=5211260&brdId=Q006&code=1204&gId=&gSite=Q&id=cst00602
시험 시간 4분 — 코스 · 차체 규모가 달라 비교에서 제외 (속도 · 작업 시간은 자율 동작 완성 뒤 단계): 같은 문서
하역 6.74 mm, 진입 323.5 / 322.2 mm (캐리지 한계 0.346 m) · 캐리지 앞면–팔레트 간격 22.1 mm, 금지 접촉 0, 팔레트 밀림 없음; 운반 중 승강 관절 0.165 m (명령 lift_target_m 0.2 에 못 미침) → 포크 중심 0.205 m · 밑면 0.193 m · 윗면 0.218 m (fork_center_height 0.04, 두께 0.025): ws1 artifacts/20261011_s4b/smoke/seed_1_v0.055
D7 v2 9회 3.0–22.6 mm, 녹화 장면 5 · 1: 19.4 · 27.0 mm, S4b dev9(seed 0–8, smoke 와 같은 스크립트 · 설정) 완주 8회 5.8–29.4 mm → 최대 29.4 mm = 기준 200 mm 의 14.7 % (D7 이전 6주차 실행 8.0 · 23.8 · 64.9 mm 는 제외): 현재 설정 완주 실행의 하역 오차
insertion_measured: D7 v2 20.4–26.1 mm, 녹화 장면 5 · 1: 25.6 · 35.5 mm, dev9 21.7–37.4 mm → 약 2–4 cm: 현재 설정 실행의 캐리지 앞면–팔레트 간격
10쪽 표준 운용 절차 대조 — 틸트 기구 없음: week-05/SCRIPT.md
§2 실제 지게차 자격증 시험 기준과 우리 지게차 비교 표 (3주차 피드백: 국가공인 시험의 표준 운용 방법): docs/references/week6_feedback.md
[/Sources]

## 14쪽 · 결론 (14:00–14:40, 40초)

정리하면, 실측 차체와 시뮬레이션에서 확인한 것에 맞춰 방향을 정했습니다. 회전 반경이 커서 전진·후진 경로를 넣었고, 삽입 끝까지 보도록 카메라를 캐리지 하단으로 옮겼습니다. 바퀴 회전만으로는 위치가 크게 어긋나 LiDAR SLAM으로 위치를 잡고, 속도를 조절할 수 없는 기존 제어기 대신 구동 보드를 만듭니다. LiDAR보다 낮은 바닥 장애물이 없다는 가정은 현장 조건으로 확인받고자 합니다. 다음 목표는 이 임무를 실차로 옮기는 것입니다. (전환)

[Sources]
출처: 3–9쪽 결과 정리
실측 조향 15°, 회전 반경 2.46 m (사진 추정 1.32 m): sim/models/dls08_measured/README.md
기존 장착 마지막 약 0.25 m 무관측: docs/plans/2026-10-03-near-field-pocket-tracking.md
358 s 에서 SLAM 4.0 cm 대 바퀴 회전만 340 cm (방향 −24.3°): docs/validation/2026-10-04-online-slam-closed-loop.md
기존 제어기 릴레이 on/off, 속도 조절 기능 없음: week-05/SCRIPT.md
과제 센서 구성(RGB-D 1 · 2D LiDAR 1) 유지, 낮은 장애물은 운용 가정: forklift CLAUDE.md
§2 결론 장표 — 무엇이 어떻게 달라지니까 무엇으로 가야 하는지: docs/references/week6_feedback.md
[/Sources]

## 15쪽 · 남은 과제와 일정 (14:40–15:15, 35초)

남은 일정입니다. 중간고사 전에는 모터 전류를 재서 구동 보드 PCB를 설계하고, 시뮬레이션에서 C, D 상황을 확인합니다. 중간고사 뒤에는 구동 보드를 만들고 Jetson에 센서를 연결합니다. 11월 중순부터 실차로 위치 추정과 팔레트 인식을, 12월 초까지 실차 전체 임무를 확인하고, 마지막 주에 최종 시연을 준비합니다. 일정은 실물 진행에 따라 조정될 수 있습니다. (전환)

[Sources]
출처: 개발 로드맵 달력 · 6주차 다음 작업 (실물 일정은 팀 계획)
§4 달력 대응: 8주차 10/23–29 중간고사, 9–10주차 10/30–11/12, 11–12주차 11/13–11/26, 13–14주차 11/27–12/10, 15주차 12/11–17 예비 · 최종 시연일 미정(15주차 가정): docs/plans/2026-09-11-development-roadmap.md
8쪽 다음 작업: 모터 전류 실측 → 전류 제한 · 방열 → PCB, 가정값 실측 교체, 센서 브래킷: week-06/build_deck.py
시험 팔레트 만드는 방법(3D 프린터 · 스티로폼 · 목재 재단) — 11/13–26 배치는 팀 확인 전 제안: docs/references/week3_feedback.md
[/Sources]

## 16쪽 · 확인 요청 (15:15–16:20, 65초)

마지막으로 리보틱스 측에 여쭤볼 것입니다. 파랗게 표시한 세 가지를 먼저 여쭙고 싶습니다. 첫째, 오늘 보여 드린 운반 임무가 실제 작업 흐름과 맞는지입니다. 둘째, 시연 판정 기준입니다. 포크를 어디까지 넣어야 하는지, 지금처럼 삽입 직전에 멈춰 다시 봐도 되는지, 틸트 없이 운반해도 되는지입니다. 셋째, 팔레트 위치와 목적지를 시스템에서 받는지, 로봇이 직접 찾아야 하는지입니다. 나머지 운용 환경과 T11 진입구 폭, 줄인 시험 코스, 원격 정지와 여러 대 운용도 표에 적은 대로 정해 주시면 설계에 반영하겠습니다. 작업장 도면과 운용 영상, 팔레트 도면도 주시면 시뮬레이션 장면을 그에 맞게 만들겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.

[Sources]
출처: 4–6주차 피드백 · 5주차 미팅 질문 이어 받음
§1 미팅 질문 세 구분 — 우리가 궁금한 것(과제 범위 · 평가 기준) · 기업이 제공할 수 있는 것 · 기업이 결정해 줘야 하는 것(예: 실내 · 실외); 파란 세 줄을 먼저 묻는다: docs/references/week4_feedback.md
11쪽 미팅 질문 (실제 운용 상황 · 초기 제공 정보 · 시뮬레이션 설정 적합성): week-05/build_deck.py
T11 진입구 235 / 350 mm 두 해석, 어느 것도 채택하지 않음 (docs/design/2026-09-17-t11-test-article-drawing.md): forklift CLAUDE.md
§1 팀 메모: 리보틱스 미팅 때 물어볼 것이 있음: docs/references/week6_feedback.md
[/Sources]
