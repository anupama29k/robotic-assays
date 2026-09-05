"""
pipeline_visualizer.py — GitLab-style pipeline visualisation for BioInterface.

Renders a vertical or horizontal stack of step cards with status colour bars,
instrument emoji, durations, and live timing. Backed by the pipeline_runs
table in Supabase (created out-of-band via the SQL migration in the
Pipeline Runner feature spec).
"""

from datetime import datetime
from typing import Literal


StatusType = Literal[
    "pending", "running", "completed", "failed",
    "cancelled", "warning", "skipped",
]


def get_status_color(status: str) -> str:
    return {
        "pending": "#d4cfc4",
        "running": "#2d6a9f",
        "completed": "#1a6b4a",
        "failed": "#c84b1f",
        "cancelled": "#888888",
        "warning": "#b85c00",
        "skipped": "#9e9e9e",
    }.get(status, "#d4cfc4")


def get_status_emoji(status: str) -> str:
    return {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "⛔",
        "warning": "⚠️",
        "skipped": "⏭️",
    }.get(status, "⏳")


def get_instrument_emoji(instrument: str) -> str:
    return {
        "liquid_handler": "🤖",
        "thermocycler": "🌡️",
        "magnetic_separator": "🧲",
        "centrifuge": "🌀",
        "incubator": "♨️",
        "plate_reader": "📊",
        "fragment_analyzer": "📈",
        "fluorometer": "💡",
        "vacuum_manifold": "🌊",
        "shaker": "〰️",
        "plate_sealer": "📦",
        "analyst": "👤",
        "robotic_arm": "🦾",
        "rail_robot": "🚊",
        "scheduler": "⚙️",
    }.get(instrument, "📦")


def _format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m}m"


def render_pipeline_html(
    pipeline_steps: list,
    step_statuses: dict = None,
    orientation: str = "vertical",
) -> str:
    """Render a GitLab-style pipeline visualisation as HTML."""
    if step_statuses is None:
        step_statuses = {}

    html = ['<div style="font-family: Outfit, sans-serif;">']

    if orientation == "vertical":
        html.append(
            '<div style="display: flex; flex-direction: column; '
            'gap: 4px; padding: 8px;">'
        )
    else:
        html.append(
            '<div style="display: flex; flex-direction: row; '
            'gap: 4px; padding: 8px; overflow-x: auto;">'
        )

    for i, step in enumerate(pipeline_steps):
        step_num = step.get("step_number", i + 1)
        status_info = step_statuses.get(str(step_num), {"status": "pending"})
        status = status_info.get("status", "pending")

        color = get_status_color(status)
        status_emoji = get_status_emoji(status)
        inst_emoji = get_instrument_emoji(step.get("instrument", ""))

        duration_str = _format_duration(step.get("duration_seconds", 0))

        actual_timing = ""
        if status_info.get("started_at"):
            try:
                if status_info.get("completed_at"):
                    started = datetime.fromisoformat(status_info["started_at"])
                    completed = datetime.fromisoformat(status_info["completed_at"])
                    actual_s = max(0, int((completed - started).total_seconds()))
                    actual_timing = f" · ran in {actual_s}s"
                else:
                    actual_timing = " · running..."
            except Exception:
                pass

        if orientation == "vertical":
            card_style = (
                f"background: white; border: 1px solid #d4cfc4; "
                f"border-left: 4px solid {color}; border-radius: 6px; "
                f"padding: 10px 14px; display: flex; align-items: center; gap: 12px;"
            )
        else:
            card_style = (
                f"background: white; border: 1px solid #d4cfc4; "
                f"border-top: 4px solid {color}; border-radius: 6px; "
                f"padding: 10px 14px; min-width: 180px; flex-shrink: 0;"
            )

        html.append(f'<div style="{card_style}">')
        html.append(f'<div style="font-size: 22px;">{status_emoji}</div>')
        html.append('<div style="flex: 1;">')
        html.append(
            f'<div style="font-size: 12px; color: #6b6560; font-weight: 500; '
            f'letter-spacing: 0.04em; text-transform: uppercase;">'
            f'Step {step_num} · {inst_emoji} {step.get("instrument", "—")}</div>'
        )
        html.append(
            f'<div style="font-size: 13px; color: #1a3a5c; font-weight: 500; '
            f'margin: 4px 0;">{step.get("description", "")[:100]}</div>'
        )
        html.append(
            f'<div style="font-size: 11px; color: #6b6560;">'
            f'⏱ {duration_str}{actual_timing}</div>'
        )
        html.append("</div>")
        html.append(
            f'<div style="font-size: 10px; background: {color}; color: white; '
            f'padding: 3px 8px; border-radius: 12px; font-weight: 600; '
            f'text-transform: uppercase; letter-spacing: 0.05em;">{status}</div>'
        )
        html.append("</div>")

        # Connector for vertical
        if orientation == "vertical" and i < len(pipeline_steps) - 1:
            line_color = color if status == "completed" else "#d4cfc4"
            html.append(
                f'<div style="margin-left: 24px; '
                f'border-left: 2px solid {line_color}; height: 12px;"></div>'
            )

    html.append("</div>")
    html.append("</div>")
    return "\n".join(html)


def compute_run_summary(pipeline_steps: list, step_statuses: dict) -> dict:
    total = len(pipeline_steps)
    completed = sum(1 for s in step_statuses.values() if s.get("status") == "completed")
    failed = sum(1 for s in step_statuses.values() if s.get("status") == "failed")
    running = sum(1 for s in step_statuses.values() if s.get("status") == "running")
    pending = total - completed - failed - running
    progress_pct = round(100 * completed / total) if total > 0 else 0
    return {
        "total_steps": total,
        "completed": completed,
        "failed": failed,
        "running": running,
        "pending": pending,
        "progress_pct": progress_pct,
    }
