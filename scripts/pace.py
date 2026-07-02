"""Simple pace/possessions formula (Dean Oliver / hackastat.eu simplified version).

Possessions ~= FGA + 0.44 * FTA - OR + TOV
Pace = (possessions / minutes_played) * 40   (40' regulation in Italian basketball,
                                                +5' per overtime period)
Game pace = average of both teams' estimated possessions.
"""

REGULATION_MINUTES = 40
OT_MINUTES = 5


def team_possessions(fga: float, fta: float, oreb: float, tov: float) -> float:
    return fga + 0.44 * fta - oreb + tov


def game_minutes(n_periods: int) -> int:
    """n_periods: how many quarters/periods were played (4 = no OT)."""
    ot_periods = max(0, n_periods - 4)
    return REGULATION_MINUTES + ot_periods * OT_MINUTES


def game_pace(fga_home, fta_home, oreb_home, tov_home,
              fga_away, fta_away, oreb_away, tov_away,
              n_periods: int = 4) -> dict:
    poss_home = team_possessions(fga_home, fta_home, oreb_home, tov_home)
    poss_away = team_possessions(fga_away, fta_away, oreb_away, tov_away)
    minutes = game_minutes(n_periods)
    avg_poss = (poss_home + poss_away) / 2
    pace = (avg_poss / minutes) * 40
    return {
        "possessions_home": poss_home,
        "possessions_away": poss_away,
        "possessions_avg": avg_poss,
        "minutes": minutes,
        "pace": pace,
    }


def result(score_team: int, score_opp: int) -> str:
    return "W" if score_team > score_opp else "L"
