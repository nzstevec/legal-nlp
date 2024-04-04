import spacy
from config import Config

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load(Config.NER_MODEL)

    def process_text(self, text: str):
        doc = self.nlp(text)
        # Process the text here
        return {
            "tokens": [token.text for token in doc],
            "pos_tags": [token.pos_ for token in doc],
            "ner_tags": [(ent.text, ent.label_) for ent in doc.ents]
        }
        
    def get_ner_labels(self):
        labels = set()
        for ent in self.nlp.get_pipe("ner").labels:
            labels.add(ent)
        return list(labels)

text_processor = TextProcessor()
