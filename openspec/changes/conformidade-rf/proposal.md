## Why

Uma revisão de conformidade comparou o comportamento implementado com os requisitos aceitos em `docs/requisitos-funcionais.md` (commit `6253069`, escrito antes do código) e encontrou cinco divergências. Nenhuma é ideia nova: são requisitos já acordados pela dupla e já anunciados no README que não estão fechados de ponta a ponta.

Duas delas quebram a demonstração do sistema:

- **A previsão de meses futuros nunca soma parcelas.** O cálculo considera apenas lançamentos classificados como compromisso ou estimativa, mas nenhum ponto do sistema classifica um lançamento como compromisso. Parcelas futuras de uma compra parcelada ficam de fora, e o painel exibe previsão zerada mesmo com parcelamento ativo. O critério de aceite de RF09 já escrito em `docs/requisitos-funcionais.md` não é atendido.
- **A receita existe apenas no mês da configuração inicial.** Não há como consultá-la nem alterá-la depois. A partir do mês seguinte o painel calcula sobra ou falta contra receita zero e sempre acusa falta.

As outras três são lacunas de contrato: pessoas e categorias não podem ser editadas, embora RF03 e RF05 digam "criar, editar e remover"; a regra de auto-categorização é criada à revelia da pessoa em toda despesa, embora RF07 diga que ela *pode* criar a regra; e a exportação/importação em CSV (RF11) está anunciada no README sem nenhuma implementação.

## What Changes

- Parcelas cujo mês de fatura é posterior ao mês corrente passam a ser classificadas como compromisso, entrando na previsão. A marcação explícita de conta fixa recorrente continua prevalecendo sobre essa regra.
- A receita de qualquer mês passa a poder ser consultada e alterada, e não apenas registrada uma vez na configuração inicial.
- Pessoas e categorias passam a poder ser renomeadas, com propagação do novo nome para os lançamentos, regras e pagamentos que as referenciam.
- A criação de regra de auto-categorização passa a depender de escolha explícita da pessoa a cada lançamento, em vez de acontecer sempre.
- Passa a existir exportação e importação de lançamentos em CSV.

## Capabilities

### New Capabilities
- `importacao-exportacao-csv`: exportação e importação dos lançamentos da conta em formato tabular portátil, permitindo backup e migração sem depender do produto

### Modified Capabilities
- `previsao-financeira`: a previsão passa a incluir parcelas futuras já contratadas, não apenas contas fixas recorrentes
- `painel-mensal`: a receita de um mês passa a ser consultável e alterável a qualquer momento
- `cadastros-de-apoio`: pessoas e categorias passam a ser editáveis, com propagação do nome para os registros que as referenciam
- `auto-categorizacao`: a criação de regra ao registrar despesa passa a ser uma escolha explícita, não um efeito automático

## Impact

- **Comportamento observável:** previsão deixa de exibir zero com parcelamento ativo; painel deixa de acusar falta indevida a partir do segundo mês; renomear pessoa deixa de órfanar lançamentos.
- **Contrato da API:** duas rotas novas de edição (pessoa e categoria), uma rota nova de consulta de receita, duas rotas novas de CSV. Nenhuma rota existente muda de assinatura.
- **Dados:** nenhuma alteração de esquema — todos os campos necessários já existem. A propagação de nome altera registros existentes dentro da mesma transação.
- **Interface:** aba de ajustes ganha receita do mês e edição de pessoa e categoria; formulário de lançamento ganha a escolha de memorizar a regra.
- **Testes:** cada critério de aceite desta proposta vira teste automatizado; a suíte roda no gate de pre-commit já existente (ADR 0002).
