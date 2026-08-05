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
FOOD_REFERENCE = {}
MEDICINE_REFERENCE = {}
RAID_BIG_REFERENCE = {}
RAID_SMALL_REFERENCE = {}
TECHNOLOGY_REFERENCE = {}
WORSHIP_REFERENCE = {}

@dataclass
class GameState:
    people: int = 5
    food: int = 7
    turn: int = 1

def roll_die() -> int:
    return random.randint(1, 6)

def food_production(roll: int) -> int:
    return FOOD_REFERENCE[roll]

def play_turn(state: GameState) -> None:
    print(f"Turn {state.turn}")
    print(f"Start of turn: {state.people} people, {state.food} food")

    rolls = []
    gained_food = 0

    for _ in range(state.people):
        r = roll_die()
        rolls.append(r)
        gained_food += food_production(r)    

    print(f"Dice rolled: {rolls}")
    print(f"Food gained from rolls: {gained_food}")

    state.food += gained_food
    print(f"Food before feeding: {state.food}")

    if state.food >= state.people:
        state.food -= state.people
        print(f"Everyone was fed. Food left over: {state.food}")
    else:
        state.people = max(state.people - 1, 0)
        state.food = 0
        print("Not enough food. You lose 1 person and food is wiped to 0.")
    
    print(f"End of turn: {state.people} people, {state.food} food")
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