# Curling Team Stats — README

This README explains how to format your input file, run the script, and interpret the statistics it returns.

---

## Overview

The script reads a table of curling games and computes team-level and per-game statistics, including hammer efficiency, steal rates, and points for/against. It supports CSV, Excel (`.xlsx`/`.xls`), and Parquet.

---

## Input File Format

**Each row is one game** from the perspective of a single team. The script expects the following columns (names are matched case-insensitively):

1. **Season** — Season identifier (e.g., `2024–25` or `2025`).
2. **Date** — Game date (recommended format `YYYY-MM-DD`).
3. **Team Name** — Your team’s name exactly as you’ll pass on the command line.
4. **Opponent** — Opposing team’s name.
5. **Location** — Venue/city/club.
6. **Outcome** — Optional free text (e.g., `W 7–4`, `L`, `Win`, etc.). Not used for calculations; the script computes its own result.
7. **Sheet** — Sheet identifier (e.g., `A`, `B`, `3`).
8. **Stone Color** — `Red` or `Yellow` (or any descriptor you use).
9. **Game Type** — `League`, `Playoff`, `Bonspiel`, `Friendly`, etc.
10. **Planned Ends** — Number of scheduled ends (e.g., `8`, `10`).
11. **Ends Played** — Number of ends actually played.
12. **End 1** … **End 9** — Per-end results from your team’s perspective.

> You can include fewer than nine end columns (e.g., only `End 1`..`End 8`). Any missing columns are ignored.

### Per-End Encoding

Each `End N` cell encodes points and whether your team had hammer.

* `+2H` → Your team scored **2** with **hammer**.
* `-1N` → Your team **allowed 1** (opponent scored 1); your team had **no hammer**.
* `0H`  → **Blank** end; your team had **hammer** (retained next end under typical rules).
* `B` or `Blank` → **Blank** end (hammer not specified). You can also use `BH`/`BN` to specify with/without hammer.
* `2H` (no sign) → Interpreted as **+2** with **hammer**.
* `-2` (no `H/N`) → Interpreted as **2 against**; hammer **unknown**.
* Empty/NaN → End not played or data missing.

> If `H/N` is omitted, hammer-based rates for that end are skipped, but points for/against still count.

### Example Row

```
Season,Date,Team Name,Opponent,Location,Outcome,Sheet,Stone Color,Game Type,Planned Ends,Ends Played,End 1,End 2,End 3,End 4,End 5,End 6,End 7,End 8,End 9
2025,2025-02-01,Monsters,Raccoons,Denver Curling,Win,A,Red,Bonspiel,8,8,+2H,-1N,0H,+1H,-2N,+3H,0H,-1N,
```

---

## Running the Script

```bash
# Basic usage (CSV/Excel/Parquet all supported)
python curling_stats.py games.csv "Monsters"

# Filter to a single season
python curling_stats.py games.xlsx "Monsters" --season 2025

# Save outputs
python curling_stats.py games.parquet "Monsters" \
  --out-json team_stats.json \
  --out-games per_game.csv
```

* `--out-json` writes the aggregate (team) statistics as JSON.
* `--out-games` writes a per-game breakdown table (CSV/XLSX/Parquet based on file extension).

---

## What Statistics Are Returned?

The script returns two outputs: an **aggregate team summary** and a **per-game breakdown**.

### 1) Aggregate Team Summary (JSON)

Key sections:

**Team & Scope**

* `team` — Team name analyzed.
* `seasons` — Seasons found in the filtered dataset.
* `games_played` — Number of games included.

**Record**

* `wins`, `losses`, `ties` — Computed from total points for vs. against in each game.

**Points**

* `for` — Total points scored across all games.
* `against` — Total points allowed across all games.
* `diff` — Points differential (`for - against`).
* `avg_for_per_game` — Average points scored per game.
* `avg_against_per_game` — Average points allowed per game.

**Hammer (when your team had hammer)**

* `ends` — Count of ends with hammer.
* `scoring_ends` — Ends with hammer where you scored > 0.
* `two_plus_ends` — Ends with hammer where you scored ≥ 2.
* `blank_ends` — Blank ends with hammer.
* `steals_allowed` — Ends with hammer where the opponent scored > 0 (i.e., steals **against** you).
* `scoring_rate` — `scoring_ends / ends`.
* `two_plus_rate` — `two_plus_ends / ends`.
* `blank_rate` — `blank_ends / ends`.

**No Hammer (when opponent had hammer)**

* `ends` — Count of ends without hammer.
* `steals_for` — Ends without hammer where **you** scored > 0 (i.e., steals **for** you).
* `force_exactly_one_ends` — Ends without hammer where opponent scored exactly 1 and you scored 0 (a classic “force”).
* `defense_leq_one_ends` — Ends without hammer where opponent scored ≤ 1 (0 or 1).
* `steal_rate` — `steals_for / ends`.
* `force_rate` — `force_exactly_one_ends / ends`.
* `defense_leq_one_rate` — `defense_leq_one_ends / ends`.

> Rates are `null` if the denominator is zero (e.g., no ends with/without hammer, or hammer unknown for all ends).

### 2) Per-Game Breakdown (table)

For each game included:

* `Season`, `Date`, `Team Name`, `Opponent`, `Location`, `Sheet`, `Stone Color`, `Game Type`, `Planned Ends`, `Ends Played`
* `Outcome (from dataset)` — The raw text from your data (not used for calculations)
* `Computed Result` — `W`, `L`, or `T`, based on points-for vs. against derived from end data
* `Points For`, `Points Against`
* `Hammer Ends`, `No-Hammer Ends`
* `Steals For`, `Steals Against`

---

## Best Practices & Tips

* **Consistent team naming**: The script matches `Team Name` exactly (case-insensitive). Keep it consistent across rows.
* **Prefer `YYYY-MM-DD` dates**: Easier to sort and filter.
* **Encode hammer whenever possible**: Rates like hammer scoring and steal/force heavily rely on `H/N` flags.
* **Outcome is optional**: The script computes its own W/L/T from end totals.
* **Short games**: If `Ends Played` < `Planned Ends`, leave later `End N` cells blank.

---

## Troubleshooting

* **“Missing required columns”** — Ensure all schema columns exist (names can vary in capitalization, but spelling must match).
* **“No rows found for team …”** — Check team spelling and season filter.
* **Weird rates** — If hammer is often missing (`H/N` omitted), hammer-based rates will be `null` and only points totals will be reliable.

---

## Example Mini-Dataset (CSV)

```
Season,Date,Team Name,Opponent,Location,Outcome,Sheet,Stone Color,Game Type,Planned Ends,Ends Played,End 1,End 2,End 3,End 4,End 5,End 6,End 7,End 8,End 9
2025,2025-02-01,Monsters,Raccoons,Denver Curling,Win,A,Red,League,8,8,+2H,-1N,0H,+1H,-2N,+3H,0H,-1N,
2025,2025-02-05,Monsters,Mopac3,Rock Creek Curling,Loss,B,Yellow,Bonspiel,8,6,0H,+2H,-1N,+1H,-2N,+2H,,,
```

---

## License & Attribution

Use, modify, and share freely. If you extend the script (e.g., charts, per-opponent splits), consider documenting your changes here for future you.