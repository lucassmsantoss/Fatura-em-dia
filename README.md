# Fatura em Dia

Aplicativo web de controle financeiro pessoal com rateio de despesas entre pessoas (família, casal, colegas de casa), parcelamento de compras e acompanhamento de faturas de cartão por ciclo de fechamento.

Repositório: https://github.com/lucassmsantoss/Fatura-em-dia

Projeto final da disciplina **Desenvolvimento de Software com IA** — Programa de Pós-Graduação em Tecnologia da Informação, Instituto Metrópole Digital, UFRN. Professor: Dr. Jean Mário Moreira de Lima.

---

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Stack tecnológica](#stack-tecnológica)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Processo de desenvolvimento (SDD + IA)](#processo-de-desenvolvimento-sdd--ia)
- [Testes](#testes)
- [Equipe](#equipe)
- [Licença](#licença)

---

## Sobre o projeto

O sistema resolve um problema real e cotidiano: controlar gastos pessoais que são, ao mesmo tempo, parcelados em diferentes cartões e divididos com outras pessoas (cônjuge, familiares, colegas de casa). Planilhas manuais não escalam bem para isso — é fácil perder o controle de quem deve o quê, em qual mês uma parcela cai, ou quanto ainda falta comprometer da renda do mês.

O projeto nasceu de um protótipo pessoal ("Caderneta") criado por um dos integrantes da dupla para uso próprio. Para este trabalho, o protótipo foi **generalizado**: removemos todos os dados e regras específicas de uma pessoa, e construímos um fluxo de configuração inicial (onboarding) e uma arquitetura com backend real, para que qualquer usuário possa usar o sistema desde o primeiro acesso.

## Funcionalidades

Lista completa com critérios de aceite em [`docs/requisitos-funcionais.md`](docs/requisitos-funcionais.md). Resumo:

| # | Funcionalidade |
|---|---|
| RF01 | Cadastro e login de usuário |
| RF02 | Onboarding de configuração inicial (nome, receita, pessoas, cartões, categorias) |
| RF03 | CRUD de pessoas para rateio de despesas |
| RF04 | CRUD de cartões/formas de pagamento (com dia de fechamento e deslocamento de fatura) |
| RF05 | CRUD de categorias de despesa |
| RF06 | Lançamento de despesa (à vista ou parcelada, dividida entre pessoas) |
| RF07 | Auto-categorização por regra de palavra-chave na descrição |
| RF08 | Painel mensal (dashboard) com totais, receita, sobra/falta e gastos por categoria/cartão |
| RF09 | Previsão de meses futuros calculada dinamicamente a partir de parcelas e contas fixas já lançadas |
| RF10 | Extrato e cobrança por pessoa (saldo devedor, registro de pagamento) |
| RF11 (bônus) | Exportação/importação de lançamentos via CSV |

## Arquitetura

O sistema é dividido em duas camadas com um contrato de API REST explícito entre elas — decisão documentada em [`docs/adr/0001-arquitetura-rest-api.md`](docs/adr/0001-arquitetura-rest-api.md):

- **Backend**: expõe uma API REST (autenticação, CRUDs de configuração, lançamentos, cálculo de painel/previsão) e persiste os dados em um banco relacional.
- **Frontend**: aplicação web (SPA) que consome a API via HTTP/JSON.

Um diagrama de arquitetura (C4/Mermaid) será adicionado em `docs/arquitetura.md` conforme o desenvolvimento avança.

```
┌─────────────┐        HTTP/JSON        ┌──────────────┐        ┌────────────┐
│  Frontend   │ ──────────────────────▶ │   Backend    │ ─────▶ │  Banco de  │
│   (SPA)     │ ◀────────────────────── │  (API REST)  │ ◀───── │   dados    │
└─────────────┘                         └──────────────┘        └────────────┘
```

## Stack tecnológica

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, autenticação JWT (python-jose) e hash de senha com bcrypt (passlib).
- **Frontend**: HTML/CSS/JavaScript puro (SPA sem build step), consumindo a API via `fetch()`.
- **Banco de dados**: SQLite.
- **Testes**: pytest — o módulo de domínio (`app/domain/fatura.py`, com as regras de ciclo de fatura, rateio, parcelamento e auto-categorização) tem cobertura unitária completa, escrita antes da implementação (TDD).
- **Ferramentas de IA / harness**: Claude Code, com processo de Spec-Driven Development documentado em `docs/`.

## Estrutura do repositório

```
.
├── README.md
├── .gitignore
├── docs/
│   ├── especificacao-inicial.md      # Spec inicial (prompt, requisitos, critérios de aceite, plano de tarefas)
│   ├── requisitos-funcionais.md      # Requisitos funcionais detalhados (RF01–RF11)
│   ├── mapeamento_funcionalidades.md # Mapeamento do protótipo original vs. o que foi generalizado
│   ├── plano_inicial.md              # Planejamento e cronograma do projeto
│   └── adr/
│       └── 0001-arquitetura-rest-api.md
├── backend/
│   ├── app/
│   │   ├── main.py           # ponto de entrada da API (FastAPI)
│   │   ├── database.py       # engine/sessão SQLAlchemy (SQLite)
│   │   ├── models.py         # tabelas: Usuario, Pessoa, Cartao, Categoria, Regra, Lancamento, Pagamento, Receita
│   │   ├── schemas.py        # contratos de entrada/saída da API (Pydantic)
│   │   ├── auth.py           # hash de senha e JWT
│   │   ├── domain/
│   │   │   └── fatura.py     # regras de negócio puras (ciclo de fatura, rateio, parcelamento, regras)
│   │   └── routers/
│   │       ├── auth.py       # RF01 — cadastro/login
│   │       ├── config.py     # RF02–RF05, RF07 — onboarding, pessoas, cartões, categorias, regras
│   │       ├── lancamentos.py# RF06, RF07 — lançar despesa, sugestão por regra
│   │       └── painel.py     # RF08–RF10 — painel, previsão, extrato, pagamentos, receita
│   ├── tests/
│   │   └── test_fatura_domain.py  # cobertura unitária do módulo de domínio (TDD)
│   ├── requirements.txt
│   └── pytest.ini
└── frontend/
    ├── index.html
    ├── css/estilo.css
    └── js/
        ├── api.js   # cliente HTTP da API (fetch + JWT em localStorage)
        └── app.js   # SPA: login/registro, onboarding, lançar, painel, extrato, ajustes
```

## Como rodar o projeto

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000` — documentação interativa (Swagger) em `http://localhost:8000/docs`, gerada automaticamente pelo FastAPI a partir dos contratos definidos em `app/schemas.py`.

### Frontend

Com o backend rodando em `http://localhost:8000`, basta abrir `frontend/index.html` diretamente no navegador (ou servir a pasta com qualquer servidor estático, ex. `python -m http.server` dentro de `frontend/`). Não há build step — é HTML/CSS/JS puro.

### Rodando os testes

```bash
cd backend
pytest -v
```

## Processo de desenvolvimento (SDD + IA)

Este projeto foi desenvolvido com apoio de agente de IA, seguindo Spec-Driven Development (SDD):

1. **Especificação** — prompt inicial, requisitos e critérios de aceite (Given/When/Then, incluindo casos de borda) em [`docs/especificacao-inicial.md`](docs/especificacao-inicial.md) e [`docs/requisitos-funcionais.md`](docs/requisitos-funcionais.md).
2. **Harness e guardrails** — nível de autonomia do agente, mecanismo de guardrail configurado e evidência de funcionamento serão documentados aqui conforme aplicados durante a implementação.
3. **Observabilidade** — histórico de sessões do agente e revisão de diffs antes de cada commit.
4. **Decisões de arquitetura** — registradas como ADRs em [`docs/adr/`](docs/adr/).

## Testes

O módulo de domínio (`backend/app/domain/fatura.py`) concentra toda a lógica de negócio pura — ciclo de fechamento de fatura, soma de meses, rateio entre pessoas, geração de parcelas e motor de regras de auto-categorização — e tem cobertura unitária completa em `backend/tests/test_fatura_domain.py` (20 testes, incluindo casos de borda como valor com arredondamento, número de parcelas inválido e descrição vazia). Os testes foram escritos antes da implementação (TDD): primeiro a suíte falhando, depois o código até todos passarem.

```bash
cd backend && pytest -v
```

## Equipe

- Lucas Medeiros dos Santos — matrícula 20261009725
- Maria Jamilli Lemos de Macedo — matrícula 20261006115

## Licença

Projeto acadêmico desenvolvido para fins avaliativos da disciplina Desenvolvimento de Software com IA (UFRN/IMD).
