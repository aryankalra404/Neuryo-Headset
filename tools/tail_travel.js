// Tail travel check for the v7 page (11 Nov 2026; v7.1: the folded spare end). Paste into the browser console on designs/v7/ (or run with a page-JS tool).
// The printed midline band is one length for every head, so its rigid end (the splice to the TPU tail) is a fixed distance behind
// the band's zero (Fpz). The cam lock sits near the inion, 0.9 x nasion-inion behind Fpz. The free tail between them is what the lock
// has to take up: computed here at NI 300, 324 (this head) and 390 mm, with the distances measured along the band as it lies on this
// head (1.2 mm lining) and scaled with NI for the other heads. Also the gap between the splice plate and the lock's jaw at NI 300.
(() => {
  const { band, surf, sites } = window.__neuryo, { strapSamples: S, STRAP_CUM: C, iSpl, lockTh, NI0 } = band;
  const arc = (th0, th1) => { let a = 0, prev = surf(0, th0); const n = Math.ceil(Math.abs(th1 - th0) / 0.05); for (let i = 1; i <= n; i++) { const th = th0 + (th1 - th0) * i / n, q = th <= 90 ? surf(0, th) : surf(180, 180 - th); a += q.p.distanceTo(prev.p); prev = q; } return a; };
  const zeroToBand = arc(sites.Fpz.el, S[0].th);                  // Fpz to the band's front end along the skin (the band is held at the anchor)
  const rigidEnd = zeroToBand + C[iSpl];                           // the band's rigid end, behind the zero (same for every head)
  const iLock = S.reduce((b, s, i) => Math.abs(s.th - lockTh) < Math.abs(S[b].th - lockTh) ? i : b, 0);
  const lockHere = zeroToBand + C[iLock], fz9 = (lockHere) / NI0;   // lock behind the zero on this head, as a fraction of NI
  const free = ni => lockHere * ni / NI0 - rigidEnd;
  const PLATE_HALF = 8, JAW_HALF = 6;   // splice plate 16 mm long, lock jaw 12 mm (model)
  // v7.1 (F2): the spare end past the lock (tab included) folds once in half, so it reaches about half its length above the lock.
  // Room: from the lock to the Pz carriage's rear edge (Pz at 0.6 x that head's size-notch NI from the zero, carriage radius 12.2 mm).
  const { SIZE_NI, TAIL_FOLD } = band, sizeFor = ni => Math.max(1, Math.min(9, Math.floor((ni - 300) / 10) + 1));
  const fold = Object.fromEntries([300, NI0, 390].map(ni => { const spare = free(390) + 45 - free(ni), reach = spare / 2, room = lockHere * ni / NI0 - (0.6 * SIZE_NI[sizeFor(ni) - 1] + 12.2);
    return [Math.round(ni), { sparePastLock_mm: +spare.toFixed(1), foldReach_mm: +reach.toFixed(1), lockToPzCarriage_mm: +room.toFixed(1), margin_mm: +(room - reach).toFixed(1) }]; }));
  return { fold, drawnHere: TAIL_FOLD ? { reachAboveLock_mm: +TAIL_FOLD.reachAboveLock.toFixed(1), eachLayer_mm: +TAIL_FOLD.layer.toFixed(1) } : null, rigidEnd_mm: +rigidEnd.toFixed(1), lockBehindZero_thisHead_mm: +lockHere.toFixed(1), lockAsFractionOfNI: +fz9.toFixed(3),
    freeTail_mm: { 300: +free(300).toFixed(1), 324: +free(NI0).toFixed(1), 390: +free(390).toFixed(1) }, travel_mm: +(free(390) - free(300)).toFixed(1),
    plateToJawGapAt300_mm: +(free(300) - PLATE_HALF - JAW_HALF).toFixed(1) };
})();
