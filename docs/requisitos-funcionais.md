# Requisitos Funcionais — Fatura em Dia

> **Registro do primeiro ciclo de especificação (08/09).** Este documento é preservado como
> evidência datada de que os requisitos foram escritos antes do código — o commit que o
> criou (`6253069`) precede em 23 horas o commit do backend (`5a95687`), verificável por
> `git log --reverse`.
>
> **A fonte da verdade das specs passou a ser [`openspec/`](../openspec/)** a partir do segundo
> ciclo — ver [ADR 0003](adr/0003-adocao-do-openspec.md). Consulte lá o contrato vigente e os
> critérios de aceite completos; este arquivo não é mais atualizado.
>
> ### Rastreabilidade — requisito funcional para capacidade especificada
>
> | RF | Capacidade em `openspec/specs/` |
> |---|---|
> | RF01 | `autenticacao` |
> | RF02 | `configuracao-inicial` |
> | RF03, RF04, RF05 | `cadastros-de-apoio` |
> | RF06 | `lancamento-de-despesas` |
> | RF07 | `auto-categorizacao` |
> | RF08 | `painel-mensal` |
> | RF09 | `previsao-financeira` |
> | RF10 | `cobranca-entre-pessoas` |
> | RF11 | `importacao-exportacao-csv` (proposta em `openspec/changes/conformidade-rf/`) |


Base: protótipo "Caderneta" (ver `docs/mapeamento_funcionalidades.md` no projeto/histórico de planejamento), generalizado para múltiplos usuários independentes (cada um com sua própria conta e configuração — sem contas compartilhadas entre usuários).

## Escopo confirmado
- 1 usuário autenticado por conta (sem login para as "pessoas" do rateio — elas são apenas etiquetas dentro da conta do usuário).
- Previsão de meses futuros é **calculada dinamicamente** a partir de parcelamentos e contas fixas ("estimativas") já lançados — não é uma tabela importada.

## Lista de requisitos (mínimo 10 exigido pelo edital)

1. **RF01 — Cadastro e login de usuário.** O usuário cria uma conta (email/senha) e autentica para acessar seus dados.
2. **RF02 — Onboarding de configuração inicial.** No primeiro acesso, o usuário configura: nome, receita mensal, ao menos uma pessoa para rateio, ao menos um cartão/forma de pagamento e categorias.
3. **RF03 — CRUD de pessoas para rateio.** Criar, editar e remover pessoas que podem aparecer como participantes de uma despesa.
4. **RF04 — CRUD de cartões/formas de pagamento.** Criar, editar e remover cartões com nome, cor, dia de fechamento da fatura e deslocamento (quantos meses até a cobrança).
5. **RF05 — CRUD de categorias.** Criar, editar e remover categorias de despesa.
6. **RF06 — Lançamento de despesa.** Registrar uma despesa com valor, descrição, data, cartão, categoria, pessoas que dividem o valor e número de parcelas (1 a 48).
7. **RF07 — Auto-categorização por regra.** Ao lançar uma despesa cuja descrição contenha uma palavra-chave já conhecida, categoria e pessoas são sugeridas automaticamente; o usuário pode criar novas regras ao lançar.
8. **RF08 — Painel mensal (dashboard).** Exibir, para um mês selecionado: total gasto, valor que é do usuário, receita, sobra/falta, gastos por cartão e por categoria.
9. **RF09 — Previsão de meses futuros.** Calcular e exibir, para os próximos meses, o total já comprometido (parcelas futuras) e estimativas de contas fixas, sem depender de dados importados.
10. **RF10 — Extrato e cobrança por pessoa.** Para cada pessoa do rateio, mostrar quanto ela deve no mês e acumulado, e permitir registrar um pagamento recebido dela.

### Requisito bônus (se houver tempo)
11. **RF11 — Exportar/Importar CSV.** Exportar os lançamentos do usuário em CSV e importar lançamentos de um CSV no mesmo formato.

## Critérios de aceite (exemplos — Given/When/Then)

### RF06 — Lançamento de despesa
- **Cenário principal**
  - Dado que o usuário está autenticado e tem ao menos um cartão e uma pessoa cadastrados,
  - Quando ele informa valor R$ 300,00, descrição "Mercado", cartão "Cartão A", categoria "Mercado", 1 parcela e marca a si mesmo como pagador,
  - Então uma despesa de R$ 300,00 é criada no mês correspondente ao ciclo de fechamento do cartão, atribuída integralmente a ele.
- **Cenário de parcelamento**
  - Dado que o usuário lança uma despesa de R$ 1.200,00 em 4 parcelas,
  - Quando ele confirma o lançamento,
  - Então são criadas 4 despesas de R$ 300,00 cada, uma em cada um dos 4 meses seguintes ao mês de referência.
- **Caso de borda — valor inválido**
  - Dado que o usuário deixa o campo valor em branco ou com R$ 0,00,
  - Quando ele tenta confirmar o lançamento,
  - Então o sistema exibe um erro e não cria nenhuma despesa.

### RF09 — Previsão de meses futuros
- **Cenário principal**
  - Dado que existem parcelas futuras já lançadas (ex.: parcelas 2/4 e 3/4 de uma compra) e uma conta fixa marcada como estimativa recorrente,
  - Quando o usuário abre o painel de um mês futuro,
  - Então o sistema soma automaticamente as parcelas com vencimento naquele mês mais as estimativas recorrentes, sem exigir nenhum dado importado manualmente.
- **Caso de borda — mês sem nenhum lançamento futuro**
  - Dado que não há nenhuma parcela nem estimativa lançada para um mês futuro específico,
  - Quando o usuário seleciona esse mês no painel,
  - Então o sistema exibe previsão zerada, sem erro.

## Plano de tarefas (alto nível)

1. Modelagem do banco de dados (usuário, pessoa, cartão, categoria, regra, lançamento, pagamento).
2. API de autenticação (cadastro/login).
3. API de configuração (pessoas, cartões, categorias) — CRUD.
4. API de lançamentos (criar com parcelamento, listar, editar, remover).
5. Lógica de ciclo de fatura (fechamento + deslocamento) e cálculo de previsão futura.
6. API de rateio/extrato (saldo por pessoa, registrar pagamento).
7. Frontend: fluxo de onboarding.
8. Frontend: tela de lançamento.
9. Frontend: painel/dashboard.
10. Frontend: extrato/cobrança.
11. Testes automatizados (cálculo de fatura, rateio, parcelamento, previsão).
12. ADR + diagrama de arquitetura.
13. Documentação de ferramentas de IA e harness utilizados.
