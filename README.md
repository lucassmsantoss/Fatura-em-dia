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

> Em definição durante a implementação — este README será atualizado conforme as escolhas forem confirmadas e justificadas na apresentação.

- **Backend**: a definir (candidato: FastAPI + Python)
- **Frontend**: a definir (candidato: React ou HTML/JS)
- **Banco de dados**: SQLite
- **Testes**: pytest (backend)
- **Ferramentas de IA / harness**: Claude Code, com processo de Spec-Driven Development documentado em `docs/`

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
├── backend/     # (a ser criado)
└── frontend/    # (a ser criado)
```

## Como rodar o projeto

> Instruções serão adicionadas assim que o backend e o frontend forem implementados.

## Processo de desenvolvimento (SDD + IA)

Este projeto foi desenvolvido com apoio de agente de IA, seguindo Spec-Driven Development (SDD):

1. **Especificação** — prompt inicial, requisitos e critérios de aceite (Given/When/Then, incluindo casos de borda) em [`docs/especificacao-inicial.md`](docs/especificacao-inicial.md) e [`docs/requisitos-funcionais.md`](docs/requisitos-funcionais.md).
2. **Harness e guardrails** — nível de autonomia do agente, mecanismo de guardrail configurado e evidência de funcionamento serão documentados aqui conforme aplicados durante a implementação.
3. **Observabilidade** — histórico de sessões do agente e revisão de diffs antes de cada commit.
4. **Decisões de arquitetura** — registradas como ADRs em [`docs/adr/`](docs/adr/).

## Testes

> Estratégia de testes automatizados (cobrindo cálculo de fatura, rateio, parcelamento e previsão) será detalhada conforme o backend for implementado.

## Equipe

- Lucas Medeiros

## Licença

Projeto acadêmico desenvolvido para fins avaliativos da disciplina Desenvolvimento de Software com IA (UFRN/IMD).
