/* Cliente HTTP para a API do Fatura em Dia. */
const API = {
  base: (window.localStorage.getItem("fed.apiBase")) || "http://localhost:8000",

  token() { return window.localStorage.getItem("fed.token"); },
  setToken(t) { t ? localStorage.setItem("fed.token", t) : localStorage.removeItem("fed.token"); },

  async req(metodo, caminho, corpo) {
    const headers = { "Content-Type": "application/json" };
    const token = this.token();
    if (token) headers["Authorization"] = "Bearer " + token;
    const resp = await fetch(this.base + caminho, {
      method: metodo,
      headers,
      body: corpo !== undefined ? JSON.stringify(corpo) : undefined,
    });
    if (resp.status === 204) return null;
    let dados = null;
    try { dados = await resp.json(); } catch (e) { /* sem corpo */ }
    if (!resp.ok) {
      const msg = (dados && (dados.detail || dados.message)) || ("Erro " + resp.status);
      throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    }
    return dados;
  },

  get(caminho) { return this.req("GET", caminho); },
  post(caminho, corpo) { return this.req("POST", caminho, corpo); },
  put(caminho, corpo) { return this.req("PUT", caminho, corpo); },
  patch(caminho, corpo) { return this.req("PATCH", caminho, corpo); },
  del(caminho) { return this.req("DELETE", caminho); },

  // ---- autenticação ----
  registrar(nome, email, senha) { return this.post("/auth/registrar", { nome, email, senha }); },
  async login(email, senha) {
    const r = await this.post("/auth/login", { email, senha });
    this.setToken(r.access_token);
    return r;
  },
  eu() { return this.get("/auth/eu"); },
  logout() { this.setToken(null); },

  // ---- onboarding / configuração ----
  onboarding(dados) { return this.post("/onboarding", dados); },
  pessoas() { return this.get("/pessoas"); },
  criarPessoa(nome) { return this.post("/pessoas", { nome }); },
  removerPessoa(id) { return this.del(`/pessoas/${id}`); },
  cartoes() { return this.get("/cartoes"); },
  criarCartao(c) { return this.post("/cartoes", c); },
  atualizarCartao(id, c) { return this.put(`/cartoes/${id}`, c); },
  removerCartao(id) { return this.del(`/cartoes/${id}`); },
  categorias() { return this.get("/categorias"); },
  criarCategoria(nome) { return this.post("/categorias", { nome }); },
  removerCategoria(id) { return this.del(`/categorias/${id}`); },
  regras() { return this.get("/regras"); },
  removerRegra(id) { return this.del(`/regras/${id}`); },

  // ---- lançamentos ----
  sugestao(descricao) { return this.get("/lancamentos/sugestao?descricao=" + encodeURIComponent(descricao)); },
  lancar(dados) { return this.post("/lancamentos", dados); },
  lancamentos(mes) { return this.get("/lancamentos" + (mes ? `?mes=${mes}` : "")); },
  atualizarDono(id, pessoas) { return this.patch(`/lancamentos/${id}/dono`, { pessoas }); },
  removerLancamento(id) { return this.del(`/lancamentos/${id}`); },

  // ---- painel / extrato / pagamentos ----
  painel(mes) { return this.get(`/painel/${mes}`); },
  previsao(aPartirDe, meses) { return this.get(`/previsao?a_partir_de=${aPartirDe}&meses=${meses || 6}`); },
  extrato(pessoa, mes) { return this.get(`/extrato/${encodeURIComponent(pessoa)}/${mes}`); },
  registrarPagamento(dados) { return this.post("/pagamentos", dados); },
  pagamentos(pessoa) { return this.get("/pagamentos" + (pessoa ? `?pessoa=${encodeURIComponent(pessoa)}` : "")); },
  definirReceita(dados) { return this.put("/receitas", dados); },
};
