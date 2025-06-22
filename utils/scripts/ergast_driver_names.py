import fastf1
import time
import json

from tqdm.std import tqdm

year_driver_mapping = {}

for year in tqdm(range(2025, 1950, -1)):
    ergast = fastf1.ergast.Ergast()
    driver_standings = ergast.get_driver_standings(year).content[0]
    year_driver_mapping[year] = [f"{first} {last}" for (first,last) in zip(driver_standings["givenName"], driver_standings["familyName"])]
    time.sleep(1)

with open("year_driver_mapping.json", "w") as f:
    json.dump(year_driver_mapping, f)
