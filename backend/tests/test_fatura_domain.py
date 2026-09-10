"""
Testes do módulo de domínio (app/domain/fatura.py).

Escritos ANTES da implementação (TDD) — cobrem as regras de negócio
centrais herdadas do protótipo "Caderneta": ciclo de fechamento de fatura,
soma de meses, rateio entre pessoas, geração de parcelas e motor de
regras de auto-categorização.
"""
import pytest
from app.domain.fatura import (
    soma_mes,
    fatura_de,
    cada_um,
    gerar_parcelas,
    aplicar_regra,
    normalizar,
)


class TestSomaMes:
    def test_soma_dentro_do_mesmo_ano(self):
        assert soma_mes("2026-09", 1) == "2026-10"

    def test_soma_virando_o_ano(self):
        assert soma_mes("2026-11", 2) == "2027-01"

    def test_soma_negativa_regride_meses(self):
        assert soma_mes("2026-03", -2) == "2026-01"

    def test_soma_negativa_virando_ano_anterior(self):
        assert soma_mes("2026-01", -1) == "2025-12"


class TestFaturaDe:
    """Cartão fecha em um dia do mês; compra após o fechamento cai no ciclo seguinte.
    'desloca' é quantos meses além disso até a fatura efetivamente cobrar."""

    def test_compra_antes_do_fechamento_fica_no_mesmo_ciclo(self):
        cartao = {"nome": "Cartão A", "fecha": 24, "desloca": 1}
        # dia 10, fecha dia 24 -> ainda dentro do ciclo de setembro
        assert fatura_de("2026-09-10", cartao) == "2026-10"  # +1 de desloca

    def test_compra_depois_do_fechamento_avanca_um_ciclo(self):
        cartao = {"nome": "Cartão A", "fecha": 24, "desloca": 1}
        # dia 28, fecha dia 24 -> cai no ciclo de outubro, + desloca 1 = novembro
        assert fatura_de("2026-09-28", cartao) == "2026-11"

    def test_cartao_sem_fechamento_nao_desloca(self):
        cartao = {"nome": "Pix", "fecha": 0, "desloca": 0}
        assert fatura_de("2026-09-15", cartao) == "2026-09"

    def test_caso_de_borda_compra_no_dia_exato_do_fechamento(self):
        # dia igual ao fechamento NÃO empurra de ciclo (só dia > fecha empurra)
        cartao = {"nome": "Cartão A", "fecha": 24, "desloca": 0}
        assert fatura_de("2026-09-24", cartao) == "2026-09"


class TestCadaUm:
    def test_divide_igualmente_entre_pessoas(self):
        lanc = {"valor": 300.0, "pessoas": ["Ana", "Bruno", "Carla"]}
        assert cada_um(lanc) == pytest.approx(100.0)

    def test_sem_pessoas_retorna_zero(self):
        lanc = {"valor": 300.0, "pessoas": []}
        assert cada_um(lanc) == 0

    def test_uma_pessoa_fica_com_o_valor_total(self):
        lanc = {"valor": 50.5, "pessoas": ["Ana"]}
        assert cada_um(lanc) == pytest.approx(50.5)


class TestGerarParcelas:
    def test_avista_gera_uma_parcela_no_mes_da_fatura(self):
        parcelas = gerar_parcelas(valor=300.0, n=1, mes_base="2026-10")
        assert len(parcelas) == 1
        assert parcelas[0]["mes"] == "2026-10"
        assert parcelas[0]["valor"] == pytest.approx(300.0)
        assert parcelas[0]["parcela"] == ""

    def test_parcelado_distribui_nos_meses_seguintes(self):
        parcelas = gerar_parcelas(valor=1200.0, n=4, mes_base="2026-10")
        assert [p["mes"] for p in parcelas] == ["2026-10", "2026-11", "2026-12", "2027-01"]
        assert all(p["valor"] == pytest.approx(300.0) for p in parcelas)
        assert [p["parcela"] for p in parcelas] == ["1/4", "2/4", "3/4", "4/4"]

    def test_arredondamento_nao_perde_centavos(self):
        # 100 / 3 = 33.333... — a soma das parcelas deve bater com o valor original
        parcelas = gerar_parcelas(valor=100.0, n=3, mes_base="2026-10")
        total = sum(p["valor"] for p in parcelas)
        assert total == pytest.approx(100.0, abs=0.01)

    def test_caso_de_borda_numero_de_parcelas_invalido_vira_uma(self):
        parcelas = gerar_parcelas(valor=50.0, n=0, mes_base="2026-10")
        assert len(parcelas) == 1


class TestAplicarRegra:
    def test_encontra_regra_por_palavra_chave_na_descricao(self):
        regras = [
            {"chave": "mercado bom preco", "cat": "Mercado", "pessoas": ["Ana"]},
            {"chave": "posto", "cat": "Combustível", "pessoas": []},
        ]
        resultado = aplicar_regra("Compra no Mercado Bom Preço", regras)
        assert resultado is not None
        assert resultado["cat"] == "Mercado"
        assert resultado["pessoas"] == ["Ana"]

    def test_ignora_acentos_e_maiusculas(self):
        regras = [{"chave": "padaria", "cat": "Alimentação", "pessoas": []}]
        assert aplicar_regra("PADARIA São José", regras) is not None

    def test_caso_de_borda_nenhuma_regra_corresponde(self):
        regras = [{"chave": "posto", "cat": "Combustível", "pessoas": []}]
        assert aplicar_regra("Cinema", regras) is None

    def test_caso_de_borda_descricao_vazia(self):
        regras = [{"chave": "posto", "cat": "Combustível", "pessoas": []}]
        assert aplicar_regra("", regras) is None


class TestNormalizar:
    def test_remove_acentos_e_baixa_caixa(self):
        assert normalizar("Alimentação") == "alimentacao"
