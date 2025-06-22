import fastf1
import time
import json
from pprint import pprint

from tqdm.std import tqdm

year_team_mapping = {}

for year in tqdm(range(2025, 1950, -1)):
    constructor_standings = fastf1.ergast.Ergast().get_constructor_standings(year).content[0]
    year_team_mapping[year] = list(constructor_standings["constructorName"])
    time.sleep(1)


with open("year_driver_mapping.json", "w") as f:
    json.dump(year_team_mapping, f)
