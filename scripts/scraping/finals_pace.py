"""Pace for the Serie A1 2025/26 final series (Famila Wuber Schio vs Umana
Reyer Venezia, Gara 1-3). Not part of the regular-season master CSV: the
playoff bracket sits behind an ASP.NET postback (the "Play Off" tab on
Calendar.aspx has no plain querystring), so the match IDs were found once
via Playwright (see scripts/explore_playoff.py) and are hardcoded here.
Reuses the same box-score parsing and pace formula as the main pipeline.
"""

import sys
import pandas as pd

from lbf_scraper import get_match_boxscore
from pace import team_possessions_advanced, game_minutes

COMPETITION_ID = 313
FINAL_MATCH_IDS = {1: 53799, 2: 53800, 3: 53801}


def build_finals_dataset() -> pd.DataFrame:
    rows = []
    for gara, mid in FINAL_MATCH_IDS.items():
        box = get_match_boxscore(COMPETITION_ID, mid)
        minutes = game_minutes(box["n_periods"])
        home_poss = team_possessions_advanced(
            box["home_fga"], box["home_fgm"], box["home_fta"], box["home_oreb"],
            box["away_dreb"], box["home_tov"])
        away_poss = team_possessions_advanced(
            box["away_fga"], box["away_fgm"], box["away_fta"], box["away_oreb"],
            box["home_dreb"], box["away_tov"])
        home_pace = round(home_poss / minutes * 40, 1)
        away_pace = round(away_poss / minutes * 40, 1)
        game_pace = round((home_pace + away_pace) / 2, 1)
        winner = box["home_team"] if box["home_score"] > box["away_score"] else box["away_team"]

        rows.append({
            "gara": gara, "match_id": mid, "date": box["date"],
            "home_team": box["home_team"], "away_team": box["away_team"],
            "home_score": box["home_score"], "away_score": box["away_score"],
            "winner": winner, "n_periods": box["n_periods"], "game_pace": game_pace,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "data/finals/finals_pace.csv"
    df = build_finals_dataset()
    df.to_csv(out_path, index=False)
    print(df.to_string(index=False))
    print(f"\nSaved to {out_path}")
