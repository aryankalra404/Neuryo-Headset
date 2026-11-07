# Neuryo EEG board, rev A

Open `kicad/neuryo.kicad_pro` in KiCad 8 or newer.

| Folder | What is in it |
|---|---|
| kicad/ | KiCad project: schematic, routed 4-layer PCB, symbol library |
| fab/ | JLCPCB files: gerbers zip, BOM, CPL (placement), hand-solder BOM, schematic and layer PDFs, STEP model |
| docs/ | DESIGN.md (spec, pin maps, every decision), REVIEW-CHECKLIST.md |
| gen/ | Python scripts that generated everything from gen/design.py |

## Status (30 Oct 2026)
- Schematic: KiCad ERC 0 errors, 0 warnings. ADS1299 pins checked against the TI datasheet table.
- PCB: fully routed. KiCad DRC 0 violations, 0 unconnected pads, schematic parity 0 issues.
- Parts: all 32 BOM lines in stock at JLCPCB (30 Oct). 14 are extended parts (about $3 loading fee each).
- Not yet done: professor review, caliper check of the devkit header spacing, battery polarity check (REVIEW-CHECKLIST.md).

## How it was generated
1. `gen/design.py` holds every part, pin and net. `gen_sch.py` writes the schematic, `gen_pcb.py` the placed board, `write_project.py` the rules.
2. `route.py` exports to Freerouting (GND excluded; it uses the plane), `finalize.py` adds ground vias, stitching and fills.
3. `patch_final.py` adds the last three connections the router could not reach, `patch_silk.py` tidies the silkscreen, `final_names.py` matches net names to the schematic.
4. `export_fab.py` writes the fab/ folder.
If you edit the board by hand in KiCad, do not re-run the generators: they would overwrite your edits.
