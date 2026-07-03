"""Pace/possessions formulas (Dean Oliver / hackastat.eu).

Simple:   Possessions ~= FGA + 0.44*FTA - OR + TOV
Advanced: Possessions ~= FGA + 0.44*FTA - 1.07*(OR/(OR+oppDR))*(FGA-FGM) + TOV
Pace = (possessions / minutes_played) * 40   (40' regulation in Italian basketball,
                                                +5' per overtime period)
"""

REGULATION_MINUTES = 40
OT_MINUTES = 5


def team_possessions_simple(fga: float, fta: float, oreb: float, tov: float) -> float:
    return fga + 0.44 * fta - oreb + tov


def team_possessions_advanced(fga: float, fgm: float, fta: float, oreb: float,
                               opp_dreb: float, tov: float) -> float:
    reb_denom = oreb + opp_dreb
    reb_factor = (oreb / reb_denom) if reb_denom else 0.0
    return fga + 0.44 * fta - 1.07 * reb_factor * (fga - fgm) + tov


def game_minutes(n_periods: int) -> int:
    """n_periods: how many quarters/periods were played (4 = no OT)."""
    ot_periods = max(0, n_periods - 4)
    return REGULATION_MINUTES + ot_periods * OT_MINUTES


def result(score_team: int, score_opp: int) -> str:
    return "W" if score_team > score_opp else "L"
