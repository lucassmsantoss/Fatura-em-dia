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
- **Fonte da verdade das specs:** o diretório [`openspec/`](../openspec/) — `openspec/specs/` descreve o contrato acordado por capacidade, e `openspec/changes/` descreve cada mudança proposta antes de virar código.
- **Histórico:** no primeiro ciclo deste projeto as specs foram escritas em Markdown estruturado à mão, imitando o fluxo do OpenSpec. Esses documentos (este arquivo e [`requisitos-funcionais.md`](requisitos-funcionais.md)) são preservados como registro datado daquele ciclo. A troca para a ferramenta de fato aconteceu no segundo ciclo, pelas razões medidas na ADR 0003 — resumidamente: o custo de adoção que havíamos estimado estava errado, e o formato à mão não tinha validação, o que deixou 8 dos 11 requisitos sem critérios de aceite sem que ninguém percebesse.

## Harness e controle de agente de IA

### Nível de autonomia

**Autonomia alta em leitura, pesquisa e redação de artefatos; gate humano obrigatório antes de
qualquer efeito externo** — commit, push, abertura de PR e instalação global de ferramenta.

*Por que este nível fez sentido para este projeto:* o trabalho tem duas naturezas de risco
muito diferentes. Ler o edital, varrer o repositório, comparar requisito com contrato e redigir
spec são atividades **reversíveis** — se o agente errar, o custo é descartar um arquivo que
ainda não saiu da máquina, e exigir aprovação a cada passo desses só consumiria o prazo de três
dias. Já commit, push, abertura de PR e instalação global de dependência são **irreversíveis ou
visíveis para terceiros**, e um erro ali contamina justamente o histórico que o edital manda
ser real. A fronteira da autonomia foi desenhada nessa linha, e não por conveniência.

A escolha se sustentou em operação: as duas intervenções humanas registradas na sessão de
especificação caíram exatamente na fronteira — uma redirecionou a estratégia (especificar antes
de programar) e a outra corrigiu qual identidade Git faria o push. Registro em
[`evidencias/sessao-agente-specs.md`](evidencias/sessao-agente-specs.md).

### Guardrail

Hook de `pre-commit` versionado em `githooks/pre-commit` e ativado por
`git config core.hooksPath githooks`. Ele roda a suíte de testes do backend e **bloqueia o
commit** quando algum teste falha. Decisão, alternativas consideradas e evidência de bloqueio
real na [ADR 0002](adr/0002-guardrail-pre-commit.md), com o print do commit recusado em
[`evidencias/guardrail-bloqueio-commit.png`](evidencias/guardrail-bloqueio-commit.png).

### Observabilidade

O harness grava um log JSONL por projeto, isolado por diretório de trabalho. O registro da
sessão em que as especificações foram construídas está transcrito, sanitizado e comentado em
[`evidencias/sessao-agente-specs.md`](evidencias/sessao-agente-specs.md): 13 turnos humanos,
166 turnos do agente e 76 chamadas de ferramenta em 12 fases — incluindo a revisão de diff que
precedeu o commit e o loop de correção da validação estrita.

Não usamos observabilidade de *runtime* (Sentry, Datadog e similares). O que o edital pede
neste item é observabilidade **do processo de desenvolvimento assistido por IA** — "log/transcript
de sessão do agente e revisão de diffs antes de aceitar mudanças" — e não monitoramento da
aplicação em produção. Registramos a distinção aqui porque ela foi objeto de divergência
explícita entre a dupla e o agente durante a sessão, resolvida relendo o texto do edital em vez
de por autoridade do agente.
