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


def substituir_nome(nomes: list[str], antigo: str, novo: str) -> list[str]:
    """
    Troca `antigo` por `novo` em uma lista de nomes, preservando a ordem e sem
    duplicar caso `novo` já esteja presente.

    Usada na renomeação de pessoas, que precisa propagar para as listas de
    participantes guardadas em lançamentos e regras.
    """
    if not nomes or antigo == novo:
        return list(nomes or [])
    resultado: list[str] = []
    for nome in nomes:
        substituido = novo if nome == antigo else nome
        if substituido not in resultado:
            resultado.append(substituido)
    return resultado

def classificar_tipo(mes_fatura: str, mes_corrente: str, conta_fixa: bool = False) -> str:
    """
    Deriva o tipo de um lançamento a partir do mês em que ele cai, do mês
    corrente e da marcação de conta fixa recorrente.

    Devolve um de três valores:
      "e" — estimativa: conta fixa recorrente
      "c" — compromisso: parcela já contratada que cai em mês ainda por vir
      "r" — aconteceu: tudo o mais

    Duas decisões deliberadas, ambas registradas no design do change
    `conformidade-rf`:

    1. `mes_corrente` é PARÂMETRO, nunca lido de dentro da função. Sem isso o
       resultado dependeria do relógio e o teste ficaria frágil.
    2. A marcação explícita de conta fixa PREVALECE sobre a inferência por
       data. Uma conta fixa lançada para um mês futuro é estimativa, não
       compromisso — quem sabe que aquilo é recorrente é a pessoa, não o
       calendário.

    A comparação de "AAAA-MM" como texto é correta: o formato é ordenável
    lexicograficamente, inclusive na virada de ano.
    """
    if conta_fixa:
        return "e"
    if mes_fatura > mes_corrente:
        return "c"
    return "r"
