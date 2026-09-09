# ADR 0001 — Backend com API REST separada do frontend

## Status
Aceito

## Contexto
O protótipo original ("Caderneta") era um único arquivo HTML/JS auto-contido, sem backend real: ele persistia estado reescrevendo a si mesmo. O edital do projeto final exige uma arquitetura com "contratos claros entre as partes do sistema (ex.: API bem definida entre front-end e back-end)" e modularidade/baixo acoplamento.

## Decisão
Vamos separar o sistema em duas partes com um contrato de API REST explícito entre elas:
- **Backend**: expõe endpoints REST (ex.: `/auth`, `/pessoas`, `/cartoes`, `/categorias`, `/lancamentos`, `/pagamentos`, `/painel/{mes}`) com banco de dados próprio (SQLite).
- **Frontend**: aplicação web que consome esses endpoints via HTTP/JSON.

## Alternativas consideradas
- **Manter tudo em um único arquivo front-end sem backend** (como o protótipo original): descartado por não atender ao critério de arquitetura do edital e por não suportar múltiplos usuários de forma real.
- **Backend monolítico servindo HTML renderizado no servidor**: descartado por não deixar tão explícito o contrato de API entre camadas, que é justamente o que o edital pede como evidência de arquitetura.

## Consequências
- Positivo: contrato de API é documentável (ex.: OpenAPI/Swagger automático), front e back podem ser desenvolvidos/testados de forma independente, e a separação facilita testes automatizados do backend isolados da interface.
- Negativo: mais tempo de setup do que o protótipo original de arquivo único — mitigado por reaproveitar a lógica de negócio já validada no protótipo (cálculo de ciclo de fatura, rateio, parcelamento).
