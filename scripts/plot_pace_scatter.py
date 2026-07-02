"""Scatter: team's own pace vs opponent's pace, one point per regular-season
game, colored by W/L. For a specific team from the master dataset.

Pace is a single value per game (average of the two teams' estimates, see
scripts/pace.py / game_pace column) — both teams necessarily play the same
number of possessions. So x and y are the same column and every point falls
exactly on the diagonal; kept for consistency with the other per-team charts.
"""

import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from plot_pace import PALETTE, slugify, team_alias


def plot_team_pace_scatter(df_team: pd.DataFrame, out_path: str, team_label: str):
    alias = team_alias(team_label)
    sns.set_theme(style="whitegrid", font_scale=1.25)
    fig, ax = plt.subplots(figsize=(6.5, 6.5))

    lo = df_team["game_pace"].min() - 2
    hi = df_team["game_pace"].max() + 2
    ax.plot([lo, hi], [lo, hi], color="grey", linestyle="--", linewidth=1, alpha=0.6)

    mean_pace = df_team["game_pace"].mean()
    ax.axvline(mean_pace, color="black", linestyle=":", linewidth=1.2, alpha=0.7,
               label=f"pace medio {alias}: {mean_pace:.1f}")

    sns.scatterplot(data=df_team, x="game_pace", y="game_pace", hue="result",
                     palette=PALETTE, s=90, ax=ax)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_title(f"Pace squadra vs pace avversaria — {alias}\n(regular season)")
    ax.set_xlabel(f"Pace {alias}")
    ax.set_ylabel("Pace avversaria")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(master_csv: str, team_query: str, out_path: str):
    df = pd.read_csv(master_csv)
    df_team = df[df["team"].str.contains(team_query, case=False)]
    if df_team.empty:
        raise ValueError(f"No rows found for team matching {team_query!r}")
    team_label = df_team["team"].iloc[0]
    plot_team_pace_scatter(df_team, out_path, team_label)
    print(f"{team_label}: {len(df_team)} partite -> {out_path}")
    print(df_team[["giornata", "opponent", "is_home", "team_score", "opp_score",
                    "result", "game_pace"]].sort_values("giornata"))


def main_all(master_csv: str, out_dir: str = "data/pace_vs_opponent"):
    df = pd.read_csv(master_csv)
    for team in sorted(df["team"].unique()):
        df_team = df[df["team"] == team]
        out_path = f"{out_dir}/pace_scatter_{slugify(team_alias(team))}.png"
        plot_team_pace_scatter(df_team, out_path, team)
        print(f"{team}: {len(df_team)} partite -> {out_path}")


if __name__ == "__main__":
    master_csv = sys.argv[1] if len(sys.argv) > 1 else "data/pace_A1_2025-26_all_teams.csv"
    if len(sys.argv) > 2 and sys.argv[2] != "--all":
        team_query = sys.argv[2]
        out_path = sys.argv[3] if len(sys.argv) > 3 else f"data/pace_vs_opponent/pace_scatter_{slugify(team_query)}.png"
        main(master_csv, team_query, out_path)
    else:
        main_all(master_csv)
