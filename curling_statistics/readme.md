# Curling Team Stats — README

This README explains how to format your input file, run the scripts (both single-team and all-teams versions), and interpret the statistics and outputs.

---

## Overview
The Curling Team Stats scripts compute comprehensive performance metrics from a dataset of curling games. You can analyze a **single team** or automatically process **all teams** in your dataset.

Outputs include:
- Per-team JSON and CSV files of statistics.
- Combined datasets (`ALL_per_game.csv` and `ALL_team_aggregate.csv`) for all teams, ready for use in Tableau or other analytics tools.

Supported input formats: **CSV**, **Excel (`.xlsx`)**, and **Parquet**.

---

## Input File Format
Each row represents a **single game** for one team. The dataset must include these columns (case-insensitive):

| Column | Description |
|--------|--------------|
| **Season** | Season identifier (e.g., `2024–25` or `2025`). |
| **Date** | Game date (`YYYY-MM-DD`). |
| **Team Name** | Your team’s name (exactly matches the one passed to the script). |
| **Opponent** | Opposing team’s name. |
| **Location** | Venue or club name. |
| **Outcome** | Optional text (e.g., `W 7–4`, `L`, `Win`). Not used in calculations. |
| **Sheet** | Sheet identifier (e.g., `A`, `B`, `3`). |
| **Stone Color** | Stone color used by your team (`Red` or `Yellow`). |
| **Game Type** | `League`, `Playoff`, `Bonspiel`, `Friendly`, etc. |
| **Planned Ends** | Scheduled ends (e.g., `8`, `10`). |
| **Ends Played** | Actual ends played. |
| **End 1 – End 9** | Per-end results (points and hammer info). |

### Per-End Encoding Examples
| Code | Meaning |
|------|----------|
| `+2H` | Scored 2 with hammer. |
| `-1N` | Allowed 1 (opponent scored 1) without hammer. |
| `0H` | Blank end while retaining hammer. |
| `B` / `BH` / `BN` | Blank end (optionally specifying with/without hammer). |
| Empty | End not played or missing. |

---

## Example CSV
```
Season,Date,Team Name,Opponent,Location,Outcome,Sheet,Stone Color,Game Type,Planned Ends,Ends Played,End 1,End 2,End 3,End 4,End 5,End 6,End 7,End 8,End 9
2025,2025-02-01,Smith Rink,Johnson Rink,Denver,W 7-6,A,Red,League,8,8,+2H,-1N,0H,+1H,-2N,+3H,0H,-1N,
2025,2025-02-05,Smith Rink,Adams Rink,Boulder,L 4-5,B,Yellow,Bonspiel,8,6,0H,+2H,-1N,+1H,-2N,+2H,,,
```

---

## Running the Scripts

### 🔹 **Option 1 — Analyze a Single Team**
Use `curling_stats.py` to analyze one team:

```bash
python curling_stats.py games.csv "Smith Rink"
```

Optional flags:
```bash
# Specify season filter
python curling_stats.py games.csv "Smith Rink" --season 2025

# Save outputs
python curling_stats.py games.xlsx "Smith Rink" --out-json smith_stats.json --out-games smith_games.csv
```

This creates per-team summary files containing game-level and aggregate stats.

---

### 🔹 **Option 2 — Analyze All Teams Automatically**
Use `run_all_teams.py` to process **every unique team** found in your dataset.

```bash
python run_all_teams.py
```

By default, this script:
- Reads `games.csv` (can be CSV, Excel, or Parquet)
- Loops through each unique `Team Name`
- Generates outputs in a folder called `team_outputs`
- Builds **consolidated data sources**

#### Environment Variable Configuration
You can customize input, season, and output directory without editing the script:

```bash
CURLING_INPUT=games.xlsx CURLING_SEASON=2025 CURLING_OUTDIR=outputs python run_all_teams.py
```

#### Output Files
| File | Description |
|------|--------------|
| `team_outputs/<Team>_stats.json` | Aggregated statistics per team. |
| `team_outputs/<Team>_per_game.csv` | Per-game results per team. |
| `team_outputs/ALL_per_game.csv` | Consolidated per-game dataset for all teams. |
| `team_outputs/ALL_team_aggregate.csv` | One-row-per-team dataset with flattened KPIs. |

The consolidated outputs are ideal for Tableau dashboards and cross-team analysis.

---

## What Statistics Are Calculated
Each team’s JSON file includes:

### 1️⃣ **Record and Points**
- Wins / Losses / Ties
- Points For / Against / Differential
- Average Points For / Against per game

### 2️⃣ **Hammer Statistics**
- Ends with hammer
- Scoring Ends (with hammer)
- Two-plus Ends (scored 2+ with hammer)
- Blank Ends (with hammer)
- Steals Allowed (opponent scored with your hammer)
- Rates: scoring, two-plus, blank

### 3️⃣ **No-Hammer Statistics**
- Ends without hammer
- Steals For (you scored without hammer)
- Force Rate (opponent held to exactly 1)
- Defense ≤1 Rate (opponent ≤1)

### 4️⃣ **Derived Rates**
- Win %, Hammer Scoring %, Steal %, Force %, and others.

All rates automatically handle divisions by zero and reflect only filtered data (e.g., season filters).

---

## Consolidated Dataset Columns
### `ALL_team_aggregate.csv`
Contains one row per team with flattened metrics such as:
```
team, games_played, record.wins, record.losses, record.ties, points.for, points.against, points.diff, hammer.ends, hammer.scoring_rate, hammer.two_plus_rate, hammer.blank_rate, no_hammer.ends, no_hammer.steal_rate, no_hammer.force_rate, no_hammer.defense_leq_one_rate
```

### `ALL_per_game.csv`
Contains per-game data for all teams, merged with a `__Team__` column to identify each team’s games.

---

## Recommended Workflow
1. Prepare your dataset (`games.csv`) with consistent team names.
2. Run `run_all_teams.py` to generate consolidated outputs.
3. Load `ALL_team_aggregate.csv` and/or `ALL_per_game.csv` into Tableau.
4. Use the provided dashboard wireframe to build visuals for:
   - Win/Loss trends
   - Hammer efficiency
   - Steal and defense rates
   - Opponent comparison

---

## Troubleshooting
| Issue | Cause / Fix |
|--------|--------------|
| **Missing column errors** | Check spelling and capitalization of required columns. |
| **No rows found for team** | Verify the team name matches exactly (case-insensitive). |
| **Division by zero / blank rates** | Happens if hammer or no-hammer ends are missing — data-dependent. |
| **JSON output unreadable** | Try opening in a code editor (VS Code, Sublime) or import into Excel/Power BI. |

---

## Example Usage Summary
```bash
# Single team
python curling_stats.py games.csv "Smith Rink" --season 2025 --out-json smith.json --out-games smith_games.csv

# All teams, auto outputs
python run_all_teams.py

# All teams, with custom inputs and season filter
CURLING_INPUT=games.xlsx CURLING_SEASON=2025 CURLING_OUTDIR=outputs python run_all_teams.py
```

---

## License & Notes
Free for personal or organizational analytics use. Contributions welcome!

If you expand metrics or create new dashboards, document your additions for easy reproducibility. 🧹🥌