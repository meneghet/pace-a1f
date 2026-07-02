"""Team-level scatter: average pace (x) vs win rate (y), one point per team,
labeled with the team name.
"""

import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from plot_pace import team_alias


def build_team_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("team").agg(
        games=("result", "size"),
        wins=("result", lambda s: (s == "W").sum()),
        avg_pace=("game_pace", "mean"),
    ).reset_index()
    summary["win_rate"] = summary["wins"] / summary["games"]
    return summary


def plot(summary: pd.DataFrame, out_path: str):
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.scatterplot(data=summary, x="avg_pace", y="win_rate", s=110,
                     color="#264653", ax=ax, zorder=3)

    for _, row in summary.iterrows():
        ax.annotate(team_alias(row["team"]), (row["avg_pace"], row["win_rate"]),
                    xytext=(6, 6), textcoords="offset points", fontsize=9,
                    ha="left", va="bottom")

    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Pace medio vs win rate — Serie A1 2025/26 (regular season)")
    ax.set_xlabel("Pace medio stagionale (possessi stimati / 40')")
    ax.set_ylabel("Win rate")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main(master_csv: str, out_path: str):
    df = pd.read_csv(master_csv)
    summary = build_team_summary(df)
    plot(summary, out_path)
    print(summary.sort_values("win_rate", ascending=False).to_string(index=False))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    master_csv = sys.argv[1] if len(sys.argv) > 1 else "data/pace_A1_2025-26_all_teams.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "data/summary/pace_vs_winrate.png"
    main(master_csv, out_path)
