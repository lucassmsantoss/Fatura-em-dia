"""Autenticação: hash de senha e emissão/validação de JWT."""
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario

SECRET_KEY = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao")
ALGORITHM = "HS256"
EXPIRA_EM_MINUTOS = 60 * 24 * 7  # 7 dias

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)


def criar_token_acesso(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=EXPIRA_EM_MINUTOS)
    payload = {"sub": str(usuario_id), "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credencial_invalida = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = payload.get("sub")
        if usuario_id is None:
            raise credencial_invalida
    except JWTError:
        raise credencial_invalida

    usuario = db.get(Usuario, int(usuario_id))
    if usuario is None:
        raise credencial_invalida
    return usuario
