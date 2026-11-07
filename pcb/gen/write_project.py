"""Write neuryo.kicad_pro with design rules and net classes (KiCad 8 format)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import gen_pcb as GP

K = os.path.join(os.path.dirname(__file__), "..", "kicad")

pro = {
    "board": {
        "design_settings": {
            "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "silk_line_width": 0.12,
                         "silk_text_size_h": 0.8, "silk_text_size_v": 0.8, "silk_text_thickness": 0.12},
            "rules": {"min_clearance": 0.127, "min_track_width": 0.127, "min_via_diameter": 0.45,
                      "min_through_hole_diameter": 0.2, "min_copper_edge_clearance": 0.3,
                      "min_hole_to_hole": 0.25, "min_silk_clearance": 0.0, "min_text_height": 0.8,
                      "min_text_thickness": 0.08},
            "rule_severities": {"silk_overlap": "ignore", "silk_over_copper": "warning",
                                "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore"},
        },
    },
    "meta": {"filename": "neuryo.kicad_pro", "version": 1},
    "net_settings": {
        "classes": [
            {"name": "Default", "clearance": 0.13, "track_width": 0.15, "via_diameter": 0.5, "via_drill": 0.25,
             "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
             "diff_pair_via_gap": 0.25, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
             "pcb_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "priority": 2147483647},
            {"name": "Power", "clearance": 0.13, "track_width": 0.4, "via_diameter": 0.7, "via_drill": 0.35,
             "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
             "diff_pair_via_gap": 0.25, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
             "pcb_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "priority": 0},
        ],
        "meta": {"version": 3},
        "net_colors": None,
        "netclass_assignments": None,
        "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in sorted(GP.POWER_NETS)],
    },
    "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
    "sheets": [["5b0a1c2e-7d3f-4e8a-9b21-0e6f2a4c8d10", "Root"]],
    "text_variables": {},
}
with open(os.path.join(K, "neuryo.kicad_pro"), "w") as fh:
    json.dump(pro, fh, indent=2)
print("wrote project")
