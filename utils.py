from starterkit.scoring import calculateScore, distanceBetweenPoint
import math
import itertools
from starterkit.data_keys import (
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
)


def score_chunk(
    map_name,
    map_data,
    starting_solution,
    location_name,
    general_data,
    range_min,
    range_max,
):
    # TODO remove assert once tested
    assert starting_solution[LK.locations][location_name][LK.f3100Count] == 0

    best_solution = None
    best_score = -math.inf

    for i in range(range_min, range_max + 1):
        current_solution = copy_solution(starting_solution)
        current_solution[LK.locations][location_name][LK.f3100Count] = i
        current_score = score_wrapper(
            map_name, current_solution, map_data, general_data
        )

        if current_score > best_score:
            best_score = current_score
            best_solution = current_solution

    return best_score, best_solution


def brute_force_locations_cluster2(
    map_name,
    map_data,
    starting_score,
    starting_solution,
    location_cluster,
    general_data,
    range_min,
    range_max,
):
    # check all within checkpoint before deciding to continue or break
    # make function that checks best score for all solutions within a checkpoint?

    # start at 0 9100 and get best chunk, then increase to max

    pass


def brute_force_locations_cluster(
    map_name,
    map_data,
    starting_score,
    starting_solution,
    location_cluster,
    general_data,
    range_min,
    range_max,
):
    best_solution = starting_solution
    best_score = starting_score

    num_locations = len(location_cluster)
    iterable = itertools.product(
        range(range_min, range_max + 1), repeat=num_locations * 2
    )
    for tpl in iterable:
        current_solution = copy_solution(starting_solution)
        for i, location_name in enumerate(location_cluster):
            current_solution[LK.locations][location_name] = {
                LK.f9100Count: tpl[i],
                LK.f3100Count: tpl[i + 1],
            }

        prune_blanks_inplace(current_solution)
        current_score = score_wrapper(
            map_name, current_solution, map_data, general_data
        )
        if current_score > best_score:
            best_score = current_score
            best_solution = current_solution

    return best_score, best_solution


def copy_solution(solution):
    new_solution = {LK.locations: {}}
    new_solution[LK.locations] = {k: v for k, v in solution[LK.locations].items()}
    return new_solution


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


def find_optimal_placement_for_location2(
    location_name,
    current_solution,
    map_data,
    general_data,
    range_min,
    range_max,
):
    map_name = map_data[SK.mapName]

    best_solution_outer = None
    best_score_outer = -math.inf

    for cnt_9100 in range(range_min, range_max + 1):
        best_solution_inner = None
        best_score_inner = -math.inf

        for cnt_3100 in range(range_min, range_max + 1):
            new_solution = copy_solution(current_solution)

            if cnt_9100 == 0 and cnt_3100 == 0:
                if location_name in new_solution[LK.locations]:
                    del new_solution[LK.locations][location_name]
            else:
                new_solution[LK.locations][location_name] = {
                    LK.f9100Count: cnt_9100,
                    LK.f3100Count: cnt_3100,
                }

            score = score_wrapper(map_name, new_solution, map_data, general_data)

            if score >= best_score_inner:
                best_solution_inner = new_solution
                best_score_inner = score
            else:
                break

        if best_score_inner >= best_score_outer:
            best_solution_outer = best_solution_inner
            best_score_outer = best_score_inner
        else:
            break

    return best_score_outer, best_solution_outer


def create_simple_solution(location_names: list[str]):
    solution = {LK.locations: {}}

    for location_name in location_names:
        solution[LK.locations][location_name] = {
            LK.f9100Count: 1,
            LK.f3100Count: 0,
        }

    prune_blanks_inplace(solution)

    return solution


def score_wrapper(map_name, solution, map_data, general_data):
    if len(solution[LK.locations]) == 0:
        return -math.inf
    else:
        return calculateScore(map_name, solution, map_data, general_data)[SK.gameScore][
            SK.total
        ]


class MapDistance:
    def __init__(self, map_data):
        # initialize distance_matrix
        self.distance_matrix = {}

        location_names = list(map_data[LK.locations].keys())

        for i in range(len(location_names)):
            location_a = location_names[i]
            self.distance_matrix[location_a] = {}
            for j in range(i, len(location_names)):
                location_b = location_names[j]
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

                self.distance_matrix[location_a][location_b] = d
                if location_a != location_b:
                    if location_b not in self.distance_matrix:
                        self.distance_matrix[location_b] = {}
                    self.distance_matrix[location_b][location_a] = d

    # TODO remove not used.
    def distance(self, localtion_a: str, location_b: str) -> float:
        return self.distance_matrix[localtion_a][location_b]

    def locations_within_radius(self, location: str, radius: float) -> frozenset[str]:
        return frozenset(
            {
                location_b
                for location_b, distance in self.distance_matrix[location].items()
                if distance <= radius
            }
        )
