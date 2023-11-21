import random
from starterkit.api import getGeneralData, getMapData
from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    GeneralKeys as GK,
)

import utils
from dotenv import load_dotenv
import os
import math


def create_wrong_solution(location_names: list[str]):
    solution = {LK.locations: {}}

    for location_name in location_names:
        solution[LK.locations][location_name] = {
            LK.f9100Count: 0,
            LK.f3100Count: 0,
        }

    return solution


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]

general_data = getGeneralData()

map_name = MN.linkoping
map_data = getMapData(map_name, api_key)
location_names = list(map_data["locations"].keys())
print(location_names)

location_cluster_max_size = 5  # TODO optimize
range_min = 0
range_max = 2
radius = general_data[GK.willingnessToTravelInMeters]  # 200.0

best_solution: dict = {LK.locations: {}}
best_score = -math.inf


location_clusters: list[frozenset[str]] = utils.get_location_clusters(
    map_data, location_names, radius
)

locations_in_clusters = [
    location for cluster in location_clusters for location in cluster
]
locations_not_in_clusters = list(set(location_names) - set(locations_in_clusters))
random.shuffle(locations_not_in_clusters)


print(f"{best_score=}")
print(f"{best_solution=}")
print(f"{locations_not_in_clusters=}")
print(f"{map_data=}")
print(f"{general_data=}")
print(f"{range_min=}")
print(f"{range_max=}")

best_score, best_solution = utils.brute_force_locations_by_single_location(
    best_score,
    best_solution,
    locations_not_in_clusters,
    map_data,
    general_data,
    range_min,
    range_max,
)

print(f"Score for {map_name}: {best_score}. Optimized for individual locations.")

# best_score, best_solution = utils.brute_force_locations_by_single_location(
#     best_score,
#     best_solution,
#     locations_not_in_clusters,
#     map_data,
#     general_data,
#     range_min,
#     range_max,
# )

# print(f"Score for {map_name}: {best_score}. Optimized for individual locations. Again.")
