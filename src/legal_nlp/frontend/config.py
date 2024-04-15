import os


class Config:
    # Default values
    NLP_CONNECTION_STRING = os.getenv(
        "NLP_API_CONNECTION_STRING", "http://127.0.0.1:8542"
    )
    RUNPOD_BEARER_TOKEN = os.getenv("RUNPOD_BEARER_TOKEN", "")
    RUNPOD_BASE_URI = os.getenv(
        "RUNPOD_BASE_URI", "https://api.runpod.ai/v2/hjxnt6qh1tc7mp"
    )
    INFERENCE_CHAT_URI = os.getenv(
        "INFERENCE_BASE_URI", "http://127.0.0.1:2235"
    )
    INFERENCE_STREAM_URI = os.getenv(
        "INFERENCE_BASE_URI", "http://127.0.0.1:2234"
    )
    STREAM_CHAT = os.getenv("STREAM_CHAT", False)
    RUNPOD_STREAM_DELAY = os.getenv("RUNPOD_STREAM_DELAY", 0.0)
    RUNPOD_STATUS_CHECK_DELAY = os.getenv("RUNPOD_STATUS_CHECK_DELAY", 0.1)
    RUNPOD_SERVERLESS=False

class PageConfig:
    page_title = "SCOTi"
    page_icon = "frontend/static/images/scoti_logo.png"
    layout = "wide"
