"""
Testes de API da capacidade `cadastros-de-apoio`.

Um teste por cenário de openspec/specs/cadastros-de-apoio/spec.md.
"""


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


class TestCadastroDePessoas:
    """Requirement: Cadastro de pessoas do rateio"""

    def test_criar_pessoa_fica_disponivel_para_lancamentos(self, client, conta_configurada):
        """Scenario: Criar pessoa."""
        criada = client.post("/pessoas", json={"nome": "Carla"}, headers=conta_configurada)
        assert criada.status_code == 201

        resposta = lancar(client, conta_configurada, pessoas=["Carla"])

        assert resposta.status_code == 201
        assert resposta.json()[0]["pessoas"] == ["Carla"]

    def test_renomear_pessoa_preserva_o_historico(self, client, conta_configurada):
        """Scenario: Renomear pessoa preserva o histórico."""
        criada = client.post("/pessoas", json={"nome": "Bruna"}, headers=conta_configurada)
        pessoa_id = criada.json()["id"]
        lancar(client, conta_configurada, valor=200.0, pessoas=["Bruna"])
        client.post(
            "/regras",
            json={"chave": "farmacia", "categoria": "Mercado", "pessoas": ["Bruna"]},
            headers=conta_configurada,
        )
        client.post(
            "/pagamentos",
            json={"pessoa": "Bruna", "valor": 50.0, "data": "2026-09-20", "mes_ref": "2026-09"},
            headers=conta_configurada,
        )
        extrato_antes = client.get("/extrato/Bruna/2026-09", headers=conta_configurada).json()

        resposta = client.put(
            f"/pessoas/{pessoa_id}", json={"nome": "Bruna Silva"}, headers=conta_configurada
        )

        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Bruna Silva"

        lancamentos = client.get("/lancamentos", headers=conta_configurada).json()
        assert any("Bruna Silva" in l["pessoas"] for l in lancamentos)
        assert not any("Bruna" in l["pessoas"] for l in lancamentos)

        regras = client.get("/regras", headers=conta_configurada).json()
        assert regras[0]["pessoas"] == ["Bruna Silva"]

        pagamentos = client.get("/pagamentos", headers=conta_configurada).json()
        assert pagamentos[0]["pessoa"] == "Bruna Silva"

        extrato_depois = client.get("/extrato/Bruna Silva/2026-09", headers=conta_configurada).json()
        assert extrato_depois["devido_no_mes"] == extrato_antes["devido_no_mes"]
        assert extrato_depois["pago_no_mes"] == extrato_antes["pago_no_mes"]
        assert extrato_depois["acumulado"] == extrato_antes["acumulado"]

    def test_remover_pessoa(self, client, conta_configurada):
        """Scenario: Remover pessoa."""
        criada = client.post("/pessoas", json={"nome": "Carla"}, headers=conta_configurada)

        resposta = client.delete(f"/pessoas/{criada.json()['id']}", headers=conta_configurada)

        assert resposta.status_code == 204
        assert "Carla" not in [p["nome"] for p in client.get("/pessoas", headers=conta_configurada).json()]

    def test_borda_editar_pessoa_de_outra_conta(self, client, conta_configurada, segunda_conta):
        """Scenario: Caso de borda — editar pessoa de outra conta."""
        criada = client.post("/pessoas", json={"nome": "Carla"}, headers=conta_configurada)
        pessoa_id = criada.json()["id"]

        resposta = client.put(
            f"/pessoas/{pessoa_id}", json={"nome": "Invadida"}, headers=segunda_conta
        )

        assert resposta.status_code == 404
        nomes = [p["nome"] for p in client.get("/pessoas", headers=conta_configurada).json()]
        assert "Carla" in nomes and "Invadida" not in nomes


class TestCadastroDeFormasDePagamento:
    """Requirement: Cadastro de formas de pagamento"""

    def test_criar_forma_de_pagamento_com_ciclo_determina_o_mes_da_fatura(self, client, conta):
        """Scenario: Criar forma de pagamento com ciclo de fatura."""
        client.post(
            "/onboarding",
            json={"renda_principal": 0, "pessoas": ["Ana"],
                  "cartoes": [{"nome": "Base", "cor": "#111", "fecha": 0, "desloca": 0}],
                  "categorias": ["Mercado"]},
            headers=conta,
        )
        client.post(
            "/cartoes",
            json={"nome": "Cartao Ciclo", "cor": "#222", "fecha": 10, "desloca": 1},
            headers=conta,
        )

        # compra no dia 15 > fechamento 10 -> proximo ciclo (10) + deslocamento 1 -> 11
        resposta = lancar(client, conta, cartao="Cartao Ciclo", data="2026-09-15")

        assert resposta.json()[0]["mes"] == "2026-11"

    def test_editar_forma_de_pagamento_vale_para_lancamentos_seguintes(self, client, conta):
        """Scenario: Editar forma de pagamento."""
        client.post(
            "/onboarding",
            json={"renda_principal": 0, "pessoas": ["Ana"],
                  "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 10, "desloca": 0}],
                  "categorias": ["Mercado"]},
            headers=conta,
        )
        cartao_id = client.get("/cartoes", headers=conta).json()[0]["id"]
        antes = lancar(client, conta, data="2026-09-15")
        assert antes.json()[0]["mes"] == "2026-10"  # dia 15 > fecha 10

        resposta = client.put(
            f"/cartoes/{cartao_id}",
            json={"nome": "Cartao A", "cor": "#111", "fecha": 20, "desloca": 0},
            headers=conta,
        )
        assert resposta.status_code == 200

        depois = lancar(client, conta, data="2026-09-15")
        assert depois.json()[0]["mes"] == "2026-09"  # agora dia 15 < fecha 20

    def test_borda_pagamento_sem_fatura_cai_no_mes_da_compra(self, client, conta):
        """Scenario: Caso de borda — pagamento sem fatura (Pix, dinheiro)."""
        client.post(
            "/onboarding",
            json={"renda_principal": 0, "pessoas": ["Ana"],
                  "cartoes": [{"nome": "Pix", "cor": "#111", "fecha": 0, "desloca": 0}],
                  "categorias": ["Mercado"]},
            headers=conta,
        )

        resposta = lancar(client, conta, cartao="Pix", data="2026-09-28")

        assert resposta.json()[0]["mes"] == "2026-09"


class TestCadastroDeCategorias:
    """Requirement: Cadastro de categorias"""

    def test_criar_categoria_fica_disponivel(self, client, conta_configurada):
        """Scenario: Criar categoria."""
        criada = client.post("/categorias", json={"nome": "Lazer"}, headers=conta_configurada)
        assert criada.status_code == 201

        resposta = lancar(client, conta_configurada, categoria="Lazer")

        assert resposta.json()[0]["categoria"] == "Lazer"

    def test_renomear_categoria_preserva_a_classificacao(self, client, conta_configurada):
        """Scenario: Renomear categoria preserva a classificação."""
        categoria_id = [
            c for c in client.get("/categorias", headers=conta_configurada).json()
            if c["nome"] == "Mercado"
        ][0]["id"]
        lancar(client, conta_configurada, valor=300.0, categoria="Mercado", pessoas=["Ana"])
        client.post(
            "/regras",
            json={"chave": "mercado", "categoria": "Mercado", "pessoas": ["Ana"]},
            headers=conta_configurada,
        )
        antes = client.get("/painel/2026-09", headers=conta_configurada).json()
        total_antes = [g for g in antes["gastos_por_categoria"] if g["categoria"] == "Mercado"][0]["valor"]

        resposta = client.put(
            f"/categorias/{categoria_id}", json={"nome": "Supermercado"}, headers=conta_configurada
        )

        assert resposta.status_code == 200
        depois = client.get("/painel/2026-09", headers=conta_configurada).json()
        categorias = {g["categoria"]: g["valor"] for g in depois["gastos_por_categoria"]}
        assert "Mercado" not in categorias
        assert categorias["Supermercado"] == total_antes

        regras = client.get("/regras", headers=conta_configurada).json()
        assert regras[0]["categoria"] == "Supermercado"

    def test_borda_editar_categoria_de_outra_conta(self, client, conta_configurada, segunda_conta):
        """Requirement: recurso de outra conta é tratado como inexistente."""
        categoria_id = client.get("/categorias", headers=conta_configurada).json()[0]["id"]

        resposta = client.put(
            f"/categorias/{categoria_id}", json={"nome": "Invadida"}, headers=segunda_conta
        )

        assert resposta.status_code == 404
