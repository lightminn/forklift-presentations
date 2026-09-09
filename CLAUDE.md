# CLAUDE.md

Guidance for coding agents. Keep the project guidance synchronized with `CLAUDE.md`.

## Scope

This repository contains weekly UOS web presentations for the autonomous forklift assignment. It is separate from robot implementation and the embedded-design lab archive. Do not add robot firmware, a ROS workspace, or simulator configuration here.

## Weekly architecture

- `week-NN/`: independent presentation snapshot, including source, narration, provenance, assets, styles and local runtime. The existing development proposal is `week-02/`. Add a new directory for each following week; do not overwrite previous weeks to prepare the next presentation.
- `week-NN/week.json`: integer week (1–99), title, summary, and status (`draft` or `published`). Directory name must match the week. Drafts are excluded from the Pages bundle and index; this does not hide files committed to the public GitHub repository.
- `week-NN/build_deck.py`: editable slide HTML, Korean narration, timing, and sources. Generates that week's `index.html`, `SCRIPT.md`, and `slide-metadata.json`.
- `week-NN/deck.css`: body layout on the official 1280 × 720 UOS canvas.
- `week-NN/support.js`, `deck-stage.js`, `vendor/`: local UOS/React runtime and fonts. Preserve official geometry and logos. Keep weekly copies independent so later changes cannot affect earlier decks.
- Root `build_deck.py`: regenerates all weeks and the public index. Root `index.html` is the weekly archive, not a slide deck. `latest/index.html` redirects to the highest numbered published week, preserving query and slide hash.
- `tools/new_week.py`: copies a previous week as an independent draft and resets validation to unverified. Copied content, dates, timing, and sources must be updated for the new week.
- `tools/build_site.py`: packages only published weeks and navigation pages. Destination must be absent or empty; never delete existing output automatically.
- `.github/workflows/presentation-pages.yml`: validates generated files, tests and JavaScript, then deploys `main` to Pages. Week discovery is automatic.

## Commands

```bash
python3 tools/new_week.py 3 --title "3주차 개발 진행 보고"
python3 build_deck.py
python3 -m unittest discover -s tests -v
node --test tests/*.test.cjs
find week-* -type d -name vendor -prune -o -type f -name '*.js' -print0 | xargs -0 -r -n1 node --check
python3 tools/build_site.py --output _site
bash present.sh
```

The creation command is an example; do not create a new week unless requested. Python has no third-party build dependencies. CI uses Python 3.12 and Node.

## 발표 구성 및 중복 방지

2026-09-09 사용자 피드백: 2주차 발표에서 앞서 설명한 내용이 뒤에서 반복되었으며, 특히 ROS 2 구성과 소프트웨어 처리 흐름의 중복이 많았다. 다음 주차부터 아래 기준을 적용한다.

- 본문 작성 전에 각 장이 답할 질문과 새로 전달할 핵심 내용을 한 문장씩 정한다. 같은 질문에 같은 답을 제시하는 장은 통합하거나 삭제한다. 이전 자료를 복사했더라도 기존 목차를 그대로 유지하지 않는다.
- ROS 2 전체 구성과 소프트웨어 처리 흐름은 한 장에서 설명한다. 앞에서 설명한 전체 흐름을 뒤의 ‘예상 주행 파이프라인’ 등 다른 제목으로 다시 설명하지 않는다. 이후 세부 장은 해당 모듈의 구현 방법, 선택 근거, 검증 결과 또는 해결할 문제를 다룬다. 필요하면 전체 구조를 짧게 참조하거나 해당 구간만 표시한다.
- 중복은 단어가 아니라 전달하는 내용으로 판단한다. ROS 2 등의 용어나 입력·출력 표기를 필요한 곳에서 다시 사용하는 것은 허용하되, 같은 역할·처리 순서를 표현만 바꾸어 재설명하지 않는다. 개요와 상세 설명을 분리할 때는 상세 장에 추가되는 구체적인 정보가 있어야 한다.
- 주간 발표는 이번 주에 새로 수행·확인·결정한 내용과 다음 조치에 집중한다. 배경 설명은 이해에 필요한 범위로 제한하고, 결론에서는 시스템 개요를 재설명하지 않고 확인된 결과·남은 문제·다음 조치를 정리한다. 장수나 발표 시간을 채우기 위해 같은 설명을 추가하지 않는다.
- 완성 후 슬라이드와 `SCRIPT.md`를 함께 순서대로 읽어 장 사이의 의미상 중복을 점검한다. 화면만 간결하게 만들고 원고에서 같은 설명을 반복하는 방식도 피한다. 중복을 통합·삭제한 후 장수와 시간 배분을 조정하고, 점검 결과를 해당 주의 `VALIDATION.md`에 간단히 기록한다. 단순 키워드 검색만으로 중복 점검을 완료한 것으로 간주하지 않는다.

## Content and validation

Read the target week's `README.md`, `SOURCES.md`, and `VALIDATION.md` before editing technical content. Distinguish assignment requirements, development proposals, candidate hardware, and measured results. Do not describe reference hardware or acceptance figures as team-built hardware or experimental results. Use formal written Korean.

Week 2 has 13 slides and 645 seconds. Its five assignment modules and all four A–D approach cases must remain represented. This count/timing contract does not apply to later weeks. Preserve the original Google Slides image elements and automatic looping without playback controls. Do not reintroduce unsupported numerical evaluation targets.

Inspect content changes at 1920 × 1080 fullscreen; phone checks are not required. Successful generation and static tests do not prove visual fit or robot performance. Preserve relative asset URLs under each weekly path. Commit generated outputs together with source changes; CI rejects generated differences, including new untracked outputs.

Publication index: https://lightminn.github.io/forklift-presentations/
Week 2: https://lightminn.github.io/forklift-presentations/week-02/
Latest published week: https://lightminn.github.io/forklift-presentations/latest/
Original root slide links such as `/#7` continue to open the same week-02 slide.
