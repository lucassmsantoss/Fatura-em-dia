<script setup>
import { onMounted, onUnmounted, ref } from "vue";
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
  menuAberto.value = false;
}

// ---- menu da conta ----
// O "sair" era um link solto ao lado da marca, fácil de acertar sem querer e
// sem nenhum contexto de quem está logado. Vira um menu: avatar com iniciais,
// nome, email, e a saída atrás de um clique a mais.
const menuAberto = ref(false);
const deslocado = ref(false);

const iniciais = (nome = "") =>
  nome.split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase() ?? "").join("");

function fecharForaDoMenu(evento) {
  if (!evento.target.closest(".conta")) menuAberto.value = false;
}
function aoRolar() {
  deslocado.value = window.scrollY > 4;
}

onMounted(() => {
  document.addEventListener("click", fecharForaDoMenu);
  window.addEventListener("scroll", aoRolar, { passive: true });
});
onUnmounted(() => {
  document.removeEventListener("click", fecharForaDoMenu);
  window.removeEventListener("scroll", aoRolar);
});

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
    <header class="cabecalho" :class="{ deslocado }">
      <div class="marca">Fatura<span> em Dia</span></div>

      <div class="conta">
        <button :aria-expanded="menuAberto" aria-haspopup="menu" @click="menuAberto = !menuAberto">
          <span class="avatar">{{ iniciais(estado.usuario?.nome) }}</span>
          <span class="nome">{{ estado.usuario?.nome }}</span>
        </button>

        <div v-if="menuAberto" class="menu" role="menu">
          <div class="cab">
            <div style="font-weight:600">{{ estado.usuario?.nome }}</div>
            <div class="e">{{ estado.usuario?.email }}</div>
          </div>
          <button role="menuitem" @click="trocarAba('ajustes')">Ajustes da conta</button>
          <button role="menuitem" class="perigo" @click="sair">Sair</button>
        </div>
      </div>
    </header>

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
