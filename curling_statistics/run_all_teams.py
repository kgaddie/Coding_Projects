#!/usr/bin/env python3
"""
Run curling stats for ALL teams and write:
- Per-team outputs: <OUTDIR>/<team>_stats.json and <OUTDIR>/<team>_per_game.csv
- Consolidated datasets:
  * <OUTDIR>/ALL_per_game.csv  (all teams' per-game rows combined)
  * <OUTDIR>/ALL_team_aggregate.csv  (one row per team; flattened KPIs)

Edit INPUT_PATH / SEASON / OUTDIR below or pass via env vars.
Requires `curling_stats.py` (fixed-schema version) in the same directory.
"""
import os
import json
import pandas as pd
from typing import Dict, Any, List

from curling_stats import load_table, save_table, compute_stats_for_team

# -----------------------
# Config
# -----------------------
INPUT_PATH = "curling_statistics\data\curling_data.csv"        # or .xlsx / .parquet
SEASON = None                   # e.g., "2025" to filter; or None for all seasons
OUTDIR = "curling_statistics\data\outputs"

# -----------------------
# Helpers
# -----------------------

def safe_name(s: str) -> str:
    s = "" if s is None else str(s)
    return "".join(ch if ch.isalnum() or ch in "-_ " else "_" for ch in s).strip().replace(" ", "_")


def flatten(d: Dict[str, Any], parent: str = "", sep: str = ".") -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        nk = f"{parent}{sep}{k}" if parent else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, nk, sep))
        else:
            out[nk] = v
    return out

# -----------------------
# Main
# -----------------------

def main():
    os.makedirs(OUTDIR, exist_ok=True)

    # Load once
    df = load_table(INPUT_PATH)

    # Resolve actual column name for "Team Name" robustly
    lc = {str(c).strip().lower(): c for c in df.columns}
    try:
        team_col = lc["team name"]
    except KeyError:
        raise SystemExit("Input is missing required 'Team Name' column.")

    teams = sorted(df[team_col].dropna().astype(str).unique())
    print(f"Found {len(teams)} teams")

    all_per_game: List[pd.DataFrame] = []
    all_agg_rows: List[Dict[str, Any]] = []

    for team in teams:
        try:
            agg, per_game = compute_stats_for_team(df, team, season=SEASON)

            safe = safe_name(team)
            # Write per-team outputs
            with open(os.path.join(OUTDIR, f"{safe}_stats.json"), "w", encoding="utf-8") as f:
                json.dump(agg, f, indent=2, ensure_ascii=False)
            save_table(per_game, os.path.join(OUTDIR, f"{safe}_per_game.csv"))

            # Accumulate for consolidated data sources
            all_per_game.append(per_game.assign(**{"__Team__": team}))
            flat = flatten(agg)
            flat["team"] = team  # ensure plain team col exists
            all_agg_rows.append(flat)

            print(f"✓ {team}")
        except Exception as e:
            print(f"⚠️ Skipped {team}: {e}")

    # -----------------------
    # Consolidated data sources
    # -----------------------
    if all_per_game:
        per_game_all = pd.concat(all_per_game, ignore_index=True)
        # Move helper team col to front if not already present
        cols = [c for c in per_game_all.columns if c != "__Team__"]
        per_game_all = per_game_all[["__Team__"] + cols]
        save_table(per_game_all, os.path.join(OUTDIR, "ALL_per_game.csv"))
        print(f"Wrote consolidated per-game: {os.path.join(OUTDIR, 'ALL_per_game.csv')}")

    if all_agg_rows:
        agg_all = pd.DataFrame(all_agg_rows)
        # Order helpful columns first
        preferred = [
            "team", "games_played", "record.wins", "record.losses", "record.ties",
            "points.for", "points.against", "points.diff",
            "hammer.ends", "hammer.scoring_rate", "hammer.two_plus_rate", "hammer.blank_rate",
            "no_hammer.ends", "no_hammer.steal_rate", "no_hammer.force_rate", "no_hammer.defense_leq_one_rate",
        ]
        cols = [c for c in preferred if c in agg_all.columns] + [c for c in agg_all.columns if c not in preferred]
        agg_all = agg_all[cols]
        save_table(agg_all, os.path.join(OUTDIR, "ALL_team_aggregate.csv"))
        print(f"Wrote consolidated aggregates: {os.path.join(OUTDIR, 'ALL_team_aggregate.csv')}")

    print("Done.")


if __name__ == "__main__":
    main()
