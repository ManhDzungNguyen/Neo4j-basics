import json

import jsonlines
from tqdm import tqdm

export_files_neo4j_version = "3.4"
NEO4J_OLD_VERSIONS = ["3.4"]

raw_node_dir = "/home/dungnguyen/work/neo4j/archive/neo4j_3_4_5/person_data"
formatted_node_dir = "/home/dungnguyen/work/neo4j/data_migration/data/import/person_data"

node_labels = ["person", "data"]
node_properties = [
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
    "total_comment_6686",
    "pagerank_6843",
    "total_actor_post_6843",
    "total_share_6843",
    "total_action_6843",
    "total_comment_6843"
]
no_nodes = 1278150
metadata = {}


metadata["node_properties"] = node_properties
with open(f"{formatted_node_dir}/node_metadata.json", "w", encoding="utf8") as f:
    json.dump(metadata, f, ensure_ascii=False)


# convert neo4j 3.4.5 apoc.export.json file format to neo4j 5.11.0 apoc.load.json file format
for i in tqdm(range(0, no_nodes, 50000), desc="convert nodes"):
    filename = (
        f"all_{'_'.join(node_labels)}_{str(i).zfill(7)}_{str(i+50000).zfill(7)}.json"
    )
    node_data = {"data": []}
    count = 0
    with jsonlines.open(f"{raw_node_dir}/{filename}", mode="r") as reader:
        for row in reader:
            item = row["n"] if export_files_neo4j_version in NEO4J_OLD_VERSIONS else row
            record = {"neo4jImportId": item["id"]}
            for n_property in node_properties:
                record[n_property] = item["properties"].get(n_property)

            node_data["data"].append(record)

    with open(f"{formatted_node_dir}/{filename}", "w", encoding="utf8") as f:
        json.dump(node_data, f, ensure_ascii=False)
