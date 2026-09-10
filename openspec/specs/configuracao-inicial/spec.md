## Purpose

Permite que uma conta recém-criada fique utilizável em uma única passagem guiada, sem nenhum dado pré-existente embutido no produto. É o que torna o sistema genérico, e não o caderno de uma pessoa específica.

## Requirements

### Requirement: Configuração inicial guiada
O sistema SHALL oferecer, no primeiro acesso, um fluxo que cadastre de uma só vez a renda mensal, as pessoas do rateio, ao menos uma forma de pagamento e as categorias de despesa.

#### Scenario: Conclusão da configuração inicial
- **GIVEN** uma conta recém-criada que ainda não configurou nada
- **WHEN** a pessoa informa renda, ao menos uma pessoa e ao menos uma forma de pagamento e conclui
- **THEN** os cadastros passam a existir na conta e a configuração inicial é marcada como concluída

#### Scenario: Retorno após configuração concluída
- **GIVEN** uma conta que já concluiu a configuração inicial
- **WHEN** a pessoa entra novamente
- **THEN** ela vai direto para a aplicação, sem repetir o fluxo de configuração

#### Scenario: Caso de borda — nenhuma pessoa informada
- **GIVEN** uma pessoa no fluxo de configuração
- **WHEN** ela tenta concluir sem cadastrar nenhuma pessoa de rateio
- **THEN** o sistema recusa a conclusão e explica que ao menos uma pessoa é necessária

### Requirement: Ausência de dados pré-existentes
Uma conta recém-criada MUST começar sem nenhuma pessoa, forma de pagamento, categoria, regra ou lançamento herdado de outra conta ou embutido no produto.

#### Scenario: Conta nova está vazia
- **GIVEN** uma conta que acabou de ser criada
- **WHEN** suas listas de pessoas, formas de pagamento, categorias e lançamentos são consultadas
- **THEN** todas voltam vazias
