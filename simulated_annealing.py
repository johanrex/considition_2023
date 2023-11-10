import random
import math
import copy
import os
import sys
import json
from database import Database
from starterkit.scoring import calculateScore
from starterkit.api import getGeneralData, getMapData

from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
)
from dotenv import load_dotenv
import utils


class SimulatedAnnealing:
    @staticmethod
    def move(solution, min_bound, max_bound):
        """Create a new solution near the current one"""
        # This is problem-specific. Override
        new_solution = copy.deepcopy(solution)
        return new_solution

    @staticmethod
    def energy(solution):
        """Calculate the energy of a solution"""
        # This is problem-specific. Override
        pass

    @staticmethod
    def acceptance_probability(old_energy, new_energy, temperature):
        """Calculate the acceptance probability"""
        if old_energy < new_energy:
            return 1.0
        else:
            return math.exp((new_energy - old_energy) / temperature)

    @staticmethod
    def simulated_annealing(
        initial_solution,
        initial_temperature,
        cooling_rate,
        energy_func=energy,
        move_func=move,
    ):
        current_solution = initial_solution
        current_energy = energy_func(current_solution)
        temperature = initial_temperature

        while temperature > 1:
            new_solution = move_func(current_solution)
            new_energy = energy_func(new_solution)

            if (
                SimulatedAnnealing.acceptance_probability(
                    current_energy, new_energy, temperature
                )
                > random.random()
            ):
                current_solution = new_solution
                current_energy = new_energy

            temperature *= cooling_rate

        return current_solution


# ----------------------------------------------


def energy_wrapper(solution):
    global map_data
    global best_score
    global algorithm

    total_score = calculateScore(map_name, solution, map_data, general_data)[
        SK.gameScore
    ][SK.total]

    if total_score > best_score:
        best_score = total_score
        print(f"Map {map_name}. New best score: {best_score}")

        db.insert(
            map_name,
            best_score,
            algorithm,
            json.dumps(solution),
        )

    return total_score


def move_wrapper(solution):
    new_solution = copy.deepcopy(solution)

    utils.fill_missing_locations_inplace(new_solution, location_names)

    # Make the change
    ok = False
    while not ok:
        index = random.randint(0, len(solution) - 1)
        machine = LK.f9100Count if random.randint(0, 1) == 0 else LK.f3100Count
        delta = random.choice([-1, 1])

        location_name = f"location{index+1}"
        val = new_solution[LK.locations][location_name][machine] + delta

        if val < range_min or val > range_max:
            ok = False
        else:
            new_solution[LK.locations][location_name][machine] = val
            ok = True

    utils.prune_blanks_inplace(new_solution)

    global nr_of_moves
    nr_of_moves += 1

    return new_solution


# ----------------------------------------------


def create_simple_solution():
    solution = {LK.locations: {}}

    for location_name in location_names:
        solution[LK.locations][location_name] = {
            LK.f9100Count: random.randint(0, 5),
            LK.f3100Count: random.randint(0, 5),
        }

    utils.prune_blanks_inplace(solution)

    return solution


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]

general_data = getGeneralData()

if len(sys.argv) > 1:
    map_name = sys.argv[1]
else:
    map_name = MN.goteborg

print(f"Using map name: {map_name}.")

map_data = getMapData(map_name, api_key)

location_names = [loc["locationName"] for loc in map_data["locations"].values()]

range_min = 0
range_max = 5

algorithm = "simulated annealing"

db = Database()


# best_score, best_solution = db.get_best_solution(map_name)
# if best_score is None and best_solution is None:
#     best_score = float("-inf")
#     best_solution = None
# else:
#     best_solution = json.loads(best_solution)
#     print(f"Loaded solution with score: {best_score}")

initial_solution = create_simple_solution()
best_score = float("-inf")

nr_of_moves = 0
SimulatedAnnealing.simulated_annealing(
    initial_solution=initial_solution,
    initial_temperature=100000,
    cooling_rate=0.995,
    energy_func=energy_wrapper,
    move_func=move_wrapper,
)

print(f"Number of moves considered: {nr_of_moves}")
