import os
import time
import requests
import numpy as np

def get_aq_matrix_10h() -> np.ndarray:
    data = get_last_10h_aq()
    matrix = []
    for item in data:
        comp = item["components"]
        label = item["main"]["aqi"]

        row = [
            label,
            comp.get("co"),
            comp.get("no"),
            comp.get("no2"),
            comp.get("o3"),
            comp.get("so2"),
            comp.get("pm2_5"),
            comp.get("pm10"),
            comp.get("nh3")
        ]

        if None not in row:
            matrix.append(row)
        if len(matrix) == 10:
            break

    if len(matrix) != 10:
        raise ValueError(f"Incomplete data: only {len(matrix)} valid rows")

    return np.array(matrix)

def get_last_10h_aq():
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing OPENWEATHERMAP_API_KEY in environment")

    end = int(time.time())
    start = end - 10 * 3600
    url = "https://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {
        "lat": 45.75,
        "lon": 4.85,
        "start": start,
        "end": end,
        "appid": api_key
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()["list"]
    return data