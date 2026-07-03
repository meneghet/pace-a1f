"""Pace per game across the season, colored by W/L. One plot per team,
built from the master long-format dataset (data/pace_A1_2025-26_all_teams.csv).
"""

import sys
import re
import json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from chart_theme import apply_theme, style_axes, INK, MUTED, ACCENT, RESULT_PALETTE

PALETTE = RESULT_PALETTE

# Short aliases for compact legends/axes/titles, loaded from team_aliases.json
# (sits next to this script). Full names stay in the data and in filenames;
# aliases are only used for on-chart text.
ALIASES_PATH = Path(__file__).parent / "team_aliases.json"
with open(ALIASES_PATH, encoding="utf-8") as f:
    TEAM_ALIASES = json.load(f)


def team_alias(team_name: str) -> str:
    return TEAM_ALIASES.get(team_name, team_name)


def slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


Y_RANGE = (62, 83)


def plot_team_pace(df_team: pd.DataFrame, out_path: str, team_label: str, league_avg_pace: float):
    df_team = df_team.sort_values("giornata").reset_index(drop=True)
    alias = team_alias(team_label)

    apply_theme()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_team, x="giornata", y="game_pace", hue="result",
                     palette=PALETTE, s=70, ax=ax, zorder=3, edgecolor="none")
    sns.lineplot(data=df_team, x="giornata", y="game_pace", color=MUTED, alpha=0.35,
                 ax=ax, legend=False, zorder=2)
    mean_pace = df_team["game_pace"].mean()
    ax.axhline(mean_pace, color=INK, linestyle="--", linewidth=1, alpha=0.7,
               label=f"media {alias}: {mean_pace:.1f}")
    ax.axhline(league_avg_pace, color=ACCENT, linestyle=":", linewidth=1.5, alpha=0.9,
               label=f"media campionato: {league_avg_pace:.1f}")
    ax.set_ylim(*Y_RANGE)
    style_axes(ax, grid_axis="y")
    ax.set_title(f"Pace per partita — {alias}")
    ax.set_xlabel("Giornata")
    ax.set_ylabel("Pace di partita\n(possessi stimati / 40')")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(master_csv: str, out_dir: str = "data/pace_per_team"):
    df = pd.read_csv(master_csv)
    teams = sorted(df["team"].unique())
    league_avg_pace = df["game_pace"].mean()
    print(f"{len(teams)} teams found in {master_csv}, media campionato: {league_avg_pace:.1f}")

    for team in teams:
        df_team = df[df["team"] == team]
        out_path = f"{out_dir}/pace_{slugify(team_alias(team))}_A1_2025-26.png"
        plot_team_pace(df_team, out_path, team, league_avg_pace)
        mean_pace = df_team["game_pace"].mean()
        print(f"  {team}: {len(df_team)} partite, pace medio {mean_pace:.1f} -> {out_path}")


if __name__ == "__main__":
    master_csv = sys.argv[1] if len(sys.argv) > 1 else "data/pace_A1_2025-26_all_teams.csv"
    main(master_csv)
