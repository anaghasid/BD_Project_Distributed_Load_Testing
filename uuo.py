import json

# Assuming metrics_data is a dictionary
metrics_data = {"node_id": "example", "test_id": "123", "value": 42}


try:
    with open("dashboard.json", "r") as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    existing_data = []

# Append new data to the existing data
existing_data.append(metrics_data)

# Dump the updated data back to the file
with open("dashboard.json", "w") as json_file:
    json.dump(existing_data, json_file, indent=4)
