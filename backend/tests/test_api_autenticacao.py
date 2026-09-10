"""
Testes de API da capacidade `autenticacao`.

Cada teste corresponde a um cenário de openspec/specs/autenticacao/spec.md.
O nome do cenário está citado na docstring para manter a rastreabilidade
contrato -> teste explícita.
"""


class TestCadastroDeConta:
    """Requirement: Cadastro de conta"""

    def test_cadastro_com_dados_validos(self, client):
        """Scenario: Cadastro com dados válidos — conta criada sem expor a senha."""
        resposta = client.post(
            "/auth/registrar",
            json={"nome": "Ana", "email": "ana@exemplo.com", "senha": "segredo123"},
        )
        assert resposta.status_code == 201
        corpo = resposta.json()
        assert corpo["email"] == "ana@exemplo.com"
        assert corpo["nome"] == "Ana"
        # a senha nao pode aparecer em nenhuma forma — nem plana, nem hash
        serializado = resposta.text.lower()
        assert "senha" not in serializado
        assert "segredo123" not in serializado

    def test_email_ja_cadastrado_e_recusado(self, client):
        """Scenario: Email já cadastrado — recusa informando o motivo."""
        dados = {"nome": "Ana", "email": "ana@exemplo.com", "senha": "segredo123"}
        client.post("/auth/registrar", json=dados)

        resposta = client.post("/auth/registrar", json=dados)

        assert resposta.status_code == 400
        assert "email" in resposta.json()["detail"].lower()

    def test_borda_senha_curta_nao_persiste_conta(self, client):
        """Scenario: Caso de borda — senha curta demais; nenhuma conta é persistida."""
        resposta = client.post(
            "/auth/registrar",
            json={"nome": "Ana", "email": "ana@exemplo.com", "senha": "123"},
        )
        assert resposta.status_code == 422

        # a conta nao pode ter sido criada: o login com essa senha deve falhar
        login = client.post("/auth/login", json={"email": "ana@exemplo.com", "senha": "123"})
        assert login.status_code == 401


class TestAutenticacaoESessao:
    """Requirement: Autenticação e sessão"""

    def test_login_com_credenciais_corretas_devolve_credencial_utilizavel(self, client):
        """Scenario: Login com credenciais corretas — credencial serve nas requisições seguintes."""
        client.post(
            "/auth/registrar",
            json={"nome": "Ana", "email": "ana@exemplo.com", "senha": "segredo123"},
        )

        resposta = client.post(
            "/auth/login", json={"email": "ana@exemplo.com", "senha": "segredo123"}
        )

        assert resposta.status_code == 200
        token = resposta.json()["access_token"]
        assert token

        # a credencial tem que ser utilizavel de fato, nao apenas existir
        eu = client.get("/auth/eu", headers={"Authorization": f"Bearer {token}"})
        assert eu.status_code == 200
        assert eu.json()["email"] == "ana@exemplo.com"

    def test_borda_senha_incorreta_nao_distingue_de_email_inexistente(self, client):
        """Scenario: Caso de borda — senha incorreta não distingue de email inexistente."""
        client.post(
            "/auth/registrar",
            json={"nome": "Ana", "email": "ana@exemplo.com", "senha": "segredo123"},
        )

        senha_errada = client.post(
            "/auth/login", json={"email": "ana@exemplo.com", "senha": "senhaerrada"}
        )
        email_inexistente = client.post(
            "/auth/login", json={"email": "ninguem@exemplo.com", "senha": "segredo123"}
        )

        assert senha_errada.status_code == email_inexistente.status_code == 401
        # a mensagem tem que ser identica, para nao revelar qual campo falhou
        assert senha_errada.json()["detail"] == email_inexistente.json()["detail"]

    def test_senha_nao_e_armazenada_em_texto_claro(self, client, db_session):
        """Requirement: sem nunca armazenar a senha em texto claro."""
        from app.models import Usuario

        client.post(
            "/auth/registrar",
            json={"nome": "Ana", "email": "ana@exemplo.com", "senha": "segredo123"},
        )

        usuario = db_session.query(Usuario).filter(Usuario.email == "ana@exemplo.com").first()
        assert usuario is not None
        assert usuario.senha_hash != "segredo123"
        assert "segredo123" not in usuario.senha_hash


class TestIsolamentoDeDadosPorConta:
    """Requirement: Isolamento de dados por conta"""

    def test_requisicao_sem_credencial_nao_devolve_dado(self, client):
        """Scenario: Requisição sem credencial — acesso recusado, nenhum dado devolvido."""
        for caminho in ["/pessoas", "/cartoes", "/categorias", "/regras", "/lancamentos"]:
            resposta = client.get(caminho)
            assert resposta.status_code == 401, caminho
            assert "nome" not in resposta.text

    def test_borda_recurso_de_outra_conta_responde_como_inexistente(
        self, client, conta, segunda_conta
    ):
        """Scenario: Caso de borda — recurso de outra conta é tratado como inexistente."""
        criada = client.post("/pessoas", json={"nome": "Carla"}, headers=conta)
        pessoa_id = criada.json()["id"]

        # a segunda conta nao pode ver a pessoa da primeira
        listagem = client.get("/pessoas", headers=segunda_conta)
        assert listagem.status_code == 200
        assert listagem.json() == []

        # nem remove-la
        remocao = client.delete(f"/pessoas/{pessoa_id}", headers=segunda_conta)
        assert remocao.status_code == 404

        # e nada foi alterado na conta de origem
        original = client.get("/pessoas", headers=conta)
        assert [p["nome"] for p in original.json()] == ["Carla"]

    def test_borda_lancamento_de_outra_conta_responde_como_inexistente(
        self, client, conta_configurada, segunda_conta
    ):
        """Scenario: Caso de borda — aplicado a lançamento, o recurso financeiro central."""
        criado = client.post(
            "/lancamentos",
            json={
                "valor": 100.0,
                "descricao": "Mercado",
                "data": "2026-09-05",
                "cartao": "Cartao A",
                "categoria": "Mercado",
                "pessoas": ["Ana"],
                "parcelas": 1,
            },
            headers=conta_configurada,
        )
        assert criado.status_code == 201
        lancamento_id = criado.json()[0]["id"]

        assert client.get("/lancamentos", headers=segunda_conta).json() == []
        assert client.delete(f"/lancamentos/{lancamento_id}", headers=segunda_conta).status_code == 404
        assert len(client.get("/lancamentos", headers=conta_configurada).json()) == 1
