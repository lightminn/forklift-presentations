# AGENTS.md

Guidance for coding agents. Keep the project guidance synchronized with `CLAUDE.md`.

## Scope

This repository contains the UOS web presentation for the autonomous forklift assignment. It is separate from robot implementation and the embedded-design lab archive. Do not add robot firmware, a ROS workspace, or simulator configuration here.

## Architecture

- `build_deck.py`: editable slide HTML, Korean narration, timing, and sources.
- `index.html`, `SCRIPT.md`, `slide-metadata.json`: generated files; regenerate them after editing the builder.
- `deck.css`: custom content styling on the official 1280 × 720 UOS canvas.
- `support.js`, `deck-stage.js`, `vendor/uos-slide-template/`: reused UOS presentation runtime. Preserve the official geometry and logos.
- `assets/`, `vendor/`: local images, fonts, and JavaScript; presentation playback must not need a CDN.
- `tools/build_site.py`: copies only publication assets into an empty output directory.
- `.github/workflows/presentation-pages.yml`: validates and deploys `main` to GitHub Pages.

## Commands

```bash
python3 build_deck.py
python3 -m unittest discover -s tests -v
node --check support.js
node --check deck-stage.js
python3 tools/build_site.py --output _site
bash present.sh
```

Python 3.12 and Node are used by CI; Python has no third-party build dependencies. The output directory for `build_site.py` must be absent or empty. Reusing a nonempty directory is rejected without deleting it.

## Content and validation

Read `SOURCES.md` before changing technical claims. Distinguish assignment requirements, development proposals, candidate hardware, and measured results. Do not describe the reference forklift or acceptance-case figures as team-built hardware or experiment results. Keep the five assignment modules and all four A–D approach cases represented.

The deck has 12 slides and a 600-second timing budget; update the publication test deliberately if that contract changes. Inspect rendered slides after content changes. Syntax checks and successful generation do not prove visual layout or robot performance. Preserve relative asset URLs so the deck works below the GitHub repository path.

Publication URL: https://lightminn.github.io/forklift-presentations/
