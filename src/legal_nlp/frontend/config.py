import os

class Config:
    # Default values
    NLP_CONNECTION_STRING = os.getenv("NLP_API_CONNECTION_STRING", "http://127.0.0.1:8542")
    
