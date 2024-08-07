import graphviz
from clients.runpod_client import RunpodClient
from clients.inference_client import InferenceClient
import json
import re
from transformers import AutoTokenizer
import html
from config import Config

RELATION_GRAPH_PROMPT = """## Relation Extraction Instructions

You are an expert entity relation extractor for documents.

### Task Description

You are tasked with building a knowledge graph (also referred to as a relation graph) which captures all the key relations between entities in a document. 
You will be given a document with entities extracted using NLP. The extracted entities are represented using angled bracket tags, for example `<DATE>17 December 2020</DATE>` represents a detected date. 
Your task is to extract ALL the relations between ALL the tagged entities in the text in a JSON format.

### JSON Output Format

The JSON should include the following fields:
 - `relation`: The relation between the entities, named in all caps and in simple directional format (e.g., CONTRACTED_WITH).
 - `entity1`: An object representing the first entity in the relation with an abbreviated label and its type.
 - `entity2`: An object representing the second entity in the relation with an abbreviated label and its type.
 - `additional_info`: Additional information about the relation, including a description.

**Relation labelling:** Relations should be named in all caps and in simple directional format.
 - The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
 - The graph is undirect so where possible try to avoid naming the relations in a way that would imply a one way directed relation
 - If a relation between 2 entities with the same relation label already exists in the graph do not add a new relation even if the description is different.
 - Do not create relations between an entity and itself.

**Entities labelling**: Entities should be proper nouns.
 - When extracting entities, it's vital to ensure consistency.
 - Entities should be short proper nouns.
 - Entites cannot be abstract terms like Nil, None, Null, or anything of that sort.
 
**Consistency:** When extracting entities, it's vital to ensure consistency.
 - An entity, such as "John Doe", could be referred to by different names or pronouns (e.g., "Joe", "John", "Mr. Doe", "he") between the given text and the existing relations in the graph. Always use the same identifier as already existing within the graph if the entity already exists, otherwise use the most copmlete identifier for that entity, in this using case use "John Doe".
 - If a similar relation already exists try to reuse the same relation label wherever appropriate.
 
### JSON Output Example

```json
[
  {
    "relation": "CONTRACTED_WITH",
    "entity1": {"entity": "Carmichael", "type": "PETITIONER"},
    "entity2": {"entity": "OneSteel", "type": "ORG"},
    "additional_info": {
      "description": "The appellant ('Carmichael', the shipper) contracted with the second respondent (OneSteel) for the manufacture and supply of head-hardened steel rails."
    }
  }
]
```
### Response Format
ONLY RESPOND IN JSON!

"""

EXAMPLES_PROMPT = """### Existing Entity Relations
{existing_relations}

"""

GENERATION_PROMPT = """### Text for Entity Relation Extraction
Here is the text from which to extract the entity relations.

{text}

### Task
1. Extract relations for the detected entities. 
2. For any new entities added to the graph try to extrapolate the relations between them and the existing entities whenever possible.
3. Create any new implicit relations based on the existing relations and info provided in the graph.
If any of the following entities are the same as one of the existing extracted entities but under a different or similar name then use the already existing entity name in the graph. Return the solution to all tasks in a single json list."""


class RelationProcessor:
    def __init__(self):
        if Config.RUNPOD_SERVERLESS:
            self.gpt_client = RunpodClient()
        else:
            self.gpt_client = InferenceClient()
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.seed = 21

    def extract_json_from_text(self, text):
        # Define a regular expression pattern to match each dictionary
        pattern = r'{\s*"relation":\s*"[^"]+",\s*"entity1":\s*{[^}]+},\s*"entity2":\s*{[^}]+},\s*"additional_info":\s*{[^}]+}\s*}'

        # Find all matches of the pattern in the text
        matches = re.findall(pattern, text, re.DOTALL)
        return json.loads(f'[{",".join(matches)}]')
    
    def extract_entities_from_text(self, text):
        pattern = r'<.*?>(.*?)<\/.*?>'
        matches = re.findall(pattern, text)
        return matches

    def strip_angle_brackets(self, entity):
        parts = entity.split(">")
        return parts[-1] if len(parts) == 1 else parts[1].split("<")[0]

    def json_to_dot(self, json_data):
        """
        Convert json entity relation into a graphviz DOT graph
        """
        dot = "digraph G {\n"

        for item in json_data:
            relation = item["relation"]
            entity1 = self.strip_angle_brackets(item["entity1"]["entity"])
            entity2 = self.strip_angle_brackets(item["entity2"]["entity"])
            description = html.escape(item["additional_info"]["description"])

            dot += f'"{entity1}" -> "{entity2}" [label="{relation}" tooltip="{description}" labeltooltip="{description}"];\n'

        dot += "}"
        
        return dot

    def build_up_relation_graph(
        self, text: str, existing_relations: str, max_new_tokens: int
    ):
        """
        This funciton is meant for iteratively building up the relation graph incrementally rather than all at once. Will return {"graph_svg": None, "relation_json": None} when finished
        """
        relation_graph_dict = self.get_relation_graph(
            text, existing_relations, max_new_tokens
        )
        return relation_graph_dict

    def get_relation_graph(self, text: str, existing_relations: str = "", max_new_tokens: int = 2048):
        entities = self.extract_entities_from_text(text)
        generate_relations_json_prompt = RELATION_GRAPH_PROMPT
        generate_relations_json_prompt += EXAMPLES_PROMPT.format(existing_relations=existing_relations)
        generate_relations_json_prompt += GENERATION_PROMPT.format(text=text)
        
        messages = [{"role": "user", "content": generate_relations_json_prompt}]

        chat_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        chat_prompt += " ["
        print(chat_prompt)
        gpt_response = self.gpt_client.get_gpt_response({}, generation_args={"max_tokens": max_new_tokens, "seed": self.seed}, prompt=chat_prompt)
        print("====")
        print(gpt_response)
        relations_json = self.extract_json_from_text(existing_relations + "\n" + gpt_response)
        
        dot_graph = self.json_to_dot(relations_json)

        dot_graph = dot_graph.replace("}", 'rankdir="LR";}')

        # Render the graph from the DOT representation
        graph = graphviz.Source(dot_graph)

        # Convert the graph to SVG format
        graph_svg = graph.pipe(format="svg").decode("utf-8").strip()

        return {"graph_svg": graph_svg, "relation_json": relations_json}


relation_processor = RelationProcessor()
