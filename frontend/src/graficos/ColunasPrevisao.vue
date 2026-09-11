<script setup>
/**
 * Previsão dos próximos meses — colunas empilhadas, duas séries.
 *
 * Parte-do-todo ao longo do tempo: cada mês soma compromisso já contratado e
 * conta fixa recorrente. Duas séries, então cor categórica + legenda sempre
 * presente — identidade nunca depende só da cor.
 *
 * As duas cores foram validadas contra a superfície branca (ΔE protan 11.8,
 * normal 20.6, contraste >= 3:1). O teal da marca reprovava no piso de croma.
 *
 * Clicar num mês leva o painel para aquele mês: o gráfico não é só leitura.
 */
import { computed } from "vue";
import { brl, mesRotulo } from "../formato.js";
import { usarDica } from "./usarDica.js";

const props = defineProps({
  meses: { type: Array, required: true }, // [{ mes, total_compromissos, total_estimativas, total_previsto }]
});
const emit = defineEmits(["escolher"]);

const ALTURA = 120;
const maximo = computed(() => Math.max(...props.meses.map((m) => m.total_previsto), 0) || 1);
const vazio = computed(() => props.meses.every((m) => m.total_previsto <= 0.004));
// Rótulo direto só no extremo: dá escala ao gráfico sem poluir com um número
// em cada coluna. O resto sai na dica de passagem e na tabela.
const mesPico = computed(() => {
  const p = props.meses.reduce((a, b) => (b.total_previsto > (a?.total_previsto ?? -1) ? b : a), null);
  return p && p.total_previsto > 0.004 ? p.mes : null;
});
const { dica, elDica, abrir, fechar } = usarDica();
const ativo = computed(() => dica.value?.m?.mes ?? null);

const altura = (v) => (v / maximo.value) * ALTURA;

const mostrar = (evento, m) => abrir(evento, { m }, ".colunas");
</script>

<template>
  <div class="colunas" @mouseleave="fechar">
    <div class="plot" :style="{ height: ALTURA + 26 + 'px' }">
      <button
        v-for="m in meses"
        :key="m.mes"
        class="col"
        :class="{ pico: m.mes === mesPico, ativo: ativo === m.mes }"
        :aria-label="`${mesRotulo(m.mes)}: ${brl(m.total_previsto)}`"
        @mouseenter="mostrar($event, m)"
        @click="emit('escolher', m.mes)"
      >
        <div class="pilha" :style="{ height: ALTURA + 'px' }">
          <!-- empilhado de baixo para cima; o gap de 2px é superfície separando -->
          <div v-if="m.total_estimativas > 0.004" class="seg est"
               :style="{ height: altura(m.total_estimativas) + 'px' }"></div>
          <div v-if="m.total_compromissos > 0.004" class="seg cmp"
               :style="{ height: altura(m.total_compromissos) + 'px' }"></div>
        </div>
        <div v-if="m.mes === mesPico" class="pico">{{ brl(m.total_previsto) }}</div>
        <div class="eixo">{{ mesRotulo(m.mes).split("/")[0] }}</div>
      </button>
    </div>

    <p v-if="vazio" class="nada">Nada comprometido nos próximos meses.</p>

    <div class="legenda">
      <span><i style="background:var(--viz-1)"></i>Já contratado</span>
      <span><i style="background:var(--viz-2)"></i>Conta fixa</span>
    </div>

    <div v-if="dica" ref="elDica" class="dica" :style="{ left: dica.x + 'px', top: dica.y + 'px' }">
      <div style="margin-bottom:3px"><b>{{ mesRotulo(dica.m.mes) }}</b> · {{ brl(dica.m.total_previsto) }}</div>
      <div class="l"><i style="background:var(--viz-1)"></i>Já contratado <b>{{ brl(dica.m.total_compromissos) }}</b></div>
      <div class="l"><i style="background:var(--viz-2)"></i>Conta fixa <b>{{ brl(dica.m.total_estimativas) }}</b></div>
    </div>
  </div>
</template>

<style scoped>
.colunas { position: relative; }
.plot { display: flex; align-items: flex-end; gap: 6px; }
.col {
  flex: 1; background: transparent; border: 0; padding: 4px 0 0; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  border-radius: 8px; transition: background .12s;
}
/* o destaque é o fundo da coluna, nunca a opacidade da marca: a cor foi
   validada em opacidade cheia e perde contraste se for esmaecida */
.col.ativo { background: var(--paper); }
.pilha { width: 100%; max-width: 24px; margin: 0 auto; display: flex; flex-direction: column;
         justify-content: flex-end; gap: 2px; }
.seg { width: 100%; transition: height .25s ease-out; }
/* topo da pilha arredondado, base quadrada na linha de base */
.seg:first-child { border-radius: 4px 4px 0 0; }
.seg:last-child { border-radius: 0 0 0 0; }
.pilha > .seg:only-child { border-radius: 4px 4px 0 0; }
.cmp { background: var(--viz-1); }
.est { background: var(--viz-2); }
.eixo { font-size: 11px; color: var(--ink3); }
.pico { font-size: 11px; font-weight: 700; color: var(--ink); font-variant-numeric: tabular-nums;
        white-space: nowrap; margin-top: -2px; }
.nada { font-size: 13px; color: var(--ink3); margin: 8px 0 0; }
</style>
