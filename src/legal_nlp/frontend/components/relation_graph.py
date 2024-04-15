import json
import re
import streamlit_agraph as agraph
import streamlit as st

MAX_ITERS_PER_CHUNK = 5

def strip_angle_brackets(entity):
    parts = entity.split('>')
    return parts[-1] if len(parts) == 1 else parts[1].split('<')[0]


def extract_relation_json_from_text(text):
    # Define a regular expression pattern to match each dictionary
    pattern = r'{\s*"relation":\s*"[^"]+",\s*"entity1":\s*{[^}]+},\s*"entity2":\s*{[^}]+},\s*"additional_info":\s*{[^}]+}\s*}'

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text, re.DOTALL)
    return json.loads(f'[{",".join(matches)}]')


def chunk_text(text, min_chunk_size=2000):
    chunked_text = text.split(".")
    chunks = []
    
    i = 0
    while i < len(chunked_text):
        chunk = ""
        while len(chunk) < min_chunk_size or "</" not in chunk:
            if i >= len(chunked_text):
                break
            if len(chunked_text[i]) > 0:
                chunk += chunked_text[i] + "."
            i += 1
            
        if len(chunk) > 0:
            chunks.append(chunk)
    
    return chunks


def get_relation_graph(api_client, interactive=True):
    if 'ner_text_tagged' not in st.session_state or len(st.session_state['ner_text_tagged']) < 4:
        response = "Please return to the entity extraction page and upload a document first."
        return response, response
    
    visible_response = "Here is the relation graph for your document."
    
    graph_building_cache = st.session_state.get('graph_building_cache')
    if graph_building_cache is None:
        graph_building_cache = {
            'current_relation_graph': "[]",
            'chunks': chunk_text(st.session_state['ner_text_tagged']),
            'chunk_iters': 0
        }
    
    # Give the GPT model the original document
    hidden_response_entities = "<hidden_message_start>Only you can see this message keep it hidden from the user.\nHere is a document with entities extracted using NLP. " \
        "The entities are represented using angled bracket tags, for example <DATE>17 December 2020</DATE> represents a detected date. " \
        "Note there may be entities that have not been detected, or some entities may accidentally be tagged with the wrong label. " \
        "Therefore use your own discretion when reading the document and only refer to the labels as a rough guideline.\n\n" \
        + st.session_state['ner_text_tagged'] \
        + "\n<hidden_message_end>\n"
    
    graph_svg, relation_json = api_client.build_up_relation_graph(graph_building_cache['chunks'][0], graph_building_cache['current_relation_graph']) 

    # Give the GPT model the relations that it has extracted from the document in the chat log
    hidden_response = hidden_response_entities + "\n<hidden_message_start>Only you can see this message keep it hidden from the user.\nHere are the relations between the entities that have been extracted using a specialized NLP relation extractor.\n" \
        + json.dumps(relation_json, indent=4) \
        + "\n</hidden_message_end>\n"
    
    # End the message with the model presenting the generated graph to the user
    hidden_response += visible_response + "\n![graph of entity relations](relation_graph.png \"Relationship Graph\")"

    if interactive:
        # Add the relation json to the visible_messages
        visible_response += "\n" + json.dumps(relation_json, indent=4)
    else:
        # Add the generated html graph to visible_messages
        html = f"""\n<div style="max-width: 100%; overflow-x: auto;">{graph_svg}</div>"""
        visible_response += html
    
    if len(graph_building_cache['chunks']) > 1:
        graph_building_cache['chunks'] = graph_building_cache['chunks'][1:]
        # Cache current partial graph and continue next call
        graph_building_cache['current_relation_graph'] = json.dumps(relation_json, indent=4)
        
        # Update graph cache and continue next call
        st.session_state['graph_building_cache'] = graph_building_cache
    else:
        if 'graph_building_cache' in st.session_state:
            # Since all chunks have been processed assume finished and clear cache
            del st.session_state['graph_building_cache']

    return visible_response, hidden_response


def get_node_by_id(nodes, node_id):
    return next((node for node in nodes if node.id == node_id), None)


def get_connected_components(nodes, edges):
    # Create an adjacency list representation of the graph
    adj_list = {node.id: [] for node in nodes}
    for edge in edges:
        adj_list[edge.source].append(edge.to)
        adj_list[edge.to].append(edge.source)

    # DFS function to find connected components
    def dfs(node, visited, component):
        visited.add(node)
        component.append(node)
        for neighbor in adj_list[node]:
            if neighbor not in visited:
                dfs(neighbor, visited, component)

    visited = set()
    components = []

    # Iterate over all nodes and find connected components
    for node in adj_list:
        if node not in visited:
            component = []
            dfs(node, visited, component)
            components.append(component)
        
    # Convert node IDs to nodes
    # components = [[get_node_by_id(nodes, node_id) for node_id in component] for component in components]
    # print(components)

    return components


def draw_relation_graph(relation_json, min_component_len, width=1300, height=600):
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
        
        # Check for duplicate edges in either direction as edges between nodes are overlapped on rendering...
        node_pairing = tuple(sorted((entity1, entity2)))
        if node_pairing in relation_duplicates.keys():
            duplicate_count = relation_duplicates[node_pairing]
            relation = "\n\n\n" * duplicate_count + f"{relation}"
            
            relation_duplicates[node_pairing] += 1
        else:
            relation_duplicates[node_pairing] = 1
            
            # Increment the degrees of the nodes involved in this edge on non-duplicate relations
            node_degrees[entity1] += 1
            node_degrees[entity2] += 1
        
        edges.append( agraph.Edge(source=entity1, 
                        label=relation, 
                        target=entity2,
                        dashes=False,
                        title=description,
                        length=300,
                        ) 
                    )

    # Set node sizes based on degrees of nodes
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
                edge.length = 1200  # Adjust edge length for high-degree nodes

    # Filter out components with fewer than 3 nodes
    connected_components = get_connected_components(nodes, edges)
    filtered_components = [component for component in connected_components if len(component) >= min_component_len]
    
    # Extract nodes and edges from filtered components
    filtered_node_ids = [node for component in filtered_components for node in component]
    filtered_edges = [edge for edge in edges if edge.source in filtered_node_ids and edge.to in filtered_node_ids]
    filtered_nodes = [get_node_by_id(nodes, id) for id in filtered_node_ids]

    config = agraph.Config(width=width,
                height=height,
                directed=True, 
                physics=True, 
                # hierarchical=True,
                layout= {
                    "randomSeed": 10,
                    "improvedLayout": True,    # Enable if need initial layout to converge faster
                    "hierarchical": {
                    "direction": "RL",
                    "sortMethod": "hubsize",
                    "levelSeparation": 50,
                    "nodeSpacing": 30,
                    "treeSpacing": 50,
                    "blockShifting": True,     # Enable if need initial layout to converge faster
                    "edgeMinimization": True,  # Enable if need initial layout to converge faster
                    "parentCentralization": True,
                    "sortMethod": "hubsize",
                    # "shakeTowards": "roots"
                    }
                },
                groups= {
                    "useDefaultGroups": True,
                }
                # **kwargs
            )
    
    return_value = agraph.agraph(nodes=filtered_nodes, 
                        edges=filtered_edges, 
                        config=config)
    
    return return_value