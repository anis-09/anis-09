# Changelog

All notable changes to this profile are recorded here.

## [1.0.0] — 2026-07-30

### Added
- Initial animated banner (`dark.svg` / `light.svg`) generated from the Python dot-matrix
  pipeline (`scripts/image_pipeline.py`, `scripts/svg_builder.py`)
- README landing-page structure: hero banner, typing animation, about, tech stack, featured
  project, stats, contribution snake, pinned projects, learning roadmap, connect, footer
- Self-hosted GitHub stats setup guide (`STATS-SETUP.md`)
- Contribution snake GitHub Action (`.github/workflows/snake.yml`)
- `config.json` as the single source of truth for profile data used by the generator

### Known limitations
- Logo-morph animation layer (from the extended banner spec) not yet implemented — needs
  reference logo images to trace
- `LifeXP` featured project card is a placeholder pending a public repo
