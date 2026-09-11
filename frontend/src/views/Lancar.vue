<script setup>
import { onMounted, reactive, ref } from "vue";
import { API } from "../api.js";
import { estado, mostrarErro, mostrarFlash } from "../estado.js";
import { brl, hojeISO } from "../formato.js";

function formVazio() {
  return {
    valor: "", descricao: "", cartao: "", categoria: "",
    pessoas: [], parcelas: 1, data: hojeISO(),
    estimativa: false,
    // Task 4.4 — a regra de auto-categorização só é criada quando a pessoa
    // pede. O contrato diz que ela PODE criar, não que o sistema cria sempre.
    salvarRegra: false,
  };
}

const f = reactive(formVazio());
const ultimos = ref([]);
const ocupado = ref(false);

if (!f.cartao && estado.cartoes.length) f.cartao = estado.cartoes[0].nome;

function alternarPessoa(nome) {
  const i = f.pessoas.indexOf(nome);
  if (i >= 0) f.pessoas.splice(i, 1);
  else f.pessoas.push(nome);
}

async function buscarSugestao() {
  if (!f.descricao.trim()) return;
  try {
    const s = await API.sugestao(f.descricao.trim());
    if (s.categoria) f.categoria = s.categoria;
    if (s.pessoas?.length) f.pessoas = [...s.pessoas];
  } catch { /* sugestão é conveniência, nunca bloqueia o lançamento */ }
}

async function carregarUltimos() {
  try { ultimos.value = (await API.lancamentos()).slice(0, 6); } catch { /* silencioso */ }
}

async function lancar() {
  estado.erro = "";
  const valor = parseFloat(String(f.valor).replace(",", "."));
  if (!(valor > 0)) { estado.erro = "Digite o valor da compra."; return; }
  if (!f.descricao.trim()) { estado.erro = "Diga o que foi a compra."; return; }
  if (!f.cartao) { estado.erro = "Escolha uma forma de pagamento."; return; }

  ocupado.value = true;
  try {
    await API.lancar({
      valor,
      descricao: f.descricao.trim(),
      data: f.data,
      cartao: f.cartao,
      categoria: f.categoria,
      pessoas: f.pessoas,
      parcelas: f.parcelas,
      estimativa: f.estimativa,
      salvar_regra: f.salvarRegra,
    });
    if (f.salvarRegra) estado.regras = await API.regras();
    Object.assign(f, formVazio());
    if (estado.cartoes.length) f.cartao = estado.cartoes[0].nome;
    mostrarFlash("Lançado com sucesso.");
    await carregarUltimos();
  } catch (e) {
    mostrarErro(e);
  } finally {
    ocupado.value = false;
  }
}

onMounted(carregarUltimos);
</script>

<template>
  <div class="bloco">
    <h2>Nova despesa</h2>

    <div class="campo"><label for="f-valor">Valor (R$)</label>
      <input id="f-valor" v-model="f.valor" type="number" step="0.01" /></div>

    <div class="campo"><label for="f-desc">Descrição</label>
      <input id="f-desc" v-model="f.descricao" type="text" placeholder="Mercado, iFood, gasolina…" @blur="buscarSugestao" /></div>

    <div class="campo"><label>Forma de pagamento</label>
      <div id="f-cartao" class="chips">
        <button v-for="c in estado.cartoes" :key="c.id" class="chip" :data-v="c.nome"
                :aria-pressed="f.cartao === c.nome" @click="f.cartao = c.nome">{{ c.nome }}</button>
        <span v-if="!estado.cartoes.length" class="mini">Cadastre uma forma de pagamento em Ajustes.</span>
      </div>
    </div>

    <div class="campo"><label>Quem divide</label>
      <div id="f-pessoas" class="chips">
        <button v-for="p in estado.pessoas" :key="p.id" class="chip" :data-v="p.nome"
                :aria-pressed="f.pessoas.includes(p.nome)" @click="alternarPessoa(p.nome)">{{ p.nome }}</button>
        <span v-if="!estado.pessoas.length" class="mini">Cadastre pessoas em Ajustes.</span>
      </div>
    </div>

    <div class="campo"><label>Categoria</label>
      <div id="f-categoria" class="chips">
        <button v-for="c in estado.categorias" :key="c.id" class="chip" :data-v="c.nome"
                :aria-pressed="f.categoria === c.nome"
                @click="f.categoria = f.categoria === c.nome ? '' : c.nome">{{ c.nome }}</button>
        <span v-if="!estado.categorias.length" class="mini">Cadastre categorias em Ajustes.</span>
      </div>
    </div>

    <div class="dupla">
      <div class="campo"><label for="f-data">Data</label><input id="f-data" v-model="f.data" type="date" /></div>
      <div class="campo"><label for="f-parcelas">Parcelas</label>
        <input id="f-parcelas" v-model.number="f.parcelas" type="number" min="1" max="48" /></div>
    </div>

    <label style="display:flex;gap:8px;align-items:center;margin-bottom:10px">
      <input id="f-est" v-model="f.estimativa" type="checkbox" style="width:auto" />
      <span class="mini">É conta fixa recorrente (aluguel, luz, internet)</span>
    </label>

    <label style="display:flex;gap:8px;align-items:center;margin-bottom:10px">
      <input id="f-salvar-regra" v-model="f.salvarRegra" type="checkbox" style="width:auto" />
      <span class="mini">Memorizar categoria e pessoas para descrições parecidas</span>
    </label>

    <div class="acoes">
      <button id="f-gravar" class="btn" :disabled="ocupado" @click="lancar">Lançar</button>
      <button id="f-limpar" class="btn sec" @click="Object.assign(f, formVazio())">Limpar</button>
    </div>
  </div>

  <div class="bloco">
    <h2>Últimos lançamentos</h2>
    <div id="f-ultimos">
      <div v-for="l in ultimos" :key="l.id" class="item">
        <div class="txt">
          <div class="tt">{{ l.descricao }}</div>
          <div class="sub">
            <span class="tag">{{ l.cartao }}</span>
            <span v-if="l.parcela" class="tag">{{ l.parcela }}</span>
            <span>{{ l.categoria || "—" }}</span>
            <span v-if="l.pessoas.length" class="tag verde">{{ l.pessoas.join(" + ") }}</span>
            <span v-else class="tag amarelo">sem dono</span>
          </div>
        </div>
        <div class="vv">{{ brl(l.valor) }}</div>
      </div>
      <p v-if="!ultimos.length" class="vazio">Nada lançado ainda.</p>
    </div>
  </div>
</template>
