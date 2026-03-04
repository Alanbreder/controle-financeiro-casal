from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import hashlib
import uuid
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth import hash_password, verify_password, create_access_token, decode_token
from jose import JWTError

from app.database import engine, SessionLocal, Base
from app.models import User, Lancamento

app = FastAPI()

# cria tabelas se não existirem
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.get("/")
def home():
    return {"status": "Sistema rodando"}


# -----------------------
# BANCO
# -----------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------
# USUÁRIO
# -----------------------

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


# -----------------------
# PROTEÇÃO SIMPLES
# -----------------------

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

# -----------------------
# LANÇAMENTOS
# -----------------------


@app.post("/lancamento")
def criar_lancamento(
    descricao: str,
    valor: float,
    mes: int,
    ano: int,
    tipo: str,
    categoria: str,
    reembolsavel: bool = False,
    quem_deve: str = None,
    parcelado: bool = False,
    total_parcelas: int = None,
    observacao: str = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if parcelado and total_parcelas:
        grupo_id = str(uuid.uuid4())

        for i in range(total_parcelas):
            novo_mes = mes + i
            novo_ano = ano

            while novo_mes > 12:
                novo_mes -= 12
                novo_ano += 1

            lanc = Lancamento(
                descricao=descricao,
                valor=valor,
                mes=novo_mes,
                ano=novo_ano,
                tipo=tipo,
                categoria=categoria,
                reembolsavel=reembolsavel,
                quem_deve=quem_deve,
                parcelado=True,
                total_parcelas=total_parcelas,
                numero_parcela=i + 1,
                grupo_parcela=grupo_id,
                observacao=observacao
            )
            db.add(lanc)

    else:
        lanc = Lancamento(
            descricao=descricao,
            valor=valor,
            mes=mes,
            ano=ano,
            tipo=tipo,
            categoria=categoria,
            reembolsavel=reembolsavel,
            quem_deve=quem_deve,
            parcelado=False,
            observacao=observacao
        )
        db.add(lanc)

    db.commit()

    return {"msg": "Lançamento criado com sucesso"}


@app.get("/lancamentos")
def listar_lancamentos(
    mes: int,
    ano: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lancamentos = db.query(Lancamento).filter(
        Lancamento.mes == mes,
        Lancamento.ano == ano
    ).all()

    return lancamentos
