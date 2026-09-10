"""
Fixtures da suíte de testes de API.

Cada teste roda contra um banco SQLite em memória próprio, criado e descartado
no escopo da função. O banco de desenvolvimento (`fatura_em_dia.db`) nunca é
tocado: a dependency `get_db` é substituída por `dependency_overrides`.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    """Banco em memória isolado por teste. StaticPool mantém a mesma conexão."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sessao = Session()
    try:
        yield sessao
    finally:
        sessao.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    """Cliente HTTP apontado para o banco isolado do teste."""
    def _get_db_de_teste():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_de_teste
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def registrar_e_entrar(client, nome="Ana", email="ana@exemplo.com", senha="segredo123"):
    """Cria uma conta, autentica e devolve o cabeçalho de autorização."""
    client.post("/auth/registrar", json={"nome": nome, "email": email, "senha": senha})
    resposta = client.post("/auth/login", json={"email": email, "senha": senha})
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def conta(client):
    """Conta autenticada, sem configuração inicial concluída."""
    return registrar_e_entrar(client)


@pytest.fixture
def segunda_conta(client):
    """Segunda conta autenticada, para os cenários de isolamento."""
    return registrar_e_entrar(client, nome="Bruno", email="bruno@exemplo.com", senha="outrasenha1")


@pytest.fixture
def conta_configurada(client, conta):
    """Conta com configuração inicial concluída: uma pessoa, um cartão e uma categoria."""
    client.post(
        "/onboarding",
        json={
            "renda_principal": 5000.0,
            "pessoas": ["Ana", "Bruno"],
            "cartoes": [{"nome": "Cartao A", "cor": "#0E6F63", "fecha": 10, "desloca": 0}],
            "categorias": ["Mercado", "Transporte"],
        },
        headers=conta,
    )
    return conta
