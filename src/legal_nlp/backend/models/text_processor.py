from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str
    
class RelationRequest(BaseModel):
    text: str
    existing_relations: str
    max_new_tokens: int