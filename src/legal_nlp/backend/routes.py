from fastapi import APIRouter
from backend.endpoints.text_processor import text_processor
from backend.models.text_processor import TextRequest

router = APIRouter()

@router.post("/process_text/")
async def process_text(request: TextRequest):
    return text_processor.process_text(request.text)

@router.get("/ner_labels/")
async def get_ner_labels():
    return text_processor.get_ner_labels()