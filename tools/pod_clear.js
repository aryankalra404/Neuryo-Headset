// Pod clearance check for the v7.2 page (11 Nov 2026). Paste into the browser console on designs/v7/ (or run with a page-JS tool).
// Reports, for the v7.2 hair pods and carriages:
//  - the slit and each pin slot to the nearest foot edge (degrees, and mm along the outer wall at r 12.2)
//  - the stud puck and the snap head to the fill tube with the pod at its upper stop (radial gap, mm)
//  - the guide-pin ends and the puck to the nearest band lead clip, with Pz at its size 1 and size 9 notch (and Fz where it is)
//  - the cartridge nose and the pod body to the midline band (the Pz window's ends and edges) with Pz at size 1 and size 9
// Pz is moved by re-placing its whole group (pod, carriage and all) at the band position of that size's notch, as tools in v7.1 did;
// the leads are drawn for this head's size and do not follow. Everything is put back afterwards.
(() => {
  const { THREE, band, headset, surf } = window.__neuryo, { strapSamples: S, STRAP_CUM: C, SIZE_NI, NI0, iPzC, cumAtTh, LEAD_CLIPS, WIN } = band;
  const UP = new THREE.Vector3(0, 1, 0), RO = 12.2, FOOT = 0.62, deg = r => r * 180 / Math.PI;
  const wrap = a => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };
  const out = { feet: {}, puckToTube: {}, clips: {}, window: {} };
  // 1. slit and slots to the feet (angles in the pod's frame; feet at aL and aL + PI, half-width 0.62 rad)
  for (const [key, pd] of [['fz', band.fzPod], ['pz', band.pzPod]]) {
    const aL = pd.aN - Math.sign(wrap(pd.aP[0] - pd.aN)) * Math.PI / 3, feet = [aL, aL + Math.PI];
    const gaps = [['slit', pd.aN, 1.6], ['pin slot 1', pd.aP[0], 2.1], ['pin slot 2', pd.aP[1], 2.1]];
    out.feet[key] = gaps.map(([n, a, w]) => { const h = w / 2 / 9.8, d = Math.min(...feet.map(f => Math.abs(wrap(a - f)))) - FOOT - h;
      return { gap: n, centreToFootCentre_deg: +deg(Math.min(...feet.map(f => Math.abs(wrap(a - f))))).toFixed(1), edgeToFootEdge_deg: +deg(d).toFixed(1), edgeToFootEdge_mm: +(d * RO).toFixed(2) }; });
  }
  // helpers
  const local = (m, root) => { const inv = root.matrixWorld.clone().invert(), pos = m.geometry.attributes.position, a = [];
    for (let i = 0; i < pos.count; i++) a.push(new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld).applyMatrix4(inv)); return a; };
  const world = m => { const pos = m.geometry.attributes.position, a = []; for (let i = 0; i < pos.count; i++) a.push(new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld)); return a; };
  const tris = m => { const pos = m.geometry.attributes.position, idx = m.geometry.index, n = idx ? idx.count : pos.count, t = [];
    const v = i => new THREE.Vector3().fromBufferAttribute(pos, idx ? idx.getX(i) : i).applyMatrix4(m.matrixWorld);
    for (let i = 0; i < n; i += 3) t.push(new THREE.Triangle(v(i), v(i + 1), v(i + 2))); return t; };
  const meshDist = (A, B, near = null) => {   // min distance from A's vertices to B's triangles and back
    const pa = A.flatMap(world), tb = B.flatMap(tris), pb = B.flatMap(world), ta = A.flatMap(tris), q = new THREE.Vector3();
    const box = new THREE.Box3().setFromPoints(pa).expandByScalar(near || 40), tbn = tb.filter(t => box.containsPoint(t.a) || box.containsPoint(t.b) || box.containsPoint(t.c));
    let best = Infinity, at = null;
    for (const p of pa) for (const t of tbn) { t.closestPointToPoint(p, q); const d = p.distanceTo(q); if (d < best) { best = d; at = q.clone(); } }
    for (const p of pb) { if (!box.containsPoint(p)) continue; for (const t of ta) { t.closestPointToPoint(p, q); const d = p.distanceTo(q); if (d < best) { best = d; at = p.clone(); } } }
    return { d: best, at };
  };
  // 2. puck and snap head to the fill tube at the upper stop (tube: r 2.0 about the pod axis, top at 27.8 + 3)
  for (const [key, pd] of [['fz', band.fzPod], ['pz', band.pzPod]]) {
    const tubeTop = 27.8 + 3, r = m => Math.min(...local(m, pd.g).filter(v => v.y <= tubeTop).map(v => Math.hypot(v.x, v.z)));
    out.puckToTube[key] = { puck_mm: +(r(pd.puck) - 2.0).toFixed(2), snapHead_mm: +(r(pd.head) - 2.0).toFixed(2), tubeTopAtUpperStop: tubeTop, snapHeadBottom: +Math.min(...local(pd.head, pd.g).map(v => v.y)).toFixed(2) };
  }
  // 3 and 4: Pz at sizes 1 and 9
  const clipMeshes = []; LEAD_CLIPS.traverse(m => { if (m.isMesh) clipMeshes.push(m); });
  const clipSet = new Set(clipMeshes), strap = []; LEAD_CLIPS.parent.traverse(m => { if (m.isMesh && !clipSet.has(m)) strap.push(m); });   // the band and everything printed with it
  const thAtCum = c => { let i = 0; while (i < C.length - 2 && C[i + 1] < c) i++; const f = (c - C[i]) / (C[i + 1] - C[i]); return S[i].th + f * (S[i + 1].th - S[i].th); };
  // overlap test (as tools/collide.js, TOL 0.3 mm) between the whole Pz group and everything else, for the moved carriage
  const rc = new THREE.Raycaster(), dirs = [new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 1)], all6 = [...dirs, ...dirs.map(d => d.clone().negate())];
  const vis = o => { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; };
  const inside = (B, p) => { let odd = 0; for (const d of dirs) { rc.set(p, d); rc.near = 0; rc.far = 1e4; if (rc.intersectObject(B, false).length % 2) odd++; } return odd >= 2; };
  const depth = (B, p) => { let best = Infinity; for (const d of all6) { rc.set(p, d); const h = rc.intersectObject(B, false); if (h.length) best = Math.min(best, h[0].distance); } return best; };
  const overlaps = pd => { const A = [], others = []; pd.g.traverse(m => { if (m.isMesh && vis(m)) A.push(m); }); const As = new Set(A);
    headset.traverse(m => { if (m.isMesh && vis(m) && !As.has(m) && m.geometry && m.geometry.attributes.position && !(m.userData.part === 'pz' && m.geometry.type === 'TubeGeometry')) others.push(m); });
    const sides = new Map(); for (const m of [...A, ...others]) { sides.set(m, m.material.side); m.material.side = THREE.DoubleSide; }
    const hits = [];
    for (const [X, Y] of [[A, others], [others, A]]) for (const a of X) { const ba = new THREE.Box3().setFromObject(a);
      for (const b of Y) { const bb = new THREE.Box3().setFromObject(b); if (!ba.intersectsBox(bb)) continue; let n = 0, w = 0;
        for (const p of world(a)) { if (!bb.containsPoint(p) || !inside(b, p)) continue; const d = depth(b, p); if (d > 0.3) { n++; w = Math.max(w, d); } }
        if (n) hits.push((a.userData.part || '?') + ':' + a.geometry.type + ' in ' + (b.userData.part || '?') + ':' + b.geometry.type + ' (' + w.toFixed(2) + ')'); } }
    for (const [m, s] of sides) m.material.side = s; return hits; };
  const pz = band.pzPod, keep = { p: pz.g.position.clone(), q: pz.g.quaternion.clone() };
  let th0 = 0, bd = Infinity; for (let th = 60; th < 160; th += 0.01) { const d = surf(0, th).p.distanceTo(keep.p); if (d < bd) { bd = d; th0 = th; } }
  const c0 = cumAtTh(th0);
  const measure = (pd, tag) => {
    headset.updateMatrixWorld(true);
    const pins = meshDist(pd.gpins, clipMeshes), puck = meshDist([pd.puck], clipMeshes);
    const pod = meshDist([pd.body, pd.collar, pd.sponge], strap, 30), cum = cumAtTh((() => { let t = 0, b = Infinity; for (let th = 60; th < 170; th += 0.02) { const d = surf(0, th).p.distanceTo(pod.at); if (d < b) { b = d; t = th; } } return t; })());
    const mm = d => d === Infinity ? 'over 40' : +d.toFixed(2);
    out.clips[tag] = { guidePinEnds_mm: mm(pins.d), puck_mm: mm(puck.d) };
    out.window[tag] = { nearestBand_mm: +pod.d.toFixed(2), nearestPointAlongBand_mm: +cum.toFixed(1) };
  };
  measure(band.fzPod, 'fz');
  for (const k of [1, 9]) {
    const c = c0 + 0.6 * (SIZE_NI[k - 1] - NI0), Sk = surf(0, thAtCum(c));
    pz.g.position.copy(Sk.p); pz.g.quaternion.setFromUnitVectors(UP, Sk.n);
    measure(pz, 'pz size ' + k); out.window['pz size ' + k].overlapsWithOtherParts = overlaps(pz);   // the Pz lead (drawn for this head's size) is left out
    Object.assign(out.window['pz size ' + k], { podCentreAlongBand_mm: +c.toFixed(1), pzWindow_mm: WIN[1].map(v => +v.toFixed(1)),
      // along the band: the 14.2 mm nose flange and body against the window's two ends
      noseToWindowFrontEnd_mm: +(c - 7.1 - WIN[1][0]).toFixed(1), noseToWindowRearEnd_mm: +(WIN[1][1] - c - 7.1).toFixed(1) });
  }
  pz.g.position.copy(keep.p); pz.g.quaternion.copy(keep.q); headset.updateMatrixWorld(true);
  return out;
})();
