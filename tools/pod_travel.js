// Pod travel check for the v7.2 page (11 Nov 2026). Paste into the browser console on designs/v7/ (or run with a page-JS tool),
// ideally with Test kit on, as tools/collide.js is run.
// For Fz and Pz: moves the pod (pd.cupG: body, Ag/AgCl pin, epoxy pot, guide pins, the pigtail's inner part) and the tip cartridge
// (pd.sponge: foam and collar) 3 mm up and 3 mm down along the pod axis, squeezes or stretches the spring to match, and reports
// (1) the guide pins against the ends of their slots, (2) the body's top to the cap's underside, (3) the fill tube's top against the
// cap's top face and the port ring's rim, and (4) every mesh the moving parts pass into (same ray-parity test as tools/collide.js,
// TOL 0.3 mm). Expected contacts are listed in ALLOWED; anything else is reported under "other". Everything is put back afterwards.
(() => {
  const { THREE, band, headset } = window.__neuryo, TOL = 0.3, MAXV = 2500;
  const vis = o => { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; };
  const meshesOf = o => { const a = []; o.traverse(m => { if (m.isMesh && vis(m)) a.push(m); }); return a; };
  const rc = new THREE.Raycaster(), dirs = [new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 1)], all6 = [...dirs, ...dirs.map(d => d.clone().negate())];
  const inside = (B, p) => { let odd = 0; for (const d of dirs) { rc.set(p, d); rc.near = 0; rc.far = 1e4; if (rc.intersectObject(B, false).length % 2) odd++; } return odd >= 2; };
  const depth = (B, p) => { let best = Infinity; for (const d of all6) { rc.set(p, d); const h = rc.intersectObject(B, false); if (h.length) best = Math.min(best, h[0].distance); } return best; };
  const ptsOf = m => { const pos = m.geometry.attributes.position, step = Math.max(1, Math.floor(pos.count / MAXV)), out = []; for (let i = 0; i < pos.count; i += step) out.push(new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld)); return out; };
  // local y range of a mesh in the pod's frame (pd.g)
  const yRange = (m, pd) => { const inv = pd.g.matrixWorld.clone().invert(), pos = m.geometry.attributes.position; let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < pos.count; i++) { const v = new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld).applyMatrix4(inv); lo = Math.min(lo, v.y); hi = Math.max(hi, v.y); } return [lo, hi]; };
  const name = (m, pd) => {
    if (m === pd.body) return 'pod body'; if (m === pd.pin) return 'Ag/AgCl pin'; if (m === pd.pot) return 'epoxy pot'; if (pd.gpins.includes(m)) return 'guide pin';
    if (m === pd.pigIn) return 'pigtail (inner)'; if (m === pd.pigOut) return 'pigtail (loop)'; if (m === pd.sponge) return 'foam'; if (m === pd.collar) return 'cartridge collar';
    if (m === pd.spring) return 'spring'; if (m === pd.puck) return 'stud puck'; if (m === pd.head) return 'snap head';
    if (m.parent === pd.car) return 'carriage'; return (m.userData.part || '?') + ':' + m.geometry.type; };
  const ALLOWED = new Set(['Ag/AgCl pin|pod body', 'Ag/AgCl pin|foam', 'guide pin|pod body', 'guide pin|carriage', 'epoxy pot|pod body', 'pigtail (inner)|epoxy pot', 'pigtail (inner)|pod body',
    'pigtail (inner)|carriage', 'pigtail (inner)|pigtail (loop)', 'foam|pod body', 'cartridge collar|pod body', 'foam|cartridge collar', 'spring|pod body', 'pod body|spring']);
  const out = {};
  for (const [key, pd] of [['fz', band.fzPod], ['pz', band.pzPod]]) {
    const movers = [pd.cupG, pd.sponge], base = movers.map(o => o.position.y), sp = { y: pd.spring.position.y, s: pd.spring.scale.y };
    const res = {};
    for (const dy of [3, -3]) {
      movers.forEach((o, i) => { o.position.y = base[i] + dy; });
      const k = (21.8 - (11.8 + dy)) / 10;   // spring between the pod's top and the cap's underside
      pd.spring.scale.y = k; pd.spring.position.y = 21.8 * (1 - k);
      headset.updateMatrixWorld(true);
      const slotY = pd.car.userData.slots, pins = pd.gpins.map(m => yRange(m, pd)), body = yRange(pd.body, pd);
      const r = {
        pinToSlotEnd_mm: +Math.min(...pins.map(([lo, hi]) => dy > 0 ? slotY[1] - hi : lo - slotY[0])).toFixed(2),
        bodyTopToCapUnderside_mm: +((23.8 - 2.0) - (body[1] - 16.0)).toFixed(2),   // the body mesh includes its fill tube: top face = tube top - 16
        fillTubeTopAboveCapTop_mm: +(body[1] - 23.8).toFixed(2),
        fillTubeTopBelowPortRim_mm: +((23.8 + 2.0) - body[1]).toFixed(2),
        springLength_mm: +(21.8 - (body[1] - 16.0)).toFixed(2),
        expected: [], other: [] };
      const A = [...meshesOf(pd.cupG), ...meshesOf(pd.sponge), pd.spring];
      const Aset = new Set(A), cand = []; headset.traverse(m => { if (m.isMesh && vis(m) && !Aset.has(m) && m.geometry && m.geometry.attributes.position) cand.push(m); });
      const sides = new Map(); for (const m of [...A, ...cand]) { sides.set(m, m.material.side); m.material.side = THREE.DoubleSide; }
      const seen = new Set();
      for (const a of A) { const pa = ptsOf(a), ba = new THREE.Box3().setFromObject(a);
        for (const b of [...A, ...cand]) { if (a === b) continue; const bb = new THREE.Box3().setFromObject(b); if (!ba.intersectsBox(bb)) continue;
          let n = 0, worst = 0; for (const p of pa) { if (!bb.containsPoint(p) || !inside(b, p)) continue; const d = depth(b, p); if (d > TOL) { n++; worst = Math.max(worst, d); } }
          if (!n) continue; const na = name(a, pd), nb = name(b, pd), tag = na + '|' + nb; if (seen.has(tag)) continue; seen.add(tag);
          (ALLOWED.has(tag) || ALLOWED.has(nb + '|' + na) ? r.expected : r.other).push({ pair: tag, n, depth: +worst.toFixed(2) }); } }
      for (const [m, s] of sides) m.material.side = s;
      res[dy > 0 ? 'up3' : 'down3'] = r;
    }
    movers.forEach((o, i) => { o.position.y = base[i]; }); pd.spring.position.y = sp.y; pd.spring.scale.y = sp.s; headset.updateMatrixWorld(true);
    out[key] = res;
  }
  return out;
})();
