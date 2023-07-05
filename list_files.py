import json

import requests

API_KEY = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImE1OGI5NGZmMDY5NDRhZDNhZjFkMDBmNDBmNTQyNjBkIiwiaCI6Im11cm11cjEyOCJ9"


def date_as_filename(year, month, day, time):
    if month < 10:
       month = f"0{month}"
    if day < 10:
         day = f"0{day}" 
    return f"RAD_NL25_PCP_NA_{year}{month}{day}{time}.nc"

response = requests.get(
    url="https://api.dataplatform.knmi.nl/open-data/v1/datasets/radar_reflectivity_composites/versions/2.0/files",
    headers={"Authorization": API_KEY},
    params={"maxKeys": 15, "startAfterFilename": date_as_filename(2023, 7, 5, 1100)}
)

print(json.dumps(response.json(), indent=4))

