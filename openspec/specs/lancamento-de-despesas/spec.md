## Purpose

É o coração do produto: registrar uma despesa dizendo quanto custou, quem divide e em quantas vezes, e deixar que o sistema resolva sozinho em qual mês de fatura cada parte dela vai cair.

## Requirements

### Requirement: Registro de despesa
O sistema SHALL registrar uma despesa a partir de valor, descrição, data, forma de pagamento, categoria, pessoas que dividem e número de parcelas entre 1 e 48.

#### Scenario: Despesa à vista atribuída a uma pessoa
- **GIVEN** uma conta com ao menos uma forma de pagamento e uma pessoa cadastradas
- **WHEN** é registrada uma despesa de R$ 300,00 em uma parcela com uma única pessoa marcada
- **THEN** é criado um lançamento de R$ 300,00 no mês de fatura correspondente, atribuído integralmente a essa pessoa

#### Scenario: Caso de borda — valor ausente ou zerado
- **GIVEN** uma pessoa preenchendo uma despesa
- **WHEN** ela tenta registrar com valor vazio, zero ou negativo
- **THEN** o sistema recusa o registro e nenhum lançamento é criado

#### Scenario: Caso de borda — forma de pagamento não cadastrada
- **GIVEN** uma despesa cuja forma de pagamento não existe na conta
- **WHEN** o registro é tentado
- **THEN** o sistema recusa e informa que a forma de pagamento não está cadastrada

### Requirement: Parcelamento
Uma despesa parcelada em N vezes SHALL gerar N lançamentos, um por mês consecutivo a partir do mês de fatura de referência, e a soma das parcelas MUST ser exatamente igual ao valor original da compra.

#### Scenario: Compra dividida em quatro parcelas
- **GIVEN** uma despesa de R$ 1.200,00 em 4 parcelas com mês de referência 2026-10
- **WHEN** ela é registrada
- **THEN** são criados 4 lançamentos de R$ 300,00, nos meses 2026-10, 2026-11, 2026-12 e 2027-01, cada um identificado por sua posição na sequência

#### Scenario: Caso de borda — divisão que não fecha em centavos
- **GIVEN** uma despesa de R$ 100,00 em 3 parcelas
- **WHEN** ela é registrada
- **THEN** a soma das três parcelas é exatamente R$ 100,00, sem centavo perdido ou criado

#### Scenario: Caso de borda — número de parcelas inválido
- **GIVEN** uma despesa cujo número de parcelas é zero, negativo ou acima de 48
- **WHEN** ela é registrada
- **THEN** o sistema trata o valor como dentro do intervalo permitido em vez de falhar

### Requirement: Ciclo de fechamento de fatura
O mês de fatura de uma compra SHALL ser determinado pelo dia de fechamento e pelo deslocamento da forma de pagamento: compra em dia posterior ao fechamento entra no ciclo seguinte, e o deslocamento é somado depois disso.

#### Scenario: Compra antes do fechamento
- **GIVEN** um cartão que fecha no dia 24 e cobra 1 mês depois
- **WHEN** uma compra é feita no dia 10 de setembro
- **THEN** ela cai na fatura de outubro

#### Scenario: Compra depois do fechamento
- **GIVEN** o mesmo cartão que fecha no dia 24 e cobra 1 mês depois
- **WHEN** uma compra é feita no dia 28 de setembro
- **THEN** ela cai na fatura de novembro

#### Scenario: Caso de borda — compra no dia exato do fechamento
- **GIVEN** um cartão que fecha no dia 24, sem deslocamento
- **WHEN** uma compra é feita no dia 24
- **THEN** ela permanece no ciclo do próprio mês, pois apenas dias posteriores ao fechamento avançam o ciclo

### Requirement: Rateio entre pessoas
O valor de um lançamento SHALL ser dividido em partes iguais entre as pessoas marcadas nele, e um lançamento sem nenhuma pessoa marcada MUST ser identificável como sem dono.

#### Scenario: Divisão igualitária
- **GIVEN** um lançamento de R$ 300,00 com três pessoas marcadas
- **WHEN** a parte de cada uma é calculada
- **THEN** cada pessoa responde por R$ 100,00

#### Scenario: Caso de borda — lançamento sem dono
- **GIVEN** um lançamento sem nenhuma pessoa marcada
- **WHEN** a parte por pessoa é calculada
- **THEN** o resultado é zero e o lançamento é contabilizado como sem dono no painel do mês

### Requirement: Correção de lançamento existente
O sistema SHALL permitir atribuir ou alterar as pessoas de um lançamento já registrado e remover um lançamento.

#### Scenario: Atribuir dono depois do registro
- **GIVEN** um lançamento registrado sem pessoas
- **WHEN** uma ou mais pessoas são atribuídas a ele
- **THEN** o lançamento deixa de ser contabilizado como sem dono e passa a compor o rateio dessas pessoas
