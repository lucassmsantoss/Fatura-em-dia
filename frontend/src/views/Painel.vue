<script setup>
import { onMounted, ref, watch } from "vue";
import { API } from "../api.js";
import { mostrarErro } from "../estado.js";
import { brl, mesAtual, mesRotulo, mesesParaSeletor } from "../formato.js";

const mes = ref(mesAtual());
const meses = mesesParaSeletor();
const painel = ref(null);
const previsao = ref([]);
const carregando = ref(true);

async function carregar() {
  carregando.value = true;
  try {
    const [p, pv] = await Promise.all([API.painel(mes.value), API.previsao(mes.value, 6)]);
    painel.value = p;
    previsao.value = pv;
  } catch (e) {
    mostrarErro(e);
  } finally {
    carregando.value = false;
  }
}

watch(mes, carregar);
onMounted(carregar);
</script>

<template>
  <div class="campo">
    <select id="p-mes" v-model="mes">
      <option v-for="m in meses" :key="m" :value="m">{{ mesRotulo(m) }}</option>
    </select>
  </div>

  <p v-if="carregando" class="mini">Carregando painel…</p>

  <template v-else-if="painel">
    <div class="bloco">
      <h2>O mês de {{ mesRotulo(painel.mes) }}</h2>
      <div class="par"><span>Total do mês</span><b>{{ brl(painel.total_mes) }}</b></div>
      <div class="par"><span>O que é seu</span><b>{{ brl(painel.meu_total) }}</b></div>
      <div class="par"><span>Sua receita</span><b>{{ brl(painel.receita_total) }}</b></div>
      <div class="par forte">
        <span>{{ painel.sobra_ou_falta >= 0 ? "Sobra" : "Falta" }}</span>
        <b :style="{ color: painel.sobra_ou_falta >= 0 ? 'var(--accent)' : 'var(--alert)' }">
          {{ brl(Math.abs(painel.sobra_ou_falta)) }}
        </b>
      </div>
      <div v-if="painel.sem_dono > 0.004" class="aviso amarelo" style="margin-top:10px">
        {{ brl(painel.sem_dono) }} ainda sem dono neste mês.
      </div>
    </div>

    <div class="bloco">
      <h2>Quem te deve</h2>
      <div v-for="s in painel.saldos_por_pessoa" :key="s.pessoa" class="item">
        <div class="txt">
          <div class="tt">{{ s.pessoa }}</div>
          <div class="sub">
            <span>no mês {{ brl(s.devido_no_mes) }}</span>
            <span v-if="s.pago_no_mes" class="tag verde">pagou {{ brl(s.pago_no_mes) }}</span>
          </div>
        </div>
        <div class="vv">{{ brl(s.acumulado) }}</div>
      </div>
      <p v-if="!painel.saldos_por_pessoa.length" class="vazio">Ninguém deve nada neste mês.</p>
    </div>

    <div class="bloco">
      <h2>Onde foi o seu dinheiro</h2>
      <div v-for="c in painel.gastos_por_categoria" :key="c.categoria" class="par">
        <span>{{ c.categoria }}</span><b>{{ brl(c.valor) }}</b>
      </div>
      <p v-if="!painel.gastos_por_categoria.length" class="vazio">Sem gastos seus neste mês.</p>
    </div>

    <div class="bloco">
      <h2>O que vem pela frente</h2>
      <div v-for="p in previsao" :key="p.mes" class="par">
        <span>{{ mesRotulo(p.mes) }}</span><b>{{ brl(p.total_previsto) }}</b>
      </div>
      <p class="mini" style="margin-top:8px">
        Soma parcelas já contratadas (compromisso) + contas fixas recorrentes (estimativa) já
        lançadas — calculado dinamicamente, sem dado importado.
      </p>
    </div>
  </template>
</template>
