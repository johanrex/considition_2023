import utils
from dotenv import load_dotenv
import os
from starterkit.api import getGeneralData, getMapData

from starterkit.data_keys import (
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
    GeneralKeys as GK,
)


def copy_solution(solution):
    new_solution = {LK.locations: {}}
    new_solution[LK.locations] = {k: v for k, v in solution[LK.locations].items()}
    return new_solution


solution = {
    "locations": {
        "location13": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location10": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location28": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location19": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location3": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location21": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location7": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location27": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location36": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location37": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location1": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location18": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location30": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location15": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location2": {"freestyle9100Count": 0, "freestyle3100Count": 1},
        "location4": {"freestyle9100Count": 0, "freestyle3100Count": 2},
        "location26": {"freestyle9100Count": 0, "freestyle3100Count": 2},
        "location39": {"freestyle9100Count": 0, "freestyle3100Count": 1},
    }
}

load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]

map_name = "linkoping"

general_data = getGeneralData()
map_data = getMapData(map_name, api_key)

for i in range(10):
    solution = copy_solution(solution)
    score = utils.score_wrapper(map_name, solution, map_data, general_data)
    print(score)
