from collections import Counter
import random
import pandas as pd
import json
import os
import math
from dotenv import load_dotenv
from database import Database
from DistanceUtils import MapDistance
from starterkit.api import getGeneralData, getMapData

from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    GeneralKeys as GK,
)
import utils


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]


general_data = getGeneralData()
map_names = general_data["trainingMapNames"]

location_cluster_max_size = 5  # TODO optimize
range_min = 0
range_max = 2
radius = general_data[GK.willingnessToTravelInMeters]  # 200.0

db = Database()
algorithm = "custom1"

# put gbg last
map_names = sorted(map_names, reverse=True)
# for map_name in map_names:
map_name = MN.linkoping
if True:
    print("#############################################")
    print("Finding solution for:", map_name)
    print("#############################################")

    map_data = getMapData(map_name, api_key)

    location_names = list(map_data["locations"].keys())
    print(len(location_names), "locations")

    random.shuffle(location_names)
    # location_names = utils.order_by_sales(location_names, map_data)

    best_solution: dict = {LK.locations: {}}
    best_score = -math.inf

    # ########################################
    # Find optimal solutions for each location
    # ########################################
    for location_name in location_names:
        best_score, best_solution = utils.find_optimal_placement_for_single_location(
            location_name, best_solution, map_data, general_data, range_min, range_max
        )

    print(f"Score for {map_name}: {best_score}. Optimized for individual locations.")

    # ########################################
    # Find locations within 200 meters
    # Try combinations within radius
    # ########################################
    location_clusters = set()
    map_distance = MapDistance(map_data)
    for location_name in location_names:
        cluster = map_distance.locations_within_radius(location_name, radius)
        if len(cluster) > 1:
            # The cluster we get may be a duplicate. Using a set keeps it unique.
            location_clusters.add(cluster)

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # TODO merge clusters with common locations
    # Treat them as one big cluster.
    # location_clusters = merge_clusters(location_clusters)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    nr_of_clusters = len(location_clusters)
    nr_of_locations_in_all_clusters = len(
        {location for cluster in location_clusters for location in cluster}
    )

    print(f"Finding clusters of locations within a radius of {radius} meters.")
    print(f"{nr_of_clusters} clusters found.")
    print(f"{nr_of_locations_in_all_clusters} unique locations in clusters.")
    print(
        f"{round(100*nr_of_locations_in_all_clusters/len(location_names))}% of all locations are in clusters."
    )

    counter = Counter([len(cluster) for cluster in location_clusters])
    lst = []
    for value, count in counter.most_common():
        lst.append((value, count))
    df = pd.DataFrame(lst, columns=["cluster_size", "count"])
    print(df.to_string(index=False))

    # ########################################
    # Keeping only small clusters due to performance
    # ########################################
    small_clusters = [
        cluster
        for cluster in location_clusters
        if len(cluster) <= location_cluster_max_size
    ]
    print(f"Limiting cluster size to {location_cluster_max_size} locations.")
    print(f"{len(small_clusters)}/{nr_of_clusters} clusters will be considered.")

    # ########################################
    # Brute force combinations within radius
    # ########################################

    # Start with the small clusters and work towards bigger
    small_clusters = sorted(small_clusters, key=len)

    for i, cluster in enumerate(small_clusters):
        print(
            f"Brute forcing cluster {i+1}/{len(small_clusters)}. Cluster size: {len(cluster)}"
        )
        locations_in_cluster = list(cluster)
        random.shuffle(locations_in_cluster)

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

    print(
        f"Score for {map_name}: {best_score}. Optimized for clusters of close locations."
    )

    # ########################################
    # Do a second round of location specific optimization. Might find something new.
    # ########################################
    for location_name in location_names:
        best_score, best_solution = utils.find_optimal_placement_for_single_location(
            location_name, best_solution, map_data, general_data, range_min, range_max
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


    locations = []
    while loc := locations.pop():
        loc_perm := get_next_permutation(loc):
        
    
    perm_score, perm_solution = get next permutation(location1)
    push score to stack

        perm_score, perm_solution = get next permutation(location2)
        push score to stack

"""
pass
