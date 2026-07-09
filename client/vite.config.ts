import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      // 8000 is often occupied on this machine (e.g. other local services)
      "/api": "http://127.0.0.1:8001",
      "/internal": "http://127.0.0.1:8001",
      "/health": "http://127.0.0.1:8001",
    },
  },
});
