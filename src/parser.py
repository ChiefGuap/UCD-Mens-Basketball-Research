"""
Parser module for extracting, normalizing, and calculating metrics
from FIBA team RSC payloads.
"""

import json
import re
from typing import List, Dict, Any
from .metrics import compute_advanced_metrics


class FIBAParser:
    @staticmethod
    def parse_team_rsc(rsc_text: str, tournament: Dict[str, Any], team_slug: str) -> List[Dict[str, Any]]:
        """
        Extracts all player records from a team's RSC response string.
        Merges biographical metadata with tournament statistical totals and per-game averages.
        """
        raw_players = {}

        # 1. Extract statistical totals & per-game objects
        # These objects have "playerId" and "pointsPerGame"
        for m in re.finditer(r'\{[^{}]*\"playerId\":\s*(\d+)[^{}]*\"pointsPerGame\":[^{}]*\}', rsc_text):
            raw = m.group(0)
            try:
                d = json.loads(raw)
                pid = d["playerId"]
                if pid not in raw_players:
                    raw_players[pid] = {}
                raw_players[pid].update(d)
            except Exception:
                pass

        # 2. Extract bio/positionCode objects
        for m in re.finditer(r'\{[^{}]*\"playerId\":\s*(\d+)[^{}]*\"positionCode\":[^{}]*\}', rsc_text):
            raw = m.group(0)
            try:
                d = json.loads(raw)
                pid = d["playerId"]
                if pid not in raw_players:
                    raw_players[pid] = {}
                raw_players[pid].update(d)
            except Exception:
                pass

        # 3. Extract personId objects (contains height, detailed position, club)
        for m in re.finditer(r'\{[^{}]*\"personId\":\s*(\d+)[^{}]*\}', rsc_text):
            raw = m.group(0)
            try:
                d = json.loads(raw)
                pid = d["personId"]
                if pid in raw_players:
                    raw_players[pid].update(d)
                else:
                    raw_players[pid] = d
            except Exception:
                pass

        normalized_records = []
        for pid, raw in raw_players.items():
            # If the record has no games played or no player name, skip
            first_name = (raw.get("firstName") or "").strip()
            last_name = (raw.get("lastName") or "").strip()
            if not first_name and not last_name:
                continue

            full_name = f"{first_name} {last_name}".strip()

            # Minutes conversion from seconds
            play_time_sec = raw.get("totalPlayTimeInSeconds")
            tot_min = round(play_time_sec / 60.0, 1) if play_time_sec is not None else None

            mpg_sec = raw.get("playTimeInSecondsPerGame")
            mpg = round(mpg_sec / 60.0, 1) if mpg_sec is not None else None

            # Position normalization
            pos = raw.get("position") or raw.get("positionCode") or "N/A"

            # Height
            height_cm = raw.get("heightInCm")
            height_ft_in = raw.get("heightInFeetInches")

            record = {
                # Tournament info
                "tournament_id": tournament["id"],
                "tournament_name": tournament["name"],
                "tournament_year": tournament["year"],
                "age_category": tournament["age_category"],
                "division": tournament["division"],
                "tournament_type": tournament["tournament_type"],
                
                # Team & Player identity
                "team_slug": team_slug,
                "team_id": raw.get("teamId"),
                "player_id": pid,
                "full_name": full_name,
                "first_name": first_name,
                "last_name": last_name,
                "uniform_number": raw.get("uniformNumber"),
                "position": pos,
                "nationality": raw.get("nationality") or raw.get("countryFIBACode"),
                "club_name": raw.get("clubName"),
                "date_of_birth": raw.get("dateOfBirth"),
                "height_cm": height_cm,
                "height_ft_in": height_ft_in,
                "is_captain": raw.get("isCaptain", False),

                # Games & Record
                "games_played": raw.get("totalGamesPlayed") or raw.get("gamesPlayed", 0),
                "games_won": raw.get("totalGamesWon"),
                "games_lost": raw.get("totalGamesLost"),

                # Box Score Totals
                "total_minutes": tot_min,
                "total_points": raw.get("totalPoints", 0),
                "total_rebounds": raw.get("totalRebounds", 0),
                "total_offensive_rebounds": raw.get("totalReboundsOffensive", 0),
                "total_defensive_rebounds": raw.get("totalReboundsDefensive", 0),
                "total_assists": raw.get("totalAssists", 0),
                "total_steals": raw.get("totalSteals", 0),
                "total_blocks": raw.get("totalBlocks", 0),
                "total_turnovers": raw.get("totalTurnovers", 0),
                "total_fouls": raw.get("totalFouls", 0),
                "total_plus_minus": raw.get("totalPlusMinus", 0),
                "total_efficiency": raw.get("totalEfficiency", 0),

                # Shooting Totals
                "total_fgm": raw.get("totalFieldGoalsMade", 0),
                "total_fga": raw.get("totalFieldGoalsAttempted", 0),
                "fg_pct": round(raw.get("fieldGoalsPercentage") or 0.0, 1),
                "total_two_pm": raw.get("totalTwoPointsMade", 0),
                "total_two_pa": raw.get("totalTwoPointsAttempted", 0),
                "two_p_pct": round(raw.get("twoPointsPercentage") or 0.0, 1),
                "total_three_pm": raw.get("totalThreePointsMade", 0),
                "total_three_pa": raw.get("totalThreePointsAttempted", 0),
                "three_p_pct": round(raw.get("threePointsPercentage") or 0.0, 1),
                "total_ftm": raw.get("totalFreeThrowsMade", 0),
                "total_fta": raw.get("totalFreeThrowsAttempted", 0),
                "ft_pct": round(raw.get("freeThrowsPercentage") or 0.0, 1),

                # Per Game Averages
                "minutes_per_game": mpg,
                "points_per_game": raw.get("pointsPerGame"),
                "rebounds_per_game": raw.get("reboundsPerGame"),
                "offensive_rebounds_per_game": raw.get("reboundsOffensivePerGame"),
                "defensive_rebounds_per_game": raw.get("reboundsDefensivePerGame"),
                "assists_per_game": raw.get("assistsPerGame"),
                "steals_per_game": raw.get("stealsPerGame"),
                "blocks_per_game": raw.get("blocksPerGame"),
                "turnovers_per_game": raw.get("turnoversPerGame"),
                "fouls_per_game": raw.get("foulsPerGame"),
                "plus_minus_per_game": raw.get("plusMinusPerGame"),
                "efficiency_per_game": raw.get("efficiencyPerGame"),

                # Double / Triple doubles
                "double_doubles": raw.get("totalDoubleDoubles", 0),
                "triple_doubles": raw.get("totalTripleDoubles", 0),
            }

            # Enrich with advanced scouting analytics
            advanced = compute_advanced_metrics(record, tournament["year"])
            record.update(advanced)

            normalized_records.append(record)

        return normalized_records

