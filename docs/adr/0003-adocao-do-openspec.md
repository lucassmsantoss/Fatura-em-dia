# ADR 0003 — Adoção do OpenSpec como ferramenta de especificação

## Status
Aceito — substitui a decisão de formato registrada em `especificacao-inicial.md` no primeiro ciclo.

## Contexto

O edital exige "uso de uma ferramenta ou formato de spec estruturado (OpenSpec, GitHub Spec-Kit, Traycer.ai, ou um formato equivalente documentado pela dupla)" e pede que a escolha seja justificada.

No primeiro ciclo do projeto optamos por Markdown estruturado à mão, imitando o fluxo do OpenSpec. A justificativa registrada na época foi o prazo: "em vez de reconfigurar o tooling completo do OpenSpec". Duas coisas mudaram essa avaliação:

1. **O custo estimado estava errado.** A instalação e inicialização do OpenSpec levam menos de dois minutos e não exigem nenhuma configuração de infraestrutura. A premissa de que reconfigurar o tooling era caro não se sustentou quando medida.
2. **O formato à mão não tinha validação.** Sem ferramenta, nada garantia que os critérios de aceite estivessem completos ou consistentes. Na prática isso se confirmou: dos 10 requisitos funcionais, apenas 2 tinham critérios de aceite escritos, e a lacuna passou despercebida até uma revisão manual.

## Decisão

Adotar o **OpenSpec** (`@fission-ai/openspec`, versão 1.13.0) como ferramenta de especificação do projeto, com os artefatos escritos em português.

```bash
npm install -g @fission-ai/openspec@1.13.0
openspec init --tools claude --language "pt-BR"
```

A estrutura passa a ser:

- `openspec/specs/<capacidade>/spec.md` — o **contrato acordado**: o que o sistema deve fazer, organizado por capacidade em vez de por número de requisito. Na semântica do OpenSpec este diretório representa o estado corrente do sistema; neste projeto, em que a especificação precede a implementação, ele representa o alvo contra o qual o código é construído.
- `openspec/changes/<nome>/` — cada **mudança proposta**, com `proposal.md` (o quê e por quê), `design.md` (como e por que assim), `specs/` (os deltas de requisito) e `tasks.md` (o plano de execução).
- `.claude/skills/openspec-*` e `.claude/commands/opsx/*` — a integração com o agente de IA, gerada pela própria ferramenta.

O ciclo de vida de uma mudança é: propor → validar → implementar → arquivar. O arquivamento promove os deltas para os specs principais, mantendo `openspec/specs/` sempre igual ao sistema real.

## Alternativas consideradas

- **Manter o Markdown à mão.** Permitido pelo edital, e era o caminho de menor esforço imediato. Descartado porque não oferece validação: a lacuna de critérios de aceite que motivou esta decisão é exatamente o tipo de erro que uma ferramenta pega e um documento livre não pega.
- **GitHub Spec-Kit.** Também citado pelo edital. Descartado por não termos experiência prévia com ele — a dupla já havia usado OpenSpec em atividade anterior da disciplina, e adotar o conhecido reduz risco a dois dias da entrega.
- **Traycer.ai.** Descartado por ser serviço externo, o que adicionaria dependência de rede e de conta a um projeto que precisa rodar offline na demonstração.

## Detalhe de verificação

O pacote npm chamado apenas `openspec` **não** é esta ferramenta: é um pacote vazio de 2019, versão 0.0.0, sem executável. O pacote correto é `@fission-ai/openspec`. Registramos isso aqui porque instalar o nome óbvio não produz erro visível — apenas não instala nada.

A adoção foi verificada antes de ser documentada: a gramática dos artefatos foi conferida contra os templates da própria ferramenta, e a diferença entre spec principal (`## Requirements`) e delta de mudança (`## ADDED Requirements`) foi testada empiricamente. Usar o cabeçalho errado no spec principal **não gera erro** — a ferramenta simplesmente registra zero requisitos.

## Consequências

- **Positivo:** os critérios de aceite passam a ser validáveis por comando (`openspec validate --strict`); a cobertura deixa de depender de revisão manual; a estrutura por capacidade revelou que faltava especificar 8 dos 11 requisitos; a integração com o agente de IA vem pronta, o que reforça a evidência de harness.
- **Positivo:** o histórico de mudanças fica auditável — cada alteração de requisito tem proposta, desenho e plano versionados junto do código.
- **Negativo:** passa a existir uma dependência de Node.js para trabalhar nas specs, num projeto cujo runtime é Python. Aceitável: a dependência é só de autoria, não de execução — o sistema roda sem ela.
- **Negativo:** os documentos do primeiro ciclo (`especificacao-inicial.md`, `requisitos-funcionais.md`) passam a conviver com o `openspec/`. Eles são preservados como registro datado do primeiro ciclo, não como fonte da verdade; a fonte da verdade passa a ser `openspec/`.
- **Neutro:** a telemetria anônima do OpenSpec foi desativada (`OPENSPEC_TELEMETRY=0`) por ser um projeto acadêmico.
