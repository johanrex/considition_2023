import os
import time
import itertools
import json
from database import Database
from starterkit.scoring import calculateScore
from starterkit.api import getGeneralData, getMapData, submit

from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
)
from dotenv import load_dotenv

# GENETIC ALGORITHM
import genetic


# def get_next_solution():
#     [print(x) for x in list(itertools.combinations_with_replacement(range(6), 3))]


def write_response_to_file(file_name, reponse):
    # get directory name from file_name
    dir_name = os.path.dirname(file_name)
    os.makedirs(dir_name, exist_ok=True)

    s = json.dumps(reponse, indent=4)

    with open(file_name, "w") as f:
        f.write(s)


def solution_from_int_list(individual: list[int], location_names: list[str]):
    individual_idx = 0
    solution = {LK.locations: {}}
    for location_name in location_names:
        if individual[individual_idx] == 0 and individual[individual_idx + 1] == 0:
            individual_idx += 2
        else:
            solution[LK.locations][location_name] = {
                LK.f9100Count: individual[individual_idx],
                LK.f3100Count: individual[individual_idx + 1],
            }
            individual_idx += 2

    return solution


def int_list_from_solution(
    solution: dict[str, dict[str, int]], location_names: list[str]
):
    genome = []

    for location_name in location_names:
        if location_name in solution[LK.locations]:
            genome.append(solution[LK.locations][location_name][LK.f9100Count])
            genome.append(solution[LK.locations][location_name][LK.f3100Count])
        else:
            genome.append(0)
            genome.append(0)

    return genome


def fitness_callback(genome: list[int]):
    global map_data
    global general_data
    global location_names
    global best_score

    solution = solution_from_int_list(genome, location_names)
    score_obj = calculateScore(map_name, solution, map_data, general_data)
    score_val = score_obj[SK.gameScore][SK.total]

    if score_val > best_score:
        best_score = score_val
        print(f"New best score: {best_score}")
        print("Genome:", genome)

        db.insert(
            map_name,
            score_val,
            algorithm,
            json.dumps(solution),
        )

        # TODO make this smarter.
        # Submit in separate process
        # if time.time() - start_time > 1:
        #     scored_solution = submit(map_name, solution, api_key)
        #     print("Submitted to api:", scored_solution)

    return score_val


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]

general_data = getGeneralData()
# write_response_to_file(f"tmp/general_data.json", general_data)


start_time = time.time()

map_name = MN.vasteras
print(f"Using map name: {map_name}.")

map_data = getMapData(map_name, api_key)

location_names = [loc["locationName"] for loc in map_data["locations"].values()]

best_genome = None
genome_length = len(location_names * 2)
range_min = 0
range_max = 5

algorithm = "genetic"

db = Database()

best_genome = None
best_score, best_solution = db.get_best_solution(map_name)
if best_score is None and best_solution is None:
    best_score = float("-inf")
else:
    best_solution = json.loads(best_solution)
    best_genome = int_list_from_solution(best_solution, location_names)
    print(f"Loaded genome with score: {best_score}")
    print("Loaded genome:", best_genome)


best_genome = genetic.genetic_algorithm(
    population_size=10,
    num_generations=1_000_000,
    genome_length=genome_length,
    range_min=range_min,
    range_max=range_max,
    start_genome=best_genome,
    fitness_callback=fitness_callback,
)


# nr_of_solutions = 5 ^ (nr_of_locations * 2)

# TODO
# create local cache for api calls.
# create custom score function that only does the SK.total calculation. E.g. remove uuid.
# Put performance metrics in fitness_callback. E.g. evaluations per second.
# create a mqtt submit queue. Do separate process that ticks off the submits.

pass
