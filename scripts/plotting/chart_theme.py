"""Shared visual theme for all pace charts, matching report.html's design
tokens (paper/ink/muted/accent/hairline) instead of seaborn's default
whitegrid look. Colors chosen and validated with the dataviz skill's
validate_palette.js against the paper surface (contrast, chroma floor, CVD
separation all pass).
"""

import matplotlib as mpl

PAPER = "#f3f4f1"
INK = "#14171a"
MUTED = "#5e6672"
ACCENT = "#c1541f"
ACCENT2 = "#1c6ea4"  # secondary identity color (e.g. a second team), pairs with ACCENT
HAIRLINE = "#dbddd5"
GOOD = "#2f8f5b"      # win
CRITICAL = "#b23a2e"  # loss

RESULT_PALETTE = {"W": GOOD, "L": CRITICAL}


def apply_theme():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.edgecolor": HAIRLINE,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "axes.labelsize": 12.5,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlecolor": INK,
        "axes.titlepad": 16,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": True,
        "grid.color": HAIRLINE,
        "grid.linewidth": 0.9,
        "axes.grid": True,
        "axes.axisbelow": True,
        "legend.frameon": False,
        "legend.fontsize": 11,
    })


def style_axes(ax, grid_axis="y"):
    """Call after building the plot: strips chart chrome down to a hairline
    baseline + light grid, editorial-report style."""
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.grid(False)
    ax.grid(axis=grid_axis, color=HAIRLINE, linewidth=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
