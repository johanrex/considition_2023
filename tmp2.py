import os
from database import Database
import json
import time
import copy
from starterkit.data_keys import (
    LocationKeys as LK,
)
import timeit
from starterkit.api import getGeneralData, getMapData
from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    GeneralKeys as GK,
)
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["apiKey"]
domain = os.environ["domain"]


map_name = MN.linkoping

prev = None
for i in range(10):
    print(i)
    map_data = getMapData(map_name, api_key)

    s = json.dumps(map_data)
    if prev is not None:
        assert s == prev
    prev = s
    time.sleep(5)


print("Done")
