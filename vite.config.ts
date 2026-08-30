import { defineConfig } from "vite";

export default defineConfig(async ({ mode }) => {
  const isVercelBuild = mode === "vercel";
  const publicDir: string | false = isVercelBuild ? false : "public";

  if (mode === "test" || isVercelBuild) {
    return {
      publicDir,
      build: {
        emptyOutDir: true,
        outDir: isVercelBuild ? "dist-vercel" : "dist",
        sourcemap: !isVercelBuild,
      },
      server: {
        host: "0.0.0.0",
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
