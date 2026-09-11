## ADDED Requirements

### Requirement: Consulta e alteração da receita de um mês
O sistema SHALL permitir consultar a receita registrada para qualquer mês e alterá-la a qualquer momento, e não apenas no momento da configuração inicial. A consulta de um mês sem receita registrada MUST devolver valores zerados em vez de erro.

#### Scenario: Consultar receita de um mês já registrado
- **GIVEN** um mês com receita registrada
- **WHEN** a receita desse mês é consultada
- **THEN** o sistema devolve a renda principal e a renda extra registradas

#### Scenario: Alterar a receita de um mês passado ou futuro
- **GIVEN** um mês diferente daquele em que a configuração inicial foi concluída
- **WHEN** uma receita é informada para esse mês
- **THEN** o painel desse mês passa a calcular sobra ou falta contra o novo valor

#### Scenario: Caso de borda — mês sem receita registrada
- **GIVEN** um mês para o qual nenhuma receita foi registrada
- **WHEN** a receita desse mês é consultada
- **THEN** o sistema devolve renda principal e renda extra iguais a zero, sem tratar a ausência como erro
