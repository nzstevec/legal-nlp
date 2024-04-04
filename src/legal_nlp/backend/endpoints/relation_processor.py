import graphviz
from clients.runpod_client import RunpodClient
import json
import re

class RelationProcessor:
    def __init__(self):
        self.gpt_client = RunpodClient()

    def extract_json_from_text(self, text):
        # Define a regular expression pattern to match each dictionary
        pattern = r'{\s*"relation":\s*"[^"]+",\s*"entity1":\s*{[^}]+},\s*"entity2":\s*{[^}]+},\s*"additional_info":\s*{[^}]+}\s*}'

        # Find all matches of the pattern in the text
        matches = re.findall(pattern, text, re.DOTALL)
        print(f'[{",".join(matches)}]')
        return json.loads(f'[{",".join(matches)}]')

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
You will be given a document with entities extracted using NLP. The extracted entities are represented using angled bracket tags, for example <DATE>17 December 2020</DATE> represents a detected date.
Please extract ALL the relations between ALL the entities in the text in a json format. The json should include the abbreviated relation, the relevant entity pair, and additional information about the relation.

Here is a sample for the output json schema:
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
ONLY RESPOND IN JSON!
Here is the text from which to extract the entity relations:\n"""
        
        generate_relations_json_prompt += text

        messages = [{"role": "user", "content": generate_relations_json_prompt}]
        gpt_response = self.gpt_client.get_gpt_response(messages, generation_args={"max_tokens": 4096})
        
        print(gpt_response)
        
        # Assume that scoti will return the entities wrapped in square brackets
        relations_json = self.extract_json_from_text(gpt_response)
        print(relations_json)
        dot_graph = self.json_to_dot(relations_json)

        # Render the graph from the DOT representation
        graph = graphviz.Source(dot_graph)

        # Convert the graph to SVG format
        graph_svg = graph.pipe(format="svg").decode("utf-8").strip()

        return {"graph_svg": graph_svg, "relation_json": relations_json}

relation_processor = RelationProcessor()
