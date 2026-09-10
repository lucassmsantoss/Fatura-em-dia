"""
RF02 (onboarding) + RF03/RF04/RF05 (CRUD de pessoas, cartões e categorias).

Cada endpoint opera apenas sobre os dados do usuário autenticado
(filtragem por usuario_id em toda consulta).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import usuario_atual
from app.database import get_db
from app.models import Cartao, Categoria, Pessoa, Regra, Usuario
from app.schemas import (
    CartaoCriar, CartaoSaida,
    CategoriaCriar, CategoriaSaida,
    OnboardingEntrada,
    PessoaCriar, PessoaSaida,
    RegraCriar, RegraSaida,
)

router = APIRouter(tags=["configuração"])


# ---------- Onboarding ----------
@router.post("/onboarding", response_model=dict)
def concluir_onboarding(dados: OnboardingEntrada, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """RF02 — Configuração inicial: cria pessoas, cartões e categorias de uma vez e marca o onboarding como concluído."""
    for nome in dados.pessoas:
        db.add(Pessoa(usuario_id=usuario.id, nome=nome))
    for cartao in dados.cartoes:
        db.add(Cartao(usuario_id=usuario.id, nome=cartao.nome, cor=cartao.cor, fecha=cartao.fecha, desloca=cartao.desloca))
    for nome in dados.categorias:
        db.add(Categoria(usuario_id=usuario.id, nome=nome))
    usuario.onboarding_concluido = True
    db.commit()
    return {"status": "ok", "onboarding_concluido": True}


# ---------- Pessoas (RF03) ----------
@router.get("/pessoas", response_model=list[PessoaSaida])
def listar_pessoas(usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    return db.query(Pessoa).filter(Pessoa.usuario_id == usuario.id).all()


@router.post("/pessoas", response_model=PessoaSaida, status_code=201)
def criar_pessoa(dados: PessoaCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    pessoa = Pessoa(usuario_id=usuario.id, nome=dados.nome)
    db.add(pessoa)
    db.commit()
    db.refresh(pessoa)
    return pessoa


@router.delete("/pessoas/{pessoa_id}", status_code=204)
def remover_pessoa(pessoa_id: int, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id, Pessoa.usuario_id == usuario.id).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")
    db.delete(pessoa)
    db.commit()


# ---------- Cartões (RF04) ----------
@router.get("/cartoes", response_model=list[CartaoSaida])
def listar_cartoes(usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    return db.query(Cartao).filter(Cartao.usuario_id == usuario.id).all()


@router.post("/cartoes", response_model=CartaoSaida, status_code=201)
def criar_cartao(dados: CartaoCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    cartao = Cartao(usuario_id=usuario.id, **dados.model_dump())
    db.add(cartao)
    db.commit()
    db.refresh(cartao)
    return cartao


@router.put("/cartoes/{cartao_id}", response_model=CartaoSaida)
def atualizar_cartao(cartao_id: int, dados: CartaoCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    cartao = db.query(Cartao).filter(Cartao.id == cartao_id, Cartao.usuario_id == usuario.id).first()
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")
    for campo, valor in dados.model_dump().items():
        setattr(cartao, campo, valor)
    db.commit()
    db.refresh(cartao)
    return cartao


@router.delete("/cartoes/{cartao_id}", status_code=204)
def remover_cartao(cartao_id: int, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    cartao = db.query(Cartao).filter(Cartao.id == cartao_id, Cartao.usuario_id == usuario.id).first()
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")
    db.delete(cartao)
    db.commit()


# ---------- Categorias (RF05) ----------
@router.get("/categorias", response_model=list[CategoriaSaida])
def listar_categorias(usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    return db.query(Categoria).filter(Categoria.usuario_id == usuario.id).all()


@router.post("/categorias", response_model=CategoriaSaida, status_code=201)
def criar_categoria(dados: CategoriaCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    categoria = Categoria(usuario_id=usuario.id, nome=dados.nome)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/categorias/{categoria_id}", status_code=204)
def remover_categoria(categoria_id: int, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id, Categoria.usuario_id == usuario.id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    db.delete(categoria)
    db.commit()


# ---------- Regras de auto-categorização (RF07) ----------
@router.get("/regras", response_model=list[RegraSaida])
def listar_regras(usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    return db.query(Regra).filter(Regra.usuario_id == usuario.id).all()


@router.post("/regras", response_model=RegraSaida, status_code=201)
def criar_regra(dados: RegraCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    regra = Regra(usuario_id=usuario.id, chave=dados.chave, categoria=dados.categoria, pessoas=dados.pessoas)
    db.add(regra)
    db.commit()
    db.refresh(regra)
    return regra


@router.delete("/regras/{regra_id}", status_code=204)
def remover_regra(regra_id: int, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    regra = db.query(Regra).filter(Regra.id == regra_id, Regra.usuario_id == usuario.id).first()
    if not regra:
        raise HTTPException(status_code=404, detail="Regra não encontrada.")
    db.delete(regra)
    db.commit()
