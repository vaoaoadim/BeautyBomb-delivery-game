#!/usr/bin/env node

import { rmSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputRoot = path.resolve(root, "dist-vercel");

if (
  path.dirname(outputRoot) !== root ||
  path.basename(outputRoot).toLowerCase() !== "dist-vercel"
) {
  throw new Error(`Refusing to clean unexpected Vercel output: ${outputRoot}`);
}

rmSync(outputRoot, { force: true, recursive: true });
console.log(`Cleaned Vercel output: ${outputRoot}`);
