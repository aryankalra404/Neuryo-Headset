// Pod fit check for the v7 page (11 Nov 2026; v7.1: 3.0 mm rule, outer box and overall width). Paste into the browser console on designs/v7/ (or run with a page-JS tool).
// For every mesh on the board (pcbGroup) takes its 8 bounding-box corners in world space and finds how far each lies inside the left
// pod cover's outer surface (closest point on the cover's triangles; inside = a ray along the board normal meets the cover).
// v7.1: needs at least 3.0 mm (0.5 mm air + 2 mm wall + 0.5 mm print margin). Also reports the pod's size: face height off the skin at the board centre along
// the board normal, and the footprint along the skin through the pod centre (front-back and up-down). Model estimates throughout.
(() => {
  const { THREE, pod, surf } = window.__neuryo, { cover, pcbGroup, S0, F0, MOD } = pod;
  cover.updateMatrixWorld(true); pcbGroup.updateMatrixWorld(true);
  const pos = cover.geometry.attributes.position, idx = cover.geometry.index.array, tris = [];
  for (let i = 0; i < idx.length; i += 3) tris.push(new THREE.Triangle(...[0, 1, 2].map(k => new THREE.Vector3().fromBufferAttribute(pos, idx[i + k]).applyMatrix4(cover.matrixWorld))));
  const rc = new THREE.Raycaster(), cp = new THREE.Vector3(), dside = cover.material.side; cover.material.side = THREE.DoubleSide;
  const res = [];
  pcbGroup.traverse(m => { if (!m.isMesh || !m.geometry) return; m.geometry.computeBoundingBox(); const bb = m.geometry.boundingBox;
    for (let c = 0; c < 8; c++) { const p = new THREE.Vector3(c & 1 ? bb.max.x : bb.min.x, c & 2 ? bb.max.y : bb.min.y, c & 4 ? bb.max.z : bb.min.z).applyMatrix4(m.matrixWorld);
      let d = Infinity; for (const t of tris) { t.closestPointToPoint(p, cp); const e = cp.distanceTo(p); if (e < d) d = e; }
      rc.set(p, F0.n); const inside = rc.intersectObject(cover, false).length % 2 === 1;
      res.push({ clr: inside ? d : -d, who: m.userData.ref || m.userData.part || m.geometry.type, p }); } });
  cover.material.side = dside;
  res.sort((a, b) => a.clr - b.clr);
  const worst = {}; for (const r of res) if (!(r.who in worst)) worst[r.who] = +r.clr.toFixed(2);
  const len = (pts) => pts.reduce((a, p, i) => i ? a + p.distanceTo(pts[i - 1]) : 0, 0), N = 60;
  const fb = len(Array.from({ length: N + 1 }, (_, i) => surf(MOD.azC - MOD.azH + 2 * MOD.azH * i / N, MOD.elC).p));
  const lo = MOD.low ? MOD.low(MOD.azC) : MOD.elC - MOD.elH, hi = MOD.high ? MOD.high(MOD.azC) : MOD.elC + MOD.elH;
  const ud = len(Array.from({ length: N + 1 }, (_, i) => surf(MOD.azC, lo + (hi - lo) * i / N).p));
  rc.set(S0.p.clone().addScaledVector(F0.n, 60), F0.n.clone().negate()); const top = rc.intersectObject(cover, false)[0];
  // v7.1: outer box of the left pod (every vertex of part 'module' with x > 20 mm, on the pod frame at surf(100, 34)) and the
  // headset's overall width (2 x the largest |x| of any visible headset mesh). Same measure as the v7 review; works on v6 too.
  const box = (() => { const { parts, headset } = window.__neuryo, S = surf(100, 34), up = new THREE.Vector3(0, 1, 0), fx = new THREE.Vector3().crossVectors(up, S.n).normalize(), fy = new THREE.Vector3().crossVectors(S.n, fx).normalize();
    const vis = o => { for (let q = o; q; q = q.parent) if (!q.visible) return false; return true; };
    const r = { x: [1e9, -1e9], y: [1e9, -1e9], n: [1e9, -1e9] }; let wx = 0;
    for (const m of parts.module.meshes) { if (!vis(m)) continue; m.updateMatrixWorld(true); const g = m.geometry.attributes.position;
      for (let i = 0; i < g.count; i++) { const v = new THREE.Vector3().fromBufferAttribute(g, i).applyMatrix4(m.matrixWorld); if (v.x <= 20) continue; const d = v.clone().sub(S.p);
        for (const [k, a] of [['x', fx], ['y', fy], ['n', S.n]]) { const q = d.dot(a); r[k][0] = Math.min(r[k][0], q); r[k][1] = Math.max(r[k][1], q); } } }
    headset.updateMatrixWorld(true); headset.traverse(m => { if (!m.isMesh || !vis(m)) return; const g = m.geometry.attributes.position; for (let i = 0; i < g.count; i++) wx = Math.max(wx, Math.abs(new THREE.Vector3().fromBufferAttribute(g, i).applyMatrix4(m.matrixWorld).x)); });
    return { podLength_mm: +(r.x[1] - r.x[0]).toFixed(1), podHeight_mm: +(r.y[1] - r.y[0]).toFixed(1), podThickness_mm: +(r.n[1] - r.n[0]).toFixed(1), headsetWidth_mm: +(2 * wx).toFixed(1) }; })();
  return { outerBox: box, smallest: +res[0].clr.toFixed(2), setBy: res[0].who, below3_0: res.filter(r => r.clr < 3.0).length, worstPerPart: Object.fromEntries(Object.entries(worst).slice(0, 8)),
    faceHeight_mm: top ? +(60 - top.distance).toFixed(1) : null, footprintAlongSkin_mm: [+fb.toFixed(1), +ud.toFixed(1)] };
})();
