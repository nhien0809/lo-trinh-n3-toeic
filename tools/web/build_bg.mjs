// Đóng gói bg.src.js + three.js thành web/bg.js (một file, không cần server).
// Cần esbuild: npm i esbuild (đặt NODE_PATH nếu cài ở chỗ khác). Đổi THREE nếu three.js ở chỗ khác.
import { build } from 'esbuild';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const THREE = process.env.THREE || path.join(os.homedir(), 'Downloads/three.js-master/three.js-master/build/three.module.js');

await build({
  entryPoints: [path.join(here, 'bg.src.js')],
  bundle: true, minify: true, format: 'iife', target: 'es2019',
  outfile: path.join(here, '..', '..', 'web', 'bg.js'),
  plugins: [{ name: 'three', setup(b) { b.onResolve({ filter: /^THREE_PATH$/ }, () => ({ path: THREE })); } }],
  banner: { js: '/* three.js (MIT, threejs.org) + nền động — sinh bởi tools/web/build_bg.mjs */' },
  treeShaking: true,
});
console.log('ok -> web/bg.js');
