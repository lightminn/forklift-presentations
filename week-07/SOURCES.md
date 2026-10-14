# 7주차 출처

쪽별 출처의 전체 목록은 `build_deck.py` 의 각 장 `sources` 와 `SCRIPT.md` 의 [Sources] 블록이다. 보드 자료의 정본은 팀이 2026-10-14 에 보낸 EasyEDA 내보내기이고, 칩 수치는 아래 데이터시트에서 옮겼다.

## 팀 자료 (2026-10-14)

| 파일 | 내용 |
|---|---|
| `diagram.png` | 전력 계통 및 제어 블록 다이어그램 — 3쪽에서 덱 배치로 다시 그림. 고친 곳: TKH7801 → KTH7801, KTH7801 「광학식」→ 자기식(홀 소자), 피드백에서 PWM 제외(두 보드 모두 PWM 핀 미사용), DRV8244/DRV8245 → 회로도대로 DRV8244 × 4, 모터에 승강 추가 |
| `mainboard_1.png` | Motor Board 회로도 1/3쪽(MOTOR&SENSOR): DRV8244SQRYJRQ1 × 4(L · R · M · H), AM26LV32EIPWR × 2, SN65LVDS31DR × 2, SN65LVDS32DR, SN74LVC1G125DBVR × 2, HX JN1.27-2x4P × 2, 5558067-1 × 2 |
| `mt6701_1–3.png` | MT_DS V1.0.0 3D 앞 · 뒷면, 회로도(MT6701QT-ACD, TLV70233DBVR) |
| `kth7801_1–3.png` | KTH_Enc V1.1.2 3D 앞 · 뒷면, 회로도(KTH7801-X-C-SOP8, TLV70233DBVR) |
| `stds_1–3.png` | STDS V1.0.0 회로도, 3D 앞 · 뒷면(SN65LVDS32DR, SN65LVDS1DBVR, TLV70233DBVR, 5558067-1) |
| `spi.png` | TI TIDUED8 Table 4 화면 캡처 — 9쪽 그래프는 원문 PDF 수치로 그림 |
| 사용자 메모 | 채널 L · R 바퀴 · M 조향 · H 승강, 절대 엔코더 KTH7801, STDS 뜻, 5 V 송전 · RJ50 이유, 전송선로 판단식과 전파 속도, LVDT41/14, MISO 왕복 지연 |

## 데이터시트 · 참고 문서

| 문서 | 쓴 값 |
|---|---|
| TI TIDA-060017 / TIDUED8 (2018-07) | 3.2.1.1 · Table 4: 1 Vpp 잡음, CAT5, 단일 종단 SPI 0.5 m 101 → 31 dB, 3 m 전부 Fail, LVDS 0.5 m 101 → 52 dB, 3 m 101 → 45 dB |
| MagnTek MT6701 Rev.1.5 (영문) · 1.9판(중문, 2024-05) | INL ±1.0° 대표 · ±1.5° 최대, VDD 3.0–5.5 V, QFN-16 ABZ Differential 핀(9 -Z · 11 -A · 12 -B), MT6701QT-ACD = AB 1,024펄스/회전 · UVW = -A-B-Z 출고 설정 |
| CONNTEK KTH7801 Series (2024-09-27) | 16비트, 비선형 오차 ±0.35°(대표), 3.3 V 판 3.0–3.6 V, SOP-8 TEST 띄움, SPI CPOL = 1 · CPHA = 1 · 16비트 프레임, CRC 판 12비트 + CRC-4, Table 9 TSCK ≥ 100 ns · TDV ≤ 50 ns · TR 10 ns |
| TI SN65LVDS31 (8.8) | tPHL 최대 2.5 ns |
| TI SN65LVDS32 (8.8) | tPLH · tPHL 최대 3 ns, 내부 종단 없음 |
| TI SN65LVDS1 (6.7) | 드라이버 tPLH · tPHL 최대 3.1 ns |
| TI SN74LVC1G125 (5.6) | tpd 최대 3.7 ns (3.3 V ± 0.3 V, 15 pF), OE Low 일 때 출력 |
| TI AM26LV32E | 3.3 V 4채널 RS-422 수신기 |
| TI TLV702 | 0–300 mA, 드롭아웃 최대 375 mV (300 mA) |
| TI DRV8244-Q1 SLVSG24C | SPI 설정 · 진단, DRVOFF, IPROPI |
| Analog Devices LTC4332 제품 페이지 | 「2MHz SCK Over 10m, Operation Up to 1200m」(사용자가 보낸 기능 목록과 같음) |

## 자산

| 파일 | 쪽 | 만든 방법 |
|---|---|---|
| `assets/80_mt_{top,bottom}.jpg`, `81_kth_{top,bottom}.jpg`, `82_stds_{top,bottom}.jpg` | 2, 6–8, 10 | 팀 3D 렌더의 검은 여백만 잘라 1100 px 로(mt6701_1 은 편집기 탭과 옆 패널 경계선도, kth7801_2 는 렌더를 가로지르는 선 하나도 지움) |
| `assets/80_mt_sch.png`, `81_kth_sch.png`, `82_stds_sch.png` | 7, 8, 10 | 팀 회로도에서 그린 부분만 남김 |
| `assets/81_kth_ldo.png` | 15 | KTH7801 회로도의 레귤레이터(U1) 부분 |
| `assets/83_main_sch.png` | 4 | 메인보드 회로도 1쪽, 크기만 줄임 |
| `assets/83_main_{drv,abz,lvds,buf,rj}.png` | 5, 11, 12, 16 | 메인보드 회로도에서 L 채널 · 바퀴 엔코더 수신 · LVDS · MISO 버퍼 · RJ 잭 부분을 잘라 냄 |
| `assets/75_enc_top.jpg`, `75_enc_bottom.jpg`, `75_enc127_top.jpg`, `75_enc127_layout.jpg` | 17 | KTH7801 보드 이전 판(2.54 mm, 1.27 mm V1.0.1) 3D 렌더와 배치도 — 알파 배경을 검정으로, 여백만 잘라 900 px |

그래프(9 · 13 · 14쪽)와 3쪽 블록도는 `build_deck.py` 가 SVG 로 그린다.
