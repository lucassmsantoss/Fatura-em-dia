## MODIFIED Requirements

### Requirement: Criação de regra ao registrar despesa
Ao registrar uma despesa, o sistema SHALL criar uma regra de auto-categorização apenas quando a pessoa pedir explicitamente por isso naquele lançamento. Quando pedido, a regra SHALL ser derivada das duas primeiras palavras da descrição, associada à categoria e às pessoas informadas, e o sistema MUST não criar uma segunda regra quando já existir uma com a mesma palavra-chave.

#### Scenario: Primeira despesa gera regra
- **GIVEN** uma conta sem nenhuma regra cadastrada
- **WHEN** é registrada uma despesa descrita como "Mercado Bom Preço" na categoria "Mercado" com a opção de memorizar marcada
- **THEN** passa a existir uma regra associando essa palavra-chave à categoria "Mercado"

#### Scenario: Despesa registrada sem pedir memorização
- **GIVEN** uma conta autenticada
- **WHEN** é registrada uma despesa sem marcar a opção de memorizar categoria e pessoas
- **THEN** nenhuma regra nova é criada e a lista de regras permanece inalterada

#### Scenario: Caso de borda — regra já existente não é duplicada
- **GIVEN** uma conta que já possui uma regra com a palavra-chave derivada da descrição
- **WHEN** outra despesa com a mesma descrição é registrada com a opção de memorizar marcada
- **THEN** nenhuma regra adicional é criada
