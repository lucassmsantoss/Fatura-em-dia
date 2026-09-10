## 1. Linha de base de testes

- [ ] 1.1 Criar a suíte de testes de API com cliente HTTP e banco isolado por teste, sem tocar no banco de desenvolvimento **(Maria)**
- [ ] 1.2 Cobrir autenticação: cadastro, email duplicado, senha curta, login correto, login incorreto e acesso sem credencial **(Maria)**
- [ ] 1.3 Cobrir isolamento entre contas: recurso de outra conta responde como inexistente **(Maria)**
- [ ] 1.4 Cobrir configuração inicial, cadastros de apoio, registro de despesa, parcelamento e ciclo de fatura pela API **(Maria)**
- [ ] 1.5 Cobrir painel, previsão e cobrança — incluindo os dois cenários hoje falhos, que devem reprovar antes da correção **(Maria)**

## 2. Previsão inclui parcelas futuras

- [ ] 2.1 Escrever o teste unitário da classificação de tipo, cobrindo precedência da conta fixa e o mês corrente como parâmetro **(Maria)**
- [ ] 2.2 Implementar a função pura de classificação no módulo de domínio **(Maria)**
- [ ] 2.3 Aplicar a classificação no registro de despesa, por parcela **(Lucas)**
- [ ] 2.4 Confirmar que o cenário de previsão da tarefa 1.5 passa a aprovar **(Lucas)**

## 3. Receita consultável e alterável

- [ ] 3.1 Escrever o teste da consulta de receita, incluindo mês sem registro devolvendo zero **(Maria)**
- [ ] 3.2 Implementar a consulta de receita por mês **(Lucas)**
- [ ] 3.3 Adicionar a seção de receita do mês na aba de ajustes, com seleção de mês **(Lucas)**

## 4. Edição de pessoas e categorias

- [ ] 4.1 Escrever os testes de renomeação com propagação e de recurso de outra conta **(Maria)**
- [ ] 4.2 Implementar a edição de pessoa com propagação para lançamentos, regras e pagamentos, em transação única **(Maria)**
- [ ] 4.3 Implementar a edição de categoria com propagação para lançamentos e regras **(Maria)**
- [ ] 4.4 Adicionar a edição de pessoa e categoria na aba de ajustes **(Lucas)**

## 5. Regra de auto-categorização por escolha explícita

- [ ] 5.1 Escrever o teste que verifica que nenhuma regra é criada sem pedido explícito **(Maria)**
- [ ] 5.2 Adicionar a opção de memorizar categoria e pessoas no formulário de lançamento, desmarcada por padrão **(Lucas)**

## 6. Exportação e importação em CSV (condicional ao tempo restante)

- [ ] 6.1 Escrever os testes do formato: ciclo completo, linha malformada e cabeçalho não reconhecido **(a definir)**
- [ ] 6.2 Implementar serialização e leitura de CSV no módulo de domínio **(a definir)**
- [ ] 6.3 Expor exportação e importação na API e na interface **(a definir)**

## 7. Fechamento

- [ ] 7.1 Atualizar o README com o estado real dos requisitos após as correções **(Maria)**
- [ ] 7.2 Arquivar este change com `openspec archive conformidade-rf`, promovendo os deltas para os specs principais **(Maria)**
