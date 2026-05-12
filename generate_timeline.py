#!/usr/bin/env python3
"""Generate a timeline PNG for the 'The Models' slide with no label overlaps.

Strategy: use angled leader lines so labels can be placed at arbitrary (x, y)
positions. Crowded right side: Gemma 4 label pulled left, Qwen3.6 placed below
the axis, and same-date models share a single date annotation.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

FIGSIZE = (13.5, 4.0)
LABEL_FONT = 11
DATE_FONT = 7.5

timeline_start = datetime(2025, 8, 1)
timeline_end = datetime(2026, 6, 1)

d = mdates.date2num  # shorthand


models = [
    {
        "name": "InternVL3.5", "sub": "241B-A28B",
        "date": datetime(2025, 8, 26), "color": "#4466CC",
        "label_x": datetime(2025, 8, 26), "label_y": 1.8,
    },
    {
        "name": "GLM-4.6V", "sub": "106B",
        "date": datetime(2025, 12, 9), "color": "#2E8B2E",
        "label_x": datetime(2025, 12, 9), "label_y": 1.8,
    },
    {
        "name": "Gemma 4", "sub": "31B",
        "date": datetime(2026, 4, 2), "color": "#CC3333",
        "label_x": datetime(2026, 2, 10), "label_y": 1.8,
        "date_y": -0.28,
    },
    {
        "name": "Qwen3.6", "sub": "27B / 35B-A3B",
        "date": datetime(2026, 4, 16), "color": "#CC8800",
        "label_x": datetime(2026, 3, 5), "label_y": -1.1,
        "date_y": -0.55,
    },
    {
        "name": "GPT-5.5", "sub": "",
        "date": datetime(2026, 4, 23), "color": "#9944CC",
        "label_x": datetime(2026, 5, 5), "label_y": 1.8,
        "date_y": -0.28,
    },
]


def make_label(m):
    if m["sub"]:
        return f"{m['name']}\n{m['sub']}"
    return m["name"]


# ── Draw ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=FIGSIZE)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Timeline arrow
ax.annotate(
    "",
    xy=(d(timeline_end), 0),
    xytext=(d(timeline_start), 0),
    arrowprops=dict(arrowstyle="->, head_width=0.3, head_length=0.15",
                    color="#888888", lw=2),
)

# Month ticks — skip Apr since it will collide with date labels
months_ticks = [
    datetime(2025, 9, 1), datetime(2025, 10, 1), datetime(2025, 11, 1),
    datetime(2025, 12, 1), datetime(2026, 1, 1), datetime(2026, 2, 1),
    datetime(2026, 3, 1), datetime(2026, 5, 1),
]
for m_dt in months_ticks:
    x = d(m_dt)
    ax.plot([x, x], [-0.06, 0.06], color="#BBBBBB", lw=1, zorder=2)
    ax.text(x, -0.17, m_dt.strftime("%b"), ha="center", va="top",
            fontsize=7, color="#AAAAAA")

# Apr tick mark only (no label — date labels will cover it)
apr1 = d(datetime(2026, 4, 1))
ax.plot([apr1, apr1], [-0.06, 0.06], color="#BBBBBB", lw=1, zorder=2)

# Year divider
jan1 = d(datetime(2026, 1, 1))
ax.plot([jan1, jan1], [-1.8, 3.0], color="#BBBBBB", lw=1.5, ls="--", zorder=0)
ax.text(d(datetime(2025, 10, 15)), -1.85, "2025",
        ha="center", va="top", fontsize=11, color="#AAAAAA")
ax.text(d(datetime(2026, 3, 5)), -1.85, "2026",
        ha="center", va="top", fontsize=11, color="#AAAAAA")

# ── Draw each model ──────────────────────────────────────────────────────
# Track which dates we've already drawn a label for
dates_labeled = set()

for m in models:
    dot_x = d(m["date"])
    lbl_x = d(m["label_x"])
    lbl_y = m["label_y"]
    color = m["color"]
    above = lbl_y > 0

    # Dot on axis
    ax.plot(dot_x, 0, "o", color=color, markersize=10, zorder=5)

    # Leader line with knee
    if above:
        knee_y = lbl_y * 0.5
        va = "bottom"
        lbl_anchor_y = lbl_y - 0.05
    else:
        knee_y = lbl_y * 0.35
        va = "top"
        lbl_anchor_y = lbl_y + 0.05

    ax.plot([dot_x, dot_x], [0, knee_y], color=color, lw=2, zorder=4)
    ax.plot([dot_x, lbl_x], [knee_y, lbl_anchor_y], color=color, lw=2, zorder=4)

    # Label text
    ax.text(lbl_x, lbl_y, make_label(m), ha="center", va=va,
            fontsize=LABEL_FONT, fontweight="bold", color=color, linespacing=1.15,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="none", alpha=0.92),
            zorder=6)

    # Date label near the dot — only once per unique date
    date_key = m["date"].strftime("%Y-%m-%d")
    if date_key not in dates_labeled:
        dates_labeled.add(date_key)
        date_str = m["date"].strftime("%b %-d")
        # Use a neutral dark color for shared dates
        n_same = sum(1 for mm in models if mm["date"] == m["date"])
        if n_same > 1:
            date_color = "#555555"
        else:
            date_color = color
        date_y = m.get("date_y", -0.28)
        ax.text(dot_x, date_y, date_str, ha="center", va="top",
                fontsize=DATE_FONT, color=date_color, fontweight="medium")


# ── Axis cleanup ─────────────────────────────────────────────────────────
ax.set_xlim(d(timeline_start), d(timeline_end))
ax.set_ylim(-2.2, 3.2)
ax.axis("off")

plt.tight_layout(pad=0.3)
plt.savefig("/Users/plato/code/strange-evals-slides/timeline.png", dpi=200,
            bbox_inches="tight", facecolor="white")
plt.close()
print("Saved timeline.png")
