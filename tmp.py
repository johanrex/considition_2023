import json
import os
import copy
import itertools
from dotenv import load_dotenv
from database import Database
from starterkit.scoring import calculateScore
from starterkit.api import getGeneralData, getMapData

from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
    GeneralKeys as GK,
)
import utils


def minus_one(location_names: list[str], best_score, best_solution):
    for location_name in location_names:
        nr_machines = 2
        for i in range(nr_machines):
            new_solution = copy.deepcopy(best_solution)

            if nr_machines == 0 and LK.f9100Count > 0:
                new_solution[LK.locations][location_name][LK.f9100Count] = -1
            elif nr_machines == 1 and LK.f3100Count > 0:
                new_solution[LK.locations][location_name][LK.f3100Count] = -1

            utils.prune_blanks_inplace(solution)
            new_score = utils.score_wrapper(
                map_name, new_solution, map_data, general_data
            )

            if new_score > best_score:
                best_score = new_score
                best_solution = new_solution

    return best_score, best_solution


def brute_force_locations(
    starting_score, starting_solution, location_cluster, map_data, general_data
):
    best_solution = starting_solution
    best_score = starting_score

    num_locations = len(location_cluster)
    iterable = itertools.product(
        range(range_min, range_max + 1), repeat=num_locations * 2
    )
    for tpl in iterable:
        current_solution = copy.deepcopy(starting_solution)
        for i, location_name in enumerate(location_cluster):
            current_solution[LK.locations][location_name] = {
                LK.f9100Count: tpl[i],
                LK.f3100Count: tpl[i + 1],
            }

        utils.prune_blanks_inplace(current_solution)
        current_score = utils.score_wrapper(
            map_name, current_solution, map_data, general_data
        )
        if current_score > best_score:
            best_score = current_score
            best_solution = current_solution

            print(f"New best score: {best_score}.")

    # score = utils.score_wrapper(map_name, solution, map_data, general_data)
    return best_score, best_solution


def create_simple_solution(location_names: list[str]):
    solution = {LK.locations: {}}

    for location_name in location_names:
        solution[LK.locations][location_name] = {
            LK.f9100Count: 1,
            LK.f3100Count: 0,
        }

    utils.prune_blanks_inplace(solution)

    return solution


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]


# db = Database()
# score, best_solution = db.get_best_solution(map_name)
# best_solution = json.loads(best_solution)

# json.dump(best_solution, open(f"tmp/solution_{map_name}.json", "w"), indent=4)

general_data = getGeneralData()
map_names = general_data["trainingMapNames"]

range_min = 0
range_max = 5
radius = general_data[GK.willingnessToTravelInMeters]  # 150.0


# for map_name in map_names:
map_name = MN.goteborg
if True:
    map_data = getMapData(map_name, api_key)

    location_names = map_data["locations"].keys()

    # ########################################
    # Find optimal solutions for each location
    # ########################################
    single_location_optimal_solutions = []
    for location_name in location_names:
        single_location_optimal_solutions.append(
            utils.find_optimal_placement_for_location(
                location_name, map_data, general_data, range_min, range_max
            )
        )

    # ########################################
    # merge solutions into one
    # ########################################
    solution = {LK.locations: {}}
    for single_solution in single_location_optimal_solutions:
        solution[LK.locations].update(single_solution[LK.locations])

    score = utils.score_wrapper(map_name, solution, map_data, general_data)
    print(f"Score for {map_name}: {score}. Optimized for individual locations.")

    # ########################################
    # Find locations within 150 meters
    # Try combinations within 150 meters
    # ########################################
    clusters = set()
    map_distance = utils.MapDistance(map_data)
    for location_name in location_names:
        cluster = map_distance.locations_within_radius(location_name, radius)
        if len(cluster) > 1:
            # The cluster we get may be a duplicate. Using a set keeps it unique.
            clusters.add(cluster)

    print(f"Found {len(clusters)} clusters of locations within {radius} meters")
    for cluster in clusters:
        print("\t", cluster)

    # ########################################
    # Brute force combinations within 150 meters
    # ########################################

    # Start with the small clusters and work towards bigger
    clusters = sorted(clusters, key=len)
    for cluster in clusters:
        print(f"Brute forcing cluster: {cluster}")
        score, solution = brute_force_locations(
            score, solution, cluster, map_data, general_data
        )

    print(f"Score for {map_name}: {score}. Optimized for clusters of close locations.")

    # TODO pruna smart.
    # minska en och se vad som händer. Öka alla andra med en och se vad som händer. Fortsätt bara om det blir bättre.

    pass


###############################################################################

"""
TODO var hostas api? Azure? Köra min lösning på Azure?


scoredSolution[SK.gameScore][SK.earnings] = (
    scoredSolution[SK.totalRevenue] - scoredSolution[SK.totalLeasingCost]
)

"willingnessToTravelInMeters": 150.0,

Teoretiskt max för en location? 
Prova sedan att sätta antal till 0 för att se om footfall + mindre leasing cost förbättrar score. 

Mindre leasing cost om man avstår från att ha en refillstation där det finns många andra. 

Kanske klustra och räkna på alla locations inom 150 meter. 
k nearest neighbors

while increasing_score
    prova sätta ut nya 9100 på var och en av locations och se om man får mer score.


----->  prova alla kombinationer på en location och alla locations inom 150 meter <--- 
"""
pass
