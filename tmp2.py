from starterkit.scoring import calculateScore, distanceBetweenPoint
from starterkit.api import submit
from starterkit.api import getGeneralData, getMapData
from dotenv import load_dotenv
import os
import math
import itertools
from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
)


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


map_name = MN.linkoping
map_data = getMapData(map_name, api_key)
location_names = list(map_data["locations"].keys())

wrong_solution = create_wrong_solution(location_names)

submit(map_name, wrong_solution, api_key)
