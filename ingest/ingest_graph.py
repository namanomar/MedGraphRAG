import requests
import json
import os
data = "./database"
print(os.listdir(data))
# DGRAPH_URL = "http://localhost:8080"

# schema = """
# name: string @index(exact) .
# type: string @index(exact) .
# treats: [uid] .
# side_effect: [uid] .
# """

# data = [
#     {"uid": "_:tuberculosis", "name": "MDR-Tuberculosis", "type": "Disease"},
#     {"uid": "_:rifampicin", "name": "Rifampicin", "type": "Drug"},
#     {"uid": "_:nausea", "name": "Nausea", "type": "Effect"},
#     {"uid": "_:rifampicin", "treats": {"uid": "_:tuberculosis"}},
#     {"uid": "_:rifampicin", "side_effect": {"uid": "_:nausea"}},
# ]

# # Upload schema
# requests.post(f"{DGRAPH_URL}/alter", data=schema)

# # Insert data
# res = requests.post(f"{DGRAPH_URL}/mutate?commitNow=true", json={"set": data})
# print("Graph ingest complete:", res.json())
