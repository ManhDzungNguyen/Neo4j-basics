import sys

sys.path.append("/home/dungnguyen/work/Neo4j-social-network")

import time

from function import NeoAdapter


neo = NeoAdapter(host="10.9.3.209", port="7687", password="12345678")
start_time = time.time()


# res = neo.run_query("CALL db.labels()").data()
# labels = [label["label"] for label in res]
labels = ["SEEDER_PS", "SEEDER_CS"]
not_remove_labels = ["User", "Post"]

for label in labels:
    if label not in not_remove_labels:
        neo.run_query(f"MATCH (n:`{label}`)  REMOVE n:`{label}`")

print(f"runtime: {time.time() - start_time}")
