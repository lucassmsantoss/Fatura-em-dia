# ADR 0004 — Frontend em Vue 3 com Vite, no lugar de JavaScript puro sem build

## Status
Aceito — substitui a escolha de stack de frontend descrita no README do primeiro ciclo.

## Contexto

O frontend nasceu como uma SPA em JavaScript puro, sem etapa de build: três arquivos
(`index.html`, `css/estilo.css`, `js/app.js`) carregados diretamente pelo navegador. A escolha
foi deliberada e adequada ao início — zero configuração, zero dependências, e qualquer pessoa
abre o `index.html` e vê a aplicação.

Três coisas mudaram essa avaliação quando o backend ficou pronto:

1. **O arquivo cresceu para 492 linhas em um módulo só.** Todas as telas — autenticação,
   configuração inicial, lançamento, painel, cobrança e ajustes — conviviam no mesmo escopo,
   manipulando o DOM via `innerHTML` e reatribuindo `onclick` a cada redesenho. Cada tela nova
   aumentava a chance de uma quebrar a outra.

2. **Sobraram sete funcionalidades de interface para entregar de uma vez** — edição de pessoas,
   categorias e formas de pagamento, receita por mês, exportação e importação em CSV, e a opção
   de memorizar regra. Adicionar sete blocos ao mesmo arquivo, sob prazo, era o cenário em que
   o formato imperativo mais cobra.

3. **A renderização manual não tinha estado reativo.** Toda mudança exigia redesenhar a tela
   inteira e reanexar os manipuladores à mão. É a classe de código em que o erro não aparece no
   teste, e sim na demonstração.

## Decisão

Adotar **Vue 3** com **Vite** como ferramenta de build, mantendo a aplicação como SPA.

```bash
npm create vite@latest   # vue
npm install
npm run dev              # desenvolvimento, porta 5173
npm run build            # produção, gera frontend/dist/
```

A interface passa a ser composta por componentes de página (`src/views/`), com estado
compartilhado em um objeto `reactive` (`src/estado.js`) e o cliente HTTP isolado em
`src/api.js`.

**Vue e não React** porque é o framework de domínio da dupla — e, a dois dias da entrega,
usar a ferramenta conhecida reduz risco mais do que qualquer vantagem técnica compensaria.
A mesma lógica que escolheu OpenSpec em vez de Spec-Kit na ADR 0003.

**Sem Vuex ou Pinia.** O estado compartilhado cabe em um `reactive` de trinta linhas; um store
dedicado seria dependência sem contrapartida nesta escala.

### Como a aplicação é servida

Duas formas, deliberadamente:

- **Desenvolvimento** — `npm run dev` sobe o Vite na 5173 e faz *proxy* dos prefixos da API
  para o backend na 8000. Há recarga instantânea, e não há CORS porque o navegador só conversa
  com uma origem.
- **Demonstração e produção** — `npm run build` gera `frontend/dist/`, e o FastAPI o serve na
  mesma origem da API. Um processo só sobe tudo.

O detalhe que faz isso funcionar: o `StaticFiles` é montado em `/` **depois** de todos os
routers. O Starlette resolve rotas na ordem de registro, então todo caminho da API é atendido
pela API, e só o que sobra cai no SPA. O `mount` é condicional à existência de `dist/`, para
não quebrar o ambiente de desenvolvimento, onde ele não existe.

A API permaneceu na raiz (`/pessoas`, `/painel/...`) em vez de migrar para um prefixo `/api`.
Mover as rotas obrigaria a reescrever os caminhos das 152 provas do backend sem ganho de
comportamento — o custo do proxy enumerar os prefixos em `vite.config.js` é menor e está
documentado lá.

## Alternativas consideradas

- **Manter JavaScript puro e só adicionar o Vite.** Daria servidor de desenvolvimento e módulos
  ES sem framework. Descartada porque o problema central não era a ausência de build, e sim a
  renderização imperativa: o arquivo monolítico continuaria monolítico.
- **React.** Tecnicamente equivalente para este escopo. Descartada por ser o framework que a
  dupla menos usa — a dois dias da apresentação, a curva de aprendizado é risco puro.
- **Não mudar nada.** Era o caminho de menor risco imediato, e foi seriamente considerado: o
  sistema funcionava. Descartada porque as sete funcionalidades restantes seriam escritas de
  qualquer forma, e escrevê-las no formato antigo custaria quase o mesmo que a migração.

## Consequências

- **Positivo:** cada tela passa a ser um arquivo. As sete funcionalidades pendentes foram
  implementadas durante a migração, em componentes separados, sem risco de uma quebrar a outra.
- **Positivo:** o estado reativo elimina a classe inteira de bug de "redesenhei e esqueci de
  reanexar o manipulador".
- **Positivo:** a aplicação passa a ser servida em uma única origem também em produção, o que
  torna o `allow_origins=["*"]` do CORS desnecessário fora do desenvolvimento.
- **Negativo:** deixa de ser possível abrir o `index.html` direto no navegador. Passa a existir
  uma etapa de build, e com ela uma dependência de Node.js para *executar* a interface — não
  apenas para autoria, como era o caso do OpenSpec na ADR 0003.
- **Negativo:** `node_modules` e um `package-lock.json` entram no projeto. O lock é versionado;
  as dependências, não.
- **Risco assumido:** a demonstração passa a depender de um build bem-sucedido. Mitigado por
  gerar o `dist/` com antecedência e servi-lo pelo backend, em vez de depender do servidor de
  desenvolvimento no momento da apresentação.
