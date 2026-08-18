from __future__ import annotations

"""Batch simulator for the Kinship board game prototype.

Creates CSV output in ./simulation_results by default.
"""

import csv
from pathlib import Path
from statistics import mean, median

from game_engine import run_game

STRATEGIES = [
    "random",
    "food",
    "hunt",
    "kinship",
    "technology",
    "worship",
    "balanced",
]

DEFAULT_GAMES_PER_STRATEGY = 1000
DEFAULT_MAX_TURNS = 20
OUTPUT_DIR = Path("simulation_results")


def run_simulation(
    games_per_strategy: int = DEFAULT_GAMES_PER_STRATEGY,
    max_turns: int = DEFAULT_MAX_TURNS,
    strategies: list[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    if strategies is None:
        strategies = STRATEGIES

    game_rows: list[dict] = []
    turn_rows: list[dict] = []
    seed_base = 100000
    game_number = 0

    for strategy in strategies:
        for index in range(games_per_strategy):
            game_number += 1
            seed = seed_base + game_number
            state, turns = run_game(
                strategy=strategy,
                seed=seed,
                max_turns=max_turns,
            )

            survived_target = state.total_turns >= max_turns and state.people > 0
            game_rows.append(
                {
                    "game_number": game_number,
                    "strategy": strategy,
                    "seed": seed,
                    "turns_survived": state.total_turns,
                    "survived_target": survived_target,
                    "final_people": state.people,
                    "max_people": state.max_people,
                    "final_food": state.food,
                    "max_food": state.max_food,
                    "total_hunts": state.total_hunts,
                    "successful_hunts": state.successful_hunts,
                    "hunt_failures": state.hunt_failures,
                    "hunt_deaths": state.hunt_deaths,
                    "total_food_rolls": state.total_food_rolls,
                    "total_food_gained": state.total_food_gained,
                    "kinship_started": state.kinship_started,
                    "kinship_completed": state.kinship_completed,
                    "tech_sets_completed": state.tech_sets_completed,
                    "tech_upgrades_completed": state.tech_upgrades_completed,
                    "prayer_earned": state.prayer_earned,
                    "prayer_spent": state.prayer_spent,
                    "sacrifices": state.sacrifices,
                    "events_ignored": state.events_ignored,
                }
            )

            for row in turns:
                row_copy = dict(row)
                row_copy["game_number"] = game_number
                row_copy["strategy"] = strategy
                row_copy["seed"] = seed
                turn_rows.append(row_copy)

    return game_rows, turn_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)

    # Union all keys because turn rows vary slightly when a game ends early.
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize(game_rows: list[dict]) -> list[dict]:
    summary: list[dict] = []
    by_strategy: dict[str, list[dict]] = {}
    for row in game_rows:
        by_strategy.setdefault(row["strategy"], []).append(row)

    for strategy, rows in by_strategy.items():
        turns = [r["turns_survived"] for r in rows]
        win_count = sum(bool(r["survived_target"]) for r in rows)
        summary.append(
            {
                "strategy": strategy,
                "games": len(rows),
                "survival_rate": win_count / len(rows),
                "average_turns": mean(turns),
                "median_turns": median(turns),
                "average_final_people": mean(r["final_people"] for r in rows),
                "average_max_people": mean(r["max_people"] for r in rows),
                "average_final_food": mean(r["final_food"] for r in rows),
                "average_hunts": mean(r["total_hunts"] for r in rows),
                "average_hunt_deaths": mean(r["hunt_deaths"] for r in rows),
                "average_tech_upgrades": mean(r["tech_upgrades_completed"] for r in rows),
                "average_prayer_spent": mean(r["prayer_spent"] for r in rows),
                "average_sacrifices": mean(r["sacrifices"] for r in rows),
            }
        )

    summary.sort(key=lambda x: (-x["survival_rate"], -x["average_turns"]))
    return summary


def write_summary(path: Path, rows: list[dict]) -> None:
    write_csv(path, rows)


def print_summary(rows: list[dict]) -> None:
    print("\nSimulation summary")
    print("=" * 95)
    print(
        f"{'Strategy':<14} {'Survival':>10} {'Avg Turns':>10} "
        f"{'Avg People':>11} {'Avg Food':>10} {'Hunt Deaths':>12}"
    )
    print("-" * 95)

    for row in rows:
        print(
            f"{row['strategy']:<14} "
            f"{row['survival_rate'] * 100:>9.1f}% "
            f"{row['average_turns']:>10.2f} "
            f"{row['average_final_people']:>11.2f} "
            f"{row['average_final_food']:>10.2f} "
            f"{row['average_hunt_deaths']:>12.2f}"
        )


def main() -> None:
    games_per_strategy = DEFAULT_GAMES_PER_STRATEGY
    max_turns = DEFAULT_MAX_TURNS

    print(
        f"Running {games_per_strategy} games per strategy "
        f"({max_turns} turns max)..."
    )

    game_rows, turn_rows = run_simulation(
        games_per_strategy=games_per_strategy,
        max_turns=max_turns,
    )
    summary_rows = summarize(game_rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "game_results.csv", game_rows)
    write_csv(OUTPUT_DIR / "turn_results.csv", turn_rows)
    write_summary(OUTPUT_DIR / "strategy_summary.csv", summary_rows)

    print_summary(summary_rows)
    print("\nSaved:")
    print(f"  {OUTPUT_DIR / 'game_results.csv'}")
    print(f"  {OUTPUT_DIR / 'turn_results.csv'}")
    print(f"  {OUTPUT_DIR / 'strategy_summary.csv'}")


if __name__ == "__main__":
    main()
