from collections import Counter
import random
import genetic_util
import pandas as pd
import json
import os
import math
import sys
from dotenv import load_dotenv
from database import Database
from distanceutils import MapDistance
from starterkit.api import getGeneralData, getMapData

from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    GeneralKeys as GK,
)
import utils


def main():
    load_dotenv()
    api_key = os.environ["apiKey"]

    general_data = getGeneralData()

    cluster_max_size = 4  # TODO 4 is reasonable but slow
    range_min = 0
    range_max = 2
    radius = general_data[GK.willingnessToTravelInMeters]  # 200.0

    db = Database()
    algorithm = "custom1"

    # for map_name in map_names:
    map_name = MN.goteborg
    if True:
        print("#############################################")
        print("Finding solution for:", map_name)
        print("#############################################")

        map_data = getMapData(map_name, api_key)

        location_names = sorted(list(map_data["locations"].keys()))
        print(len(location_names), "locations")

        # random.shuffle(location_names)
        # location_names = utils.order_by_sales(location_names, map_data)

        # ########################################
        # Find optimal solutions for each location
        # ########################################

        best_score, best_solution = utils.brute_force_single_locations_many_times(
            location_names, map_data, general_data, range_min, range_max
        )

        # TODO why the hell does score increase after second round of optimizing for individual locations?

        # ########################################
        # Find clusters of locations within radius
        # ########################################
        location_clusters: list[frozenset[str]] = utils.get_location_clusters(
            map_data, location_names, radius
        )

        locations_in_clusters = [
            location for cluster in location_clusters for location in cluster
        ]

        locations_not_in_clusters = list(
            set(location_names) - set(locations_in_clusters)
        )

        # Why does this produce different results every time? It shouldn't. I'm missing something.
        # random.shuffle(locations_not_in_clusters)

        locations_not_in_clusters = utils.order_by_sales(
            locations_not_in_clusters, map_data
        )

        nr_of_clusters = len(location_clusters)
        nr_of_locations_in_all_clusters = len(
            {location for cluster in location_clusters for location in cluster}
        )

        print(f"Finding clusters of locations within a radius of {radius} meters.")
        print(f"{nr_of_locations_in_all_clusters} unique locations in clusters.")
        print(
            f"{round(100*nr_of_locations_in_all_clusters/len(location_names))}% of all locations are in clusters."
        )

        print(utils.get_clusters_summary(location_clusters))

        # ########################################
        # merge clusters with common locations
        # ########################################
        print("Merging clusters with common locations.")
        location_clusters = utils.merge_clusters_with_common_locations(
            location_clusters
        )
        print(utils.get_clusters_summary(location_clusters))

        # ########################################
        # Keeping only small clusters due to performance
        # ########################################
        small_clusters = [
            cluster for cluster in location_clusters if len(cluster) <= cluster_max_size
        ]

        large_clusters = [
            cluster for cluster in location_clusters if len(cluster) > cluster_max_size
        ]

        print(f"Limiting cluster size to {cluster_max_size} locations.")
        print(f"{len(small_clusters)}/{nr_of_clusters} clusters will be considered.")

        # ########################################
        # Small clusters: brute force
        # ########################################

        f"{len(small_clusters)} small clusters. Using brute force."

        # Start with the smallest clusters and work towards bigger
        small_clusters = sorted(small_clusters, key=len)
        for i, cluster in enumerate(small_clusters):
            print(
                f"Brute force. Cluster size: {len(cluster)}. {i+1}/{len(small_clusters)}."
            )
            locations_in_cluster = list(cluster)
            locations_in_cluster = utils.order_by_sales(
                locations_in_cluster, map_data, reverse=False
            )

            best_score, best_solution = utils.brute_force_locations_cluster(
                map_name,
                map_data,
                best_score,
                best_solution,
                locations_in_cluster,
                general_data,
                range_min,
                range_max,
            )

        print(f"Score for {map_name}: {best_score}. Optimized for small clusters.")

        # ########################################
        # Large clusters: genetic algorithm
        # ########################################

        nr_of_evolutions = 3
        nr_of_generations = 1000
        population_size = 10

        print(f"{len(large_clusters)} large clusters. Using genetic algorithm.")
        for i, cluster in enumerate(large_clusters):
            print(
                f"Genetic. Cluster size: {len(cluster)}. {i+1}/{len(large_clusters)}."
            )
            locations_in_cluster = list(cluster)

            ga = genetic_util.GeneticUtil(
                map_name, locations_in_cluster, map_data, general_data, best_solution
            )
            best_score, best_solution = ga.run_evolution(
                nr_of_evolutions,
                nr_of_generations,
                population_size,
                best_score,
                best_solution,
                range_min,
                range_max,
            )

        # ########################################
        # Do a second round of location specific optimization. Might find something new.
        # ########################################
        best_score, best_solution = utils.brute_force_locations_by_single_location(
            best_score,
            best_solution,
            location_names,
            map_data,
            general_data,
            range_min,
            range_max,
        )

        print(
            f"Score for {map_name}: {best_score}. Second round of optimizing for individual locations."
        )

        # ########################################
        # Add to database
        # ########################################
        db.insert(
            map_name,
            best_score,
            algorithm,
            json.dumps(best_solution),
        )

        print("Done.")
        print("")

        pass


if __name__ == "__main__":
    main()


###############################################################################

"""
TODO optimizations
    var hostas api? Azure? Köra min lösning på Azure?
    bättre brute force för location cluster. Kanske nån stack för att hålla reda på inre loopen. 
    mypy?
    cython?
    mypyc?
    skriv om scoring function så den inte gör dict access?
    multithreading?
    parallellisera?
    skriv till db async?
    c++ scoring?

TODO competition day
    Reboot computer for fresh memory
    Make sure it commits to database
    Make sure the submit script is running
    Make sure to switch to the competition maps. 

"""
pass

# bara kör en massa single location optimization med random start input och se var de diffar. Där finns något att brute forca.

# parallellisera den genetiska modellen!!!!

# Hur köra på vm i molnet?
#   Fixa konto på ms.
#   docker?


# TODO read cached data from file and see if that solves the differences.
