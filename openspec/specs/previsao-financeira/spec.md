## Purpose

Antecipa o quanto dos próximos meses já está comprometido antes que eles cheguem, calculando a partir do que já foi lançado — nunca a partir de tabela histórica importada ou de dado embutido no produto.

## Requirements

### Requirement: Previsão calculada a partir dos lançamentos
Para uma sequência de meses futuros, o sistema SHALL calcular o total previsto somando os lançamentos já registrados naqueles meses, separando o que é conta fixa recorrente do que é compromisso já contratado. A previsão MUST ser derivada dos lançamentos existentes, nunca de dados importados ou embutidos.

#### Scenario: Meses futuros com contas fixas recorrentes
- **GIVEN** uma conta fixa recorrente lançada em meses futuros
- **WHEN** a previsão é consultada a partir do mês corrente
- **THEN** cada mês futuro apresenta esse valor no total de estimativas e no total previsto

#### Scenario: Caso de borda — mês futuro sem nada lançado
- **GIVEN** um mês futuro sem nenhum lançamento
- **WHEN** a previsão é consultada
- **THEN** esse mês aparece com previsão zerada, sem erro

#### Scenario: Caso de borda — horizonte de meses fora do intervalo
- **GIVEN** um pedido de previsão com quantidade de meses igual a zero ou acima do limite suportado
- **WHEN** a previsão é consultada
- **THEN** o sistema ajusta a quantidade para dentro do intervalo permitido em vez de falhar

### Requirement: Previsão começa após o mês de referência
A previsão SHALL cobrir os meses posteriores ao mês de referência informado, sem incluir o próprio mês de referência.

#### Scenario: Previsão a partir do mês corrente
- **GIVEN** um pedido de previsão a partir de 2026-09 com horizonte de 3 meses
- **WHEN** ela é consultada
- **THEN** são devolvidos os meses 2026-10, 2026-11 e 2026-12
