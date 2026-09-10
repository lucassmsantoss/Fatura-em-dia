"""RF08 (painel mensal) + RF09 (previsão de meses futuros) + RF10 (extrato/cobrança)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import usuario_atual
from app.database import get_db
from app.domain.fatura import cada_um, soma_mes
from app.models import Lancamento, Pagamento, Pessoa, Receita, Usuario
from app.schemas import (
    GastoPorCategoria, PagamentoCriar, PagamentoSaida, PainelSaida,
    PrevisaoMes, ReceitaEntrada, ReceitaSaida, SaldoPessoa,
)

router = APIRouter(tags=["painel"])


def _lancamentos_do_mes(db: Session, usuario_id: int, mes: str) -> list[Lancamento]:
    return db.query(Lancamento).filter(Lancamento.usuario_id == usuario_id, Lancamento.mes == mes).all()


def _acumulado_pessoa(db: Session, usuario_id: int, pessoa: str, ate_mes: str) -> float:
    """RF10 — saldo acumulado: soma o que a pessoa deve em todos os meses até `ate_mes`,
    subtraindo o que ela já pagou até lá."""
    lancamentos = (
        db.query(Lancamento)
        .filter(Lancamento.usuario_id == usuario_id, Lancamento.mes <= ate_mes)
        .all()
    )
    devido = sum(cada_um({"valor": l.valor, "pessoas": l.pessoas}) for l in lancamentos if pessoa in (l.pessoas or []))
    pagamentos = (
        db.query(Pagamento)
        .filter(Pagamento.usuario_id == usuario_id, Pagamento.pessoa == pessoa, Pagamento.mes_ref <= ate_mes)
        .all()
    )
    pago = sum(p.valor for p in pagamentos)
    return round(devido - pago, 2)


@router.get("/painel/{mes}", response_model=PainelSaida)
def painel_do_mes(mes: str, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """RF08 — Dashboard mensal: totais, receita, sobra/falta, gastos por categoria e saldos por pessoa."""
    lancamentos = _lancamentos_do_mes(db, usuario.id, mes)

    total_mes = round(sum(l.valor for l in lancamentos), 2)
    meu_total = round(sum(cada_um({"valor": l.valor, "pessoas": l.pessoas}) for l in lancamentos if usuario.nome in (l.pessoas or [])), 2)
    sem_dono = round(sum(l.valor for l in lancamentos if not l.pessoas), 2)

    receita = db.query(Receita).filter(Receita.usuario_id == usuario.id, Receita.mes == mes).first()
    receita_total = (receita.renda_principal + receita.renda_extra) if receita else 0.0
    sobra_ou_falta = round(receita_total - meu_total, 2)

    cats: dict[str, float] = {}
    for l in lancamentos:
        if usuario.nome in (l.pessoas or []):
            cats[l.categoria or "Outros"] = cats.get(l.categoria or "Outros", 0) + cada_um({"valor": l.valor, "pessoas": l.pessoas})
    gastos_por_categoria = [GastoPorCategoria(categoria=k, valor=round(v, 2)) for k, v in sorted(cats.items(), key=lambda x: -x[1])]

    pessoas = db.query(Pessoa).filter(Pessoa.usuario_id == usuario.id, Pessoa.nome != usuario.nome).all()
    saldos = []
    for p in pessoas:
        devido_no_mes = round(sum(cada_um({"valor": l.valor, "pessoas": l.pessoas}) for l in lancamentos if p.nome in (l.pessoas or [])), 2)
        pago_no_mes = round(
            sum(pg.valor for pg in db.query(Pagamento).filter(Pagamento.usuario_id == usuario.id, Pagamento.pessoa == p.nome, Pagamento.mes_ref == mes).all()),
            2,
        )
        if abs(devido_no_mes) < 0.005 and abs(pago_no_mes) < 0.005:
            acumulado = _acumulado_pessoa(db, usuario.id, p.nome, mes)
            if abs(acumulado) < 0.005:
                continue
        else:
            acumulado = _acumulado_pessoa(db, usuario.id, p.nome, mes)
        saldos.append(SaldoPessoa(pessoa=p.nome, devido_no_mes=devido_no_mes, pago_no_mes=pago_no_mes, acumulado=acumulado))

    return PainelSaida(
        mes=mes,
        total_mes=total_mes,
        meu_total=meu_total,
        receita_total=receita_total,
        sobra_ou_falta=sobra_ou_falta,
        sem_dono=sem_dono,
        gastos_por_categoria=gastos_por_categoria,
        saldos_por_pessoa=saldos,
    )


@router.get("/previsao", response_model=list[PrevisaoMes])
def previsao_meses_futuros(a_partir_de: str, meses: int = 6, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """
    RF09 — Previsão calculada dinamicamente: soma, para cada um dos próximos
    meses, os lançamentos já registrados como compromisso (parcelas futuras)
    e estimativa (contas fixas recorrentes). Não depende de nenhum dado importado.
    """
    resultado = []
    mes = a_partir_de
    for _ in range(max(1, min(24, meses))):
        mes = soma_mes(mes, 1)
        lancamentos = _lancamentos_do_mes(db, usuario.id, mes)
        total_compromissos = round(sum(l.valor for l in lancamentos if l.tipo == "c"), 2)
        total_estimativas = round(sum(l.valor for l in lancamentos if l.tipo == "e"), 2)
        resultado.append(PrevisaoMes(
            mes=mes,
            total_compromissos=total_compromissos,
            total_estimativas=total_estimativas,
            total_previsto=round(total_compromissos + total_estimativas, 2),
        ))
    return resultado


@router.get("/extrato/{pessoa}/{mes}", response_model=SaldoPessoa)
def extrato_pessoa(pessoa: str, mes: str, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """RF10 — Extrato de uma pessoa em um mês (usado pela tela de cobrança)."""
    existe = db.query(Pessoa).filter(Pessoa.usuario_id == usuario.id, Pessoa.nome == pessoa).first()
    if not existe:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")
    lancamentos = _lancamentos_do_mes(db, usuario.id, mes)
    devido_no_mes = round(sum(cada_um({"valor": l.valor, "pessoas": l.pessoas}) for l in lancamentos if pessoa in (l.pessoas or [])), 2)
    pago_no_mes = round(
        sum(pg.valor for pg in db.query(Pagamento).filter(Pagamento.usuario_id == usuario.id, Pagamento.pessoa == pessoa, Pagamento.mes_ref == mes).all()),
        2,
    )
    acumulado = _acumulado_pessoa(db, usuario.id, pessoa, mes)
    return SaldoPessoa(pessoa=pessoa, devido_no_mes=devido_no_mes, pago_no_mes=pago_no_mes, acumulado=acumulado)


@router.post("/pagamentos", response_model=PagamentoSaida, status_code=201)
def registrar_pagamento(dados: PagamentoCriar, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """RF10 — Registrar um pagamento recebido de uma pessoa."""
    pagamento = Pagamento(usuario_id=usuario.id, **dados.model_dump())
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


@router.get("/pagamentos", response_model=list[PagamentoSaida])
def listar_pagamentos(pessoa: str | None = None, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    query = db.query(Pagamento).filter(Pagamento.usuario_id == usuario.id)
    if pessoa:
        query = query.filter(Pagamento.pessoa == pessoa)
    return query.order_by(Pagamento.data.desc()).all()


@router.get("/receitas", response_model=list[ReceitaSaida])
def listar_receitas(usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """
    RF08 — Lista todas as receitas já registradas na conta, ordenadas por mês.

    Complementa a consulta por mês: aquela preenche um campo, esta responde
    "em quais meses eu já registrei receita?" — que é como se percebe um mês
    esquecido, cuja falta o painel só mostra como sobra negativa sem causa
    aparente.
    """
    return (
        db.query(Receita)
        .filter(Receita.usuario_id == usuario.id)
        .order_by(Receita.mes)
        .all()
    )


@router.get("/receitas/{mes}", response_model=ReceitaSaida)
def consultar_receita(mes: str, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """
    RF08 — Consulta a receita de um mês.

    Mês sem receita registrada devolve zero, não 404: a ausência é o estado
    normal de qualquer mês ainda não configurado, não uma condição de erro.
    Devolver zero deixa a interface abrir o campo em branco; devolver 404
    obrigaria a tratar como erro o caso mais comum.
    """
    receita = db.query(Receita).filter(
        Receita.usuario_id == usuario.id, Receita.mes == mes
    ).first()
    if not receita:
        return ReceitaSaida(mes=mes, renda_principal=0.0, renda_extra=0.0)
    return receita


@router.put("/receitas", response_model=ReceitaSaida)
def definir_receita(dados: ReceitaEntrada, usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    """Define (ou atualiza) a receita de um mês específico."""
    receita = db.query(Receita).filter(Receita.usuario_id == usuario.id, Receita.mes == dados.mes).first()
    if not receita:
        receita = Receita(usuario_id=usuario.id, mes=dados.mes)
        db.add(receita)
    receita.renda_principal = dados.renda_principal
    receita.renda_extra = dados.renda_extra
    db.commit()
    db.refresh(receita)
    return receita
