# Docs

| File | What it covers |
|---|---|
| [v1.md](v1.md) | v1 · 26 Oct design: spec and what's on the page |
| [v2.md](v2.md) | v2 · 29 Oct research plan: spec, every change from v1 and why, what's still unproven |
| [v3.md](v3.md) | v3 · 29 Oct review: spec, channel map, every change from v2 with how sure each one is, budget corrections, what's still unproven |
| [v4.md](v4.md) | v4 · 7 Nov product design: what the product is, spec, channel map, every change from v3 with how sure each one is, fit across 500 to 580 mm heads and 300 to 390 mm nasion–inion, the v4.4 review fixes (size range, printed band, halo lining, foam tip), the buildable frame (buy or print), cleaning model, page controls, what's still open |
| [v5.md](v5.md) | v5 · 7 Nov trial: v4.4 with the board in a side box above the left ear: why (real board size, crowded back), every change from v4, rev B changes from rev A, where competitors put their electronics, weight and balance, what's still open |
| [head.md](head.md) | The shared mannequin head: how it was made, how to use it, all 77 measured 10-10 positions and the mastoid points M1/M2 |

## Keeping these up to date
- Every new design gets its own `vN.md`: a spec table, a "What changed from vN-1, and why" table with decision and evidence IDs from Neuryo-Research, and the open items.
- Mark a design's status (current plan or retired, and by which decision) in its doc and in `designs/designs.json`.
- If the shared head is rebuilt, regenerate `head.md` from `designs/shared/head/head.json`.
