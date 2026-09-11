## Context

Existe no repositório um protótipo provisório — API em FastAPI, persistência em SQLite via SQLAlchemy, interface em JavaScript sem etapa de build e um módulo de domínio puro (`app/domain/fatura.py`) com testes unitários. Ele foi escrito **antes** das specs existirem e **não é entrega nem referência**: serve como estudo de viabilidade e como fonte de peças reaproveitáveis. O contrato a ser implementado é o de `openspec/specs/`, não o comportamento desse protótipo.

O que se aproveita dele como decisão, e não como código, é a separação entre domínio puro e camada HTTP — decisão da ADR 0001, e o que torna a lógica financeira testável sem subir servidor. A implementação deve preservar essa separação.

Restrições que moldam o desenho:

- **O modelo de dados do protótipo atende ao contrato.** Os campos exigidos pelas capacidades já estão previstos nele, incluindo o campo de tipo do lançamento com três valores (aconteceu, compromisso, estimativa). Reaproveitá-lo é escolha de economia, não obrigação.
- **Pessoas, categorias e formas de pagamento são referenciadas por nome nos lançamentos**, não por chave estrangeira. É a modelagem do protótipo, e mantê-la é decisão consciente de prazo — não vai ser revertida agora. Ela é a razão de a renomeação exigir propagação explícita, e fica registrada como dívida conhecida nos Non-Goals.
- **O gate de pre-commit (ADR 0002) roda a suíte do backend** em todo commit que toque `backend/`. Qualquer tarefa aqui só entra com a suíte verde.

## Goals / Non-Goals

**Goals:**

- Fechar a divergência entre os requisitos aceitos e o contrato especificado, sem introduzir requisito novo além do RF11 já anunciado.
- Manter a regra de negócio nova em funções puras no módulo de domínio, testáveis sem banco, seguindo o padrão já estabelecido.
- Produzir, para cada critério de aceite desta proposta, um teste automatizado equivalente.

**Non-Goals:**

- Substituir a referência por nome por chave estrangeira. É a correção estrutural certa, mas é uma migração de dados que não cabe no prazo; fica registrada como dívida conhecida.
- Editar valor, descrição ou categoria de um lançamento já gravado. Permanece fora de escopo, como já registrado em `docs/mapeamento_funcionalidades.md`.
- Notificação automática de cobrança por e-mail ou mensagem.
- Autenticação própria para as pessoas do rateio: elas seguem sendo rótulos internos da conta.

## Decisions

### Classificação do tipo de lançamento vira função pura

O tipo deixa de ser um valor fixo escolhido no momento do registro e passa a ser derivado de três entradas: o mês de fatura da parcela, o mês corrente e a marcação de conta fixa recorrente. A derivação vira uma função pura no módulo de domínio, ao lado de `fatura_de` e `gerar_parcelas`, testável sem banco e sem servidor.

A precedência é deliberada: **a marcação explícita da pessoa vence a inferência por data.** Uma conta fixa lançada para um mês futuro é estimativa, não compromisso — quem sabe que aquilo é recorrente é a pessoa, não o calendário.

*Alternativa descartada:* classificar no momento da leitura, dentro do cálculo da previsão, comparando o mês do lançamento com a data de hoje. Foi descartada porque tornaria o tipo um valor volátil — o mesmo lançamento mudaria de classificação com a passagem do tempo, sem nada ter acontecido com ele, e o campo persistido continuaria mentindo.

### Renomear propaga em vez de cascatear

Como lançamentos guardam o nome e não o identificador, renomear sem propagar deixaria registros órfãos e quebraria o extrato da pessoa. A propagação acontece na mesma transação da renomeação: ou o nome muda em todo lugar, ou não muda em lugar nenhum.

*Alternativa descartada:* proibir a renomeação quando a pessoa já tiver lançamentos. Resolveria a integridade ao custo de tornar o requisito RF03 inútil justamente para quem já usa o sistema.

### Consulta de receita de mês inexistente devolve zero, não 404

A ausência de receita em um mês é o estado normal de qualquer mês ainda não configurado, não uma condição de erro. Devolver zero permite que a interface abra o campo em branco e a pessoa preencha; devolver 404 obrigaria a interface a tratar como erro aquilo que é o caso mais comum.

### O CSV é serializado e interpretado no domínio

Serialização e leitura das linhas ficam em um módulo de domínio próprio, puro, sem acesso a banco. As rotas apenas leem os lançamentos, entregam ao domínio e devolvem o resultado. Isso mantém o teste do formato — inclusive o da linha malformada — independente de banco e de autenticação.

### Importação parcial em vez de tudo-ou-nada por linha

Uma linha inválida não aborta o arquivo: as demais entram e a resposta relata o que foi rejeitado. Um arquivo cujo cabeçalho não corresponde ao formato, porém, é recusado por inteiro — nesse caso não há interpretação confiável de nenhuma linha.

## Risks / Trade-offs

| Risco | Mitigação |
|---|---|
| A propagação de nome altera muitos registros de uma vez e é a operação mais destrutiva deste change. | Executada em transação única, restrita à conta autenticada, e coberta por teste que verifica o extrato da pessoa antes e depois da renomeação. |
| A classificação por data é a regra mais fácil de implementar errado, porque só se manifesta em meses futuros. | O teste de API é escrito **antes** da implementação, a partir dos cenários do contrato, e falha enquanto a regra não existir — tornando a lacuna visível em vez de silenciosa. |
| A comparação com o "mês corrente" torna o resultado dependente da data de execução, o que fragiliza o teste. | O mês corrente entra como parâmetro explícito da função pura, nunca lido de dentro dela — o teste passa a data que quiser. |
| RF11 é o item de maior esforço e o menos crítico dos cinco. | Está deliberadamente por último no plano de tarefas e é o único item marcado como condicional ao tempo restante. |
| A referência por nome continua sendo a fragilidade estrutural do modelo. | Fora de escopo aqui, mas registrada explicitamente como dívida conhecida em Non-Goals para não ser confundida com esquecimento. |
