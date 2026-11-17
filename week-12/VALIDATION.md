# 12주차 발표자료 검증 기록

## 2026-11-17 작성 · 게시

- 11주차를 복사해(`tools/new_week.py 12 --from 11`) 새로 썼다. 표지 + 6장 · 370초. 11주차 그림은 로고와 후보 화면(`s04_candidates.png` 로 이름만 바꿈)만 남기고 지웠고, `make_replan.py` 도 뺐다.
- 수치 대조: 02 장은 `2026-11-17-hw-day.md` 「H743 링크」 표와 원자료 `jetson/h743_link.txt`(PASS v3 600.0s states=59999 seq_gaps=0 host_gap_max=10.661ms rtt 3.97/10.26ms resets=0), 03 장은 「다리 정체」 표와 `jetson/stall/{idle,load}/verdict.txt`(최대 21.9 · 29.6 ms, ALL PASS), `jetson/imu.txt`(399.8 · 200.1 Hz, dropped 0). 04 장은 B-P1b 결론(69/84), B-P2d 4 절(68/84), 출발 이동 시험 2 절(67 → 69, 틀린 확정 0). 05 장은 짧은 곡선 비교 2 절(16 → 8, 9 = 9, 90 → 18).
- 05 장 영상 원본 두 개를 ws1 에서 받아 sha256 을 대조했다(9b3bc418… · e53ef020…, 총괄이 준 값과 일치). 끔 실행 `result.json` 의 운반 cusp 재계획 2 회(101.2 · 113.2 s), 켬 실행 0 회를 확인했고, 자른 구간(시뮬 40–245 s)에 두 실행의 꺼내기 · 운반 · 하역이 모두 들어간다.
- 사진: H743 은 사용자 사진을 잘라 EXIF 를 지웠다. D435 · Jetson · LiDAR 사진의 출처와 라이선스는 SOURCES.md. 새로 만든 JPEG 에 EXIF 가 없음을 확인했다.
- `python3 build_deck.py`(주차 · 전체) 통과, `python3 -m unittest discover -s tests` 12 통과, `node --test tests/*.test.cjs` 7 통과, JavaScript `node --check` 통과, `tools/build_site.py` 새 출력 폴더에 공개 12주 398 파일, `latest/` 는 week-12.
- 1920 × 1080 렌더(Playwright, 썸네일 줄 끔 `?_snthumb=1`)로 표지와 1–6쪽 확인: 02 장 표의 Jetson 칸 넘침(왕복 시간 칸을 「9.3 · 10.2 ms」로 줄임), 03 장 헤드라인 두 줄 · 사진 높이 불일치(헤드라인 줄임, 사진 칸 230 px 고정), LiDAR 사진의 회전 화살표(잘라 냄), 01 장 표 아래 빈 공간(행 간격 늘림), 06 장 첫 행 두 줄(문구 줄임)을 고쳤다. 05 장 영상은 6 s 뒤 재생 중(일시정지 아님), 750 × 739 px 로 표시됨을 확인했다.
- 덱 검토는 Codex · 서브에이전트로 돌리지 않았다(프로젝트 메모리 deck-user-reviews). 사용자가 게시본을 확인한다.
