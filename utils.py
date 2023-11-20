from starterkit.scoring import calculateScore
import math
import itertools
from starterkit.data_keys import (
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
    GeneralKeys as GK,
)

# increasingscore_3100
# increasingscore_9100


class PermutationManager:
    machine_permutations = (
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    )

    # switch to genetic algorithm for the large clusters?

    # ta bort alla kombinationer med en summa > x
    # ta bort alla kombinationer med en summa < x

    # sort by score?

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # if increasing score, continue.
    # if decreasing score, continue 3.
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # kanske alltid kolla 3 framåt.
    # lookahead_count
    # lower_decreased_count

    @classmethod
    def get_next_permutation(cls, current_permutation_idx):
        if current_permutation_idx == len(cls.machine_permutations) - 1:
            return None, None
        else:
            next_permutation_idx = current_permutation_idx + 1
            return (
                next_permutation_idx,
                cls.machine_permutations[next_permutation_idx],
            )

    @classmethod
    def should_continue(
        cls, old_score, current_score, old_permutation_idx, current_permutation_idx
    ):
        if current_score > old_score:
            return True
        elif current_score == old_score:
            if current_permutation_idx > old_permutation_idx:
                return True
            else:
                return False
        else:
            return False


def brute_force_single_location(
    map_name,
    map_data,
    starting_solution,
    location_name,
    general_data,
):
    best_score = -math.inf
    best_solution = None

    for f9100count, f3100count in PermutationManager.machine_permutations:
        current_solution = copy_solution(starting_solution)

        if f9100count == 0 and f3100count == 0:
            if location_name in current_solution[LK.locations]:
                del current_solution[LK.locations][location_name]
        else:
            current_solution[LK.locations][location_name] = {
                LK.f9100Count: f9100count,
                LK.f3100Count: f3100count,
            }

        current_score = score_wrapper(
            map_name, current_solution, map_data, general_data
        )

        if current_score > best_score:
            best_score = current_score
            best_solution = current_solution

    return best_score, best_solution


def score_all_3100(
    map_name,
    map_data,
    starting_solution,
    location_name,
    general_data,
    range_min,
    range_max,
):
    best_solution = None
    best_score = -math.inf

    for i in range(range_min, range_max + 1):
        current_solution = copy_solution(starting_solution)
        current_solution[LK.locations][location_name][LK.f3100Count] = i

        if (
            current_solution[LK.locations][location_name][LK.f9100Count] == 0
            and current_solution[LK.locations][location_name][LK.f3100Count] == 0
        ):
            del current_solution[LK.locations][location_name]

        current_score = score_wrapper(
            map_name, current_solution, map_data, general_data
        )

        if current_score > best_score:
            best_score = current_score
            best_solution = current_solution

    return best_score, best_solution


def score_location(
    map_name,
    map_data,
    starting_solution,
    location_name,
    general_data,
    range_min,
    range_max,
):
    best_solution = None
    best_score = -math.inf

    for i in range(range_min, range_max + 1):
        current_solution = copy_solution(starting_solution)

        if location_name not in current_solution[LK.locations]:
            current_solution[LK.locations][location_name] = {
                LK.f9100Count: 0,
                LK.f3100Count: 0,
            }
        current_solution[LK.locations][location_name][LK.f9100Count] = i

        best_score_3100, best_solution_3100 = score_all_3100(
            map_name,
            map_data,
            current_solution,
            location_name,
            general_data,
            range_min,
            range_max,
        )

        if best_score_3100 > best_score:
            best_score = best_score_3100
            best_solution = best_solution_3100
        else:
            break

    return best_score, best_solution


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
            if tpl[i] == 0 and tpl[i + 1] == 0:
                if location_name in current_solution[LK.locations]:
                    del current_solution[LK.locations][location_name]
            else:
                current_solution[LK.locations][location_name] = {
                    LK.f9100Count: tpl[i],
                    LK.f3100Count: tpl[i + 1],
                }

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


def find_optimal_placement_for_single_location(
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
    solution: dict = {LK.locations: {}}

    for location_name in location_names:
        solution[LK.locations][location_name] = {
            LK.f9100Count: 1,
            LK.f3100Count: 0,
        }

    return solution


def order_by_sales(locations, map_data):
    sorted_locations = sorted(
        locations, key=lambda x: map_data[LK.locations][x][GK.salesVol], reverse=True
    )
    return sorted_locations


def score_wrapper(map_name, solution, map_data, general_data):
    if len(solution[LK.locations]) == 0:
        return -math.inf
    else:
        return calculateScore(map_name, solution, map_data, general_data)[SK.gameScore][
            SK.total
        ]
