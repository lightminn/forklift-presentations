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

- 발표의 목적과 청중에게 필요한 정보를 기준으로 주제·순서·분량을 정한다. 특정 항목의 포함이나 고정된 장수를 전제하지 않는다.
- 각 장의 역할과 새로 전달하는 내용을 확인한다. 제목이나 표현만 바꾼 동일한 설명은 통합하거나 삭제한다.
- 개요·상세 설명·요약은 이해에 도움이 되는 경우에 구성한다. 같은 내용을 다시 다룰 때에는 설명의 깊이나 관점이 추가되는지, 또는 짧은 정리가 필요한지 판단한다.
- 슬라이드와 발표 원고를 전체 흐름으로 검토하여 불필요한 반복을 줄인다. 중복 여부는 단어의 재등장이 아니라 전달 내용과 설명의 필요성으로 판단하고, 정리한 내용에 맞춰 장수와 시간을 조정한다.
- 개발 중 발생한 오류와 그 수정, 내부 규칙·검사·예외 처리 같은 구현 세부는, 설명하지 않으면 청중이 발표 흐름을 이해할 수 없는 경우가 아니면 넣지 않는다. 결과와 다음 결정에 필요한 사실만 남긴다.

## Content and validation

Read the target week's `README.md`, `SOURCES.md`, and `VALIDATION.md` before editing technical content. Distinguish assignment requirements, development proposals, candidate hardware, and measured results. Do not describe reference hardware or acceptance figures as team-built hardware or experimental results. Use formal written Korean.

Week 2 has 13 slides and 645 seconds. Its five assignment modules and all four A–D approach cases must remain represented. This count/timing contract does not apply to later weeks. Preserve the original Google Slides image elements and automatic looping without playback controls. Do not reintroduce unsupported numerical evaluation targets.

Inspect content changes at 1920 × 1080 fullscreen; phone checks are not required. Successful generation and static tests do not prove visual fit or robot performance. Preserve relative asset URLs under each weekly path. Commit generated outputs together with source changes; CI rejects generated differences, including new untracked outputs.

Publication index: https://lightminn.github.io/forklift-presentations/
Week 2: https://lightminn.github.io/forklift-presentations/week-02/
Latest published week: https://lightminn.github.io/forklift-presentations/latest/
Original root slide links such as `/#7` continue to open the same week-02 slide.
