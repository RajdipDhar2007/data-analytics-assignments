"""Core logic for the ingestion page (Assignment 2): read CSV, load to SQLite,
profile the data and build a ReportLab summary report. No Streamlit imports,
so it can be tested independently."""
from __future__ import annotations

import io
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

MAX_REPORT_COLUMNS = 60


# ---------------------------------------------------------------------- reading
def sanitize_table_name(name: str) -> str:
    """'COVID data (v2).csv' -> 'covid_data_v2' (safe SQLite table name)."""
    stem = re.sub(r"\.csv$", "", name.strip(), flags=re.I)
    stem = re.sub(r"\W+", "_", stem).strip("_").lower()
    if not stem:
        stem = "uploaded_data"
    if stem[0].isdigit():
        stem = "t_" + stem
    return stem


def read_csv_bytes(data: bytes) -> pd.DataFrame:
    """Parse uploaded bytes as CSV; raises ValueError with a friendly message."""
    if not data.strip():
        raise ValueError("The file is empty.")
    last_err = None
    for enc in ("utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(io.BytesIO(data), encoding=enc, sep=None, engine="python")
            break
        except (UnicodeDecodeError, pd.errors.ParserError) as e:  # try next encoding
            last_err = e
    else:
        raise ValueError(f"Could not read this file as CSV: {last_err}")
    if df.empty or df.shape[1] == 0:
        raise ValueError("The CSV has no data rows.")
    # tidy headers: strip spaces, fill blanks, make unique
    seen: dict[str, int] = {}
    cols = []
    for i, c in enumerate(df.columns):
        c = str(c).strip() or f"column_{i + 1}"
        seen[c] = seen.get(c, 0) + 1
        cols.append(c if seen[c] == 1 else f"{c}_{seen[c]}")
    df.columns = cols
    return df


# --------------------------------------------------------------------- database
def _connect(db_path: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.execute(
        """CREATE TABLE IF NOT EXISTS ingestion_log (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               uploaded_at TEXT NOT NULL,
               source_file TEXT NOT NULL,
               table_name TEXT NOT NULL,
               rows_loaded INTEGER NOT NULL,
               columns_loaded INTEGER NOT NULL,
               mode TEXT NOT NULL)"""
    )
    return con


def write_to_db(df: pd.DataFrame, db_path: str | Path, table: str,
                source_file: str, if_exists: str = "fail") -> dict:
    """Load df into SQLite. if_exists: 'fail' | 'replace' | 'append'."""
    if if_exists not in ("fail", "replace", "append"):
        raise ValueError("if_exists must be fail, replace or append")
    if table == "ingestion_log":
        raise ValueError("'ingestion_log' is reserved - choose another table name.")
    con = _connect(db_path)
    try:
        df.to_sql(table, con, if_exists=if_exists, index=False, chunksize=1000)
        total = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con.execute(
            "INSERT INTO ingestion_log (uploaded_at, source_file, table_name, rows_loaded,"
            " columns_loaded, mode) VALUES (?,?,?,?,?,?)",
            (now, source_file, table, len(df), df.shape[1], if_exists),
        )
        con.commit()
    finally:
        con.close()
    return {"table": table, "rows_loaded": len(df), "rows_in_table": total,
            "uploaded_at": now, "mode": if_exists, "db_path": str(db_path)}


def list_tables(db_path: str | Path) -> pd.DataFrame:
    """Tables in the database with row counts."""
    if not Path(db_path).exists():
        return pd.DataFrame(columns=["table", "rows"])
    con = _connect(db_path)
    try:
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return pd.DataFrame([(n, con.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0]) for n in names],
                            columns=["table", "rows"])
    finally:
        con.close()


def read_table(db_path: str | Path, table: str, limit: int = 100) -> pd.DataFrame:
    con = _connect(db_path)
    try:
        return pd.read_sql_query(f'SELECT * FROM "{table}" LIMIT {int(limit)}', con)
    finally:
        con.close()


# ---------------------------------------------------------------------- profile
def profile_dataframe(df: pd.DataFrame) -> dict:
    n = len(df)
    cols = pd.DataFrame({
        "Column": df.columns,
        "Type": [str(t) for t in df.dtypes],
        "Non-null": df.notna().sum().values,
        "Missing": df.isna().sum().values,
        "Missing %": (df.isna().sum().values / n * 100).round(1),
        "Unique": df.nunique(dropna=True).values,
    })
    numeric = df.select_dtypes("number")
    desc = (numeric.describe().T[["mean", "std", "min", "max"]].reset_index()
            .rename(columns={"index": "Column"}) if not numeric.empty else pd.DataFrame())
    text_cols = [c for c in df.columns if df[c].dtype == object or str(df[c].dtype) == "str"][:5]
    top_values = {c: df[c].value_counts().head(3) for c in text_cols}
    return {
        "rows": n, "columns": df.shape[1],
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_kb": round(df.memory_usage(deep=True).sum() / 1024, 1),
        "column_table": cols, "numeric_summary": desc, "top_values": top_values,
        "sample": df.head(5),
    }


# -------------------------------------------------------------------------- PDF
def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def _table(df: pd.DataFrame, cell: ParagraphStyle, col_widths=None) -> Table:
    head = ParagraphStyle("th", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")
    rows = [[Paragraph(escape(str(c)), head) for c in df.columns]]
    for rec in df.itertuples(index=False):
        rows.append([Paragraph(escape(_fmt(v)), cell) for v in rec])
    t = Table(rows, repeatRows=1, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f6fa")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def build_summary_pdf(prof: dict, meta: dict) -> bytes:
    """Ingestion summary report. meta: filename, table, db_path, uploaded_at, mode, rows_in_table."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Data Ingestion Summary Report")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], spaceBefore=12, spaceAfter=5)
    small = ParagraphStyle("small", parent=ss["Normal"], fontSize=8.5, textColor=colors.grey)
    cell = ParagraphStyle("cell", parent=ss["Normal"], fontSize=8, leading=10)
    body = ss["Normal"]

    story = [Paragraph("Data Ingestion Summary Report", h1),
             Paragraph(f"Report generated {datetime.now():%d %b %Y, %H:%M}", small), Spacer(1, 8)]

    info = [
        ["Source file", meta["filename"]],
        ["Database / table", f'{meta["db_path"]}  /  {meta["table"]}'],
        ["Uploaded at", meta["uploaded_at"]],
        ["Load mode", meta["mode"]],
        ["Rows loaded this upload", f'{prof["rows"]:,}'],
        ["Rows now in table", f'{meta["rows_in_table"]:,}'],
        ["Columns", f'{prof["columns"]:,}'],
        ["Missing cells", f'{prof["missing_cells"]:,}'],
        ["Duplicate rows", f'{prof["duplicate_rows"]:,}'],
        ["In-memory size", f'{prof["memory_kb"]:,} KB'],
    ]
    info = [[Paragraph(f"<b>{escape(a)}</b>", cell), Paragraph(escape(b), cell)] for a, b in info]
    t = Table(info, colWidths=[5 * cm, 12.4 * cm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                           ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f6fa"))]))
    story += [Paragraph("1. Upload overview", h2), t]

    ct = prof["column_table"]
    story.append(Paragraph("2. Column profile", h2))
    if len(ct) > MAX_REPORT_COLUMNS:
        story.append(Paragraph(f"Showing the first {MAX_REPORT_COLUMNS} of {len(ct)} columns.", small))
    story.append(_table(ct.head(MAX_REPORT_COLUMNS), cell,
                        [5.4 * cm, 2.4 * cm, 2.2 * cm, 2 * cm, 2.2 * cm, 2.2 * cm]))

    if not prof["numeric_summary"].empty:
        ns = prof["numeric_summary"].head(MAX_REPORT_COLUMNS)
        story += [Paragraph("3. Numeric columns", h2),
                  _table(ns, cell, [5.4 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm])]

    if prof["top_values"]:
        story.append(Paragraph("4. Most common values in text columns", h2))
        for col, vc in prof["top_values"].items():
            txt = ", ".join(f"{escape(str(k))} ({v:,})" for k, v in vc.items())
            story.append(Paragraph(f"<b>{escape(col)}:</b> {txt}", body))

    sample = prof["sample"].iloc[:, :8]
    story += [Paragraph("5. Sample rows", h2), _table(sample, cell)]
    if prof["columns"] > 8:
        story.append(Paragraph(f"First 8 of {prof['columns']} columns shown.", small))
    doc.build(story)
    return buf.getvalue()
