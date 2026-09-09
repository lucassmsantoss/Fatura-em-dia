# Mapeamento de Funcionalidades — Caderneta → Projeto Final

Base: artefato "Caderneta do Lucas" (app de controle financeiro pessoal/compartilhado).
Objetivo: generalizar para qualquer usuário, com backend real (API REST) e onboarding de configuração.

Legenda: ✅ existe no artefato atual · ⚠️ existe mas está hardcoded/precisa generalizar · ❌ não existe, precisa criar.

## 1. Conta e acesso
| Item | Status | Observação |
|---|---|---|
| Login/cadastro de usuário | ❌ | Hoje é um usuário fixo ("Lucas"), sem senha nem conta. Precisa criar do zero. |
| Sessão/autenticação (token/JWT) | ❌ | Necessário para a API REST distinguir usuários. |
| Recuperação de senha | ❌ | Pode ficar fora do escopo mínimo (não é requisito do edital), mas conta como req. extra se der tempo. |
| Multi-usuário real (cada um com sua conta) | ❌ | Hoje "pessoas" é só uma lista de nomes dentro da config de UM usuário — não são contas de verdade. Decisão de escopo necessária (ver pergunta abaixo). |

## 2. Onboarding / Configuração inicial
| Item | Status | Observação |
|---|---|---|
| Wizard de primeiro acesso | ❌ | Hoje os dados vêm de um objeto `PADRAO` fixo no código. Precisa de um fluxo guiado: nome, receita, pessoas, cartões, categorias. |
| Cadastro de "pessoas" para dividir gastos | ⚠️ | Existe a lista, mas é hardcoded (Lucas, Bruna, Mãe...). Precisa virar CRUD. |
| Cadastro de cartões/contas de pagamento | ⚠️ | Existe (nome, cor, dia de fechamento, deslocamento de fatura) mas hardcoded. Precisa virar CRUD. |
| Cadastro/edição de categorias | ⚠️ | Lista fixa de categorias. Precisa virar CRUD (criar/editar/remover categoria). |
| Definir receita mensal | ✅ | Já existe tela em Ajustes (salário, caronas, outros), por mês. |

## 3. Lançamento de despesas (tela "Lançar")
| Item | Status | Observação |
|---|---|---|
| Registrar despesa (valor, descrição, data) | ✅ | Completo. |
| Escolher cartão/forma de pagamento | ✅ | Via chips. |
| Dividir entre pessoas (1 a 3) | ✅ | Rateio igualitário automático. |
| Parcelamento (1x a 48x) | ✅ | Gera um lançamento por parcela, distribuído nos meses seguintes. |
| Categorização manual | ✅ | Via chips. |
| Auto-categorização por regra de palavra-chave | ✅ | "Lembrar categoria e pessoas" cria regra nova. |
| Marcar como "conta fixa" (estimativa recorrente) | ✅ | Para aluguel, luz, internet — meses futuros. |
| Edição de lançamento já lançado | ⚠️ | Só dá pra editar tipo (aconteceu/compromisso/estimativa) e "dono" (pessoas). Não dá pra editar valor/descrição/categoria depois de lançado. |
| Excluir lançamento | ✅ | |

## 4. Painel / Dashboard
| Item | Status | Observação |
|---|---|---|
| Total do mês, "o que é seu", sobra/falta vs receita | ✅ | |
| Fita visual (aconteceu / compromisso / estimativa) | ✅ | |
| Fatura por cartão | ✅ | |
| Gastos por categoria (ranking) | ✅ | |
| Previsão dos próximos meses | ✅ | Usa uma tabela de `previsao` pré-calculada (dados históricos do Lucas) — **não é calculada dinamicamente**, é dado importado. Precisa decidir se vira cálculo real ou é descartada. |
| Alertas (estourou receita, gasto sem dono) | ✅ | |
| Resolver "sem dono" (atribuir pessoa depois) | ✅ | |

## 5. Cobrança entre pessoas (tela "Cobrar"/Extrato)
| Item | Status | Observação |
|---|---|---|
| Ver saldo devedor por pessoa | ✅ | |
| Saldo acumulado (meses anteriores) | ✅ | |
| Registrar pagamento recebido | ✅ (parcial) | Botão existe na tela, mas não vi o handler completo — precisa confirmar se está implementado ou é placeholder. |
| "Copiar cobrança" (gerar texto para mandar) | ✅ (parcial) | Mesma observação acima. |
| Notificar pessoa automaticamente (email/whatsapp) | ❌ | Não existe — hoje é manual ("copiar texto"). |

## 6. Dados e integração
| Item | Status | Observação |
|---|---|---|
| Exportar CSV | ✅ | |
| Importar CSV (colar da planilha) | ✅ | |
| Persistência | ⚠️ | Hoje é um truque: o próprio artefato se republica com o estado novo (`window.claude.use("artifact")`) + fallback em `localStorage`. **Isso precisa virar API REST + banco de dados de verdade** (decisão já tomada). |
| Multi-dispositivo/sincronização real | ❌ | Hoje é "salvo nesta página" — sem backend real, não sincroniza entre dispositivos de fato. |

## 7. Coisas que existem mas usam dados pessoais do Lucas (remover/generalizar)
- Nome fixo "Lucas", salário 4400, lista de pessoas da família dele.
- Tabela `previsao` com números reais das faturas dele até 2030.
- `regras` de categorização com nomes de lojas/serviços específicos dele (Superfácil, Queiroz, Wellhub Bruna, etc.).
- Título "Caderneta do Lucas" → precisa de nome de produto genérico.

## Perguntas em aberto para fechar o escopo

1. **Multi-usuário real ou "grupo fechado"?** O modelo atual tem 1 usuário logado ("eu") e uma lista de "pessoas" que só existem dentro da conta dele (elas não logam, não têm conta própria — é só rateio). Isso é suficiente pros 10 requisitos e é bem mais rápido de construir. A alternativa (cada pessoa do grupo com login próprio, vendo o mesmo grupo) é mais "correto" mas dobra a complexidade de autenticação/permissões. **Recomendo manter o modelo atual (1 conta, pessoas como "etiquetas" de rateio)** dado o prazo.
2. **Previsão de meses futuros**: vira um cálculo real (ex: média dos últimos meses, ou projeção simples de compromissos já lançados) ou fica fora do escopo do MVP?
3. **Registrar pagamento / copiar cobrança**: confirmar se ficam no escopo dos 10 requisitos ou são "bônus" se sobrar tempo.
4. **Nome do produto**: como vamos chamar a versão genérica? (ex: "Rateio", "DivideAí", "Contas em Dia" — pensamos juntos.)
