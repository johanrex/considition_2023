import os
from starterkit.api import getGeneralData, getMapData
from starterkit.scoring import calculateScore, distanceBetweenPoint
from collections import Counter
import math
from dotenv import load_dotenv
import copy
from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
)
import utils


def find_optimal_placement_for_location(
    location_name, map_data, general_data, range_min, range_max
):
    map_name = map_data[SK.mapName]

    scores = []

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

            scores.append((score, (i, j)))
    return scores


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]


general_data = getGeneralData()
map_names = general_data["trainingMapNames"]

range_min = 0
range_max = 5

all_permutations = []

for map_name in map_names:
    map_data = getMapData(map_name, api_key)
    location_names = map_data["locations"].keys()

    prev_permutations = None
    for location_name in location_names:
        score_infos = find_optimal_placement_for_location(
            location_name, map_data, general_data, range_min, range_max
        )

        score_infos.sort(key=lambda x: x[0], reverse=True)
        permutations = [score_info[1] for score_info in score_infos]
        permutations = str(permutations)

        all_permutations.append(permutations)

    counter = Counter(all_permutations)
    print(counter.most_common())

    pass
    break

    """ llägg först ut max antal 9100, fyll sedan upp med 3100..."""

    """ varje location har en optimal permutation. Man kanske skall använda den. """

pass
