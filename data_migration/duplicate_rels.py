from function import NeoAdapter
import time
from tqdm import tqdm

neo = NeoAdapter(host="10.9.3.209", port="7687", password="12345678")
start_time = time.time()


for i in tqdm(range(31,36,2)):
    query = f"""
    CALL apoc.periodic.iterate(
        'MATCH (user1)-[r1:mutual_6586]->(user2:person:data) RETURN user1, r1, user2',
        'CREATE (user1)-[r2:clone_{i}_mutual_6586]->(user2) SET r2 = r1 CREATE (user1)-[r3:clone_{i+1}_mutual_6586]->(user2) SET r3 = r1',
        {{batchSize:1000}}
    )
    """

    res = neo.run_query(query) 

print(f"runtime: {time.time() - start_time}")