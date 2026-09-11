"""Ponto de entrada da API — Fatura em Dia."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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


@app.get("/saude", tags=["status"])
def saude():
    return {"status": "ok", "servico": "Fatura em Dia API"}


# ---------- Interface (SPA) ----------
# O build do frontend é servido pelo próprio backend, na mesma origem da API.
# O mount fica DEPOIS de todos os routers de propósito: o Starlette resolve as
# rotas na ordem em que foram registradas, então qualquer caminho da API é
# atendido pela API, e só o que sobra cai no SPA.
#
# Em desenvolvimento o dist/ não existe e o Vite serve a interface na 5173,
# fazendo proxy da API para cá — por isso o mount é condicional.
DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="spa")
