/**
 * Cliente HTTP da API do Fatura em Dia.
 *
 * Os caminhos são relativos à origem: em desenvolvimento o Vite faz proxy dos
 * prefixos da API para o backend (ver vite.config.js), e em produção o próprio
 * FastAPI serve o dist/ e a API na mesma origem. Não há CORS em nenhum dos dois.
 */
const BASE = import.meta.env.VITE_API_BASE ?? "";
const CHAVE_TOKEN = "fed.token";

function token() {
  return localStorage.getItem(CHAVE_TOKEN);
}

function guardarToken(t) {
  if (t) localStorage.setItem(CHAVE_TOKEN, t);
  else localStorage.removeItem(CHAVE_TOKEN);
}

async function req(metodo, caminho, corpo) {
  const headers = {};
  if (corpo !== undefined && !(corpo instanceof FormData)) headers["Content-Type"] = "application/json";
  const t = token();
  if (t) headers.Authorization = `Bearer ${t}`;

  const resp = await fetch(BASE + caminho, {
    method: metodo,
    headers,
    body: corpo instanceof FormData ? corpo : corpo !== undefined ? JSON.stringify(corpo) : undefined,
  });

  if (resp.status === 204) return null;

  const tipo = resp.headers.get("content-type") || "";
  let dados = null;
  if (tipo.includes("application/json")) {
    try { dados = await resp.json(); } catch { /* sem corpo */ }
  } else {
    dados = await resp.text();
  }

  if (!resp.ok) {
    const msg = (dados && (dados.detail || dados.message)) || `Erro ${resp.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return dados;
}

const get = (c) => req("GET", c);
const post = (c, b) => req("POST", c, b);
const put = (c, b) => req("PUT", c, b);
const patch = (c, b) => req("PATCH", c, b);
const del = (c) => req("DELETE", c);

export const API = {
  token,
  logout: () => guardarToken(null),

  // ---- autenticação ----
  registrar: (nome, email, senha) => post("/auth/registrar", { nome, email, senha }),
  async login(email, senha) {
    const r = await post("/auth/login", { email, senha });
    guardarToken(r.access_token);
    return r;
  },
  eu: () => get("/auth/eu"),

  // ---- configuração ----
  onboarding: (dados) => post("/onboarding", dados),

  pessoas: () => get("/pessoas"),
  criarPessoa: (nome) => post("/pessoas", { nome }),
  renomearPessoa: (id, nome) => put(`/pessoas/${id}`, { nome }),
  removerPessoa: (id) => del(`/pessoas/${id}`),

  cartoes: () => get("/cartoes"),
  criarCartao: (c) => post("/cartoes", c),
  atualizarCartao: (id, c) => put(`/cartoes/${id}`, c),
  removerCartao: (id) => del(`/cartoes/${id}`),

  categorias: () => get("/categorias"),
  criarCategoria: (nome) => post("/categorias", { nome }),
  renomearCategoria: (id, nome) => put(`/categorias/${id}`, { nome }),
  removerCategoria: (id) => del(`/categorias/${id}`),

  regras: () => get("/regras"),
  removerRegra: (id) => del(`/regras/${id}`),

  // ---- lançamentos ----
  sugestao: (descricao) => get(`/lancamentos/sugestao?descricao=${encodeURIComponent(descricao)}`),
  lancar: (dados) => post("/lancamentos", dados),
  lancamentos: (mes) => get("/lancamentos" + (mes ? `?mes=${mes}` : "")),
  atribuirDono: (id, pessoas) => patch(`/lancamentos/${id}/dono`, { pessoas }),
  removerLancamento: (id) => del(`/lancamentos/${id}`),

  // ---- CSV (RF11) ----
  exportarCsv: () => get("/lancamentos/exportar"),
  importarCsv: (arquivo) => {
    const fd = new FormData();
    fd.append("arquivo", arquivo);
    return post("/lancamentos/importar", fd);
  },

  // ---- painel / cobrança ----
  painel: (mes) => get(`/painel/${mes}`),
  previsao: (aPartirDe, meses = 6) => get(`/previsao?a_partir_de=${aPartirDe}&meses=${meses}`),
  extrato: (pessoa, mes) => get(`/extrato/${encodeURIComponent(pessoa)}/${mes}`),
  registrarPagamento: (dados) => post("/pagamentos", dados),
  pagamentos: (pessoa) => get("/pagamentos" + (pessoa ? `?pessoa=${encodeURIComponent(pessoa)}` : "")),

  // ---- receita ----
  receitas: () => get("/receitas"),
  receitaDoMes: (mes) => get(`/receitas/${mes}`),
  definirReceita: (dados) => put("/receitas", dados),
};
