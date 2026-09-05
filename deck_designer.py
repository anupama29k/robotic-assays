"""
deck_designer.py — Workcell deck configuration module for BioInterface.

Resource types, deck templates, default-position generation, and SVG rendering.
Backed by the deck_configurations table in Supabase (created out-of-band via
the SQL migration in the Deck Designer feature spec).
"""

from typing import Literal


ResourceType = Literal[
    "tip_rack_1000ul", "tip_rack_200ul", "tip_rack_50ul",
    "reagent_reservoir_25ml", "reagent_reservoir_100ml",
    "source_plate_96", "source_plate_384",
    "destination_plate_96", "destination_plate_384",
    "magnetic_separator", "heater_shaker",
    "cold_block", "thermocycler_seat",
    "trash", "empty",
]


DECK_TEMPLATES = {
    "hamilton_star_16pos": {
        "name": "Hamilton STAR (16 positions)",
        "total_positions": 16,
        "default_layout": [
            ("P1", "tip_rack_1000ul", "1000uL Tips"),
            ("P2", "tip_rack_200ul", "200uL Tips"),
            ("P3", "reagent_reservoir_25ml", "Buffer A"),
            ("P4", "source_plate_96", "Source Plate"),
            ("P5", "destination_plate_96", "Destination Plate"),
            ("P6", "magnetic_separator", "Magnetic Separator"),
            ("P7", "heater_shaker", "Heater/Shaker"),
            ("P8", "trash", "Tip Waste"),
        ],
    },
    "tecan_fluent_8pos": {
        "name": "Tecan Fluent (8 positions)",
        "total_positions": 8,
        "default_layout": [
            ("P1", "tip_rack_1000ul", "1000uL Tips"),
            ("P2", "tip_rack_200ul", "200uL Tips"),
            ("P3", "reagent_reservoir_25ml", "Buffer"),
            ("P4", "source_plate_96", "Source"),
            ("P5", "destination_plate_96", "Destination"),
        ],
    },
    "opentrons_ot2_12pos": {
        "name": "Opentrons OT-2 (12 positions)",
        "total_positions": 12,
        "default_layout": [
            ("P1", "tip_rack_200ul", "200uL Tips"),
            ("P2", "tip_rack_50ul", "50uL Tips"),
            ("P3", "reagent_reservoir_25ml", "Reagents"),
            ("P4", "source_plate_96", "Source"),
            ("P5", "destination_plate_96", "Destination"),
            ("P11", "trash", "Tip Waste"),
        ],
    },
    "custom": {
        "name": "Custom Deck",
        "total_positions": 12,
        "default_layout": [],
    },
}


def make_default_positions(deck_type: str) -> list:
    """Generate a default position list for a deck template."""
    template = DECK_TEMPLATES.get(deck_type, DECK_TEMPLATES["custom"])
    n = template["total_positions"]
    layout_dict = {pos_id: (rt, label) for pos_id, rt, label in template["default_layout"]}

    positions = []
    for i in range(1, n + 1):
        pos_id = f"P{i}"
        if pos_id in layout_dict:
            rt, label = layout_dict[pos_id]
            positions.append({
                "position_id": pos_id,
                "position_label": f"Position {i}",
                "resource_type": rt,
                "resource_label": label,
                "notes": "",
            })
        else:
            positions.append({
                "position_id": pos_id,
                "position_label": f"Position {i}",
                "resource_type": "empty",
                "resource_label": "",
                "notes": "",
            })
    return positions


def get_resource_emoji(resource_type: str) -> str:
    return {
        "tip_rack_1000ul": "🔵",
        "tip_rack_200ul": "🟢",
        "tip_rack_50ul": "🟡",
        "reagent_reservoir_25ml": "🧪",
        "reagent_reservoir_100ml": "🧪",
        "source_plate_96": "📋",
        "source_plate_384": "📋",
        "destination_plate_96": "📊",
        "destination_plate_384": "📊",
        "magnetic_separator": "🧲",
        "heater_shaker": "🔥",
        "cold_block": "❄️",
        "thermocycler_seat": "🌡️",
        "trash": "🗑️",
        "empty": "⬜",
    }.get(resource_type, "❓")


def render_deck_svg(positions: list, deck_type: str = "hamilton_star_16pos") -> str:
    """Render an SVG visualization of the deck."""
    n = len(positions)
    if n == 0:
        return "<svg width='600' height='100'></svg>"

    cols = min(4, n)
    rows = (n + cols - 1) // cols
    cell_w = 140
    cell_h = 90
    padding = 20
    width = cols * cell_w + 2 * padding
    height = rows * cell_h + 2 * padding + 40

    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#fafaf7; border:1px solid #d4cfc4; border-radius:8px;">',
        f'<text x="{width/2}" y="22" text-anchor="middle" '
        f'font-family="DM Serif Display, serif" font-size="16" fill="#1a3a5c">Deck Layout</text>',
    ]

    for i, pos in enumerate(positions):
        row = i // cols
        col = i % cols
        x = padding + col * cell_w
        y = padding + 30 + row * cell_h

        bg_color = {
            "empty": "#f0e8d8",
            "tip_rack_1000ul": "#d4e8f0",
            "tip_rack_200ul": "#d4f0d8",
            "tip_rack_50ul": "#f0e8b0",
            "source_plate_96": "#e0d4f0",
            "destination_plate_96": "#f0d4d4",
            "magnetic_separator": "#d4d4d4",
            "trash": "#888888",
        }.get(pos["resource_type"], "#e8e8e8")

        svg.append(
            f'<rect x="{x+5}" y="{y+5}" width="{cell_w-10}" height="{cell_h-10}" '
            f'rx="6" fill="{bg_color}" stroke="#1a3a5c" stroke-width="1.5"/>'
        )
        svg.append(
            f'<text x="{x + cell_w/2}" y="{y + 25}" text-anchor="middle" '
            f'font-family="DM Mono, monospace" font-size="13" font-weight="600" '
            f'fill="#1a3a5c">{pos["position_id"]}</text>'
        )
        rt_short = pos["resource_type"].replace("_", " ")[:18]
        svg.append(
            f'<text x="{x + cell_w/2}" y="{y + 45}" text-anchor="middle" '
            f'font-family="Outfit, sans-serif" font-size="10" fill="#262626">{rt_short}</text>'
        )
        label = (pos.get("resource_label", "") or "")[:22]
        svg.append(
            f'<text x="{x + cell_w/2}" y="{y + 62}" text-anchor="middle" '
            f'font-family="Outfit, sans-serif" font-size="9" fill="#6b6560" '
            f'font-style="italic">{label}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def get_position_for_resource(deck_positions: list, resource_type: str):
    for pos in deck_positions:
        if pos["resource_type"] == resource_type:
            return pos["position_id"]
    return None


def get_position_by_label(deck_positions: list, label_substring: str):
    label_lower = label_substring.lower()
    for pos in deck_positions:
        if label_lower in pos.get("resource_label", "").lower():
            return pos["position_id"]
    return None


def deck_to_pylabrobot_setup(positions: list, deck_type: str = "hamilton_star_16pos") -> str:
    """Generate PyLabRobot deck setup code from a deck configuration.
    Resource classes and slot-keyword vary by platform — Hamilton uses
    `rails=`, Opentrons uses `slot=`, Tecan uses `location=`.
    """
    import re as _re

    # ── Platform-specific resource & slot mapping ──────────────────────
    if "opentrons" in deck_type:
        platform = {
            "deck_class": "OT2Deck",
            "deck_import": "from pylabrobot.resources.opentrons import OT2Deck",
            "resource_imports": (
                "from pylabrobot.resources.opentrons import (\n"
                "    opentrons_96_tiprack_300ul,\n"
                "    opentrons_96_tiprack_20ul,\n"
                "    opentrons_96_tiprack_1000ul,\n"
                "    nest_96_wellplate_200ul_flat,\n"
                "    nest_12_reservoir_15ml,\n"
                ")"
            ),
            "tip_rack_300ul": "opentrons_96_tiprack_300ul",
            "tip_rack_50ul": "opentrons_96_tiprack_20ul",
            "tip_rack_1000ul": "opentrons_96_tiprack_1000ul",
            "plate_96": "nest_96_wellplate_200ul_flat",
            "reservoir": "nest_12_reservoir_15ml",
            "slot_kwarg": "slot",
        }
    elif "tecan" in deck_type:
        platform = {
            "deck_class": "FluentDeck",
            "deck_import": "from pylabrobot.resources.tecan import FluentDeck",
            "resource_imports": (
                "from pylabrobot.resources.tecan import (\n"
                "    DiTi_1000ul,\n"
                "    DiTi_200ul,\n"
                "    DiTi_50ul,\n"
                "    Tecan_Plate_96,\n"
                "    Tecan_Reservoir_100ml,\n"
                ")"
            ),
            "tip_rack_300ul": "DiTi_200ul",
            "tip_rack_50ul": "DiTi_50ul",
            "tip_rack_1000ul": "DiTi_1000ul",
            "plate_96": "Tecan_Plate_96",
            "reservoir": "Tecan_Reservoir_100ml",
            "slot_kwarg": "location",
        }
    else:  # hamilton (default)
        platform = {
            "deck_class": "STARLetDeck",
            "deck_import": "from pylabrobot.resources.hamilton import STARLetDeck",
            "resource_imports": (
                "from pylabrobot.resources import (\n"
                "    HTF_L, STF_L, LTF_L,  # tip racks (1000/200/50 uL)\n"
                "    Cos_96_DW_1mL, Cos_96_DW_2mL,  # plates\n"
                "    Reservoir_25mL,  # reservoirs\n"
                ")"
            ),
            "tip_rack_300ul": "STF_L",
            "tip_rack_50ul": "LTF_L",
            "tip_rack_1000ul": "HTF_L",
            "plate_96": "Cos_96_DW_1mL",
            "reservoir": "Reservoir_25mL",
            "slot_kwarg": "rails",
        }

    lines = [
        "# === Deck setup from BioInterface Deck Designer ===",
        platform["deck_import"],
        platform["resource_imports"],
        "",
        f"deck = {platform['deck_class']}()",
        "",
    ]

    for pos in positions:
        if pos["resource_type"] == "empty":
            continue

        pos_id = pos["position_id"]
        rt = pos["resource_type"]
        label = pos.get("resource_label", pos_id)

        # Sanitise label into a valid Python identifier
        raw = label.lower().replace(" ", "_").replace("/", "_")
        raw = _re.sub(r"[^a-z0-9_]", "", raw)
        raw = _re.sub(r"_+", "_", raw).strip("_")
        if not raw or raw[0].isdigit():
            raw = f"r_{raw}" if raw else pos_id.lower()
        var_name = raw

        # Resource class lookup
        resource_class = None
        if rt == "tip_rack_1000ul":
            resource_class = platform["tip_rack_1000ul"]
        elif rt == "tip_rack_200ul":
            resource_class = platform["tip_rack_300ul"]
        elif rt == "tip_rack_50ul":
            resource_class = platform["tip_rack_50ul"]
        elif "plate" in rt:
            resource_class = platform["plate_96"]
        elif "reagent_reservoir" in rt:
            resource_class = platform["reservoir"]

        lines.append(f"# {pos_id}: {label}")
        if resource_class:
            lines.append(f'{var_name} = {resource_class}(name="{label}")')
            try:
                slot_num = int(pos_id[1:])
                lines.append(
                    f"deck.assign_child_resource({var_name}, "
                    f"{platform['slot_kwarg']}={slot_num})"
                )
            except ValueError:
                lines.append(
                    f"# Could not parse numeric slot from {pos_id}"
                )
        else:
            lines.append(f"# {rt} at {pos_id} — manual setup required")
        lines.append("")

    return "\n".join(lines)
