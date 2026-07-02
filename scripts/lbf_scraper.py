"""Scrape legabasketfemminile.it (Serie A1, competition ID=313) and compute
pace + W/L per game for a chosen team across the season.
"""

import re
import time
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd

from pace import team_possessions, game_minutes, result

HEADERS = {"User-Agent": "Mozilla/5.0 (research script - pace analysis)"}
BASE = "https://www.legabasketfemminile.it/"
COMPETITION_ID = 313

# TOTALI DI SQUADRA row column layout (0-indexed, after the 'TOTALI DI SQUADRA' label cell):
# 0:'' 1:'' 2:FALLI_C 3:FALLI_S 4:T2_R 5:T2_T 6:T2_% 7:T3_R 8:T3_T 9:T3_% 10:TL_R 11:TL_T 12:TL_%
# 13:RIMB_O 14:RIMB_D 15:RIMB_TOT 16:STOP_D 17:STOP_S 18:PALLE_P 19:PALLE_R 20:AS 21:VAL 22:OER
COL = {
    "t2_att": 5, "t3_att": 8, "tl_att": 11, "reb_off": 13, "palle_perse": 18,
}


def get_calendar_match_ids(competition_id: int) -> list[int]:
    r = requests.get(f"{BASE}Calendar.aspx?ID={competition_id}", headers=HEADERS, timeout=20)
    r.raise_for_status()
    mids = sorted(set(int(m) for m in re.findall(
        rf"MatchStats\.aspx\?ID={competition_id}&amp;MID=(\d+)", r.text)))
    return mids


def parse_team_totals(table) -> dict:
    rows = table.find_all("tr")
    team_name = rows[0].find_all(["td", "th"])[0].get_text(strip=True)
    totals_row = None
    for tr in rows:
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if cells and cells[0] == "TOTALI DI SQUADRA":
            totals_row = cells[1:]  # drop label
            break
    if totals_row is None:
        raise ValueError(f"TOTALI DI SQUADRA row not found for {team_name}")

    def num(idx, default=0.0):
        try:
            return float(totals_row[idx].replace(",", "."))
        except (IndexError, ValueError):
            return default

    return {
        "team": team_name,
        "fga": num(COL["t2_att"]) + num(COL["t3_att"]),
        "fta": num(COL["tl_att"]),
        "oreb": num(COL["reb_off"]),
        "tov": num(COL["palle_perse"]),
    }


def get_match_boxscore(competition_id: int, match_id: int) -> dict:
    url = f"{BASE}MatchStats.aspx?ID={competition_id}&MID={match_id}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    home_team = soup.find(id="Content_L_Squadre_Casa").get_text(strip=True)
    home_city = soup.find(id="Content_L_Citta_Casa").get_text(strip=True)
    away_team = soup.find(id="Content_L_Squadre_Fuori").get_text(strip=True)
    away_city = soup.find(id="Content_L_Citta_Fuori").get_text(strip=True)
    home_score = int(soup.find(id="Content_L_Punteggio_Casa").get_text(strip=True))
    away_score = int(soup.find(id="Content_L_Punteggio_Fuori").get_text(strip=True))
    quarti = soup.find(id="Content_L_Quarti").get_text(strip=True)
    n_periods = len(quarti.split(","))

    date = soup.find(id="Content_LB_DataGara").get_text(strip=True)
    giornata_text = soup.select_one(".page-header h1").get_text(strip=True)
    giornata_match = re.search(r"(\d+)", giornata_text)
    giornata = int(giornata_match.group(1)) if giornata_match else None

    tables = [t for t in soup.find_all("table") if "TOTALI DI SQUADRA" in t.get_text()]
    if len(tables) != 2:
        raise ValueError(f"Expected 2 team tables, found {len(tables)} for MID={match_id}")

    home_stats = parse_team_totals(tables[0])
    away_stats = parse_team_totals(tables[1])

    return {
        "match_id": match_id,
        "date": date,
        "giornata": giornata,
        "home_team": f"{home_team} {home_city}".strip(),
        "away_team": f"{away_team} {away_city}".strip(),
        "home_score": home_score,
        "away_score": away_score,
        "n_periods": n_periods,
        "home_fga": home_stats["fga"], "home_fta": home_stats["fta"],
        "home_oreb": home_stats["oreb"], "home_tov": home_stats["tov"],
        "away_fga": away_stats["fga"], "away_fta": away_stats["fta"],
        "away_oreb": away_stats["oreb"], "away_tov": away_stats["tov"],
    }


def build_full_season_dataset(competition_id: int, rate_limit_s: float = 1.0) -> pd.DataFrame:
    """One row per (match, team-perspective): 2 rows per match, own pace + opponent's pace."""
    mids = get_calendar_match_ids(competition_id)
    print(f"Found {len(mids)} matches in competition {competition_id}", file=sys.stderr)

    rows = []
    for mid in mids:
        try:
            box = get_match_boxscore(competition_id, mid)
        except Exception as e:
            print(f"  MID={mid}: skipped ({e})", file=sys.stderr)
            time.sleep(rate_limit_s)
            continue

        minutes = game_minutes(box["n_periods"])
        home_poss = team_possessions(box["home_fga"], box["home_fta"], box["home_oreb"], box["home_tov"])
        away_poss = team_possessions(box["away_fga"], box["away_fta"], box["away_oreb"], box["away_tov"])
        home_pace = round(home_poss / minutes * 40, 1)
        away_pace = round(away_poss / minutes * 40, 1)
        game_pace_avg = round((home_pace + away_pace) / 2, 1)

        for is_home in (True, False):
            team = box["home_team"] if is_home else box["away_team"]
            opponent = box["away_team"] if is_home else box["home_team"]
            team_score = box["home_score"] if is_home else box["away_score"]
            opp_score = box["away_score"] if is_home else box["home_score"]
            team_pace = home_pace if is_home else away_pace
            opp_pace = away_pace if is_home else home_pace

            rows.append({
                "match_id": mid,
                "date": box["date"],
                "giornata": box["giornata"],
                "team": team,
                "opponent": opponent,
                "is_home": is_home,
                "team_score": team_score,
                "opp_score": opp_score,
                "result": result(team_score, opp_score),
                "n_periods": box["n_periods"],
                "team_pace": team_pace,
                "opp_pace": opp_pace,
                "game_pace": game_pace_avg,
            })

        print(f"  MID={mid} (g.{box['giornata']}, {box['date']}): {box['home_team']} {box['home_score']}-"
              f"{box['away_score']} {box['away_team']} -> game_pace={game_pace_avg:.1f}", file=sys.stderr)
        time.sleep(rate_limit_s)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "data/pace_A1_2025-26_all_teams.csv"
    df = build_full_season_dataset(COMPETITION_ID)
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} rows ({df['match_id'].nunique()} matches, {df['team'].nunique()} teams) to {out_path}")
