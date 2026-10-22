import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

// Settings come from the repo-root .env (see .env.example). Only VITE_* values reach the browser.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, "..", "");
  // index.html uses %VITE_SITE_URL% for canonical / Open Graph links
  process.env.VITE_SITE_URL ??= env.VITE_SITE_URL || "http://localhost:5173";
  return {
    envDir: "..",
    plugins: [react(), tailwindcss()],
    // `npm run dev`: forward API calls to uvicorn
    server: { proxy: { "/api": env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000" } },
    preview: { proxy: { "/api": env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000" } },
  };
});
