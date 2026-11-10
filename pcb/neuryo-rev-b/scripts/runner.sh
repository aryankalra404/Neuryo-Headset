#!/bin/bash
# Neuryo KiCad runner v5. Runs KiCad's own tools (ERC, DRC with schematic parity, netlist, renders, fab outputs)
# when Claude puts a job file in pcb-work/jobs. Only touches files inside pcb-work. Ctrl+C to stop.
# Job file: line 1 = project path inside pcb-work without extension; line 2 = options: img refill fab fw order
# order (v5): JLCPCB order set in out/<job>/order: Gerbers for copper, paste, silkscreen, mask and Edge.Cuts only, and
# Excellon drill with plated and non-plated holes in separate files
# fw: line 1 is a PlatformIO project folder inside pcb-work; builds it with PlatformIO (installed once, by
# PlatformIO's own installer, into ~/.platformio). Nothing is uploaded to a board.
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
W="$HOME/Desktop/Neuryo-Research/pcb-work"
mkdir -p "$W/jobs" "$W/out"
"$CLI" version || { echo "kicad-cli not found at $CLI"; exit 1; }
echo "Runner v5 on, watching $W/jobs. Leave this window open. Ctrl+C to stop."
while true; do
  for j in "$W"/jobs/*.job; do
    [ -e "$j" ] || continue
    name=$(basename "$j" .job); rel=$(head -1 "$j" | tr -d '\r'); opt=$(sed -n 2p "$j"); rm -f "$j"
    case "$rel" in *..*|/*|"") echo "skipped $name (bad path)"; continue;; esac
    P="$W/$rel"; O="$W/out/$name"; mkdir -p "$O"
    {
      [ -f "$P.kicad_sch" ] && "$CLI" sch erc --format json --severity-all --units mm -o "$O/erc.json" "$P.kicad_sch"
      [ -f "$P.kicad_sch" ] && "$CLI" sch export netlist --format kicadsexpr -o "$O/netlist.net" "$P.kicad_sch"
      if [ -f "$P.kicad_pcb" ]; then
        case "$opt" in *refill*) R="--refill-zones --save-board";; *) R="";; esac
        "$CLI" pcb drc --format json --severity-all --units mm --schematic-parity $R -o "$O/drc.json" "$P.kicad_pcb"
      fi
      case "$opt" in *img*)
        [ -f "$P.kicad_sch" ] && "$CLI" sch export pdf -o "$O/schematic.pdf" "$P.kicad_sch"
        [ -f "$P.kicad_pcb" ] && "$CLI" pcb render --side top -w 2400 -h 1600 -o "$O/top.png" "$P.kicad_pcb"
        [ -f "$P.kicad_pcb" ] && "$CLI" pcb render --side bottom -w 2400 -h 1600 -o "$O/bottom.png" "$P.kicad_pcb"
        [ -f "$P.kicad_pcb" ] && "$CLI" pcb export pdf --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Silkscreen,B.Silkscreen,Edge.Cuts --mode-multipage -o "$O/layers.pdf" "$P.kicad_pcb"
      ;; esac
      case "$opt" in *fw*)
        PIO="$HOME/.platformio/penv/bin/pio"
        if [ ! -x "$PIO" ]; then
          curl -fsSL -o "$W/get-platformio.py" https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py && python3 "$W/get-platformio.py"
        fi
        "$PIO" run -d "$P"; echo "pio exit $?"
      ;; esac
      case "$opt" in *fab*)
        mkdir -p "$O/fab"
        "$CLI" pcb export gerbers -o "$O/fab/" "$P.kicad_pcb"
        "$CLI" pcb export drill -o "$O/fab/" "$P.kicad_pcb"
        "$CLI" pcb export pos --format csv --units mm --side both -o "$O/fab/positions.csv" "$P.kicad_pcb"
        [ -f "$P.kicad_sch" ] && "$CLI" sch export bom -o "$O/fab/bom.csv" "$P.kicad_sch"
      ;; esac
      case "$opt" in *order*)
        mkdir -p "$O/order"
        "$CLI" pcb export gerbers --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts -o "$O/order/" "$P.kicad_pcb"
        "$CLI" pcb export drill --excellon-separate-th -o "$O/order/" "$P.kicad_pcb"
        "$CLI" pcb export pos --format csv --units mm --side both -o "$O/order/positions-kicad.csv" "$P.kicad_pcb"
      ;; esac
    } > "$O/log.txt" 2>&1
    date > "$O/DONE"; echo "$(date +%T) $name done"
  done
  sleep 2
done
