import json
import os
import copy
from dotenv import load_dotenv
from database import Database
from starterkit.scoring import calculateScore
from starterkit.api import getGeneralData, getMapData

from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
)
import utils


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

range_min = 0
range_max = 5

general_data = getGeneralData()
map_names = general_data["trainingMapNames"]


for map_name in map_names:
    # map_name = MN.goteborg
    # if True:
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
    merged_solution = {LK.locations: {}}
    for single_solution in single_location_optimal_solutions:
        merged_solution[LK.locations].update(single_solution[LK.locations])

    score = utils.score_wrapper(map_name, merged_solution, map_data, general_data)
    print(f"Score for {map_name}: {score}.")

    # ########################################
    # Find locations within 150 meters
    # Try combinations within 150 meters
    # ########################################

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
        det finns distance i scoring filen. 
        for loc1 in locations:
            for loc2 in locations:
                if loc1 == loc2:
                    continue
                if distance(loc1, loc2) < 150:
                    for f9100 in range(0, 5):
                        for f3100 in range(0, 5):
                            solution = create_simple_solution()
                            solution[loc1][f9100] = f9100
                            solution[loc1][f3100] = f3100
                            calculateScore(solution)
                            if score > best_score:
                                best_score = score
                                best_solution = solution
                                


"""
pass
