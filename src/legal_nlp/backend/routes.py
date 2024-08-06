from fastapi import APIRouter
from endpoints.text_processor import text_processor
from endpoints.relation_processor import relation_processor
from models.text_processor import TextRequest, RelationRequest

router = APIRouter()


@router.post("/process_text/")
async def process_text(request: TextRequest):
    return text_processor.process_text(request.text, request.labels)


@router.get("/ner_labels/")
async def get_ner_labels():
    return text_processor.get_ner_labels()


@router.post("/get_entity_relations/")
async def get_ner_labels(request: RelationRequest):
    return relation_processor.get_relation_graph(
        request.text, request.existing_relations, request.max_new_tokens
    )


@router.post("/extend_entity_relations/")
async def get_ner_labels(request: RelationRequest):
    return relation_processor.build_up_relation_graph(
        request.text, request.existing_relations, request.max_new_tokens
    )
