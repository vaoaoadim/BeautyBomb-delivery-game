#!/usr/bin/env node

import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = path.join(root, "src");
const publicRoot = path.join(root, "public");
const outputRoot = path.join(root, "dist-vercel");
const scannedFiles = [path.join(root, "index.html")];

function collectSourceFiles(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const absolutePath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      collectSourceFiles(absolutePath);
      continue;
    }

    if (/\.(?:css|html|json|ts)$/.test(entry.name)) {
      scannedFiles.push(absolutePath);
    }
  }
}

collectSourceFiles(sourceRoot);

const runtimePaths = new Set();
const assetPattern = /\/assets\/[^"'`)\s]+/g;

for (const sourceFile of scannedFiles) {
  const source = readFileSync(sourceFile, "utf8");

  for (const match of source.matchAll(assetPattern)) {
    runtimePaths.add(match[0]);
  }
}

let totalBytes = 0;

for (const runtimePath of [...runtimePaths].sort()) {
  const relativePath = runtimePath.replace(/^\//, "");
  const sourcePath = path.join(publicRoot, relativePath);
  const outputPath = path.join(outputRoot, relativePath);

  if (!existsSync(sourcePath)) {
    throw new Error(`Missing Vercel runtime asset: ${runtimePath}`);
  }

  mkdirSync(path.dirname(outputPath), { recursive: true });
  copyFileSync(sourcePath, outputPath);
  totalBytes += statSync(sourcePath).size;
}

console.log(
  `Prepared Vercel build: ${runtimePaths.size} runtime assets, ${totalBytes} bytes`,
);
