import graphviz
from clients.runpod_client import RunpodClient
import json
import re
from transformers import AutoTokenizer
import html

RELATION_GRAPH_PROMPT = """## Legal Relation Extraction Instructions

You are an expert entity relation extractor for legal documents.

### Task Description

You will be given a legal document with entities extracted using NLP. The extracted entities are represented using angled bracket tags, for example `<DATE>17 December 2020</DATE>` represents a detected date. 
Your task is to extract ALL the relations between ALL the tagged entities in the text in a JSON format.

### JSON Output Format

The JSON should include the following fields:
 - `relation`: The relation between the entities, named in all caps and in simple directional format (e.g., CONTRACTED_WITH).
 - `entity1`: An object representing the first entity in the relation with an abbreviated label and its type.
 - `entity2`: An object representing the second entity in the relation with an abbreviated label and its type.
 - `additional_info`: Additional information about the relation, including a description.
 
**Relation labelling:** Relations should be named in all caps and in simple directional format.
 - The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
 - Make sure to capture the direction of the relationship as well, for example in the relation Carmichael CONTRACTED_WITH OneSteel, Carmichael should be `entity1` and OneSteel should be `entity2`.

**Entities labelling**: Entities should be proper nouns.
 - **Allowed entity types:** JUDGE, COURT, GPE, RESPONDENT, DATE, WITNESS, PRECEDENT, CASE_NUMBER, LAWYER, PROVISION, STATUTE, PETITIONER, ORG, PERSON, OTHER
 - When extracting entities, it's vital to ensure consistency.
 - DO NOT make entity labels longer than 4 words unless it is either a statue, provision or a precedent. In which case you should quote the entity name as is given in the text.
 - Entities should be short proper nouns.
 - Statues, provisions, and references to precedent cases are entities.
 
**Consistency:** When extracting entities, it's vital to ensure consistency.
 - If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"), always use the most complete identifier for that entity throughout the relation graph. In this example, use "John Doe" as the entity name. Remember, the relation graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial. 
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

### Text for Entity Relation Extraction
Here is the text from which to extract the entity relations:\n"""


class RelationProcessor:
    def __init__(self):
        self.gpt_client = RunpodClient()
<<<<<<< 946e7982f09c6259a1531cd71fa418e2090db0e5
        self.tokenizer = AutoTokenizer.from_pretrained(
            "mistralai/Mixtral-8x7B-Instruct-v0.1"
        )
=======
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.seed = 21
>>>>>>> 29377974961ae779a6512301224f05527dafc73b

    def extract_json_from_text(self, text):
        # Define a regular expression pattern to match each dictionary
        pattern = r'{\s*"relation":\s*"[^"]+",\s*"entity1":\s*{[^}]+},\s*"entity2":\s*{[^}]+},\s*"additional_info":\s*{[^}]+}\s*}'

        # Find all matches of the pattern in the text
        matches = re.findall(pattern, text, re.DOTALL)
        return json.loads(f'[{",".join(matches)}]')

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
<<<<<<< 946e7982f09c6259a1531cd71fa418e2090db0e5

        print(dot)
=======
        
>>>>>>> 29377974961ae779a6512301224f05527dafc73b
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

<<<<<<< 946e7982f09c6259a1531cd71fa418e2090db0e5
    def get_relation_graph(
        self, text: str, existing_relations: str = "", max_new_tokens: int = 2048
    ):

        # NOTE: I think the key to improving this is to improve the entities extracted. Some of them are low quality, which result in
        # seriously whacky relationships being defined
        generate_relations_json_prompt = """You are an expert entity relation extractor for legal documents. 
You will be given a document with entities extracted using NLP. The extracted entities are represented using angled bracket tags, for example <DATE>17 December 2020</DATE> represents a detected date.
Please extract ALL the relations between the tagged entities in the text in a json format. The json should include the abbreviated relation, the relevant entity pair, and additional information about the relation.
Make sure to capture the direction of the relationship as well, for example in the relation Carmichael Contracted_With OneSteel, Carmichael should be entity1 and OneSteel should be entity2.
The relationships you define will be used to build a knowledge graph to inform key officials. You must be accurate, defining clear and consistent relationships.
You should only use the entities which are appropriate. An entity should be clear, concise, and non duplicated. The goal is to produce an informative knowledge graph, so not all entities are required.

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

=======
    def get_relation_graph(self, text: str, existing_relations: str = "", max_new_tokens: int = 2048):
        generate_relations_json_prompt = RELATION_GRAPH_PROMPT
        
>>>>>>> 29377974961ae779a6512301224f05527dafc73b
        generate_relations_json_prompt += text

        messages = [{"role": "user", "content": generate_relations_json_prompt}]

        chat_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # If we have an exisint relation dict that we're extending start off the assistant response with it
        existing_relations_prompt = ""
        if len(existing_relations) > 0:
            indented_relations_dict = json.dumps(
                json.loads(existing_relations), indent=4
            )
            # Remove closing bracket and add comma to prompt model to continue
            existing_relations_prompt = (
                indented_relations_dict.split("]")[0].strip() + ","
            )
            chat_prompt += " " + existing_relations_prompt

<<<<<<< 946e7982f09c6259a1531cd71fa418e2090db0e5
        gpt_response = self.gpt_client.get_gpt_response(
            {}, generation_args={"max_tokens": max_new_tokens}, prompt=chat_prompt
        )

=======
        gpt_response = self.gpt_client.get_gpt_response({}, generation_args={"max_tokens": max_new_tokens, "seed": self.seed}, prompt=chat_prompt)
        
>>>>>>> 29377974961ae779a6512301224f05527dafc73b
        # Assume that scoti will return the entities wrapped in square brackets
        relations_json = self.extract_json_from_text(
            existing_relations_prompt + gpt_response
        )
        dot_graph = self.json_to_dot(relations_json)

        dot_graph = dot_graph.replace("}", 'rankdir="LR";}')

        # Render the graph from the DOT representation
        graph = graphviz.Source(dot_graph)

        # Convert the graph to SVG format
        graph_svg = graph.pipe(format="svg").decode("utf-8").strip()

        return {"graph_svg": graph_svg, "relation_json": relations_json}


relation_processor = RelationProcessor()
