"""Schemas Pydantic — contrato de entrada/saída da API (o que o front-end consome)."""
from pydantic import BaseModel, EmailStr, Field


# ---------- Autenticação ----------
class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    senha: str = Field(min_length=6)


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioSaida(BaseModel):
    id: int
    nome: str
    email: EmailStr
    onboarding_concluido: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Onboarding ----------
class OnboardingEntrada(BaseModel):
    renda_principal: float = 0
    pessoas: list[str] = []
    cartoes: list["CartaoCriar"] = []
    categorias: list[str] = []


# ---------- Pessoas ----------
class PessoaCriar(BaseModel):
    nome: str


class PessoaSaida(PessoaCriar):
    id: int

    class Config:
        from_attributes = True


# ---------- Cartões ----------
class CartaoCriar(BaseModel):
    nome: str
    cor: str = "#0E6F63"
    fecha: int = 0
    desloca: int = 0


class CartaoSaida(CartaoCriar):
    id: int

    class Config:
        from_attributes = True


# ---------- Categorias ----------
class CategoriaCriar(BaseModel):
    nome: str


class CategoriaSaida(CategoriaCriar):
    id: int

    class Config:
        from_attributes = True


# ---------- Regras ----------
class RegraCriar(BaseModel):
    chave: str
    categoria: str = ""
    pessoas: list[str] = []


class RegraSaida(RegraCriar):
    id: int

    class Config:
        from_attributes = True


# ---------- Lançamentos ----------
class LancamentoCriar(BaseModel):
    valor: float = Field(gt=0)
    descricao: str = Field(min_length=1)
    data: str  # AAAA-MM-DD
    cartao: str
    categoria: str = ""
    pessoas: list[str] = []
    parcelas: int = 1
    estimativa: bool = False
    salvar_regra: bool = False


class LancamentoAtualizarDono(BaseModel):
    pessoas: list[str]


class LancamentoSaida(BaseModel):
    id: int
    data: str
    mes: str
    descricao: str
    categoria: str
    cartao: str
    parcela: str
    valor: float
    pessoas: list[str]
    tipo: str

    class Config:
        from_attributes = True


class LinhaRejeitada(BaseModel):
    linha: int
    motivo: str


class ImportacaoResultado(BaseModel):
    importados: int
    rejeitados: list[LinhaRejeitada] = []


class SugestaoRegra(BaseModel):
    categoria: str | None = None
    pessoas: list[str] = []
    chave_encontrada: str | None = None


# ---------- Pagamentos ----------
class PagamentoCriar(BaseModel):
    pessoa: str
    valor: float = Field(gt=0)
    data: str
    mes_ref: str
    obs: str = ""


class PagamentoSaida(PagamentoCriar):
    id: int

    class Config:
        from_attributes = True


# ---------- Receita ----------
class ReceitaEntrada(BaseModel):
    mes: str
    renda_principal: float = 0
    renda_extra: float = 0


class ReceitaSaida(ReceitaEntrada):
    class Config:
        from_attributes = True


# ---------- Painel ----------
class GastoPorCategoria(BaseModel):
    categoria: str
    valor: float


class SaldoPessoa(BaseModel):
    pessoa: str
    devido_no_mes: float
    pago_no_mes: float
    acumulado: float


class PainelSaida(BaseModel):
    mes: str
    total_mes: float
    meu_total: float
    receita_total: float
    sobra_ou_falta: float
    sem_dono: float
    gastos_por_categoria: list[GastoPorCategoria]
    saldos_por_pessoa: list[SaldoPessoa]


class PrevisaoMes(BaseModel):
    mes: str
    total_compromissos: float
    total_estimativas: float
    total_previsto: float
