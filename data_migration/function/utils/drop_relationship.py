import sys

sys.path.append("/home/dungnguyen/work/neo4j/data_migration_neo4j_3.4.5-5.11.0")

import time

from function import NeoAdapter


neo = NeoAdapter(host="10.9.3.209", port="7687", password="12345678")

init_time = time.time()
res = neo.drop_relationship("clone_22_all")
print(res)
print(f"runtime: {time.time() - init_time}")
