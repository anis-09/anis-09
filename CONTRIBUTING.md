# Maintaining this profile

This is a personal profile repo, but it's built like a small software project — the generated
files (`assets/banner/*.svg`) are build output, not source. Never hand-edit them; regenerate
instead.

## Source of truth

| Editable (source) | Generated (never hand-edit) |
|---|---|
| `config.json` | `assets/banner/dark.svg` |
| `scripts/*.py` | `assets/banner/light.svg` |
| Your portrait photo | `output/*_preview.png` |

## Common updates

**Change your role, tagline, stack, or contact info**
Edit `config.json`, then re-run the generator (see below). Nothing else needs to change.

**Update the portrait**
Replace the source photo and re-run `scripts/image_pipeline.py` — pick a photo with a flat,
evenly lit background (see the framing notes in the original prompt). A busy background is the
single biggest cause of a bad segmentation.

**Change the color palette**
Edit the `PALETTE` / `LIGHT_PALETTE` dicts at the top of `scripts/svg_builder.py`. Keep it to
five colors max, per the design system.

**Regenerate the banner**
```bash
cd scripts
python3 image_pipeline.py /path/to/portrait.jpg
python3 svg_builder.py
```
This writes fresh `dark.svg` / `light.svg` into `output/`, from which you copy into
`assets/banner/`.

**Update the contribution snake**
Nothing to do manually — `.github/workflows/snake.yml` regenerates it every 12 hours and on every
push to `main`. Trigger it manually from the Actions tab if you want it sooner.

**Update stats theme colors**
Edit the query params on the stats URLs directly in `README.md` — see `STATS-SETUP.md` for the
full parameter reference.

## Before committing a change

- [ ] Banner still renders correctly in both light and dark GitHub themes
- [ ] File size of each SVG stays under ~1MB (`ls -la assets/banner/`)
- [ ] No placeholder text (`YOUR-STATS-INSTANCE`, etc.) left in `README.md` once deployed
- [ ] Links in the README resolve (no 404s)
