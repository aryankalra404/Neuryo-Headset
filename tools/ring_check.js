// Head ring path check for the v7 page (11 Nov 2026; v7.1: flat print outline). Paste into the browser console on designs/v7/ (or run with a page-JS tool).
// The ring strap (14 x 3 mm on its lining) from pivot to pivot: smallest distance from its lower edge to the top of the ear, smallest
// distance from the strap (lining underside, full width) to the forehead strip, and the gap between the strap's top and the board's
// underside (and its bottom-side parts) where it runs under the left pod; the same for the battery cell in the right pod.
// Also the tightest bend along the whole loop (ring strap and nape section) and the angle between the two at each pivot.
(() => {
  const { THREE, ring, pod } = window.__neuryo, { frontSamples: S, ringOff, STRAP_W, STRAP_T, earTop, STRIP, RING } = ring, V = THREE.Vector3;
  const ear = window.__neuryo.surf(earTop.az, earTop.el).p;
  const strip = []; STRIP.updateMatrixWorld(true); STRIP.traverse(m => { if (!m.isMesh) return; const g = m.geometry.attributes.position; for (let i = 0; i < g.count; i++) strip.push(new V().fromBufferAttribute(g, i).applyMatrix4(m.matrixWorld)); });
  const pg = pod.pcbGroup; pg.updateMatrixWorld(true);
  const boxes = []; pg.children.forEach(m => { if (!m.isMesh || !m.geometry) return; m.geometry.computeBoundingBox(); const b = m.geometry.boundingBox.clone(); b.min.add(m.position); b.max.add(m.position); if (b.min.z < -0.79) boxes.push({ b, ref: m.userData.ref || (m === pg.children[0] ? 'board' : m.userData.part) }); });
  const bg = pod.battG; bg.updateMatrixWorld(true); const cell = bg.children[0]; cell.geometry.computeBoundingBox(); const cb = cell.geometry.boundingBox.clone(); cb.min.add(cell.position); cb.max.add(cell.position);
  let earMin = 1e9, stripMin = 1e9, stripAt = null, bMin = 1e9, bWho = null, bAt = null, cMin = 1e9;
  for (const s of S) { const down = s.side.clone().multiplyScalar(s.side.y < 0 ? 1 : -1), aL = Math.abs(s.az);
    const lo = s.p.clone().addScaledVector(down, STRAP_W / 2); earMin = Math.min(earMin, lo.distanceTo(ear));
    for (const w of [-7, -3.5, 0, 3.5, 7]) { const p0 = s.p.clone().addScaledVector(s.side, w);
      if (aL < 70) for (const q of strip) { const d = q.distanceTo(p0); if (d < stripMin) { stripMin = d; stripAt = [+s.az.toFixed(1), +s.el.toFixed(1)]; } }
      const top = p0.clone().addScaledVector(s.n, ringOff(s) + STRAP_T);
      if (s.az > 0) { const L = pg.worldToLocal(top.clone()); for (const { b, ref } of boxes) if (L.x > b.min.x - 0.3 && L.x < b.max.x + 0.3 && L.y > b.min.y - 0.3 && L.y < b.max.y + 0.3) { const g = b.min.z - L.z; if (g < bMin) { bMin = g; bWho = ref; bAt = [+s.az.toFixed(1), +s.el.toFixed(1)]; } } }
      else { const L = bg.worldToLocal(top.clone()); if (L.x > cb.min.x && L.x < cb.max.x && L.y > cb.min.y && L.y < cb.max.y) cMin = Math.min(cMin, cb.min.z - L.z); } } }
  // pod base over the strap (the tunnel): for every base vertex within the strap's width, its height off the skin minus the strap's top
  let tMin = 1e9, tAt = null;
  for (const base of [pod.base, pod.battBase].filter(Boolean)) { base.updateMatrixWorld(true); const g = base.geometry.attributes.position;
    for (let i = 0; i < g.count; i++) { const v = new V().fromBufferAttribute(g, i).applyMatrix4(base.matrixWorld);
      let best = null, bd = 1e9; for (const s of S) { const d = s.p.distanceToSquared(v); if (d < bd) { bd = d; best = s; } }
      const r = v.clone().sub(best.p), lat = Math.abs(r.dot(best.side)), along = Math.abs(r.dot(best.t)), h = r.dot(best.nn);   // in the strap's own frame
      if (lat < STRAP_W / 2 && along < 1.0) {   // the strap's rounded edge (the page's sweep profile): top at lateral x
        const c = Math.pow(Math.min(1, 2 * lat / STRAP_W), 1 / 0.22), top = STRAP_T / 2 * Math.pow(Math.sqrt(Math.max(0, 1 - c * c)), 0.32) + STRAP_T / 2;
        const g2 = h - (ringOff(best) + top); if (g2 < tMin) { tMin = g2; tAt = [+best.az.toFixed(1), +lat.toFixed(1)]; } } } }
  // bends: smallest radius of the centre line (on the head, so it includes the head's own curvature) and the turn across each pivot
  const loop = [...RING.strap, ...RING.nape.slice().reverse()].filter((s, i, a) => i === 0 || s.p.distanceTo(a[i - 1].p) > 0.05); let rMin = 1e9, rAt = null;
  for (let i = 1; i < loop.length - 1; i++) { const a = loop[i - 1].p, b = loop[i].p, c = loop[i + 1].p; const t1 = b.clone().sub(a), t2 = c.clone().sub(b); const ang = t1.angleTo(t2), ds = (t1.length() + t2.length()) / 2; if (ds > 0.05 && ang > 1e-6) { const r = ds / ang; if (r < rMin) { rMin = r; rAt = [+loop[i].az.toFixed(1), +loop[i].el.toFixed(1)]; } } }
  const turn = (a, b, c) => +(b.clone().sub(a).angleTo(c.clone().sub(b)) * 57.3).toFixed(1);
  const st = RING.strap, np = RING.nape;
  // v7.1 (F5): flat print outline. The centre line laid into its best-fit plane with the same length and the same in-plane curve:
  // project onto the plane, keep each step's turning angle there, rebuild with the 3D step lengths.
  const P = S.map(x => x.p.clone().addScaledVector(x.n, ringOff(x) + STRAP_T / 2)), c0 = P.reduce((a, p) => a.add(p), new V()).multiplyScalar(1 / P.length);
  let xx = 0, xy = 0, xz = 0, yy = 0, yz = 0, zz = 0; for (const p of P) { const d = p.clone().sub(c0); xx += d.x * d.x; xy += d.x * d.y; xz += d.x * d.z; yy += d.y * d.y; yz += d.y * d.z; zz += d.z * d.z; }
  const inv = new THREE.Matrix3().set(xx, xy, xz, xy, yy, yz, xz, yz, zz).invert(); let nrm = new V(0.3, 1, 0.2).normalize(); for (let i = 0; i < 60; i++) nrm = nrm.applyMatrix3(inv).normalize();
  const u1 = new V().crossVectors(nrm, new V(1, 0, 0)).normalize(), u2 = new V().crossVectors(nrm, u1);
  const Q = P.map(p => { const d = p.clone().sub(c0); return [d.dot(u1), d.dot(u2)]; }); let dev = 0; for (const p of P) dev = Math.max(dev, Math.abs(p.clone().sub(c0).dot(nrm)));
  const flat = [[0, 0]]; let ang = Math.atan2(Q[1][1] - Q[0][1], Q[1][0] - Q[0][0]), len3 = 0;
  for (let i = 1; i < P.length; i++) { const L3 = P[i].distanceTo(P[i - 1]); len3 += L3; if (i > 1) { const a0 = Math.atan2(Q[i - 1][1] - Q[i - 2][1], Q[i - 1][0] - Q[i - 2][0]), a1 = Math.atan2(Q[i][1] - Q[i - 1][1], Q[i][0] - Q[i - 1][0]); let da = a1 - a0; while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI; ang += da; }
    const q = flat.at(-1); flat.push([q[0] + L3 * Math.cos(ang), q[1] + L3 * Math.sin(ang)]); }
  const xs = flat.map(q => q[0]), ys = flat.map(q => q[1]), W = Math.max(...xs) - Math.min(...xs), H = Math.max(...ys) - Math.min(...ys);
  // align the outline's long side with x for the bed size: try rotations
  let best = [1e9, 0, 0]; for (let a = 0; a < Math.PI; a += Math.PI / 180) { const c = Math.cos(a), si = Math.sin(a), rx = flat.map(q => q[0] * c - q[1] * si), ry = flat.map(q => q[0] * si + q[1] * c), w = Math.max(...rx) - Math.min(...rx), h = Math.max(...ry) - Math.min(...ry); if (Math.max(w, h) < best[0]) best = [Math.max(w, h), w, h]; }
  const flatPrint = { developedLength_mm: +len3.toFixed(0), outline_mm: [+best[1].toFixed(0), +best[2].toFixed(0)], outOfPlaneBefore_mm: +dev.toFixed(1), fitsBed220: best[0] + STRAP_W < 220 };
  return { flatPrint, strapToEarTop_mm: +earMin.toFixed(1), strapToStrip_mm: +stripMin.toFixed(1), stripAt, strapTopToBoardUnderside_mm: +bMin.toFixed(2), setBy: bWho, at: bAt,
    strapTopToBatteryCell_mm: cMin === 1e9 ? 'not under the cell' : +cMin.toFixed(2), podBaseAboveStrapTop_mm: +tMin.toFixed(2), podBaseAt: tAt, tightestBendRadius_mm: +rMin.toFixed(1), bendAt: rAt,
    pivotTurn_deg: { left: turn(st[1].p, st[0].p, np[1].p), right: turn(st.at(-2).p, st.at(-1).p, np.at(-2).p) } };
})();
