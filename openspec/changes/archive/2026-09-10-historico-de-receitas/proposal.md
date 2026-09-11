## Why

O contrato hoje permite consultar a receita **de um mês por vez**. Isso atende o campo de
receita da aba de ajustes, mas não responde a pergunta que a pessoa faz quando abre aquela aba:
*em quais meses eu já registrei receita, e quanto?*

Sem essa visão, quem usa o sistema por alguns meses não tem como perceber que esqueceu de
registrar a receita de um mês — o painel daquele mês simplesmente acusa falta, e a causa fica
invisível. O único jeito de descobrir é abrir mês a mês e conferir.

Esta é uma capacidade **nova**, não uma lacuna do contrato anterior: a consulta por mês foi
implementada exatamente como especificada. A necessidade apareceu ao usar a especificação para
desenhar a interface de ajustes.

## What Changes

- Passa a existir a consulta das receitas já registradas na conta, em uma única chamada,
  ordenadas por mês.
- A consulta por mês individual permanece como está — as duas convivem, com propósitos
  diferentes: preencher um campo (por mês) e enxergar o histórico (listagem).

## Capabilities

### Modified Capabilities
- `painel-mensal`: passa a permitir enxergar de uma vez todos os meses com receita registrada, e não apenas consultar um mês por vez

## Impact

- **Contrato da API:** uma rota nova de listagem. Nenhuma rota existente muda de assinatura.
- **Dados:** nenhuma alteração de esquema — a tabela de receitas já guarda tudo o que a
  listagem precisa.
- **Interface:** a aba de ajustes pode exibir o histórico ao lado do campo de edição.
- **Testes:** os cenários desta proposta viram teste automatizado, escritos antes da
  implementação.
