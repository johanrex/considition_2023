from database import Database
import os
import random
import json
from collections import Counter
from multiprocessing import Pool
from functools import partial
import pandas as pd
from distanceutils import MapDistance
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


def score_checkpoint(
    map_name: str, score: float, solution: dict, algorithm: str
) -> None:
    print(f"Writing score {score} to database")
    Database().insert(
        map_name,
        score,
        algorithm,
        json.dumps(solution),
    )


def brute_force_single_location(
    map_name,
    map_data,
    starting_solution,
    location_name,
    general_data,
) -> tuple[float, dict]:
    best_score = -math.inf
    best_solution = {}

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
) -> tuple[float, dict]:
    best_solution = {}
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
) -> tuple[float, dict]:
    best_solution = {}
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


def get_location_clusters(
    map_data: dict, location_names: list[str], radius: float
) -> list[frozenset[str]]:
    """Get a list of location clusters within radius where cluster has radius"""
    location_clusters_set = set()
    map_distance = MapDistance(map_data)
    for location_name in location_names:
        cluster = map_distance.locations_within_radius(location_name, radius)
        if len(cluster) > 1:
            # The cluster we get may be a duplicate. Using a set keeps it unique.
            location_clusters_set.add(cluster)

    return list(location_clusters_set)


def merge_clusters_with_common_locations(
    location_clusters: list[frozenset[str]],
) -> list[frozenset]:
    merged_clusters: list[frozenset] = []
    q = list(location_clusters)
    while len(q) > 0:
        current_cluster = q.pop(0)
        for other_cluster in q:
            if len(current_cluster & other_cluster) > 0:
                current_cluster |= other_cluster
                q.remove(other_cluster)

        merged_clusters.append(current_cluster)

    return merged_clusters


def get_clusters_summary(location_clusters) -> str:
    counter = Counter([len(cluster) for cluster in location_clusters])
    lst = [(value, count) for value, count in counter.most_common()]
    df = pd.DataFrame(lst, columns=["cluster_size", "count"])
    df = df.sort_values("cluster_size")
    msg = "Total nr of clusters: " + str(len(location_clusters)) + "\n"
    msg += df.to_string(index=False)
    return msg


def brute_force_locations_cluster(
    map_name,
    map_data,
    starting_score,
    starting_solution,
    location_cluster,
    general_data,
    range_min,
    range_max,
) -> tuple[float, dict]:
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


def copy_solution(solution: dict) -> dict:
    new_solution = {LK.locations: {}}
    new_solution[LK.locations] = {k: v for k, v in solution[LK.locations].items()}
    return new_solution


def fill_missing_locations_inplace(solution: dict, location_names: list[str]) -> None:
    for location_name in location_names:
        if location_name not in solution[LK.locations]:
            solution[LK.locations][location_name] = {
                LK.f9100Count: 0,
                LK.f3100Count: 0,
            }


def brute_force_single_locations_many_times_worker(
    i: int,
    location_names: list[str],
    map_data: dict,
    general_data: dict,
    range_min: int,
    range_max: int,
) -> tuple[float, dict]:
    print(f"Running attempt {i+1} in process ID {os.getpid()}")
    return brute_force_single_locations(
        location_names, map_data, general_data, range_min, range_max
    )


def brute_force_single_locations_many_times(
    location_names, map_data, general_data, range_min, range_max, attempts=3
) -> tuple[float, dict]:
    print("Brute forcing initial solution on individual locations...")
    best_solution: dict
    best_score = -math.inf

    try:
        # attempts can be run in parallel.
        with Pool() as p:
            partial_worker = partial(
                brute_force_single_locations_many_times_worker,
                location_names=location_names,
                map_data=map_data,
                general_data=general_data,
                range_min=range_min,
                range_max=range_max,
            )
            results = p.map(partial_worker, range(attempts))
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        p.terminate()
        p.join()

    for attempt_best_score, attempt_best_solution in results:
        if attempt_best_score > best_score:
            best_score = attempt_best_score
            best_solution = attempt_best_solution
            print("New best score:", best_score)

    return best_score, best_solution


def brute_force_single_locations(
    location_names,
    map_data,
    general_data,
    range_min,
    range_max,
) -> tuple[float, dict]:
    prev_score = -math.inf
    best_score = -math.inf
    best_solution: dict = {LK.locations: {}}
    improvement = True
    while improvement:
        random.shuffle(location_names)

        (
            candidate_score,
            candidate_best_solution,
        ) = brute_force_locations_by_single_location(
            best_score,
            best_solution,
            location_names,
            map_data,
            general_data,
            range_min,
            range_max,
        )

        if prev_score == candidate_score:
            improvement = False

        if candidate_score > best_score:
            best_score = candidate_score
            best_solution = candidate_best_solution
            print(f"New best score:{best_score}. Pid {os.getpid()}")
            score_checkpoint(
                map_data["mapName"], best_score, best_solution, "custom1"
            )  # hack to get anything at all from the big cities.

        prev_score = best_score
    return best_score, best_solution


def brute_force_locations_by_single_location(
    best_score: float,
    best_solution: dict,
    location_names: list[str],
    map_data: dict,
    general_data: dict,
    range_min: int,
    range_max: int,
) -> tuple[float, dict]:
    for location_name in location_names:
        best_score, best_solution = find_optimal_placement_for_single_location(
            location_name, best_solution, map_data, general_data, range_min, range_max
        )
    return best_score, best_solution


def find_optimal_placement_for_single_location(
    location_name: str,
    current_solution: dict,
    map_data: dict,
    general_data: dict,
    range_min: int,
    range_max: int,
) -> tuple[float, dict]:
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


def create_random_solution(location_names: list[str]) -> dict:
    solution: dict = {LK.locations: {}}
    arr = [0, 1, 2]

    for location_name in location_names:
        rnd1 = random.choice(arr)
        rnd2 = random.choice(arr)
        if rnd1 != 0 or rnd2 != 0:
            solution[LK.locations][location_name] = {
                LK.f9100Count: rnd1,
                LK.f3100Count: rnd2,
            }

    return solution


def create_simple_solution(location_names: list[str]) -> dict:
    solution: dict = {LK.locations: {}}

    for location_name in location_names:
        solution[LK.locations][location_name] = {
            LK.f9100Count: 1,
            LK.f3100Count: 0,
        }

    return solution


def order_by_sales(locations: list[str], map_data: dict, reverse=True) -> list[str]:
    sorted_locations = sorted(
        locations, key=lambda x: map_data[LK.locations][x][GK.salesVol], reverse=reverse
    )
    return sorted_locations


def score_wrapper(
    map_name: str, solution: dict, map_data: dict, general_data: dict
) -> float:
    if len(solution[LK.locations]) == 0:
        return -math.inf
    else:
        return calculateScore(map_name, solution, map_data, general_data)[SK.gameScore][
            SK.total
        ]
