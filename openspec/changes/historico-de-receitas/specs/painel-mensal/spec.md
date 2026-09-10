## ADDED Requirements

### Requirement: Listagem das receitas registradas
O sistema SHALL permitir consultar, em uma única chamada, todas as receitas já registradas na conta autenticada, ordenadas por mês. A listagem MUST conter apenas as receitas da conta autenticada, e MUST devolver lista vazia quando não houver nenhuma receita registrada.

#### Scenario: Conta com receitas em vários meses
- **GIVEN** uma conta com receita registrada em três meses distintos
- **WHEN** as receitas da conta são consultadas
- **THEN** o sistema devolve as três, cada uma com seu mês, renda principal e renda extra, ordenadas por mês

#### Scenario: Caso de borda — conta sem nenhuma receita registrada
- **GIVEN** uma conta que ainda não registrou receita em nenhum mês
- **WHEN** as receitas da conta são consultadas
- **THEN** o sistema devolve uma lista vazia, sem tratar a ausência como erro

#### Scenario: Caso de borda — receitas de outra conta não aparecem
- **GIVEN** duas contas, cada uma com receitas registradas
- **WHEN** uma delas consulta suas receitas
- **THEN** apenas as receitas da própria conta são devolvidas
