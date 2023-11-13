import time

import pandas as pd
from py2neo import Graph


class NeoAdapter(object):
    def __init__(self, host="localhost", port="7688", password="123!@#"):
        """
        Initialize a NeoAdapter instance.

        Args:
            host (str): Hostname or IP address of the Neo4j database server.
            port (str): Port number for the Neo4j database server.
            password (str): Password for authentication.

        """

        self.__graph = Graph(host=host, port=port, password=password)

    def run_query(self, query=None, filepath=None):
        """
        Run a Cypher query on the Neo4j graph database.

        Args:
            query (str, optional): The Cypher query to run.
            filepath (str, optional): Path to a file containing the Cypher query.

        Returns:
            Result: The result of the query.
        """

        if filepath:
            with open(filepath, "r") as file:
                query = file.read()

        res = self.__graph.run(query)
        return res

    def clear_database(self):
        """
        Clear the entire Neo4j database including graphs and indexes.
        """

        ls_graph = self.list_graph()
        for graph in ls_graph:
            self.drop_graph(graph)

        query = """
            CALL apoc.periodic.iterate(
                'MATCH (n) RETURN n', 
                'DETACH DELETE n', 
                { batchSize:1000 }
            )
        """
        self.run_query(query)

        index_info = self.run_query("SHOW INDEXES").data()
        ls_index = [index["name"] for index in index_info]
        for index in ls_index:
            self.run_query(f"DROP INDEX {index}")

        return 1

    def drop_nodes_with_label(self, label: str):
        """
        Drop nodes with specific label.
        """

        query = f"""
            CALL apoc.periodic.iterate(
                'MATCH (n:{label}) RETURN n', 
                'DETACH DELETE n', 
                {{ batchSize:1000 }}
            )
        """
        res = self.run_query(query)

        return res

    def drop_property(
        self, property_name: str, label: str, dtype="node", directed=True
    ):
        """
        Drop a property from nodes or relationships of a given label.

        Args:
            property_name (str): The name of the property to drop.
            label (str): The label of the nodes or relationships to target.
            dtype (str, optional): The type of element to target ("node" or "relationship").
            directed (bool, optional): Whether the relationship is directed or not.

        Returns:
            Result: The result of the operation.
        """

        assert (
            isinstance(property_name, str) and len(property_name) > 0
        ), "invalid property_name"
        assert isinstance(label, str) and len(label) > 0, "invalid label"
        assert dtype in ["node", "nelationship"], "invalid type"

        relationship_direction = ">" if directed else ""

        query = (
            f"""
            CALL apoc.periodic.iterate(
                'MATCH (u:{label} WHERE u.{property_name} IS NOT NULL) RETURN u',
                'REMOVE u.{property_name}',
                {{batchSize:1000}}
            )
            YIELD batches, total
            RETURN batches, total
        """
            if dtype == "node"
            else f"""
            CALL apoc.periodic.iterate(
                'MATCH ()-[r:{label} WHERE r.{property_name} IS NOT NULL]-{relationship_direction}() RETURN r',
                'REMOVE r.{property_name}',
                {{batchSize:1000}}
            )
            YIELD batches, total
            RETURN batches, total
        """
        )

        res = self.run_query(query)
        return res

    def drop_relationship(self, relationship: str):
        """
        Drop all relationships which have a specific label.

        Args:
            relationship (str): The label of relationship to drop.

        Returns:
            Result: The result of the operation.
        """

        query = f"""
            CALL apoc.periodic.iterate(
                'MATCH p = ()-[r:{relationship}]->() RETURN r',
                'DETACH DELETE r',
                {{batchSize:1000}}
            )
            YIELD batches, total
            RETURN batches, total
        """
        res = self.run_query(query)
        return res

    def list_graph(self):
        """
        List all graph names available in the catalog.
        """

        query = """
            CALL gds.graph.list()
            YIELD graphName
            RETURN graphName;
        """
        res = self.run_query(query).data()
        res = [gds_graph["graphName"] for gds_graph in res]
        return res

    def drop_graph(self, graph_name):
        """
        Drop a graph in catalog by its name.
        """

        query = f"""
            CALL gds.graph.drop('{graph_name}')
            YIELD graphName;
        """
        res = self.run_query(query)
        return res

    def calculate_PageRank(self, graph_name, top_k=20, to_pandas=True):
        """
        Calculate PageRank scores for nodes in a graph.

        Args:
            graph_name (str): The name of the graph to calculate PageRank on.
            top_k (int, optional): Number of top nodes to retrieve.
            to_pandas (bool, optional): Convert the result to a pandas DataFrame.

        Returns:
            DataFrame or Result: If to_pandas is True, returns a DataFrame with PageRank scores and node identifiers. Otherwise, returns the raw result.
        """

        start_time = time.time()
        query = (
            """
            CALL gds.pageRank.stream('"""
            + graph_name
            + """', {
                maxIterations: 20,
                dampingFactor: 0.85,
                relationshipWeightProperty: 'weight'
            })
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).uid AS uid, score
            ORDER BY score DESC
            LIMIT """
            + str(top_k)
            + """;
        """
        )
        res = self.run_query(query)
        print(f"time_calculate_PageRank: {time.time() - start_time}")

        if to_pandas:
            res = pd.DataFrame(res.data())

        return res
