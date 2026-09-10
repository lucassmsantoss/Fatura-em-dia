"""
Serialização e leitura de lançamentos em CSV — RF11.

Módulo de domínio puro: não conhece banco, sessão nem HTTP. Recebe e devolve
estruturas simples, o que mantém o teste do formato — inclusive o da linha
malformada — independente de banco e de autenticação.

Duas decisões de desenho, registradas no change `conformidade-rf`:

1. **Importação parcial.** Uma linha inválida não aborta o arquivo: as demais
   entram e o chamador recebe a relação do que foi rejeitado e por quê.
2. **Cabeçalho inválido recusa o arquivo inteiro.** Sem cabeçalho reconhecível
   não há interpretação confiável de nenhuma linha, então não faz sentido
   importar parte dela.
"""
from __future__ import annotations

import csv
import io
from typing import TypedDict

COLUNAS = ["data", "mes", "descricao", "categoria", "cartao", "parcela", "valor", "pessoas", "tipo"]

# as pessoas vão num único campo, separadas por ponto e vírgula, para não
# colidir com a vírgula que separa as colunas
SEPARADOR_PESSOAS = ";"

TIPOS_VALIDOS = {"r", "c", "e"}


class LinhaRejeitada(TypedDict):
    linha: int
    motivo: str


class CabecalhoInvalido(ValueError):
    """O arquivo não tem as colunas do formato de exportação."""


def serializar(lancamentos: list[dict]) -> str:
    """
    Monta o CSV a partir dos lançamentos. Sempre escreve a linha de cabeçalho,
    mesmo quando não há nenhum lançamento — um arquivo só com cabeçalho é
    resposta válida para uma conta vazia, não um erro.
    """
    saida = io.StringIO()
    escritor = csv.DictWriter(saida, fieldnames=COLUNAS, lineterminator="\n")
    escritor.writeheader()
    for lancamento in lancamentos:
        escritor.writerow({
            "data": lancamento.get("data", ""),
            "mes": lancamento.get("mes", ""),
            "descricao": lancamento.get("descricao", ""),
            "categoria": lancamento.get("categoria", ""),
            "cartao": lancamento.get("cartao", ""),
            "parcela": lancamento.get("parcela", ""),
            "valor": f'{float(lancamento.get("valor", 0)):.2f}',
            "pessoas": SEPARADOR_PESSOAS.join(lancamento.get("pessoas") or []),
            "tipo": lancamento.get("tipo", "r"),
        })
    return saida.getvalue()


def interpretar(texto: str) -> tuple[list[dict], list[LinhaRejeitada]]:
    """
    Lê um CSV no formato da exportação e devolve (lançamentos, rejeitados).

    Levanta `CabecalhoInvalido` quando as colunas não correspondem ao formato —
    nesse caso nada deve ser importado.

    O número da linha relatado é o do ARQUIVO (cabeçalho é a linha 1), que é o
    que a pessoa vê ao abrir a planilha.
    """
    leitor = csv.DictReader(io.StringIO(texto))
    colunas = [c.strip() for c in (leitor.fieldnames or [])]
    if not set(COLUNAS).issubset(set(colunas)):
        faltando = [c for c in COLUNAS if c not in colunas]
        raise CabecalhoInvalido(
            "Cabeçalho não reconhecido: faltam as colunas " + ", ".join(faltando)
        )

    aceitos: list[dict] = []
    rejeitados: list[LinhaRejeitada] = []

    for indice, linha in enumerate(leitor, start=2):  # 2 = primeira linha após o cabeçalho
        descricao = (linha.get("descricao") or "").strip()
        if not descricao:
            rejeitados.append({"linha": indice, "motivo": "descrição vazia"})
            continue

        bruto = (linha.get("valor") or "").strip()
        try:
            valor = float(bruto.replace(",", "."))
        except ValueError:
            rejeitados.append({"linha": indice, "motivo": f"valor não numérico: {bruto!r}"})
            continue
        if valor <= 0:
            rejeitados.append({"linha": indice, "motivo": f"valor deve ser maior que zero: {bruto!r}"})
            continue

        mes = (linha.get("mes") or "").strip()
        if len(mes) != 7 or mes[4] != "-":
            rejeitados.append({"linha": indice, "motivo": f"mês de fatura inválido: {mes!r}"})
            continue

        pessoas = [p.strip() for p in (linha.get("pessoas") or "").split(SEPARADOR_PESSOAS) if p.strip()]
        tipo = (linha.get("tipo") or "r").strip()

        aceitos.append({
            "data": (linha.get("data") or "").strip(),
            "mes": mes,
            "descricao": descricao,
            "categoria": (linha.get("categoria") or "").strip(),
            "cartao": (linha.get("cartao") or "").strip(),
            "parcela": (linha.get("parcela") or "").strip(),
            "valor": round(valor, 2),
            "pessoas": pessoas,
            "tipo": tipo if tipo in TIPOS_VALIDOS else "r",
        })

    return aceitos, rejeitados
