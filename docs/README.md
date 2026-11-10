# Docs

| File | What it covers |
|---|---|
| [v1.md](v1.md) | v1 · 26 Oct design: spec and what's on the page |
| [v2.md](v2.md) | v2 · 29 Oct research plan: spec, every change from v1 and why, what's still unproven |
| [v3.md](v3.md) | v3 · 29 Oct review: spec, channel map, every change from v2 with how sure each one is, budget corrections, what's still unproven |
| [v4.md](v4.md) | v4 · 7 Nov product design: what the product is, spec, channel map, every change from v3 with how sure each one is, fit across 500 to 580 mm heads and 300 to 390 mm nasion–inion, the v4.4 review fixes (size range, printed band, halo lining, foam tip), the v4.5 main board (Low-Cost-EEG analog half + XIAO ESP32-S3, fit check, options compared), the buildable frame (buy or print), cleaning model, page controls, what's still open |
| [v5.md](v5.md) | v5 · 7 Nov arch concept: why the forehead box goes, what changed from v4, the mechanics check (pod force, rear hook, pivot bar, sliders), wiring, the frame test, what is still open |
| [v6.md](v6.md) | v6 · 8 Nov head ring + v4 midline (lead design): spec, why it changed from v4 and v5, checks done and what is not yet measured; v6.2 (10 Nov) review fixes |
| [buy-plan/](buy-plan/Neuryo-v6-buy-plan.pdf) | v6 prototype buy plan (9 Nov 2026, v6.2 wording 10 Nov, current): rev B board at JLCPCB (Standard PCBA, both sides), FRI pods, electrodes, frame and bench parts, prices re-read on the seller pages; one of everything for one headset, about ₹57,500 through VIT (₹53,400 if the lab has filament and tools); `data_v6.py` + `make_pdf_v6.py` rebuild it |
| [buy-plan/ (v5)](buy-plan/Neuryo-v5-buy-plan.pdf) | v5.1b prototype buy plan (7 Nov 2026): every item with price and seller link, grouped by shop, imports and gates, about ₹46,900 through VIT; `data.py` + `make_pdf.py` rebuild it |
| [ideas-v4-review.md](ideas-v4-review.md) | Ideas only (not decisions) from the 7 Nov review of v4.1, some since covered by v4.2–v4.4: hair pods, threaded carriages, spine depth, weight estimate, frame-test additions |
| [head.md](head.md) | The shared mannequin head: how it was made, how to use it, all 77 measured 10-10 positions and the mastoid points M1/M2 |

## Keeping these up to date
- Every new design gets its own `vN.md`: a spec table, a "What changed from vN-1, and why" table with decision and evidence IDs from Neuryo-Research, and the open items.
- Mark a design's status (current plan or retired, and by which decision) in its doc and in `designs/designs.json`.
- If the shared head is rebuilt, regenerate `head.md` from `designs/shared/head/head.json`.
