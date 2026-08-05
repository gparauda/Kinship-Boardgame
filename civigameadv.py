#Playtest prototype for the food + dice loop.
# basic rules:
# - Start with 5 people and 7 food.
# - Each 'person' is 1 die roll per turn.
# - Each die result produces food based on the reference sheet
# - After rolling, you must spend 1 food per person.
# - If you do not have enough food, you lose 1 person max per turn and your food is wiped to 0.
from __future__ import annotations

from dataclasses import dataclass
import random
FOOD_REFERENCE = {
     1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 2,
    6: 3
}
HUNT_FACES = ["skull", "skull", 2, 3, 4, 5]

def roll_hunt_die() -> tuple[str, int]:
    face = random.choice(HUNT_FACES)
    value = 0 if face == "skull" else face
    return face, value

def hunt_threshold(turn: int) -> int:
    return max(1, (turn + 1) // 2)
TECHNOLOGY_REFERENCE = {
    1: ("item", "stick"),
    2: ("item", "rope"),
    3: ("item", "rock"),
    4: ("item", "stick"),
    5: ("item", "rope"),
    6: ("item", "rock")
}
WORSHIP_REFERENCE = {
     1: ("sacrifice", 1),
    2: ("sacrifice", 1),
    3: ("prayer", 1),
    4: ("prayer", 1),
    5: ("prayer", 1),
    6: ("prayer", 1)
}
EVENTS_T1 = [
    {"name": "Mild Winter", "threat": 5, "food_modifier": -1, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Animal Migration", "threat": 6, "food_modifier": 0, "hunt_modifier": 2, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Calm Skies", "threat": 5, "food_modifier": 0, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Rocky Terrain", "threat": 3, "food_modifier": 0, "hunt_modifier": -3, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Local Thieves", "threat": 5, "food_modifier": 0, "hunt_modifier": 0, "food_loss": 3, "kinship_modifier": 0, "prayer_modifier": 0},
]

EVENTS_T2 = [
    {"name": "Harsh Winter", "threat": 8, "food_modifier": -2, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Predator Activity", "threat": 7, "food_modifier": -2, "hunt_modifier": -2, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Fertile Season", "threat": 9, "food_modifier": 1, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Obsidian Deposit", "threat": 7, "food_modifier": 0, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 1},
    {"name": "Spiritual Awakening", "threat": 10, "food_modifier": 0, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 1},
]

EVENTS_T3 = [
    {"name": "Endless Winter", "threat": 13, "food_modifier": -2, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Mammoth Herd", "threat": 15, "food_modifier": 0, "hunt_modifier": 2, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Epidemic", "threat": 13, "food_modifier": -1, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Great Flood", "threat": 12, "food_modifier": -1, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 0},
    {"name": "Eclipse", "threat": 14, "food_modifier": 0, "hunt_modifier": 0, "food_loss": 0, "kinship_modifier": 0, "prayer_modifier": 1},
]
@dataclass
class GameState:
    people: int = 5
    food: int = 7
    turn: int = 1
    prayer_tokens: int = 0
    kinship_projects: list[str] = None
    tech_tiles: list[str] = None
    sacrifice_tokens: int = 0
    current_event: dict | None = None
    def __post_init__(self):
        if self.kinship_projects is None:
            self.kinship_projects = []
        if self.tech_tiles is None:
            self.tech_tiles = []

def event_mod(state: GameState, key: str) -> int:
    if state.current_event is None:
        return 0
    return state.current_event.get(key, 0)
def roll_die() -> int:
    return random.randint(1, 6)

def parse_allocation(text: str) -> dict[str, int]:
    allocation: dict[str, int] = {}
    parts = text.split()

    for part in parts:
        number = ""
        letter = ""

        for ch in part:
            if ch.isdigit():
                number += ch
            else:
                letter += ch

        if not number or not letter:
            raise ValueError(f"Bad allocation chunk: {part}")
        if len(letter) != 1:
            raise ValueError(f"Use one-letter codes only: {part}")

        allocation[letter] = allocation.get(letter, 0) + int(number)

    return allocation

def draw_event(turn: int) -> dict:
    if turn <= 7:
        return random.choice(EVENTS_T1)
    elif turn <= 14:
        return random.choice(EVENTS_T2)
    else:
        return random.choice(EVENTS_T3)
    
def roll_category(state: GameState, category: str, roll: int) -> None:
    if category == "F" and roll in FOOD_REFERENCE:
        value = FOOD_REFERENCE[roll]
        value += event_mod(state, "food_modifier")
        value = max(value, 0)
        state.food += value

    elif category == "T":
        effect, value = TECHNOLOGY_REFERENCE[roll]

        if effect == "item":
            state.tech_tiles.append(value)

    elif category == "W":
        effect, value = WORSHIP_REFERENCE[roll]

        if effect == "prayer":
            state.prayer_tokens += value

        elif effect == "sacrifice":
            state.sacrifice_tokens += value
def active_kinship_workers(state: GameState) -> int:
    return 2 * len(state.kinship_projects)

def resolve_kinship_projects(state: GameState) -> None:
    still_active = []
    completed = 0

    for turns_left in state.kinship_projects:
        turns_left -= 1
        if turns_left <= 0:
            completed += 1
        else:
            still_active.append(turns_left)

    state.kinship_projects = still_active
    state.people += completed

    if completed > 0:
        print(f"{completed} kinship project(s) finished -> +{completed} people")
def play_turn(state: GameState) -> None:

    print(f"\nTurn {state.turn}")
    state.current_event = draw_event(state.turn)
    print(f"Event: {state.current_event['name']}  |  Threat: {state.current_event['threat']}")

    food_loss = state.current_event.get("food_loss", 0)
    if food_loss > 0:
        state.food = max(state.food - food_loss, 0)
        print(f"{food_loss} food is lost before allocation.")
    resolve_kinship_projects(state)

    print(f"Start of turn: {state.people} people, {state.food} food")
    available_workers = state.people - active_kinship_workers(state)

    while True:
        raw = input(
            f"Assign {available_workers} available people (example: 1F 2K 1r 1T): "
        ).strip()

        try:
            allocation = parse_allocation(raw)
        except ValueError as err:
            print(err)
            continue

        total_assigned = sum(allocation.values())
        if total_assigned != available_workers:
            print(
                f"You must assign exactly {available_workers} people. "
                f"You assigned {total_assigned}."
            )
            continue
        valid_categories = {"F", "K", "H", "r", "T", "W"}
        invalid = [c for c in allocation if c not in valid_categories]

        if invalid:
            print(f"Invalid category: {', '.join(invalid)}")
            print("Valid categories are: F, K, H, r, T, W.")
            continue

        if allocation.get("K", 0) % 2 != 0:
            print("Kinship must be assigned in groups of 2 people.")
            continue
        break
    kinship_count = allocation.get("K", 0)
    new_kinship_projects = kinship_count // 2
    state.kinship_projects.extend([3] * new_kinship_projects)

    if new_kinship_projects > 0:
        print(f"Started {new_kinship_projects} kinship project(s).")

    hunt_count = allocation.get("H", 0)
    if hunt_count > 0:
        hunt_faces = []
        hunt_score = 0
        skulls = 0

        for _ in range(hunt_count):
            face, value = roll_hunt_die()
            hunt_faces.append(face)
            hunt_score += value
            
            if face == "skull":
                skulls += 1
        hunt_score += event_mod(state, "hunt_modifier")

        print(f"H: {hunt_count} dice")
        print(f"  hunt rolls: {hunt_faces}")
        print(f"  hunt score: {hunt_score}")

        if skulls > 0:
            print(f"  skull rolled, threat level is {state.current_event['threat']}")

            if hunt_score < state.current_event['threat']:
                state.people = max(state.people - 1, 0)
                print("  Critical failure! One person dies.")
            else:
                state.food += hunt_score
                print(f"  Dangerous hunt succeeds. You gain {hunt_score} food.")
        else:
            state.food += hunt_score
            print(f"  Hunt succeeds. You gain {hunt_score} food.")
    for category, count in allocation.items():
        if category not in {"F","K", "H", "r", "T", "W"}:
            print(f"Unknown category '{category}', skipped.")
            continue

        for _ in range(count):
            roll = roll_die()
            roll_category(state, category, roll)

    print(f"Food before feeding: {state.food}")

    if state.food >= state.people:
        state.food -= state.people
        print(f"Everyone was fed. Food left over: {state.food}")
    else:
        state.people = max(state.people - 1, 0)
        state.food = 0
        print("Not enough food. You lose 1 person and food is wiped to 0.")



    print(f"End of turn: {state.people} people, {state.food} food")
    print(f"Prayer tokens: {state.prayer_tokens}")
    #print(f"Kinship projects active: {len(state.kinship_projects)}")
    print(f"Kinship timers: {state.kinship_projects}")
    print(f"Tech tiles: {state.tech_tiles}")

    state.turn += 1
   
def main() -> None:
    state = GameState()
    print("Food and dice prototype")
    print("Press Enter to play a turn, or type q to quit.\n")

    while state.people > 0:
        command = input("Next turn? ").strip().lower()
        if command == "q":
            break

        play_turn(state)

    print("\nGame over.")
    print(f"Final state: {state.people} people, {state.food} food after turn {state.turn - 1}")


if __name__ == "__main__":
    main()