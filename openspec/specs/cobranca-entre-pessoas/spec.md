## Purpose

Fecha o ciclo social do produto: saber quanto cada pessoa deve, sem planilha paralela, e registrar o que ela já pagou para que a dívida pare de aparecer.

## Requirements

### Requirement: Extrato de uma pessoa em um mês
O sistema SHALL apresentar, para uma pessoa e um mês, quanto ela deve pelas despesas daquele mês, quanto já pagou naquele mês e o saldo acumulado até ali.

#### Scenario: Pessoa com despesas no mês
- **GIVEN** uma pessoa marcada em lançamentos rateados de um mês
- **WHEN** seu extrato daquele mês é consultado
- **THEN** o sistema apresenta o valor devido no mês, o valor já pago no mês e o acumulado

#### Scenario: Caso de borda — pessoa não cadastrada
- **GIVEN** um nome que não corresponde a nenhuma pessoa da conta
- **WHEN** o extrato dela é solicitado
- **THEN** o sistema responde que a pessoa não existe, sem devolver valores

### Requirement: Saldo acumulado entre meses
O saldo acumulado de uma pessoa SHALL considerar tudo o que lhe coube em todos os meses até o mês consultado, descontado tudo o que ela já pagou até esse mesmo mês.

#### Scenario: Dívida atravessa meses
- **GIVEN** uma pessoa que deve valores em dois meses consecutivos e não pagou nada
- **WHEN** o extrato do segundo mês é consultado
- **THEN** o acumulado corresponde à soma das duas dívidas

#### Scenario: Caso de borda — pagamento quita o acumulado
- **GIVEN** uma pessoa cujo acumulado é igual ao valor que ela acabou de pagar
- **WHEN** o extrato é consultado após o registro do pagamento
- **THEN** o acumulado dela fica zerado

### Requirement: Registro de pagamento recebido
O sistema SHALL registrar um pagamento recebido de uma pessoa, com valor, data e mês de referência, e esse registro MUST abater o saldo devedor dela.

#### Scenario: Registrar pagamento parcial
- **GIVEN** uma pessoa que deve R$ 200,00 no mês
- **WHEN** é registrado um pagamento de R$ 50,00 referente a esse mês
- **THEN** o saldo dela passa a refletir R$ 150,00 em aberto

#### Scenario: Caso de borda — valor de pagamento inválido
- **GIVEN** um registro de pagamento com valor zero ou negativo
- **WHEN** ele é enviado
- **THEN** o sistema recusa o registro e o saldo da pessoa permanece inalterado

### Requirement: Lista de devedores do mês
O painel do mês SHALL listar as pessoas com valor devido, pago ou acumulado diferente de zero, omitindo quem está integralmente quite.

#### Scenario: Pessoa quite não aparece
- **GIVEN** uma pessoa sem despesas no mês e com acumulado zerado
- **WHEN** o painel do mês é consultado
- **THEN** ela não aparece na lista de quem deve
