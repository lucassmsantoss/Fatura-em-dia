# Evidência de observabilidade — sessão do agente de especificação

> Evidência referente ao item **IV. Harness e controle de agentes** do edital:
>
> **“Evidência de observabilidade do processo: log/transcript de sessão do agente e revisão de diffs antes de aceitar mudanças.”**

---

## 1. Objetivo desta evidência

Este documento registra como o agente de IA foi utilizado durante uma etapa real do desenvolvimento do **Fatura em Dia**, com foco na estruturação do processo de Spec-Driven Development (SDD), adoção do OpenSpec, formalização das especificações e preparação das mudanças para revisão.

O objetivo não é apenas apresentar os artefatos produzidos pelo agente, mas permitir observar **como o agente chegou até eles**:

- quais direcionamentos foram dados pelo humano;
- quais decisões foram tomadas durante a sessão;
- quais ferramentas o agente utilizou;
- onde houve intervenção humana;
- quais erros ocorreram;
- como esses erros foram corrigidos;
- como o guardrail atuou;
- e como as alterações foram revisadas antes de serem aceitas no histórico Git.

Para facilitar a leitura, uma sessão física longa do Claude Code foi dividida neste documento em **quatro momentos lógicos do processo**:

1. entendimento do produto e definição da abordagem;
2. estruturação do SDD e escolha da ferramenta;
3. criação e validação das especificações;
4. harness, revisão de diff e entrega.

Os quatro momentos pertencem ao mesmo transcript físico e são apresentados separadamente apenas para evidenciar a evolução da interação humano-agente.

---

## 2. Procedência do registro

O registro foi derivado do transcript real gravado automaticamente pelo **Claude Code** durante a execução do projeto.

O Claude Code mantém os transcripts locais associados ao diretório de cada projeto em:

```text
~/.claude/projects/<slug>/
```

O `slug` é derivado do diretório de trabalho utilizado pelo agente. Dessa forma, a sessão deste projeto fica separada dos transcripts de outros projetos utilizados na mesma máquina.

| Informação | Valor |
|---|---|
| Projeto | Fatura em Dia |
| Sessão física | `c8579109` (identificador truncado) |
| Data | 10/09/2026 |
| Período | 03:46 → 05:53 |
| Duração aproximada | 2h07 |
| Turnos humanos | 13 |
| Turnos do agente | 166 |
| Chamadas de ferramenta | 76 |
| Bash | 72 |
| Read | 2 |
| Skill | 1 |
| Pergunta explícita ao humano | 1 |
| Resultado principal | `openspec/`, ADR 0003, branch, commit e PR #2 |

### Sanitização

Antes de publicar esta evidência:

- caminhos absolutos foram reduzidos para `~`;
- diretórios temporários e de sandbox foram omitidos;
- informações de autenticação foram omitidas;
- identificadores não necessários foram truncados;
- mensagens automáticas de carregamento do harness não foram consideradas turnos humanos;
- conteúdo de outros projetos não foi incluído.

A íntegra permanece representada pelo arquivo JSONL original. Este documento apresenta os trechos relevantes e um resumo estruturado das ações para tornar a evidência legível.

---

## 3. O produto: Fatura em Dia

Antes de iniciar a formalização das specs, o agente precisou compreender qual produto estava sendo construído.

O **Fatura em Dia** é uma aplicação web de controle financeiro pessoal voltada principalmente para situações em que uma mesma despesa pode envolver simultaneamente:

- compras parceladas;
- diferentes cartões ou formas de pagamento;
- ciclos de fechamento de fatura;
- divisão da despesa entre diferentes pessoas;
- previsão de compromissos financeiros futuros.

O problema observado é que esse tipo de controle tende a se tornar difícil em planilhas ou anotações manuais.

Não basta registrar que uma compra ocorreu.

O sistema precisa conseguir representar, por exemplo:

> uma compra parcelada em vários meses, realizada em determinado cartão, cujo valor é dividido entre duas ou mais pessoas e cujas parcelas precisam aparecer no ciclo correto de cada fatura.

O projeto surgiu a partir de um protótipo pessoal anterior denominado **Caderneta**.

Para o trabalho da disciplina, o objetivo passou a ser transformar essa solução específica em um produto generalizado, no qual diferentes usuários possam configurar seus próprios dados financeiros.

Entre as funcionalidades previstas no produto estão:

- cadastro e autenticação;
- onboarding financeiro;
- pessoas utilizadas no rateio;
- cartões e formas de pagamento;
- categorias;
- lançamento de despesas;
- parcelamento;
- rateio;
- auto-categorização;
- painel mensal;
- previsão financeira;
- cobrança entre pessoas;
- importação e exportação de dados.

A partir desse entendimento, o trabalho passou a seguir a seguinte direção:

```text
problema
    ↓
comportamentos esperados
    ↓
specifications
    ↓
critérios de aceite
    ↓
design
    ↓
tasks
    ↓
implementação
```

A intenção foi evitar continuar utilizando o código existente como única fonte para descobrir o comportamento esperado do sistema.

---

## 4. Nível de autonomia adotado

O nível de autonomia adotado durante a sessão foi:

> **Alta autonomia para leitura, investigação, análise, execução de validações e elaboração de artefatos; intervenção humana nos pontos de decisão e antes de efeitos externos relevantes.**

Esse nível foi considerado adequado porque grande parte da atividade consistia em:

- explorar documentação;
- analisar código existente;
- comparar implementação e requisitos;
- estudar o funcionamento de uma ferramenta;
- elaborar specifications;
- executar validadores;
- executar testes;
- analisar diffs.

Essas atividades são relativamente reversíveis.

Por outro lado, ações como:

- escolha definitiva de abordagem;
- mudança de identidade Git;
- push para o repositório;
- criação de Pull Request;

foram tratadas como pontos em que o controle humano precisava permanecer explícito.

A sessão contém exemplos dos dois comportamentos:

```text
Agente
  ├── lê autonomamente
  ├── pesquisa autonomamente
  ├── valida autonomamente
  ├── propõe autonomamente
  │
  ├── humano pode interromper
  ├── agente pode solicitar decisão
  │
  └── efeitos externos passam por gate humano
```

---

## 5. Transcript da sessão — visão geral

A sessão não foi uma sequência linear de comandos para geração de código.

Ela passou por quatro momentos claramente identificáveis:

| Momento | Objetivo |
|---|---|
| 1 | Entender o Fatura em Dia e decidir como abordar o SDD |
| 2 | Escolher e aprender uma ferramenta formal de especificação |
| 3 | Transformar requisitos existentes em uma baseline OpenSpec |
| 4 | Preparar harness, revisar mudanças e realizar a entrega |

Os recortes abaixo foram retirados do fluxo da sessão e mantêm os direcionamentos humanos relevantes.

As descrições das ações do agente correspondem às operações registradas no transcript e às chamadas de ferramenta associadas.

---

## 6. Momento 1 — entendimento do produto antes de continuar o desenvolvimento

### Objetivo

O primeiro momento da sessão consistiu em descobrir:

> **O que já existe no Fatura em Dia e como transformar esse material em um processo realmente orientado por especificação?**

O repositório já possuía:

- documentação;
- requisitos funcionais;
- decisões de arquitetura;
- backend;
- frontend;
- testes;
- implementação parcial.

A intenção, porém, não era simplesmente continuar implementando a partir desse ponto.

Era necessário primeiro verificar se o que existia poderia formar uma baseline de produto.

### Transcript — início do trabalho

#### Humano

> Usar o PDF do edital como fonte do que deve ser feito e correlacionar com o que Lucas já havia feito.

#### Agente — ações registradas

O agente iniciou pela leitura do edital e depois passou a investigar o repositório.

Foram consultados:

```text
README.md
docs/especificacao-inicial.md
docs/requisitos-funcionais.md
docs/arquitetura.md
docs/plano_inicial.md
docs/mapeamento_funcionalidades.md
docs/adr/
backend/
frontend/
testes
histórico Git
configurações do projeto
```

O comportamento observado nesse primeiro momento foi de **intake e diagnóstico**, e não de implementação imediata.

### Verificação do estado real

Depois da documentação, o agente inspecionou também o estado efetivo da aplicação.

Entre as ações registradas:

```text
- execução da suíte de testes;
- inspeção da implementação do backend;
- inspeção da implementação do frontend;
- verificação de contratos;
- rastreamento de comportamentos descritos nos requisitos;
- inspeção do histórico Git;
- comparação entre documentação e código existente.
```

Um exemplo foi a investigação do tipo `"compromisso"`.

O agente procurou onde esse tipo estava sendo atribuído e constatou que o comportamento descrito não estava efetivamente implementado daquela forma.

Isso foi importante porque evitou assumir que:

```text
documentação existente == comportamento real
```

A documentação passou a ser tratada como fonte de descoberta que precisava ser validada contra o estado real do projeto.

---

## 7. Momento 2 — intervenção humana e mudança para Spec-Driven Development

Durante a investigação inicial, o humano interrompeu o fluxo para redefinir a prioridade.

#### Humano

> “os specs tem que ser feitos antes do desenvolvimento né? então acho que temos que atacar logo essa parte toda de spec”

Esse turno mudou explicitamente o foco da sessão.

A prioridade deixou de ser:

```text
entender o que falta
        ↓
continuar implementando
```

e passou a ser:

```text
entender o produto
        ↓
formalizar comportamento
        ↓
estabelecer baseline
        ↓
somente depois continuar implementação
```

### Primeira tentativa

O agente inicialmente criou:

```text
docs/specs/
```

e começou a estruturar manualmente uma especificação de mudança.

Essa solução foi interrompida antes de ser adotada.

#### Humano — interrupção

```text
[Request interrupted by user]
```

Em seguida:

#### Humano

> “Calma, quero algo bem feito”

O humano questionou se simplesmente criar arquivos Markdown manualmente representaria de fato o processo de SDD desejado e se deveria ser utilizada uma ferramenta específica para gerenciar as specifications.

Esse é um dos pontos em que o transcript demonstra diretamente o **controle humano sobre a autonomia do agente**.

O agente havia iniciado um caminho possível.

O humano interrompeu.

A direção foi alterada.

A primeira solução foi descartada.

---

## 8. Momento 2.1 — escolha de uma ferramenta de SDD

A partir da intervenção, a pergunta passou a ser:

> **Qual ferramenta deve estruturar o processo de especificação do Fatura em Dia?**

O agente recebeu autonomia para investigar antes de alterar o projeto.

### Investigação

As ações registradas incluíram:

```text
- verificar disponibilidade de Node/npm;
- procurar utilização anterior de OpenSpec;
- consultar o registry npm;
- investigar a CLI;
- identificar o pacote correto;
- instalar a ferramenta primeiro em ambiente isolado.
```

Durante a investigação ocorreu um problema real.

O pacote:

```text
openspec
```

não correspondia à ferramenta pretendida.

A inspeção mostrou um pacote:

```text
versão: 0.0.0
executável: inexistente
```

O agente então identificou o pacote correto:

```text
@fission-ai/openspec
```

Essa descoberta foi posteriormente registrada na **ADR 0003**, para que a decisão pudesse ser reproduzida.

---

## 9. Momento 2.2 — aprender a ferramenta antes de alterar o projeto

Antes de inicializar o OpenSpec dentro do Fatura em Dia, o agente criou um ambiente descartável.

A intenção foi reduzir o risco de modificar a estrutura do projeto sem compreender previamente a ferramenta.

As ações registradas incluíram:

```bash
openspec init
```

executado em sandbox.

Depois disso, o agente inspecionou:

```text
config.yaml

templates

estrutura de specs

estrutura de changes

proposal

design

tasks

spec deltas
```

Também foi criado um change descartável apenas para compreender o fluxo.

O agente verificou ainda o comportamento do modo:

```text
--strict
```

e testou empiricamente como os cenários deveriam ser estruturados.

### Resultado

Somente depois dessa investigação a ferramenta foi adotada no projeto real:

```bash
npm install -g @fission-ai/openspec@1.13.0
```

A versão foi fixada para reduzir variações no ambiente.

Depois:

```bash
openspec init
```

foi executado dentro do Fatura em Dia.

A tentativa manual anterior em `docs/specs/` foi descartada.

---

## 10. Momento 3 — construção da baseline do Fatura em Dia

Com a ferramenta definida, começou a formalização das specifications permanentes do produto.

A baseline foi organizada em capabilities.

Atualmente, o diretório contém:

```text
openspec/specs/
├── autenticacao/
├── auto-categorizacao/
├── cadastros-de-apoio/
├── cobranca-entre-pessoas/
├── configuracao-inicial/
├── lancamento-de-despesas/
├── painel-mensal/
└── previsao-financeira/
```

Essa organização permite representar o comportamento do produto por domínio, em vez de manter uma lista monolítica de requisitos.

### Relação com os requisitos anteriores

Os requisitos funcionais existentes não foram simplesmente apagados.

Eles foram utilizados como material para derivação e rastreabilidade das novas capabilities.

Exemplo conceitual:

```text
RF01
  ↓
autenticacao

RF02
  ↓
configuracao-inicial

RF03 + RF04 + RF05
  ↓
cadastros-de-apoio

RF06
  ↓
lancamento-de-despesas

RF07
  ↓
auto-categorizacao

RF08
  ↓
painel-mensal

RF09
  ↓
previsao-financeira

RF10
  ↓
cobranca-entre-pessoas
```

Dessa forma, o documento anterior continua servindo como registro histórico, enquanto o OpenSpec passa a representar a fonte estruturada do comportamento esperado.

---

## 11. Transcript — criação das specs

Durante a autoria, o agente precisou distinguir dois tipos de artefato.

### Baseline

Representa:

> O que o produto promete fazer atualmente?

Estrutura:

```text
openspec/specs/
```

### Change

Representa:

> O que queremos alterar na baseline?

Estrutura:

```text
openspec/changes/<change>/
```

Essa distinção se tornou importante durante a própria sessão.

O agente verificou que uma specification permanente deveria utilizar:

```md
## Requirements
```

e não:

```md
## ADDED Requirements
```

O segundo formato pertence aos **spec deltas** de um change.

### Escrita da baseline

As oito capability specs foram produzidas em etapas e posteriormente submetidas ao validator.

Foi executado:

```bash
openspec validate --strict
```

A validação strict passou a funcionar como uma barreira objetiva entre:

```text
texto produzido pelo agente
```

e:

```text
spec estruturalmente aceita pelo projeto
```

Não era suficiente que a resposta do modelo parecesse correta.

O artefato também precisava obedecer ao formato verificável escolhido pela dupla.

---

## 12. Momento 3.1 — primeira mudança modelada como change

Depois da baseline, o agente estruturou uma mudança seguindo o workflow do OpenSpec.

Foram produzidos:

```text
proposal

spec deltas

design

tasks
```

O change relacionava a alteração proposta às capabilities afetadas.

### Erro real detectado pelo validator

Durante esse processo ocorreu uma falha de validação.

Um bloco:

```text
MODIFIED
```

foi rejeitado pelo OpenSpec.

O fluxo observado foi:

```text
agente produz spec
       ↓
openspec validate --strict
       ↓
erro
       ↓
agente inspeciona o problema
       ↓
corrige o delta
       ↓
executa novamente a validação
       ↓
validação passa
```

Esse evento é relevante como evidência de harness porque demonstra que a saída do agente não era automaticamente considerada correta.

Existia um mecanismo externo capaz de rejeitar um artefato produzido pelo modelo.

---

## 13. Momento 3.2 — documentação da decisão

Depois de validar o processo, o agente documentou a escolha realizada.

Entre os artefatos produzidos ou atualizados estavam:

```text
docs/adr/0003-adocao-do-openspec.md

docs/especificacao-inicial.md

docs/requisitos-funcionais.md

openspec/
```

A ADR registra:

- por que uma ferramenta estruturada foi adotada;
- por que o OpenSpec foi escolhido;
- como ele se encaixa no projeto;
- como baseline e changes são utilizados;
- e detalhes encontrados durante a investigação da ferramenta.

Também foi criado o mapeamento entre requisitos históricos e capabilities.

---

## 14. Momento 4 — harness e controle do agente

Depois da formalização do SDD, o foco da conversa mudou novamente.

#### Humano

> “pronto, criei o pr. agora qual seria o passo seguinte? pensando no que ja temos”

Posteriormente:

#### Humano

> “o que precisamos pra deixar o harness ok? porque tipo o sistema funcional só vem depois se é SDD”

Esse turno demonstra que SDD e Harness foram tratados como etapas explícitas do processo e não simplesmente mencionados depois que o sistema já estava pronto.

---

## 15. Evidências de controle humano

A sessão contém três comportamentos importantes relacionados à autonomia.

### 15.1 Interrupções

Foram registradas duas ocorrências de:

```text
[Request interrupted by user]
```

A primeira ocorreu durante a definição da estratégia de specification.

A segunda ocorreu durante a preparação da integração Git.

Em ambos os casos, o agente estava executando uma sequência de trabalho e foi interrompido pelo humano antes de prosseguir.

### 15.2 Pergunta explícita ao humano

O transcript também registra uma utilização da ferramenta de pergunta ao usuário.

Nesse momento o agente não inferiu sozinho a decisão.

O fluxo foi:

```text
agente identifica decisão
        ↓
interrompe execução
        ↓
pergunta ao humano
        ↓
recebe orientação
        ↓
continua
```

### 15.3 Correção da identidade Git

Durante a preparação da entrega, foi detectado que a identidade inicialmente considerada pelo agente não era a identidade adequada para escrever no repositório.

#### Humano — interrupção

```text
[Request interrupted by user]
```

#### Humano

> Correção de identidade: não usar a conta que não tem acesso ao repositório.

Depois:

#### Humano

> Usar a conta pessoal, que é colaboradora do repositório.

A partir dessa intervenção, o agente:

```text
- verificou as contas disponíveis;
- verificou identidade SSH;
- associou a chave à conta adequada;
- ajustou o remote;
- testou a autenticação;
- somente então prosseguiu.
```

Esse é um exemplo concreto de um efeito externo que não foi simplesmente deixado sob decisão irrestrita do agente.

---

## 16. Guardrail configurado

O projeto utiliza um mecanismo de guardrail baseado em Git Hook.

Durante a sessão foi verificada a configuração do repositório e ativado:

```bash
git config core.hooksPath githooks
```

A partir disso, operações de commit passaram a ser submetidas ao hook do projeto.

O guardrail não foi apenas documentado.

Foi realizado um teste no qual uma operação incompatível com a regra configurada foi efetivamente bloqueada.

A evidência visual está disponível em:

```text
guardrail-bloqueio-commit.png
```

Isso atende à necessidade de demonstrar um:

> **bloqueio real, não apenas descrito.**

---

## 17. Revisão de diff antes de aceitar mudanças

Além do transcript, o edital solicita explicitamente evidência de:

> **revisão de diffs antes de aceitar mudanças.**

Esse comportamento também aparece na sessão.

As alterações foram primeiro acumuladas no working tree.

Antes do commit, o agente verificou o estado da mudança e inspecionou o diff.

A sequência observada foi equivalente a:

```bash
git status
git diff --stat
git diff
```

A intenção dessa etapa era verificar:

- quais arquivos estavam sendo adicionados;
- quais arquivos estavam sendo modificados;
- se havia arquivos fora do escopo;
- se as alterações correspondiam à tarefa solicitada;
- se não havia conteúdo acidental no commit;
- e se os artefatos de SDD estavam coerentes entre si.

Somente depois dessa inspeção o fluxo avançou para o commit.

A ordem observada foi:

```text
alterações
    ↓
validações
    ↓
git status
    ↓
git diff
    ↓
revisão
    ↓
commit
    ↓
push
    ↓
Pull Request
```

Isso mantém uma fronteira entre:

```text
mudança produzida pelo agente
```

e:

```text
mudança aceita no histórico do projeto
```

---

## 18. Transcript — entrega da mudança

Depois da preparação dos artefatos, o humano solicitou:

#### Humano

> “quero que você crie o PR dessa parte e deixe lá”

Antes da entrega, foram registradas ações de verificação sobre:

```text
gh auth

git config

git remote

hooks

identidade Git

identidade SSH

permissão no repositório
```

Depois da correção da identidade pelo humano, o agente prosseguiu com:

```text
criação da branch

revisão das mudanças

commit

push

criação do Pull Request

verificação do Pull Request
```

A alteração, portanto, não foi integrada diretamente à branch principal.

Ela foi disponibilizada por Pull Request, mantendo mais um ponto explícito de inspeção antes da integração definitiva.

---

## 19. Log operacional — sequência observada

Além dos recortes conversacionais, o transcript contém o registro das ações executadas pelo agente.

Abaixo, as ações foram agrupadas por fase para facilitar a inspeção.

### Fase 1 — Intake do edital

Foram registradas aproximadamente 8 ações relacionadas ao intake.

```text
- localizar o PDF da especificação;
- tentar mecanismos locais de extração;
- constatar ausência das ferramentas inicialmente previstas;
- criar ambiente virtual isolado;
- instalar biblioteca para leitura;
- extrair conteúdo;
- exibir o texto;
- correlacionar os requisitos do edital com o projeto.
```

### Fase 2 — Leitura do repositório

Foram registradas aproximadamente 12 ações.

O agente inspecionou:

```text
README

especificacao-inicial.md

requisitos-funcionais.md

ADRs

arquitetura.md

plano_inicial.md

mapeamento_funcionalidades.md

backend

frontend

testes

histórico Git

configuração do projeto
```

Também foram verificados:

```text
requirements

main

database

auth

schemas

routers

hook

.gitignore

evidências
```

### Fase 3 — Verificação do estado real

Foram registradas aproximadamente 5 ações.

```text
- executar a suíte de testes;
- rastrear o comportamento de "compromisso";
- verificar discrepância entre documentação e implementação;
- tentar executar a aplicação;
- conferir a ordem cronológica do histórico Git.
```

### Fase 4 — Primeira tentativa descartada

Foram registradas 2 ações principais.

```text
- criar docs/specs/;
- iniciar uma specification manual.
```

Essa abordagem foi interrompida pelo humano e posteriormente removida.

### Fase 5 — Escolha da ferramenta

Foram registradas aproximadamente 7 ações.

```text
- verificar Node/npm;
- procurar uso anterior do OpenSpec;
- consultar pacote openspec;
- identificar que o pacote encontrado não era a CLI pretendida;
- pesquisar o pacote correto;
- identificar @fission-ai/openspec;
- verificar versão e comandos.
```

### Fase 6 — Aprendizado da gramática

Foram registradas aproximadamente 8 ações.

```text
- openspec init em sandbox;
- inspeção da estrutura;
- leitura do config.yaml;
- leitura dos templates;
- leitura das regras de autoria;
- criação de um change descartável;
- consulta às instruções de spec delta;
- teste de validação strict.
```

### Fase 7 — Adoção real

Principais ações:

```bash
npm install -g @fission-ai/openspec@1.13.0

openspec init
```

A tentativa manual anterior foi descartada.

### Fase 8 — Escrita das specs

O agente:

```text
- confirmou o formato da baseline;
- escreveu as primeiras capabilities;
- escreveu as capabilities restantes;
- listou as specifications;
- executou validação strict.
```

A baseline ficou organizada nas oito capabilities:

```text
autenticacao

auto-categorizacao

cadastros-de-apoio

cobranca-entre-pessoas

configuracao-inicial

lancamento-de-despesas

painel-mensal

previsao-financeira
```

### Fase 9 — Change proposto

Foram produzidos:

```text
proposal

spec deltas

design

tasks
```

Durante a validação:

```text
MODIFIED inválido
        ↓
falha
        ↓
correção
        ↓
nova validação
        ↓
sucesso
```

Depois foram verificados:

```text
status

listagem

relações entre artefatos
```

### Fase 10 — Documentação da decisão

Foram realizadas ações relacionadas a:

```text
ADR 0003

especificacao-inicial.md

requisitos-funcionais.md

rastreabilidade RF → capability
```

Depois foram executadas novamente:

```text
validação das specs

validação do change

suíte de testes
```

### Fase 11 — Entrega e revisão de diff

Essa fase é particularmente importante para o requisito de observabilidade.

O agente:

```text
- verificou autenticação gh;
- verificou identidade Git;
- verificou remote;
- verificou hooks;
- verificou permissão de escrita;
- conferiu contas;
- conferiu identidade SSH;
- ativou core.hooksPath;
- criou a branch;
- preparou as alterações;
- revisou o diff;
- realizou o commit;
- testou a identidade correta;
- realizou o push;
- criou o Pull Request;
- verificou sua criação.
```

O diff foi revisado **antes do commit**.

### Fase 12 — Observabilidade

No encerramento da sessão, o próprio processo de observabilidade foi discutido.

Foram executadas ações para:

```text
- localizar os transcripts do Claude Code;
- identificar o JSONL associado ao projeto;
- avaliar conteúdo sensível antes de publicação;
- localizar o requisito exato de observabilidade no edital.
```

---

## 20. Discussão sobre o significado de observabilidade

A interpretação do termo **observabilidade** gerou uma divergência explícita entre humano e agente.

#### Humano

> “só a observabilidade que não concordo, quando penso nisso penso em métricas, pegar erros como no sentry datadog etc, não?”

Em vez de manter sua interpretação original, o agente voltou ao edital para verificar o requisito exato.

O texto encontrado fazia referência a:

```text
log/transcript de sessão do agente

+

revisão de diffs antes de aceitar mudanças
```

A partir disso, foram separados dois conceitos.

### Observabilidade da aplicação

Em uma aplicação em produção, observabilidade normalmente pode envolver:

- logs;
- métricas;
- traces;
- erros;
- latência;
- alertas.

E ferramentas como:

- Sentry;
- Datadog;
- Grafana;
- OpenTelemetry.

### Observabilidade do processo agentic

No contexto específico do item de **Harness e controle de agentes** deste projeto, a preocupação é conseguir responder perguntas como:

- O que o agente recebeu como instrução?
- O que ele decidiu fazer?
- Quais ferramentas executou?
- Onde houve erro?
- Como o erro foi corrigido?
- O humano interveio?
- Qual arquivo foi alterado?
- O diff foi verificado?
- O guardrail atuou?
- Quando a mudança passou a ser aceita?

Por isso, neste trabalho, a observabilidade do processo é evidenciada por:

```text
transcript persistido
        +
tool calls
        +
intervenções humanas
        +
validações
        +
guardrail
        +
diff
        +
histórico Git
        +
Pull Request
```

---

## 21. Quatro momentos da interação humano-agente

A sessão pode ser resumida da seguinte forma:

| Momento | Pergunta principal | Resultado |
|---|---|---|
| **1. Produto e discovery** | O que é o Fatura em Dia e o que já existe? | Leitura do produto, edital, documentação, código e testes |
| **2. SDD** | Como transformar esse material em specifications estruturadas? | Investigação e adoção do OpenSpec |
| **3. Specifications** | Qual é a baseline comportamental do produto? | 8 capability specs, change, design e tasks |
| **4. Harness** | Como controlar e observar o agente antes de aceitar mudanças? | Guardrail, validações, diff review, commit, push e PR |

Em forma de fluxo:

```text
┌─────────────────────────────┐
│  1. Entendimento do produto │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     2. Definição do SDD     │
│          OpenSpec           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   3. Specs + Change + ADR   │
│       validação strict      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         4. Harness          │
│ guardrail + diff + revisão  │
└──────────────┬──────────────┘
               │
               ▼
           commit / PR
```

---

## 22. O que esta evidência demonstra

| Exigência | Evidência apresentada |
|---|---|
| Definição do nível de autonomia | Autonomia alta para atividades reversíveis e gates humanos para decisões e efeitos externos |
| Justificativa da autonomia | Pesquisa, leitura e validação são reversíveis; integração externa exige maior controle |
| Intervenção humana | Duas interrupções registradas no transcript |
| Decisão solicitada ao humano | Uma chamada explícita de pergunta |
| Guardrail configurado | Git Hook por meio de `core.hooksPath` |
| Guardrail funcionando | Bloqueio real registrado em `guardrail-bloqueio-commit.png` |
| Transcript da sessão | JSONL `c8579109` |
| Tool calls rastreáveis | 76 chamadas registradas |
| Erro do agente observável | Spec delta `MODIFIED` rejeitada |
| Correção observável | Ajuste do artefato seguido de nova validação |
| Validação estruturada | `openspec validate --strict` |
| Controle antes da aceitação | `git diff` revisado antes do commit |
| Efeito externo controlado | Identidade Git corrigida pelo humano antes do push |
| Revisão posterior | Mudança enviada via Pull Request |
| SDD utilizado de fato | baseline → change → design → tasks → implementação |

---

## 23. Relação com os artefatos do projeto

Esta evidência deve ser analisada em conjunto com os demais artefatos.

### Specifications

```text
openspec/specs/
```

Contém a baseline estruturada do Fatura em Dia.

### Changes

```text
openspec/changes/
```

Contém mudanças propostas em relação à baseline.

### ADR

```text
docs/adr/0003-adocao-do-openspec.md
```

Registra a decisão de adoção da ferramenta utilizada para SDD.

### Especificação inicial

```text
docs/especificacao-inicial.md
```

Registra o contexto inicial e a política de desenvolvimento adotada.

### Requisitos históricos

```text
docs/requisitos-funcionais.md
```

Mantém os requisitos funcionais anteriores e sua relação com as capabilities.

### Evidência do guardrail

```text
guardrail-bloqueio-commit.png
```

Demonstra a atuação real do mecanismo de bloqueio.

### Histórico Git

O histórico do repositório complementa o transcript permitindo verificar:

- branch;
- commit;
- ordem das alterações;
- Pull Request.

---

## 24. Por que o transcript é importante

Sem o transcript, seria possível observar apenas:

```text
estado inicial do repositório
          ↓
estado final do repositório
```

Isso não permitiria saber:

- quanto da solução foi definida pelo humano;
- quais caminhos o agente tentou;
- quais caminhos foram descartados;
- quais erros ocorreram;
- se houve intervenção humana;
- se o agente tomou decisões sozinho;
- se houve validação antes da aceitação.

Com o transcript, é possível reconstruir:

```text
prompt
  ↓
interpretação
  ↓
tool call
  ↓
resultado
  ↓
erro/sucesso
  ↓
intervenção
  ↓
correção
  ↓
diff
  ↓
aceitação
```

Por isso o JSONL funciona como uma forma de **audit trail do processo assistido por IA**.

---

## 25. Por que a revisão de diff é importante

O transcript mostra **como o agente trabalhou**.

O diff mostra **o que efetivamente mudou no produto**.

Os dois artefatos são complementares.

Um agente pode, por exemplo:

```text
ler 20 arquivos
       ↓
testar 5 abordagens
       ↓
executar dezenas de comandos
       ↓
produzir várias hipóteses
```

mas apenas parte disso deve chegar ao repositório.

A revisão de diff cria uma fronteira clara:

```text
atividade do agente
        ↓
mudança candidata
        ↓
DIFF
        ↓
revisão
        ↓
mudança aceita
```

Essa fronteira é importante para evitar que toda alteração produzida pelo agente seja automaticamente tratada como correta.

---

## 26. Conclusão

A sessão registrada demonstra que o Claude Code foi utilizado como parte de um processo de engenharia controlado e observável, e não apenas como gerador de código.

O agente recebeu autonomia para:

- ler;
- investigar;
- comparar;
- pesquisar;
- estruturar;
- propor;
- validar.

Mas permaneceu sujeito a mecanismos de controle nos pontos relevantes.

Durante a sessão houve:

- entendimento do problema do produto;
- análise do estado existente;
- direcionamento humano para SDD;
- interrupção de uma abordagem considerada inadequada;
- investigação de uma ferramenta;
- teste da ferramenta em sandbox;
- adoção do OpenSpec;
- formalização de oito capabilities;
- validação strict;
- erro real detectado pelo validator;
- correção da spec;
- documentação arquitetural;
- configuração de guardrail;
- bloqueio real pelo guardrail;
- intervenção humana sobre identidade Git;
- revisão do diff antes do commit;
- e entrega por Pull Request.

A sequência observada foi:

```text
PRODUTO
   ↓
SPEC
   ↓
VALIDAÇÃO
   ↓
CHANGE
   ↓
DESIGN
   ↓
TASKS
   ↓
GUARDRAIL
   ↓
DIFF
   ↓
REVISÃO
   ↓
COMMIT / PR
```

Assim, a evidência permite observar não somente **o que foi produzido pelo agente**, mas também **como as decisões foram tomadas, como o humano manteve controle sobre o processo e em que momento uma alteração passou de saída do agente para mudança aceita no projeto**.

---

## 27. Evidências complementares

Este registro é complementado por:

1. transcript JSONL da sessão `c8579109`;
2. `openspec/specs/`;
3. `openspec/changes/`;
4. `docs/adr/0003-adocao-do-openspec.md`;
5. `docs/especificacao-inicial.md`;
6. `docs/requisitos-funcionais.md`;
7. `guardrail-bloqueio-commit.png`;
8. histórico de commits;
9. Pull Request da alteração.

Em conjunto, esses artefatos demonstram:

```text
Specification-Driven Development
        +
Harness
        +
Guardrails
        +
Observabilidade
        +
Revisão humana
```