// Exports the v6 headset from the v6 page to designs/v6/neuryo-v6.glb for the try-on page (10 Nov 2026).
// Product mode, parts inside the pods (board, battery) left out. Serve the repo root, then:
//   python3 -m http.server 8765 &   node tools/export_glb.js http://localhost:8765/designs/v6/ designs/v6/neuryo-v6.glb
// Needs playwright-core and Chrome (set PLAYWRIGHT_CORE and CHROME if they are not on the default paths).
// v7 (11 Nov): node tools/export_glb.js http://localhost:8765/designs/v7/ designs/v7/neuryo-v7.glb. The nasion gauge and the test-kit
// chin strap are hidden in the default view, so the try-on model leaves them out.
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const fs = require('fs');
(async () => {
  const [url, out] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: process.env.CHROME || undefined, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
  const p = await (await b.newContext({ viewport: { width: 1200, height: 800 } })).newPage();
  p.on('pageerror', e => console.error('page error:', e.message));
  await p.goto(url, { waitUntil: 'load' });
  await p.waitForFunction(() => window.__neuryo, null, { timeout: 90000 });
  await p.waitForTimeout(2000);
  const res = await p.evaluate(async () => {
    const { GLTFExporter } = await import('three/addons/exporters/GLTFExporter.js');
    const { headset } = window.__neuryo; let hidden = 0, meshes = 0;
    const BOARD = new Set(['pcb', 'power', 'prot', 'ads', 'esp', 'usb', 'imu', 'ecg']);   // everything on the board, plus the battery cell (use: inside)
    headset.traverse(m => { if (m.isMesh && m.visible && (BOARD.has(m.userData.part) || m.userData.use === 'inside')) { m.visible = false; hidden++; } });
    headset.updateMatrixWorld(true);
    const buf = await new GLTFExporter().parseAsync(headset, { binary: true, onlyVisible: true });
    const vis = o => { for (let q = o; q; q = q.parent) if (!q.visible) return false; return true; };
    headset.traverse(m => { if (m.isMesh && vis(m)) meshes++; });
    const u8 = new Uint8Array(buf); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    return { b64: btoa(s), hidden, meshes };
  });
  fs.writeFileSync(out, Buffer.from(res.b64, 'base64'));
  console.log('wrote', out, fs.statSync(out).size, 'bytes;', res.meshes, 'meshes,', res.hidden, 'inside-the-pod meshes left out');
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
