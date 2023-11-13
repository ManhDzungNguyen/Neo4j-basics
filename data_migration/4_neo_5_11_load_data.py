import time
import json

from tqdm import tqdm

from function import NeoAdapter


neo = NeoAdapter(host="10.9.3.209", port="7687", password="12345678")

load_node = False
create_index = False
load_relationship = True

# node config
node_import_dir = "/home/dungnguyen/work/neo4j/data_migration/data/import/person_data"
node_labels = ["person", "data"]

# các trường của node sẽ được đưa vào database nếu chưa có node
create_node_properties = [
    "name",
    "id",
    "pagerank_2377",
    "total_actor_post_2377",
    "total_share_2377",
    "total_action_2377",
    "total_comment_2377",
    "pagerank_6586",
    "total_actor_post_6586",
    "total_share_6586",
    "total_action_6586",
    "total_comment_6586",
    "pagerank_6843",
    "total_actor_post_6843",
    "total_share_6843",
    "total_action_6843",
    "total_comment_6843"
]  # properties set only in "CREATE", not set in "MATCH"

# các trường của node sẽ được đưa vào database nếu đã có node với id thỏa mãn
match_node_properties = [
    "pagerank_2377",
    "total_actor_post_2377",
    "total_share_2377",
    "total_action_2377",
    "total_comment_2377",
    "pagerank_6586",
    "total_actor_post_6586",
    "total_share_6586",
    "total_action_6586",
    "total_comment_6586",
    "pagerank_6843",
    "total_actor_post_6843",
    "total_share_6843",
    "total_action_6843",
    "total_comment_6843"
]
pk_property = "neo4jImportId"
no_nodes = 1278150

# relationship config
rel_import_dir = "/home/dungnguyen/work/neo4j/data_migration/data/import/mutual_6843"
rel_labels = ["mutual_6843"]
node_pk_property = "neo4jImportId"
rel_start_property = "start_id"
rel_end_property = "end_id"
no_rels = 2321076


init_time = time.time()

if load_node:
    create_properties_query = ", ".join(
        [f"n.{n_property}=node.{n_property}" for n_property in create_node_properties]
    )
    match_properties_query = ", ".join(
        [f"n.{n_property}=node.{n_property}" for n_property in match_node_properties]
    )

    start_time = time.time()
    for i in tqdm(range(0, no_nodes, 50000), desc="import nodes"):
        filepath = f"{node_import_dir}/all_{'_'.join(node_labels)}_{str(i).zfill(7)}_{str(i+50000).zfill(7)}.json"
        query = f"""
            CALL apoc.periodic.iterate(
                'CALL apoc.load.json("{filepath}") YIELD value UNWIND value.data AS node RETURN node',
                'MERGE (n:{':'.join(node_labels)} {{{pk_property}:node.{pk_property}}}) ON CREATE SET {create_properties_query} ON MATCH SET {match_properties_query}',
                {{batchSize:1000}}
            )
        """
        neo.run_query(query)
    print(f"Fininised importing nodes: {time.time() - start_time}")


if create_index:
    start_time = time.time()
    neo.run_query(
        "CREATE INDEX person_import_index FOR (u:person) ON (u.neo4jImportId)"
    )
    neo.run_query("CREATE INDEX person_search_index FOR (u:person) ON (u.id)")
    print(f"Fininised creating index: {time.time() - start_time}")


if load_relationship:
    with open(f"{rel_import_dir}/rel_metadata.json") as f:
        rel_properties = json.load(f).get("rel_properties", [])

    start_node_query = (
        f"s_n:{':'.join(node_labels)} {{{node_pk_property}:rel.{rel_start_property}}}"
    )
    end_node_query = (
        f"e_n:{':'.join(node_labels)} {{{node_pk_property}:rel.{rel_end_property}}}"
    )
    rel_properties_query = ", ".join(
        [f"{r_property}:rel.{r_property}" for r_property in rel_properties]
    )

    start_time = time.time()
    for i in tqdm(range(0, no_rels, 50000), desc="import rels"):
        filepath = f"{rel_import_dir}/all_{'_'.join(rel_labels)}_{str(i).zfill(7)}_{str(i+50000).zfill(7)}.json"
        query = f"""
            CALL apoc.periodic.iterate(
                'CALL apoc.load.json("{filepath}") YIELD value UNWIND value.data AS rel RETURN rel',
                'MATCH ({start_node_query}),({end_node_query}) MERGE (s_n)-[r:{":".join(rel_labels)} {{{rel_properties_query}}}]->(e_n)',
                {{batchSize:5000}}
            )
        """
        neo.run_query(query)
    print(f"Fininised importing relationships: {time.time() - start_time}")


print(f"\nTotal runtime: {time.time() - init_time}")
