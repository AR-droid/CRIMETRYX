from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm

# === Neo4j Credentials ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j123"

# === Class to Manage Neo4j Graph ===
class Neo4jGraphManager:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j driver connection."""
        self._driver.close()

    def create_nodes(self, nodes):
        """Create nodes and relationships in the Neo4j database."""
        with self._driver.session() as session:
            for n in tqdm(nodes, desc="Creating nodes"):
                # Validate input data
                if not n.get("SuspectID") or not n.get("PredictedCrimeType"):
                    print(f"Skipping invalid record: {n}")
                    continue

                # Create nodes and relationships
                session.execute_write(self._create_node, n)

    def del_nodes(self, label, mode):
        """Delete nodes based on label and mode."""
        with self._driver.session() as session:
            if 'node' in mode:
                session.execute_write(self._delete_nodes, label)
            else:
                session.execute_write(self._delete_visu_nodes, label)

    def transGraph(self, delta, delta2=None):
        """Perform graph transformations."""
        with self._driver.session() as session:
            session.execute_write(self._duplicate_node, 2, 4)
            session.execute_write(self._transport_part1, delta)
            if delta2 is not None:
                return session.execute_write(self._transport_part2, delta2)

    def get_graph_data(self):
        """Fetch graph data from Neo4j and return nodes and links."""
        query = """
        MATCH (s:Suspect)-[r]->(n)
        RETURN s.id AS source, type(r) AS relation, 
               CASE 
                   WHEN exists(n.id) THEN n.id
                   WHEN exists(n.name) THEN n.name
                   WHEN exists(n.description) THEN n.description
                   ELSE "Unknown"
               END AS target
        """
        links = []
        nodes = set()

        with self._driver.session() as session:
            results = session.execute_read(lambda tx: tx.run(query).data())

        for record in results:
            src = record['source']
            tgt = record['target']
            rel = record['relation']
            links.append({"source": src, "target": tgt, "label": rel})
            nodes.add(src)
            nodes.add(tgt)

        return {
            "nodes": [{"id": n} for n in nodes],
            "links": links
        }

    @staticmethod
    def _create_node(tx, node):
        """Create a node and its relationships in Neo4j."""
        tx.run("""
            MERGE (s:Suspect {id: $sid})
            MERGE (c:CrimeType {name: $ctype})
            MERGE (w:Weapon {name: $weapon})
            MERGE (m:MO {description: $mo})
            MERGE (l:Location {id: $loc})

            MERGE (s)-[:LIKELY_TO_COMMIT]->(c)
            MERGE (s)-[:LIKELY_TO_USE]->(w)
            MERGE (s)-[:MATCHED_WITH_PATTERN]->(m)
            MERGE (s)-[:ACTIVE_IN]->(l)
        """, sid=node['SuspectID'],
             ctype=node['PredictedCrimeType'],
             weapon=node['LikelyWeapon'],
             mo=node['MatchedMOExamples'],
             loc=node['LocationID'])

    @staticmethod
    def _delete_nodes(tx, label):
        """Delete all nodes of a given label."""
        tx.run(f"MATCH (n:{label}) DETACH DELETE n")

    @staticmethod
    def _delete_visu_nodes(tx, label):
        """Delete nodes with a 'visu' property."""
        tx.run(f"MATCH (n:{label}) WHERE exists(n.visu) DETACH DELETE n")

    @staticmethod
    def _duplicate_node(tx, src, dst):
        """Placeholder for duplicating nodes."""
        print(f"Duplicating from node {src} to {dst} (placeholder)")

    @staticmethod
    def _transport_part1(tx, delta):
        """Placeholder for transport part 1."""
        print(f"Transport part 1 using delta {delta} (placeholder)")

    @staticmethod
    def _transport_part2(tx, delta2):
        """Placeholder for transport part 2."""
        print(f"Transport part 2 using delta2 {delta2} (placeholder)")


# === Ingesting Data ===
if __name__ == "__main__":
    # Load prediction CSV
    df = pd.read_csv("../data/rule_based_predictions.csv").fillna("Unknown")
    df.replace(r'^\s*$', 'Unknown', regex=True, inplace=True)

    # Add dummy location from suspect ID
    df['LocationID'] = df['SuspectID'].apply(lambda x: "L" + x[-2:])

    # Convert to dict records
    nodes = df.to_dict(orient="records")

    # Ingest into Neo4j
    print("🔗 Connecting to Neo4j...")
    manager = Neo4jGraphManager(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    print("🚀 Creating graph from rule-based predictions...")
    manager.create_nodes(nodes)

    # Fetch graph data after ingestion
    print("🔍 Fetching graph data from Neo4j...")
    graph_data = manager.get_graph_data()
    print("Nodes:", graph_data["nodes"])
    print("Links:", graph_data["links"])

    manager.close()
    print("✅ Graph creation and data fetching completed successfully.")