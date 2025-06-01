import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path

json_path = Path(__file__).resolve().parent / "air_quality_scaler_params.json"

with open(json_path, "r") as f:
    scaler_params = json.load(f)

scaler = MinMaxScaler()

data_min = []
data_max = []
scale = []

for key in scaler_params.keys():
    data_min.append(scaler_params[key]['min'])
    data_max.append(scaler_params[key]['max'])
    scale.append(scaler_params[key]['scale'])

scaler.data_min_ = np.array(data_min)
scaler.data_max_ = np.array(data_max)
scaler.scale_ = np.array(scale)

scaler.min_ = -scaler.data_min_ * scaler.scale_