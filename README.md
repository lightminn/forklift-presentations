# 자율 지게차 프로젝트 개발 방향

UOS 공식 PowerPoint `UOS_PTformat_B`에서 옮긴 웹 디자인 시스템을 사용하는 **12장, 10분 발표자료**입니다. 과제 요구 → 플랫폼 개조 → 인식·계획·삽입 제어 → A–D 검증 → 개발 일정으로 구성했습니다.

## 공개 발표와 저장소

- **발표 주소:** https://lightminn.github.io/forklift-presentations/
- **GitHub 레포:** https://github.com/lightminn/forklift-presentations

`main`에 push하면 GitHub Actions가 생성물 일치·배포 파일 검사를 수행한 뒤 GitHub Pages에 배포합니다. 배포 결과는 레포의 **Actions → Deploy presentation**에서 확인합니다. 온라인 발표는 로컬 서버 없이 접속할 수 있습니다.

## 로컬 실행

이 폴더에서 실행합니다. Python 3만 필요하며 별도 패키지 설치나 빌드는 필요하지 않습니다.

```bash
bash present.sh
```

브라우저에서 **http://127.0.0.1:8765**를 엽니다. 다른 포트는 `bash present.sh 8766`처럼 지정합니다. 서버 종료는 `Ctrl+C`입니다. HTML 파일을 직접 더블클릭하면 브라우저의 로컬 파일 제한 때문에 실행되지 않을 수 있으므로 HTTP 서버를 사용합니다.

- `←` / `→`, `PageUp` / `PageDown`, `Space`: 슬라이드 이동
- `F`: 전체화면 전환
- `Home` / `End`: 처음 / 마지막 슬라이드
- `R`: 처음으로 돌아가기
- `1`–`9`, `0`: 1–10쪽으로 이동
- 왼쪽 썸네일을 클릭해 이동할 수 있습니다. 전체화면에서는 썸네일이 숨겨집니다.

모든 이미지, 한국어 글꼴, React 및 UOS 런타임을 로컬에 포함했습니다. 외부 인터넷 없이 로컬 서버로 발표할 수 있습니다. 슬라이드의 출처 링크를 여는 경우에는 인터넷이 필요합니다.

## 발표 원고와 내용 수정

- [`SCRIPT.md`](SCRIPT.md): 장별 한국어 발표 원고, 시간 배분, 출처. 배분 합계는 600초이며 실제 발화 시간은 리허설로 조정합니다.
- [`build_deck.py`](build_deck.py): 슬라이드 본문과 원고의 편집 원본.
- [`deck.css`](deck.css): 발표 본문 배치와 타이포그래피.
- [`index.html`](index.html): 생성된 웹 발표자료. 각 슬라이드의 `data-speaker-notes`에 원고와 `[Sources]`가 있습니다. 이 노트 속성은 호환 발표 호스트용이며, 단독 웹 화면에는 원고 패널이 없습니다. 발표자는 `SCRIPT.md`를 별도로 열어 사용합니다.
- [`SOURCES.md`](SOURCES.md): 원문과 이미지 출처, 개발 제안과 미확인 사항의 경계.
- [`VALIDATION.md`](VALIDATION.md): 실제 실행·시각 검증 범위.

편집 원본을 수정했다면 다음 명령으로 HTML과 원고를 다시 생성합니다.

```bash
python3 build_deck.py
```

`index.html`과 `SCRIPT.md`, `slide-metadata.json`을 직접 수정하면 다음 생성 때 덮어씁니다. 서버는 `build_deck.py`를 실행하지 않고 기존 `index.html`을 그대로 제공합니다.

## 제안과 확정 사항

과제 원문의 다섯 단계와 네 가지 접근 시나리오는 요구사항입니다. 판매 링크의 전동 지게차는 개조 후보이며, 구매 여부·제어 구조·상세 사양은 확인되지 않았습니다. 상위 컴퓨터와 MCU의 분담, Hybrid A* 검토, 반복 시험 목표와 8주 일정은 개발 제안입니다. 구현 또는 실험 완료를 의미하지 않습니다.

발표자료는 로봇 구현 폴더와 분리된 전용 레포에서 관리합니다. 이 폴더 전체를 옮기면 다른 컴퓨터에서도 로컬 서버로 실행할 수 있습니다.

## 배포 전 검사

```bash
python3 build_deck.py
python3 -m unittest discover -s tests -v
node --check support.js
node --check deck-stage.js
python3 tools/build_site.py --output _site
```

`_site`는 존재하지 않거나 비어 있어야 합니다. 배포 묶음에는 실행에 필요한 HTML·CSS·JavaScript·그림·글꼴만 넣습니다. `build_deck.py`, 원고, 출처와 개발 도구는 GitHub 레포에서 확인할 수 있습니다.

내용 수정 시 생성된 `index.html`, `SCRIPT.md`, `slide-metadata.json`도 함께 커밋합니다. CI는 생성기 실행 후 이 세 파일에 차이가 있으면 배포를 중단합니다. 워크플로는 `workflow_dispatch`로 수동 재실행할 수도 있습니다.
