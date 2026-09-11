<script setup>
import { ref } from "vue";
import { API } from "../api.js";
import { estado, carregarConfig, mostrarErro } from "../estado.js";

const nome = ref("");
const email = ref("");
const senha = ref("");
const ocupado = ref(false);

const ehRegistro = () => estado.tela === "registro";

function trocarModo(tela) {
  estado.tela = tela;
  estado.erro = "";
}

async function entrarComSessao() {
  estado.usuario = await API.eu();
  await carregarConfig();
  estado.tela = estado.usuario.onboarding_concluido ? "app" : "onboarding";
}

async function enviar() {
  estado.erro = "";
  ocupado.value = true;
  try {
    if (ehRegistro()) {
      await API.registrar(nome.value.trim(), email.value.trim(), senha.value);
    }
    await API.login(email.value.trim(), senha.value);
    await entrarComSessao();
  } catch (e) {
    mostrarErro(e);
  } finally {
    ocupado.value = false;
  }
}
</script>

<template>
  <div class="centro">
    <div class="topo" style="justify-content:center">
      <div class="marca">Fatura<span> em Dia</span></div>
    </div>

    <div class="bloco">
      <h2>{{ ehRegistro() ? "Criar conta" : "Entrar" }}</h2>

      <div v-if="ehRegistro()" class="campo">
        <label for="r-nome">Nome</label>
        <input id="r-nome" v-model="nome" type="text" @keyup.enter="enviar" />
      </div>

      <div class="campo">
        <label :for="ehRegistro() ? 'r-email' : 'l-email'">Email</label>
        <input :id="ehRegistro() ? 'r-email' : 'l-email'" v-model="email" type="email" @keyup.enter="enviar" />
      </div>

      <div class="campo">
        <label :for="ehRegistro() ? 'r-senha' : 'l-senha'">
          {{ ehRegistro() ? "Senha (mínimo 6 caracteres)" : "Senha" }}
        </label>
        <input :id="ehRegistro() ? 'r-senha' : 'l-senha'" v-model="senha" type="password" @keyup.enter="enviar" />
      </div>

      <p v-if="estado.erro" class="erro">{{ estado.erro }}</p>

      <div class="acoes">
        <button class="btn" :disabled="ocupado" @click="enviar">
          {{ ehRegistro() ? "Criar conta" : "Entrar" }}
        </button>
      </div>

      <p class="mini" style="margin-top:12px;text-align:center">
        <template v-if="ehRegistro()">
          Já tem conta? <button class="link" @click="trocarModo('login')">Entrar</button>
        </template>
        <template v-else>
          Não tem conta? <button class="link" @click="trocarModo('registro')">Criar conta</button>
        </template>
      </p>
    </div>
  </div>
</template>
