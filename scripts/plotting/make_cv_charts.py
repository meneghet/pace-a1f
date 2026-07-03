"""One-off: compact variant of the pace-over-time chart, for a minimal
CV-attachment report. Reuses the master dataset; does not touch the main
pipeline outputs.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from plot_pace import PALETTE, team_alias, Y_RANGE
from plot_pace_deviation import DEV_RANGE
from chart_theme import apply_theme, style_axes, INK, MUTED, ACCENT

OUT_DIR = "data/cv_report"
TEAMS = ["Famila Wuber Schio", "Umana Reyer Venezia"]


def clean_pace_over_time(df_team, team, out_path, league_avg_pace):
    df_team = df_team.sort_values("giornata").reset_index(drop=True)
    alias = team_alias(team)

    apply_theme()
    fig, ax = plt.subplots(figsize=(9, 4.2))
    sns.scatterplot(data=df_team, x="giornata", y="game_pace", hue="result",
                     palette=PALETTE, s=80, ax=ax, zorder=3, edgecolor="none")
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
    ax.set_ylabel("Pace di partita")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv("data/pace_A1_2025-26_all_teams.csv")
    league_avg_pace = df["game_pace"].mean()

    for team in TEAMS:
        df_team = df[df["team"] == team]
        alias_slug = team_alias(team).lower().replace(" ", "_")
        clean_pace_over_time(df_team, team, f"{OUT_DIR}/pace_over_time_{alias_slug}_clean.png",
                              league_avg_pace)
    print(f"Saved charts to {OUT_DIR}/")


if __name__ == "__main__":
    main()
