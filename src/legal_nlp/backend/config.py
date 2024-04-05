import os


class Config:
    # Default values
    HOST = os.getenv("NLP_API_HOST", "127.0.0.1")
    PORT = int(os.getenv("NLP_API_PORT", 8543))

    RUNPOD_BEARER_TOKEN = os.getenv("RUNPOD_BEARER_TOKEN", "")
    RUNPOD_BASE_URI = os.getenv(
        "RUNPOD_BASE_URI", "https://api.runpod.ai/v2/hjxnt6qh1tc7mp"
    )
    STREAM_CHAT = os.getenv("STREAM_CHAT", False)
    RUNPOD_STREAM_DELAY = os.getenv("RUNPOD_STREAM_DELAY", 0.0)
    RUNPOD_STATUS_CHECK_DELAY = os.getenv("RUNPOD_STATUS_CHECK_DELAY", 0.1)

    NER_MODEL = "nlp/models/en_legal_ner_trf"
