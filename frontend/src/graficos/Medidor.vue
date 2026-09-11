<script setup>
/**
 * Medidor — uma razão contra um limite.
 *
 * Usado para "quanto da sua receita já está comprometido" e para "quanto a
 * pessoa já pagou do que deve". É um medidor e não uma pizza de duas fatias:
 * a pergunta é sobre proporção contra um teto, não sobre partes de um todo.
 */
import { computed } from "vue";

const props = defineProps({
  valor: { type: Number, required: true },
  limite: { type: Number, required: true },
  rotuloEsquerda: { type: String, default: "" },
  rotuloDireita: { type: String, default: "" },
  cor: { type: String, default: "var(--viz-1)" },
  corExcedente: { type: String, default: "var(--alert)" },
});

const fracao = computed(() => (props.limite > 0 ? props.valor / props.limite : 0));
const estourou = computed(() => fracao.value > 1);
const preenchido = computed(() => Math.min(100, Math.max(0, fracao.value * 100)));
</script>

<template>
  <div class="medidor">
    <div class="trilha" role="meter" :aria-valuenow="Math.round(preenchido)" aria-valuemin="0" aria-valuemax="100">
      <div class="parte" :style="{ width: preenchido + '%', background: estourou ? corExcedente : cor }"></div>
    </div>
    <div class="leg">
      <span>{{ rotuloEsquerda }}</span>
      <span>{{ rotuloDireita }}</span>
    </div>
  </div>
</template>
