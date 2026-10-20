#!/usr/bin/env node
//
// Renders the App Store screenshot set from template.html at the size Apple
// requires for the primary iPhone slot: 1320x2868 (6.9"). The listing's old set
// was exported at 1242x2688, the 6.5" spec, which Apple upscales.
//
//   node ios/screenshots/generate.mjs
//
// Needs Google Chrome installed; no npm dependencies.

import { execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync, rmSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const WIDTH = 1320;
const HEIGHT = 2868;

const here = dirname(fileURLToPath(import.meta.url));
const template = resolve(here, 'template.html');
const outDir = resolve(here, 'out');

const CHROME = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
].find(p => { try { readFileSync(p); return true; } catch { return false; } });

if (!CHROME) {
  console.error('No Chrome-family browser found. Install Google Chrome and retry.');
  process.exit(1);
}

// Slot order is the order the frames appear in template.html, which is the
// order they should sit in App Store Connect.
const frames = [...readFileSync(template, 'utf8').matchAll(/data-name="([^"]+)"/g)].map(m => m[1]);

mkdirSync(outDir, { recursive: true });

for (const name of frames) {
  const out = resolve(outDir, `${name}.png`);
  rmSync(out, { force: true });
  const profile = resolve(outDir, `.chrome-profile-${name}`);
  execFileSync(CHROME, [
    '--headless=new',
    `--user-data-dir=${profile}`,
    '--no-first-run',
    '--hide-scrollbars',
    '--force-device-scale-factor=1',
    '--default-background-color=00000000',
    '--virtual-time-budget=4000',
    `--window-size=${WIDTH},${HEIGHT}`,
    `--screenshot=${out}`,
    `file://${template}?frame=${name.slice(0, 2)}`
  ], { stdio: 'inherit' });
  rmSync(profile, { recursive: true, force: true });
  console.log(`${name}.png  ${WIDTH}x${HEIGHT}`);
}

console.log(`\n${frames.length} frames written to ${outDir}`);
