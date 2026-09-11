<script setup>
import { onMounted } from "vue";
import { API } from "./api.js";
import { estado, carregarConfig, sair } from "./estado.js";
import Autenticacao from "./views/Autenticacao.vue";
import Onboarding from "./views/Onboarding.vue";
import Lancar from "./views/Lancar.vue";
import Painel from "./views/Painel.vue";
import Cobrar from "./views/Cobrar.vue";
import Ajustes from "./views/Ajustes.vue";

const ABAS = [
  ["lancar", "Lançar", Lancar],
  ["painel", "Painel", Painel],
  ["cobrar", "Cobrar", Cobrar],
  ["ajustes", "Ajustes", Ajustes],
];

const componenteDaAba = () => ABAS.find(([id]) => id === estado.aba)?.[2] ?? Lancar;

function trocarAba(id) {
  estado.aba = id;
  estado.erro = "";
}

onMounted(async () => {
  if (!API.token()) return;
  try {
    estado.usuario = await API.eu();
    await carregarConfig();
    estado.tela = estado.usuario.onboarding_concluido ? "app" : "onboarding";
  } catch {
    sair();
  }
});
</script>

<template>
  <p v-if="estado.tela === 'carregando'" class="mini" style="margin-top:40px;text-align:center">
    Carregando…
  </p>

  <Autenticacao v-else-if="estado.tela === 'login' || estado.tela === 'registro'" />

  <Onboarding v-else-if="estado.tela === 'onboarding'" />

  <template v-else>
    <div class="topo">
      <div class="marca">Fatura<span> em Dia</span></div>
      <button class="link" @click="sair">sair</button>
    </div>

    <div v-if="estado.flash" class="aviso verde">{{ estado.flash }}</div>
    <div v-if="estado.erro" class="aviso vermelho">{{ estado.erro }}</div>

    <component :is="componenteDaAba()" />

    <nav id="nav">
      <div class="in">
        <button
          v-for="[id, rotulo] in ABAS"
          :key="id"
          :data-aba="id"
          :aria-current="estado.aba === id"
          @click="trocarAba(id)"
        >{{ rotulo }}</button>
      </div>
    </nav>
  </template>
</template>
