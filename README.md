# Fatura em Dia

Aplicativo web de controle financeiro pessoal com rateio de despesas entre pessoas (família, casal, colegas de casa), parcelamento de compras e acompanhamento de faturas de cartão por ciclo de fechamento.

Repositório: https://github.com/lucassmsantoss/Fatura-em-dia

Projeto final da disciplina **Desenvolvimento de Software com IA** — Programa de Pós-Graduação em Tecnologia da Informação, Instituto Metrópole Digital, UFRN. Professor: Dr. Jean Mário Moreira de Lima.

---

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Estado atual](#estado-atual)
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

Os onze requisitos funcionais estão **especificados** com critérios de aceite verificáveis em
[`openspec/specs/`](openspec/) — 9 capacidades, 29 requisitos e 69 cenários Given/When/Then,
todos aprovados em `openspec validate --all --strict`. A rastreabilidade RF → capacidade está em
[`docs/requisitos-funcionais.md`](docs/requisitos-funcionais.md).

A **implementação** está em andamento e é construída contra esse contrato, na ordem do plano de
tarefas em [`openspec/changes/conformidade-rf/tasks.md`](openspec/changes/conformidade-rf/tasks.md).
O código presente em `backend/` e `frontend/` é protótipo provisório, escrito antes das
especificações existirem — ver a nota em [Estado atual](#estado-atual).

| # | Funcionalidade | Capacidade especificada |
|---|---|---|
| RF01 | Cadastro e login de usuário | `autenticacao` |
| RF02 | Onboarding de configuração inicial (nome, receita, pessoas, cartões, categorias) | `configuracao-inicial` |
| RF03 | CRUD de pessoas para rateio de despesas | `cadastros-de-apoio` |
| RF04 | CRUD de cartões/formas de pagamento (com dia de fechamento e deslocamento de fatura) | `cadastros-de-apoio` |
| RF05 | CRUD de categorias de despesa | `cadastros-de-apoio` |
| RF06 | Lançamento de despesa (à vista ou parcelada, dividida entre pessoas) | `lancamento-de-despesas` |
| RF07 | Auto-categorização por regra de palavra-chave na descrição | `auto-categorizacao` |
| RF08 | Painel mensal (dashboard) com totais, receita, sobra/falta e gastos por categoria/cartão | `painel-mensal` |
| RF09 | Previsão de meses futuros calculada dinamicamente a partir de parcelas e contas fixas já lançadas | `previsao-financeira` |
| RF10 | Extrato e cobrança por pessoa (saldo devedor, registro de pagamento) | `cobranca-entre-pessoas` |
| RF11 (bônus) | Exportação/importação de lançamentos via CSV | `importacao-exportacao-csv` |

## Estado atual

Este projeto segue Spec-Driven Development, então a especificação precede o código — e o estado
do repositório reflete essa ordem:

| Camada | Estado |
|---|---|
| Especificação (`openspec/specs/`) | **fechada** — 11 RFs, 29 requisitos, 69 cenários, validados |
| Decisões de arquitetura (`docs/adr/`) | **fechadas** — 3 ADRs + diagramas C4 |
| Harness e guardrail | **ativos** — hook de pre-commit + evidência de bloqueio e de observabilidade |
| Backend (`backend/`) | **conforme ao contrato** — 152 testes, 72/72 cenários cobertos |
| Frontend (`frontend/`) | **reescrito em Vue 3 + Vite**, cobrindo os 11 RFs |

O que vale como contrato é `openspec/specs/`, não o código. O protótipo anterior às
especificações foi trazido à conformidade capacidade por capacidade, com teste derivado do
cenário escrito antes da implementação; a interface foi reescrita em seguida (ADR 0004).

## Arquitetura

O sistema é dividido em duas camadas com um contrato de API REST explícito entre elas — decisão documentada em [`docs/adr/0001-arquitetura-rest-api.md`](docs/adr/0001-arquitetura-rest-api.md):

- **Backend**: expõe uma API REST (autenticação, CRUDs de configuração, lançamentos, cálculo de painel/previsão) e persiste os dados em um banco relacional.
- **Frontend**: aplicação web (SPA) que consome a API via HTTP/JSON.

Os diagramas de contexto e de contêineres (C4 em Mermaid) estão em [`docs/arquitetura.md`](docs/arquitetura.md).

```
┌─────────────┐        HTTP/JSON        ┌──────────────┐        ┌────────────┐
│  Frontend   │ ──────────────────────▶ │   Backend    │ ─────▶ │  Banco de  │
│   (SPA)     │ ◀────────────────────── │  (API REST)  │ ◀───── │   dados    │
└─────────────┘                         └──────────────┘        └────────────┘
```

## Stack tecnológica

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, autenticação JWT (python-jose) e hash de senha com bcrypt (passlib).
- **Frontend**: SPA em **Vue 3** com **Vite**, consumindo a API via `fetch()`. A troca do JavaScript puro sem build para Vue/Vite está justificada na [ADR 0004](docs/adr/0004-frontend-vite-vue.md).
- **Banco de dados**: SQLite.
- **Testes**: pytest — 20 testes unitários cobrindo o módulo de domínio do protótipo (`app/domain/fatura.py`: ciclo de fatura, rateio, parcelamento e auto-categorização), escritos antes dele (TDD). A suíte de API, derivada dos cenários do contrato, ainda não existe — ver [Testes](#testes).
- **Ferramentas de IA / harness**: Claude Code, com processo de Spec-Driven Development documentado em `docs/`.

## Estrutura do repositório

```
.
├── README.md
├── .gitignore
├── openspec/                         # FONTE DA VERDADE das especificações
│   ├── config.yaml
│   ├── specs/                        # contrato acordado, uma pasta por capacidade
│   │   ├── autenticacao/             # RF01
│   │   ├── configuracao-inicial/     # RF02
│   │   ├── cadastros-de-apoio/       # RF03, RF04, RF05
│   │   ├── lancamento-de-despesas/   # RF06
│   │   ├── auto-categorizacao/       # RF07
│   │   ├── painel-mensal/            # RF08
│   │   ├── previsao-financeira/      # RF09
│   │   ├── cobranca-entre-pessoas/   # RF10
│   │   └── importacao-exportacao-csv/# RF11
│   └── changes/                      # mudanças propostas antes de virar código
│       ├── conformidade-rf/          # proposal.md, design.md, specs/ (deltas), tasks.md
│       └── archive/                  # changes já promovidos aos specs
├── githooks/
│   └── pre-commit                    # GUARDRAIL: bloqueia commit com teste falhando (ADR 0002)
├── .claude/                          # integração com o agente, gerada pelo openspec init
│   ├── skills/openspec-*/            # skills de propose, apply, archive, sync, update
│   └── commands/opsx/                # comandos correspondentes
├── docs/
│   ├── especificacao-inicial.md      # Spec inicial (prompt/behavior, harness, nível de autonomia)
│   ├── requisitos-funcionais.md      # Requisitos do 1º ciclo + rastreabilidade RF → capacidade
│   ├── mapeamento_funcionalidades.md # Mapeamento do protótipo original vs. o que foi generalizado
│   ├── plano_inicial.md              # Planejamento e cronograma do projeto
│   ├── arquitetura.md                # Diagramas C4 (contexto e contêineres) em Mermaid
│   ├── adr/
│   │   ├── 0001-arquitetura-rest-api.md
│   │   ├── 0002-guardrail-pre-commit.md
│   │   ├── 0003-adocao-do-openspec.md
│   │   └── 0004-frontend-vite-vue.md
│   └── evidencias/
│       ├── guardrail-bloqueio-commit.png  # bloqueio real do guardrail
│       └── sessao-agente-specs.md         # transcript sanitizado da sessão do agente
├── backend/                          # protótipo provisório — ver Estado atual
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
└── frontend/                         # SPA em Vue 3 + Vite (ADR 0004)
    ├── index.html                    # entrada do Vite
    ├── package.json
    ├── vite.config.js                # proxy dos prefixos da API em desenvolvimento
    └── src/
        ├── main.js
        ├── App.vue                   # casca: telas, navegação, avisos
        ├── api.js                    # cliente HTTP (fetch + JWT em localStorage)
        ├── estado.js                 # estado compartilhado (reactive, sem store)
        ├── formato.js                # moeda e aritmética de meses
        ├── estilo.css
        └── views/
            ├── Autenticacao.vue      # RF01
            ├── Onboarding.vue        # RF02
            ├── Lancar.vue            # RF06, RF07
            ├── Painel.vue            # RF08, RF09
            ├── Cobrar.vue            # RF10
            └── Ajustes.vue           # RF03, RF04, RF05, receita e CSV (RF11)
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

Há dois modos, e os dois funcionam:

**Desenvolvimento** — servidor do Vite com recarga instantânea, fazendo proxy da API para o backend:

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

**Demonstração** — build estático servido pelo próprio backend, em uma única origem e um único processo:

```bash
cd frontend && npm run build     # gera frontend/dist/
cd ../backend && uvicorn app.main:app
# aplicação e API em http://localhost:8000
```

O backend serve `frontend/dist/` quando ele existe, montado **depois** dos routers — assim todo caminho da API é atendido pela API e só o resto cai no SPA. Detalhes na [ADR 0004](docs/adr/0004-frontend-vite-vue.md).

### Rodando os testes

```bash
cd backend
pytest -v
```

## Processo de desenvolvimento (SDD + IA)

Este projeto foi desenvolvido com apoio de agente de IA, seguindo Spec-Driven Development (SDD):

1. **Especificação** — prompt inicial, requisitos e critérios de aceite (Given/When/Then, incluindo casos de borda) em [`docs/especificacao-inicial.md`](docs/especificacao-inicial.md) e [`docs/requisitos-funcionais.md`](docs/requisitos-funcionais.md).
2. **Harness e guardrails** — nível de autonomia adotado (e por que ele fez sentido aqui), guardrail de `pre-commit` e evidência de bloqueio real em [`docs/especificacao-inicial.md`](docs/especificacao-inicial.md#harness-e-controle-de-agente-de-ia) e [`docs/adr/0002-guardrail-pre-commit.md`](docs/adr/0002-guardrail-pre-commit.md).
3. **Observabilidade** — log da sessão do agente transcrito e sanitizado em [`docs/evidencias/sessao-agente-specs.md`](docs/evidencias/sessao-agente-specs.md), incluindo a revisão de diff que precedeu o commit.
4. **Decisões de arquitetura** — registradas como ADRs em [`docs/adr/`](docs/adr/): API REST separada (0001), guardrail de pre-commit (0002), adoção do OpenSpec (0003) e frontend em Vue/Vite (0004).

## Testes

**O que já existe.** O módulo de domínio do protótipo (`backend/app/domain/fatura.py`) concentra
a lógica de negócio pura — ciclo de fechamento de fatura, soma de meses, rateio entre pessoas,
geração de parcelas e motor de regras de auto-categorização — e tem **20 testes unitários** em
`backend/tests/test_fatura_domain.py`, incluindo casos de borda como valor com arredondamento,
número de parcelas inválido e descrição vazia. Esses testes cobrem integralmente as funções
daquele módulo e foram escritos antes dele (TDD): primeiro a suíte falhando, depois o código até
todos passarem.

**O que ainda não existe.** Cobertura do sistema. Não há suíte de testes de API, e portanto os
cenários do contrato que envolvem HTTP, persistência e isolamento entre contas ainda não têm
teste correspondente. Fechar isso é o bloco 1 do plano de tarefas, e a regra adotada é um teste
por cenário de `openspec/specs/`, escrito **antes** da implementação da capacidade.

Ou seja: cobertura unitária completa **do módulo de domínio do protótipo**, não do sistema.

```bash
cd backend && pytest -v
```

## Equipe

- Lucas Medeiros dos Santos — matrícula 20261009725
- Maria Jamilli Lemos de Macedo — matrícula 20261006115

## Licença

Projeto acadêmico desenvolvido para fins avaliativos da disciplina Desenvolvimento de Software com IA (UFRN/IMD).
