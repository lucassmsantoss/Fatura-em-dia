"""
Testes de API da capacidade `auto-categorizacao`.

Um teste por cenário de openspec/specs/auto-categorizacao/spec.md.
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


def sugerir(client, headers, descricao):
    return client.get("/lancamentos/sugestao", params={"descricao": descricao}, headers=headers)


class TestSugestaoPorPalavraChave:
    """Requirement: Sugestão por palavra-chave"""

    def test_descricao_corresponde_a_uma_regra(self, client, conta_configurada):
        """Scenario: Descrição corresponde a uma regra."""
        client.post(
            "/regras",
            json={"chave": "mercado bom preco", "categoria": "Mercado", "pessoas": ["Ana"]},
            headers=conta_configurada,
        )

        resposta = sugerir(client, conta_configurada, "Compra no Mercado Bom Preço")

        assert resposta.status_code == 200
        assert resposta.json()["categoria"] == "Mercado"
        assert resposta.json()["pessoas"] == ["Ana"]

    def test_comparacao_tolerante_a_acento_e_caixa(self, client, conta_configurada):
        """Scenario: Comparação tolerante a acento e caixa."""
        client.post(
            "/regras",
            json={"chave": "padaria", "categoria": "Mercado", "pessoas": []},
            headers=conta_configurada,
        )

        resposta = sugerir(client, conta_configurada, "PADARIA São José")

        assert resposta.json()["chave_encontrada"] == "padaria"

    def test_primeira_regra_correspondente_vence(self, client, conta_configurada):
        """Requirement: procura a PRIMEIRA regra cuja palavra-chave esteja contida na descrição."""
        client.post("/regras", json={"chave": "mercado", "categoria": "Mercado", "pessoas": []},
                    headers=conta_configurada)
        client.post("/regras", json={"chave": "bom preco", "categoria": "Transporte", "pessoas": []},
                    headers=conta_configurada)

        resposta = sugerir(client, conta_configurada, "Mercado Bom Preço")

        assert resposta.json()["categoria"] == "Mercado"

    def test_borda_nenhuma_regra_corresponde(self, client, conta_configurada):
        """Scenario: Caso de borda — nenhuma regra corresponde; sugestão vazia, sem erro."""
        client.post("/regras", json={"chave": "padaria", "categoria": "Mercado", "pessoas": ["Ana"]},
                    headers=conta_configurada)

        resposta = sugerir(client, conta_configurada, "Posto de gasolina")

        assert resposta.status_code == 200
        assert resposta.json()["categoria"] is None
        assert resposta.json()["pessoas"] == []
        assert resposta.json()["chave_encontrada"] is None

    def test_borda_descricao_vazia(self, client, conta_configurada):
        """Scenario: Caso de borda — descrição vazia."""
        client.post("/regras", json={"chave": "padaria", "categoria": "Mercado", "pessoas": ["Ana"]},
                    headers=conta_configurada)

        resposta = sugerir(client, conta_configurada, "")

        assert resposta.status_code == 200
        assert resposta.json()["categoria"] is None
        assert resposta.json()["chave_encontrada"] is None


class TestCriacaoDeRegraAoRegistrarDespesa:
    """Requirement: Criação de regra ao registrar despesa"""

    def test_primeira_despesa_gera_regra_quando_memorizar_esta_marcado(self, client, conta_configurada):
        """Scenario: Primeira despesa gera regra."""
        assert client.get("/regras", headers=conta_configurada).json() == []

        lancar(
            client, conta_configurada,
            descricao="Mercado Bom Preço", categoria="Mercado", salvar_regra=True,
        )

        regras = client.get("/regras", headers=conta_configurada).json()
        assert len(regras) == 1
        assert regras[0]["categoria"] == "Mercado"
        # a chave vem das duas primeiras palavras da descricao
        assert regras[0]["chave"] == "Mercado Bom"

    def test_despesa_sem_pedir_memorizacao_nao_cria_regra(self, client, conta_configurada):
        """Scenario: Despesa registrada sem pedir memorização."""
        lancar(client, conta_configurada, descricao="Mercado Bom Preço", categoria="Mercado")

        assert client.get("/regras", headers=conta_configurada).json() == []

    def test_memorizar_explicitamente_falso_nao_cria_regra(self, client, conta_configurada):
        """Scenario: Despesa registrada sem pedir memorização — flag explicitamente falsa."""
        lancar(
            client, conta_configurada,
            descricao="Mercado Bom Preço", categoria="Mercado", salvar_regra=False,
        )

        assert client.get("/regras", headers=conta_configurada).json() == []

    def test_borda_regra_ja_existente_nao_e_duplicada(self, client, conta_configurada):
        """Scenario: Caso de borda — regra já existente não é duplicada."""
        lancar(client, conta_configurada, descricao="Mercado Bom Preço",
               categoria="Mercado", salvar_regra=True)
        assert len(client.get("/regras", headers=conta_configurada).json()) == 1

        lancar(client, conta_configurada, descricao="Mercado Bom Preço",
               categoria="Transporte", salvar_regra=True)

        assert len(client.get("/regras", headers=conta_configurada).json()) == 1

    def test_regra_criada_guarda_as_pessoas_informadas(self, client, conta_configurada):
        """Requirement: a regra é associada à categoria E às pessoas informadas."""
        lancar(
            client, conta_configurada, descricao="Farmacia Central",
            categoria="Mercado", pessoas=["Ana", "Bruno"], salvar_regra=True,
        )

        regras = client.get("/regras", headers=conta_configurada).json()
        assert regras[0]["pessoas"] == ["Ana", "Bruno"]


class TestGestaoDasRegras:
    """Requirement: Gestão das regras"""

    def test_remover_regra_que_classifica_errado(self, client, conta_configurada):
        """Scenario: Remover regra que classifica errado."""
        criada = client.post(
            "/regras",
            json={"chave": "padaria", "categoria": "Transporte", "pessoas": []},
            headers=conta_configurada,
        )
        assert sugerir(client, conta_configurada, "Padaria da esquina").json()["categoria"] == "Transporte"

        resposta = client.delete(f"/regras/{criada.json()['id']}", headers=conta_configurada)

        assert resposta.status_code == 204
        assert sugerir(client, conta_configurada, "Padaria da esquina").json()["categoria"] is None

    def test_consultar_regras_da_conta(self, client, conta_configurada):
        """Requirement: o sistema SHALL permitir consultar as regras da conta."""
        client.post("/regras", json={"chave": "padaria", "categoria": "Mercado", "pessoas": []},
                    headers=conta_configurada)

        resposta = client.get("/regras", headers=conta_configurada)

        assert resposta.status_code == 200
        assert [r["chave"] for r in resposta.json()] == ["padaria"]
