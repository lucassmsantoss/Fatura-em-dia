# Fatura em Dia

Aplicativo web de controle financeiro pessoal com rateio de despesas entre pessoas (família, casal, colegas de casa), parcelamento de compras e acompanhamento de faturas de cartão por ciclo de fechamento.

Projeto final da disciplina **Desenvolvimento de Software com IA** — UFRN/IMD (Prof. Jean Mário Moreira de Lima).

## Origem do projeto

O sistema nasceu de um protótipo pessoal ("Caderneta") criado por um dos integrantes para controlar suas próprias finanças e dividir contas com a família. Para este projeto, o protótipo foi generalizado: removemos todos os dados pessoais e regras hardcoded, e adicionamos um fluxo de configuração inicial (onboarding) para que qualquer usuário possa configurar seu próprio conjunto de pessoas, cartões e categorias.

## Requisitos funcionais

Ver [`docs/requisitos-funcionais.md`](docs/requisitos-funcionais.md).

## Arquitetura

- **Backend**: API REST (a definir: FastAPI/Node — ver ADR 0001).
- **Frontend**: SPA consumindo a API via HTTP.
- **Banco de dados**: SQLite (simplicidade adequada ao prazo do projeto).

Detalhes em [`docs/adr/0001-arquitetura-rest-api.md`](docs/adr/0001-arquitetura-rest-api.md).

## Processo de desenvolvimento (SDD + IA)

Este projeto foi desenvolvido com apoio de agente de IA seguindo Spec-Driven Development.
Ver [`docs/especificacao-inicial.md`](docs/especificacao-inicial.md) para a especificação inicial (prompt, requisitos, critérios de aceite e plano de tarefas).

## Equipe

- [Nome completo 1] — matrícula [XXXXX]
- [Nome completo 2] — matrícula [XXXXX]
