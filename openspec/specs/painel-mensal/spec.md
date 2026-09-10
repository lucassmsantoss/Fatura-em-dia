## Purpose

Responde à única pergunta que a pessoa realmente faz no fim do mês: quanto disso tudo é meu, quanto entrou, e sobrou ou faltou. Consolida em um mês os lançamentos, o rateio e a receita.

## Requirements

### Requirement: Consolidação do mês
Para um mês escolhido, o sistema SHALL apresentar o total lançado, a parcela que cabe à pessoa dona da conta, a receita registrada para aquele mês e a diferença entre as duas últimas como sobra ou falta.

#### Scenario: Mês com despesas e receita
- **GIVEN** um mês com lançamentos rateados e receita registrada
- **WHEN** o painel desse mês é consultado
- **THEN** ele apresenta o total do mês, o total próprio, a receita e a sobra ou falta correspondente

#### Scenario: Caso de borda — mês sem nenhum lançamento
- **GIVEN** um mês sem nenhum lançamento
- **WHEN** o painel desse mês é consultado
- **THEN** os totais voltam zerados, sem erro

#### Scenario: Caso de borda — mês sem receita registrada
- **GIVEN** um mês em que nenhuma receita foi registrada
- **WHEN** o painel desse mês é consultado
- **THEN** a receita é tratada como zero e a sobra ou falta é calculada contra esse valor

### Requirement: Distribuição do gasto próprio por categoria
O sistema SHALL apresentar, para o mês escolhido, quanto da parcela própria da pessoa foi para cada categoria, ordenado do maior para o menor.

#### Scenario: Ranking de categorias
- **GIVEN** um mês com despesas próprias em várias categorias
- **WHEN** o painel é consultado
- **THEN** as categorias aparecem com seus totais, da maior para a menor

### Requirement: Visibilidade de gasto sem dono
O sistema SHALL informar, para o mês escolhido, o valor total dos lançamentos que não têm nenhuma pessoa atribuída, para que possam ser corrigidos.

#### Scenario: Mês contém lançamento sem dono
- **GIVEN** um mês com ao menos um lançamento sem pessoa atribuída
- **WHEN** o painel é consultado
- **THEN** o valor sem dono é destacado como pendência do mês

### Requirement: Registro de receita mensal
O sistema SHALL permitir registrar a receita de um mês, composta de renda principal e renda extra, e MUST substituir o valor anterior quando o mesmo mês for registrado novamente.

#### Scenario: Registrar receita de um mês
- **GIVEN** um mês sem receita registrada
- **WHEN** a receita desse mês é informada
- **THEN** o painel daquele mês passa a calcular sobra ou falta contra esse valor

#### Scenario: Caso de borda — registrar duas vezes o mesmo mês
- **GIVEN** um mês que já tem receita registrada
- **WHEN** uma nova receita é informada para o mesmo mês
- **THEN** o valor é substituído, sem criar um segundo registro para aquele mês
