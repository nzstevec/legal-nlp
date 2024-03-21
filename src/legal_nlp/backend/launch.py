from fastapi import FastAPI
from backend.routes import router

app = FastAPI()

app.include_router(router)