#Playtest prototype for the food + dice loop.
# basic rules:
# - Start with 5 people and 7 food.
# - Each 'person' is 1 die roll per turn, allocated to one of the following actions: hunt (H), gather (F), invest in technology (T), 
#   [ignore for now]worship(W) , or work on kinship projects (K).
# - After rolling, you must have 1 food per person.
# - If you do not have enough food, you lose 1 person max per turn and your food is wiped to 0.
# Events: each turn, a random event is drawn that may affect the threat level of hunts, the amount of food gained from gathering, or other modifiers.
# - gather rolls are made with a standard d6 (faces: 1,1,2,2,2, and 3) The amount of food gained is based on the roll and any modifiers from technology or events.
# - hunt rolls are made with a special die that has 2 skulls and 4 numbered faces (2-5). If you roll any skulls, you must meet the threat level of the current event to succeed. 
#       If you fail, you lose 1 person. If you succeed, you gain food equal to the sum of the numbered faces rolled.
# - technology rolls are made with a standard d6. Each face corresponds to a specific technology piece (stick, rope, rock). 
#       If you collect all three pieces, you can choose one permanent die-face upgrade for any category (F, W, or H).
# - kinship projects require 2 people to start and take 2 turns to complete, meaning those 2 people will be unavailable for the duration of the project.
#       Each completed project adds 1 person to your tribe.

from __future__ import annotations

from dataclasses import dataclass
import nt
import random

def game_input(prompt: str) -> str:
    answer = input(prompt).strip()

    if answer.lower() == "q":
        print("\nGame ended by player.")
        raise SystemExit

    return answer
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
    {
        "name": "Mild Winter",
        "description": "Food production is reduced by 1 this turn.",
        "threat": 5,
        "food_modifier": -1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Animal Migration",
        "description": "The animal migration makes it easier to hunt. Add 2 to your total Hunt score.",
        "threat": 6,
        "food_modifier": 0,
        "hunt_modifier": 2,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Calm Skies",
        "description": "Everything is going smoothly.",
        "threat": 5,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Rocky Terrain",
        "description": "The mountainous terrain makes hunting more difficult. Subtract 3 from your total Hunt score.",
        "threat": 3,
        "food_modifier": 0,
        "hunt_modifier": -3,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Local Thieves",
        "description": "Thieves steal 3 food from your supplies.",
        "threat": 5,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 3,
        "kinship_modifier": 0,
        "prayer_modifier": 0
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
        "prayer_modifier": 0
    },
    {
        "name": "Predator Activity",
        "description": "Food production is reduced by 2, and the Hunt score is reduced by 2.",
        "threat": 7,
        "food_modifier": -2,
        "hunt_modifier": -2,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Fertile Season",
        "description": "Food production increases by 1 this turn.",
        "threat": 9,
        "food_modifier": 1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Obsidian Deposit",
        "description": "Your tribe finds valuable materials. Gain 1 additional Prayer Token this turn.",
        "threat": 7,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 1
    },
    {
        "name": "Spiritual Awakening",
        "description": "Your tribe feels unusually connected to the spirits. Gain 1 additional Prayer Token this turn.",
        "threat": 10,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 1
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
        "prayer_modifier": 0
    },
    {
        "name": "Mammoth Herd",
        "description": "A massive herd has appeared. Add 2 to your total Hunt score.",
        "threat": 15,
        "food_modifier": 0,
        "hunt_modifier": 2,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Epidemic",
        "description": "The tribe is weakened. Food production is reduced by 1 this turn.",
        "threat": 13,
        "food_modifier": -1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Great Flood",
        "description": "Floodwaters damage food supplies. Food production is reduced by 1 this turn.",
        "threat": 12,
        "food_modifier": -1,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 0
    },
    {
        "name": "Eclipse",
        "description": "The tribe receives a sign from the spirits. Gain 1 additional Prayer Token this turn.",
        "threat": 14,
        "food_modifier": 0,
        "hunt_modifier": 0,
        "food_loss": 0,
        "kinship_modifier": 0,
        "prayer_modifier": 1
    },
]

@dataclass
class GameState:
    people: int = 5
    food: int = 7
    turn: int = 1
    prayer_tokens: int = 0
    kinship_projects: list[str] = None
    tech_tiles: list[str] = None
    tech_upgrades: dict[str, dict[int, int]] = None
    current_event: dict | None = None
    def __post_init__(self):
        if self.kinship_projects is None:
            self.kinship_projects = []
        if self.tech_tiles is None:
            self.tech_tiles = []
        if self.tech_upgrades is None:
            self.tech_upgrades = {
                "F": {},
                "W": {},
                "T": {},
            }

def event_mod(state: GameState, key: str) -> int:
    if state.current_event is None:
        return 0
    if state.current_event.get("ignored", False):
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
    if turn <= 7 and turn > 1:
        return random.choice(EVENTS_T1)
    elif turn <= 14:
        return random.choice(EVENTS_T2)
    else:
        return random.choice(EVENTS_T3)
def tech_bonus(state: GameState, category: str, roll: int) -> int:

    return state.tech_upgrades.get(category, {}).get(roll, 0)   
def resolve_sacrifice(state: GameState) -> None:
    print("\nSACRIFICE REQUIRED")
    print("1. +10 food")
    print("2. 1 free Technology upgrade")
    print("3. Immediately finish all Kinship projects")

    while True:
        choice = game_input("Choose 1, 2, or 3: ")

        if choice == "1":
            state.people -= 1
            state.food += 10
            print("The worshipper was sacrificed. +10 food.")
            break

        elif choice == "2":
            state.people -= 1
            print("The worshipper was sacrificed. You gain 1 free Technology upgrade.")
            # Technology upgrade logic later.
            break

        elif choice == "3":
            state.people -= 1

            completed = len(state.kinship_projects)
            state.kinship_projects = []
            state.people += completed

            print("The worshipper was sacrificed.")
            print(f"{completed} Kinship project(s) finished -> +{completed} new people added to the tribe.")
            break

        else:
            print("Invalid choice. Enter 1, 2, or 3.")
def roll_category(state: GameState, category: str, roll: int) -> None:
    if category == "F" and roll in FOOD_REFERENCE:
        value = FOOD_REFERENCE[roll]
        value += tech_bonus(state, "F", roll)
        value += event_mod(state, "food_modifier")
        value = max(value, 0)
        state.food += value

    elif category == "T":
        effect, value = TECHNOLOGY_REFERENCE[roll]

        if effect == "item":
            state.tech_tiles.append(value)
            print(f"    gained tech piece: {value}")    
            check_technology_completion(state)

    elif category == "W":
        effect, value = WORSHIP_REFERENCE[roll]

        if effect == "prayer":
            value += tech_bonus(state, "W", roll)
            state.prayer_tokens += value
            print(f"    gained {value} Prayer Token(s)")
        elif effect == "sacrifice":
            resolve_sacrifice(state) 

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
        print(f"{completed} kinship project(s) finished -> +{completed} new people added to the tribe.")
def check_technology_completion(state: GameState) -> None:
    required = {"stick", "rope", "rock"}

    if required.issubset(set(state.tech_tiles)):
        print("Technology complete! Choose one permanent die-face upgrade.")

        while True:
            category = game_input("Upgrade which category? (F, W, or T): ").upper()
            if category in {"F", "W", "T"}:
                break
            print("Invalid category. Choose F, W, or T.")

        while True:
            face_raw = game_input("Which die face to upgrade? (1-6): ")
            if face_raw in {"1", "2", "3", "4", "5", "6"}:
                face = int(face_raw)
                break
            print("Enter a number from 1 to 6.")

        # If you already have tech_upgrades in GameState, this applies the permanent upgrade.
        state.tech_upgrades[category][face] = state.tech_upgrades[category].get(face, 0) + 1

        # Wipe all tech pieces after using the set
        state.tech_tiles = []

        print(f"Upgraded {category} face {face}. Technology materials reset to 0.")
def play_turn(state: GameState) -> None:

    print(f"\nTurn {state.turn}")
    state.current_event = draw_event(state.turn)
    print(f"\nEVENT: {state.current_event['name']}")
    print(f"Threat: {state.current_event['threat']}")
    print(state.current_event["description"])

    if state.prayer_tokens >= 2:
        use_prayer = game_input(
            f"You have {state.prayer_tokens} Prayer Tokens. "
            "Spend 2 to ignore this event? type y or n: "
        ).strip().lower()

        while True: 
            if use_prayer == "y":
                state.prayer_tokens -= 2
                state.current_event["ignored"] = True
                print("Your prayers have been answered. The event has been ignored.")
                break
            elif use_prayer == "n":
                print("No time for prayers, perhaps another day")
                break
            else:
                print("The gods are displeased with your indecision. Please choose y or n.")



    food_loss = event_mod(state, "food_loss")
    if food_loss > 0:
        state.food = max(state.food - food_loss, 0)
        print(f"{food_loss} food was lost.")
    resolve_kinship_projects(state)

    print(f"Start of turn: {state.people} people, {state.food} food")
    available_workers = state.people - active_kinship_workers(state)

    while True:
        raw = game_input(
            f"Assign {available_workers} available people (example: 1F 2K 1H 1T 1W): "
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
    state.kinship_projects.extend([2] * new_kinship_projects)

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

    food_count = allocation.get("F", 0)
    if food_count > 0:
        food_faces = []
        food_results = []

        for _ in range(food_count):
            roll = roll_die()

            gain = FOOD_REFERENCE[roll]
            gain += tech_bonus(state, "F", roll)
            gain += event_mod(state, "food_modifier")
            gain = max(gain, 0)

            food_faces.append(roll)
            food_results.append(gain)

            state.food += gain

        food_gained = sum(food_results)

        print(
            f"Food rolls: {food_faces} -> {food_results} "
            f"= {food_gained} food gained"
        )
    for category, count in allocation.items():

        if category not in {"F","K", "H", "T", "W"}:
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



    print(f"End of turn: {state.people} people, {available_workers} available.")
    if state.prayer_tokens > 0:
        print(f"Prayer tokens: {state.prayer_tokens}")
    if state.kinship_projects:
        print(f"Kinship projects active: {len(state.kinship_projects)}")
        print(f"Kinship timers: {state.kinship_projects}")
    if state.tech_tiles:
        print(f"Tech tiles: {state.tech_tiles}")

    state.turn += 1
   
def main() -> None:
    state = GameState()
    print("Welcome to Kinship!")
    print("Press Enter to play a turn, or type q to quit.\n")

    while state.people > 0:
        command = game_input("Next turn? ")
        play_turn(state)

    print("\nGame over.")
    print(f"Final state: {state.people} people, {state.food} food after turn {state.turn - 1}")


if __name__ == "__main__":
    main()