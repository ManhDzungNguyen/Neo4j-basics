import sys

sys.path.append("/home/dungnguyen/work/Neo4j-social-network")

import time

from function import NeoAdapter


neo = NeoAdapter(host="10.9.3.209", port="7687", password="12345678")

init_time = time.time()
relationship_name = "rel_01"
start_year = 2018
start_month = 7
start_day = 1
end_year = 2018
end_month = 9
end_day = 1

start_year, start_month, start_day, end_year, end_month, end_day = (
    str(start_year),
    str(start_month),
    str(start_day),
    str(end_year),
    str(end_month),
    str(end_day),
)

res = neo.graph.run(
    """
MATCH (u:User)
WITH COLLECT(u) AS ls_user
UNWIND ls_user AS user1
CALL {
    WITH user1
    MATCH (user1)-[r1:COMMENTED WHERE date({year: """
    + start_year
    + """, month: """
    + start_month
    + """, day: """
    + start_day
    + """}) <= date(r1.first_cmt_time) < date({year: """
    + end_year
    + """, month: """
    + end_month
    + """, day: """
    + end_day
    + """})]->(post:Post)<-[r2:COMMENTED WHERE date({year: """
    + start_year
    + """, month: """
    + start_month
    + """, day: """
    + start_day
    + """}) <= date(r1.first_cmt_time) < date({year: """
    + end_year
    + """, month: """
    + end_month
    + """, day: """
    + end_day
    + """})]-(user2:User WHERE user1.uid < user2.uid)
    WITH user1, user2, COLLECT(DISTINCT post) AS commonPosts
    WITH user1, user2, SIZE(commonPosts) AS numberOfCommonPosts
    WHERE numberOfCommonPosts > 1
    MERGE (user1)-[r:"""
    + relationship_name
    + """]-(user2)
    SET r.weight = numberOfCommonPosts
} IN TRANSACTIONS OF 10 ROWS
"""
)
print(res)
print(f"runtime: {time.time() - init_time}")
