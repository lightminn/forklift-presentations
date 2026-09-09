# 자율 지게차 프로젝트 · 주차별 발표자료

임베디드구동 및 실습의 자율 지게차 프로젝트 발표를 주차별로 관리한다. 현재 공개 자료는 **2주차 개발 계획**이며, UOS 공식 템플릿을 사용한 13장·10분 45초 발표이다.

## 공개 주소

| 용도 | 주소 |
|---|---|
| 전체 주차 목록 | https://lightminn.github.io/forklift-presentations/ |
| 2주차 발표 | https://lightminn.github.io/forklift-presentations/week-02/ |
| 최근 공개 발표 | https://lightminn.github.io/forklift-presentations/latest/ |

각 주차 주소는 계속 유지한다. `/latest/`는 `published` 상태 중 주차 번호가 가장 큰 자료로 연결한다. 기존 기본 주소의 `#7` 등 슬라이드 링크는 2주차의 같은 쪽으로 연결한다. `main`에 push하면 GitHub Actions의 **Deploy presentation**이 검사 후 GitHub Pages에 배포한다.

## 레포 구조

```text
forklift-presentations/
├── index.html                 # 생성된 주차별 목록
├── archive.css                # 목록 화면 스타일
├── latest/index.html          # 생성된 최근 발표 연결
├── build_deck.py              # 모든 주차와 목록 재생성
├── present.sh                 # 로컬 미리보기
├── week-02/                   # 2주차 원본 및 생성물
│   ├── week.json              # 주차·제목·요약·공개 상태
│   ├── build_deck.py           # 해당 주의 본문·원고·시간 배분
│   ├── index.html
│   ├── SCRIPT.md
│   ├── slide-metadata.json
│   ├── SOURCES.md
│   ├── VALIDATION.md
│   ├── deck.css / *.js
│   └── assets/ / vendor/      # 이미지·글꼴·UOS 런타임
├── tools/
│   ├── new_week.py            # 이전 주를 복사하여 새 초안 생성
│   ├── weekly.py              # 주차 목록 및 연결 페이지 생성
│   └── build_site.py          # 공개 자료만 배포 묶음에 포함
└── tests/
```

`week-03/`, `week-04/`처럼 주차별 폴더를 추가한다. 각 주차는 원고·출처·이미지·실행 파일을 독립 보관한다. 후속 발표를 위해 이전 주 폴더를 수정하거나 공용 이미지로 교체하지 않는다. 글꼴·React·UOS 런타임도 각 주차에 포함하므로 다른 주의 변경에 영향을 받지 않는다.

## 다음 주 자료 작성

레포 루트에서 실행한다. Python 3 표준 라이브러리만 사용한다.

```bash
python3 tools/new_week.py 3 --title "3주차 개발 진행 보고"
```

최근 공개 주차를 복사하여 `week-03/`을 생성한다. 특정 주차를 바탕으로 작성하려면 `--from 2`를 추가한다. 이미 존재하는 주차에는 덮어쓰지 않는다.

1. `week-03/build_deck.py`에서 표지·본문·원고·기준일·장수·시간 배분을 이번 주 내용으로 수정한다. 초기 파일에는 이전 주 내용이 포함되어 있다.
2. 필요한 이미지와 `SOURCES.md`를 갱신한다. `VALIDATION.md`는 **미검증**으로 시작하며 실제 확인한 결과만 기록한다.
3. `week-03/week.json`에 목록용 제목과 요약을 작성한다. 생성 시 `status`는 `draft`이며, 초안은 Pages 배포와 공개 목록에서 제외한다. 공개 GitHub 레포에 커밋한 파일 자체는 열람할 수 있다.
4. 아래 명령으로 생성한 후 `http://127.0.0.1:8765/week-03/`에서 1920 × 1080 전체화면을 확인한다.

```bash
python3 build_deck.py
bash present.sh
```

5. 내용과 화면 확인이 끝나면 `week.json`의 `status`를 `published`로 변경하고 다시 생성·검사한다. 해당 주차 폴더와 갱신된 `index.html`, `latest/index.html`을 함께 커밋하여 `main`에 push한다. 목록과 `/latest/`는 새 공개 주차에 맞게 자동 갱신된다.

```json
{
  "week": 3,
  "title": "3주차 개발 진행 보고",
  "summary": "이번 주 수행 내용에 맞게 작성",
  "status": "published"
}
```

위 설정은 공개할 때의 예시이며, 현재 레포에 3주차 자료가 생성되어 있다는 뜻은 아니다.

## 발표 내용 구성 원칙

각 장은 서로 다른 질문에 답하고 새로운 내용을 전달해야 한다. 초안을 작성하기 전에 장별 핵심 내용을 한 문장씩 정하고, 같은 설명이 반복되는 장은 통합하거나 삭제한다.

- **ROS 2 전체 구성과 소프트웨어 흐름은 한 장에서 설명한다.** 뒤에서 제목만 바꾸어 전체 파이프라인을 다시 설명하지 않는다.
- 세부 장에서는 해당 모듈의 구현 방법·선택 근거·검증 결과·문제점을 다룬다. 앞선 전체 구조는 필요한 구간만 짧게 참조한다.
- 이번 주의 수행 내용과 확인 결과를 중심으로 구성하고, 결론은 남은 문제와 다음 조치로 마무리한다. 장수나 시간을 채우기 위한 반복 설명은 추가하지 않는다.
- 발표자료와 `SCRIPT.md`를 함께 순서대로 검토하여 내용과 원고 양쪽의 중복을 확인한다. 단어가 같다는 이유만으로 삭제하지 않고, 새로 전달하는 정보가 있는지 판단한다. 중복 정리 후 장수·시간을 조정하고 해당 주 `VALIDATION.md`에 점검 결과를 기록한다.

이 기준은 2주차 발표에서 지적된 ROS 2·소프트웨어 흐름의 반복을 방지하기 위한 후속 주차 작성 기준이다.

## 로컬 실행 및 발표

```bash
bash present.sh
```

**http://127.0.0.1:8765/**에서 주차를 선택한다. 다른 포트는 `bash present.sh 8766`으로 지정한다. 서버는 기존 생성 파일을 제공하므로 내용 수정 후 `python3 build_deck.py`를 실행해야 한다.

- `F`: 전체화면. 발표 기준은 16:9, 1920 × 1080이다.
- `←` / `→`, `PageUp` / `PageDown`, `Space`: 슬라이드 이동.
- `Home` / `End`, `R`: 처음·마지막 장 이동 또는 처음으로 복귀.
- `1`–`9`, `0`: 1–10쪽 바로 이동.
- 각 주의 `SCRIPT.md`: 발표자용 원고. 별도 창이나 편집기에서 연다.

폰트·이미지·실행 파일은 로컬에 포함되어 인터넷 없이 로컬 서버로 발표할 수 있다. 외부 출처 링크를 여는 경우에는 인터넷이 필요하다.

## 검사 및 배포

```bash
python3 build_deck.py
python3 -m unittest discover -s tests -v
node --test tests/*.test.cjs
find week-* -type d -name vendor -prune -o -type f -name '*.js' -print0 | xargs -0 -r -n1 node --check
python3 tools/build_site.py --output _site
```

`_site`는 존재하지 않거나 비어 있어야 한다. 비어 있지 않은 폴더와 레포 루트를 출력 대상으로 지정하면 파일을 보존하고 거부한다. 반복 검사 시에는 새로운 출력 경로를 사용한다.

CI는 전체 생성 결과가 커밋된 파일과 일치하는지 확인하고, 주차별 경로·자산·초안 제외·기존 주차 보존·주소 연결 및 JavaScript 검사를 통과한 경우에 배포한다. 주차 폴더를 추가할 때 워크플로의 경로 목록을 수정할 필요가 없다. 13장·645초와 A–D 동작 검사는 2주차의 계약이며, 이후 주차는 해당 주제에 맞게 장수·시간을 정한다.

배포 묶음에는 목록·연결 페이지와 공개한 주차의 HTML·CSS·JavaScript·이미지·글꼴만 포함한다. 원고·출처·개발 도구는 [GitHub 레포](https://github.com/lightminn/forklift-presentations)에서 확인한다. [2주차 자료 안내](week-02/README.md), [2주차 출처](week-02/SOURCES.md), [2주차 검증 기록](week-02/VALIDATION.md)을 함께 참고한다.
