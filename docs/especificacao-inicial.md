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

- Formato: documentos Markdown estruturados (`especificacao-inicial.md`, `requisitos-funcionais.md`, ADRs), organizados de forma equivalente ao fluxo do OpenSpec (proposta → design → tarefas → revisão), já usado por esta dupla em atividade anterior da disciplina.
- Justificativa da escolha: dado o prazo curto do projeto final, optamos por um formato de spec estruturado em Markdown simples em vez de reconfigurar o tooling completo do OpenSpec, mantendo porém a mesma disciplina de processo (prompt → requisitos → critérios de aceite → plano de tarefas → revisão humana antes de implementar).

## Harness e controle de agente de IA

- **Nível de autonomia**: alto na geração de documentação, specs e código de teste; revisão humana obrigatória antes de qualquer commit na branch principal.
- **Guardrail**: [a definir/registrar durante a implementação — ex.: hook de bloqueio de commit direto em `main`, ou TDD Guard exigindo teste antes da implementação].
- **Observabilidade**: histórico desta conversa (transcript da sessão do agente) + revisão de diffs antes de cada commit.
