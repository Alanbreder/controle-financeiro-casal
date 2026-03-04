from . import models
from .database import engine
from fastapi import FastAPI
from app.database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"status": "Sistema rodando"}


app = FastAPI()


models.Base.metadata.create_all(bind=engine)
