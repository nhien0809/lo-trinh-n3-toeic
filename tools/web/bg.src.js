// Nền động three.js dùng chung cho tracker + trang ôn từ.
// Bundle: node tools/web/build_bg.mjs  ->  web/bg.js (IIFE, chạy được qua file://)
import * as THREE from 'THREE_PATH';

function css(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

function start() {
  const canvas = document.createElement('canvas');
  canvas.id = 'bg3d';
  canvas.setAttribute('aria-hidden', 'true');
  Object.assign(canvas.style, { position: 'fixed', inset: '0', width: '100%', height: '100%', zIndex: '-1', pointerEvents: 'none' });
  document.body.prepend(canvas);

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch (e) { canvas.remove(); return; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 200);
  camera.position.set(0, 7, 22);
  camera.lookAt(0, 0, 0);

  // Lưới điểm dạng sóng
  const NX = 90, NZ = 50, GAP = 0.55;
  const pos = new Float32Array(NX * NZ * 3);
  let i = 0;
  for (let x = 0; x < NX; x++) for (let z = 0; z < NZ; z++) {
    pos[i++] = (x - NX / 2) * GAP; pos[i++] = 0; pos[i++] = (z - NZ / 2) * GAP;
  }
  const waveGeo = new THREE.BufferGeometry();
  waveGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const waveMat = new THREE.PointsMaterial({ size: 0.09, transparent: true, opacity: 0.55, depthWrite: false });
  const wave = new THREE.Points(waveGeo, waveMat);
  wave.position.y = -3;
  scene.add(wave);

  // Hạt trôi (như cánh hoa)
  const NP = 140;
  const pp = new Float32Array(NP * 3), vel = new Float32Array(NP);
  for (let k = 0; k < NP; k++) {
    pp[k * 3] = (Math.random() - 0.5) * 50; pp[k * 3 + 1] = Math.random() * 20 - 4; pp[k * 3 + 2] = (Math.random() - 0.5) * 30;
    vel[k] = 0.004 + Math.random() * 0.01;
  }
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pp, 3));
  const pMat = new THREE.PointsMaterial({ size: 0.18, transparent: true, opacity: 0.7, depthWrite: false });
  const petals = new THREE.Points(pGeo, pMat);
  scene.add(petals);

  function applyTheme() {
    waveMat.color.set(css('--bg-wave', '#6b8cff'));
    pMat.color.set(css('--bg-petal', '#ff8fb1'));
  }
  applyTheme();
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', applyTheme);
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  function resize() {
    const w = window.innerWidth, h = window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener('resize', resize);

  let mx = 0, my = 0;
  window.addEventListener('pointermove', e => { mx = e.clientX / window.innerWidth - 0.5; my = e.clientY / window.innerHeight - 0.5; }, { passive: true });

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let t = 0, running = true;
  function frame() {
    if (!running) return;
    t += reduce ? 0 : 0.012;
    const a = waveGeo.attributes.position.array;
    for (let j = 0; j < a.length; j += 3) {
      const x = a[j], z = a[j + 2];
      a[j + 1] = Math.sin(x * 0.35 + t) * 0.6 + Math.cos(z * 0.45 + t * 0.8) * 0.5;
    }
    waveGeo.attributes.position.needsUpdate = true;
    if (!reduce) {
      for (let k = 0; k < NP; k++) {
        pp[k * 3 + 1] -= vel[k]; pp[k * 3] += Math.sin(t + k) * 0.004;
        if (pp[k * 3 + 1] < -5) pp[k * 3 + 1] = 16;
      }
      pGeo.attributes.position.needsUpdate = true;
    }
    camera.position.x += (mx * 3 - camera.position.x) * 0.03;
    camera.position.y += (7 - my * 2 - camera.position.y) * 0.03;
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
    if (!reduce) requestAnimationFrame(frame);
  }
  document.addEventListener('visibilitychange', () => {
    const vis = document.visibilityState === 'visible';
    if (vis && !running) { running = true; requestAnimationFrame(frame); }
    else if (!vis) running = false;
  });
  requestAnimationFrame(frame);
  window.__bgRedraw = () => { applyTheme(); if (reduce) requestAnimationFrame(frame); };
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
