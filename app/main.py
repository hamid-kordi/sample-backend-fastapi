from fastapi import FastAPI, Depends, Security
from app.api.user import router

app = FastAPI()

app.include_router(router, prefix="/user", tags=["user"])
