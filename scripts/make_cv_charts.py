"""One-off: clean variants (no mean-reference lines) of two charts, for a
minimal CV-attachment report. Reuses the master dataset; does not touch the
main pipeline outputs.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from plot_pace import PALETTE, team_alias, Y_RANGE
from plot_pace_deviation import DEV_RANGE

OUT_DIR = "data/cv_report"
TEAMS = ["Famila Wuber Schio", "Umana Reyer Venezia"]


def clean_pace_over_time(df_team, team, out_path):
    df_team = df_team.sort_values("giornata").reset_index(drop=True)
    alias = team_alias(team)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    sns.scatterplot(data=df_team, x="giornata", y="game_pace", hue="result",
                     palette=PALETTE, s=80, ax=ax)
    sns.lineplot(data=df_team, x="giornata", y="game_pace", color="grey", alpha=0.4,
                 ax=ax, legend=False)
    ax.set_ylim(*Y_RANGE)
    ax.set_title(f"Pace per partita — {alias}")
    ax.set_xlabel("Giornata")
    ax.set_ylabel("Pace di partita")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def clean_pace_vs_opponent(df_team, team, out_path):
    alias = team_alias(team)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 6))

    lo = min(df_team["team_pace"].min(), df_team["opp_pace"].min()) - 2
    hi = max(df_team["team_pace"].max(), df_team["opp_pace"].max()) + 2
    ax.plot([lo, hi], [lo, hi], color="grey", linestyle="--", linewidth=1, alpha=0.6)

    sns.scatterplot(data=df_team, x="team_pace", y="opp_pace", hue="result",
                     palette=PALETTE, s=90, ax=ax)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_title(f"Pace {alias} vs pace avversaria")
    ax.set_xlabel(f"Pace {alias}")
    ax.set_ylabel("Pace avversaria")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv("data/pace_A1_2025-26_all_teams.csv")

    for team in TEAMS:
        df_team = df[df["team"] == team]
        alias_slug = team_alias(team).lower().replace(" ", "_")
        clean_pace_over_time(df_team, team, f"{OUT_DIR}/pace_over_time_{alias_slug}_clean.png")
        clean_pace_vs_opponent(df_team, team, f"{OUT_DIR}/pace_vs_opponent_{alias_slug}_clean.png")
    print(f"Saved clean charts to {OUT_DIR}/")


if __name__ == "__main__":
    main()
