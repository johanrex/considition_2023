import os
import time
import itertools
import json
import pickle
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


def get_next_solution():
    [print(x) for x in list(itertools.combinations_with_replacement(range(6), 3))]


def list_all_maps():
    # let's hardcode them for now
    return [
        MN.stockholm,
        MN.goteborg,
        MN.malmo,
        MN.uppsala,
        MN.vasteras,
        MN.orebro,
        MN.london,
        MN.linkoping,
        MN.berlin,
    ]


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


def fitness_callback(individual: list[int]):
    global map_data
    global general_data
    global location_names
    global max_score

    solution = solution_from_int_list(individual, location_names)

    score_obj = calculateScore(map_name, solution, map_data, general_data)
    score_val = score_obj[SK.gameScore][SK.total]

    if score_val > max_score:
        max_score = score_val
        print(f"New max score: {max_score}")
        print("Genome:", individual)

        checkpoint = {"genome": individual, "score_val": score_val}
        pickle.dump(checkpoint, open(checkpoint_filename, "wb"))

        # TODO make this smarter.
        # Write to mqtt queue? Submit to api in separate process?
        if time.time() - start_time > 1:
            scored_solution = submit(map_name, solution, api_key)
            print("Submitted to api:", scored_solution)

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


genome_length = len(location_names * 2)
min_val = 0
max_val = 5


checkpoint_filename = f"tmp/genetic_{map_data[SK.mapName]}.pkl"
if os.path.exists(checkpoint_filename):
    checkpoint = pickle.load(open(checkpoint_filename, "rb"))
    max_score = checkpoint["score_val"]
    print(f"Loaded checkpoint with score: {max_score}")
else:
    max_score = float("-inf")

best_genome = genetic.genetic_algorithm(
    population_size=10,
    num_generations=100_000,
    individual_length=genome_length,
    min_val=min_val,
    max_val=max_val,
    start_individual=None,
    fitness_callback=fitness_callback,
)


# nr_of_solutions = 5 ^ (nr_of_locations * 2)

# TODO
# create local cache for api calls.
# create custom score function that only does the SK.total calculation. E.g. remove uuid.
# Put performance metrics in fitness_callback. E.g. evaluations per second.
# create a mqtt submit queue. Do separate process that ticks off the submits.

pass
