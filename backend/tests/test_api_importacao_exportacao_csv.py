"""
Testes de API da capacidade `importacao-exportacao-csv`.

Um teste por cenário de openspec/specs/importacao-exportacao-csv/spec.md.
"""
import pytest

from app.domain.csv_lancamentos import COLUNAS

CABECALHO = ",".join(COLUNAS)


def lancar(client, headers, **campos):
    corpo = {
        "valor": 100.0, "descricao": "Compra", "data": "2026-09-05",
        "cartao": "Cartao A", "categoria": "Mercado", "pessoas": ["Ana"], "parcelas": 1,
    }
    corpo.update(campos)
    return client.post("/lancamentos", json=corpo, headers=headers)


def importar(client, headers, texto):
    return client.post(
        "/lancamentos/importar",
        files={"arquivo": ("lancamentos.csv", texto.encode("utf-8"), "text/csv")},
        headers=headers,
    )


@pytest.fixture
def conta_csv(client, conta):
    client.post(
        "/onboarding",
        json={"renda_principal": 0, "pessoas": ["Ana", "Bruno"],
              "cartoes": [{"nome": "Cartao A", "cor": "#111", "fecha": 0, "desloca": 0}],
              "categorias": ["Mercado"]},
        headers=conta,
    )
    return conta


class TestExportacaoDeLancamentos:
    """Requirement: Exportação de lançamentos"""

    def test_exportar_conta_com_lancamentos(self, client, conta_csv):
        """Scenario: Exportar conta com lançamentos."""
        lancar(client, conta_csv, valor=300.0, descricao="Mercado", pessoas=["Ana", "Bruno"])
        lancar(client, conta_csv, valor=80.0, descricao="Padaria", pessoas=["Ana"])

        resposta = client.get("/lancamentos/exportar", headers=conta_csv)

        assert resposta.status_code == 200
        assert resposta.headers["content-type"].startswith("text/csv")
        linhas = resposta.text.strip().split("\n")
        assert linhas[0] == CABECALHO
        assert len(linhas) == 3
        assert "Mercado" in linhas[1] and "Ana;Bruno" in linhas[1]
        assert "Padaria" in linhas[2]

    def test_borda_conta_sem_lancamentos(self, client, conta_csv):
        """Scenario: Caso de borda — conta sem lançamentos devolve só o cabeçalho."""
        resposta = client.get("/lancamentos/exportar", headers=conta_csv)

        assert resposta.status_code == 200
        assert resposta.text.strip() == CABECALHO

    def test_exportacao_e_isolada_por_conta(self, client, conta_csv, segunda_conta):
        """Requirement: exporta os lançamentos da conta AUTENTICADA."""
        lancar(client, conta_csv, valor=300.0, descricao="Mercado")

        resposta = client.get("/lancamentos/exportar", headers=segunda_conta)

        assert resposta.text.strip() == CABECALHO

    def test_exportacao_exige_credencial(self, client):
        assert client.get("/lancamentos/exportar").status_code == 401


class TestImportacaoDeLancamentos:
    """Requirement: Importação de lançamentos"""

    def test_ciclo_de_exportacao_e_importacao_preserva_os_dados(
        self, client, conta_csv, segunda_conta
    ):
        """Scenario: Ciclo de exportação e importação preserva os dados."""
        lancar(client, conta_csv, valor=300.0, descricao="Mercado", pessoas=["Ana", "Bruno"])
        lancar(client, conta_csv, valor=80.0, descricao="Padaria", pessoas=["Ana"])
        lancar(client, conta_csv, valor=45.5, descricao="Farmacia", pessoas=[])
        exportado = client.get("/lancamentos/exportar", headers=conta_csv).text

        resposta = importar(client, segunda_conta, exportado)

        assert resposta.status_code == 200
        assert resposta.json() == {"importados": 3, "rejeitados": []}

        recriados = client.get("/lancamentos", headers=segunda_conta).json()
        recriados.sort(key=lambda l: l["id"])
        assert [l["descricao"] for l in recriados] == ["Mercado", "Padaria", "Farmacia"]
        assert [l["valor"] for l in recriados] == [300.0, 80.0, 45.5]
        assert [l["mes"] for l in recriados] == ["2026-09"] * 3
        assert [l["pessoas"] for l in recriados] == [["Ana", "Bruno"], ["Ana"], []]

    def test_borda_linha_malformada_nao_aborta_a_importacao(self, client, conta_csv):
        """Scenario: Caso de borda — linha malformada não aborta a importação."""
        texto = (
            f"{CABECALHO}\n"
            "2026-09-05,2026-09,Mercado,Mercado,Cartao A,,300.00,Ana,r\n"
            "2026-09-06,2026-09,Padaria,Mercado,Cartao A,,vinte,Ana,r\n"
            "2026-09-07,2026-09,Farmacia,Mercado,Cartao A,,45.50,Ana,r\n"
        )

        resposta = importar(client, conta_csv, texto)

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["importados"] == 2
        assert len(corpo["rejeitados"]) == 1
        assert corpo["rejeitados"][0]["linha"] == 3
        assert "não numérico" in corpo["rejeitados"][0]["motivo"]

        descricoes = [l["descricao"] for l in client.get("/lancamentos", headers=conta_csv).json()]
        assert sorted(descricoes) == ["Farmacia", "Mercado"]

    def test_borda_arquivo_sem_cabecalho_reconhecivel(self, client, conta_csv):
        """Scenario: Caso de borda — arquivo sem cabeçalho reconhecível é recusado inteiro."""
        texto = "nome,sobrenome,idade\nAna,Silva,30\nBruno,Souza,28\n"

        resposta = importar(client, conta_csv, texto)

        assert resposta.status_code == 400
        assert "cabeçalho" in resposta.json()["detail"].lower()
        assert client.get("/lancamentos", headers=conta_csv).json() == []

    def test_importacao_e_isolada_por_conta(self, client, conta_csv, segunda_conta):
        """Requirement: os lançamentos entram na conta autenticada."""
        texto = f"{CABECALHO}\n2026-09-05,2026-09,Mercado,Mercado,Cartao A,,300.00,Ana,r\n"

        importar(client, segunda_conta, texto)

        assert client.get("/lancamentos", headers=conta_csv).json() == []
        assert len(client.get("/lancamentos", headers=segunda_conta).json()) == 1

    def test_importacao_exige_credencial(self, client):
        resposta = client.post(
            "/lancamentos/importar",
            files={"arquivo": ("x.csv", CABECALHO.encode(), "text/csv")},
        )
        assert resposta.status_code == 401
