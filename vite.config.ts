import { defineConfig } from "vite";

export default defineConfig(async ({ mode }) => {
  if (mode === "test") {
    return {
      build: {
        outDir: "dist",
        sourcemap: true,
      },
    };
  }

  const { cloudflare } = await import("@cloudflare/vite-plugin");

  return {
    build: {
      outDir: "dist",
      sourcemap: true,
    },
    plugins: [
      cloudflare({
        viteEnvironment: {
          name: "server",
        },
        config: {
          main: "./worker/index.ts",
          compatibility_flags: ["nodejs_compat"],
        },
      }),
    ],
    server: {
      host: "0.0.0.0",
    },
  };
});
