import os

class Config:
    # Default values
    HOST = os.getenv("NLP_API_HOST", "127.0.0.1")
    PORT = int(os.getenv("NLP_API_PORT", 8542))
    
