<script setup>
import { reactive, ref } from "vue";
import { API } from "../api.js";
import { estado, carregarConfig, mostrarErro, mesAtual } from "../estado.js";

// Nada aqui nasce preenchido: o requisito "Ausência de dados pré-existentes"
// pede que a conta não receba nenhuma categoria ou forma de pagamento embutida
// no produto. Os campos são de digitação livre, então a lista começa vazia.
const rascunho = reactive({
  renda_principal: 0,
  pessoas: [],
  cartoes: [],
  categorias: [],
});

const novaPessoa = ref("");
const novaCategoria = ref("");
const ocupado = ref(false);

function adicionarPessoa() {
  const v = novaPessoa.value.trim();
  if (!v || rascunho.pessoas.includes(v)) return;
  rascunho.pessoas.push(v);
  novaPessoa.value = "";
}

function adicionarCategoria() {
  const v = novaCategoria.value.trim();
  if (!v || rascunho.categorias.includes(v)) return;
  rascunho.categorias.push(v);
  novaCategoria.value = "";
}

function adicionarCartao() {
  rascunho.cartoes.push({ nome: "", cor: "#0E6F63", fecha: 0, desloca: 0 });
}

async function concluir() {
  estado.erro = "";
  if (!rascunho.pessoas.length) {
    estado.erro = "Adicione ao menos uma pessoa (pode ser só você).";
    return;
  }
  if (!rascunho.cartoes.length || rascunho.cartoes.some((c) => !c.nome.trim())) {
    estado.erro = "Adicione ao menos uma forma de pagamento e dê um nome a ela.";
    return;
  }

  ocupado.value = true;
  try {
    await API.onboarding({
      renda_principal: Number(rascunho.renda_principal) || 0,
      pessoas: rascunho.pessoas,
      cartoes: rascunho.cartoes.map((c) => ({ ...c, nome: c.nome.trim() })),
      categorias: rascunho.categorias,
    });
    estado.usuario.onboarding_concluido = true;
    await carregarConfig();
    estado.tela = "app";
  } catch (e) {
    mostrarErro(e);
  } finally {
    ocupado.value = false;
  }
}
</script>

<template>
  <div class="topo"><div class="marca">Fatura<span> em Dia</span></div></div>

  <div class="bloco">
    <h2>Bem-vindo(a), {{ estado.usuario?.nome }}</h2>
    <p class="mini">Vamos configurar rapidamente antes de começar. Isso leva menos de um minuto.</p>
  </div>

  <div class="bloco">
    <h2>Sua renda mensal</h2>
    <div class="campo">
      <label for="ob-renda">Renda principal (R$)</label>
      <input id="ob-renda" v-model="rascunho.renda_principal" type="number" step="0.01" />
      <p class="mini">Vira a receita de {{ mesAtual() }}. Dá para alterar depois em Ajustes.</p>
    </div>
  </div>

  <div class="bloco">
    <h2>Pessoas para dividir despesas</h2>
    <p class="mini" style="margin-top:-6px">
      Inclua você mesmo(a) — use exatamente o nome "{{ estado.usuario?.nome }}" para que o painel calcule o que é seu.
    </p>
    <div id="ob-pessoas" class="chips" style="margin:10px 0">
      <span v-for="(p, i) in rascunho.pessoas" :key="p" class="chip" aria-pressed="true">
        {{ p }}
        <button style="border:0;background:none;cursor:pointer" @click="rascunho.pessoas.splice(i, 1)">×</button>
      </span>
      <span v-if="!rascunho.pessoas.length" class="mini">Nenhuma pessoa ainda.</span>
    </div>
    <div class="acoes">
      <input id="ob-nova-pessoa" v-model="novaPessoa" type="text" placeholder="Nome da pessoa" @keyup.enter="adicionarPessoa" />
      <button id="ob-add-pessoa" class="btn small" @click="adicionarPessoa">Adicionar</button>
    </div>
  </div>

  <div class="bloco">
    <h2>Formas de pagamento</h2>
    <p class="mini" style="margin-top:-6px">
      O dia de fechamento e o deslocamento definem em qual fatura cada compra cai. Deixe zerado para Pix ou dinheiro.
    </p>
    <div v-for="(c, i) in rascunho.cartoes" :key="i" style="padding:10px 0;border-top:1px solid var(--line)">
      <div class="campo">
        <label>Nome</label>
        <input v-model="c.nome" type="text" :data-cartao-nome="i" placeholder="Ex.: Cartão Nubank" />
      </div>
      <div class="dupla">
        <div class="campo"><label>Fecha no dia</label><input v-model.number="c.fecha" type="number" min="0" max="31" :data-cartao-fecha="i" /></div>
        <div class="campo"><label>Meses até cobrar</label><input v-model.number="c.desloca" type="number" min="0" max="6" :data-cartao-desloca="i" /></div>
      </div>
      <div class="campo"><label>Cor</label><input v-model="c.cor" type="color" :data-cartao-cor="i" /></div>
      <button class="chip small" @click="rascunho.cartoes.splice(i, 1)">remover</button>
    </div>
    <span v-if="!rascunho.cartoes.length" class="mini">Nenhuma forma de pagamento ainda.</span>
    <div class="acoes" style="margin-top:10px">
      <button id="ob-add-cartao" class="btn sec small" @click="adicionarCartao">+ Adicionar forma de pagamento</button>
    </div>
  </div>

  <div class="bloco">
    <h2>Categorias de despesa</h2>
    <p class="mini" style="margin-top:-6px">Crie as categorias que fazem sentido para você — nada vem pronto.</p>
    <div id="ob-categorias" class="chips" style="margin:10px 0">
      <span v-for="(c, i) in rascunho.categorias" :key="c" class="chip" aria-pressed="true">
        {{ c }}
        <button style="border:0;background:none;cursor:pointer" @click="rascunho.categorias.splice(i, 1)">×</button>
      </span>
      <span v-if="!rascunho.categorias.length" class="mini">Nenhuma categoria ainda.</span>
    </div>
    <div class="acoes">
      <input id="ob-nova-cat" v-model="novaCategoria" type="text" placeholder="Ex.: Mercado" @keyup.enter="adicionarCategoria" />
      <button id="ob-add-cat" class="btn small" @click="adicionarCategoria">Adicionar</button>
    </div>
  </div>

  <p v-if="estado.erro" class="erro">{{ estado.erro }}</p>
  <div class="acoes">
    <button id="ob-concluir" class="btn" :disabled="ocupado" @click="concluir">Concluir configuração</button>
  </div>
</template>
