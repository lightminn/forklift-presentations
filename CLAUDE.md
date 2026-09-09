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

## Content and validation

Read the target week's `README.md`, `SOURCES.md`, and `VALIDATION.md` before editing technical content. Distinguish assignment requirements, development proposals, candidate hardware, and measured results. Do not describe reference hardware or acceptance figures as team-built hardware or experimental results. Use formal written Korean.

Week 2 has 13 slides and 645 seconds. Its five assignment modules and all four A–D approach cases must remain represented. This count/timing contract does not apply to later weeks. Preserve the original Google Slides image elements and automatic looping without playback controls. Do not reintroduce unsupported numerical evaluation targets.

Inspect content changes at 1920 × 1080 fullscreen; phone checks are not required. Successful generation and static tests do not prove visual fit or robot performance. Preserve relative asset URLs under each weekly path. Commit generated outputs together with source changes; CI rejects generated differences, including new untracked outputs.

Publication index: https://lightminn.github.io/forklift-presentations/
Week 2: https://lightminn.github.io/forklift-presentations/week-02/
Latest published week: https://lightminn.github.io/forklift-presentations/latest/
Original root slide links such as `/#7` continue to open the same week-02 slide.
