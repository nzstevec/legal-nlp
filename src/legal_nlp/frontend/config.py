import os


class Config:
    # Default values
    NLP_CONNECTION_STRING = os.getenv(
        "NLP_API_CONNECTION_STRING", "http://127.0.0.1:8549"
    )
    RUNPOD_BEARER_TOKEN = os.getenv(
        "RUNPOD_BEARER_TOKEN", "ZXNJGLFM2X390VJJSJY8910YHQLISIY5H9A67JHZ"
    )
    RUNPOD_BASE_URI = os.getenv(
        "RUNPOD_BASE_URI", "https://api.runpod.ai/v2/5bniip0yjm37iq"
    )
    STREAM_CHAT = os.getenv("STREAM_CHAT", True)
    RUNPOD_STREAM_DELAY = os.getenv("RUNPOD_STREAM_DELAY", 0.0)
    RUNPOD_STATUS_CHECK_DELAY = os.getenv("RUNPOD_STATUS_CHECK_DELAY", 0.1)


class PageConfig:
    page_title = "SCOTi"
    page_icon = "frontend/static/images/scoti_logo.png"
    layout = "wide"
