## Why

O primeiro passe de especificação foi escrito lendo o protótipo que existia no repositório. O
efeito disso só ficou visível depois: as capacidades em `openspec/specs/` descreviam o que
aquele protótipo fazia, e não os requisitos que a dupla havia acordado em
`docs/requisitos-funcionais.md` (commit `6253069`). O contrato nasceu mais estreito que os
requisitos que ele deveria codificar — e, pior, mais estreito de um jeito silencioso: quem
lesse só os specs concluiria que estava tudo conforme.

Cinco pontos ficaram de fora:

- `cadastros-de-apoio` dizia "criar e remover" pessoas e categorias. RF03 e RF05 dizem
  "criar, **editar** e remover".
- `previsao-financeira` não exigia que parcelas futuras entrassem na previsão, embora seja
  exatamente o que RF09 descreve e o que dá sentido à funcionalidade.
- `painel-mensal` só exigia *registrar* receita, não consultá-la nem alterá-la depois — o que
  deixaria a receita presa ao mês da configuração inicial.
- `auto-categorizacao` descrevia a criação de regra como efeito automático de todo lançamento.
  RF07 diz que a pessoa **pode** criar a regra.
- RF11 (exportar/importar CSV) estava anunciado no README sem capacidade correspondente.

O código de backend e frontend presente no repositório é **protótipo provisório**, não entrega:
ele foi escrito antes das specs existirem e não é a referência de nada. A correção aqui é de
contrato, e acontece **antes** da implementação — que é a ordem que o SDD exige.

## What Changes

- Pessoas e categorias passam a ser editáveis no contrato, com propagação do novo nome para os
  lançamentos, regras e pagamentos que as referenciam.
- A previsão passa a exigir que parcela cujo mês de fatura é posterior ao mês corrente seja
  classificada como compromisso já contratado. A marcação explícita de conta fixa recorrente
  prevalece sobre essa classificação por data.
- A receita de qualquer mês passa a ser consultável e alterável; mês sem receita registrada
  devolve zero, não erro.
- A criação de regra de auto-categorização passa a depender de escolha explícita da pessoa a
  cada lançamento.
- Passa a existir a capacidade de exportação e importação de lançamentos em CSV.

## Capabilities

### New Capabilities
- `importacao-exportacao-csv`: exportação e importação dos lançamentos da conta em formato tabular portátil, permitindo backup e migração sem depender do produto

### Modified Capabilities
- `previsao-financeira`: a previsão passa a incluir parcelas futuras já contratadas, não apenas contas fixas recorrentes
- `painel-mensal`: a receita de um mês passa a ser consultável e alterável a qualquer momento
- `cadastros-de-apoio`: pessoas e categorias passam a ser editáveis, com propagação do nome para os registros que as referenciam
- `auto-categorizacao`: a criação de regra ao registrar despesa passa a ser uma escolha explícita, não um efeito automático

## Impact

- **Contrato:** `openspec/specs/` passa a cobrir os 11 requisitos funcionais acordados — 9
  capacidades, 29 requirements, 69 cenários, todos aprovados em `openspec validate --strict`.
  A rastreabilidade RF → capacidade está em `docs/requisitos-funcionais.md`.
- **Implementação:** nenhuma. Este change não entrega código; ele fecha o contrato contra o
  qual o código será construído. O plano de construção está em `tasks.md`.
- **Dados:** o contrato não exige alteração de esquema — os campos necessários já estão
  previstos no modelo do protótipo e podem ser reaproveitados.
- **Testes:** cada cenário do contrato deve virar teste automatizado; a suíte roda no gate de
  pre-commit já existente (ADR 0002).
