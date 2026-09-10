"""
Testes de API da capacidade `lancamento-de-despesas`.

Um teste por cenário de openspec/specs/lancamento-de-despesas/spec.md.
"""
import pytest


def lancar(client, headers, **campos):
    corpo = {
        "valor": 100.0,
        "descricao": "Compra",
        "data": "2026-09-05",
        "cartao": "Cartao A",
        "categoria": "Mercado",
        "pessoas": ["Ana"],
        "parcelas": 1,
    }
    corpo.update(campos)
    return client.post("/lancamentos", json=corpo, headers=headers)


@pytest.fixture
def conta_com_cartao_simples(client, conta):
    """Conta cujo cartão não tem fechamento nem deslocamento: a fatura é o mês da compra."""
    client.post(
        "/onboarding",
        json={
            "renda_principal": 0,
            "pessoas": ["Ana", "Bruno", "Caio"],
            "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 0, "desloca": 0}],
            "categorias": ["Mercado"],
        },
        headers=conta,
    )
    return conta


class TestRegistroDeDespesa:
    """Requirement: Registro de despesa"""

    def test_despesa_a_vista_atribuida_a_uma_pessoa(self, client, conta_com_cartao_simples):
        """Scenario: Despesa à vista atribuída a uma pessoa."""
        resposta = lancar(
            client, conta_com_cartao_simples, valor=300.0, data="2026-09-10", pessoas=["Ana"]
        )

        assert resposta.status_code == 201
        lancamentos = resposta.json()
        assert len(lancamentos) == 1
        assert lancamentos[0]["valor"] == 300.0
        assert lancamentos[0]["mes"] == "2026-09"
        assert lancamentos[0]["pessoas"] == ["Ana"]
        assert lancamentos[0]["parcela"] == ""

    @pytest.mark.parametrize("valor", [0, -50.0])
    def test_borda_valor_zerado_ou_negativo_nao_cria_lancamento(
        self, client, conta_com_cartao_simples, valor
    ):
        """Scenario: Caso de borda — valor ausente ou zerado."""
        resposta = lancar(client, conta_com_cartao_simples, valor=valor)

        assert resposta.status_code >= 400
        assert client.get("/lancamentos", headers=conta_com_cartao_simples).json() == []

    def test_borda_valor_ausente_nao_cria_lancamento(self, client, conta_com_cartao_simples):
        """Scenario: Caso de borda — valor ausente."""
        resposta = client.post(
            "/lancamentos",
            json={"descricao": "Sem valor", "data": "2026-09-05", "cartao": "Cartao A",
                  "categoria": "Mercado", "pessoas": ["Ana"], "parcelas": 1},
            headers=conta_com_cartao_simples,
        )

        assert resposta.status_code == 422
        assert client.get("/lancamentos", headers=conta_com_cartao_simples).json() == []

    def test_borda_forma_de_pagamento_nao_cadastrada(self, client, conta_com_cartao_simples):
        """Scenario: Caso de borda — forma de pagamento não cadastrada."""
        resposta = lancar(client, conta_com_cartao_simples, cartao="Cartao Inexistente")

        assert resposta.status_code == 400
        assert "cadastrad" in resposta.json()["detail"].lower()
        assert client.get("/lancamentos", headers=conta_com_cartao_simples).json() == []


class TestParcelamento:
    """Requirement: Parcelamento"""

    def test_compra_dividida_em_quatro_parcelas(self, client, conta_com_cartao_simples):
        """Scenario: Compra dividida em quatro parcelas."""
        resposta = lancar(
            client, conta_com_cartao_simples, valor=1200.0, data="2026-10-05", parcelas=4
        )

        assert resposta.status_code == 201
        parcelas = resposta.json()
        assert len(parcelas) == 4
        assert [p["mes"] for p in parcelas] == ["2026-10", "2026-11", "2026-12", "2027-01"]
        assert [p["valor"] for p in parcelas] == [300.0, 300.0, 300.0, 300.0]
        assert [p["parcela"] for p in parcelas] == ["1/4", "2/4", "3/4", "4/4"]

    def test_borda_divisao_que_nao_fecha_em_centavos(self, client, conta_com_cartao_simples):
        """Scenario: Caso de borda — divisão que não fecha em centavos."""
        resposta = lancar(client, conta_com_cartao_simples, valor=100.0, parcelas=3)

        parcelas = resposta.json()
        assert len(parcelas) == 3
        assert round(sum(p["valor"] for p in parcelas), 2) == 100.0

    @pytest.mark.parametrize("parcelas,esperado", [(0, 1), (-5, 1), (100, 48)])
    def test_borda_numero_de_parcelas_invalido_e_ajustado(
        self, client, conta_com_cartao_simples, parcelas, esperado
    ):
        """Scenario: Caso de borda — número de parcelas inválido é ajustado, não falha."""
        resposta = lancar(client, conta_com_cartao_simples, valor=480.0, parcelas=parcelas)

        assert resposta.status_code == 201
        assert len(resposta.json()) == esperado


class TestCicloDeFechamentoDeFatura:
    """Requirement: Ciclo de fechamento de fatura"""

    @pytest.fixture
    def conta_com_cartao_ciclo(self, client, conta):
        """Cartão que fecha no dia 24 e cobra 1 mês depois."""
        client.post(
            "/onboarding",
            json={"renda_principal": 0, "pessoas": ["Ana"],
                  "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 24, "desloca": 1}],
                  "categorias": ["Mercado"]},
            headers=conta,
        )
        return conta

    def test_compra_antes_do_fechamento(self, client, conta_com_cartao_ciclo):
        """Scenario: Compra antes do fechamento — dia 10 de setembro cai em outubro."""
        resposta = lancar(client, conta_com_cartao_ciclo, data="2026-09-10")

        assert resposta.json()[0]["mes"] == "2026-10"

    def test_compra_depois_do_fechamento(self, client, conta_com_cartao_ciclo):
        """Scenario: Compra depois do fechamento — dia 28 de setembro cai em novembro."""
        resposta = lancar(client, conta_com_cartao_ciclo, data="2026-09-28")

        assert resposta.json()[0]["mes"] == "2026-11"

    def test_borda_compra_no_dia_exato_do_fechamento(self, client, conta):
        """Scenario: Caso de borda — compra no dia exato do fechamento permanece no ciclo."""
        client.post(
            "/onboarding",
            json={"renda_principal": 0, "pessoas": ["Ana"],
                  "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 24, "desloca": 0}],
                  "categorias": ["Mercado"]},
            headers=conta,
        )

        resposta = lancar(client, conta, data="2026-09-24")

        assert resposta.json()[0]["mes"] == "2026-09"


class TestRateioEntrePessoas:
    """Requirement: Rateio entre pessoas"""

    def test_divisao_igualitaria(self, client, conta_com_cartao_simples):
        """Scenario: Divisão igualitária — R$ 300,00 entre três pessoas dá R$ 100,00 cada."""
        lancar(
            client, conta_com_cartao_simples, valor=300.0, data="2026-09-10",
            pessoas=["Ana", "Bruno", "Caio"],
        )

        for pessoa in ["Ana", "Bruno", "Caio"]:
            extrato = client.get(f"/extrato/{pessoa}/2026-09", headers=conta_com_cartao_simples).json()
            assert extrato["devido_no_mes"] == 100.0, pessoa

    def test_borda_lancamento_sem_dono(self, client, conta_com_cartao_simples):
        """Scenario: Caso de borda — lançamento sem dono é contabilizado como tal no painel."""
        lancar(client, conta_com_cartao_simples, valor=250.0, data="2026-09-10", pessoas=[])

        painel = client.get("/painel/2026-09", headers=conta_com_cartao_simples).json()

        assert painel["sem_dono"] == 250.0
        assert painel["total_mes"] == 250.0
        assert painel["meu_total"] == 0.0


class TestCorrecaoDeLancamentoExistente:
    """Requirement: Correção de lançamento existente"""

    def test_atribuir_dono_depois_do_registro(self, client, conta_com_cartao_simples):
        """Scenario: Atribuir dono depois do registro."""
        criado = lancar(
            client, conta_com_cartao_simples, valor=200.0, data="2026-09-10", pessoas=[]
        )
        lancamento_id = criado.json()[0]["id"]
        assert client.get("/painel/2026-09", headers=conta_com_cartao_simples).json()["sem_dono"] == 200.0

        resposta = client.patch(
            f"/lancamentos/{lancamento_id}/dono",
            json={"pessoas": ["Ana", "Bruno"]},
            headers=conta_com_cartao_simples,
        )

        assert resposta.status_code == 200
        painel = client.get("/painel/2026-09", headers=conta_com_cartao_simples).json()
        assert painel["sem_dono"] == 0.0
        extrato = client.get("/extrato/Bruno/2026-09", headers=conta_com_cartao_simples).json()
        assert extrato["devido_no_mes"] == 100.0

    def test_remover_lancamento(self, client, conta_com_cartao_simples):
        """Requirement: o sistema SHALL permitir remover um lançamento."""
        criado = lancar(client, conta_com_cartao_simples, valor=200.0, data="2026-09-10")
        lancamento_id = criado.json()[0]["id"]

        resposta = client.delete(f"/lancamentos/{lancamento_id}", headers=conta_com_cartao_simples)

        assert resposta.status_code == 204
        assert client.get("/lancamentos", headers=conta_com_cartao_simples).json() == []
