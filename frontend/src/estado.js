/**
 * Estado compartilhado da aplicação.
 *
 * `reactive` do Vue no lugar de um store dedicado: o escopo é pequeno e uma
 * dependência a mais não se paga aqui. Preserva a decisão do protótipo de
 * manter estado local, sem Vuex/Pinia.
 */
import { reactive } from "vue";
import { API } from "./api.js";
import { mesAtual } from "./formato.js";

export const estado = reactive({
  tela: API.token() ? "carregando" : "login",
  usuario: null,
  pessoas: [],
  cartoes: [],
  categorias: [],
  regras: [],
  aba: "lancar",
  erro: "",
  flash: "",
});

export async function carregarConfig() {
  const [pessoas, cartoes, categorias, regras] = await Promise.all([
    API.pessoas(), API.cartoes(), API.categorias(), API.regras(),
  ]);
  Object.assign(estado, { pessoas, cartoes, categorias, regras });
}

export function mostrarErro(e) {
  estado.erro = (e && e.message) || String(e);
}

let timerFlash;
export function mostrarFlash(msg) {
  estado.flash = msg;
  clearTimeout(timerFlash);
  timerFlash = setTimeout(() => { estado.flash = ""; }, 3500);
}

export function sair() {
  API.logout();
  Object.assign(estado, {
    tela: "login", usuario: null, pessoas: [], cartoes: [], categorias: [], regras: [],
    aba: "lancar", erro: "", flash: "",
  });
}

export { mesAtual };
