"""
Módulo de domínio: regras de negócio centrais do Fatura em Dia.

Funções puras (sem I/O, sem banco de dados), portadas e generalizadas a
partir do protótipo original ("Caderneta"). Mantidas isoladas do resto da
aplicação para serem fáceis de testar unitariamente — ver
tests/test_fatura_domain.py.
"""
from __future__ import annotations

import unicodedata
from typing import TypedDict


class Cartao(TypedDict, total=False):
    nome: str
    fecha: int      # dia do mês em que a fatura fecha (0 = não se aplica, ex: Pix)
    desloca: int     # quantos meses além do ciclo até a fatura cobrar


class Lancamento(TypedDict, total=False):
    valor: float
    pessoas: list[str]


class Regra(TypedDict, total=False):
    chave: str
    cat: str
    pessoas: list[str]


def soma_mes(mes: str, n: int) -> str:
    """Soma (ou subtrai) n meses a uma referência 'AAAA-MM', virando o ano quando necessário."""
    ano, mes_num = (int(x) for x in mes.split("-"))
    indice = (mes_num - 1) + n
    ano += indice // 12
    mes_num = (indice % 12) + 1
    return f"{ano:04d}-{mes_num:02d}"


def fatura_de(data_iso: str, cartao: Cartao) -> str:
    """
    Determina em qual mês de fatura uma compra feita em `data_iso` (AAAA-MM-DD)
    vai aparecer, dado o dia de fechamento e o deslocamento do cartão.

    Regra: se o dia da compra for MAIOR que o dia de fechamento, a compra
    entra no ciclo do mês seguinte. Depois disso, soma-se o deslocamento
    (quantos meses até a fatura efetivamente cobrar).
    """
    dia = int(data_iso[8:10])
    mes = data_iso[:7]
    fecha = cartao.get("fecha") or 0
    desloca = cartao.get("desloca") or 0
    if fecha > 0 and dia > fecha:
        mes = soma_mes(mes, 1)
    if desloca:
        mes = soma_mes(mes, desloca)
    return mes


def cada_um(lancamento: Lancamento) -> float:
    """Valor que cabe a cada pessoa em um lançamento dividido igualmente."""
    pessoas = lancamento.get("pessoas") or []
    if not pessoas:
        return 0.0
    return lancamento["valor"] / len(pessoas)


def gerar_parcelas(valor: float, n: int, mes_base: str) -> list[dict]:
    """
    Distribui `valor` em `n` parcelas iguais, uma por mês a partir de `mes_base`.
    Garante que a soma das parcelas bata exatamente com o valor original
    (a última parcela absorve a diferença de arredondamento).
    """
    n = max(1, min(48, int(n or 1)))
    parcela_base = round(valor / n, 2)
    parcelas = []
    soma_parcial = 0.0
    for i in range(1, n + 1):
        if i < n:
            valor_parcela = parcela_base
        else:
            # última parcela absorve o resto para não perder centavos
            valor_parcela = round(valor - soma_parcial, 2)
        soma_parcial += valor_parcela
        parcelas.append({
            "mes": soma_mes(mes_base, i - 1),
            "valor": valor_parcela,
            "parcela": f"{i}/{n}" if n > 1 else "",
        })
    return parcelas


def normalizar(texto: str) -> str:
    """Remove acentos e baixa a caixa, para comparação tolerante de texto."""
    if not texto:
        return ""
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return sem_acento.lower()


def aplicar_regra(descricao: str, regras: list[Regra]) -> Regra | None:
    """
    Procura, na ordem, a primeira regra cuja palavra-chave apareça na
    descrição (comparação sem acento/maiúsculas). Retorna None se nenhuma bater.
    """
    desc_normalizada = normalizar(descricao)
    if not desc_normalizada:
        return None
    for regra in regras:
        chave = normalizar(regra.get("chave", ""))
        if chave and chave in desc_normalizada:
            return regra
    return None
