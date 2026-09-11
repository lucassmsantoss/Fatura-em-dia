<script setup>
import { onMounted, ref, watch } from "vue";
import { API } from "../api.js";
import { estado, carregarConfig, mostrarErro, mostrarFlash } from "../estado.js";
import { brl, mesAtual, mesRotulo, mesesParaSeletor } from "../formato.js";

// ---------- edição inline (tasks 2.6 e 2.7) ----------
// Renomear pessoa ou categoria propaga o novo nome para lançamentos, regras e
// pagamentos no backend, em transação única. Por isso a edição aqui é uma
// operação só, e não "remover e criar de novo" — que órfanaria o histórico.
const editando = ref(null); // { tipo: 'pessoa'|'categoria', id, nome }
const novaPessoa = ref("");
const novaCategoria = ref("");

function iniciarEdicao(tipo, item) {
  editando.value = { tipo, id: item.id, nome: item.nome };
}

async function salvarEdicao() {
  const { tipo, id, nome } = editando.value;
  const limpo = nome.trim();
  if (!limpo) return;
  try {
    if (tipo === "pessoa") await API.renomearPessoa(id, limpo);
    else await API.renomearCategoria(id, limpo);
    editando.value = null;
    await carregarConfig();
    mostrarFlash("Nome atualizado em todo o histórico.");
  } catch (e) { mostrarErro(e); }
}

async function acao(fn, mensagem) {
  try {
    await fn();
    await carregarConfig();
    if (mensagem) mostrarFlash(mensagem);
  } catch (e) { mostrarErro(e); }
}

// ---------- formas de pagamento (task 2.6) ----------
const cartaoEditando = ref(null);
const cartaoNovo = ref(null);

function novoCartao() {
  cartaoNovo.value = { nome: "", cor: "#0E6F63", fecha: 0, desloca: 0 };
}

async function salvarCartaoNovo() {
  if (!cartaoNovo.value.nome.trim()) return;
  await acao(() => API.criarCartao({ ...cartaoNovo.value, nome: cartaoNovo.value.nome.trim() }), "Forma de pagamento criada.");
  cartaoNovo.value = null;
}

async function salvarCartaoEditado() {
  const c = cartaoEditando.value;
  if (!c.nome.trim()) return;
  await acao(() => API.atualizarCartao(c.id, {
    nome: c.nome.trim(), cor: c.cor, fecha: c.fecha, desloca: c.desloca,
  }), "Forma de pagamento atualizada.");
  cartaoEditando.value = null;
}

// ---------- receita do mês (task 5.4) ----------
const mesesReceita = mesesParaSeletor();
const mesReceita = ref(mesAtual());
const receita = ref({ renda_principal: 0, renda_extra: 0 });
const historico = ref([]);

async function carregarReceita() {
  try {
    const r = await API.receitaDoMes(mesReceita.value);
    receita.value = { renda_principal: r.renda_principal, renda_extra: r.renda_extra };
  } catch (e) { mostrarErro(e); }
}

async function carregarHistorico() {
  try { historico.value = await API.receitas(); } catch { /* silencioso */ }
}

async function salvarReceita() {
  try {
    await API.definirReceita({
      mes: mesReceita.value,
      renda_principal: Number(receita.value.renda_principal) || 0,
      renda_extra: Number(receita.value.renda_extra) || 0,
    });
    await carregarHistorico();
    mostrarFlash(`Receita de ${mesRotulo(mesReceita.value)} salva.`);
  } catch (e) { mostrarErro(e); }
}

// ---------- CSV (task 8.3) ----------
const arquivoCsv = ref(null);
const relatorioImportacao = ref(null);

async function exportar() {
  try {
    const texto = await API.exportarCsv();
    const url = URL.createObjectURL(new Blob([texto], { type: "text/csv;charset=utf-8" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = "lancamentos.csv";
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) { mostrarErro(e); }
}

async function importar(evento) {
  const arquivo = evento.target.files?.[0];
  if (!arquivo) return;
  relatorioImportacao.value = null;
  try {
    relatorioImportacao.value = await API.importarCsv(arquivo);
    mostrarFlash(`${relatorioImportacao.value.importados} lançamento(s) importado(s).`);
  } catch (e) {
    mostrarErro(e);
  } finally {
    evento.target.value = "";
  }
}

watch(mesReceita, carregarReceita);
onMounted(() => { carregarReceita(); carregarHistorico(); });
</script>

<template>
  <!-- RECEITA DO MÊS (task 5.4) -->
  <div class="bloco">
    <h2>Receita do mês</h2>
    <div class="campo">
      <label for="aj-mes-receita">Mês</label>
      <select id="aj-mes-receita" v-model="mesReceita">
        <option v-for="m in mesesReceita" :key="m" :value="m">{{ mesRotulo(m) }}</option>
      </select>
    </div>
    <div class="dupla">
      <div class="campo"><label>Renda principal (R$)</label>
        <input id="aj-renda-principal" v-model="receita.renda_principal" type="number" step="0.01" /></div>
      <div class="campo"><label>Renda extra (R$)</label>
        <input id="aj-renda-extra" v-model="receita.renda_extra" type="number" step="0.01" /></div>
    </div>
    <div class="acoes"><button id="aj-salvar-receita" class="btn small" @click="salvarReceita">Salvar receita</button></div>

    <template v-if="historico.length">
      <p class="mini" style="margin-top:14px">Meses já registrados</p>
      <div v-for="r in historico" :key="r.mes" class="par">
        <span>{{ mesRotulo(r.mes) }}</span><b>{{ brl(r.renda_principal + r.renda_extra) }}</b>
      </div>
    </template>
    <p v-else class="mini" style="margin-top:12px">Nenhum mês com receita registrada ainda.</p>
  </div>

  <!-- PESSOAS (tasks 2.7) -->
  <div class="bloco">
    <h2>Pessoas</h2>
    <div id="aj-pessoas">
      <div v-for="p in estado.pessoas" :key="p.id" class="item">
        <template v-if="editando?.tipo === 'pessoa' && editando.id === p.id">
          <input v-model="editando.nome" type="text" @keyup.enter="salvarEdicao" />
          <button class="chip small" @click="salvarEdicao">salvar</button>
          <button class="chip small" @click="editando = null">cancelar</button>
        </template>
        <template v-else>
          <div class="txt tt">{{ p.nome }}</div>
          <button class="chip small" @click="iniciarEdicao('pessoa', p)">editar</button>
          <button class="chip small" @click="acao(() => API.removerPessoa(p.id))">remover</button>
        </template>
      </div>
      <p v-if="!estado.pessoas.length" class="vazio">Nenhuma pessoa cadastrada.</p>
    </div>
    <div class="acoes" style="margin-top:10px">
      <input id="aj-nova-pessoa" v-model="novaPessoa" type="text" placeholder="Nome"
             @keyup.enter="novaPessoa.trim() && acao(() => API.criarPessoa(novaPessoa.trim())).then(() => (novaPessoa = ''))" />
      <button id="aj-add-pessoa" class="btn small"
              @click="novaPessoa.trim() && acao(() => API.criarPessoa(novaPessoa.trim())).then(() => (novaPessoa = ''))">
        Adicionar
      </button>
    </div>
  </div>

  <!-- FORMAS DE PAGAMENTO (task 2.6) -->
  <div class="bloco">
    <h2>Formas de pagamento</h2>
    <div id="aj-cartoes">
      <div v-for="c in estado.cartoes" :key="c.id" style="padding:9px 0;border-top:1px solid var(--line)">
        <template v-if="cartaoEditando?.id === c.id">
          <div class="campo"><label>Nome</label><input v-model="cartaoEditando.nome" type="text" /></div>
          <div class="dupla">
            <div class="campo"><label>Fecha no dia</label><input v-model.number="cartaoEditando.fecha" type="number" min="0" max="31" /></div>
            <div class="campo"><label>Meses até cobrar</label><input v-model.number="cartaoEditando.desloca" type="number" min="0" max="6" /></div>
          </div>
          <div class="campo"><label>Cor</label><input v-model="cartaoEditando.cor" type="color" /></div>
          <button class="chip small" @click="salvarCartaoEditado">salvar</button>
          <button class="chip small" @click="cartaoEditando = null">cancelar</button>
        </template>
        <template v-else>
          <div class="par">
            <span>
              <i :style="{ display:'inline-block', width:'9px', height:'9px', borderRadius:'50%', background:c.cor, marginRight:'7px' }"></i>
              {{ c.nome }}
            </span>
            <span>
              <button class="chip small" @click="cartaoEditando = { ...c }">editar</button>
              <button class="chip small" @click="acao(() => API.removerCartao(c.id))">remover</button>
            </span>
          </div>
          <div class="mini">fecha dia {{ c.fecha || "—" }} · {{ c.desloca }} mês(es) até a fatura</div>
        </template>
      </div>
      <p v-if="!estado.cartoes.length" class="vazio">Nenhuma forma de pagamento cadastrada.</p>
    </div>

    <div v-if="cartaoNovo" style="padding-top:10px;border-top:1px solid var(--line);margin-top:10px">
      <div class="campo"><label>Nome</label><input id="aj-novo-cartao-nome" v-model="cartaoNovo.nome" type="text" placeholder="Ex.: Cartão Nubank" /></div>
      <div class="dupla">
        <div class="campo"><label>Fecha no dia</label><input v-model.number="cartaoNovo.fecha" type="number" min="0" max="31" /></div>
        <div class="campo"><label>Meses até cobrar</label><input v-model.number="cartaoNovo.desloca" type="number" min="0" max="6" /></div>
      </div>
      <div class="campo"><label>Cor</label><input v-model="cartaoNovo.cor" type="color" /></div>
      <button class="btn small" @click="salvarCartaoNovo">Salvar</button>
      <button class="chip small" @click="cartaoNovo = null">cancelar</button>
    </div>
    <div v-else class="acoes" style="margin-top:10px">
      <button id="aj-add-cartao" class="btn sec small" @click="novoCartao">+ Adicionar forma de pagamento</button>
    </div>
  </div>

  <!-- CATEGORIAS (task 2.7) -->
  <div class="bloco">
    <h2>Categorias</h2>
    <div id="aj-categorias">
      <div v-for="c in estado.categorias" :key="c.id" class="item">
        <template v-if="editando?.tipo === 'categoria' && editando.id === c.id">
          <input v-model="editando.nome" type="text" @keyup.enter="salvarEdicao" />
          <button class="chip small" @click="salvarEdicao">salvar</button>
          <button class="chip small" @click="editando = null">cancelar</button>
        </template>
        <template v-else>
          <div class="txt tt">{{ c.nome }}</div>
          <button class="chip small" @click="iniciarEdicao('categoria', c)">editar</button>
          <button class="chip small" @click="acao(() => API.removerCategoria(c.id))">remover</button>
        </template>
      </div>
      <p v-if="!estado.categorias.length" class="vazio">Nenhuma categoria cadastrada.</p>
    </div>
    <div class="acoes" style="margin-top:10px">
      <input id="aj-nova-cat" v-model="novaCategoria" type="text" placeholder="Ex.: Mercado"
             @keyup.enter="novaCategoria.trim() && acao(() => API.criarCategoria(novaCategoria.trim())).then(() => (novaCategoria = ''))" />
      <button id="aj-add-cat" class="btn small"
              @click="novaCategoria.trim() && acao(() => API.criarCategoria(novaCategoria.trim())).then(() => (novaCategoria = ''))">
        Adicionar
      </button>
    </div>
  </div>

  <!-- REGRAS -->
  <div class="bloco">
    <h2>Regras de auto-categorização</h2>
    <div id="aj-regras">
      <div v-for="r in estado.regras" :key="r.id" class="item">
        <div class="txt">
          <div class="tt">{{ r.chave }}</div>
          <div class="sub">
            <span class="tag">{{ r.categoria || "—" }}</span>
            <span v-if="r.pessoas.length" class="tag verde">{{ r.pessoas.join(" + ") }}</span>
          </div>
        </div>
        <button class="chip small" @click="acao(() => API.removerRegra(r.id))">remover</button>
      </div>
      <p v-if="!estado.regras.length" class="vazio">
        Nenhuma regra ainda — marque "memorizar" ao lançar uma despesa para criar uma.
      </p>
    </div>
  </div>

  <!-- CSV (task 8.3) -->
  <div class="bloco">
    <h2>Exportar e importar (CSV)</h2>
    <p class="mini" style="margin-top:-6px">
      Leve seus lançamentos para fora do sistema, ou traga de volta um arquivo no mesmo formato.
    </p>
    <div class="acoes" style="margin-top:10px">
      <button id="aj-exportar-csv" class="btn sec small" @click="exportar">Exportar lançamentos</button>
      <label class="btn sec small" style="cursor:pointer">
        Importar arquivo
        <input ref="arquivoCsv" type="file" accept=".csv,text/csv" style="display:none" @change="importar" />
      </label>
    </div>

    <div v-if="relatorioImportacao" style="margin-top:12px">
      <div class="par"><span>Importados</span><b>{{ relatorioImportacao.importados }}</b></div>
      <template v-if="relatorioImportacao.rejeitados.length">
        <p class="mini" style="margin-top:8px">Linhas recusadas</p>
        <div v-for="r in relatorioImportacao.rejeitados" :key="r.linha" class="par">
          <span>linha {{ r.linha }}</span><span class="mini">{{ r.motivo }}</span>
        </div>
      </template>
      <p v-else class="mini" style="margin-top:8px">Nenhuma linha recusada.</p>
    </div>
  </div>
</template>
