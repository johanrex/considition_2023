from database import Database
import json
import copy
from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
)
import timeit


db = Database()

score, solution = db.get_best_solution("goteborg")
solution = json.loads(solution)


def copy_solution_deepcopy(solution):
    return copy.deepcopy(solution)


def copy_solution_dict_comprehension(solution):
    new_solution = {LK.locations: {}}
    new_solution[LK.locations] = {k: v for k, v in solution[LK.locations].items()}
    return new_solution


n = 10_000

time_dict_comprehension = timeit.timeit(
    "copy_solution_dict_comprehension(solution)", globals=globals(), number=n
)

time_deepcopy = timeit.timeit(
    "copy_solution_deepcopy(solution)", globals=globals(), number=n
)

print("dict comprehension\t", time_dict_comprehension)
print("deepcopy\t\t", time_deepcopy)
