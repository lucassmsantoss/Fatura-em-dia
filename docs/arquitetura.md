# Arquitetura — Fatura em Dia

Este documento complementa a [ADR 0001](adr/0001-arquitetura-rest-api.md) (decisão de dividir o sistema em backend REST + frontend SPA) e a [ADR 0002](adr/0002-guardrail-pre-commit.md) (guardrail) com uma visão visual da arquitetura, no estilo C4 (Contexto e Contêineres).

## Diagrama de contexto

Mostra o sistema como uma caixa única e quem interage com ele.

```mermaid
C4Context
    title Fatura em Dia — Diagrama de Contexto

    Person(usuario, "Usuário", "Pessoa que quer controlar gastos pessoais, parcelamentos e rateio de despesas")

    System(faturaEmDia, "Fatura em Dia", "Permite cadastrar cartões, categorias e pessoas, lançar despesas (à vista ou parceladas), ratear entre pessoas e acompanhar o painel mensal e a previsão de meses futuros")

    Rel(usuario, faturaEmDia, "Usa via navegador", "HTTPS")
```

## Diagrama de contêineres

Detalha os blocos internos do sistema e como eles se comunicam.

```mermaid
C4Container
    title Fatura em Dia — Diagrama de Contêineres

    Person(usuario, "Usuário")

    Container_Boundary(sistema, "Fatura em Dia") {
        Container(frontend, "Frontend (SPA)", "HTML + CSS + JavaScript puro", "Login/registro, onboarding, lançamento de despesas, painel, extrato — consome a API via fetch()")
        Container(backend, "Backend (API REST)", "Python + FastAPI", "Autenticação (JWT), CRUDs de configuração, lançamentos, cálculo de painel e previsão")
        ContainerDb(banco, "Banco de dados", "SQLite", "Usuarios, Pessoas, Cartoes, Categorias, Regras, Lancamentos, Pagamentos, Receitas")
    }

    Rel(usuario, frontend, "Usa", "HTTPS/navegador")
    Rel(frontend, backend, "Consome", "HTTP/JSON (fetch)")
    Rel(backend, banco, "Lê e escreve", "SQLAlchemy/SQL")
```

## Componentes do backend

O backend é organizado em camadas para manter as regras de negócio isoladas de detalhes de framework/web (facilita testar `app/domain/fatura.py` sem subir servidor nenhum):

```mermaid
graph TD
    subgraph Backend [ "backend/app" ]
        main["main.py<br/>(entrypoint FastAPI, CORS, lifespan)"]

        subgraph routers [ "routers/ (camada HTTP)" ]
            r_auth["auth.py<br/>RF01 — cadastro/login"]
            r_config["config.py<br/>RF02–RF05, RF07 — onboarding, pessoas, cartões, categorias, regras"]
            r_lanc["lancamentos.py<br/>RF06, RF07 — lançar despesa"]
            r_painel["painel.py<br/>RF08–RF10 — painel, previsão, extrato, pagamentos"]
        end

        auth_py["auth.py<br/>(hash de senha + JWT)"]
        models["models.py<br/>(tabelas SQLAlchemy)"]
        schemas["schemas.py<br/>(contratos Pydantic)"]
        database["database.py<br/>(engine/sessão SQLite)"]

        subgraph domain [ "domain/ (regras de negócio puras)" ]
            fatura["fatura.py<br/>fatura_de, cada_um, gerar_parcelas, aplicar_regra"]
        end
    end

    main --> routers
    r_auth --> auth_py
    r_auth --> models
    r_config --> models
    r_lanc --> models
    r_lanc --> domain
    r_painel --> models
    r_painel --> domain
    routers --> schemas
    models --> database

    tests["tests/test_fatura_domain.py<br/>(20 testes unitários, TDD)"] -.->|testa isoladamente, sem subir API| fatura
```

## Fluxo de autenticação (JWT)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant F as Frontend (SPA)
    participant B as Backend (FastAPI)
    participant DB as SQLite

    U->>F: Preenche login (email + senha)
    F->>B: POST /auth/login
    B->>DB: Busca usuário por email
    DB-->>B: Usuario (senha_hash)
    B->>B: Verifica senha (bcrypt) e gera JWT
    B-->>F: 200 OK { token }
    F->>F: Salva token no localStorage
    F->>B: Requisições seguintes com Authorization: Bearer <token>
    B->>B: Valida JWT antes de processar
```
