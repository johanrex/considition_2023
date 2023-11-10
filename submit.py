from starterkit.data_keys import MapNames as MN
from database import Database
import os
import json
import time
import logging
from dotenv import load_dotenv
from starterkit.api import submit
from starterkit.api import getGeneralData

logger = logging.getLogger("submit_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]

db = Database()

general_data = getGeneralData()
map_names = general_data["trainingMapNames"]

logger.info("---------------------------------")
logger.info("Current best solutions:")
for map_name in map_names:
    total_score, _ = db.get_best_solution(map_name)
    logger.info(f"{map_name}:\t{total_score}")
logger.info("---------------------------------")

while True:
    logger.info("Checking for new solutions")
    for map_name in map_names:
        # Do some housekeeping
        db.keep_only_best_solution(map_name)

        # Get unsubmitted solutions
        total_score, unsubmitted_solution = db.get_best_unsubmitted_solution(map_name)

        if unsubmitted_solution is not None:
            logger.info(
                f"Submitting solution for: {map_name} with score: {total_score}"
            )

            submit(map_name, json.loads(unsubmitted_solution), api_key)

            db.mark_solution_as_submitted(map_name, unsubmitted_solution)
            db.keep_only_best_solution(map_name)

            time.sleep(5)

    # TODO do this better. Perhaps with tenacity
    time.sleep(20)
