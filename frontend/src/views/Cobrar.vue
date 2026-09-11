<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { API } from "../api.js";
import { estado, mostrarErro, mostrarFlash } from "../estado.js";
import { brl, hojeISO, mesAtual, mesRotulo, mesesParaSeletor } from "../formato.js";
import Medidor from "../graficos/Medidor.vue";

const meses = mesesParaSeletor();
const mes = ref(mesAtual());
const pessoa = ref(null);
const extrato = ref(null);
const pagamentos = ref([]);
const saldos = ref({});           // nome -> acumulado, para os cartões de seleção
const valorPagamento = ref("");
const carregando = ref(false);

// Quem aparece na cobrança: todo mundo menos a própria pessoa da conta — ela não
// se cobra. Mesma exclusão que o painel já faz em "Quem te deve". Se ela for a
// única cadastrada, mostra assim mesmo, para a aba não ficar vazia sem explicação.
const outras = computed(() => {
  const semAConta = estado.pessoas.filter((p) => p.nome !== estado.usuario?.nome);
  return semAConta.length ? semAConta : estado.pessoas;
});
const quitado = computed(() => extrato.value && Math.abs(extrato.value.acumulado) < 0.005);
const restante = computed(() =>
  extrato.value ? Math.max(0, extrato.value.devido_no_mes - extrato.value.pago_no_mes) : 0
);

const iniciais = (nome) =>
  nome.split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase() ?? "").join("");

async function carregarSaldos() {
  try {
    const p = await API.painel(mes.value);
    saldos.value = Object.fromEntries(p.saldos_por_pessoa.map((s) => [s.pessoa, s.acumulado]));
  } catch { /* os cartões funcionam sem o saldo */ }
}

async function carregar() {
  if (!pessoa.value) pessoa.value = outras.value[0]?.nome ?? null;
  if (!pessoa.value) return;
  carregando.value = true;
  try {
    const [e, pg] = await Promise.all([
      API.extrato(pessoa.value, mes.value),
      API.pagamentos(pessoa.value),
    ]);
    extrato.value = e;
    pagamentos.value = pg;
  } catch (e) {
    mostrarErro(e);
  } finally {
    carregando.value = false;
  }
}

function quitarTudo() {
  valorPagamento.value = String(restante.value.toFixed(2));
}

async function registrar() {
  const valor = parseFloat(String(valorPagamento.value).replace(",", "."));
  if (!(valor > 0)) { mostrarErro(new Error("Informe um valor maior que zero.")); return; }
  try {
    await API.registrarPagamento({ pessoa: pessoa.value, valor, data: hojeISO(), mes_ref: mes.value });
    valorPagamento.value = "";
    mostrarFlash(`Pagamento de ${brl(valor)} registrado.`);
    await Promise.all([carregar(), carregarSaldos()]);
  } catch (e) { mostrarErro(e); }
}

watch([pessoa, mes], carregar);
watch(mes, carregarSaldos);
onMounted(() => { carregar(); carregarSaldos(); });
</script>

<template>
  <div v-if="!estado.pessoas.length" class="bloco">
    <p class="vazio">Cadastre pessoas em Ajustes para usar a cobrança.</p>
  </div>

  <template v-else>
    <!-- Seleção por cartão, com o saldo já visível: escolher sem adivinhar -->
    <div id="ex-pessoas" class="pessoas-grade">
      <button
        v-for="p in outras"
        :key="p.id"
        class="pessoa-card"
        :data-v="p.nome"
        :aria-pressed="p.nome === pessoa"
        @click="pessoa = p.nome"
      >
        <span class="avatar">{{ iniciais(p.nome) }}</span>
        <span class="info">
          <span class="n">{{ p.nome }}</span>
          <span class="v">{{ saldos[p.nome] ? brl(saldos[p.nome]) : "em dia" }}</span>
        </span>
      </button>
    </div>

    <div class="campo">
      <select id="ex-mes" v-model="mes" aria-label="Mês da cobrança">
        <option v-for="m in meses" :key="m" :value="m">{{ mesRotulo(m) }}</option>
      </select>
    </div>

    <p v-if="carregando" class="mini">Carregando…</p>

    <template v-else-if="extrato">
      <div class="bloco">
        <div class="hero">
          <div class="rot">{{ pessoa }} · total a receber</div>
          <div class="num" :style="{ color: quitado ? 'var(--ink3)' : 'var(--accent)' }">
            {{ brl(extrato.acumulado) }}
          </div>
          <p class="ctx">
            <template v-if="quitado">Está tudo quitado — nada a cobrar.</template>
            <template v-else>Acumulado de todos os meses até {{ mesRotulo(mes) }}, já descontando o que foi pago.</template>
          </p>
        </div>

        <Medidor
          v-if="extrato.devido_no_mes > 0.004"
          :valor="extrato.pago_no_mes"
          :limite="extrato.devido_no_mes"
          :rotulo-esquerda="`pagou ${brl(extrato.pago_no_mes)}`"
          :rotulo-direita="`de ${brl(extrato.devido_no_mes)} em ${mesRotulo(mes)}`"
        />

        <div class="kpis">
          <div class="kpi"><div class="r">Gastos do mês</div><div class="v">{{ brl(extrato.devido_no_mes) }}</div></div>
          <div class="kpi"><div class="r">Pagou no mês</div><div class="v">{{ brl(extrato.pago_no_mes) }}</div></div>
          <div class="kpi"><div class="r">Falta no mês</div><div class="v">{{ brl(restante) }}</div></div>
        </div>
      </div>

      <div class="bloco">
        <h2>Registrar pagamento recebido</h2>
        <div class="campo">
          <label for="ex-valor-pagto">Valor recebido (R$)</label>
          <input id="ex-valor-pagto" v-model="valorPagamento" type="number" step="0.01"
                 placeholder="0,00" @keyup.enter="registrar" />
        </div>
        <div class="acoes">
          <button id="ex-registrar" class="btn" @click="registrar">Registrar</button>
          <button v-if="restante > 0.004" class="btn sec" @click="quitarTudo">
            Quitar {{ brl(restante) }}
          </button>
        </div>
        <p class="mini" style="margin-top:8px">
          O pagamento entra em {{ mesRotulo(mes) }} e abate o acumulado dela.
        </p>
      </div>

      <div class="bloco">
        <h2>Pagamentos de {{ pessoa }}</h2>
        <div v-for="p in pagamentos" :key="p.id" class="item">
          <div class="txt">
            <div class="tt">{{ brl(p.valor) }}</div>
            <div class="sub">
              <span class="tag">{{ mesRotulo(p.mes_ref) }}</span>
              <span>recebido em {{ p.data.split("-").reverse().join("/") }}</span>
            </div>
          </div>
        </div>
        <p v-if="!pagamentos.length" class="vazio">Nenhum pagamento registrado ainda.</p>
      </div>
    </template>
  </template>
</template>
