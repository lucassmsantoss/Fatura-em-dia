"""RF06 (lançar despesa com parcelamento e rateio) + RF07 (auto-categorização)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import usuario_atual
from app.database import get_db
from app.domain.fatura import aplicar_regra, fatura_de, gerar_parcelas
from app.models import Cartao, Lancamento, Regra, Usuario
from app.schemas import (
    LancamentoAtualizarDono, LancamentoAtualizarTipo, LancamentoCriar,
    LancamentoSaida, SugestaoRegra,
)

router = APIRouter(prefix="/lancamentos", tags=["lançamentos"])


def _cartao_do_usuario(db: Session, usuario_id: int, nome_cartao: str) -> Cartao:
    cartao = db.query(Cartao).filter(Cartao.usuario_id == usuario_id, Cartao.nome == nome_cartao).first()
    if not cartao:
        raise HTTPException(status_code=400, detail=f"Cartão '{nome_cartao}' não está cadastrado.")
    return cartao


@router.get("/sugestao", response_model=SugestaoRegra)
def sugerir_por_descricao(descricao: str, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """RF07 — Dada uma descrição, sugere categoria e pessoas com base nas regras já cadastradas."""
    regras = db.query(Regra).filter(Regra.usuario_id == usuario.id).all()
    regras_dict = [{"chave": r.chave, "cat": r.categoria, "pessoas": r.pessoas} for r in regras]
    encontrada = aplicar_regra(descricao, regras_dict)
    if not encontrada:
        return SugestaoRegra()
    return SugestaoRegra(
        categoria=encontrada.get("cat") or None,
        pessoas=encontrada.get("pessoas") or [],
        chave_encontrada=encontrada.get("chave"),
    )


@router.post("", response_model=list[LancamentoSaida], status_code=201)
def lancar_despesa(dados: LancamentoCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """
    RF06 — Cria uma despesa (à vista ou parcelada). Cada parcela vira um
    lançamento próprio, no mês de fatura correspondente.

    Caso de borda: valor <= 0 ou descrição vazia é rejeitado pela validação
    do schema (Field(gt=0) / min_length=1) antes de chegar aqui.
    """
    cartao = _cartao_do_usuario(db, usuario.id, dados.cartao)
    mes_base = fatura_de(dados.data, {"fecha": cartao.fecha, "desloca": cartao.desloca})
    parcelas = gerar_parcelas(dados.valor, dados.parcelas, mes_base)

    tipo_padrao = "e" if dados.estimativa else "r"
    criados = []
    for p in parcelas:
        lanc = Lancamento(
            usuario_id=usuario.id,
            data=dados.data,
            mes=p["mes"],
            descricao=dados.descricao.strip(),
            categoria=dados.categoria or "Outros",
            cartao=dados.cartao,
            parcela=p["parcela"],
            valor=p["valor"],
            pessoas=dados.pessoas,
            tipo=tipo_padrao,
        )
        db.add(lanc)
        criados.append(lanc)

    if dados.salvar_regra and dados.descricao.strip():
        chave = " ".join(dados.descricao.strip().split()[:2])
        ja_existe = db.query(Regra).filter(Regra.usuario_id == usuario.id, Regra.chave.ilike(chave)).first()
        if not ja_existe:
            db.add(Regra(usuario_id=usuario.id, chave=chave, categoria=dados.categoria, pessoas=dados.pessoas))

    db.commit()
    for lanc in criados:
        db.refresh(lanc)
    return criados


@router.get("", response_model=list[LancamentoSaida])
def listar_lancamentos(mes: str | None = None, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    query = db.query(Lancamento).filter(Lancamento.usuario_id == usuario.id)
    if mes:
        query = query.filter(Lancamento.mes == mes)
    return query.order_by(Lancamento.id.desc()).all()


@router.patch("/{lancamento_id}/tipo", response_model=LancamentoSaida)
def atualizar_tipo(lancamento_id: int, dados: LancamentoAtualizarTipo, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """Alterna entre aconteceu / compromisso / estimativa."""
    lanc = db.query(Lancamento).filter(Lancamento.id == lancamento_id, Lancamento.usuario_id == usuario.id).first()
    if not lanc:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.")
    lanc.tipo = dados.tipo
    db.commit()
    db.refresh(lanc)
    return lanc


@router.patch("/{lancamento_id}/dono", response_model=LancamentoSaida)
def atualizar_dono(lancamento_id: int, dados: LancamentoAtualizarDono, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """Atribui/remove pessoas de um lançamento (resolver 'sem dono')."""
    lanc = db.query(Lancamento).filter(Lancamento.id == lancamento_id, Lancamento.usuario_id == usuario.id).first()
    if not lanc:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.")
    lanc.pessoas = dados.pessoas
    db.commit()
    db.refresh(lanc)
    return lanc


@router.delete("/{lancamento_id}", status_code=204)
def remover_lancamento(lancamento_id: int, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    lanc = db.query(Lancamento).filter(Lancamento.id == lancamento_id, Lancamento.usuario_id == usuario.id).first()
    if not lanc:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado.")
    db.delete(lanc)
    db.commit()
