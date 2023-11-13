from function import NeoAdapter
import time
from tqdm import tqdm


neo = NeoAdapter(host="10.9.3.178", port="7687", password="123!@#")
start_time = time.time()

export_nodes = False
export_relationships = True

# node config
node_labels = ["person", "data"]
no_nodes = 1278150

# relationship config
rel_labels = ["mutual_6843"]
no_rels = 2321076


if export_nodes:
    for i in tqdm(range(0, no_nodes, 50000), desc=f"export nodes"):
        query = f"""
        CALL apoc.export.json.query(
            "MATCH (n:{':'.join(node_labels)}) RETURN n ORDER BY id(n) SKIP {str(i)} LIMIT {str(50000)}",
            "/tmp/all_{'_'.join(node_labels)}_{str(i).zfill(7)}_{str(i+50000).zfill(7)}.json",
            {{}}
        )
        YIELD file, nodes, relationships, properties, data
        RETURN file, nodes, relationships, properties, data
        """
        res = neo.run_query(query)


if export_relationships:
    for i in tqdm(range(0, no_rels, 50000), desc=f"export rels"):
        query = f"""
        CALL apoc.export.json.query(
            "MATCH (s_n:{':'.join(node_labels)})-[r:{":".join(rel_labels)}]->(e_n:{':'.join(node_labels)}) RETURN r ORDER BY id(r) SKIP {str(i)} LIMIT {str(50000)}",
            "/tmp/all_{'_'.join(rel_labels)}_{str(i).zfill(7)}_{str(i+50000).zfill(7)}.json",
            {{}}
        )
        YIELD file, nodes, relationships, properties, data
        RETURN file, nodes, relationships, properties, data
        """
        res = neo.run_query(query)


print(f"runtime: {time.time() - start_time}")
