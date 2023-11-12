import json
import os
import copy
import math
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


def brute_force_location_cluster(
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


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]


# score, best_solution = db.get_best_solution(map_name)
# best_solution = json.loads(best_solution)

# json.dump(best_solution, open(f"tmp/solution_{map_name}.json", "w"), indent=4)

general_data = getGeneralData()
map_names = general_data["trainingMapNames"]

range_min = 0
range_max = 5
radius = general_data[GK.willingnessToTravelInMeters]  # 150.0

db = Database()
algorithm = "custom1"

# put gbg last
map_names = sorted(map_names, reverse=True)
# for map_name in map_names:
map_name = MN.goteborg
if True:
    print("Finding solution for:", map_name)

    map_data = getMapData(map_name, api_key)

    location_names = map_data["locations"].keys()

    best_solution = {LK.locations: {}}
    best_score = -math.inf

    # ########################################
    # Find optimal solutions for each location
    # ########################################
    for location_name in location_names:
        best_score, best_solution = utils.find_optimal_placement_for_location2(
            location_name, best_solution, map_data, general_data, range_min, range_max
        )
    print(f"Score for {map_name}: {best_score}. Optimized for individual locations.")

    # ########################################
    # Find locations within 150 meters
    # Try combinations within 150 meters
    # ########################################
    location_clusters = set()
    map_distance = utils.MapDistance(map_data)
    for location_name in location_names:
        cluster = map_distance.locations_within_radius(location_name, radius)
        if len(cluster) > 1:
            # The cluster we get may be a duplicate. Using a set keeps it unique.
            location_clusters.add(cluster)

    print(
        f"Found {len(location_clusters)} clusters of locations within {radius} meters"
    )

    # ########################################
    # Keeping only some small clusters due to performance
    # ########################################
    cluster_limit = 3  # TODO optimize
    location_clusters = [
        cluster for cluster in location_clusters if len(cluster) <= cluster_limit
    ]
    print(
        f"Limiting cluster size to {cluster_limit}. Keeping {len(location_clusters)} clusters."
    )

    # ########################################
    # Brute force combinations within 150 meters
    # ########################################

    # Start with the small clusters and work towards bigger
    location_clusters = sorted(location_clusters, key=len)

    for cluster in location_clusters:
        print(f"Brute forcing cluster: {cluster}")
        best_score, best_solution = brute_force_location_cluster(
            best_score, best_solution, cluster, map_data, general_data
        )

    print(
        f"Score for {map_name}: {best_score}. Optimized for clusters of close locations."
    )

    # ########################################
    # Do a second round of location specific optimization. Might find something new.
    # ########################################
    for location_name in location_names:
        best_score, best_solution = utils.find_optimal_placement_for_location2(
            location_name, best_solution, map_data, general_data, range_min, range_max
        )
    print(f"Score for {map_name}: {best_score}. Optimized for individual locations.")

    # ########################################
    # Add to database
    # ########################################
    db.insert(
        map_name,
        best_score,
        algorithm,
        json.dumps(best_solution),
    )

    # TODO pruna smart.
    # minska en och se vad som händer. Öka alla andra med en och se vad som händer. Fortsätt bara om det blir bättre.

    pass


###############################################################################

"""
TODO optimizations
    var hostas api? Azure? Köra min lösning på Azure?
    bättre brute force för location cluster. Kanske nån stack för att hålla reda på inre loopen. 
    mypy?
    cython?
    mypyc?
    skriv om scoring function så den inte gör dict access?
    c++ scoring?

    locations = []
    while loc := locations.pop():
        loc_perm := get_next_permutation(loc):
        
    
    perm_score, perm_solution = get next permutation(location1)
    push score to stack

        perm_score, perm_solution = get next permutation(location2)
        push score to stack

"""
pass
