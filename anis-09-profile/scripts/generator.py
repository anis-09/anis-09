"""
generator.py
Single entry point for the banner build.

Usage:
    python3 generator.py [path/to/portrait.jpg]

Reads config.json, runs the portrait through image_pipeline.py, builds both
SVGs via svg_builder.py, validates them, and writes dark.svg / light.svg to
../output/.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from image_pipeline import process_portrait
from svg_builder import build_banner

ROOT = Path(__file__).parent.parent
DEFAULT_PORTRAIT = "/mnt/user-data/uploads/WhatsApp_Image_2026-07-30_at_11_35_41_AM.jpeg"


def validate_svg(svg_text, mode):
    errors = []
    if not svg_text.strip().startswith("<svg"):
        errors.append(f"[{mode}] does not start with <svg>")
    if svg_text.count("<svg") != 1:
        errors.append(f"[{mode}] more than one <svg> root element")
    size_kb = len(svg_text.encode("utf-8")) / 1024
    if size_kb > 1024:
        errors.append(f"[{mode}] file size {size_kb:.0f}KB exceeds 1MB target")
    if "</svg>" not in svg_text:
        errors.append(f"[{mode}] missing closing </svg> tag")
    return errors


def main():
    portrait_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PORTRAIT

    with open(ROOT / "config.json") as f:
        config = json.load(f)

    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)

    all_errors = []
    for mode in ("dark", "light"):
        print(f"[{mode}] processing portrait...")
        dots = process_portrait(portrait_path, mode)
        np.save(out_dir / f"dots_{mode}.npy", dots)

        print(f"[{mode}] building SVG...")
        svg = build_banner(config, dots, mode)

        errors = validate_svg(svg, mode)
        all_errors.extend(errors)

        out_path = out_dir / f"{mode}.svg"
        out_path.write_text(svg)
        print(f"[{mode}] wrote {out_path} ({len(svg.encode('utf-8')) / 1024:.0f}KB)")

    if all_errors:
        print("\nValidation FAILED:")
        for e in all_errors:
            print(" -", e)
        sys.exit(1)

    print("\nValidation passed. Copy output/dark.svg and output/light.svg into assets/banner/.")


if __name__ == "__main__":
    main()
