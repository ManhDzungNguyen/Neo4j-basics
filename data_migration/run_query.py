from function import NeoAdapter
import time
from tqdm import tqdm

neo = NeoAdapter(host="10.9.3.209", port="7687", password="12345678")
# neo = NeoAdapter(host="10.9.3.178", port="7687", password="123!@#")
start_time = time.time()


# query = """
# MATCH (u:person:data)
# WHERE   u.total_action_6586 > 0
# WITH u ORDER BY u.pagerank_6586 desc
# LIMIT 100 WITH COLLECT(u.id) AS ids

# MATCH p=((a:person:data WHERE a.id IN ids)-[r:mutual_6586 WHERE r.mutual_action_count > 1]->(b:person:data WHERE b.id IN ids))
# RETURN p    
# """

query = """
MATCH (u:person:data)
WHERE   u.total_action_6586 > 0
WITH u ORDER BY u.pagerank_6586 desc
LIMIT 100 WITH COLLECT(u.id) AS ids

MATCH p=((a:person:data)-[r:clone_36_mutual_6586]->(b:person:data))
WHERE   a.id IN ids AND b.id IN ids
    AND r.mutual_action_count > 1
RETURN p
"""

res = neo.run_query(query)
print(res)             
print(f"runtime: {time.time() - start_time}")