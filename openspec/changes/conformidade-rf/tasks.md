## 1. Linha de base de testes de API

- [ ] 1.1 Criar a suíte de testes de API com cliente HTTP e banco isolado por teste, sem tocar no banco de desenvolvimento **(Maria)**
- [ ] 1.2 Derivar os testes dos cenários do contrato em `openspec/specs/`, um teste por cenário, escritos **antes** da implementação de cada capacidade **(Maria)**
- [ ] 1.3 Cobrir `autenticacao`: cadastro, email duplicado, senha curta, login correto, login incorreto, acesso sem credencial **(Maria)**
- [ ] 1.4 Cobrir `autenticacao` → isolamento: recurso de outra conta responde como inexistente **(Maria)**

## 2. Configuração inicial e cadastros de apoio

- [ ] 2.1 Testes de `configuracao-inicial`, incluindo a recusa de concluir sem nenhuma pessoa — validada **na API**, não só na interface **(Maria)**
- [ ] 2.2 Implementar a configuração inicial guiada, registrando a renda informada como receita do mês corrente **(a definir)**
- [ ] 2.3 Testes de `cadastros-de-apoio`: criação, remoção, renomeação com propagação, e recurso de outra conta **(Maria)**
- [ ] 2.4 Implementar edição de pessoa com propagação para lançamentos, regras e pagamentos, em transação única **(Maria)**
- [ ] 2.5 Implementar edição de categoria com propagação para lançamentos e regras **(Maria)**
- [ ] 2.6 Implementar criação e edição de forma de pagamento acessíveis **depois** da configuração inicial, não apenas durante ela **(Lucas)**
- [ ] 2.7 Expor pessoas, categorias e formas de pagamento na aba de ajustes com criar, editar e remover **(Lucas)**

## 3. Lançamento de despesa e ciclo de fatura

- [ ] 3.1 Testes de `lancamento-de-despesas`: registro, parcelamento, ciclo de fechamento, rateio, correção de dono, e os casos de borda de valor e descrição **(Maria)**
- [ ] 3.2 Implementar as funções puras de ciclo de fatura, rateio e geração de parcelas no módulo de domínio **(Maria)**
- [ ] 3.3 Implementar o registro de despesa sobre essas funções, uma parcela por lançamento **(a definir)**
- [ ] 3.4 Implementar o formulário de lançamento **(Lucas)**

## 4. Auto-categorização

- [ ] 4.1 Teste da sugestão por palavra-chave, incluindo tolerância a acento e caixa e os casos de borda **(Maria)**
- [ ] 4.2 Teste que verifica que **nenhuma regra é criada sem pedido explícito** **(Maria)**
- [ ] 4.3 Implementar o motor de regras como função pura e a criação condicional da regra **(Maria)**
- [ ] 4.4 Adicionar a opção de memorizar categoria e pessoas no formulário, **desmarcada por padrão** **(Lucas)**

## 5. Painel mensal e receita

- [ ] 5.1 Testes de `painel-mensal`: consolidação, ranking por categoria, gasto sem dono, e receita — incluindo mês sem receita devolvendo zero **(Maria)**
- [ ] 5.2 Implementar o painel do mês **(a definir)**
- [ ] 5.3 Implementar consulta e alteração de receita por mês **(a definir)**
- [ ] 5.4 Adicionar a seção de receita do mês na aba de ajustes, com seleção de mês **(Lucas)**

## 6. Previsão financeira

- [ ] 6.1 Teste unitário da classificação de tipo, cobrindo precedência da conta fixa recorrente e o mês corrente como **parâmetro explícito** da função **(Maria)**
- [ ] 6.2 Implementar a função pura de classificação no módulo de domínio **(Maria)**
- [ ] 6.3 Aplicar a classificação no registro de despesa, por parcela **(Lucas)**
- [ ] 6.4 Teste de API da previsão: parcelas futuras somadas como compromisso, primeira parcela do mês corrente fora, mês vazio zerado, horizonte fora do intervalo ajustado **(Maria)**
- [ ] 6.5 Implementar a previsão sobre os lançamentos classificados **(a definir)**

## 7. Cobrança entre pessoas

- [ ] 7.1 Testes de `cobranca-entre-pessoas`: extrato do mês, saldo acumulado, registro de pagamento, lista de devedores **(Maria)**
- [ ] 7.2 Implementar extrato, acumulado e registro de pagamento **(a definir)**
- [ ] 7.3 Implementar a aba de cobrança **(Lucas)**

## 8. Exportação e importação em CSV (condicional ao tempo restante)

- [ ] 8.1 Testes do formato: ciclo completo, conta vazia, linha malformada e cabeçalho não reconhecido **(a definir)**
- [ ] 8.2 Implementar serialização e leitura de CSV em módulo de domínio próprio, sem acesso a banco **(a definir)**
- [ ] 8.3 Expor exportação e importação na API e na interface **(a definir)**

## 9. Fechamento

- [ ] 9.1 Rodar `openspec validate --all --strict` e confirmar que todo cenário do contrato tem teste correspondente **(Maria)**
- [ ] 9.2 Atualizar o README com o estado real dos requisitos, sem promessas em tempo futuro **(Maria)**
- [ ] 9.3 Arquivar este change com `openspec archive conformidade-rf` **(Maria)**
