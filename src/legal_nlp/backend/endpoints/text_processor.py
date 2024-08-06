import spacy
from config import Config


class TextProcessor:
    def __init__(self):        
        self.custom_spacy_config = { "gliner_model": "EmergentMethods/gliner_medium_news-v2.1",
                            "chunk_size": 250,
                            "labels": ["people","company"],
                            "style": "ent"}
        self.nlp = spacy.blank("en")
        self.nlp.add_pipe("gliner_spacy", config=self.custom_spacy_config)

    def process_text(self, text: str, labels: list[str]):
        # Change gliner_spacy labels to the labels provided
        gliner_spacy_pipe = self.nlp.get_pipe("gliner_spacy")
        gliner_spacy_pipe.labels = labels
        
        doc = self.nlp(text)
        # Process the text here
        return {
            "tokens": [token.text for token in doc],
            "pos_tags": [token.pos_ for token in doc],
            "ner_tags": [(ent.text, ent.label_) for ent in doc.ents],
        }

    def get_ner_labels(self):
        return self.custom_spacy_config["labels"]


text_processor = TextProcessor()
