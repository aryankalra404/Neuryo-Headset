// Head ring path check for the v7 page (11 Nov 2026). Paste into the browser console on designs/v7/ (or run with a page-JS tool).
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
  return { strapToEarTop_mm: +earMin.toFixed(1), strapToStrip_mm: +stripMin.toFixed(1), stripAt, strapTopToBoardUnderside_mm: +bMin.toFixed(2), setBy: bWho, at: bAt,
    strapTopToBatteryCell_mm: cMin === 1e9 ? 'not under the cell' : +cMin.toFixed(2), podBaseAboveStrapTop_mm: +tMin.toFixed(2), podBaseAt: tAt, tightestBendRadius_mm: +rMin.toFixed(1), bendAt: rAt,
    pivotTurn_deg: { left: turn(st[1].p, st[0].p, np[1].p), right: turn(st.at(-2).p, st.at(-1).p, np.at(-2).p) } };
})();
