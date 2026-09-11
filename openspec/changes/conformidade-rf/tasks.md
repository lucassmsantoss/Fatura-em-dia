## 1. Linha de base de testes de API

- [x] 1.1 Criar a suíte de testes de API com cliente HTTP e banco isolado por teste, sem tocar no banco de desenvolvimento **(Maria)**
- [x] 1.2 Derivar os testes dos cenários do contrato em `openspec/specs/`, um teste por cenário, escritos **antes** da implementação de cada capacidade — feito para as 9 capacidades **(Maria)**
- [x] 1.3 Cobrir `autenticacao`: cadastro, email duplicado, senha curta, login correto, login incorreto, acesso sem credencial **(Maria)**
- [x] 1.4 Cobrir `autenticacao` → isolamento: recurso de outra conta responde como inexistente **(Maria)**

## 2. Configuração inicial e cadastros de apoio

- [x] 2.1 Testes de `configuracao-inicial`, incluindo a recusa de concluir sem nenhuma pessoa — validada **na API**, não só na interface **(Maria)**
- [x] 2.2 Implementar a configuração inicial guiada, registrando a renda informada como receita do mês corrente **(a definir)**
- [x] 2.3 Testes de `cadastros-de-apoio`: criação, remoção, renomeação com propagação, e recurso de outra conta **(Maria)**
- [x] 2.4 Implementar edição de pessoa com propagação para lançamentos, regras e pagamentos, em transação única **(Maria)**
- [x] 2.5 Implementar edição de categoria com propagação para lançamentos e regras **(Maria)**
- [x] 2.6 Expor criação e edição de forma de pagamento **depois** da configuração inicial, não apenas durante ela — API já atende (`POST`/`PUT /cartoes`, coberta por teste); falta a interface **(Lucas)**
- [x] 2.7 Expor pessoas, categorias e formas de pagamento na aba de ajustes com criar, editar e remover **(Lucas)**

## 3. Lançamento de despesa e ciclo de fatura

- [x] 3.1 Testes de `lancamento-de-despesas`: registro, parcelamento, ciclo de fechamento, rateio, correção de dono, e os casos de borda de valor e descrição **(Maria)**
- [x] 3.2 Implementar as funções puras de ciclo de fatura, rateio e geração de parcelas no módulo de domínio — já existiam no protótipo e conformam ao contrato; verificado por teste **(Maria)**
- [x] 3.3 Implementar o registro de despesa sobre essas funções, uma parcela por lançamento — já conformava; nenhuma mudança de código foi necessária **(a definir)**
- [x] 3.4 Implementar o formulário de lançamento **(Lucas)**

## 4. Auto-categorização

- [x] 4.1 Teste da sugestão por palavra-chave, incluindo tolerância a acento e caixa e os casos de borda **(Maria)**
- [x] 4.2 Teste que verifica que **nenhuma regra é criada sem pedido explícito** **(Maria)**
- [x] 4.3 Implementar o motor de regras como função pura e a criação condicional da regra — backend já conformava (`salvar_regra` default `False`, honrado pelo router); o desvio está só no front, que envia `true` fixo **(Maria)**
- [x] 4.4 Adicionar a opção de memorizar categoria e pessoas no formulário, **desmarcada por padrão** **(Lucas)**

## 5. Painel mensal e receita

- [x] 5.1 Testes de `painel-mensal`: consolidação, ranking por categoria, gasto sem dono, e receita — incluindo mês sem receita devolvendo zero **(Maria)**
- [x] 5.2 Implementar o painel do mês — já conformava (consolidação, ranking próprio, sem dono); nenhuma mudança de código **(a definir)**
- [x] 5.3 Implementar consulta e alteração de receita por mês **(a definir)**
- [x] 5.4 Adicionar a seção de receita do mês na aba de ajustes, com seleção de mês **(Lucas)**

## 6. Previsão financeira

- [x] 6.1 Teste unitário da classificação de tipo, cobrindo precedência da conta fixa recorrente e o mês corrente como **parâmetro explícito** da função **(Maria)**
- [x] 6.2 Implementar a função pura de classificação no módulo de domínio **(Maria)**
- [x] 6.3 Aplicar a classificação no registro de despesa, por parcela — feito junto com 6.2; removido também o `PATCH /lancamentos/{id}/tipo`, sem respaldo no contrato **(Lucas)**
- [x] 6.4 Teste de API da previsão: parcelas futuras somadas como compromisso, primeira parcela do mês corrente fora, mês vazio zerado, horizonte fora do intervalo ajustado **(Maria)**
- [x] 6.5 Implementar a previsão sobre os lançamentos classificados — o cálculo já conformava; o que faltava era alguém classificar **(a definir)**

## 7. Cobrança entre pessoas

- [x] 7.1 Testes de `cobranca-entre-pessoas`: extrato do mês, saldo acumulado, registro de pagamento, lista de devedores **(Maria)**
- [x] 7.2 Implementar extrato, acumulado e registro de pagamento — já conformava; nenhuma mudança de código **(a definir)**
- [x] 7.3 Implementar a aba de cobrança **(Lucas)**

## 8. Exportação e importação em CSV (condicional ao tempo restante)

- [x] 8.1 Testes do formato: ciclo completo, conta vazia, linha malformada e cabeçalho não reconhecido **(a definir)**
- [x] 8.2 Implementar serialização e leitura de CSV em módulo de domínio próprio, sem acesso a banco **(a definir)**
- [x] 8.3 Expor exportação e importação na interface — API já exposta (`GET /lancamentos/exportar`, `POST /lancamentos/importar`), coberta por teste **(a definir)**

## 9. Fechamento

- [x] 9.1 Rodar `openspec validate --all --strict` e confirmar que todo cenário do contrato tem teste correspondente **(Maria)**
- [x] 9.2 Atualizar o README com o estado real dos requisitos, sem promessas em tempo futuro **(Maria)**
- [ ] 9.3 Arquivar este change com `openspec archive conformidade-rf` **(Maria)**
