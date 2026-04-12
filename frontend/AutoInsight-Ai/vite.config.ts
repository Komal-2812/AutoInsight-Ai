/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path"; // <-- add this

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"), // <-- this maps @ to src
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
  },
});