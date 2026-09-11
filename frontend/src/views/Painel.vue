<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { API } from "../api.js";
import { mostrarErro } from "../estado.js";
import { brl, mesAtual, mesRotulo, mesesParaSeletor } from "../formato.js";
import BarrasCategoria from "../graficos/BarrasCategoria.vue";
import ColunasPrevisao from "../graficos/ColunasPrevisao.vue";
import Medidor from "../graficos/Medidor.vue";

const mes = ref(mesAtual());
const meses = mesesParaSeletor();
const painel = ref(null);
const previsao = ref([]);
const carregando = ref(true);
const verTabela = ref({ categorias: false, previsao: false });

const sobrou = computed(() => (painel.value?.sobra_ou_falta ?? 0) >= 0);
const comprometido = computed(() => {
  const p = painel.value;
  if (!p || p.receita_total <= 0) return null;
  return Math.round((p.meu_total / p.receita_total) * 100);
});

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

function irParaMes(m) {
  if (meses.includes(m)) mes.value = m;
}

watch(mes, carregar);
onMounted(carregar);
</script>

<template>
  <div class="campo">
    <select id="p-mes" v-model="mes" aria-label="Mês do painel">
      <option v-for="m in meses" :key="m" :value="m">{{ mesRotulo(m) }}</option>
    </select>
  </div>

  <p v-if="carregando" class="mini">Carregando painel…</p>

  <template v-else-if="painel">
    <!-- O número que responde a pergunta do fim do mês -->
    <div class="bloco">
      <div class="hero">
        <div class="rot">{{ sobrou ? "Sobra em " + mesRotulo(painel.mes) : "Falta em " + mesRotulo(painel.mes) }}</div>
        <div class="num" :style="{ color: sobrou ? 'var(--accent)' : 'var(--alert)' }">
          {{ brl(Math.abs(painel.sobra_ou_falta)) }}
        </div>
        <p class="ctx">
          <template v-if="comprometido !== null">
            Você comprometeu <b>{{ comprometido }}%</b> da sua receita neste mês.
          </template>
          <template v-else>
            Nenhuma receita registrada para este mês — registre em Ajustes para ver sobra ou falta.
          </template>
        </p>
      </div>

      <Medidor
        v-if="painel.receita_total > 0"
        :valor="painel.meu_total"
        :limite="painel.receita_total"
        :rotulo-esquerda="`Seu gasto ${brl(painel.meu_total)}`"
        :rotulo-direita="`Receita ${brl(painel.receita_total)}`"
      />

      <div class="kpis">
        <div class="kpi"><div class="r">Total do mês</div><div class="v">{{ brl(painel.total_mes) }}</div></div>
        <div class="kpi"><div class="r">O que é seu</div><div class="v">{{ brl(painel.meu_total) }}</div></div>
        <div class="kpi"><div class="r">Receita</div><div class="v">{{ brl(painel.receita_total) }}</div></div>
      </div>

      <div v-if="painel.sem_dono > 0.004" class="aviso amarelo" style="margin-top:12px;margin-bottom:0">
        {{ brl(painel.sem_dono) }} ainda sem dono neste mês — atribua em Lançar para entrar no rateio.
      </div>
    </div>

    <!-- Gastos por categoria -->
    <div class="bloco">
      <div class="cabecalho-bloco">
        <h2>Onde foi o seu dinheiro</h2>
        <button v-if="painel.gastos_por_categoria.length" class="alternar"
                @click="verTabela.categorias = !verTabela.categorias">
          {{ verTabela.categorias ? "ver gráfico" : "ver tabela" }}
        </button>
      </div>

      <template v-if="painel.gastos_por_categoria.length">
        <BarrasCategoria v-if="!verTabela.categorias" :itens="painel.gastos_por_categoria" />
        <table v-else class="dados">
          <thead><tr><th>Categoria</th><th>Valor</th></tr></thead>
          <tbody>
            <tr v-for="c in painel.gastos_por_categoria" :key="c.categoria">
              <td>{{ c.categoria }}</td><td>{{ brl(c.valor) }}</td>
            </tr>
          </tbody>
        </table>
      </template>
      <p v-else class="vazio">Sem gastos seus neste mês.</p>
    </div>

    <!-- Previsão -->
    <div class="bloco">
      <div class="cabecalho-bloco">
        <h2>O que vem pela frente</h2>
        <button class="alternar" @click="verTabela.previsao = !verTabela.previsao">
          {{ verTabela.previsao ? "ver gráfico" : "ver tabela" }}
        </button>
      </div>

      <ColunasPrevisao v-if="!verTabela.previsao" :meses="previsao" @escolher="irParaMes" />
      <table v-else class="dados">
        <thead><tr><th>Mês</th><th>Já contratado</th><th>Conta fixa</th><th>Total</th></tr></thead>
        <tbody>
          <tr v-for="p in previsao" :key="p.mes">
            <td>{{ mesRotulo(p.mes) }}</td>
            <td>{{ brl(p.total_compromissos) }}</td>
            <td>{{ brl(p.total_estimativas) }}</td>
            <td>{{ brl(p.total_previsto) }}</td>
          </tr>
        </tbody>
      </table>

      <p class="mini" style="margin-top:10px">
        Somado das parcelas já contratadas e das contas fixas recorrentes já lançadas — calculado
        a cada consulta, sem dado importado. Clique num mês para abrir o painel dele.
      </p>
    </div>

    <!-- Quem te deve -->
    <div class="bloco">
      <h2>Quem te deve</h2>
      <template v-if="painel.saldos_por_pessoa.length">
        <div v-for="s in painel.saldos_por_pessoa" :key="s.pessoa" class="item" style="display:block">
          <div style="display:flex;justify-content:space-between;align-items:baseline;gap:10px">
            <div class="tt">{{ s.pessoa }}</div>
            <div class="vv" :style="{ color: s.acumulado > 0.004 ? 'var(--ink)' : 'var(--ink3)' }">
              {{ brl(s.acumulado) }}
            </div>
          </div>
          <Medidor
            v-if="s.devido_no_mes > 0.004"
            :valor="s.pago_no_mes"
            :limite="s.devido_no_mes"
            :rotulo-esquerda="`pagou ${brl(s.pago_no_mes)}`"
            :rotulo-direita="`de ${brl(s.devido_no_mes)} no mês`"
          />
          <div v-else class="mini" style="margin-top:4px">Sem gastos neste mês · saldo vindo de meses anteriores</div>
        </div>
      </template>
      <p v-else class="vazio">Ninguém deve nada neste mês.</p>
    </div>
  </template>
</template>
