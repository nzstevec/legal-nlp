import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def process_text(self, text):
        endpoint = f"{self.base_url}/process_text"
        data = {"text": str(text)}
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        
        return response.json()

    def get_ner_labels(self):
        endpoint = f"{self.base_url}/ner_labels"
        response = requests.get(endpoint)
        response.raise_for_status()
        
        return response.json()
    
    def get_relation_graph(self, text):
        endpoint = f"{self.base_url}/entity_relations"
        data = {"text": str(text)}
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        
        response_json = response.json()
        graph_svg = response_json["graph_svg"]
        relation_json = response_json["relation_json"]
        
        return graph_svg, relation_json
