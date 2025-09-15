import { defineConfig, configDefaults } from "vitest/config";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import path from "node:path";

// Recreate __dirname in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },

    // Vitest config (typed via vitest/config)
    test: {
        environment: "jsdom",
        globals: true,
        css: true,
        setupFiles: "./src/tests/setup.ts",
        coverage: {
            provider: "v8",
            reporter: ["text", "html"],
            exclude: [...configDefaults.coverage.exclude, "src/tests/**"],
        },
    },
});
