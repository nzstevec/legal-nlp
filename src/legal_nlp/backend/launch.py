from fastapi import FastAPI
from routes import router

try:
    app = FastAPI()

    app.include_router(router)

except Exception as e:
    print(f"****>>>>> Error: {e}")