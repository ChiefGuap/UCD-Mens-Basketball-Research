"""
Advanced basketball metrics and scouting analytics calculations.
"""

from typing import Dict, Any


def compute_advanced_metrics(p: Dict[str, Any], tournament_year: int) -> Dict[str, Any]:
    """
    Computes NCAA scouting and advanced analytics metrics for a player record.
    """
    pts = float(p.get("total_points") or 0)
    fgm = float(p.get("total_fgm") or 0)
    fga = float(p.get("total_fga") or 0)
    three_pm = float(p.get("total_three_pm") or 0)
    three_pa = float(p.get("total_three_pa") or 0)
    ftm = float(p.get("total_ftm") or 0)
    fta = float(p.get("total_fta") or 0)
    ast = float(p.get("total_assists") or 0)
    to = float(p.get("total_turnovers") or 0)
    reb = float(p.get("total_rebounds") or 0)
    stl = float(p.get("total_steals") or 0)
    blk = float(p.get("total_blocks") or 0)
    tot_min = float(p.get("total_minutes") or 0)

    # Effective Field Goal Percentage (eFG%)
    if fga > 0:
        efg_pct = round(((fgm + 0.5 * three_pm) / fga) * 100, 2)
        three_pt_rate = round((three_pa / fga) * 100, 2)
        ft_rate = round((fta / fga) * 100, 2)
    else:
        efg_pct = None
        three_pt_rate = None
        ft_rate = None

    # True Shooting Percentage (TS%)
    ts_denom = 2 * (fga + 0.44 * fta)
    if ts_denom > 0:
        ts_pct = round((pts / ts_denom) * 100, 2)
    else:
        ts_pct = None

    # Assist-to-Turnover Ratio (AST/TO)
    if to > 0:
        ast_to_ratio = round(ast / to, 2)
    elif ast > 0:
        ast_to_ratio = round(ast, 2)
    else:
        ast_to_ratio = None

    # Per-36 Minutes Projections (for bench / low-minute scouting)
    if tot_min >= 15.0:  # Minimum 15 total tournament minutes for stable projection
        factor = 36.0 / tot_min
        per36_pts = round(pts * factor, 1)
        per36_reb = round(reb * factor, 1)
        per36_ast = round(ast * factor, 1)
        per36_stl = round(stl * factor, 1)
        per36_blk = round(blk * factor, 1)
    else:
        per36_pts = None
        per36_reb = None
        per36_ast = None
        per36_stl = None
        per36_blk = None

    # Age during competition year
    dob = p.get("date_of_birth")
    approx_age = None
    if dob and len(str(dob)) >= 4:
        try:
            birth_year = int(str(dob)[:4])
            approx_age = tournament_year - birth_year
        except (ValueError, TypeError):
            approx_age = None

    return {
        "efg_pct": efg_pct,
        "ts_pct": ts_pct,
        "ast_to_ratio": ast_to_ratio,
        "three_pt_rate": three_pt_rate,
        "ft_rate": ft_rate,
        "per36_pts": per36_pts,
        "per36_reb": per36_reb,
        "per36_ast": per36_ast,
        "per36_stl": per36_stl,
        "per36_blk": per36_blk,
        "approx_competition_age": approx_age,
    }

