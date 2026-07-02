"""Bar chart: pace of the 3 games of the Serie A1 2025/26 final (Schio vs
Venezia), with each team's regular-season average pace as a reference line.
"""

import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from plot_pace import team_alias

SCHIO = "Famila Wuber Schio"
VENEZIA = "Umana Reyer Venezia"


def plot(finals: pd.DataFrame, season_avg: dict, out_path: str):
    sns.set_theme(style="whitegrid", font_scale=1.25)
    fig, ax = plt.subplots(figsize=(8, 5.5))

    ylo, yhi = 55, 78

    labels = [f"Gara {g}" for g in finals["gara"]]
    bars = ax.bar(labels, finals["game_pace"] - ylo, bottom=ylo, color="#264653",
                  width=0.5, zorder=3)

    for bar, (_, row) in zip(bars, finals.iterrows()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_y() + 0.3,
                f"{row['game_pace']:.1f}", ha="center", va="bottom", fontsize=11, zorder=4)
        score = f"{row['home_score']}-{row['away_score']}"
        winner_alias = team_alias(row["winner"])
        ax.text(bar.get_x() + bar.get_width() / 2, ylo + 0.4,
                f"{score}\n{winner_alias} vince", ha="center", va="bottom",
                fontsize=9, color="white", zorder=4)

    ax.axhline(season_avg[SCHIO], color="#e76f51", linestyle="--", linewidth=1.3,
               label=f"media stagionale Schio: {season_avg[SCHIO]:.1f}", zorder=2)
    ax.axhline(season_avg[VENEZIA], color="#2a9d8f", linestyle="--", linewidth=1.3,
               label=f"media stagionale Venezia: {season_avg[VENEZIA]:.1f}", zorder=2)

    ax.set_ylim(ylo, yhi)
    ax.set_title("Pace nella finale scudetto — Famila Wuber Schio vs Umana Reyer Venezia")
    ax.set_ylabel("Pace di partita (possessi stimati / 40')")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(finals_csv: str, master_csv: str, out_path: str):
    finals = pd.read_csv(finals_csv)
    master = pd.read_csv(master_csv)
    season_avg = master.groupby("team")["game_pace"].mean().to_dict()
    plot(finals, season_avg, out_path)
    print(finals[["gara", "date", "home_team", "home_score", "away_score", "away_team", "game_pace"]]
          .to_string(index=False))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    finals_csv = sys.argv[1] if len(sys.argv) > 1 else "data/finals/finals_pace.csv"
    master_csv = sys.argv[2] if len(sys.argv) > 2 else "data/pace_A1_2025-26_all_teams.csv"
    out_path = sys.argv[3] if len(sys.argv) > 3 else "data/finals/pace_finali.png"
    main(finals_csv, master_csv, out_path)
