# Kinship rules:
# - Start with 5 people and 7 food.
# - Each 'person' is 1 die roll per turn, allocated to one of the following actions: hunt (H), gather (F), invest in technology (T), 
#   Worship (W) , or work on kinship projects (K).
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

#github command: git add .
#git commit -m "Updated worship and game input"
#git push

from __future__ import annotations

from dataclasses import dataclass
import random

def game_input(prompt: str) -> str:
    answer = input(prompt).strip()

    if answer.lower() == "q":
        print("\n game quit.")
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
    kinship_projects: list[int] = None
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
    elif turn == 1:
        return {
            "name": "First Turn",
            "description": "No event on the first turn.",
            "threat": 5,
            "food_modifier": 0,
            "hunt_modifier": 0,
            "food_loss": 0,
            "kinship_modifier": 0,
            "prayer_modifier": 0
        }
    elif turn <= 14:
        return random.choice(EVENTS_T2)
    else:
        return random.choice(EVENTS_T3)
def tech_bonus(state: GameState, category: str, roll: int) -> int:

    return state.tech_upgrades.get(category, {}).get(roll, 0)   
def choose_technology_upgrade(state: GameState) -> None:
    print("\nChoose a permanent die-face upgrade.")
    print("F = Food")
    print("W = Worship")

    while True:
        category = game_input("Choose category (F/W): ").upper()

        if category in {"F", "W"}:
            break

        print("Invalid category. Choose F or W.")

    while True:
        face_input = game_input("Choose die face to upgrade (1-6): ")

        if face_input in {"1", "2", "3", "4", "5", "6"}:
            face = int(face_input)
            break

        print("Invalid face. Choose 1-6.")

    old_bonus = state.tech_upgrades[category].get(face, 0)
    state.tech_upgrades[category][face] = old_bonus + 1

    if category == "F":
        old_result = FOOD_REFERENCE[face] + old_bonus
        new_result = FOOD_REFERENCE[face] + old_bonus + 1
        print(f"Food face {face}: {old_result} -> {new_result}")

    elif category == "W":
        effect, base_value = WORSHIP_REFERENCE[face]
        old_result = base_value + old_bonus
        new_result = base_value + old_bonus + 1
        print(f"Worship face {face}: {effect} {old_result} -> {new_result}")
def resolve_sacrifice(state: GameState, roll: int) -> None:
    upgraded = tech_bonus(state, "W", roll) > 0

    if upgraded:
        print("\nDEVOUT SACRIFICE")
        print("This sacrifice has been enhanced by Technology.")
        print("1. +20 food")
        print("2. 2 free Technology upgrades")
        print("3. Net 1 new tribe member")
    else:
        print("\nSACRIFICE REQUIRED")
        print("1. +10 food")
        print("2. 1 free Technology upgrade")
        print("3. all Kinship projects completed")

    while True:
        choice = game_input("Choose 1, 2, or 3: ")

        if choice == "1":
            state.people -= 1

            if upgraded:
                state.food += 20
                print("The devout worshipper was sacrificed. +20 food.")
            else:
                state.food += 10
                print("The worshipper was sacrificed. +10 food.")

            break

        elif choice == "2":
            state.people -= 1

            if upgraded:
                print("The devout worshipper was sacrificed. You gain 2 free Technology upgrades.")
                choose_technology_upgrade(state)
                choose_technology_upgrade(state)
            else:
                print("The worshipper was sacrificed. You gain 1 free Technology upgrade.")
                choose_technology_upgrade(state)

            break

        elif choice == "3":
            state.people -= 1

            if upgraded: 
                state.people += 2
                print("The devout worshipper was sacrificed. 2 new tribe members join.")
        
            else:
                completed = len(state.kinship_projects)
                state.kinship_projects = []
                state.people += completed

                print("The worshipper was sacrificed.")
                print(f"All Kinship projects completed -> +{completed} people.")
        

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
            
            value += event_mod(state, "prayer_modifier")
            state.prayer_tokens += value
            print(f"    gained {value} Prayer Token(s)")
        elif effect == "sacrifice":
            resolve_sacrifice(state, roll) 
            if state.people <= 0:
                return

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

    if not required.issubset(set(state.tech_tiles)):
        return

    print("\nTechnology complete!")
    choose_technology_upgrade(state)

    state.tech_tiles = []
    print("All technology materials were consumed.")
    state.tech_tiles = []

def play_turn(state: GameState) -> None:

    print(f"\nTurn {state.turn}")
    state.current_event = draw_event(state.turn)
    print(f"\nEVENT: {state.current_event['name']}")
    print(f"Threat: {state.current_event['threat']}")
    print(state.current_event["description"])

    if state.prayer_tokens >= 2:

        attempts = 0

        while attempts < 3:
            use_prayer = game_input(
                f"You have {state.prayer_tokens} Prayer Tokens. "
                "Spend 2 to ignore this event? Type y or n: "
            ).lower()

            if use_prayer == "y":
                state.prayer_tokens -= 2
                state.current_event["ignored"] = True
                print("Your prayers have been answered. The event has been ignored.")
                break

            elif use_prayer == "n":
                print("No time for prayers, perhaps another day.")
                break

            else:
                attempts += 1
                print("The gods are displeased with your indecision. Please choose y or n.")

        else:
            print("Too many invalid answers. Prayer will not be used this turn.")



    food_loss = event_mod(state, "food_loss")
    if food_loss > 0:
        state.food = max(state.food - food_loss, 0)
        print(f"{food_loss} food was lost.")
    resolve_kinship_projects(state)

    print(f"Start of turn: {state.people} people, {state.food} food")
    available_workers = state.people - active_kinship_workers(state)
    if available_workers < 0:
        print("\nYour tribe has collapsed.")
        return
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
        valid_categories = {"F", "K", "H", "T", "W"}
        invalid = [c for c in allocation if c not in valid_categories]

        if invalid:
            print(f"Invalid category: {', '.join(invalid)}")
            print("Valid categories are: F, K, H, T, W.")
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
                if state.people <= 0:
                    return
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

        if category in {"F", "K", "H"}:
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
        if state.people <= 0:
            return


    print(f"End of turn: {state.people} people")
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
    print("Welcome to Kinship! \n")
    

    while state.people > 0:
        if state.turn == 1: 
            command = game_input("Press Enter to start the game, or type q to quit: ")
        else:
            command = game_input("Next turn? ")
        
        play_turn(state)

    print("\nGame over.")
    print(f"Final state: {state.people} people, {state.food} food after turn {state.turn - 1}")


if __name__ == "__main__":
    main()