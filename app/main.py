from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import hashlib

from app.database import engine, SessionLocal, Base
from app.models import User
import app.models as models

app = FastAPI()

# cria as tabelas
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"status": "Sistema rodando"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/criar-usuario")
def criar_usuario(username: str, password: str, db: Session = Depends(get_db)):
    senha_hash = hashlib.sha256(password.encode()).hexdigest()
    user = User(username=username, password=senha_hash)
    db.add(user)
    db.commit()
    return {"msg": "Usuário criado"}
