## MODIFIED Requirements

### Requirement: Cadastro de pessoas do rateio
O sistema SHALL permitir criar, editar e remover pessoas que podem participar do rateio de uma despesa. Pessoas do rateio MUST ser rótulos internos da conta, sem acesso próprio ao sistema. Renomear uma pessoa MUST propagar o novo nome para todos os lançamentos, regras e pagamentos da conta que a referenciam, de modo que o histórico dela permaneça íntegro.

#### Scenario: Criar pessoa
- **GIVEN** uma conta autenticada
- **WHEN** a pessoa cadastra um novo nome no rateio
- **THEN** esse nome passa a estar disponível para ser marcado em lançamentos

#### Scenario: Renomear pessoa preserva o histórico
- **GIVEN** uma pessoa chamada "Bruna" marcada em lançamentos e com pagamentos registrados
- **WHEN** ela é renomeada para "Bruna Silva"
- **THEN** os lançamentos, regras e pagamentos que a citavam passam a citar o novo nome, e o extrato dela continua apresentando os mesmos valores

#### Scenario: Remover pessoa
- **GIVEN** uma pessoa cadastrada no rateio
- **WHEN** ela é removida
- **THEN** deixa de aparecer entre as opções de rateio

#### Scenario: Caso de borda — editar pessoa de outra conta
- **GIVEN** o identificador de uma pessoa que pertence a outra conta
- **WHEN** a pessoa autenticada tenta renomeá-la
- **THEN** o sistema responde como se ela não existisse e nada é alterado

### Requirement: Cadastro de categorias
O sistema SHALL permitir criar, editar e remover categorias de despesa próprias da conta. Renomear uma categoria MUST propagar o novo nome para os lançamentos e regras da conta que a referenciam.

#### Scenario: Criar categoria
- **GIVEN** uma conta autenticada
- **WHEN** a pessoa cadastra uma nova categoria
- **THEN** ela passa a estar disponível na classificação de despesas

#### Scenario: Renomear categoria preserva a classificação
- **GIVEN** uma categoria "Mercado" usada em lançamentos do mês
- **WHEN** ela é renomeada para "Supermercado"
- **THEN** o ranking de gastos por categoria do painel passa a exibir o novo nome com o mesmo total
