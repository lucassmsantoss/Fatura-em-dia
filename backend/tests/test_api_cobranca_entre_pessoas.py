"""
Testes de API da capacidade `cobranca-entre-pessoas`.

Um teste por cenário de openspec/specs/cobranca-entre-pessoas/spec.md.
"""
import pytest


def lancar(client, headers, **campos):
    corpo = {
        "valor": 100.0,
        "descricao": "Compra",
        "data": "2026-09-05",
        "cartao": "Cartao A",
        "categoria": "Mercado",
        "pessoas": ["Bruno"],
        "parcelas": 1,
    }
    corpo.update(campos)
    return client.post("/lancamentos", json=corpo, headers=headers)


def pagar(client, headers, **campos):
    corpo = {"pessoa": "Bruno", "valor": 50.0, "data": "2026-09-20", "mes_ref": "2026-09"}
    corpo.update(campos)
    return client.post("/pagamentos", json=corpo, headers=headers)


@pytest.fixture
def conta_rateio(client, conta):
    """Conta com Bruno e Caio no rateio e cartão sem ciclo."""
    client.post(
        "/onboarding",
        json={"renda_principal": 0, "pessoas": ["Ana", "Bruno", "Caio"],
              "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 0, "desloca": 0}],
              "categorias": ["Mercado"]},
        headers=conta,
    )
    return conta


class TestExtratoDeUmaPessoaEmUmMes:
    """Requirement: Extrato de uma pessoa em um mês"""

    def test_pessoa_com_despesas_no_mes(self, client, conta_rateio):
        """Scenario: Pessoa com despesas no mês."""
        lancar(client, conta_rateio, valor=300.0, pessoas=["Ana", "Bruno"])
        pagar(client, conta_rateio, valor=40.0)

        extrato = client.get("/extrato/Bruno/2026-09", headers=conta_rateio).json()

        assert extrato["pessoa"] == "Bruno"
        assert extrato["devido_no_mes"] == 150.0
        assert extrato["pago_no_mes"] == 40.0
        assert extrato["acumulado"] == 110.0

    def test_borda_pessoa_nao_cadastrada(self, client, conta_rateio):
        """Scenario: Caso de borda — pessoa não cadastrada."""
        resposta = client.get("/extrato/Fulano/2026-09", headers=conta_rateio)

        assert resposta.status_code == 404
        assert "devido_no_mes" not in resposta.text

    def test_borda_pessoa_de_outra_conta_nao_tem_extrato(
        self, client, conta_rateio, segunda_conta
    ):
        """Requirement: leitura de dado financeiro restrita à conta autenticada."""
        lancar(client, conta_rateio, valor=300.0, pessoas=["Bruno"])

        resposta = client.get("/extrato/Bruno/2026-09", headers=segunda_conta)

        assert resposta.status_code == 404


class TestSaldoAcumuladoEntreMeses:
    """Requirement: Saldo acumulado entre meses"""

    def test_divida_atravessa_meses(self, client, conta_rateio):
        """Scenario: Dívida atravessa meses."""
        lancar(client, conta_rateio, valor=100.0, data="2026-09-05", pessoas=["Bruno"])
        lancar(client, conta_rateio, valor=250.0, data="2026-10-05", pessoas=["Bruno"])

        extrato = client.get("/extrato/Bruno/2026-10", headers=conta_rateio).json()

        assert extrato["devido_no_mes"] == 250.0
        assert extrato["acumulado"] == 350.0

    def test_borda_pagamento_quita_o_acumulado(self, client, conta_rateio):
        """Scenario: Caso de borda — pagamento quita o acumulado."""
        lancar(client, conta_rateio, valor=100.0, data="2026-09-05", pessoas=["Bruno"])
        lancar(client, conta_rateio, valor=250.0, data="2026-10-05", pessoas=["Bruno"])
        assert client.get("/extrato/Bruno/2026-10", headers=conta_rateio).json()["acumulado"] == 350.0

        pagar(client, conta_rateio, valor=350.0, data="2026-10-20", mes_ref="2026-10")

        extrato = client.get("/extrato/Bruno/2026-10", headers=conta_rateio).json()
        assert extrato["acumulado"] == 0.0

    def test_acumulado_nao_conta_meses_posteriores_ao_consultado(self, client, conta_rateio):
        """Requirement: considera tudo até o mês consultado — não além dele."""
        lancar(client, conta_rateio, valor=100.0, data="2026-09-05", pessoas=["Bruno"])
        lancar(client, conta_rateio, valor=900.0, data="2026-12-05", pessoas=["Bruno"])

        extrato = client.get("/extrato/Bruno/2026-09", headers=conta_rateio).json()

        assert extrato["acumulado"] == 100.0


class TestRegistroDePagamentoRecebido:
    """Requirement: Registro de pagamento recebido"""

    def test_registrar_pagamento_parcial(self, client, conta_rateio):
        """Scenario: Registrar pagamento parcial."""
        lancar(client, conta_rateio, valor=200.0, pessoas=["Bruno"])

        resposta = pagar(client, conta_rateio, valor=50.0)

        assert resposta.status_code == 201
        extrato = client.get("/extrato/Bruno/2026-09", headers=conta_rateio).json()
        assert extrato["devido_no_mes"] == 200.0
        assert extrato["pago_no_mes"] == 50.0
        assert extrato["acumulado"] == 150.0

    @pytest.mark.parametrize("valor", [0, -30.0])
    def test_borda_valor_de_pagamento_invalido(self, client, conta_rateio, valor):
        """Scenario: Caso de borda — valor de pagamento inválido."""
        lancar(client, conta_rateio, valor=200.0, pessoas=["Bruno"])
        antes = client.get("/extrato/Bruno/2026-09", headers=conta_rateio).json()

        resposta = pagar(client, conta_rateio, valor=valor)

        assert resposta.status_code >= 400
        depois = client.get("/extrato/Bruno/2026-09", headers=conta_rateio).json()
        assert depois == antes

    def test_pagamento_guarda_data_e_mes_de_referencia(self, client, conta_rateio):
        """Requirement: com valor, data e mês de referência."""
        pagar(client, conta_rateio, valor=75.0, data="2026-09-18", mes_ref="2026-09")

        pagamentos = client.get("/pagamentos", params={"pessoa": "Bruno"}, headers=conta_rateio).json()

        assert len(pagamentos) == 1
        assert pagamentos[0]["valor"] == 75.0
        assert pagamentos[0]["data"] == "2026-09-18"
        assert pagamentos[0]["mes_ref"] == "2026-09"


class TestListaDeDevedoresDoMes:
    """Requirement: Lista de devedores do mês"""

    def test_pessoa_quite_nao_aparece(self, client, conta_rateio):
        """Scenario: Pessoa quite não aparece."""
        lancar(client, conta_rateio, valor=100.0, pessoas=["Bruno"])

        painel = client.get("/painel/2026-09", headers=conta_rateio).json()

        devedores = [s["pessoa"] for s in painel["saldos_por_pessoa"]]
        assert "Bruno" in devedores
        assert "Caio" not in devedores  # sem despesas e sem acumulado

    def test_pessoa_com_acumulado_de_mes_anterior_continua_aparecendo(self, client, conta_rateio):
        """Requirement: lista quem tem devido, pago OU acumulado diferente de zero."""
        lancar(client, conta_rateio, valor=100.0, data="2026-09-05", pessoas=["Bruno"])

        painel = client.get("/painel/2026-10", headers=conta_rateio).json()

        saldos = {s["pessoa"]: s for s in painel["saldos_por_pessoa"]}
        assert saldos["Bruno"]["devido_no_mes"] == 0.0
        assert saldos["Bruno"]["acumulado"] == 100.0

    def test_pessoa_some_da_lista_depois_de_quitar(self, client, conta_rateio):
        """Scenario: Pessoa quite não aparece — verificado pela transição."""
        lancar(client, conta_rateio, valor=100.0, data="2026-09-05", pessoas=["Bruno"])
        assert "Bruno" in [
            s["pessoa"] for s in client.get("/painel/2026-10", headers=conta_rateio).json()["saldos_por_pessoa"]
        ]

        pagar(client, conta_rateio, valor=100.0, data="2026-09-20", mes_ref="2026-09")

        painel = client.get("/painel/2026-10", headers=conta_rateio).json()
        assert "Bruno" not in [s["pessoa"] for s in painel["saldos_por_pessoa"]]
