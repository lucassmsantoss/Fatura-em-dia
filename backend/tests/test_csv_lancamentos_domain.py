"""
Testes unitários do módulo de domínio de CSV — puros, sem banco e sem HTTP.

Cobrem o formato em si; os testes de API cobrem o ciclo pela aplicação.
"""
import pytest

from app.domain.csv_lancamentos import (
    COLUNAS,
    CabecalhoInvalido,
    interpretar,
    serializar,
)

UM_LANCAMENTO = {
    "data": "2026-09-05", "mes": "2026-09", "descricao": "Mercado Bom Preço",
    "categoria": "Mercado", "cartao": "Cartao A", "parcela": "1/2",
    "valor": 150.5, "pessoas": ["Ana", "Bruno"], "tipo": "r",
}


class TestSerializar:
    def test_escreve_cabecalho_e_uma_linha_por_lancamento(self):
        texto = serializar([UM_LANCAMENTO, dict(UM_LANCAMENTO, descricao="Padaria")])

        linhas = texto.strip().split("\n")
        assert linhas[0] == ",".join(COLUNAS)
        assert len(linhas) == 3

    def test_lista_vazia_produz_apenas_o_cabecalho(self):
        texto = serializar([])

        assert texto.strip() == ",".join(COLUNAS)

    def test_pessoas_vao_num_campo_unico_separadas_por_ponto_e_virgula(self):
        texto = serializar([UM_LANCAMENTO])

        assert "Ana;Bruno" in texto

    def test_valor_sai_com_duas_casas(self):
        texto = serializar([dict(UM_LANCAMENTO, valor=7)])

        assert ",7.00," in texto

    def test_caso_de_borda_descricao_com_virgula_nao_quebra_as_colunas(self):
        """A vírgula separa colunas; uma descrição que a contenha precisa ser citada."""
        texto = serializar([dict(UM_LANCAMENTO, descricao="Mercado, feira e padaria")])

        lidos, rejeitados = interpretar(texto)
        assert rejeitados == []
        assert lidos[0]["descricao"] == "Mercado, feira e padaria"


class TestInterpretar:
    def test_ciclo_completo_preserva_os_dados(self):
        originais = [
            dict(UM_LANCAMENTO, descricao="A", valor=10.0),
            dict(UM_LANCAMENTO, descricao="B", valor=20.5, pessoas=["Caio"]),
            dict(UM_LANCAMENTO, descricao="C", valor=30.0, pessoas=[]),
        ]

        lidos, rejeitados = interpretar(serializar(originais))

        assert rejeitados == []
        assert [l["descricao"] for l in lidos] == ["A", "B", "C"]
        assert [l["valor"] for l in lidos] == [10.0, 20.5, 30.0]
        assert [l["pessoas"] for l in lidos] == [["Ana", "Bruno"], ["Caio"], []]
        assert all(l["mes"] == "2026-09" for l in lidos)

    def test_arquivo_so_com_cabecalho_devolve_nada_sem_erro(self):
        lidos, rejeitados = interpretar(",".join(COLUNAS) + "\n")

        assert lidos == []
        assert rejeitados == []

    def test_linha_malformada_nao_aborta_as_demais(self):
        texto = serializar([
            dict(UM_LANCAMENTO, descricao="A", valor=10.0),
            dict(UM_LANCAMENTO, descricao="B", valor=20.0),
        ]).replace("20.00", "vinte")

        lidos, rejeitados = interpretar(texto)

        assert [l["descricao"] for l in lidos] == ["A"]
        assert len(rejeitados) == 1
        assert rejeitados[0]["linha"] == 3          # cabeçalho é 1, "A" é 2, a quebrada é 3
        assert "não numérico" in rejeitados[0]["motivo"]

    def test_cabecalho_nao_reconhecido_recusa_o_arquivo_inteiro(self):
        with pytest.raises(CabecalhoInvalido) as erro:
            interpretar("nome,sobrenome,idade\nAna,Silva,30\n")

        assert "Cabeçalho não reconhecido" in str(erro.value)

    @pytest.mark.parametrize("valor,fragmento", [
        ("0.00", "maior que zero"),
        ("-5.00", "maior que zero"),
        ("abc", "não numérico"),
        ("", "não numérico"),
    ])
    def test_valores_invalidos_sao_rejeitados_com_motivo(self, valor, fragmento):
        texto = ",".join(COLUNAS) + f"\n2026-09-05,2026-09,Teste,Mercado,Cartao A,,{valor},Ana,r\n"

        lidos, rejeitados = interpretar(texto)

        assert lidos == []
        assert fragmento in rejeitados[0]["motivo"]

    def test_descricao_vazia_e_rejeitada(self):
        texto = ",".join(COLUNAS) + "\n2026-09-05,2026-09,,Mercado,Cartao A,,10.00,Ana,r\n"

        lidos, rejeitados = interpretar(texto)

        assert lidos == []
        assert "descrição vazia" in rejeitados[0]["motivo"]

    def test_mes_de_fatura_invalido_e_rejeitado(self):
        texto = ",".join(COLUNAS) + "\n2026-09-05,setembro,Teste,Mercado,Cartao A,,10.00,Ana,r\n"

        lidos, rejeitados = interpretar(texto)

        assert lidos == []
        assert "mês de fatura inválido" in rejeitados[0]["motivo"]

    def test_valor_com_virgula_decimal_e_aceito(self):
        """Planilhas em pt-BR exportam 10,50 — aceitar evita rejeição em massa."""
        texto = ",".join(COLUNAS) + '\n2026-09-05,2026-09,Teste,Mercado,Cartao A,,"10,50",Ana,r\n'

        lidos, rejeitados = interpretar(texto)

        assert rejeitados == []
        assert lidos[0]["valor"] == 10.5

    def test_tipo_desconhecido_vira_aconteceu(self):
        texto = ",".join(COLUNAS) + "\n2026-09-05,2026-09,Teste,Mercado,Cartao A,,10.00,Ana,x\n"

        lidos, _ = interpretar(texto)

        assert lidos[0]["tipo"] == "r"
