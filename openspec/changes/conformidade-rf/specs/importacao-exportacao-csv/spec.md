## Purpose

Permite que a pessoa leve os próprios lançamentos para fora do produto e os traga de volta, em formato tabular aberto, sem depender de o sistema continuar existindo ou de acesso à conta original.

## ADDED Requirements

### Requirement: Exportação de lançamentos
O sistema SHALL exportar todos os lançamentos da conta autenticada em formato CSV, com uma linha por lançamento e uma linha inicial de cabeçalho identificando as colunas.

#### Scenario: Exportar conta com lançamentos
- **GIVEN** uma conta com lançamentos registrados
- **WHEN** a exportação é solicitada
- **THEN** o sistema devolve um CSV com uma linha de cabeçalho e uma linha por lançamento, contendo data, mês de fatura, descrição, categoria, forma de pagamento, parcela, valor, pessoas e tipo

#### Scenario: Caso de borda — conta sem lançamentos
- **GIVEN** uma conta sem nenhum lançamento
- **WHEN** a exportação é solicitada
- **THEN** o sistema devolve um CSV contendo apenas a linha de cabeçalho, sem erro

### Requirement: Importação de lançamentos
O sistema SHALL importar lançamentos a partir de um CSV no mesmo formato produzido pela exportação, e MUST relatar quantas linhas foram importadas e quais foram rejeitadas.

#### Scenario: Ciclo de exportação e importação preserva os dados
- **GIVEN** uma conta com três lançamentos exportados em CSV
- **WHEN** esse CSV é importado em uma conta vazia
- **THEN** os três lançamentos são recriados com o mesmo valor, mês de fatura e pessoas

#### Scenario: Caso de borda — linha malformada não aborta a importação
- **GIVEN** um CSV cuja segunda linha contém um valor não numérico
- **WHEN** o arquivo é importado
- **THEN** as demais linhas são importadas normalmente e a resposta identifica a linha rejeitada e o motivo

#### Scenario: Caso de borda — arquivo sem cabeçalho reconhecível
- **GIVEN** um arquivo cujas colunas não correspondem ao formato esperado
- **WHEN** a importação é tentada
- **THEN** o sistema recusa o arquivo inteiro e nenhum lançamento é criado
