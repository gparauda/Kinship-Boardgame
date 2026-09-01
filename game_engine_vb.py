from __future__ import annotations

"""Simulation-friendly game engine for the Kinship board game prototype.

This file contains game rules/state only. It does not ask for terminal input.
The simulator can call run_turn(...) with an allocation dictionary such as
{"F": 3, "K": 2}.

The rules below are based on the user's current civigameadv.py prototype.
"""

from dataclasses import dataclass, field
import random
from typing import Optional

# -----------------------------
# Base game tables
# -----------------------------

# Matches the current playable prototype's FOOD_REFERENCE.
FOOD_REFERENCE = {
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 2,
    6: 3,
}

HUNT_FACES = ["skull", "skull", 2, 3, 4, 5]

TECHNOLOGY_REFERENCE = {
    1: ("item", "stick"),
    2: ("item", "rope"),
    3: ("item", "rock"),
    4: ("item", "stick"),
    5: ("item", "rope"),
    6: ("item", "rock"),
}

WORSHIP_REFERENCE = {
    1: ("sacrifice", 1),
    2: ("sacrifice", 1),
    3: ("prayer", 1),
    4: ("prayer", 1),
    5: ("prayer", 1),
    6: ("prayer", 1),
}

EVENTS_T1 = [
    {
        "name": "Mild Winter",
        "description": "Food production is reduced by 1 this turn.",
        "threat": 5,
        "food_modifier": -1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Animal Migration",
        "description": "The animal migration makes it easier to hunt. Add 2 to your total Hunt score.",
        "threat": 6,
        "food_modifier": 0,
        "hunt_modifier": 2,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Calm Skies",
        "description": "Everything is going smoothly.",
        "threat": 5,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Rocky Terrain",
        "description": "The mountainous terrain makes hunting more difficult. Subtract 3 from your total Hunt score.",
        "threat": 3,
        "food_modifier": 0,
        "hunt_modifier": -3,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Local Thieves",
        "description": "Thieves steal 3 food from your supplies.",
        "threat": 5,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 3,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
]

EVENTS_T2 = [
    {
        "name": "Harsh Winter",
        "description": "Food production is reduced by 2 this turn.",
        "threat": 8,
        "food_modifier": -2,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Predator Activity",
        "description": "Food production is reduced by 2, and the Hunt score is reduced by 2.",
        "threat": 7,
        "food_modifier": -2,
        "hunt_modifier": -2,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Fertile Season",
        "description": "Food production increases by 1 this turn.",
        "threat": 9,
        "food_modifier": 1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Obsidian Deposit",
        "description": "Your tribe finds valuable materials. Gain 1 additional Prayer Token this turn from each Prayer result.",
        "threat": 7,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 1,
    },
    {
        "name": "Spiritual Awakening",
        "description": "Your tribe feels unusually connected to the spirits. Gain 1 additional Prayer Token this turn from each Prayer result.",
        "threat": 10,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 1,
    },
]

EVENTS_T3 = [
    {
        "name": "Endless Winter",
        "description": "Food production is reduced by 2 this turn.",
        "threat": 13,
        "food_modifier": -2,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Mammoth Herd",
        "description": "A massive herd has appeared. Add 2 to your total Hunt score.",
        "threat": 15,
        "food_modifier": 0,
        "hunt_modifier": 2,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Epidemic",
        "description": "The tribe is weakened. Food production is reduced by 1 this turn.",
        "threat": 13,
        "food_modifier": -1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Great Flood",
        "description": "Floodwaters damage food supplies. Food production is reduced by 1 this turn.",
        "threat": 12,
        "food_modifier": -1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0,
    },
    {
        "name": "Eclipse",
        "description": "The tribe receives a sign from the spirits. Gain 1 additional Prayer Token this turn from each Prayer result.",
        "threat": 14,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 1,
    },
]

VALID_CATEGORIES = {"F", "K", "H", "T", "W"}


@dataclass
class GameState:
    people: int = 5
    food: int = 7
    turn: int = 1
    prayer_tokens: int = 0
    kinship_projects: list[int] = field(default_factory=list)
    tech_tiles: list[str] = field(default_factory=list)
    tech_upgrades: dict[str, dict[int, int]] = field(
        default_factory=lambda: {"F": {}, "W": {}, "T": {}}
    )
    current_event: Optional[dict] = None

    # Statistics collected during a simulation.
    total_hunts: int = 0
    successful_hunts: int = 0
    hunt_failures: int = 0
    hunt_deaths: int = 0
    total_food_rolls: int = 0
    total_food_gained: int = 0
    kinship_started: int = 0
    kinship_completed: int = 0
    tech_sets_completed: int = 0
    tech_upgrades_completed: int = 0
    prayer_earned: int = 0
    prayer_spent: int = 0
    sacrifices: int = 0
    events_ignored: int = 0
    total_turns: int = 0
    max_people: int = 5
    max_food: int = 7


def draw_event(turn: int, rng: random.Random) -> dict:
    if turn == 1:
        return {
            "name": "First Turn",
            "description": "No event on the first turn.",
            "threat": 5,
            "food_modifier": 0,
            "hunt_modifier": 0,
            "food_loss": 0,
            "kinship_modifier": 0,
            "prayer_modifier": 0,
        }
    if turn <= 7:
        return rng.choice(EVENTS_T1).copy()
    if turn <= 14:
        return rng.choice(EVENTS_T2).copy()
    return rng.choice(EVENTS_T3).copy()


def event_mod(state: GameState, key: str) -> int:
    if state.current_event is None:
        return 0
    if state.current_event.get("ignored", False):
        return 0
    return int(state.current_event.get(key, 0))


def tech_bonus(state: GameState, category: str, roll: int) -> int:
    return int(state.tech_upgrades.get(category, {}).get(roll, 0))


def roll_die(rng: random.Random) -> int:
    return rng.randint(1, 6)


def roll_hunt_die(rng: random.Random) -> tuple[str, int]:
    face = rng.choice(HUNT_FACES)
    value = 0 if face == "skull" else face
    return face, value


def active_kinship_workers(state: GameState) -> int:
    return 2 * len(state.kinship_projects)


def resolve_kinship_projects(state: GameState) -> int:
    """Advance timers at turn start. Returns number of completed projects."""
    still_active: list[int] = []
    completed = 0

    for turns_left in state.kinship_projects:
        turns_left -= 1
        if turns_left <= 0:
            completed += 1
        else:
            still_active.append(turns_left)

    state.kinship_projects = still_active
    state.people += completed
    state.kinship_completed += completed
    state.max_people = max(state.max_people, state.people)
    return completed


def choose_technology_upgrade_sim(state: GameState, category: str = "F") -> tuple[str, int]:
    """Choose a deterministic, simple tech upgrade for simulation.

    The caller can supply F or W. The simulator uses the lowest face in that
    category with the best marginal effect as a deterministic default.
    """
    if category == "F":
        scores = []
        for face in range(1, 7):
            current = FOOD_REFERENCE[face] + tech_bonus(state, "F", face)
            scores.append((current, face))
        _, face = min(scores, key=lambda x: (x[0], x[1]))
    elif category == "W":
        scores = []
        for face in range(3, 7):
            _, base = WORSHIP_REFERENCE[face]
            current = base + tech_bonus(state, "W", face)
            scores.append((current, face))
        _, face = min(scores, key=lambda x: (x[0], x[1]))
    else:
        raise ValueError("Simulation upgrades can only target F or W")

    state.tech_upgrades[category][face] = tech_bonus(state, category, face) + 1
    state.tech_upgrades_completed += 1
    return category, face


def resolve_sacrifice_sim(state: GameState, roll: int, strategy: str, rng: random.Random) -> None:
    """Resolve an immediate sacrifice using a simple strategy policy."""
    upgraded = tech_bonus(state, "W", roll) > 0
    state.sacrifices += 1
    state.people -= 1

    if state.people < 0:
        state.people = 0
        return

    if strategy == "food":
        choice = 1
    elif strategy == "technology":
        choice = 2
    elif strategy == "kinship":
        choice = 3
    elif strategy == "worship":
        choice = 2
    elif strategy == "hunt":
        choice = 1
    elif strategy == "random":
        choice = rng.choice([1, 2, 3])
    else:
        # Balanced policy: use the immediate payoff if food is dangerously low,
        # otherwise take the long-term benefit.
        choice = 1 if state.food < max(3, state.people) else 2

    if choice == 1:
        state.food += 20 if upgraded else 10
    elif choice == 2:
        choose_technology_upgrade_sim(state, category="F")
        if upgraded:
            choose_technology_upgrade_sim(state, category="F")
    elif choice == 3:
        # Regular sacrifice: immediately finish all Kinship projects.
        # Devout sacrifice: net +1 person (sacrifice was already applied above).
        if upgraded:
            state.people += 2
            state.max_people = max(state.max_people, state.people)
        else:
            completed = len(state.kinship_projects)
            state.kinship_projects = []
            state.people += completed
            state.max_people = max(state.max_people, state.people)


def resolve_worship_roll(state: GameState, roll: int, strategy: str, rng: random.Random) -> None:
    effect, value = WORSHIP_REFERENCE[roll]
    if effect == "prayer":
        gained = value + tech_bonus(state, "W", roll) + event_mod(state, "prayer_modifier")
        state.prayer_tokens += gained
        state.prayer_earned += gained
    else:
        resolve_sacrifice_sim(state, roll, strategy, rng)


def check_technology_completion_sim(state: GameState, strategy: str) -> None:
    required = {"stick", "rope", "rock"}
    if not required.issubset(set(state.tech_tiles)):
        return

    state.tech_sets_completed += 1
    # The user's current rule: when one of each is present, consume all pieces.
    state.tech_tiles = []

    # Technology strategy choices.
    if strategy == "worship":
        choose_technology_upgrade_sim(state, "W")
    else:
        choose_technology_upgrade_sim(state, "F")


def apply_food_roll(state: GameState, roll: int) -> int:
    gain = FOOD_REFERENCE[roll]
    gain += tech_bonus(state, "F", roll)
    gain += event_mod(state, "food_modifier")
    gain = max(gain, 0)
    state.food += gain
    state.total_food_rolls += 1
    state.total_food_gained += gain
    return gain


def resolve_hunt(state: GameState, count: int, strategy: str, rng: random.Random) -> dict:
    """Version B: Hunt success always requires meeting the event Threat.

    - Score >= Threat: successful hunt, gain the score as food.
    - Score < Threat and no skulls: hunt fails, gain no food, no death.
    - Score < Threat and at least one skull: critical failure, lose 1 person.
    """
    if count <= 0:
        return {
            "rolls": [],
            "score": 0,
            "skulls": 0,
            "success": True,
            "death": False,
    }

    rolls = []
    score = 0
    skulls = 0
    state.total_hunts += 1

    for _ in range(count):
        face, value = roll_hunt_die(rng)
        rolls.append(face)
        score += value
        if face == "skull":
            skulls += 1

    score += event_mod(state, "hunt_modifier")
    threat = int(state.current_event["threat"])
    success = score >= threat
    death = False

    if success:
        state.food += score
        state.successful_hunts += 1
    elif skulls > 0:
        state.people = max(state.people - 1, 0)
        state.hunt_failures += 1
        state.hunt_deaths += 1
        death = True
    else:
        state.hunt_failures += 1

    return {
        "rolls": rolls,
        "score": score,
        "skulls": skulls,
        "success": success,
        "death": death,
    }


def valid_allocation(allocation: dict[str, int], available_workers: int) -> bool:
    if set(allocation) - VALID_CATEGORIES:
        return False
    if sum(allocation.values()) != available_workers:
        return False
    if allocation.get("K", 0) % 2 != 0:
        return False
    if any(count < 0 for count in allocation.values()):
        return False
    return True


def prepare_turn(state: GameState, rng: random.Random, strategy: str) -> dict:
    """Apply start-of-turn effects and return information needed for allocation."""
    if state.people <= 0:
        return {"game_over": True, "available_workers": 0}

    state.current_event = draw_event(state.turn, rng)

    # Prayer can ignore event effects, but never the Hunt threat.
    prayer_used = False
    if state.prayer_tokens >= 2:
        harmful = (
            event_mod(state, "food_modifier") < 0
            or event_mod(state, "food_loss") > 0
            or event_mod(state, "hunt_modifier") < 0
            or event_mod(state, "kinship_modifier") > 0
        )
        very_bad = state.current_event["threat"] >= 12
        use = False
        if strategy in {"worship", "balanced", "food"} and (harmful or very_bad):
            use = True
        elif strategy == "random" and (harmful or very_bad) and rng.random() < 0.5:
            use = True
        if use:
            state.prayer_tokens -= 2
            state.prayer_spent += 2
            state.events_ignored += 1
            state.current_event["ignored"] = True
            prayer_used = True

    food_loss = event_mod(state, "food_loss")
    if food_loss > 0:
        state.food = max(state.food - food_loss, 0)

    completed = resolve_kinship_projects(state)
    available_workers = state.people - active_kinship_workers(state)

    return {
        "event": state.current_event["name"],
        "threat": state.current_event["threat"],
        "food_loss": food_loss,
        "prayer_used": prayer_used,
        "kinship_completed": completed,
        "available_workers": available_workers,
        "game_over": available_workers < 0 or state.people <= 0,
    }


def run_turn(
    state: GameState,
    allocation: dict[str, int],
    rng: random.Random,
    strategy: str = "balanced",
    prepared: dict | None = None,
) -> dict:
    """Resolve one complete turn using a validated allocation."""
    if state.people <= 0:
        return {"turn": state.turn, "ended": True}

    if prepared is None:
        prepared = prepare_turn(state, rng, strategy)

    available_workers = int(prepared["available_workers"])
    if prepared.get("game_over"):
        return {
            "turn": state.turn,
            "event": state.current_event["name"] if state.current_event else "None",
            "available_workers": available_workers,
            "game_over": True,
            "cause": "kinship_overcommitment" if available_workers < 0 else "population_zero",
            "prayer_used": prepared.get("prayer_used", False),
            "kinship_completed": prepared.get("kinship_completed", 0),
        }

    if not valid_allocation(allocation, available_workers):
        raise ValueError(
            f"Invalid allocation {allocation} for {available_workers} available workers"
        )

    # Start Kinship projects. A current prototype project is represented as 3 here,
    # matching the existing playable file's timing convention.
    kinship_count = allocation.get("K", 0)
    new_projects = kinship_count // 2
    state.kinship_projects.extend([3] * new_projects)
    state.kinship_started += new_projects

    # Hunt
    hunt_data = resolve_hunt(state, allocation.get("H", 0), strategy, rng)

    # Food
    food_results = []
    for _ in range(allocation.get("F", 0)):
        food_results.append(apply_food_roll(state, roll_die(rng)))

    # Technology and Worship
    for _ in range(allocation.get("T", 0)):
        roll = roll_die(rng)
        effect, value = TECHNOLOGY_REFERENCE[roll]
        if effect == "item":
            state.tech_tiles.append(value)
            check_technology_completion_sim(state, strategy)

    for _ in range(allocation.get("W", 0)):
        roll = roll_die(rng)
        resolve_worship_roll(state, roll, strategy, rng)
        if state.people <= 0:
            break

    # Feed everyone in the tribe, including Kinship workers.
    fed = state.food >= state.people
    lost_to_food = False
    if fed:
        state.food -= state.people
    else:
        state.people = max(state.people - 1, 0)
        state.food = 0
        lost_to_food = True

    state.turn += 1
    state.total_turns += 1
    state.max_people = max(state.max_people, state.people)
    state.max_food = max(state.max_food, state.food)

    game_over = state.people <= 0
    completed = int(prepared.get("kinship_completed", 0))
    prayer_used = bool(prepared.get("prayer_used", False))
    food_loss = int(prepared.get("food_loss", 0))

    return {
        "turn": state.turn - 1,
        "event": state.current_event["name"],
        "threat": state.current_event["threat"],
        "allocation": allocation.copy(),
        "available_workers": available_workers,
        "kinship_started": new_projects,
        "kinship_completed": completed,
        "hunt_count": allocation.get("H", 0),
        "hunt_score": hunt_data["score"],
        "hunt_skulls": hunt_data["skulls"],
        "hunt_success": hunt_data["success"],
        "hunt_death": hunt_data["death"],
        "food_rolls": food_results,
        "food_gained": sum(food_results),
        "food_loss": food_loss,
        "prayer_used": prayer_used,
        "fed": fed,
        "lost_to_food": lost_to_food,
        "people_end": state.people,
        "food_end": state.food,
        "game_over": game_over,
    }


# -----------------------------
# Strategy helpers
# -----------------------------


def _allocate_from_priority(available: int, priorities: list[tuple[str, int]]) -> dict[str, int]:
    allocation: dict[str, int] = {}
    remaining = available
    for category, amount in priorities:
        if remaining <= 0:
            break
        if category == "K":
            amount = min(amount, remaining - (remaining % 2))
            amount -= amount % 2
        else:
            amount = min(amount, remaining)
        if amount > 0:
            allocation[category] = amount
            remaining -= amount
    if remaining > 0:
        allocation["F"] = allocation.get("F", 0) + remaining
    return allocation


def random_allocation(state: GameState, rng: random.Random) -> dict[str, int]:
    available = state.people - active_kinship_workers(state)
    allocation = {c: 0 for c in VALID_CATEGORIES}
    remaining = available

    categories = ["F", "H", "T", "W", "K"]
    rng.shuffle(categories)
    while remaining > 0:
        category = rng.choice(["F", "H", "T", "W"] + (["K"] if remaining >= 2 else []))
        if category == "K":
            allocation["K"] += 2
            remaining -= 2
        else:
            allocation[category] += 1
            remaining -= 1
    return {k: v for k, v in allocation.items() if v > 0}


def strategy_allocation(state: GameState, rng: random.Random, name: str) -> dict[str, int]:
    available = state.people - active_kinship_workers(state)
    if available < 0:
        return {}

    if name == "random":
        return random_allocation(state, rng)

    # Heuristics are intentionally simple. They are baselines, not optimal solvers.
    event = state.current_event or {}
    food_need = max(0, state.people - state.food)
    hunt_bonus = int(event.get("hunt_modifier", 0))
    hunt_threat = int(event.get("threat", 5))

    if name == "food":
        food_workers = min(available, max(1, food_need + 1))
        return _allocate_from_priority(available, [("F", food_workers), ("H", available - food_workers)])

    if name == "hunt":
        hunt_workers = available if hunt_bonus >= 0 and hunt_threat <= 9 else max(1, available // 2)
        if food_need > 0:
            return _allocate_from_priority(available, [("F", min(food_need, available)), ("H", hunt_workers)])
        return _allocate_from_priority(available, [("H", hunt_workers), ("F", available - hunt_workers)])

    if name == "kinship":
        k = available if available % 2 == 0 else max(0, available - 1)
        if k >= 2:
            return _allocate_from_priority(available, [("K", k), ("F", available - k)])
        return {"F": available} if available else {}

    if name == "technology":
        tech_workers = max(1, available // 2) if available >= 2 else 0
        return _allocate_from_priority(available, [("T", tech_workers), ("F", available - tech_workers)])

    if name == "worship":
        worship_workers = max(1, available // 2) if available >= 1 else 0
        return _allocate_from_priority(available, [("W", worship_workers), ("F", available - worship_workers)])

    # balanced/default
    if available == 0:
        return {}
    if food_need > 0:
        food_workers = min(available, max(1, food_need))
        remaining = available - food_workers
        priorities = [("F", food_workers)]
        if remaining >= 2:
            priorities.append(("K", 2))
            remaining -= 2
        if remaining > 0:
            priorities.append(("T", 1))
            remaining -= 1
        if remaining > 0:
            priorities.append(("H", remaining))
        return _allocate_from_priority(available, priorities)
    return _allocate_from_priority(
        available,
        [("K", 2 if available >= 2 else 0), ("T", max(0, available - 2)), ("F", 1)],
    )


def run_game(
    strategy: str = "balanced",
    seed: Optional[int] = None,
    max_turns: int = 20,
) -> tuple[GameState, list[dict]]:
    rng = random.Random(seed)
    state = GameState()
    turn_rows: list[dict] = []

    for _ in range(max_turns):
        if state.people <= 0:
            break

        prepared = prepare_turn(state, rng, strategy)
        if prepared.get("game_over"):
            turn_rows.append({
                "turn": state.turn,
                "event": state.current_event["name"] if state.current_event else "None",
                "available_workers": prepared.get("available_workers", 0),
                "game_over": True,
                "cause": "kinship_overcommitment" if prepared.get("available_workers", 0) < 0 else "population_zero",
                "prayer_used": prepared.get("prayer_used", False),
                "kinship_completed": prepared.get("kinship_completed", 0),
            })
            break

        allocation = strategy_allocation(state, rng, strategy)
        result = run_turn(state, allocation, rng, strategy=strategy, prepared=prepared)
        turn_rows.append(result)

        if result.get("game_over") or state.people <= 0:
            break

    return state, turn_rows
