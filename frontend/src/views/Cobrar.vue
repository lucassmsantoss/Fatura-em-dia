<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { API } from "../api.js";
import { estado, mostrarErro, mostrarFlash } from "../estado.js";
import { brl, hojeISO, mesAtual, mesRotulo, mesesParaSeletor } from "../formato.js";

const meses = mesesParaSeletor();
const mes = ref(mesAtual());
const pessoa = ref(null);
const extrato = ref(null);
const valorPagamento = ref("");
const carregando = ref(false);

const outras = computed(() =>
  estado.pessoas.filter((p) => p.nome !== estado.usuario?.nome)
);

function escolherPadrao() {
  if (pessoa.value) return;
  pessoa.value = outras.value[0]?.nome ?? estado.pessoas[0]?.nome ?? null;
}

async function carregar() {
  escolherPadrao();
  if (!pessoa.value) return;
  carregando.value = true;
  try {
    extrato.value = await API.extrato(pessoa.value, mes.value);
  } catch (e) {
    mostrarErro(e);
  } finally {
    carregando.value = false;
  }
}

async function registrarPagamento() {
  const valor = parseFloat(String(valorPagamento.value).replace(",", "."));
  if (!(valor > 0)) { mostrarErro(new Error("Informe um valor válido.")); return; }
  try {
    await API.registrarPagamento({
      pessoa: pessoa.value, valor, data: hojeISO(), mes_ref: mes.value,
    });
    valorPagamento.value = "";
    mostrarFlash("Pagamento registrado.");
    await carregar();
  } catch (e) {
    mostrarErro(e);
  }
}

watch([pessoa, mes], carregar);
onMounted(carregar);
</script>

<template>
  <div v-if="!estado.pessoas.length" class="bloco">
    <p class="vazio">Cadastre pessoas em Ajustes para usar a cobrança.</p>
  </div>

  <template v-else>
    <div id="ex-pessoas" class="chips" style="margin-bottom:12px">
      <button v-for="p in estado.pessoas" :key="p.id" class="chip" :data-v="p.nome"
              :aria-pressed="p.nome === pessoa" @click="pessoa = p.nome">{{ p.nome }}</button>
    </div>

    <div class="campo">
      <select id="ex-mes" v-model="mes">
        <option v-for="m in meses" :key="m" :value="m">{{ mesRotulo(m) }}</option>
      </select>
    </div>

    <p v-if="carregando" class="mini">Carregando…</p>

    <div v-else-if="extrato" class="bloco">
      <h2>{{ pessoa }} · {{ mesRotulo(mes) }}</h2>
      <div class="par"><span>Gastos deste mês</span><b>{{ brl(extrato.devido_no_mes) }}</b></div>
      <div class="par"><span>Já pagou (no mês)</span><b>{{ brl(extrato.pago_no_mes) }}</b></div>
      <div class="par forte">
        <span>Total a receber (acumulado)</span>
        <b :style="{ color: extrato.acumulado > 0.004 ? 'var(--accent)' : 'var(--ink3)' }">
          {{ brl(extrato.acumulado) }}
        </b>
      </div>
      <div class="acoes" style="margin-top:12px">
        <input id="ex-valor-pagto" v-model="valorPagamento" type="number" step="0.01" placeholder="Valor recebido" />
        <button id="ex-registrar" class="btn" @click="registrarPagamento">Registrar pagamento</button>
      </div>
    </div>
  </template>
</template>
