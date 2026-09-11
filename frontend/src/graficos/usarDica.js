/**
 * Dica de passagem posicionada e contida dentro do gráfico.
 *
 * Sem a contenção, a dica da primeira coluna sangra para fora da tela e o
 * texto é cortado — foi o que aconteceu na primeira versão. A largura é
 * medida depois de renderizar, não estimada.
 */
import { nextTick, ref } from "vue";

export function usarDica() {
  const dica = ref(null);
  const elDica = ref(null);

  async function abrir(evento, conteudo, seletorContainer) {
    const container = evento.currentTarget.closest(seletorContainer);
    const caixa = container.getBoundingClientRect();
    const alvo = evento.currentTarget.getBoundingClientRect();

    dica.value = {
      x: alvo.left - caixa.left + alvo.width / 2,
      y: alvo.top - caixa.top,
      ...conteudo,
    };

    await nextTick();
    const el = elDica.value;
    if (!el) return;
    const metade = el.offsetWidth / 2;
    const margem = 4;
    // mantém as duas bordas dentro do container
    dica.value.x = Math.min(
      Math.max(dica.value.x, metade + margem),
      caixa.width - metade - margem
    );
  }

  function fechar() {
    dica.value = null;
  }

  return { dica, elDica, abrir, fechar };
}
