#!/usr/bin/env node
/* Compatibility shim: agents call `playwright-screenshot.js <url> <out> [--full|--scrape]`.
 * Forwards to playwright-extract.js. */
const { spawnSync } = require('child_process');
const path = require('path');
const args = process.argv.slice(2);
if (args.length < 1) { console.error('Usage: playwright-screenshot.js <url> [<out.png>] [--full|--scrape]'); process.exit(1); }
const url = args[0];
const second = args[1];
const flags = args.slice(1).filter(a => a.startsWith('--'));
const out = (second && !second.startsWith('--')) ? second : null;
const fwd = [path.join(__dirname, 'playwright-extract.js'), url];
if (flags.includes('--scrape')) {
  fwd.push('--scrape');
  if (out) fwd.push('--output', out);
} else {
  fwd.push('--screenshot');
  if (flags.includes('--full')) fwd.push('--full');
  if (out) fwd.push('--output', out);
}
const r = spawnSync('node', fwd, { stdio: 'inherit' });
process.exit(r.status || 0);
