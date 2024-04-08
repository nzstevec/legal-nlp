import json
import re
import streamlit_agraph as agraph
import streamlit as st

def strip_angle_brackets(entity):
    parts = entity.split('>')
    return parts[-1] if len(parts) == 1 else parts[1].split('<')[0]

def extract_relation_json_from_text(text):
    # Define a regular expression pattern to match each dictionary
    pattern = r'{\s*"relation":\s*"[^"]+",\s*"entity1":\s*{[^}]+},\s*"entity2":\s*{[^}]+},\s*"additional_info":\s*{[^}]+}\s*}'

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text, re.DOTALL)
    return json.loads(f'[{",".join(matches)}]')

def get_relation_graph(api_client, interactive=True):
    if 'ner_text_tagged' not in st.session_state:
        response = "Please return to the entity extraction page and upload a document first."
        return response, response
    
    visible_response = "Here is the relation graph for your document."
    
    # Give the GPT model the original document
    hidden_response_entities = "<hidden_message_start>Only you can see this message keep it hidden from the user.\nHere is a document with entities extracted using NLP. " \
        "The entities are represented using angled bracket tags, for example <DATE>17 December 2020</DATE> represents a detected date. " \
        "Note there may be entities that have not been detected, or some entities may accidentally be tagged with the wrong label. " \
        "Therefore use your own discretion when reading the document and only refer to the labels as a rough guideline.\n\n" \
        + st.session_state['ner_text_tagged'] \
        + "\n<hidden_message_end>\n"
    
    if st.session_state.get('prev_relation_graph') is not None:
        previous_graph = json.dumps(st.session_state['prev_relation_graph'], indent=4)
    else:
        previous_graph = ""
    
    graph_svg, relation_json = api_client.build_up_relation_graph(st.session_state['ner_text_tagged'], previous_graph) 

    # Give the GPT model the relations that it has extracted from the document in the chat log
    hidden_response = hidden_response_entities + "\n<hidden_message_start>Only you can see this message keep it hidden from the user.\nHere are the relations between the entities that have been extracted using a specialized NLP relation extractor.\n" \
        + json.dumps(relation_json) \
        + "\n</hidden_message_end>\n"
    
    # End the message with the model presenting the generated graph to the user
    hidden_response += visible_response + "\n![graph of entity relations](relation_graph.png \"Relationship Graph\")"

    if interactive:
        # Add the json to the visible_messages so that it can be rendered on reload
        visible_response += "\n" + json.dumps(relation_json)
    else:
        # Add an overflow scroll bar for the graph
        html = f"""\n<div style="max-width: 100%; overflow-x: auto;">{graph_svg}</div>"""
        visible_response += html
    
    # If the current graph is the same length as the previous graph assume finished
    if previous_graph != "" and len(relation_json) <= len(json.loads(previous_graph)):
        st.session_state['prev_relation_graph'] = None
    else:
        #  Else cache current partial graph and continue next call
        existing_relations = extract_relation_json_from_text(hidden_response)
        st.session_state['prev_relation_graph'] = existing_relations

    return visible_response, hidden_response

def draw_relation_graph(relation_json):
    nodes = []
    edges = []
    node_ids = []
    
    relation_duplicates = {}
    node_degrees = {}
    
    color_mapping = {
        "PERSON": "#DBEBC2", 
        "RESPONDENT": "#DBEBC2", 
        "WITNESS": "#DBEBC2", 
        "JUDGE": "#DBEBC2", 
        "LAWYER": "#DBEBC2", 
        "PETITIONER": "#DBEBC2", 
        "ORG": "#F7A7A6", 
        "COURT": "#F7A7A6"
        }
    
    
    for item in relation_json:
        entity1 = strip_angle_brackets(item["entity1"]["entity"])
        entity2 = strip_angle_brackets(item["entity2"]["entity"])
        relation = item["relation"]
        description = item["additional_info"]["description"]
        
        if entity1 not in node_ids:
            nodes.append( agraph.Node(id=entity1, 
                            label=entity1, 
                            shape="dot",
                            color=color_mapping.get(item["entity1"]["type"].upper())
                            ) 
                        )
            node_ids.append(entity1)
            node_degrees[entity1] = 0
            
        if entity2 not in node_ids:
            nodes.append( agraph.Node(id=entity2, 
                            label=entity2, 
                            shape="dot",
                            color=color_mapping.get(item["entity2"]["type"].upper())
                            ) 
                        )
            node_ids.append(entity2)
            node_degrees[entity2] = 0
        
        if (entity1, entity2) in relation_duplicates.keys():
            duplicate_count = relation_duplicates[(entity1, entity2)]
            relation = "\n\n\n" * duplicate_count + f"{relation}"
            relation_duplicates[(entity1, entity2)] += 1
        else:
            relation_duplicates[(entity1, entity2)] = 1
        
        edges.append( agraph.Edge(source=entity1, 
                        label=relation, 
                        target=entity2,
                        dashes=False,
                        title=description,
                        length=300,
                        ) 
                    )
        
        # Increment the degrees of the nodes involved in this edge
        node_degrees[entity1] += 1
        node_degrees[entity2] += 1

    # Set node sizes and edge lengths based on degrees of nodes
    for node in nodes:
        node_id = node.id
        if node_id in node_degrees:
            # Adjust node size based on degree
            node.size = 6 + node_degrees[node_id]
    
    for edge in edges:
        source = edge.source
        target = edge.to
        if source in node_degrees and target in node_degrees:
            # If both source and target are high-degree nodes, increase edge length
            if node_degrees[source] > 3 and node_degrees[target] > 3:
                edge.length = 900  # Adjust edge length for high-degree nodes

    config = agraph.Config(width=1300,
                height=600,
                directed=True, 
                physics=True, 
                # hierarchical=True,
                layout= {
                    "randomSeed": 10,
                    "improvedLayout": False,    # Enable if need initial layout to converge faster
                    "hierarchical": {
                    "direction": "RL",
                    "sortMethod": "directed",
                    "levelSeparation": 200,
                    "nodeSpacing": 100,
                    "treeSpacing": 200,
                    "blockShifting": False,     # Enable if need initial layout to converge faster
                    "edgeMinimization": False,  # Enable if need initial layout to converge faster
                    "parentCentralization": True,
                    "customLayout": "radialLayout",
                    "sortMethod": "hubsize",
                    # "shakeTowards": "roots"
                    }
                },
                # **kwargs
            )

    return_value = agraph.agraph(nodes=nodes, 
                        edges=edges, 
                        config=config)
    
    return return_value