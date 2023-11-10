from starterkit.scoring import calculateScore, distanceBetweenPoint
import math
import copy
from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
)


def create_zero_solution(location_names: list[str]):
    solution = {LK.locations: {}}
    for location_name in location_names:
        solution[LK.locations][location_name] = {
            LK.f9100Count: 0,
            LK.f3100Count: 0,
        }
    return solution


def fill_missing_locations_inplace(solution, location_names):
    for location_name in location_names:
        if location_name not in solution[LK.locations]:
            solution[LK.locations][location_name] = {
                LK.f9100Count: 0,
                LK.f3100Count: 0,
            }


def prune_blanks_inplace(solution):
    solution[LK.locations] = {
        k: v
        for k, v in solution[LK.locations].items()
        if v[LK.f9100Count] > 0 or v[LK.f3100Count] > 0
    }


def find_optimal_placement_for_location(
    location_name, map_data, general_data, range_min, range_max
):
    map_name = map_data[SK.mapName]
    best_score = -math.inf
    best_solution = None

    for i in range(range_min, range_max + 1):
        for j in range(range_min, range_max + 1):
            solution = {LK.locations: {}}
            solution[LK.locations][location_name] = {
                LK.f9100Count: i,
                LK.f3100Count: j,
            }

            # can't score zero solution
            if i == 0 and j == 0:
                continue

            score = calculateScore(map_name, solution, map_data, general_data)[
                SK.gameScore
            ][SK.total]

            if score > best_score:
                best_score = score
                best_solution = solution

    return best_solution


def score_wrapper(map_name, solution, map_data, general_data):
    return calculateScore(map_name, solution, map_data, general_data)[SK.gameScore][
        SK.total
    ]


class MapDistance:
    def __init__(self, map_data):
        location_names = map_data[LK.locations].keys()
        for location_a in location_names:
            for location_b in location_names:
                if location_a == location_b:
                    d = 0
                else:
                    location_a_data = map_data[LK.locations][location_a]
                    location_b_data = map_data[LK.locations][location_b]

                    lat_a = location_a_data[CK.latitude]
                    long_a = location_a_data[CK.longitude]
                    lat_b = location_b_data[CK.latitude]
                    long_b = location_b_data[CK.longitude]

                    d = distanceBetweenPoint(lat_a, long_a, lat_b, long_b)

                d.... put in distance matrix

        # distanceBetweenPoint(lat_1, long_1, lat_2, long_2) -> int:

    def distance(localtion_a: str, location_b: str) -> float:
        return 0
