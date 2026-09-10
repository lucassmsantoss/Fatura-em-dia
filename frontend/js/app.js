/* Fatura em Dia — SPA vanilla JS consumindo a API REST (ver js/api.js). */
"use strict";

const app = document.getElementById("app");
const navEl = document.getElementById("nav");

const estado = {
  tela: API.token() ? "carregando" : "login",
  usuario: null,
  pessoas: [], cartoes: [], categorias: [], regras: [],
  aba: "lancar",
  mesPainel: mesAtual(),
  pessoaExtrato: null,
  mesExtrato: mesAtual(),
  erro: "",
  flash: "",
};

function mesAtual() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
}
function hojeISO() {
  const d = new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}
function somaMes(mes, n) {
  const [a, m] = mes.split("-").map(Number);
  const idx = (m - 1) + n;
  const ano = a + Math.floor(idx / 12);
  const mesNovo = ((idx % 12) + 12) % 12 + 1;
  return ano + "-" + String(mesNovo).padStart(2, "0");
}
function mesRotulo(mes) {
  const MESES = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];
  const [a, m] = mes.split("-");
  return MESES[Number(m) - 1] + "/" + a.slice(2);
}
function brl(v) { return (v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" }); }
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

function mostrarErro(e) { estado.erro = (e && e.message) || String(e); render(); }
function mostrarFlash(msg) { estado.flash = msg; render(); setTimeout(() => { estado.flash = ""; render(); }, 3500); }

// ---------------- boot ----------------
async function iniciar() {
  if (API.token()) {
    try {
      estado.usuario = await API.eu();
      await carregarConfig();
      estado.tela = estado.usuario.onboarding_concluido ? "app" : "onboarding";
    } catch (e) {
      API.logout();
      estado.tela = "login";
    }
  }
  render();
}

async function carregarConfig() {
  [estado.pessoas, estado.cartoes, estado.categorias, estado.regras] = await Promise.all([
    API.pessoas(), API.cartoes(), API.categorias(), API.regras(),
  ]);
}

// ---------------- render raiz ----------------
function render() {
  navEl.hidden = estado.tela !== "app";
  if (estado.tela === "carregando") { app.innerHTML = "<p class='mini' style='margin-top:40px;text-align:center'>Carregando…</p>"; return; }
  if (estado.tela === "login") return renderLogin();
  if (estado.tela === "registro") return renderRegistro();
  if (estado.tela === "onboarding") return renderOnboarding();
  renderApp();
}

// ---------------- login / registro ----------------
function renderLogin() {
  app.innerHTML = `
    <div class="centro">
      <div class="topo" style="justify-content:center"><div class="marca">Fatura<span> em Dia</span></div></div>
      <div class="bloco">
        <h2>Entrar</h2>
        <div class="campo"><label>Email</label><input type="email" id="l-email"></div>
        <div class="campo"><label>Senha</label><input type="password" id="l-senha"></div>
        ${estado.erro ? `<p class="erro">${esc(estado.erro)}</p>` : ""}
        <div class="acoes"><button class="btn" id="b-entrar">Entrar</button></div>
        <p class="mini" style="margin-top:12px;text-align:center">Não tem conta? <button class="link" id="b-ir-registro">Criar conta</button></p>
      </div>
    </div>`;
  document.getElementById("b-entrar").onclick = async () => {
    estado.erro = "";
    const email = document.getElementById("l-email").value.trim();
    const senha = document.getElementById("l-senha").value;
    try {
      await API.login(email, senha);
      estado.usuario = await API.eu();
      await carregarConfig();
      estado.tela = estado.usuario.onboarding_concluido ? "app" : "onboarding";
      render();
    } catch (e) { mostrarErro(e); }
  };
  document.getElementById("b-ir-registro").onclick = () => { estado.erro = ""; estado.tela = "registro"; render(); };
}

function renderRegistro() {
  app.innerHTML = `
    <div class="centro">
      <div class="topo" style="justify-content:center"><div class="marca">Fatura<span> em Dia</span></div></div>
      <div class="bloco">
        <h2>Criar conta</h2>
        <div class="campo"><label>Nome</label><input type="text" id="r-nome"></div>
        <div class="campo"><label>Email</label><input type="email" id="r-email"></div>
        <div class="campo"><label>Senha (mínimo 6 caracteres)</label><input type="password" id="r-senha"></div>
        ${estado.erro ? `<p class="erro">${esc(estado.erro)}</p>` : ""}
        <div class="acoes"><button class="btn" id="b-criar">Criar conta</button></div>
        <p class="mini" style="margin-top:12px;text-align:center">Já tem conta? <button class="link" id="b-ir-login">Entrar</button></p>
      </div>
    </div>`;
  document.getElementById("b-criar").onclick = async () => {
    estado.erro = "";
    const nome = document.getElementById("r-nome").value.trim();
    const email = document.getElementById("r-email").value.trim();
    const senha = document.getElementById("r-senha").value;
    try {
      await API.registrar(nome, email, senha);
      await API.login(email, senha);
      estado.usuario = await API.eu();
      estado.tela = "onboarding";
      render();
    } catch (e) { mostrarErro(e); }
  };
  document.getElementById("b-ir-login").onclick = () => { estado.erro = ""; estado.tela = "login"; render(); };
}

// ---------------- onboarding ----------------
const rascunhoOnboarding = {
  pessoas: [],
  cartoes: [{ nome: "Cartão principal", cor: "#0E6F63", fecha: 0, desloca: 0 }],
  categorias: [],
  renda_principal: 0,
};

function renderOnboarding() {
  const r = rascunhoOnboarding;
  app.innerHTML = `
    <div class="topo"><div class="marca">Fatura<span> em Dia</span></div></div>
    <div class="bloco">
      <h2>Bem-vindo(a), ${esc(estado.usuario ? estado.usuario.nome : "")}</h2>
      <p class="mini">Vamos configurar rapidamente antes de começar. Isso leva menos de um minuto.</p>
    </div>

    <div class="bloco">
      <h2>Sua renda mensal</h2>
      <div class="campo"><label>Renda principal (R$)</label><input type="number" step="0.01" id="ob-renda" value="${r.renda_principal}"></div>
    </div>

    <div class="bloco">
      <h2>Pessoas para dividir despesas</h2>
      <p class="mini" style="margin-top:-6px">Inclua você mesmo(a) — use exatamente o nome "${esc(estado.usuario ? estado.usuario.nome : "")}" para que o painel calcule o que é seu.</p>
      <div class="chips" id="ob-pessoas" style="margin:10px 0">
        ${r.pessoas.map((p, i) => `<span class="chip" aria-pressed="true">${esc(p)} <button data-rm-pessoa="${i}" style="border:0;background:none;cursor:pointer">×</button></span>`).join("")}
      </div>
      <div class="acoes"><input type="text" id="ob-nova-pessoa" placeholder="Nome da pessoa"><button class="btn small" id="ob-add-pessoa">Adicionar</button></div>
    </div>

    <div class="bloco">
      <h2>Cartões / formas de pagamento</h2>
      ${r.cartoes.map((c, i) => `
        <div style="padding:8px 0;border-top:${i ? "1px solid var(--line)" : "0"}">
          <div class="dupla">
            <div class="campo"><label>Nome</label><input type="text" data-cartao-nome="${i}" value="${esc(c.nome)}"></div>
            <div class="campo"><label>Cor</label><input type="text" data-cartao-cor="${i}" value="${esc(c.cor)}"></div>
          </div>
          <div class="dupla">
            <div class="campo"><label>Fecha dia (0 = não se aplica)</label><input type="number" min="0" max="31" data-cartao-fecha="${i}" value="${c.fecha}"></div>
            <div class="campo"><label>Meses até a fatura</label><input type="number" min="0" max="2" data-cartao-desloca="${i}" value="${c.desloca}"></div>
          </div>
        </div>`).join("")}
      <button class="btn sec small" id="ob-add-cartao">+ Adicionar outro cartão</button>
    </div>

    <div class="bloco">
      <h2>Categorias de despesa</h2>
      <p class="mini" style="margin-top:-6px">Crie as categorias que fazem sentido para você — nada vem pronto.</p>
      <div class="chips" id="ob-categorias">
        ${r.categorias.map((c, i) => `<span class="chip" aria-pressed="true">${esc(c)} <button data-rm-cat="${i}" style="border:0;background:none;cursor:pointer">×</button></span>`).join("") || "<span class='mini'>Nenhuma categoria ainda.</span>"}
      </div>
      <div class="acoes" style="margin-top:10px"><input type="text" id="ob-nova-cat" placeholder="Ex.: Mercado"><button class="btn small" id="ob-add-cat">Adicionar</button></div>
    </div>

    ${estado.erro ? `<p class="erro">${esc(estado.erro)}</p>` : ""}
    <div class="acoes"><button class="btn" id="ob-concluir">Concluir configuração</button></div>
  `;

  document.getElementById("ob-add-pessoa").onclick = () => {
    const v = document.getElementById("ob-nova-pessoa").value.trim();
    if (v) { r.pessoas.push(v); renderOnboarding(); }
  };
  document.querySelectorAll("[data-rm-pessoa]").forEach(b => b.onclick = () => { r.pessoas.splice(+b.dataset.rmPessoa, 1); renderOnboarding(); });
  document.getElementById("ob-add-cat").onclick = () => {
    const v = document.getElementById("ob-nova-cat").value.trim();
    if (v) { r.categorias.push(v); renderOnboarding(); }
  };
  document.querySelectorAll("[data-rm-cat]").forEach(b => b.onclick = () => { r.categorias.splice(+b.dataset.rmCat, 1); renderOnboarding(); });
  document.getElementById("ob-add-cartao").onclick = () => { r.cartoes.push({ nome: "Novo cartão", cor: "#7C8987", fecha: 0, desloca: 0 }); renderOnboarding(); };
  document.querySelectorAll("[data-cartao-nome]").forEach(i => i.onchange = () => r.cartoes[+i.dataset.cartaoNome].nome = i.value);
  document.querySelectorAll("[data-cartao-cor]").forEach(i => i.onchange = () => r.cartoes[+i.dataset.cartaoCor].cor = i.value);
  document.querySelectorAll("[data-cartao-fecha]").forEach(i => i.onchange = () => r.cartoes[+i.dataset.cartaoFecha].fecha = +i.value || 0);
  document.querySelectorAll("[data-cartao-desloca]").forEach(i => i.onchange = () => r.cartoes[+i.dataset.cartaoDesloca].desloca = +i.value || 0);
  document.getElementById("ob-renda").onchange = e => r.renda_principal = +e.target.value || 0;

  document.getElementById("ob-concluir").onclick = async () => {
    estado.erro = "";
    if (!r.pessoas.length) { estado.erro = "Adicione ao menos uma pessoa (pode ser só você)."; render(); return; }
    if (!r.cartoes.length) { estado.erro = "Adicione ao menos um cartão/forma de pagamento."; render(); return; }
    try {
      await API.onboarding({ renda_principal: r.renda_principal, pessoas: r.pessoas, cartoes: r.cartoes, categorias: r.categorias });
      if (r.renda_principal > 0) await API.definirReceita({ mes: mesAtual(), renda_principal: r.renda_principal, renda_extra: 0 });
      estado.usuario.onboarding_concluido = true;
      await carregarConfig();
      estado.tela = "app";
      render();
    } catch (e) { mostrarErro(e); }
  };
}

// ---------------- app principal (abas) ----------------
function renderApp() {
  app.innerHTML = `
    <div class="topo">
      <div class="marca">Fatura<span> em Dia</span></div>
      <button class="link" id="b-sair">sair</button>
    </div>
    ${estado.flash ? `<div class="aviso verde">${esc(estado.flash)}</div>` : ""}
    ${estado.erro ? `<div class="aviso vermelho">${esc(estado.erro)}</div>` : ""}
    <div id="conteudo-aba"></div>
  `;
  document.getElementById("b-sair").onclick = () => { API.logout(); estado.tela = "login"; estado.usuario = null; render(); };
  pintarNav();
  const conteudo = document.getElementById("conteudo-aba");
  if (estado.aba === "lancar") return renderLancar(conteudo);
  if (estado.aba === "painel") return renderPainel(conteudo);
  if (estado.aba === "extrato") return renderExtrato(conteudo);
  if (estado.aba === "ajustes") return renderAjustes(conteudo);
}

function pintarNav() {
  const itens = [["lancar", "Lançar"], ["painel", "Painel"], ["extrato", "Cobrar"], ["ajustes", "Ajustes"]];
  navEl.innerHTML = `<div class="in">${itens.map(([id, rot]) =>
    `<button data-aba="${id}" aria-current="${estado.aba === id}">${rot}</button>`).join("")}</div>`;
  navEl.querySelectorAll("button").forEach(b => b.onclick = () => { estado.aba = b.dataset.aba; estado.erro = ""; render(); });
}

// ---------------- Lançar (RF06/RF07) ----------------
const formLancamento = novoFormLancamento();
function novoFormLancamento() {
  return { valor: "", descricao: "", cartao: "", categoria: "", pessoas: [], parcelas: 1, data: hojeISO(), estimativa: false };
}

function renderLancar(el) {
  const f = formLancamento;
  if (!f.cartao && estado.cartoes.length) f.cartao = estado.cartoes[0].nome;
  el.innerHTML = `
    <div class="bloco">
      <h2>Nova despesa</h2>
      <div class="campo"><label>Valor (R$)</label><input type="number" step="0.01" id="f-valor" value="${f.valor}"></div>
      <div class="campo"><label>Descrição</label><input type="text" id="f-desc" value="${esc(f.descricao)}" placeholder="Mercado, iFood, gasolina…"></div>
      <div class="campo"><label>Cartão</label><div class="chips" id="f-cartao">
        ${estado.cartoes.map(c => `<button class="chip" data-v="${esc(c.nome)}" aria-pressed="${f.cartao === c.nome}">${esc(c.nome)}</button>`).join("") || "<span class='mini'>Cadastre um cartão em Ajustes.</span>"}
      </div></div>
      <div class="campo"><label>Quem divide</label><div class="chips" id="f-pessoas">
        ${estado.pessoas.map(p => `<button class="chip" data-v="${esc(p.nome)}" aria-pressed="${f.pessoas.includes(p.nome)}">${esc(p.nome)}</button>`).join("") || "<span class='mini'>Cadastre pessoas em Ajustes.</span>"}
      </div></div>
      <div class="campo"><label>Categoria</label><div class="chips" id="f-categoria">
        ${estado.categorias.map(c => `<button class="chip" data-v="${esc(c.nome)}" aria-pressed="${f.categoria === c.nome}">${esc(c.nome)}</button>`).join("") || "<span class='mini'>Cadastre categorias em Ajustes.</span>"}
      </div></div>
      <div class="dupla">
        <div class="campo"><label>Data</label><input type="date" id="f-data" value="${f.data}"></div>
        <div class="campo"><label>Parcelas</label><input type="number" min="1" max="48" id="f-parcelas" value="${f.parcelas}"></div>
      </div>
      <label style="display:flex;gap:8px;align-items:center;margin-bottom:10px"><input type="checkbox" id="f-est" style="width:auto" ${f.estimativa ? "checked" : ""}> <span class="mini">É conta fixa recorrente (aluguel, luz, internet)</span></label>
      <div class="acoes"><button class="btn" id="f-gravar">Lançar</button><button class="btn sec" id="f-limpar">Limpar</button></div>
    </div>
    <div class="bloco"><h2>Últimos lançamentos</h2><div id="f-ultimos"></div></div>
  `;

  el.querySelector("#f-valor").oninput = e => f.valor = e.target.value;
  el.querySelector("#f-data").onchange = e => f.data = e.target.value;
  el.querySelector("#f-parcelas").onchange = e => f.parcelas = Math.max(1, Math.min(48, +e.target.value || 1));
  el.querySelector("#f-est").onchange = e => f.estimativa = e.target.checked;

  const descInput = el.querySelector("#f-desc");
  descInput.oninput = e => f.descricao = e.target.value;
  descInput.onblur = async () => {
    if (!f.descricao.trim()) return;
    try {
      const s = await API.sugestao(f.descricao.trim());
      if (s.categoria) f.categoria = s.categoria;
      if (s.pessoas && s.pessoas.length) f.pessoas = s.pessoas.slice();
      if (s.chave_encontrada) renderLancar(el);
    } catch (e) { /* silencioso */ }
  };

  el.querySelectorAll("#f-cartao [data-v]").forEach(b => b.onclick = () => { f.cartao = b.dataset.v; renderLancar(el); });
  el.querySelectorAll("#f-categoria [data-v]").forEach(b => b.onclick = () => { f.categoria = (f.categoria === b.dataset.v ? "" : b.dataset.v); renderLancar(el); });
  el.querySelectorAll("#f-pessoas [data-v]").forEach(b => b.onclick = () => {
    const v = b.dataset.v, i = f.pessoas.indexOf(v);
    if (i >= 0) f.pessoas.splice(i, 1); else f.pessoas.push(v);
    renderLancar(el);
  });

  el.querySelector("#f-limpar").onclick = () => { Object.assign(f, novoFormLancamento()); renderLancar(el); };
  el.querySelector("#f-gravar").onclick = async () => {
    estado.erro = "";
    const valor = parseFloat(String(f.valor).replace(",", "."));
    if (!(valor > 0)) { estado.erro = "Digite o valor da compra."; render(); return; }
    if (!f.descricao.trim()) { estado.erro = "Diga o que foi a compra."; render(); return; }
    if (!f.cartao) { estado.erro = "Escolha um cartão."; render(); return; }
    try {
      await API.lancar({
        valor, descricao: f.descricao.trim(), data: f.data, cartao: f.cartao,
        categoria: f.categoria, pessoas: f.pessoas, parcelas: f.parcelas,
        estimativa: f.estimativa, salvar_regra: true,
      });
      Object.assign(f, novoFormLancamento());
      mostrarFlash("Lançado com sucesso.");
      carregarUltimos(el);
    } catch (e) { mostrarErro(e); }
  };

  carregarUltimos(el);
}

async function carregarUltimos(el) {
  try {
    const ls = await API.lancamentos();
    const alvo = el.querySelector("#f-ultimos");
    if (!alvo) return;
    const ultimos = ls.slice(0, 6);
    alvo.innerHTML = ultimos.length ? ultimos.map(itemLancamentoHTML).join("") : "<p class='vazio'>Nada lançado ainda.</p>";
  } catch (e) { /* silencioso */ }
}

function itemLancamentoHTML(l) {
  return `<div class="item"><div class="txt">
    <div class="tt">${esc(l.descricao)}</div>
    <div class="sub"><span class="tag">${esc(l.cartao)}</span>${l.parcela ? `<span class="tag">${esc(l.parcela)}</span>` : ""}<span>${esc(l.categoria || "—")}</span>
      ${l.pessoas.length ? `<span class="tag verde">${esc(l.pessoas.join(" + "))}</span>` : `<span class="tag amarelo">sem dono</span>`}
    </div></div><div class="vv">${brl(l.valor)}</div></div>`;
}

// ---------------- Painel (RF08/RF09) ----------------
async function renderPainel(el) {
  el.innerHTML = "<p class='mini'>Carregando painel…</p>";
  try {
    const [painel, previsao] = await Promise.all([API.painel(estado.mesPainel), API.previsao(estado.mesPainel, 6)]);
    const meses = mesesParaSeletor();
    el.innerHTML = `
      <div class="campo"><select id="p-mes">${meses.map(m => `<option value="${m}" ${m === estado.mesPainel ? "selected" : ""}>${mesRotulo(m)}</option>`).join("")}</select></div>
      <div class="bloco">
        <h2>O mês de ${mesRotulo(painel.mes)}</h2>
        <div class="par"><span>Total do mês</span><b>${brl(painel.total_mes)}</b></div>
        <div class="par"><span>O que é seu</span><b>${brl(painel.meu_total)}</b></div>
        <div class="par"><span>Sua receita</span><b>${brl(painel.receita_total)}</b></div>
        <div class="par forte"><span>${painel.sobra_ou_falta >= 0 ? "Sobra" : "Falta"}</span><b style="color:${painel.sobra_ou_falta >= 0 ? "var(--accent)" : "var(--alert)"}">${brl(Math.abs(painel.sobra_ou_falta))}</b></div>
        ${painel.sem_dono > 0.004 ? `<div class="aviso amarelo" style="margin-top:10px">${brl(painel.sem_dono)} ainda sem dono neste mês.</div>` : ""}
      </div>
      <div class="bloco"><h2>Quem te deve</h2>
        ${painel.saldos_por_pessoa.length ? painel.saldos_por_pessoa.map(s => `
          <div class="item"><div class="txt"><div class="tt">${esc(s.pessoa)}</div><div class="sub"><span>no mês ${brl(s.devido_no_mes)}</span>${s.pago_no_mes ? `<span class="tag verde">pagou ${brl(s.pago_no_mes)}</span>` : ""}</div></div>
          <div class="vv">${brl(s.acumulado)}</div></div>`).join("") : "<p class='vazio'>Ninguém deve nada neste mês.</p>"}
      </div>
      <div class="bloco"><h2>Onde foi o seu dinheiro</h2>
        ${painel.gastos_por_categoria.length ? painel.gastos_por_categoria.map(c => `<div class="par"><span>${esc(c.categoria)}</span><b>${brl(c.valor)}</b></div>`).join("") : "<p class='vazio'>Sem gastos seus neste mês.</p>"}
      </div>
      <div class="bloco"><h2>O que vem pela frente</h2>
        ${previsao.map(p => `<div class="par"><span>${mesRotulo(p.mes)}</span><b>${brl(p.total_previsto)}</b></div>`).join("")}
        <p class="mini" style="margin-top:8px">Soma parcelas já contratadas (compromisso) + contas fixas recorrentes (estimativa) já lançadas — calculado dinamicamente, sem dado importado.</p>
      </div>
    `;
    el.querySelector("#p-mes").onchange = e => { estado.mesPainel = e.target.value; renderPainel(el); };
  } catch (e) { mostrarErro(e); }
}

function mesesParaSeletor() {
  const base = mesAtual();
  const arr = [];
  for (let i = -3; i <= 12; i++) arr.push(somaMes(base, i));
  return arr;
}

// ---------------- Extrato / Cobrar (RF10) ----------------
async function renderExtrato(el) {
  if (!estado.pessoaExtrato) {
    const outras = estado.pessoas.filter(p => !estado.usuario || p.nome !== estado.usuario.nome);
    estado.pessoaExtrato = outras.length ? outras[0].nome : (estado.pessoas[0] && estado.pessoas[0].nome);
  }
  if (!estado.pessoaExtrato) { el.innerHTML = "<div class='bloco'><p class='vazio'>Cadastre pessoas em Ajustes para usar a cobrança.</p></div>"; return; }

  el.innerHTML = "<p class='mini'>Carregando…</p>";
  try {
    const dados = await API.extrato(estado.pessoaExtrato, estado.mesExtrato);
    const meses = mesesParaSeletor();
    el.innerHTML = `
      <div class="chips" id="ex-pessoas" style="margin-bottom:12px">
        ${estado.pessoas.map(p => `<button class="chip" data-v="${esc(p.nome)}" aria-pressed="${p.nome === estado.pessoaExtrato}">${esc(p.nome)}</button>`).join("")}
      </div>
      <div class="campo"><select id="ex-mes">${meses.map(m => `<option value="${m}" ${m === estado.mesExtrato ? "selected" : ""}>${mesRotulo(m)}</option>`).join("")}</select></div>
      <div class="bloco">
        <h2>${esc(estado.pessoaExtrato)} · ${mesRotulo(estado.mesExtrato)}</h2>
        <div class="par"><span>Gastos deste mês</span><b>${brl(dados.devido_no_mes)}</b></div>
        <div class="par"><span>Já pagou (no mês)</span><b>${brl(dados.pago_no_mes)}</b></div>
        <div class="par forte"><span>Total a receber (acumulado)</span><b style="color:${dados.acumulado > 0.004 ? "var(--accent)" : "var(--ink3)"}">${brl(dados.acumulado)}</b></div>
        <div class="acoes" style="margin-top:12px">
          <input type="number" step="0.01" id="ex-valor-pagto" placeholder="Valor recebido">
          <button class="btn" id="ex-registrar">Registrar pagamento</button>
        </div>
      </div>
    `;
    el.querySelectorAll("#ex-pessoas [data-v]").forEach(b => b.onclick = () => { estado.pessoaExtrato = b.dataset.v; renderExtrato(el); });
    el.querySelector("#ex-mes").onchange = e => { estado.mesExtrato = e.target.value; renderExtrato(el); };
    el.querySelector("#ex-registrar").onclick = async () => {
      const valor = parseFloat(el.querySelector("#ex-valor-pagto").value);
      if (!(valor > 0)) { mostrarErro(new Error("Informe um valor válido.")); return; }
      try {
        await API.registrarPagamento({ pessoa: estado.pessoaExtrato, valor, data: hojeISO(), mes_ref: estado.mesExtrato });
        mostrarFlash("Pagamento registrado.");
        renderExtrato(el);
      } catch (e) { mostrarErro(e); }
    };
  } catch (e) { mostrarErro(e); }
}

// ---------------- Ajustes (RF03/RF04/RF05) ----------------
async function renderAjustes(el) {
  el.innerHTML = `
    <div class="bloco"><h2>Pessoas</h2>
      <div id="aj-pessoas"></div>
      <div class="acoes" style="margin-top:10px"><input type="text" id="aj-nova-pessoa" placeholder="Nome"><button class="btn small" id="aj-add-pessoa">Adicionar</button></div>
    </div>
    <div class="bloco"><h2>Cartões</h2><div id="aj-cartoes"></div></div>
    <div class="bloco"><h2>Categorias</h2>
      <div id="aj-categorias"></div>
      <div class="acoes" style="margin-top:10px"><input type="text" id="aj-nova-cat" placeholder="Nome"><button class="btn small" id="aj-add-cat">Adicionar</button></div>
    </div>
    <div class="bloco"><h2>Regras de auto-categorização</h2><div id="aj-regras"></div></div>
  `;
  renderListaPessoas(el);
  renderListaCartoes(el);
  renderListaCategorias(el);
  renderListaRegras(el);

  el.querySelector("#aj-add-pessoa").onclick = async () => {
    const v = el.querySelector("#aj-nova-pessoa").value.trim();
    if (!v) return;
    await API.criarPessoa(v); estado.pessoas = await API.pessoas(); renderListaPessoas(el);
  };
  el.querySelector("#aj-add-cat").onclick = async () => {
    const v = el.querySelector("#aj-nova-cat").value.trim();
    if (!v) return;
    await API.criarCategoria(v); estado.categorias = await API.categorias(); renderListaCategorias(el);
  };
}

function renderListaPessoas(el) {
  const alvo = el.querySelector("#aj-pessoas");
  alvo.innerHTML = estado.pessoas.map(p => `<div class="item"><div class="txt tt">${esc(p.nome)}</div><button class="chip small" data-rm="${p.id}">remover</button></div>`).join("") || "<p class='vazio'>Nenhuma pessoa cadastrada.</p>";
  alvo.querySelectorAll("[data-rm]").forEach(b => b.onclick = async () => { await API.removerPessoa(+b.dataset.rm); estado.pessoas = await API.pessoas(); renderListaPessoas(el); });
}
function renderListaCategorias(el) {
  const alvo = el.querySelector("#aj-categorias");
  alvo.innerHTML = estado.categorias.map(c => `<div class="item"><div class="txt tt">${esc(c.nome)}</div><button class="chip small" data-rm="${c.id}">remover</button></div>`).join("") || "<p class='vazio'>Nenhuma categoria cadastrada.</p>";
  alvo.querySelectorAll("[data-rm]").forEach(b => b.onclick = async () => { await API.removerCategoria(+b.dataset.rm); estado.categorias = await API.categorias(); renderListaCategorias(el); });
}
function renderListaCartoes(el) {
  const alvo = el.querySelector("#aj-cartoes");
  alvo.innerHTML = estado.cartoes.map(c => `
    <div style="padding:9px 0;border-top:1px solid var(--line)">
      <div class="par"><span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${esc(c.cor)};margin-right:7px"></i>${esc(c.nome)}</span>
      <button class="chip small" data-rm="${c.id}">remover</button></div>
      <div class="mini">fecha dia ${c.fecha || "—"} · ${c.desloca} mês(es) até a fatura</div>
    </div>`).join("") || "<p class='vazio'>Nenhum cartão cadastrado.</p>";
  alvo.querySelectorAll("[data-rm]").forEach(b => b.onclick = async () => { await API.removerCartao(+b.dataset.rm); estado.cartoes = await API.cartoes(); renderListaCartoes(el); });
}
function renderListaRegras(el) {
  const alvo = el.querySelector("#aj-regras");
  alvo.innerHTML = estado.regras.map(r => `
    <div class="item"><div class="txt"><div class="tt">${esc(r.chave)}</div><div class="sub"><span class="tag">${esc(r.categoria || "—")}</span>${r.pessoas.length ? `<span class="tag verde">${esc(r.pessoas.join(" + "))}</span>` : ""}</div></div>
    <button class="chip small" data-rm="${r.id}">remover</button></div>`).join("") || "<p class='vazio'>Nenhuma regra ainda — elas são criadas automaticamente ao lançar despesas.</p>";
  alvo.querySelectorAll("[data-rm]").forEach(b => b.onclick = async () => { await API.removerRegra(+b.dataset.rm); estado.regras = await API.regras(); renderListaRegras(el); });
}

iniciar();
