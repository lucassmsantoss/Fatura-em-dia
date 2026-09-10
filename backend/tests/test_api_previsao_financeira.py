"""
Testes de API da capacidade `previsao-financeira`.

Um teste por cenário de openspec/specs/previsao-financeira/spec.md.

Os meses são derivados da data de execução, não fixados: o contrato fala em
"mês corrente", e um teste com mês fixo passaria hoje e falharia no mês que vem.
"""
from datetime import date

import pytest

from app.domain.fatura import soma_mes


def mes_corrente() -> str:
    return date.today().strftime("%Y-%m")


def mes_em(n: int) -> str:
    """Mês corrente deslocado de n meses."""
    return soma_mes(mes_corrente(), n)


def lancar(client, headers, **campos):
    corpo = {
        "valor": 100.0,
        "descricao": "Compra",
        "data": date.today().isoformat(),
        "cartao": "Cartao A",
        "categoria": "Mercado",
        "pessoas": ["Ana"],
        "parcelas": 1,
    }
    corpo.update(campos)
    return client.post("/lancamentos", json=corpo, headers=headers)


@pytest.fixture
def conta_sem_ciclo(client, conta):
    """Cartão sem fechamento nem deslocamento: a fatura é o mês da própria compra."""
    client.post(
        "/onboarding",
        json={"renda_principal": 0, "pessoas": ["Ana"],
              "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 0, "desloca": 0}],
              "categorias": ["Mercado"]},
        headers=conta,
    )
    return conta


def previsao(client, headers, a_partir_de=None, meses=6):
    return client.get(
        "/previsao",
        params={"a_partir_de": a_partir_de or mes_corrente(), "meses": meses},
        headers=headers,
    )


class TestPrevisaoCalculadaAPartirDosLancamentos:
    """Requirement: Previsão calculada a partir dos lançamentos"""

    def test_meses_futuros_com_contas_fixas_recorrentes(self, client, conta_sem_ciclo):
        """Scenario: Meses futuros com contas fixas recorrentes."""
        for n in (1, 2, 3):
            data_futura = f"{mes_em(n)}-05"
            lancar(client, conta_sem_ciclo, valor=1500.0, descricao="Aluguel",
                   data=data_futura, estimativa=True)

        meses = {p["mes"]: p for p in previsao(client, conta_sem_ciclo, meses=3).json()}

        for n in (1, 2, 3):
            assert meses[mes_em(n)]["total_estimativas"] == 1500.0
            assert meses[mes_em(n)]["total_previsto"] == 1500.0

    def test_parcelas_futuras_entram_na_previsao(self, client, conta_sem_ciclo):
        """Scenario: Parcelas futuras entram na previsão."""
        lancar(client, conta_sem_ciclo, valor=1200.0, descricao="Compra parcelada", parcelas=4)

        meses = {p["mes"]: p for p in previsao(client, conta_sem_ciclo, meses=3).json()}

        for n in (1, 2, 3):
            assert meses[mes_em(n)]["total_compromissos"] == 300.0, mes_em(n)
            assert meses[mes_em(n)]["total_previsto"] == 300.0

    def test_borda_parcela_do_mes_corrente_nao_e_compromisso(self, client, conta_sem_ciclo):
        """Scenario: Caso de borda — parcela do mês corrente não é compromisso."""
        criado = lancar(client, conta_sem_ciclo, valor=1200.0, parcelas=4)

        primeira = criado.json()[0]
        assert primeira["mes"] == mes_corrente()
        assert primeira["tipo"] == "r"

        meses = [p["mes"] for p in previsao(client, conta_sem_ciclo, meses=3).json()]
        assert mes_corrente() not in meses

    def test_borda_conta_fixa_vence_a_classificacao_por_data(self, client, conta_sem_ciclo):
        """Scenario: Caso de borda — conta fixa vence a classificação por data."""
        resposta = lancar(client, conta_sem_ciclo, valor=800.0, descricao="Internet",
                          data=f"{mes_em(2)}-05", estimativa=True)

        assert resposta.json()[0]["tipo"] == "e"

        mes = {p["mes"]: p for p in previsao(client, conta_sem_ciclo, meses=3).json()}[mes_em(2)]
        assert mes["total_estimativas"] == 800.0
        assert mes["total_compromissos"] == 0.0

    def test_borda_mes_futuro_sem_nada_lancado(self, client, conta_sem_ciclo):
        """Scenario: Caso de borda — mês futuro sem nada lançado."""
        resultado = previsao(client, conta_sem_ciclo, meses=3).json()

        assert [p["total_previsto"] for p in resultado] == [0.0, 0.0, 0.0]

    @pytest.mark.parametrize("pedido,esperado", [(0, 1), (-3, 1), (100, 24)])
    def test_borda_horizonte_fora_do_intervalo_e_ajustado(
        self, client, conta_sem_ciclo, pedido, esperado
    ):
        """Scenario: Caso de borda — horizonte de meses fora do intervalo é ajustado, não falha."""
        resposta = previsao(client, conta_sem_ciclo, meses=pedido)

        assert resposta.status_code == 200
        assert len(resposta.json()) == esperado

    def test_previsao_soma_compromisso_e_estimativa_no_mesmo_mes(self, client, conta_sem_ciclo):
        """Requirement: separa os dois, e o total previsto é a soma deles."""
        lancar(client, conta_sem_ciclo, valor=600.0, descricao="Compra parcelada", parcelas=2)
        lancar(client, conta_sem_ciclo, valor=900.0, descricao="Aluguel",
               data=f"{mes_em(1)}-05", estimativa=True)

        mes = {p["mes"]: p for p in previsao(client, conta_sem_ciclo, meses=2).json()}[mes_em(1)]

        assert mes["total_compromissos"] == 300.0
        assert mes["total_estimativas"] == 900.0
        assert mes["total_previsto"] == 1200.0

    def test_previsao_e_isolada_por_conta(self, client, conta_sem_ciclo, segunda_conta):
        """Requirement: derivada dos lançamentos existentes — da própria conta."""
        lancar(client, conta_sem_ciclo, valor=1200.0, parcelas=4)

        resultado = previsao(client, segunda_conta, meses=3).json()

        assert [p["total_previsto"] for p in resultado] == [0.0, 0.0, 0.0]


class TestPrevisaoComecaAposOMesDeReferencia:
    """Requirement: Previsão começa após o mês de referência"""

    def test_previsao_a_partir_do_mes_de_referencia(self, client, conta_sem_ciclo):
        """Scenario: Previsão a partir do mês corrente."""
        resultado = previsao(client, conta_sem_ciclo, a_partir_de="2026-09", meses=3).json()

        assert [p["mes"] for p in resultado] == ["2026-10", "2026-11", "2026-12"]
