"""Simple horizontal bar chart: average pace per team, sorted descending,
value annotated on each bar.
"""

import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from plot_pace import team_alias


def build_team_avg_pace(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("team")["team_pace"].mean().reset_index(name="avg_pace")
    summary["alias"] = summary["team"].apply(team_alias)
    return summary.sort_values("avg_pace", ascending=False).reset_index(drop=True)


def plot(summary: pd.DataFrame, out_path: str):
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 6))

    order = summary.iloc[::-1]  # highest pace at the top of a barh chart
    bars = ax.barh(order["alias"], order["avg_pace"], color="#264653")

    for bar, value in zip(bars, order["avg_pace"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{value:.1f}", va="center", ha="left", fontsize=10)

    ax.set_xlim(60, 80)
    ax.set_title("Pace medio per squadra — Serie A1 2025/26 (regular season)")
    ax.set_xlabel("Pace medio stagionale (possessi stimati / 40')")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main(master_csv: str, out_path: str):
    df = pd.read_csv(master_csv)
    summary = build_team_avg_pace(df)
    plot(summary, out_path)
    print(summary[["alias", "avg_pace"]].to_string(index=False))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    master_csv = sys.argv[1] if len(sys.argv) > 1 else "data/pace_A1_2025-26_all_teams.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "data/summary/pace_bar.png"
    main(master_csv, out_path)
