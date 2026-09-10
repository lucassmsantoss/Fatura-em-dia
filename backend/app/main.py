"""Ponto de entrada da API — Fatura em Dia."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, config, lancamentos, painel


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Fatura em Dia — API",
    description="Controle financeiro pessoal com rateio de despesas, parcelamento e ciclo de fatura por cartão.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em desenvolvimento; restringir em produção
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(config.router)
app.include_router(lancamentos.router)
app.include_router(painel.router)


@app.get("/", tags=["status"])
def raiz():
    return {"status": "ok", "servico": "Fatura em Dia API"}
