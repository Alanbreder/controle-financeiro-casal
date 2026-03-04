from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError

from app.database import Base, engine, SessionLocal
from app.models import User, Lancamento
from app.schemas import LancamentoResponse
from app.auth import hash_password, verify_password, create_access_token, decode_token

app = FastAPI()

# 🔥 RESET TOTAL (TEMPORÁRIO)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user


@app.post("/criar-usuario")
def criar_usuario(username: str, password: str, db: Session = Depends(get_db)):
    senha_hash = hash_password(password)

    user = User(username=username, password=senha_hash)
    db.add(user)
    db.commit()

    return {"msg": "Usuário criado com sucesso"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401, detail="Usuário ou senha inválidos")

    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/lancamentos", response_model=List[LancamentoResponse])
def listar_lancamentos(
    mes: int,
    ano: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Lancamento).filter(
        Lancamento.mes == mes,
        Lancamento.ano == ano
    ).all()
