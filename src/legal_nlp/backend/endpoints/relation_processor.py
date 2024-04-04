import graphviz
from clients.runpod_client import RunpodClient

class RelationProcessor:
    def __init__(self):
        pass

    def get_relation_graph(self, text: str):
         # Define the DOT representation of the graph
        dot_graph = """
        digraph G {
            "Carmichael" -> "OneSteel" [label="Contracted_With"];
            "OneSteel" -> "Whyalla" [label="Arranged_For_Shipment"];
            "Whyalla" -> "Mackay" [label="Shipped_To"];
            "BBC" -> "OneSteel" [label="Prepared_Stowage_Plan"];
            "OneSteel" -> "OneSteel's subcontractor" [label="Loaded_Onto_Ship"];
        }
        """

        # Render the graph from the DOT representation
        graph = graphviz.Source(dot_graph)

        # Convert the graph to SVG format
        graph_svg = graph.pipe(format="svg").decode("utf-8")

        return graph_svg

relation_processor = RelationProcessor()
