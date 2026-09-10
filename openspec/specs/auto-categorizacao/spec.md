## Purpose

Reduz o esforço de lançar despesas repetidas: o sistema aprende com o que já foi classificado antes e propõe categoria e rateio a partir da própria descrição digitada.

## Requirements

### Requirement: Sugestão por palavra-chave
Ao receber uma descrição, o sistema SHALL procurar entre as regras da conta a primeira cuja palavra-chave esteja contida nessa descrição e sugerir a categoria e as pessoas associadas a ela. A comparação MUST ignorar acentuação e diferença entre maiúsculas e minúsculas.

#### Scenario: Descrição corresponde a uma regra
- **GIVEN** uma regra que associa a palavra-chave "mercado bom preco" à categoria "Mercado" e à pessoa "Ana"
- **WHEN** é digitada a descrição "Compra no Mercado Bom Preço"
- **THEN** o sistema sugere a categoria "Mercado" e a pessoa "Ana"

#### Scenario: Comparação tolerante a acento e caixa
- **GIVEN** uma regra com a palavra-chave "padaria"
- **WHEN** é digitada a descrição "PADARIA São José"
- **THEN** a regra é reconhecida como correspondente

#### Scenario: Caso de borda — nenhuma regra corresponde
- **GIVEN** uma conta cujas regras não têm relação com a descrição digitada
- **WHEN** a sugestão é solicitada
- **THEN** o sistema devolve uma sugestão vazia, sem erro e sem alterar o que a pessoa já preencheu

#### Scenario: Caso de borda — descrição vazia
- **GIVEN** uma descrição em branco
- **WHEN** a sugestão é solicitada
- **THEN** o sistema devolve sugestão vazia e nenhuma regra é considerada correspondente

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

### Requirement: Gestão das regras
O sistema SHALL permitir consultar e remover as regras de auto-categorização da conta.

#### Scenario: Remover regra que classifica errado
- **GIVEN** uma regra que vem sugerindo a categoria errada
- **WHEN** ela é removida
- **THEN** descrições que antes correspondiam a ela deixam de receber aquela sugestão
