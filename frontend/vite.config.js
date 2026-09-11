import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// A API vive na raiz (/pessoas, /painel/...), e não sob um prefixo /api.
// Manter assim evitou mexer nas 152 provas do backend, então o proxy de
// desenvolvimento precisa enumerar os prefixos da API explicitamente.
// Em produção o FastAPI serve estes mesmos caminhos e o dist/ no resto.
const PREFIXOS_DA_API = [
  "/auth",
  "/onboarding",
  "/pessoas",
  "/cartoes",
  "/categorias",
  "/regras",
  "/lancamentos",
  "/painel",
  "/previsao",
  "/extrato",
  "/pagamentos",
  "/receitas",
];

const proxy = Object.fromEntries(
  PREFIXOS_DA_API.map((p) => [p, { target: "http://localhost:8000", changeOrigin: true }])
);

export default defineConfig({
  plugins: [vue()],
  server: { port: 5173, proxy },
  build: { outDir: "dist", emptyOutDir: true },
});
