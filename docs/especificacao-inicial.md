# Especificação Inicial (SDD) — Fatura em Dia

## Prompt inicial (behavior)

> Construir um sistema web de controle financeiro pessoal que permita a um usuário lançar despesas (à vista ou parceladas), dividi-las com outras pessoas (rateio), acompanhar o ciclo de fechamento de fatura de diferentes cartões, visualizar um painel mensal com totais e previsão de meses futuros, e cobrar/receber pagamentos das pessoas com quem divide as contas. O sistema deve ser utilizável por qualquer usuário desde o primeiro acesso, por meio de um fluxo de configuração inicial (onboarding), sem dados hardcoded de um usuário específico.

## Requisitos

Ver documento separado: [`requisitos-funcionais.md`](requisitos-funcionais.md).

## Critérios de aceite

Ver exemplos detalhados (Given/When/Then, incluindo casos de borda) em [`requisitos-funcionais.md`](requisitos-funcionais.md#critérios-de-aceite-exemplos--givenwhenthen).

## Plano de tarefas

Ver [`requisitos-funcionais.md`](requisitos-funcionais.md#plano-de-tarefas-alto-nível).

## Ferramenta/formato de spec utilizado

- **Ferramenta: OpenSpec** (`@fission-ai/openspec` 1.13.0), com artefatos escritos em português. Decisão e justificativa completas na [ADR 0003](adr/0003-adocao-do-openspec.md).
- **Fonte da verdade das specs:** o diretório [`openspec/`](../openspec/) — `openspec/specs/` descreve o contrato vigente por capacidade, e `openspec/changes/` descreve cada mudança proposta antes de virar código.
- **Histórico:** no primeiro ciclo deste projeto as specs foram escritas em Markdown estruturado à mão, imitando o fluxo do OpenSpec. Esses documentos (este arquivo e [`requisitos-funcionais.md`](requisitos-funcionais.md)) são preservados como registro datado daquele ciclo. A troca para a ferramenta de fato aconteceu no segundo ciclo, pelas razões medidas na ADR 0003 — resumidamente: o custo de adoção que havíamos estimado estava errado, e o formato à mão não tinha validação, o que deixou 8 dos 11 requisitos sem critérios de aceite sem que ninguém percebesse.

## Harness e controle de agente de IA

- **Nível de autonomia**: alto na geração de documentação, specs e código de teste; revisão humana obrigatória antes de qualquer commit na branch principal.
- **Guardrail**: hook de `pre-commit` versionado em `githooks/pre-commit`, que roda a suíte de testes do backend e **bloqueia o commit** quando algum teste falha. Decisão, alternativas e evidência de bloqueio real na [ADR 0002](adr/0002-guardrail-pre-commit.md).
- **Observabilidade**: histórico desta conversa (transcript da sessão do agente) + revisão de diffs antes de cada commit.
