from __future__ import annotations

"""Simulator for Version C of the Kinship board game.

This file is designed to work with game_engine_vc.py.
It runs many complete games, records game-level and turn-level data,
and writes CSV files for later analysis.
"""

# import csv
from pathlib import Path
import random

from game_engine_vc import GameState, run_game, strategy_allocation


# ============================================================
# SETTINGS
# ============================================================

# Number of games to run for each strategy.
GAMES_PER_STRATEGY = 1000

# Maximum number of turns in a simulated game.
MAX_TURNS = 100

# Folder where all Version C results will be saved.
OUTPUT_DIR = Path("simulation_results_vc")

# Built-in strategies from game_engine_vc.py.
STRATEGIES = [
    "random",
    "food",
    "hunt",
    "kinship",
    "technology",
    "worship",
    "balanced",
]


# ============================================================
# RUN GAMES
# ============================================================


def simulate_strategy(strategy: str) -> tuple[list[dict], list[dict]]:
    """Run all games for one strategy and return game/turn rows."""

    game_rows: list[dict] = []
    turn_rows: list[dict] = []

    for game_number in range(1, GAMES_PER_STRATEGY + 1):
        # Unique seed so every game has a reproducible random sequence.
        seed = 100000 + (game_number * 100) + hash(strategy) % 100

        state, turns = run_game(
            strategy=strategy,
            seed=seed,
            max_turns=MAX_TURNS,
        )

        # Record every turn from this game.
        for row in turns:
            row = row.copy()
            row["strategy"] = strategy
            row["game_number"] = game_number
            row["seed"] = seed
            turn_rows.append(row)

        # Determine why the game ended.
        if state.people <= 0:
            end_reason = "population_zero"
        elif state.total_turns >= MAX_TURNS:
            end_reason = "max_turns_reached"
        else:
            end_reason = "other"

        game_rows.append(
            {
                "strategy": strategy,
                "game_number": game_number,
                "seed": seed,
                "turns_survived": state.total_turns,
                "ended_at_max_turns": state.total_turns >= MAX_TURNS and state.people > 0,
                "end_reason": end_reason,
                "final_people": state.people,
                "max_people": state.max_people,
                "final_food": state.food,
                "max_food": state.max_food,
                "total_hunts": state.total_hunts,
                "successful_hunts": state.successful_hunts,
                "hunt_failures": state.hunt_failures,
                "hunt_deaths": state.hunt_deaths,
                "tech_sets_completed": state.tech_sets_completed,
                "tech_upgrades": state.tech_upgrades_completed,
                "kinship_started": state.kinship_started,
                "kinship_completed": state.kinship_completed,
                "prayer_earned": state.prayer_earned,
                "prayer_spent": state.prayer_spent,
                "events_ignored": state.events_ignored,
                "sacrifices": state.sacrifices,
            }
        )

    return game_rows, turn_rows


# ============================================================
# SUMMARIZE RESULTS
# ============================================================


def summarize(game_rows: list[dict]) -> list[dict]:
    """Create one summary row per strategy."""

    summary: list[dict] = []

    for strategy in STRATEGIES:
        rows = [r for r in game_rows if r["strategy"] == strategy]
        if not rows:
            continue

        n = len(rows)

        def avg(column: str) -> float:
            return sum(float(r[column]) for r in rows) / n

        summary.append(
            {
                "strategy": strategy,
                "games": n,
                "survival_rate": sum(r["ended_at_max_turns"] for r in rows) / n,
                "average_turns": avg("turns_survived"),
                "average_final_people": avg("final_people"),
                "average_max_people": avg("max_people"),
                "average_final_food": avg("final_food"),
                "average_max_food": avg("max_food"),
                "average_hunts": avg("total_hunts"),
                "average_successful_hunts": avg("successful_hunts"),
                "average_hunt_failures": avg("hunt_failures"),
                "average_hunt_deaths": avg("hunt_deaths"),
                "average_tech_upgrades": avg("tech_upgrades"),
                "average_kinship_started": avg("kinship_started"),
                "average_kinship_completed": avg("kinship_completed"),
                "average_prayer_earned": avg("prayer_earned"),
                "average_prayer_spent": avg("prayer_spent"),
                "average_events_ignored": avg("events_ignored"),
                "average_sacrifices": avg("sacrifices"),
            }
        )

    return summary

# ============================================================
# PRINT RESULTS
# ============================================================


def print_summary(summary: list[dict]) -> None:
    print("\nVersion C simulation")
    print("=" * 100)
    print(
        f"{'Strategy':<14} "
        f"{'Survival':>10} "
        f"{'Avg Turns':>10} "
        f"{'Avg People':>12} "
        f"{'Avg Food':>10} "
        f"{'Hunt Deaths':>12}"
    )
    print("-" * 100)

    for row in summary:
        print(
            f"{row['strategy']:<14} "
            f"{row['survival_rate'] * 100:>9.1f}% "
            f"{row['average_turns']:>10.2f} "
            f"{row['average_final_people']:>12.2f} "
            f"{row['average_final_food']:>10.2f} "
            f"{row['average_hunt_deaths']:>12.2f}"
        )


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    print(
        f"Running Version C: {GAMES_PER_STRATEGY} games per strategy, "
        f"{MAX_TURNS} turns max."
    )

    all_game_rows: list[dict] = []
    all_turn_rows: list[dict] = []

    for strategy in STRATEGIES:
        print(f"Running strategy: {strategy}")
        game_rows, turn_rows = simulate_strategy(strategy)
        all_game_rows.extend(game_rows)
        all_turn_rows.extend(turn_rows)

    summary = summarize(all_game_rows)

    # write_csv(OUTPUT_DIR / "game_results.csv", all_game_rows)
    # write_csv(OUTPUT_DIR / "turn_results.csv", all_turn_rows)
    # write_csv(OUTPUT_DIR / "strategy_summary.csv", summary)

    print_summary(summary)

    # print("\nSaved results to:")
    # print(f"  {OUTPUT_DIR / 'game_results.csv'}")
    # print(f"  {OUTPUT_DIR / 'turn_results.csv'}")
    # print(f"  {OUTPUT_DIR / 'strategy_summary.csv'}")


if __name__ == "__main__":
    main()
