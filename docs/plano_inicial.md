# Plano — Projeto Final: Desenvolvimento de Software com IA
**Prof. Jean Mário Moreira de Lima — UFRN/IMD**
**Apresentação: sábado, 12/09/2026 (hoje é quarta, 09/09 — restam 3 dias)**

---

## 0. Ação imediata (hoje, agora)

### 0.1 Confirmar o checkpoint de 05/09 com a dupla
Mande agora para seu parceiro(a):

> "Oi! Confirma pra mim: você chegou a mandar o email do checkpoint (05/09) pro professor com nomes, matrículas, ideia e requisitos? Se não, precisamos mandar hoje mesmo, mesmo atrasado."

### 0.2 Se NÃO foi enviado, envie hoje — modelo de email

**Para:** jean.lima@imd.ufrn.br
**Assunto:** [Desenvolvimento de Software com IA] Checkpoint da dupla — [Seu Nome] e [Nome da Dupla]

> Prezado Prof. Jean,
>
> Peço desculpas pelo atraso no envio deste checkpoint (previsto para 05/09).
>
> **Dupla:**
> - [Nome completo 1] — matrícula [XXXXX]
> - [Nome completo 2] — matrícula [XXXXX]
>
> **Ideia do projeto:** [uma frase — ex: "TaskFlow Acadêmico, um sistema para gestão de checkpoints e entregas de disciplinas de pós-graduação, com painel colaborativo para duplas/grupos"]
>
> **Requisitos a serem implementados:** [lista resumida dos 10 requisitos — ver seção 2 abaixo]
>
> **Frameworks/tecnologias:** [ex: FastAPI (Python) no back-end, React + Vite no front-end, SQLite, pytest para testes, Claude Code como harness de agente de IA com OpenSpec para SDD]
>
> Seguimos para o desenvolvimento com apresentação confirmada para 12/09.
>
> Atenciosamente,
> [Seu nome]

---

## 1. Escolha da ideia de projeto

Critérios que pesaram na escolha: viável em 3 dias a dois, com 10 requisitos funcionais claros e demonstráveis, arquitetura com contrato explícito front/back, fácil de testar, e que aproveite o **harness já configurado** no repositório `ia-dev-lab` (OpenSpec, skills do Claude Code, testes com pytest) — isso é o maior risco do prazo, então reaproveitar setup é decisivo.

### 🏆 Recomendada: **TaskFlow Acadêmico**
Um painel colaborativo para duplas/grupos gerenciarem checkpoints e entregas de disciplinas — literalmente o problema que vocês estão vivendo agora. Pertinência real e fácil de justificar na apresentação ("construímos isso porque precisávamos disso essa semana").

**Por que essa e não o CPF/CNPJ do ia-dev-lab:** o professor valoriza originalidade ("mais do que a reprodução de exemplos já vistos"); reaproveitar o exercício de validação de CPF/CNPJ como projeto final pode ler como retrabalho de aula. Recomendo reaproveitar apenas o **ambiente/harness** (OpenSpec, skills, hooks) e construir um domínio novo.

**Requisitos funcionais (10):**
1. Cadastro/login de usuário (a dupla).
2. Criar disciplina (nome, professor, data da apresentação/entrega final).
3. Criar checkpoint dentro de uma disciplina (título, descrição, prazo).
4. Marcar status do checkpoint (pendente / em andamento / concluído).
5. Atribuir responsável do checkpoint (qual integrante da dupla).
6. Adicionar comentário/nota a um checkpoint.
7. Listar/filtrar checkpoints por disciplina, status ou prazo.
8. Dashboard com contagem de pendentes, atrasados e concluídos.
9. Alerta visual para checkpoints atrasados (prazo < hoje e não concluído).
10. Exportar relatório (CSV ou PDF) dos checkpoints de uma disciplina.

**Arquitetura:** API REST (FastAPI) + front-end simples (React ou HTML/JS puro com fetch) + SQLite. Contrato de API documentado (OpenAPI/Swagger nativo do FastAPI já serve como "contrato claro").

### Alternativa 2: **Divisor de Contas de Casa Compartilhada**
App para grupos de estudantes dividirem despesas (aluguel, mercado, contas). Requisitos claros (criar grupo, lançar despesa, dividir igualmente/por peso, saldo por pessoa, histórico, quitar dívida, notificação de pendência, exportar extrato, múltiplas moedas opcional, gráfico de gastos por categoria).

### Alternativa 3: **Assistente de Revisão Bibliográfica**
Upload de PDFs de artigos → extração de metadados e resumo automático (usando IA) → organização por tema/tag → busca semântica simples → exportação de bibliografia. Mais chamativo (usa IA na aplicação em si, não só no processo), mas mais arriscado no prazo por causa da integração com modelo de IA para resumo/embeddings.

**Minha recomendação:** vá com **TaskFlow Acadêmico** — é o menor risco de prazo e tem uma boa narrativa (Situação/Tarefa real do método STAR).

> Me diga se topa essa ideia ou se prefere outra — eu ajusto o restante do plano em cima da escolhida.

---

## 2. Aproveitando o repositório `ia-dev-lab`

Vocês já têm, no `ia-dev-lab`:
- OpenSpec configurado (`.claude/skills/openspec-*`, `openspec/config.yaml`) — usem para a spec estruturada exigida (seção IV do edital).
- Comandos `.claude/commands/opsx/*` (propose, explore, update, apply, archive, sync) — esse é o fluxo de SDD pronto.
- Estrutura de testes com pytest já validada (`tests/`).
- ADRs em `docs/adr/` — sigam o mesmo padrão para o novo projeto.
- Relatórios já gerados (`docs/relatorio-final.md`, `docs/relatorio-sdd.md`) — modelo pronto para o "Documento de modelos, estratégias e ferramentas usadas" exigido na entrega.

**Recomendação prática:** criem um **novo branch/feature** (ou até um novo repo, se preferirem separar do trabalho anterior) mas copiem a estrutura de `.claude/`, `openspec/config.yaml` e o padrão de ADR — isso poupa horas de setup de harness.

**Guardrail real (exigido):** vocês precisam de pelo menos um mecanismo que bloqueie de fato algo (não só declarado). Duas opções rápidas:
- **TDD Guard**: bloqueia código de implementação sendo escrito antes do teste correspondente existir.
- **Hook de permissão do Claude Code**: ex. um hook que impede `git push --force` ou edição direta em arquivos de spec sem passar pelo fluxo do OpenSpec.
Escolham UM, testem que ele realmente bloqueia algo, e guardem o log/print disso como evidência.

**Observabilidade (exigido):** salvem o transcript da sessão do agente (esta conversa pode servir de exemplo) e façam prints/registros de revisão de diffs antes de aceitar mudanças (ex: `git diff` revisado antes de commit).

---

## 3. Cronograma (3 dias)

### Quarta 09/09 (hoje) — Fundação
- [ ] Confirmar com a dupla o envio do checkpoint (ou enviar atrasado — seção 0).
- [ ] Confirmar/ajustar a ideia do projeto (seção 1).
- [ ] Criar repositório Git (GitHub/GitLab), convidar o parceiro como colaborador.
- [ ] Estruturar o projeto reaproveitando `.claude/` e `openspec/` do `ia-dev-lab`.
- [ ] Rodar `/opsx:propose` (ou equivalente) para gerar a spec inicial: prompt inicial, requisitos, critérios de aceite (Given/When/Then, incluindo 1 caso de borda), plano de tarefas.
- [ ] Primeiro commit real (estrutura + spec) — não deixem tudo para um commit único no fim.
- [ ] Definir e documentar nível de autonomia do agente de IA (ex: "autonomia alta em código de testes, revisão humana obrigatória antes de merge em main").
- [ ] Configurar o guardrail (hook ou TDD Guard) e testar que ele bloqueia algo de fato.

### Quinta 10/09 — Implementação core
- [ ] Modelagem de dados (schema SQLite) + API REST (endpoints dos 10 requisitos).
- [ ] Testes automatizados cobrindo pelo menos metade dos requisitos (TDD: teste antes do código, se estiverem usando o guardrail).
- [ ] Commits incrementais (várias vezes ao dia, com mensagens claras).
- [ ] Front-end básico consumindo a API (telas principais: dashboard, lista de checkpoints, criar/editar).
- [ ] Escrever o ADR da decisão de arquitetura mais relevante (ex: "por que REST + SQLite em vez de outra stack", ou "por que separar front/back").
- [ ] Gerar o diagrama de arquitetura (Mermaid/C4) — pode pedir para o agente de IA gerar e revisar.

### Sexta 11/09 — Fechamento e polimento
- [ ] Terminar os requisitos restantes.
- [ ] Completar cobertura de testes.
- [ ] Revisar todos os diffs pendentes, dar merge final, garantir histórico de commits limpo e real (não squash artificial).
- [ ] Montar a apresentação (PPT) cobrindo os 7 pontos da seção V do edital.
- [ ] Escrever o "Documento de modelos, estratégias e ferramentas usadas" (lista objetiva).
- [ ] Escrever e publicar o post no LinkedIn (método STAR — modelo na seção 4 abaixo), com print/GIF/link da demo.
- [ ] Montar o documento final de entrega: nomes, link do repositório, link do post no LinkedIn.
- [ ] Ensaiar a demo ao vivo (rodar o sistema do zero para garantir que funciona sem surpresas).

### Sábado 12/09 — Apresentação
- [ ] Checar ambiente de demo com antecedência (internet, banco de dados populado, etc.).
- [ ] Apresentar cobrindo: contexto/motivação → processo SDD → harness/guardrails/observabilidade → arquitetura (ADR + diagrama) → ferramentas de IA usadas → demo ao vivo → aprendizados/dificuldades.

---

## 4. Modelo do post no LinkedIn (método STAR)

> **Situação:** [problema real — ex: "Como estudantes de pós-graduação, perdíamos o controle de prazos e checkpoints de múltiplas disciplinas espalhados em emails e planilhas."]
>
> **Tarefa:** [o que se propuseram a construir e por quê — ex: "Construímos o TaskFlow Acadêmico, um painel colaborativo para gerenciar checkpoints de disciplinas em dupla, como projeto final da disciplina Desenvolvimento de Software com IA."]
>
> **Ação:** [processo — SDD com OpenSpec, especificação com critérios de aceite, harness com [ferramenta] e guardrail [X], arquitetura [Y]. Justifique as escolhas.]
>
> **Resultado:** [o que foi entregue, impacto/aprendizado sobre desenvolvimento assistido por IA de forma sistemática, próximos passos se fizer sentido.]
>
> [Incluir print/GIF/link da demo]
>
> #DesenvolvimentoDeSoftware #IA #UFRN #IMD

---

## 5. Checklist final de entregáveis (antes de 12/09)

- [ ] Repositório com histórico de commits real (acesso ao professor se privado).
- [ ] Apresentação (PPT) cobrindo os 7 pontos da seção V.
- [ ] Documento de modelos/ferramentas/estratégias de IA usadas.
- [ ] Post no LinkedIn (STAR) publicado, com link.
- [ ] Documento final com nomes + link do repositório + link do post no LinkedIn, enviado antes da apresentação.
- [ ] Pelo menos 1 spec real (SDD), 1 ADR, 1 diagrama de arquitetura, 1 guardrail funcional com evidência, log/transcript de sessão de agente.
