// Compiles src/tailwind.css and publishes it under a content-hashed filename.
//
// Why the hash: netlify.toml serves /styles/* with `max-age=31536000,
// immutable`, which tells browsers never to revalidate. With a fixed filename
// that was a one-way door - a returning visitor kept the stylesheet they had
// cached for a year, so a CSS change (new .btn-cta rules, say) never reached
// them and the affected elements fell back to unstyled defaults. The HTML is
// served `max-age=0, must-revalidate`, so a new filename in the <link> is
// picked up on the next visit. Hashing the name is what makes the immutable
// header honest.
//
// The hashed filename is written back into the committed HTML and into the
// page-generator template, so the repo always reflects what is deployed.

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, readdirSync, unlinkSync, mkdtempSync, rmSync } from 'node:fs';
import { join, dirname, relative } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const STYLES_DIR = join(ROOT, 'www', 'styles');
const TEMPLATE = join(ROOT, 'scripts', 'seo', 'build_pages.py');

// Any /styles/tailwind*.css reference, hashed or not.
const LINK_RE = /\/styles\/tailwind(?:\.[a-f0-9]{8})?\.css/g;

function compile() {
  const tmp = mkdtempSync(join(tmpdir(), 'tmcss-'));
  const out = join(tmp, 'tailwind.css');
  try {
    execFileSync(
      join(ROOT, 'node_modules', '.bin', 'tailwindcss'),
      ['-i', join(ROOT, 'src', 'tailwind.css'), '-o', out, '--minify'],
      { cwd: ROOT, stdio: ['ignore', 'ignore', 'inherit'] },
    );
    return readFileSync(out);
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

function htmlFiles(dir) {
  const found = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) found.push(...htmlFiles(path));
    else if (entry.name.endsWith('.html')) found.push(path);
  }
  return found;
}

const css = compile();
const hash = createHash('sha256').update(css).digest('hex').slice(0, 8);
const filename = `tailwind.${hash}.css`;
const href = `/styles/${filename}`;

writeFileSync(join(STYLES_DIR, filename), css);

// Drop superseded builds so the publish directory holds exactly one stylesheet.
for (const name of readdirSync(STYLES_DIR)) {
  if (/^tailwind(\.[a-f0-9]{8})?\.css$/.test(name) && name !== filename) {
    unlinkSync(join(STYLES_DIR, name));
  }
}

const targets = [...htmlFiles(join(ROOT, 'www')), TEMPLATE];
const rewritten = [];
for (const file of targets) {
  const before = readFileSync(file, 'utf8');
  const after = before.replace(LINK_RE, href);
  if (after !== before) {
    writeFileSync(file, after);
    rewritten.push(relative(ROOT, file));
  }
}

console.log(`css: www/styles/${filename} (${css.length} bytes)`);
console.log(
  rewritten.length
    ? `relinked ${rewritten.length} file(s): ${rewritten.join(', ')}`
    : 'relinked 0 file(s): already current',
);
