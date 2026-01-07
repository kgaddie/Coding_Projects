"""
Curling Team Stats (Fixed Column Schema)
=======================================

This script ingests a tabular dataset of curling games (CSV/Excel/Parquet) with a
fixed set of columns and computes a set of statistics for a given team.

Required columns (exact logical fields; matching is case-insensitive):
- Season [ex: 2024-2025], text
- Date [ex: 2024-11-15], date/text
- Team Name [ex: "Monsters"], text
- Opponent [ex: "Matthews"], text
- Location [ex: "Denver CC"], text
- Outcome [ex: "Win", "Loss"], text
- Sheet [ex: "A", "3"], text
- Stone Color [ex: "Red", "Yellow"], text
- Game Type [ex: "League", "Playoff"], text
- Planned Ends [ex: 8, 10], integer
- Ends Played [ex: 8, 10], integer
- End 1, End 2, ... End 9 (any subset present is OK) [ex: "+2H", "-1N", "B"], text

Per-end cell encoding (flexible):
- "+2H" → scored 2 with hammer
- "-1N" → allowed 1 without hammer (we did not have hammer)
- "0H"  → blank end with hammer retained
- "B" or "Blank" → blank end (optionally with H/N, e.g., "BH")
- "2H" (no sign) → interpreted as +2 with hammer
- "-2" (no H/N) → interpreted as 2 against, hammer unknown
- Empty/NaN → end not played or data missing

Outputs:
- Printed JSON summary to stdout
- Optional JSON/CSV/Excel/Parquet reports via CLI flags

Usage examples:
  python curling_stats.py curling_statistics\data\curling_data.csv "Monsters"
  python curling_stats.py curling_statistics\data\curling_data.csv "Monsters" --season 2025 --out-json curling_statistics\data\stats.json --out-games curling_statistics\data\per_game.csv

"""

#########################################
# Importing Base Packages for Scripting #
#########################################

# Standard Python Base Packages
from __future__ import annotations
import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Third-Party Packages to be Installed via pip
import pandas as pd

##############################
# Constants for fixed schema #
##############################

SCHEMA_COLS = [
    "Season", "Date", "Team Name", "Opponent", "Location", "Outcome", "Sheet",
    "Stone Color", "Game Type", "Planned Ends", "Ends Played",
]
END_COLUMNS = [f"End {i}" for i in range(1, 10)]  # End 1..End 9

# Regex for parsing end tokens (avoid backslash sequences in this file)
NORMALIZE_KEEP = re.compile(r"[^0-9+HNBN-]", re.IGNORECASE)  # keep digits, +, H/N/B, -


#############################################################
# Parsing helpers for Input File Interpretation/Integration #
#############################################################

@dataclass #Shortcut for creating classes for data storage in statistics

class EndResult:
    points_for: int = 0
    points_against: int = 0
    had_hammer: Optional[bool] = None  # True (H), False (N), None unknown
    is_blank: bool = False

    @property
    def steal_for(self) -> Optional[bool]:
        if self.had_hammer is None:
            return None
        return (not self.had_hammer) and (self.points_for > 0)

    @property
    def steal_against(self) -> Optional[bool]:
        if self.had_hammer is None:
            return None
        return self.had_hammer and (self.points_against > 0)

    @property
    def hammer_two_plus(self) -> Optional[bool]:
        if self.had_hammer is None:
            return None
        return self.had_hammer and (self.points_for >= 2)

    @property
    def hammer_scoring(self) -> Optional[bool]:
        if self.had_hammer is None:
            return None
        return self.had_hammer and (self.points_for > 0)

    @property
    def hammer_blank(self) -> Optional[bool]:
        if self.had_hammer is None:
            return None
        return self.had_hammer and self.is_blank

    @property
    def force_exactly_one(self) -> Optional[bool]:
        if self.had_hammer is None:
            return None
        return (not self.had_hammer) and (self.points_against == 1) and (self.points_for == 0)

    @property
    def no_hammer_defense_leq_one(self) -> Optional[bool]:
        if self.had_hammer is None:
            return None
        return (not self.had_hammer) and (self.points_against <= 1)

def _clean_end_token(raw: object) -> str:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    if s.lower() in {"b", "blank", "blank end"}:
        return "B"
    s2 = re.sub(NORMALIZE_KEEP, "", s)
    if not s2:
        # salvage digits and H/N if present
        digits = re.findall(r"[+-]?[0-9]+", s)
        flags = re.findall(r"[HN]", s, re.IGNORECASE)
        s2 = (digits[0] if digits else "") + (flags[0].upper() if flags else "")
    return s2.upper()

def parse_end_value(raw: object) -> Optional[EndResult]:
    if pd.isna(raw):
        return None
    token = _clean_end_token(raw)
    if token == "":
        return None

    if token in {"B", "BH", "BN"}:
        hh = None if token == "B" else token.endswith("H")
        return EndResult(points_for=0, points_against=0, had_hammer=hh, is_blank=True)

    m = re.match(r"^([+-]?)([0-9]+)([HN])?$", token)
    if not m:
        nums = re.findall(r"[+-]?[0-9]+", token)
        flags = re.findall(r"[HN]", token)
        if not nums:
            return None
        val = int(nums[0])
        hh = (flags[0].upper() == "H") if flags else None
    else:
        sign, num, flag = m.groups()
        val = int(num)
        if sign == "-":
            val = -val
        hh = None if flag is None else (flag.upper() == "H")

    if val == 0:
        return EndResult(points_for=0, points_against=0, had_hammer=hh, is_blank=True)
    elif val > 0:
        return EndResult(points_for=val, points_against=0, had_hammer=hh, is_blank=False)
    else:
        return EndResult(points_for=0, points_against=abs(val), had_hammer=hh, is_blank=False)


##############################################
# Data Class for Team Aggregation Statistics #
##############################################

@dataclass
class TeamGameStats:
    points_for: int = 0
    points_against: int = 0

    def result(self) -> str:
        if self.points_for > self.points_against:
            return "W"
        if self.points_for < self.points_against:
            return "L"
        return "T"

@dataclass
class TeamAggregate:
    team: str
    seasons: set
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    points_for: int = 0
    points_against: int = 0
    hammer_ends: int = 0
    nonhammer_ends: int = 0
    hammer_scoring_ends: int = 0
    hammer_two_plus_ends: int = 0
    hammer_blank_ends: int = 0
    steals_for: int = 0
    steals_against: int = 0
    force_exactly_one_ends: int = 0
    no_hammer_defense_leq_one_ends: int = 0

    def finalize(self) -> Dict:
        pf, pa = self.points_for, self.points_against
        gd = pf - pa
        avg_pf_game = pf / self.games_played if self.games_played else 0.0
        avg_pa_game = pa / self.games_played if self.games_played else 0.0

        def r(x):
            return None if x is None else round(x, 3)

        return {
            "team": self.team,
            "seasons": sorted(self.seasons),
            "games_played": self.games_played,
            "record": {"wins": self.wins, "losses": self.losses, "ties": self.ties},
            "points": {
                "for": pf,
                "against": pa,
                "diff": gd,
                "avg_for_per_game": round(avg_pf_game, 3),
                "avg_against_per_game": round(avg_pa_game, 3),
            },
            "hammer": {
                "ends": self.hammer_ends,
                "scoring_ends": self.hammer_scoring_ends,
                "two_plus_ends": self.hammer_two_plus_ends,
                "blank_ends": self.hammer_blank_ends,
                "scoring_rate": r(self.hammer_scoring_ends / self.hammer_ends if self.hammer_ends else None),
                "two_plus_rate": r(self.hammer_two_plus_ends / self.hammer_ends if self.hammer_ends else None),
                "blank_rate": r(self.hammer_blank_ends / self.hammer_ends if self.hammer_ends else None),
                "steals_allowed": self.steals_against,
            },
            "no_hammer": {
                "ends": self.nonhammer_ends,
                "steals_for": self.steals_for,
                "steal_rate": r(self.steals_for / self.nonhammer_ends if self.nonhammer_ends else None),
                "force_exactly_one_ends": self.force_exactly_one_ends,
                "force_rate": r(self.force_exactly_one_ends / self.nonhammer_ends if self.nonhammer_ends else None),
                "defense_leq_one_ends": self.no_hammer_defense_leq_one_ends,
                "defense_leq_one_rate": r(self.no_hammer_defense_leq_one_ends / self.nonhammer_ends if self.nonhammer_ends else None),
            },
        }


####################
# Core computation #
####################

def compute_stats_for_team(
    df: pd.DataFrame,
    team: str,
    season: Optional[str] = None,
) -> Tuple[Dict, pd.DataFrame]:
    # Normalize columns by case-insensitive lookup
    lc = {str(c).strip().lower(): c for c in df.columns}

    # Validate presence (we allow missing trailing End columns)
    missing = [c for c in SCHEMA_COLS if c.lower() not in lc]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    end_cols_present = [c for c in END_COLUMNS if c.lower() in lc]
    # Map to real-case column names from df
    season_col = lc["season"]
    date_col = lc["date"]
    team_col = lc["team name"]
    opp_col = lc["opponent"]
    location_col = lc["location"]
    outcome_col = lc["outcome"]
    sheet_col = lc["sheet"]
    stone_col = lc["stone color"]
    game_type_col = lc["game type"]
    planned_col = lc["planned ends"]
    played_col = lc["ends played"]
    end_cols_real = [lc[c.lower()] for c in end_cols_present]

    # Filter to the specified team and optional season
    mask = df[team_col].astype(str).str.strip().str.lower() == team.strip().lower()
    if season is not None:
        mask &= df[season_col].astype(str).str.strip().str.lower() == str(season).strip().lower()
    team_df = df.loc[mask].copy()

    if team_df.empty:
        msg = f"No rows found for team '{team}'" + (f" in season '{season}'" if season else "")
        raise ValueError(msg)

    agg = TeamAggregate(team=team, seasons=set())
    per_game_records: List[Dict] = []

    for _, row in team_df.iterrows():
        agg.seasons.add(str(row[season_col]))

        game_points_for = 0
        game_points_against = 0
        hammer_ends = nonhammer_ends = 0
        hammer_scoring_ends = hammer_two_plus_ends = hammer_blank_ends = 0
        steals_for = steals_against = 0
        force_exactly_one_ends = no_hammer_defense_leq_one_ends = 0

        for c in end_cols_real:
            res = parse_end_value(row[c])
            if res is None:
                continue

            game_points_for += res.points_for
            game_points_against += res.points_against

            if res.had_hammer is True:
                hammer_ends += 1
                if res.hammer_scoring:
                    hammer_scoring_ends += 1
                if res.hammer_two_plus:
                    hammer_two_plus_ends += 1
                if res.hammer_blank:
                    hammer_blank_ends += 1
                if res.steal_against:
                    steals_against += 1
            elif res.had_hammer is False:
                nonhammer_ends += 1
                if res.steal_for:
                    steals_for += 1
                if res.force_exactly_one:
                    force_exactly_one_ends += 1
                if res.no_hammer_defense_leq_one:
                    no_hammer_defense_leq_one_ends += 1

        # Update aggregates
        agg.games_played += 1
        agg.points_for += game_points_for
        agg.points_against += game_points_against
        agg.hammer_ends += hammer_ends
        agg.nonhammer_ends += nonhammer_ends
        agg.hammer_scoring_ends += hammer_scoring_ends
        agg.hammer_two_plus_ends += hammer_two_plus_ends
        agg.hammer_blank_ends += hammer_blank_ends
        agg.steals_for += steals_for
        agg.steals_against += steals_against
        agg.force_exactly_one_ends += force_exactly_one_ends
        agg.no_hammer_defense_leq_one_ends += no_hammer_defense_leq_one_ends

        g = TeamGameStats(points_for=game_points_for, points_against=game_points_against)
        res_letter = g.result()
        if res_letter == "W":
            agg.wins += 1
        elif res_letter == "L":
            agg.losses += 1
        else:
            agg.ties += 1

        per_game_records.append({
            "Season": row[season_col],
            "Date": row[date_col],
            "Team Name": row[team_col],
            "Opponent": row[opp_col],
            "Location": row[location_col],
            "Outcome (from dataset)": row[outcome_col],
            "Computed Result": res_letter,
            "Sheet": row[sheet_col],
            "Stone Color": row[stone_col],
            "Game Type": row[game_type_col],
            "Planned Ends": row[planned_col],
            "Ends Played": row[played_col],
            "Points For": game_points_for,
            "Points Against": game_points_against,
            "Hammer Ends": hammer_ends,
            "No-Hammer Ends": nonhammer_ends,
            "Steals For": steals_for,
            "Steals Against": steals_against,
        })

    per_game_df = pd.DataFrame(per_game_records)
    return agg.finalize(), per_game_df


###########################################
# Definitions for Loading and Saving Data #
###########################################

def load_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".csv", ".tsv"}:
        return pd.read_csv(path)
    if ext in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if ext == ".parquet":
        return pd.read_parquet(path)
    # default to csv
    return pd.read_csv(path)

def save_table(df: pd.DataFrame, path: Optional[str]):
    if not path:
        return
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext in {".xlsx", ".xls"}:
        df.to_excel(path, index=False)
    elif ext == ".parquet":
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)


#################################################################
# Definitions for Client Interactions for Calling Specific Data #
#################################################################

def main():
    p = argparse.ArgumentParser(description="Compute curling stats for a team from a fixed-schema dataset.")
    p.add_argument("input", help="Path to input table (CSV/XLSX/Parquet)")
    p.add_argument("team", help="Team name to analyze (exact match, case-insensitive)")
    p.add_argument("--season", default=None, help="Optional season filter (exact match)")
    p.add_argument("--out-json", default=None, help="Optional path to write aggregate stats JSON")
    p.add_argument("--out-games", default=None, help="Optional path to write per-game CSV/XLSX/Parquet")
    
    args = p.parse_args()

    df = load_table(args.input)
    aggregate, per_game = compute_stats_for_team(df, args.team, season=args.season)

    # Pretty print summary
    print("\n=== Team Summary ===")
    print(json.dumps(aggregate, indent=2, default=str))

    # Optional outputs
    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(aggregate, f, indent=2, default=str)

    if args.out_games:
        save_table(per_game, args.out_games)

    print("\nPer-game breakdown (first 10 rows):")
    try:
        print(per_game.head(10).to_string(index=False))
    except Exception:
        print(per_game.head(10))

# Checking to see if script is being called/run directly or importated as a module
if __name__ == "__main__":
    main()
