"""Data loading, charts and PDF export for the COVID-19 dashboard (Assignment 1).

Everything here is plain Python (no Streamlit), so it can be tested on its own
and re-used by app.py.
"""
from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend - safe inside Streamlit and scripts
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DATA_DIR = Path(__file__).parent / "data"
METRICS = ["Confirmed", "Deaths", "Recovered", "Active"]
COLORS = {
    "Confirmed": "#1f77b4",
    "Deaths": "#d62728",
    "Recovered": "#2ca02c",
    "Active": "#ff7f0e",
}


# --------------------------------------------------------------------------- data
def load_country_latest(path: Path | None = None) -> pd.DataFrame:
    """One row per country - latest snapshot (country_wise_latest.csv)."""
    return pd.read_csv(path or DATA_DIR / "country_wise_latest.csv")


def load_daily(path: Path | None = None) -> pd.DataFrame:
    """One row per country per day (full_grouped.csv)."""
    return pd.read_csv(path or DATA_DIR / "full_grouped.csv", parse_dates=["Date"])


def kpi_totals(df: pd.DataFrame) -> dict[str, int]:
    return {m: int(df[m].sum()) for m in METRICS}


def daily_trend(daily: pd.DataFrame, regions: list[str], start, end) -> pd.DataFrame:
    """World (or selected WHO regions) totals per day, between start and end."""
    d = daily[daily["WHO Region"].isin(regions)]
    d = d[(d["Date"] >= pd.Timestamp(start)) & (d["Date"] <= pd.Timestamp(end))]
    return d.groupby("Date")[METRICS].sum().reset_index()


# ------------------------------------------------------------------------- charts
def _short(x, _pos=None) -> str:
    if x >= 1e6:
        return f"{x / 1e6:.1f}M".replace(".0M", "M")
    if x >= 1e3:
        return f"{x / 1e3:.0f}K"
    return f"{x:.0f}"


def bar_top_countries(df: pd.DataFrame, metric: str, n: int):
    top = df.nlargest(n, metric).sort_values(metric)
    fig, ax = plt.subplots(figsize=(7, 0.42 * n + 1.6))
    bars = ax.barh(top["Country/Region"], top[metric], color=COLORS[metric])
    ax.bar_label(bars, labels=[_short(v) for v in top[metric]], padding=3, fontsize=8)
    ax.set_title(f"Top {n} countries by {metric.lower()} cases" if metric == "Confirmed"
                 else f"Top {n} countries by {metric.lower()}", fontweight="bold")
    ax.xaxis.set_major_formatter(FuncFormatter(_short))
    ax.set_xlim(0, top[metric].max() * 1.12 if len(top) else 1)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def line_trend(trend: pd.DataFrame, series: list[str], log: bool = False):
    fig, ax = plt.subplots(figsize=(10, 4.2))
    for s in series:
        ax.plot(trend["Date"], trend[s], label=s, color=COLORS[s], linewidth=2)
    ax.set_title("Global COVID-19 trend over time", fontweight="bold")
    ax.yaxis.set_major_formatter(FuncFormatter(_short))
    if log:
        ax.set_yscale("log")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def pie_by_region(df: pd.DataFrame, metric: str):
    share = df.groupby("WHO Region")[metric].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    wedges, _t, autotexts = ax.pie(
        share, autopct=lambda p: f"{p:.1f}%" if p >= 4 else "",
        startangle=90, counterclock=False, pctdistance=0.78,
        wedgeprops={"width": 0.55, "edgecolor": "white"},
        colors=plt.get_cmap("tab10").colors[: len(share)],
    )
    for t in autotexts:
        t.set_fontsize(8)
        t.set_color("white")
    ax.legend(wedges, [f"{r} ({_short(v)})" for r, v in share.items()],
              loc="center left", bbox_to_anchor=(1, 0.5), frameon=False, fontsize=8)
    ax.set_title(f"Share of {metric.lower()} by WHO region", fontweight="bold")
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- PDF
def fig_to_png(fig, dpi: int = 150) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    return buf.getvalue()


def _image(png: bytes, width_cm: float) -> Image:
    w, h = ImageReader(io.BytesIO(png)).getSize()
    width = width_cm * cm
    return Image(io.BytesIO(png), width=width, height=width * h / w)


def build_pdf(kpis: dict[str, int], figs: dict[str, bytes], filters: str,
              top_table: pd.DataFrame, data_as_of: str) -> bytes:
    """Dashboard snapshot as a PDF (ReportLab)."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="COVID-19 Dashboard Report")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], spaceBefore=10, spaceAfter=4)
    small = ParagraphStyle("small", parent=ss["Normal"], fontSize=8.5, textColor=colors.grey)

    story = [
        Paragraph("COVID-19 Dashboard Report", h1),
        Paragraph(f"Data as of {data_as_of} &nbsp;|&nbsp; Generated "
                  f"{datetime.now():%d %b %Y, %H:%M} &nbsp;|&nbsp; {filters}", small),
        Spacer(1, 10),
    ]
    kpi_tbl = Table([[m for m in METRICS], [f"{kpis[m]:,}" for m in METRICS]],
                    colWidths=[4.25 * cm] * 4)
    style = [("ALIGN", (0, 0), (-1, -1), "CENTER"),
             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
             ("FONTSIZE", (0, 1), (-1, 1), 13),
             ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
             ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
             ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey)]
    for i, m in enumerate(METRICS):
        style.append(("TEXTCOLOR", (i, 0), (i, 0), colors.HexColor(COLORS[m])))
    kpi_tbl.setStyle(TableStyle(style))
    story += [kpi_tbl, Spacer(1, 6)]

    for title, key, width in [("Bar chart", "bar", 13), ("Line chart", "line", 16.5),
                              ("Pie chart", "pie", 13)]:
        story.append(KeepTogether([Paragraph(title, h2), _image(figs[key], width)]))

    rows = [list(top_table.columns)] + [
        [str(r[0])] + [f"{int(v):,}" for v in r[1:]] for r in top_table.itertuples(index=False)
    ]
    tbl = Table(rows, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f6fa")]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story += [Paragraph("Top countries (table)", h2), tbl, Spacer(1, 8),
              Paragraph("Source: Kaggle - COVID-19 Dataset (Johns Hopkins CSSE / Worldometer).", small)]
    doc.build(story)
    return buf.getvalue()
