"""
Testes de API da capacidade `configuracao-inicial`.

Um teste por cenário de openspec/specs/configuracao-inicial/spec.md.
"""
from datetime import date


def mes_corrente() -> str:
    return date.today().strftime("%Y-%m")


CONFIGURACAO_VALIDA = {
    "renda_principal": 5000.0,
    "pessoas": ["Ana", "Bruno"],
    "cartoes": [{"nome": "Cartao A", "cor": "#0E6F63", "fecha": 10, "desloca": 0}],
    "categorias": ["Mercado", "Transporte"],
}


class TestConfiguracaoInicialGuiada:
    """Requirement: Configuração inicial guiada"""

    def test_conclusao_cria_os_cadastros_e_marca_como_concluida(self, client, conta):
        """Scenario: Conclusão da configuração inicial."""
        resposta = client.post("/onboarding", json=CONFIGURACAO_VALIDA, headers=conta)
        assert resposta.status_code == 200

        assert [p["nome"] for p in client.get("/pessoas", headers=conta).json()] == ["Ana", "Bruno"]
        assert [c["nome"] for c in client.get("/cartoes", headers=conta).json()] == ["Cartao A"]
        assert [c["nome"] for c in client.get("/categorias", headers=conta).json()] == [
            "Mercado",
            "Transporte",
        ]
        assert client.get("/auth/eu", headers=conta).json()["onboarding_concluido"] is True

    def test_a_renda_informada_vira_receita_do_mes_corrente(self, client, conta):
        """Requirement: o fluxo cadastra a renda mensal — não apenas pessoas, cartões e categorias."""
        client.post("/onboarding", json=CONFIGURACAO_VALIDA, headers=conta)

        painel = client.get(f"/painel/{mes_corrente()}", headers=conta).json()
        assert painel["receita_total"] == 5000.0

    def test_retorno_apos_configuracao_concluida(self, client, conta):
        """Scenario: Retorno após configuração concluída — não repete o fluxo."""
        client.post("/onboarding", json=CONFIGURACAO_VALIDA, headers=conta)

        eu = client.get("/auth/eu", headers=conta).json()

        assert eu["onboarding_concluido"] is True

    def test_borda_nenhuma_pessoa_informada_e_recusado(self, client, conta):
        """Scenario: Caso de borda — nenhuma pessoa informada; recusa e explica."""
        sem_pessoas = dict(CONFIGURACAO_VALIDA, pessoas=[])

        resposta = client.post("/onboarding", json=sem_pessoas, headers=conta)

        assert resposta.status_code == 400
        assert "pessoa" in resposta.json()["detail"].lower()
        # nada pode ter sido persistido, nem a configuracao marcada como concluida
        assert client.get("/cartoes", headers=conta).json() == []
        assert client.get("/categorias", headers=conta).json() == []
        assert client.get("/auth/eu", headers=conta).json()["onboarding_concluido"] is False

    def test_borda_nenhuma_forma_de_pagamento_e_recusado(self, client, conta):
        """Requirement: o fluxo exige ao menos uma forma de pagamento."""
        sem_cartoes = dict(CONFIGURACAO_VALIDA, cartoes=[])

        resposta = client.post("/onboarding", json=sem_cartoes, headers=conta)

        assert resposta.status_code == 400
        assert client.get("/pessoas", headers=conta).json() == []
        assert client.get("/auth/eu", headers=conta).json()["onboarding_concluido"] is False


class TestAusenciaDeDadosPreExistentes:
    """Requirement: Ausência de dados pré-existentes"""

    def test_conta_nova_esta_vazia(self, client, conta):
        """Scenario: Conta nova está vazia."""
        for caminho in ["/pessoas", "/cartoes", "/categorias", "/regras", "/lancamentos"]:
            assert client.get(caminho, headers=conta).json() == [], caminho
        assert client.get("/auth/eu", headers=conta).json()["onboarding_concluido"] is False
