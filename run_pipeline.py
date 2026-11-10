#!/usr/bin/env python3
"""
Main execution pipeline for UC Davis Men's Basketball FIBA Scouting Extraction.
Extracts player stats across U19 and U20 competitions from 2021 to 2024.
"""

import sqlite3
from pathlib import Path
import pandas as pd

from src.config import TOURNAMENTS, PROCESSED_DATA_DIR, REPORTS_DIR
from src.scraper import FIBAScraper
from src.parser import FIBAParser


def save_to_sqlite(df: pd.DataFrame, db_path: Path):
    """Saves DataFrame into an indexed SQLite database."""
    conn = sqlite3.connect(db_path)
    df.to_sql("players_stats", conn, if_exists="replace", index=False)

    # Create helpful indexes for quick scouting queries
    with conn:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_player_name ON players_stats(full_name);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tournament ON players_stats(tournament_id);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_position ON players_stats(position);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nationality ON players_stats(nationality);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_eff ON players_stats(efficiency_per_game);")
    conn.close()
    print(f"✅ Saved SQLite database to {db_path}")


def df_to_markdown(df: pd.DataFrame) -> str:
    """Converts a pandas DataFrame into a GitHub Flavored Markdown table without external dependencies."""
    headers = [str(c) for c in df.columns]
    col_widths = [max(len(h), *(len(str(val)) for val in df[c])) for h, c in zip(headers, df.columns)]
    
    header_row = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |"
    separator_row = "| " + " | ".join("-" * w for w in col_widths) + " |"
    
    data_rows = []
    for _, row in df.iterrows():
        data_rows.append("| " + " | ".join(str(val if pd.notnull(val) else "-").ljust(w) for val, w in zip(row, col_widths)) + " |")
        
    return "\n".join([header_row, separator_row] + data_rows)


def generate_scouting_report(df: pd.DataFrame, report_path: Path):
    """
    Generates an executive markdown scouting report highlighting top prospects
    for UC Davis coaching and analytics staff.
    """
    report_lines = [
        "# UC Davis Men's Basketball — FIBA International Scouting Leaderboards",
        "",
        f"**Dataset Overview:** {len(df)} total player-tournament records extracted across {df['tournament_id'].nunique()} competitions.",
        "",
        "---",
        "",
        "## 1. Top Scoring Threats (Min. 4 GP, Sorted by PPG)",
        "",
    ]

    # Top scorers
    scorers = df[(df["games_played"] >= 4) & (df["points_per_game"].notnull())].sort_values(
        by="points_per_game", ascending=False
    ).head(10)
    scorer_cols = ["full_name", "nationality", "position", "tournament_name", "games_played", "points_per_game", "ts_pct", "efg_pct"]
    scorers_table = scorers[scorer_cols].rename(columns={
        "full_name": "Player",
        "nationality": "Country",
        "position": "Pos",
        "tournament_name": "Tournament",
        "games_played": "GP",
        "points_per_game": "PPG",
        "ts_pct": "TS%",
        "efg_pct": "eFG%",
    })
    report_lines.append(df_to_markdown(scorers_table))
    report_lines.extend(["", "---", "", "## 2. Elite Perimeter Shooters (Min. 1.5 3PM/G, Sorted by 3P%)", ""])

    # Top shooters
    shooters = df[
        (df["games_played"] >= 4) &
        (df["total_three_pm"] >= 8) &
        (df["three_p_pct"].notnull())
    ].sort_values(by="three_p_pct", ascending=False).head(10)
    shooter_cols = ["full_name", "nationality", "position", "tournament_name", "games_played", "total_three_pm", "total_three_pa", "three_p_pct"]
    shooters_table = shooters[shooter_cols].rename(columns={
        "full_name": "Player",
        "nationality": "Country",
        "position": "Pos",
        "tournament_name": "Tournament",
        "games_played": "GP",
        "total_three_pm": "3PM",
        "total_three_pa": "3PA",
        "three_p_pct": "3P%",
    })
    report_lines.append(df_to_markdown(shooters_table))
    report_lines.extend(["", "---", "", "## 3. Floor Generals & Playmakers (Min. 3.0 APG, Sorted by AST/TO)", ""])

    # Playmakers
    playmakers = df[
        (df["games_played"] >= 4) &
        (df["assists_per_game"] >= 3.0) &
        (df["ast_to_ratio"].notnull())
    ].sort_values(by="ast_to_ratio", ascending=False).head(10)
    playmaker_cols = ["full_name", "nationality", "position", "tournament_name", "games_played", "assists_per_game", "total_assists", "total_turnovers", "ast_to_ratio"]
    playmakers_table = playmakers[playmaker_cols].rename(columns={
        "full_name": "Player",
        "nationality": "Country",
        "position": "Pos",
        "tournament_name": "Tournament",
        "games_played": "GP",
        "assists_per_game": "APG",
        "total_assists": "AST",
        "total_turnovers": "TO",
        "ast_to_ratio": "AST/TO",
    })
    report_lines.append(df_to_markdown(playmakers_table))
    report_lines.extend(["", "---", "", "## 4. Dominant Rebounders & Interior Presence (Sorted by RPG)", ""])

    # Rebounders
    rebounders = df[
        (df["games_played"] >= 4) &
        (df["rebounds_per_game"].notnull())
    ].sort_values(by="rebounds_per_game", ascending=False).head(10)
    rebounder_cols = ["full_name", "nationality", "position", "tournament_name", "games_played", "rebounds_per_game", "total_offensive_rebounds", "total_defensive_rebounds", "blocks_per_game"]
    rebounders_table = rebounders[rebounder_cols].rename(columns={
        "full_name": "Player",
        "nationality": "Country",
        "position": "Pos",
        "tournament_name": "Tournament",
        "games_played": "GP",
        "rebounds_per_game": "RPG",
        "total_offensive_rebounds": "OREB",
        "total_defensive_rebounds": "DREB",
        "blocks_per_game": "BPG",
    })
    report_lines.append(df_to_markdown(rebounders_table))
    report_lines.extend(["", "---", "", "## 5. Most Efficient Overall Performers (Sorted by Efficiency / Game)", ""])

    # Efficiency
    efficient = df[
        (df["games_played"] >= 4) &
        (df["efficiency_per_game"].notnull())
    ].sort_values(by="efficiency_per_game", ascending=False).head(10)
    eff_cols = ["full_name", "nationality", "position", "tournament_name", "games_played", "points_per_game", "rebounds_per_game", "assists_per_game", "efficiency_per_game"]
    eff_table = efficient[eff_cols].rename(columns={
        "full_name": "Player",
        "nationality": "Country",
        "position": "Pos",
        "tournament_name": "Tournament",
        "games_played": "GP",
        "points_per_game": "PPG",
        "rebounds_per_game": "RPG",
        "assists_per_game": "APG",
        "efficiency_per_game": "EFF",
    })
    report_lines.append(df_to_markdown(eff_table))

    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"✅ Generated scouting report at {report_path}")


def main():
    print("=" * 70)
    print("🏀 UC DAVIS MEN'S BASKETBALL — FIBA U19/U20 SCOUTING SCRAPER")
    print("=" * 70)

    scraper = FIBAScraper()
    all_player_records = []

    for t_idx, tournament in enumerate(TOURNAMENTS, 1):
        print(f"\n[{t_idx}/{len(TOURNAMENTS)}] Processing: {tournament['name']} ({tournament['age_category']}, {tournament['year']})")
        team_slugs = scraper.get_team_slugs(tournament)

        tournament_player_count = 0
        for team_slug in team_slugs:
            try:
                rsc_payload = scraper.get_team_rsc_payload(tournament, team_slug)
                players = FIBAParser.parse_team_rsc(rsc_payload, tournament, team_slug)
                all_player_records.extend(players)
                tournament_player_count += len(players)
            except Exception as e:
                print(f"    ⚠️ Error parsing team {team_slug}: {e}")

        print(f"  -> Extracted {tournament_player_count} players from {tournament['name']}")

    if not all_player_records:
        print("❌ No player records were extracted. Please check network connectivity.")
        return

    df = pd.DataFrame(all_player_records)
    print(f"\n📊 Extraction Complete! Total player-tournament rows: {len(df)}")
    print(f"Unique players: {df['full_name'].nunique()}")

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Save to CSV
    csv_path = PROCESSED_DATA_DIR / "fiba_u19_u20_all_players.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved CSV to {csv_path}")

    # 2. Save to Parquet (if pyarrow / fastparquet installed)
    try:
        parquet_path = PROCESSED_DATA_DIR / "fiba_u19_u20_all_players.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"✅ Saved Parquet to {parquet_path}")
    except Exception as e:
        print(f"ℹ️ Parquet export skipped (optional): {e}")

    # 3. Save to SQLite database
    db_path = PROCESSED_DATA_DIR / "fiba_scouting.db"
    save_to_sqlite(df, db_path)

    # 4. Generate Scouting Report
    report_path = REPORTS_DIR / "ucd_scouting_report.md"
    generate_scouting_report(df, report_path)

    print("\n🏁 All pipeline steps completed successfully!")


if __name__ == "__main__":
    main()

