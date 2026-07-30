"""
svg_builder.py
Builds dark.svg / light.svg banners from the dithered dot arrays + profile config.
Source of truth. Never hand-edit the generated SVGs.
"""
import json
import random
import numpy as np

BANNER_W, BANNER_H = 1180, 610
GRID_W, GRID_H = 300, 340

PALETTE = {
    "bg": "#09090B",
    "purple": "#7C3AED",
    "cyan": "#22D3EE",
    "green": "#10B981",
    "white": "#F8FAFC",
    "gray": "#94A3B8",
}

LIGHT_PALETTE = {
    "bg": "#FFFFFF",
    "panel": "#F4F4F5",
    "purple": "#7C3AED",
    "cyan": "#0891B2",
    "green": "#059669",
    "text": "#09090B",
    "gray": "#52525B",
}

random.seed(42)


def _row_runs(dots):
    """Yield (row, run_start_col, run_len) for horizontal runs of True cells.
    Run-length encoding: flat dark regions (hair, shirt) collapse to one
    rect instead of one path segment per pixel, which is what keeps file
    size in budget at full dot density."""
    h, w = dots.shape
    for y in range(h):
        row = dots[y]
        x = 0
        while x < w:
            if row[x]:
                start = x
                while x < w and row[x]:
                    x += 1
                yield y, start, x - start
            else:
                x += 1


def dots_to_path_groups(dots, ox, oy, dot_w, dot_h, n_groups=60):
    """Return list of path-d strings, one per group, scattered across the whole
    portrait (not by spatial region) so the intro fade shimmers evenly.
    Horizontal runs are merged into single rect commands (run-length encoding)
    to keep file size within budget at full dot density."""
    runs = list(_row_runs(dots))
    n = len(runs)
    order = np.arange(n)
    np.random.default_rng(7).shuffle(order)
    groups = [[] for _ in range(n_groups)]
    for i, idx in enumerate(order):
        groups[i % n_groups].append(runs[idx])

    dh1 = round(dot_h, 1)
    paths = []
    for g in groups:
        cmds = []
        for (row, start, length) in g:
            x = ox + start * dot_w
            y = oy + row * dot_h
            w = round(length * dot_w, 1)
            cmds.append(f"M{x:.1f},{y:.1f}h{w}v{dh1}h{-w}Z")
        paths.append("".join(cmds))
    return paths


def build_portrait_svg(dots, ox, oy, box_w, box_h, fill_color, animate=True):
    dot_w = box_w / GRID_W
    dot_h = box_h / GRID_H
    groups = dots_to_path_groups(dots, ox, oy, dot_w, dot_h, n_groups=60)

    out = ['<g id="portrait-dots">']
    for i, d in enumerate(groups):
        if not d:
            continue
        delay = (i / len(groups)) * 1.9  # spread across ~1.9s of the 3.2s intro
        anim = ""
        if animate:
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.5s" fill="freeze" '
                f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            )
        out.append(f'<path d="{d}" fill="{fill_color}" opacity="0">{anim}</path>')
    out.append("</g>")
    return "\n".join(out)


def dotted_leader(label, value, y, x_label, x_value_right, color_label, color_value, font_size=14):
    """Row with label ... value, dots computed from remaining width (never hand-edited)."""
    label_w = len(label) * font_size * 0.56
    value_w = len(value) * font_size * 0.60
    gap_start = x_label + label_w + 6
    gap_end = x_value_right - value_w - 6
    dot_span = max(gap_end - gap_start, 0)
    n_dots = max(int(dot_span / 6), 0)
    dots = " ".join(["\u2022"] * n_dots) if n_dots > 0 else ""
    return f'''<text x="{x_label}" y="{y}" font-family="JetBrains Mono, monospace" font-size="{font_size}" fill="{color_label}">{label}</text>
<text x="{gap_start}" y="{y}" font-family="JetBrains Mono, monospace" font-size="{font_size}" fill="#2D3343" letter-spacing="4">{dots}</text>
<text x="{x_value_right}" y="{y}" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="{font_size}" fill="{color_value}" textLength="{value_w:.0f}" lengthAdjust="spacingAndGlyphs">{value}</text>'''


def build_banner(config, dots_array, mode="dark"):
    pal = PALETTE if mode == "dark" else LIGHT_PALETTE
    bg = pal["bg"]
    panel_bg = "#111114" if mode == "dark" else pal["panel"]
    border = "#1F1F23" if mode == "dark" else "#E4E4E7"
    text_primary = pal["white"] if mode == "dark" else pal["text"]
    text_secondary = pal["gray"]
    accent = pal["purple"]
    accent2 = pal["cyan"]
    dot_fill = pal["white"] if mode == "dark" else "#18181B"

    left_w = int(BANNER_W * 0.38)
    pad = 32
    portrait_box_w = left_w - pad * 2
    portrait_box_h = int(portrait_box_w * (GRID_H / GRID_W))
    portrait_x = pad
    portrait_y = (BANNER_H - portrait_box_h) // 2

    right_x = left_w + 48
    right_w = BANNER_W - right_x - pad

    portrait_svg = build_portrait_svg(
        dots_array, portrait_x, portrait_y, portrait_box_w, portrait_box_h, dot_fill
    )

    # --- info panel rows ---
    rows_data = [
        ("Subject", config["name"]),
        ("Role", config["role"]),
        ("Origin", config["location"]),
        ("Status", config["status"]),
        ("Core.Lang", ", ".join(config["stack"]["languages"][:3])),
        ("Core.Frontend", ", ".join(config["stack"]["frontend"][:3])),
        ("Core.Backend", ", ".join(config["stack"]["backend"])),
        ("Core.Database", ", ".join(config["stack"]["database"])),
        ("Grid.Mail", config["email"]),
        ("Grid.LinkedIn", config["linkedin"].replace("https://", "")),
        ("Grid.GitHub", config["github"].replace("https://", "")),
    ]

    row_y_start = 158
    row_gap = 23
    rows_svg = []
    for i, (label, value) in enumerate(rows_data):
        y = row_y_start + i * row_gap
        rows_svg.append(
            dotted_leader(label, value, y, right_x, right_x + right_w, text_secondary, text_primary)
        )

    typing_lines = config.get("typing_lines", ["Turning ideas into scalable software."])
    typing_text = typing_lines[0]

    radial_glow = ""
    if mode == "dark":
        radial_glow = f'''<radialGradient id="portraitGlow" cx="50%" cy="45%" r="60%">
  <stop offset="0%" stop-color="{accent}" stop-opacity="0.10"/>
  <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
</radialGradient>
<rect x="0" y="0" width="{left_w}" height="{BANNER_H}" fill="url(#portraitGlow)"/>'''

    svg = f'''<svg width="{BANNER_W}" height="{BANNER_H}" viewBox="0 0 {BANNER_W} {BANNER_H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{config['name']} — {config['role']} — animated GitHub profile banner">
<title>{config['name']} · {config['role']}</title>
<defs>
{radial_glow}
</defs>
<rect x="0" y="0" width="{BANNER_W}" height="{BANNER_H}" rx="14" fill="{bg}"/>
<rect x="0.5" y="0.5" width="{BANNER_W-1}" height="{BANNER_H-1}" rx="14" fill="none" stroke="{border}" stroke-width="1"/>

<!-- LEFT: portrait panel -->
<text x="{pad}" y="40" font-family="JetBrains Mono, monospace" font-size="12" letter-spacing="2" fill="{text_secondary}">VISUAL.MAP</text>
<rect x="{portrait_x-8}" y="{portrait_y-8}" width="{portrait_box_w+16}" height="{portrait_box_h+16}" rx="10" fill="{panel_bg}" stroke="{border}" stroke-width="1"/>
<g shape-rendering="crispEdges">
{portrait_svg}
</g>
<text x="{pad}" y="{BANNER_H-52}" font-family="JetBrains Mono, monospace" font-size="11" fill="{text_secondary}">Portrait Quality <tspan fill="{accent2}">LIVE</tspan></text>
<text x="{pad}" y="{BANNER_H-34}" font-family="JetBrains Mono, monospace" font-size="11" fill="{text_secondary}">Resolution 300×340</text>
<text x="{pad}" y="{BANNER_H-16}" font-family="JetBrains Mono, monospace" font-size="11" fill="{text_secondary}">Engine Python Pipeline</text>

<!-- divider -->
<line x1="{left_w}" y1="24" x2="{left_w}" y2="{BANNER_H-24}" stroke="{border}" stroke-width="1"/>

<!-- RIGHT: terminal / info panel -->
<circle cx="{right_x+6}" cy="46" r="4" fill="#EF4444" opacity="0.7"/>
<circle cx="{right_x+20}" cy="46" r="4" fill="#F59E0B" opacity="0.7"/>
<circle cx="{right_x+34}" cy="46" r="4" fill="#10B981" opacity="0.7"/>
<text x="{right_x+52}" y="50" font-family="JetBrains Mono, monospace" font-size="13" fill="{text_secondary}">profile.sh --live</text>

<circle cx="{right_x+right_w-64}" cy="46" r="4" fill="#EF4444">
  <animate attributeName="opacity" values="0.8;1;0.8" dur="2.5s" repeatCount="indefinite"/>
</circle>
<text x="{right_x+right_w-54}" y="50" font-family="JetBrains Mono, monospace" font-size="12" fill="#EF4444" letter-spacing="1">LIVE</text>

<line x1="{right_x}" y1="70" x2="{right_x+right_w}" y2="70" stroke="{border}" stroke-width="1"/>

<text x="{right_x}" y="102" font-family="Inter, sans-serif" font-size="26" font-weight="600" fill="{text_primary}">{config['name']}</text>
<text x="{right_x}" y="126" font-family="JetBrains Mono, monospace" font-size="13" fill="{accent2}">@{config['handle']}</text>

<g font-family="JetBrains Mono, monospace">
{chr(10).join(rows_svg)}
</g>

<line x1="{right_x}" y1="{row_y_start + len(rows_data)*row_gap + 6}" x2="{right_x+right_w}" y2="{row_y_start + len(rows_data)*row_gap + 6}" stroke="{border}" stroke-width="1"/>

<text x="{right_x}" y="{row_y_start + len(rows_data)*row_gap + 34}" font-family="JetBrains Mono, monospace" font-size="14" fill="{accent2}">&gt; <tspan fill="{text_primary}">{typing_text}</tspan><tspan fill="{accent2}">
  <animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/>
</tspan><tspan fill="{accent2}">_</tspan></text>
</svg>'''
    return svg


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/claude/github-profile/scripts")
    with open("/home/claude/github-profile/config.json") as f:
        config = json.load(f)

    for mode in ("dark", "light"):
        dots = np.load(f"/home/claude/github-profile/output/dots_{mode}.npy")
        svg = build_banner(config, dots, mode)
        out_path = f"/home/claude/github-profile/output/{mode}.svg"
        with open(out_path, "w") as f:
            f.write(svg)
        print(mode, "svg bytes:", len(svg))
