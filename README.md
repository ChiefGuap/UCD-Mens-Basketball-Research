# UC Davis Men's Basketball — FIBA U19 & U20 International Scouting Pipeline

Automated web scraping and advanced analytics pipeline for FIBA U19 and U20 international basketball tournaments across the past three years (2021–2024). Designed for the UC Davis Men's Basketball coaching and analytics staff for international talent evaluation, transfer/recruiting scouting, and efficiency benchmarking.

---

## 🏀 Tournaments Covered

- **FIBA U20 EuroBasket (Division A)**: 2024, 2023, 2022
- **FIBA U20 EuroBasket (Division B)**: 2024, 2023, 2022
- **FIBA U19 Basketball World Cup**: 2023, 2021

Unlike the basic qualifying leaderboard on the FIBA website (which caps at 50 players meeting a >50% games played threshold), this pipeline extracts **100% of participating players across every competing national team roster**.

---

## 📂 Project Structure

```
.
├── run_pipeline.py           # Main end-to-end execution script
├── requirements.txt          # Python dependencies
├── src/
│   ├── config.py             # Tournament mapping, headers, URLs, and paths
│   ├── scraper.py            # FIBA RSC payload fetcher with caching & rate-limiting
│   ├── parser.py             # JSON extractor for player bios & box score totals
│   └── metrics.py            # NCAA scouting analytics (eFG%, TS%, AST/TO, Per-36)
├── data/
│   ├── raw/                  # Cached RSC & HTML payloads (idempotent scraping)
│   └── processed/
│       ├── fiba_u19_u20_all_players.csv   # Unified master CSV dataset
│       └── fiba_scouting.db               # Indexed SQLite database
└── reports/
    └── ucd_scouting_report.md             # Top prospects leaderboard by category
```

---

## 🚀 Quickstart

### 1. Installation

Ensure you have Python 3.9+ installed, then install requirements:

```bash
pip install -r requirements.txt
```

### 2. Run the Full Scraping & Analytics Pipeline

```bash
python3 run_pipeline.py
```

The script will:
1. Discover all competing national teams per tournament.
2. Fetch and parse each team's full roster and tournament statistics.
3. Cache all responses in `data/raw/` so repeat runs complete instantly without extra network requests.
4. Calculate advanced metrics:
   - **Effective Field Goal Percentage (eFG%)**
   - **True Shooting Percentage (TS%)**
   - **Assist-to-Turnover Ratio (AST/TO)**
   - **Per-36 Minutes Projections** (`per36_pts`, `per36_reb`, `per36_ast`, `per36_stl`, `per36_blk`)
   - **Approximate Age During Competition**
5. Save the unified dataset to `data/processed/fiba_u19_u20_all_players.csv` and an indexed SQLite database `data/processed/fiba_scouting.db`.
6. Output a scouting summary report to `reports/ucd_scouting_report.md`.

---

## 🔍 Example SQL Queries

You can query `data/processed/fiba_scouting.db` with any SQLite client, Python, or R:

### Find Top European 3-Point Shooters (6'6"+, 38%+ 3PT)
```sql
SELECT full_name, nationality, position, height_ft_in, tournament_name, 
       total_three_pm, total_three_pa, three_p_pct, points_per_game
FROM players_stats
WHERE height_cm >= 198 
  AND total_three_pm >= 8 
  AND three_p_pct >= 38.0
ORDER BY three_p_pct DESC;
```

### High-Efficiency Guards with > 2.0 AST/TO Ratio
```sql
SELECT full_name, nationality, position, tournament_name,
       assists_per_game, turnovers_per_game, ast_to_ratio, ts_pct, efficiency_per_game
FROM players_stats
WHERE games_played >= 4
  AND assists_per_game >= 3.0
  AND ast_to_ratio >= 2.0
ORDER BY efficiency_per_game DESC;
```
