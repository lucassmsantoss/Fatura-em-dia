from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import criar_token_acesso, gerar_hash_senha, usuario_atual, verificar_senha
from app.database import get_db
from app.models import Usuario
from app.schemas import Token, UsuarioCriar, UsuarioLogin, UsuarioSaida

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/registrar", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED)
def registrar(dados: UsuarioCriar, db: Session = Depends(get_db)):
    """RF01 — Cadastro de usuário."""
    ja_existe = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if ja_existe:
        raise HTTPException(status_code=400, detail="Já existe uma conta com este email.")
    usuario = Usuario(nome=dados.nome, email=dados.email, senha_hash=gerar_hash_senha(dados.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    """RF01 — Login de usuário."""
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos.")
    token = criar_token_acesso(usuario.id)
    return Token(access_token=token)


@router.get("/eu", response_model=UsuarioSaida)
def eu(usuario: Usuario = Depends(usuario_atual)):
    return usuario
