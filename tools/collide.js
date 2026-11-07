// Collision check for the v5 page (8 Nov 2026). Paste into the browser console on designs/v5/ (or run with a page-JS tool).
// For every pair of visible meshes in the headset, samples the vertices of one and tests whether they lie inside the other
// (ray parity along 3 axes, 2 of 3 must agree). Reports pairs with points more than TOL inside, with the deepest point.
// Meshes in the same printed part can be listed in SAME so their overlaps are ignored.
(() => {
  const { THREE, headset } = window.__neuryo;
  const TOL = 0.3, MAXV = 2500;
  headset.updateMatrixWorld(true);
  const vis = o => { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; };
  const meshes = [];
  headset.traverse(m => { if (m.isMesh && vis(m) && m.geometry && m.geometry.attributes.position) meshes.push(m); });
  const info = meshes.map(m => {
    const g = m.geometry, pos = g.attributes.position, step = Math.max(1, Math.floor(pos.count / MAXV)), pts = [];
    for (let i = 0; i < pos.count; i += step) pts.push(new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld));
    const box = new THREE.Box3().setFromObject(m);
    const side = m.material.side; return { m, pts, box, side };
  });
  const rc = new THREE.Raycaster(); rc.firstHitOnly = false;
  const dirs = [new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 1)];
  const all6 = [...dirs, ...dirs.map(d => d.clone().negate())];
  function inside(B, p) {
    let odd = 0;
    for (const d of dirs) { rc.set(p, d); rc.near = 0; rc.far = 1e4; const h = rc.intersectObject(B, false); if (h.length % 2) odd++; }
    return odd >= 2;
  }
  function depth(B, p) { let best = Infinity; for (const d of all6) { rc.set(p, d); const h = rc.intersectObject(B, false); if (h.length) best = Math.min(best, h[0].distance); } return best; }
  const out = [];
  for (const I of info) I.m.material.side = THREE.DoubleSide;
  for (let a = 0; a < info.length; a++) for (let b = 0; b < info.length; b++) {
    if (a === b) continue;
    const A = info[a], B = info[b];
    if (!A.box.intersectsBox(B.box)) continue;
    if (A.m.parent === B.m.parent && A.m.userData.part === B.m.userData.part && A.m.userData.onePrint) continue;
    let n = 0, worst = 0, wp = null;
    for (const p of A.pts) { if (!B.box.containsPoint(p)) continue; if (!inside(B.m, p)) continue; const d = depth(B.m, p); if (d > TOL) { n++; if (d > worst) { worst = d; wp = p; } } }
    if (n) out.push({ a: (A.m.userData.part || '?') + ':' + (A.m.name || A.m.geometry.type) + '#' + a, b: (B.m.userData.part || '?') + ':' + (B.m.name || B.m.geometry.type) + '#' + b, n, depth: +worst.toFixed(2), at: wp.toArray().map(v => +v.toFixed(1)) });
  }
  for (const I of info) I.m.material.side = I.side;
  out.sort((x, y) => y.depth - x.depth);
  return { meshes: meshes.length, hits: out };
})();
