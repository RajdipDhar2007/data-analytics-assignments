# Assignment 2: Ingestion Page

Part of [Data Analytics & Communication Assignments](../README.md).

## The assignment

> Create an ingestion page which:
>
> - Handles file uploading
> - Uploads a CSV file to a database
> - Generates a summary report using ReportLab
>
> **Tools:** Streamlit and ReportLab.

## What I built

A Streamlit page that takes a CSV from upload to database to PDF report in four steps:

1. **Upload** a CSV with the file uploader. The file is checked, and clear errors are shown for empty files, bad encodings and unreadable CSVs. UTF-8 and Latin-1 are both handled, and the delimiter is detected automatically.
2. **Preview** the first 20 rows.
3. **Upload to database** (SQLite). Pick the table name (cleaned automatically into a safe name) and what happens if the table already exists: `fail`, `replace` or `append`. Every load is also recorded in an `ingestion_log` table.
4. **Download the summary report**, a PDF made with ReportLab.

The page also lists every table in the database, with row counts and a preview.

<img src="../docs/images/ingestion_report.png" width="360" alt="First page of the generated summary report">

### What the PDF report contains

1. Upload overview: source file, table, time, load mode, rows, columns, missing cells, duplicate rows
2. Column profile: type, non-null count, missing count and percentage, unique values
3. Numeric columns: mean, standard deviation, min, max
4. Most common values in the text columns
5. Sample rows

A complete example is in [`../sample_outputs/ingestion_summary_country_wise_latest.pdf`](../sample_outputs/ingestion_summary_country_wise_latest.pdf).

## Run it

```bash
# from the repository root
pip install -r requirements.txt
streamlit run Assignment_2_Ingestion_Page/app.py
```

Then upload `sample_data/country_wise_latest.csv`, or any CSV of your own. The database file `ingestion.db` is created next to `app.py` the first time you upload (it is git-ignored). You can point to a different database file in the sidebar.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit page: upload, preview, load, download |
| `ingest_core.py` | CSV reading and validation, SQLite loading, data profiling and the ReportLab report (no Streamlit code, so it is easy to test) |
| `sample_data/country_wise_latest.csv` | A CSV to try the page with |

## Tests

```bash
python -m unittest discover -s tests -v
```
