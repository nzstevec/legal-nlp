import graphviz
from clients.runpod_client import RunpodClient
import json

class RelationProcessor:
    def __init__(self):
        self.gpt_client = RunpodClient()

    def extract_json_from_text(self, raw_string):
        start_index = raw_string.find("[")
        end_index = raw_string.rfind("]") + 1

        if start_index != -1 and end_index != -1:
            json_string = raw_string[start_index:end_index]
            json_data = json.loads(json_string)
            return json_data
        else:
            return None

    def strip_angle_brackets(self, entity):
        parts = entity.split('>')
        return parts[-1] if len(parts) == 1 else parts[1].split('<')[0]

    def json_to_dot(self, json_data):
        """ 
            Convert json entity relation into a graphviz DOT graph
        """
        dot = "digraph G {\n"

        for item in json_data:
            relation = item['relation']
            entity1 = self.strip_angle_brackets(item['entity1']['entity'])
            entity2 = self.strip_angle_brackets(item['entity2']['entity'])

            dot += f'"{entity1}" -> "{entity2}" [label="{relation}"];\n'

        dot += "}"
        return dot

    def get_relation_graph(self, text: str):
             
        generate_relations_json_prompt = """You are an expert entity relation extractor for legal documents. 
Given the following piece of text with entities marked using angled bracket tags please extract any relevant relations between the entities in the following text in a json format. 
The json should include the abbreviated relation, the relevant entity pair, and additional information about the relation.

Here is a sample for the output json formatting:
```json
[
  {
  "relation": "Contracted_With",
  "entity1": {"entity": "<PETITIONER>Carmichael</PETITIONER>", "type": "Person"},
  "entity2": {"entity": "<ORG>OneSteel</ORG>", "type": "Organization"},
  "additional_info": {
    "description": "The appellant ('Carmichael', the shipper) contracted with the second respondent (OneSteel) for the manufacture and supply of head-hardened steel rails."
  }
]
```

Here is the text from which to extract the entity relations:\n"""
        
        generate_relations_json_prompt += text

        messages = [{"role": "user", "content": generate_relations_json_prompt}]
        gpt_response = self.gpt_client.get_gpt_response(messages, generation_args={"max_tokens": 4096})

        # Assume that scoti will return the entities wrapped in square brackets
        relations_json = self.extract_json_from_text(gpt_response)
        
        dot_graph = self.json_to_dot(relations_json)

        # Render the graph from the DOT representation
        graph = graphviz.Source(dot_graph)

        # Convert the graph to SVG format
        graph_svg = graph.pipe(format="svg").decode("utf-8").strip()

        return {"graph_svg": graph_svg, "relation_json": relations_json}

relation_processor = RelationProcessor()
