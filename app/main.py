
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import hashlib
from fastapi import HTTPException, Header
from app.database import engine, SessionLocal, Base
from app.models import User, Models, Lancamento


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


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    senha_hash = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != senha_hash:
        raise HTTPException(
            status_code=401, detail="Usuário ou senha inválidos")

    return {"msg": "Login realizado com sucesso"}


def verificar_usuario(username: str = Header(...), password: str = Header(...), db: Session = Depends(get_db)):
    senha_hash = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != senha_hash:
        raise HTTPException(status_code=401, detail="Não autorizado")

    return user


@app.get("/protegido")
def protegido(user: User = Depends(verificar_usuario)):
    return {"msg": "Acesso autorizado"}
