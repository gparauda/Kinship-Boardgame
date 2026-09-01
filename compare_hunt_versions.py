from __future__ import annotations

"""Compare the original Hunt rules against Hunt Version B.

Version A = current game_engine.py
Version B = game_engine_vb.py

The comparison uses the exact same strategy names and seeds for both versions,
so the results are easier to compare.
"""

import csv
from pathlib import Path
import importlib.util

A_PATH = Path(__file__).with_name("game_engine.py")
B_PATH = Path(__file__).with_name("game_engine_vb.py")

GAMES_PER_STRATEGY = 1000
MAX_TURNS = 20
STRATEGIES = [
    "random",
    "food",
    "hunt",
    "kinship",
    "technology",
    "worship",
    "balanced",
]

OUTPUT_DIR = Path("hunt_version_comparison")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_version(module, version_label: str) -> list[dict]:
    rows: list[dict] = []
    game_number = 0
    for strategy in STRATEGIES:
        for index in range(GAMES_PER_STRATEGY):
            game_number += 1
            seed = 100000 + game_number
            state, turns = module.run_game(
                strategy=strategy,
                seed=seed,
                max_turns=MAX_TURNS,
            )
            rows.append(
                {
                    "version": version_label,
                    "strategy": strategy,
                    "game_number": game_number,
                    "seed": seed,
                    "turns_survived": state.total_turns,
                    "survived_target": state.total_turns >= MAX_TURNS and state.people > 0,
                    "final_people": state.people,
                    "max_people": state.max_people,
                    "final_food": state.food,
                    "max_food": state.max_food,
                    "total_hunts": state.total_hunts,
                    "successful_hunts": state.successful_hunts,
                    "hunt_failures": state.hunt_failures,
                    "hunt_deaths": state.hunt_deaths,
                    "tech_upgrades": state.tech_upgrades_completed,
                    "prayer_spent": state.prayer_spent,
                    "sacrifices": state.sacrifices,
                }
            )
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        groups.setdefault((row["version"], row["strategy"]), []).append(row)

    for (version, strategy), rs in groups.items():
        n = len(rs)
        out.append(
            {
                "version": version,
                "strategy": strategy,
                "games": n,
                "survival_rate": sum(r["survived_target"] for r in rs) / n,
                "average_turns": sum(r["turns_survived"] for r in rs) / n,
                "average_final_people": sum(r["final_people"] for r in rs) / n,
                "average_final_food": sum(r["final_food"] for r in rs) / n,
                "average_hunts": sum(r["total_hunts"] for r in rs) / n,
                "average_successful_hunts": sum(r["successful_hunts"] for r in rs) / n,
                "average_hunt_failures": sum(r["hunt_failures"] for r in rs) / n,
                "average_hunt_deaths": sum(r["hunt_deaths"] for r in rs) / n,
            }
        )
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def print_comparison(summary: list[dict]) -> None:
    print("\nHunt rule comparison")
    print("=" * 90)
    print(f"{'Version':<10} {'Strategy':<14} {'Survival':>10} {'Avg Turns':>10} {'Hunt Deaths':>12} {'Avg Food':>10}")
    print("-" * 90)
    for row in summary:
        print(
            f"{row['version']:<10} "
            f"{row['strategy']:<14} "
            f"{row['survival_rate'] * 100:>9.1f}% "
            f"{row['average_turns']:>10.2f} "
            f"{row['average_hunt_deaths']:>12.2f} "
            f"{row['average_final_food']:>10.2f}"
        )


def main() -> None:
    engine_a = load_module("engine_a", A_PATH)
    engine_b = load_module("engine_b", B_PATH)

    print(f"Running {GAMES_PER_STRATEGY} games per strategy, {MAX_TURNS} turns max...")
    rows_a = run_version(engine_a, "A-original")
    rows_b = run_version(engine_b, "B-threat-always")
    all_rows = rows_a + rows_b
    summary = summarize(all_rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "hunt_version_game_results.csv", all_rows)
    write_csv(OUTPUT_DIR / "hunt_version_summary.csv", summary)
    print_comparison(summary)

    print("\nSaved:")
    print(f"  {OUTPUT_DIR / 'hunt_version_game_results.csv'}")
    print(f"  {OUTPUT_DIR / 'hunt_version_summary.csv'}")


if __name__ == "__main__":
    main()
