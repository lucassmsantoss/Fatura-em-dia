"""
Testes de API da capacidade `painel-mensal`.

Um teste por cenário de openspec/specs/painel-mensal/spec.md.
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
def conta_mes_simples(client, conta):
    """Cartão sem ciclo: a fatura é o mês da própria compra, o que mantém os testes legíveis."""
    client.post(
        "/onboarding",
        json={
            "renda_principal": 0,
            "pessoas": ["Ana", "Bruno", "Caio"],
            "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 0, "desloca": 0}],
            "categorias": ["Mercado", "Transporte"],
        },
        headers=conta,
    )
    return conta


class TestConsolidacaoDoMes:
    """Requirement: Consolidação do mês"""

    def test_mes_com_despesas_e_receita(self, client, conta_mes_simples):
        """Scenario: Mês com despesas e receita."""
        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 4000.0,
                                      "renda_extra": 1000.0}, headers=conta_mes_simples)
        lancar(client, conta_mes_simples, valor=300.0, pessoas=["Ana", "Bruno"])
        lancar(client, conta_mes_simples, valor=200.0, pessoas=["Ana"])

        painel = client.get("/painel/2026-09", headers=conta_mes_simples).json()

        assert painel["total_mes"] == 500.0
        assert painel["meu_total"] == 350.0        # 150 (metade de 300) + 200
        assert painel["receita_total"] == 5000.0
        assert painel["sobra_ou_falta"] == 4650.0  # 5000 - 350

    def test_sobra_ou_falta_fica_negativa_quando_o_gasto_supera_a_receita(self, client, conta_mes_simples):
        """Requirement: a diferença é apresentada como sobra OU falta."""
        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 100.0,
                                      "renda_extra": 0}, headers=conta_mes_simples)
        lancar(client, conta_mes_simples, valor=400.0, pessoas=["Ana"])

        painel = client.get("/painel/2026-09", headers=conta_mes_simples).json()

        assert painel["sobra_ou_falta"] == -300.0

    def test_borda_mes_sem_nenhum_lancamento(self, client, conta_mes_simples):
        """Scenario: Caso de borda — mês sem nenhum lançamento."""
        painel = client.get("/painel/2026-12", headers=conta_mes_simples).json()

        assert painel["total_mes"] == 0.0
        assert painel["meu_total"] == 0.0
        assert painel["sem_dono"] == 0.0
        assert painel["gastos_por_categoria"] == []

    def test_borda_mes_sem_receita_registrada(self, client, conta_mes_simples):
        """Scenario: Caso de borda — mês sem receita registrada; receita tratada como zero."""
        lancar(client, conta_mes_simples, valor=200.0, pessoas=["Ana"])

        painel = client.get("/painel/2026-09", headers=conta_mes_simples).json()

        assert painel["receita_total"] == 0.0
        assert painel["sobra_ou_falta"] == -200.0


class TestDistribuicaoPorCategoria:
    """Requirement: Distribuição do gasto próprio por categoria"""

    def test_ranking_de_categorias_do_maior_para_o_menor(self, client, conta_mes_simples):
        """Scenario: Ranking de categorias."""
        lancar(client, conta_mes_simples, valor=100.0, categoria="Transporte", pessoas=["Ana"])
        lancar(client, conta_mes_simples, valor=300.0, categoria="Mercado", pessoas=["Ana"])

        painel = client.get("/painel/2026-09", headers=conta_mes_simples).json()

        assert [(g["categoria"], g["valor"]) for g in painel["gastos_por_categoria"]] == [
            ("Mercado", 300.0),
            ("Transporte", 100.0),
        ]

    def test_ranking_considera_apenas_a_parcela_propria(self, client, conta_mes_simples):
        """Requirement: quanto da parcela PRÓPRIA da pessoa foi para cada categoria."""
        lancar(client, conta_mes_simples, valor=300.0, categoria="Mercado",
               pessoas=["Ana", "Bruno", "Caio"])

        painel = client.get("/painel/2026-09", headers=conta_mes_simples).json()

        assert painel["gastos_por_categoria"][0]["valor"] == 100.0


class TestVisibilidadeDeGastoSemDono:
    """Requirement: Visibilidade de gasto sem dono"""

    def test_mes_contem_lancamento_sem_dono(self, client, conta_mes_simples):
        """Scenario: Mês contém lançamento sem dono."""
        lancar(client, conta_mes_simples, valor=150.0, pessoas=[])
        lancar(client, conta_mes_simples, valor=100.0, pessoas=["Ana"])

        painel = client.get("/painel/2026-09", headers=conta_mes_simples).json()

        assert painel["sem_dono"] == 150.0
        assert painel["total_mes"] == 250.0


class TestRegistroDeReceitaMensal:
    """Requirement: Registro de receita mensal"""

    def test_registrar_receita_de_um_mes(self, client, conta_mes_simples):
        """Scenario: Registrar receita de um mês."""
        lancar(client, conta_mes_simples, valor=200.0, pessoas=["Ana"])

        resposta = client.put("/receitas", json={"mes": "2026-09", "renda_principal": 3000.0,
                                                 "renda_extra": 0}, headers=conta_mes_simples)

        assert resposta.status_code == 200
        painel = client.get("/painel/2026-09", headers=conta_mes_simples).json()
        assert painel["sobra_ou_falta"] == 2800.0

    def test_borda_registrar_duas_vezes_o_mesmo_mes_substitui(self, client, conta_mes_simples):
        """Scenario: Caso de borda — registrar duas vezes o mesmo mês substitui, não duplica."""
        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 3000.0,
                                      "renda_extra": 0}, headers=conta_mes_simples)

        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 4500.0,
                                      "renda_extra": 500.0}, headers=conta_mes_simples)

        assert client.get("/painel/2026-09", headers=conta_mes_simples).json()["receita_total"] == 5000.0
        consulta = client.get("/receitas/2026-09", headers=conta_mes_simples).json()
        assert consulta["renda_principal"] == 4500.0
        assert consulta["renda_extra"] == 500.0


class TestConsultaEAlteracaoDaReceita:
    """Requirement: Consulta e alteração da receita de um mês"""

    def test_consultar_receita_de_um_mes_ja_registrado(self, client, conta_mes_simples):
        """Scenario: Consultar receita de um mês já registrado."""
        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 4000.0,
                                      "renda_extra": 700.0}, headers=conta_mes_simples)

        resposta = client.get("/receitas/2026-09", headers=conta_mes_simples)

        assert resposta.status_code == 200
        assert resposta.json()["mes"] == "2026-09"
        assert resposta.json()["renda_principal"] == 4000.0
        assert resposta.json()["renda_extra"] == 700.0

    def test_alterar_a_receita_de_um_mes_passado_ou_futuro(self, client, conta_mes_simples):
        """Scenario: Alterar a receita de um mês passado ou futuro."""
        lancar(client, conta_mes_simples, valor=500.0, data="2027-03-10", pessoas=["Ana"])

        client.put("/receitas", json={"mes": "2027-03", "renda_principal": 2000.0,
                                      "renda_extra": 0}, headers=conta_mes_simples)

        painel = client.get("/painel/2027-03", headers=conta_mes_simples).json()
        assert painel["receita_total"] == 2000.0
        assert painel["sobra_ou_falta"] == 1500.0

    def test_borda_mes_sem_receita_devolve_zero_sem_erro(self, client, conta_mes_simples):
        """Scenario: Caso de borda — mês sem receita registrada devolve zero, não erro."""
        resposta = client.get("/receitas/2030-01", headers=conta_mes_simples)

        assert resposta.status_code == 200
        assert resposta.json()["mes"] == "2030-01"
        assert resposta.json()["renda_principal"] == 0.0
        assert resposta.json()["renda_extra"] == 0.0

    def test_receita_e_isolada_por_conta(self, client, conta_mes_simples, segunda_conta):
        """Requirement: toda leitura de dado financeiro é restrita à conta autenticada."""
        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 9000.0,
                                      "renda_extra": 0}, headers=conta_mes_simples)

        resposta = client.get("/receitas/2026-09", headers=segunda_conta)

        assert resposta.status_code == 200
        assert resposta.json()["renda_principal"] == 0.0


class TestListagemDasReceitasRegistradas:
    """
    Requirement: Listagem das receitas registradas
    (openspec/changes/historico-de-receitas/specs/painel-mensal/spec.md)
    """

    def test_conta_com_receitas_em_varios_meses(self, client, conta_mes_simples):
        """Scenario: Conta com receitas em vários meses — devolvidas ordenadas por mês."""
        # gravadas fora de ordem de proposito: a ordenacao e responsabilidade do sistema
        for mes, principal, extra in [
            ("2026-11", 5200.0, 0.0),
            ("2026-09", 4000.0, 700.0),
            ("2026-10", 4000.0, 0.0),
        ]:
            client.put(
                "/receitas",
                json={"mes": mes, "renda_principal": principal, "renda_extra": extra},
                headers=conta_mes_simples,
            )

        resposta = client.get("/receitas", headers=conta_mes_simples)

        assert resposta.status_code == 200
        receitas = resposta.json()
        assert [r["mes"] for r in receitas] == ["2026-09", "2026-10", "2026-11"]
        assert receitas[0]["renda_principal"] == 4000.0
        assert receitas[0]["renda_extra"] == 700.0
        assert receitas[2]["renda_principal"] == 5200.0

    def test_borda_conta_sem_nenhuma_receita_registrada(self, client, conta_mes_simples):
        """Scenario: Caso de borda — conta sem nenhuma receita devolve lista vazia, sem erro."""
        resposta = client.get("/receitas", headers=conta_mes_simples)

        assert resposta.status_code == 200
        assert resposta.json() == []

    def test_borda_receitas_de_outra_conta_nao_aparecem(
        self, client, conta_mes_simples, segunda_conta
    ):
        """Scenario: Caso de borda — receitas de outra conta não aparecem."""
        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 9000.0,
                                      "renda_extra": 0}, headers=conta_mes_simples)
        client.put("/receitas", json={"mes": "2026-09", "renda_principal": 1500.0,
                                      "renda_extra": 0}, headers=segunda_conta)

        resposta = client.get("/receitas", headers=segunda_conta)

        assert [r["renda_principal"] for r in resposta.json()] == [1500.0]

    def test_listagem_exige_credencial(self, client):
        """Requirement: a listagem contém apenas receitas da conta autenticada."""
        assert client.get("/receitas").status_code == 401
