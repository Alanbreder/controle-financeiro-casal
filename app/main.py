from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import hashlib
import uuid

from app.database import engine, SessionLocal, Base
from app.models import User, Lancamento

app = FastAPI()

# cria tabelas se não existirem
Base.metadata.create_all(bind=engine)


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
    senha_hash = hashlib.sha256(password.encode()).hexdigest()

    usuario_existente = db.query(User).filter(
        User.username == username).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    user = User(username=username, password=senha_hash)
    db.add(user)
    db.commit()

    return {"msg": "Usuário criado com sucesso"}


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    senha_hash = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != senha_hash:
        raise HTTPException(
            status_code=401, detail="Usuário ou senha inválidos")

    return {"msg": "Login realizado com sucesso"}


# -----------------------
# PROTEÇÃO SIMPLES
# -----------------------

def verificar_usuario(
    username: str = Header(...),
    password: str = Header(...),
    db: Session = Depends(get_db)
):
    senha_hash = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != senha_hash:
        raise HTTPException(status_code=401, detail="Não autorizado")

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
    user: User = Depends(verificar_usuario),
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
