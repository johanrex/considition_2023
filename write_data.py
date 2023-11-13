import json
import os
from dotenv import load_dotenv
from starterkit.api import getGeneralData, getMapData


def write_file(file_name, data):
    # get directory name from file_name
    dir_name = os.path.dirname(file_name)
    os.makedirs(dir_name, exist_ok=True)

    s = json.dumps(data, indent=4)

    with open(file_name, "w") as f:
        f.write(s)


load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]


general_data = getGeneralData()
write_file("tmp/general_data.json", general_data)

map_names = general_data["trainingMapNames"]

for map_name in map_names:
    # map_name = MN.linkoping
    # if True:
    print("Finding solution for:", map_name)

    map_data = getMapData(map_name, api_key)
    write_file(f"tmp/map_data_{map_name}.json", map_data)
