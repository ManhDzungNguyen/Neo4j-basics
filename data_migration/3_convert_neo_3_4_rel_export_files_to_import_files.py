import json

import jsonlines
from tqdm import tqdm

# export_files_neo4j_version = "3.4.5"
export_files_neo4j_version = "3.4.5"
NEO4J_OLD_VERSIONS = ["3.4.5"]

raw_rel_dir = "/home/dungnguyen/work/neo4j/archive/neo4j_3_4_5/mutual_6843"
formatted_rel_dir = "/home/dungnguyen/work/neo4j/data_migration/data/import/mutual_6843"
rel_labels = ["mutual_6843"]
no_rels = 2321076

rel_properties = []
metadata = {}


# get all possible relationship properties
for i in tqdm(range(0, no_rels, 50000), desc="get rel properties"):
    with jsonlines.open(
        f"{raw_rel_dir}/all_{'_'.join(rel_labels)}_{str(i).zfill(7)}_{str(i+50000).zfill(7)}.json",
        mode="r",
    ) as reader:
        for row in reader:
            item = row["r"] if export_files_neo4j_version in NEO4J_OLD_VERSIONS else row
            rel_properties += list(item["properties"].keys())
            rel_properties = list(set(rel_properties))

rel_properties.sort()
metadata["rel_properties"] = rel_properties
with open(f"{formatted_rel_dir}/rel_metadata.json", "w", encoding="utf8") as f:
    json.dump(metadata, f, ensure_ascii=False)


# convert neo4j 3.4.5 apoc.export.json file format to neo4j 5.11.0 apoc.load.json file format
for i in tqdm(range(0, no_rels, 50000), desc="convert rels"):
    filename = (
        f"all_{'_'.join(rel_labels)}_{str(i).zfill(7)}_{str(i+50000).zfill(7)}.json"
    )
    rel_data = {"data": []}
    count = 0
    with jsonlines.open(f"{raw_rel_dir}/{filename}", mode="r") as reader:
        for row in reader:
            item = row["r"] if export_files_neo4j_version in NEO4J_OLD_VERSIONS else row
            record = {
                "start_id": item["start"]["id"],
                "end_id": item["end"]["id"],
            }
            for r_property in rel_properties:
                record[r_property] = item["properties"].get(r_property)

            rel_data["data"].append(record)

    with open(f"{formatted_rel_dir}/{filename}", "w", encoding="utf8") as f:
        json.dump(rel_data, f, ensure_ascii=False)
