"""Scatter: how much the game's pace (single shared value, see game_pace in
scripts/pace.py) deviated from each side's OWN average pace, one point per
regular-season game, colored by W/L.

x = game_pace - team_avg_pace
y = game_pace - opp_avg_pace
Each side's deviation is measured against its own season-average game_pace,
so the origin (0,0) means "both sides played exactly at their usual pace".
x and y differ only because the two baselines (team_avg vs opp_avg) differ,
not because the game itself had two different paces.

Marker size is proportional to the final-score margin of that game.
"""

import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from plot_pace import slugify, team_alias

# Fixed, shared across all teams: computed from the global min/max deviation
# (-9.2 / +9.2 across the whole dataset), plus a bit of padding.
DEV_RANGE = (-10, 10)

# Fixed, shared across all teams: global min/max final-score margin
# (2 / 60 across the whole dataset), mapped to marker area.
MARGIN_RANGE = (2, 60)
MARKER_SIZE_RANGE = (40, 400)

WIN_LOSS_PALETTE = {"W": "green", "L": "red"}

FINALISTS = ["Famila Wuber Schio", "Umana Reyer Venezia"]


def plot_team_pace_deviation(df_team: pd.DataFrame, out_path: str, team_label: str,
                              team_avg_lookup: dict):
    alias = team_alias(team_label)
    team_avg = team_avg_lookup[team_label]

    df_team = df_team.copy()
    df_team["team_dev"] = df_team["game_pace"] - team_avg
    df_team["opp_dev"] = df_team["game_pace"] - df_team["opponent"].map(team_avg_lookup)
    df_team["margin"] = (df_team["team_score"] - df_team["opp_score"]).abs()

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6.5, 6.5))

    lo, hi = DEV_RANGE

    ax.axhline(0, color="black", linestyle=":", linewidth=1, alpha=0.5)
    ax.axvline(0, color="black", linestyle=":", linewidth=1, alpha=0.5)

    edge_pad = (hi - lo) * 0.03
    ax.text(0, hi - edge_pad, "Loro corrono\ndi più", color="#1f4ea1", alpha=0.45,
             fontsize=14, ha="center", va="top", zorder=1)
    ax.text(0, lo + edge_pad, "Loro corrono\ndi meno", color="#1f4ea1", alpha=0.45,
             fontsize=14, ha="center", va="bottom", zorder=1)
    ax.text(lo + edge_pad, 0, "Noi corriamo\ndi meno", color="#1f4ea1", alpha=0.45,
             fontsize=14, ha="left", va="center", ma="center", zorder=1)
    ax.text(hi - edge_pad, 0, "Noi corriamo\ndi più", color="#1f4ea1", alpha=0.45,
             fontsize=14, ha="right", va="center", ma="center", zorder=1)

    sns.scatterplot(data=df_team, x="team_dev", y="opp_dev", hue="result",
                     hue_order=["W", "L"], palette=WIN_LOSS_PALETTE,
                     size="margin", sizes=MARKER_SIZE_RANGE, size_norm=MARGIN_RANGE,
                     ax=ax, zorder=3)

    for _, row in df_team[df_team["opponent"].isin(FINALISTS)].iterrows():
        ax.annotate(team_alias(row["opponent"]), (row["team_dev"], row["opp_dev"]),
                    xytext=(2, 2), textcoords="offset points", fontsize=9,
                    color="black", ha="left", va="bottom", zorder=4)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_title(f"Scostamento pace dalla propria media — {alias}\n(regular season)")
    ax.set_xlabel(f"Pace {alias} − media {alias} ({team_avg:.1f})")
    ax.set_ylabel("Pace avversaria − media avversaria")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main(master_csv: str, team_query: str, out_path: str):
    df = pd.read_csv(master_csv)
    team_avg_lookup = df.groupby("team")["game_pace"].mean().to_dict()
    df_team = df[df["team"].str.contains(team_query, case=False)]
    if df_team.empty:
        raise ValueError(f"No rows found for team matching {team_query!r}")
    team_label = df_team["team"].iloc[0]
    plot_team_pace_deviation(df_team, out_path, team_label, team_avg_lookup)
    print(f"{team_label}: {len(df_team)} partite -> {out_path}")


def main_all(master_csv: str, out_dir: str = "data/pace_deviation"):
    df = pd.read_csv(master_csv)
    team_avg_lookup = df.groupby("team")["game_pace"].mean().to_dict()
    for team in sorted(df["team"].unique()):
        df_team = df[df["team"] == team]
        out_path = f"{out_dir}/pace_deviation_{slugify(team_alias(team))}.png"
        plot_team_pace_deviation(df_team, out_path, team, team_avg_lookup)
        print(f"{team}: {len(df_team)} partite -> {out_path}")


if __name__ == "__main__":
    master_csv = sys.argv[1] if len(sys.argv) > 1 else "data/pace_A1_2025-26_all_teams.csv"
    if len(sys.argv) > 2 and sys.argv[2] != "--all":
        team_query = sys.argv[2]
        out_path = sys.argv[3] if len(sys.argv) > 3 else f"data/pace_deviation/pace_deviation_{slugify(team_query)}.png"
        main(master_csv, team_query, out_path)
    else:
        main_all(master_csv)
