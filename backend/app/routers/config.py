"""
RF02 (onboarding) + RF03/RF04/RF05 (CRUD de pessoas, cartões e categorias).

Cada endpoint opera apenas sobre os dados do usuário autenticado
(filtragem por usuario_id em toda consulta).
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import usuario_atual
from app.database import get_db
from app.domain.fatura import substituir_nome
from app.models import Cartao, Categoria, Lancamento, Pagamento, Pessoa, Receita, Regra, Usuario
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
    """
    RF02 — Configuração inicial: cadastra de uma só vez a renda mensal, as pessoas
    do rateio, as formas de pagamento e as categorias, e marca a configuração
    como concluída.

    A validação acontece ANTES de qualquer escrita: uma configuração recusada não
    pode deixar cadastro parcial para trás.
    """
    if not dados.pessoas:
        raise HTTPException(
            status_code=400,
            detail="Informe ao menos uma pessoa para o rateio (pode ser você mesmo).",
        )
    if not dados.cartoes:
        raise HTTPException(
            status_code=400,
            detail="Informe ao menos uma forma de pagamento.",
        )

    for nome in dados.pessoas:
        db.add(Pessoa(usuario_id=usuario.id, nome=nome))
    for cartao in dados.cartoes:
        db.add(Cartao(usuario_id=usuario.id, nome=cartao.nome, cor=cartao.cor, fecha=cartao.fecha, desloca=cartao.desloca))
    for nome in dados.categorias:
        db.add(Categoria(usuario_id=usuario.id, nome=nome))

    # a renda informada no fluxo vira a receita do mês corrente
    if dados.renda_principal:
        mes_corrente = date.today().strftime("%Y-%m")
        db.add(Receita(
            usuario_id=usuario.id,
            mes=mes_corrente,
            renda_principal=dados.renda_principal,
            renda_extra=0.0,
        ))

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


@router.put("/pessoas/{pessoa_id}", response_model=PessoaSaida)
def atualizar_pessoa(pessoa_id: int, dados: PessoaCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """
    RF03 — Renomeia uma pessoa e propaga o novo nome para tudo que a referencia.

    Lançamentos, regras e pagamentos guardam o NOME da pessoa, não a chave
    estrangeira (decisão herdada do protótipo, ver models.py). Sem a propagação,
    renomear deixaria o histórico órfão e quebraria o extrato dela.

    Tudo acontece na mesma transação: ou o nome muda em todo lugar, ou não muda
    em lugar nenhum.
    """
    pessoa = db.query(Pessoa).filter(Pessoa.id == pessoa_id, Pessoa.usuario_id == usuario.id).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")

    nome_antigo, nome_novo = pessoa.nome, dados.nome
    if nome_antigo == nome_novo:
        return pessoa

    try:
        pessoa.nome = nome_novo

        for lancamento in db.query(Lancamento).filter(Lancamento.usuario_id == usuario.id).all():
            atualizadas = substituir_nome(lancamento.pessoas or [], nome_antigo, nome_novo)
            if atualizadas != (lancamento.pessoas or []):
                lancamento.pessoas = atualizadas  # reatribui: coluna JSON não detecta mutação in-place

        for regra in db.query(Regra).filter(Regra.usuario_id == usuario.id).all():
            atualizadas = substituir_nome(regra.pessoas or [], nome_antigo, nome_novo)
            if atualizadas != (regra.pessoas or []):
                regra.pessoas = atualizadas

        for pagamento in db.query(Pagamento).filter(
            Pagamento.usuario_id == usuario.id, Pagamento.pessoa == nome_antigo
        ).all():
            pagamento.pessoa = nome_novo

        db.commit()
    except Exception:
        db.rollback()
        raise

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


@router.put("/categorias/{categoria_id}", response_model=CategoriaSaida)
def atualizar_categoria(categoria_id: int, dados: CategoriaCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """
    RF05 — Renomeia uma categoria e propaga o novo nome para lançamentos e regras.

    Mesma razão da renomeação de pessoa: a categoria é referenciada por nome.
    Sem propagar, o ranking do painel passaria a mostrar duas categorias onde
    havia uma.
    """
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id, Categoria.usuario_id == usuario.id
    ).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")

    nome_antigo, nome_novo = categoria.nome, dados.nome
    if nome_antigo == nome_novo:
        return categoria

    try:
        categoria.nome = nome_novo
        db.query(Lancamento).filter(
            Lancamento.usuario_id == usuario.id, Lancamento.categoria == nome_antigo
        ).update({Lancamento.categoria: nome_novo}, synchronize_session=False)
        db.query(Regra).filter(
            Regra.usuario_id == usuario.id, Regra.categoria == nome_antigo
        ).update({Regra.categoria: nome_novo}, synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise

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
