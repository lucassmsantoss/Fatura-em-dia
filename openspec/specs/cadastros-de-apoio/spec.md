## Purpose

Mantém os três cadastros que dão sentido a um lançamento — quem divide, por onde foi pago e de que tipo é o gasto — sob controle da própria pessoa, sem lista fixa imposta pelo produto.

## Requirements

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

### Requirement: Cadastro de formas de pagamento
O sistema SHALL permitir criar, editar e remover formas de pagamento, cada uma com nome, cor, dia de fechamento e quantidade de meses até a cobrança da fatura.

#### Scenario: Criar forma de pagamento com ciclo de fatura
- **GIVEN** uma conta autenticada
- **WHEN** a pessoa cadastra um cartão com dia de fechamento e deslocamento de meses
- **THEN** esses parâmetros passam a determinar em que mês de fatura cai cada compra feita nesse cartão

#### Scenario: Editar forma de pagamento
- **GIVEN** uma forma de pagamento existente
- **WHEN** seus dados são alterados
- **THEN** os novos valores passam a valer para os lançamentos criados a partir de então

#### Scenario: Caso de borda — pagamento sem fatura
- **GIVEN** uma forma de pagamento com dia de fechamento igual a zero, como Pix ou dinheiro
- **WHEN** uma compra é registrada nela
- **THEN** a compra cai no mês da própria data da compra, sem deslocamento de ciclo

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

