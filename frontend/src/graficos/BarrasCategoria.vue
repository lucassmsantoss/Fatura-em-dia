<script setup>
/**
 * Gastos por categoria — barras horizontais, série única.
 *
 * A tarefa do dado é comparar magnitude, não distinguir identidade: uma cor só
 * (sequencial), com o comprimento fazendo o trabalho. Horizontal porque nomes de
 * categoria são longos. Série única não leva legenda — o título do bloco já diz
 * o que está plotado.
 *
 * HTML e não SVG: texto nativo, responsivo sem viewBox, e nenhum risco de o
 * rótulo esticar junto com a barra.
 */
import { computed } from "vue";
import { brl } from "../formato.js";
import { usarDica } from "./usarDica.js";

const props = defineProps({ itens: { type: Array, required: true } });

const maximo = computed(() => Math.max(...props.itens.map((i) => i.valor), 0) || 1);
const total = computed(() => props.itens.reduce((s, i) => s + i.valor, 0));
const { dica, elDica, abrir, fechar } = usarDica();
const ativa = computed(() => dica.value?.item?.categoria ?? null);

const percentual = (v) => Math.max(1.5, (v / maximo.value) * 100);
const fatia = (v) => (total.value ? Math.round((v / total.value) * 100) : 0);

const mostrar = (evento, item) => abrir(evento, { item }, ".barras");
</script>

<template>
  <div class="barras" @mouseleave="fechar">
    <div
      v-for="i in itens"
      :key="i.categoria"
      class="linha"
      :class="{ ativa: ativa === i.categoria }"
      @mouseenter="mostrar($event, i)"
    >
      <div class="rot" :title="i.categoria">{{ i.categoria }}</div>
      <div class="trilha">
        <div class="marca" :style="{ width: percentual(i.valor) + '%' }"></div>
      </div>
      <div class="val">{{ brl(i.valor) }}</div>
    </div>

    <div v-if="dica" ref="elDica" class="dica" :style="{ left: dica.x + 'px', top: dica.y + 'px' }">
      <div class="l"><i style="background:var(--viz-1)"></i>{{ dica.item.categoria }}</div>
      <b>{{ brl(dica.item.valor) }}</b> · {{ fatia(dica.item.valor) }}% do seu gasto
    </div>
  </div>
</template>

<style scoped>
.barras { display: flex; flex-direction: column; gap: 10px; position: relative; }
.linha {
  display: grid;
  grid-template-columns: minmax(60px, 1fr) minmax(0, 2.4fr) auto;
  align-items: center; gap: 10px; padding: 3px 6px; margin: -3px -6px;
  transition: background .12s;
}
/* destaque por fundo, não por opacidade — a cor da marca foi validada cheia */
.linha.ativa { background: var(--paper); border-radius: 8px; }
.rot {
  font-size: 13px; color: var(--ink2);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
/* trilha dá a referência de escala sem precisar de grade */
.trilha { height: 18px; background: var(--viz-track); border-radius: 4px; overflow: hidden; }
.marca {
  height: 100%; background: var(--viz-1);
  /* ponta arredondada, quadrada na linha de base */
  border-radius: 0 4px 4px 0;
  transition: width .25s ease-out;
}
.val { font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; white-space: nowrap; }

@media (max-width: 420px) {
  .linha { grid-template-columns: minmax(52px, 1fr) minmax(0, 1.6fr) auto; }
}
</style>
