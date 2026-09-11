/** Formatação e aritmética de meses — espelha as regras do domínio no backend. */

export function mesAtual() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function hojeISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function somaMes(mes, n) {
  const [ano, m] = mes.split("-").map(Number);
  const indice = m - 1 + n;
  const anoNovo = ano + Math.floor(indice / 12);
  const mesNovo = (((indice % 12) + 12) % 12) + 1;
  return `${anoNovo}-${String(mesNovo).padStart(2, "0")}`;
}

const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

export function mesRotulo(mes) {
  const [ano, m] = mes.split("-");
  return `${MESES[Number(m) - 1]}/${ano.slice(2)}`;
}

export function mesesParaSeletor(de = -3, ate = 12) {
  const base = mesAtual();
  const lista = [];
  for (let i = de; i <= ate; i++) lista.push(somaMes(base, i));
  return lista;
}

export function brl(v) {
  return (v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}
