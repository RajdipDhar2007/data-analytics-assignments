"""Assignment 2 - Ingestion page (Streamlit + SQLite + ReportLab).

Run:  streamlit run app.py
Upload a CSV -> preview -> load into a SQLite table -> download a PDF summary.
"""
from pathlib import Path

import streamlit as st

import ingest_core as ic

st.set_page_config(page_title="CSV Ingestion", page_icon="📥", layout="wide")
st.title("📥 CSV Ingestion Page")
st.caption("Upload a CSV, load it into a database, and get a PDF summary report.")

DEFAULT_DB = str(Path(__file__).parent / "ingestion.db")
db_path = st.sidebar.text_input("SQLite database file", DEFAULT_DB)

uploaded = st.file_uploader("1. Choose a CSV file", type=["csv"])

if uploaded is None:
    st.info("Waiting for a file. Try `sample_data/country_wise_latest.csv`.")
else:
    try:
        df = ic.read_csv_bytes(uploaded.getvalue())
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.success(f"Read **{uploaded.name}**: {len(df):,} rows x {df.shape[1]} columns")
    st.subheader("2. Preview")
    st.dataframe(df.head(20))

    st.subheader("3. Upload to database")
    c1, c2 = st.columns(2)
    with c1:
        table = st.text_input("Table name", ic.sanitize_table_name(uploaded.name))
    with c2:
        mode = st.radio("If the table already exists", ["fail", "replace", "append"],
                        horizontal=True,
                        help="fail = stop with an error, replace = overwrite, append = add rows")
    table = ic.sanitize_table_name(table)

    if st.button("Upload to database", type="primary"):
        try:
            result = ic.write_to_db(df, db_path, table, uploaded.name, mode)
            prof = ic.profile_dataframe(df)
            pdf = ic.build_summary_pdf(prof, {"filename": uploaded.name, **result})
            st.session_state["last"] = {"result": result, "pdf": pdf, "name": table}
        except ValueError as e:      # e.g. table exists with mode=fail
            st.error(str(e))
        except Exception as e:       # sqlite errors, e.g. schema mismatch on append
            st.error(f"Database error: {e}")

last = st.session_state.get("last")
if last:
    r = last["result"]
    st.success(f"Loaded {r['rows_loaded']:,} rows into table **{r['table']}** "
               f"({r['rows_in_table']:,} rows in the table now).")
    st.subheader("4. Summary report")
    st.download_button("📄 Download summary report (PDF)", last["pdf"],
                       file_name=f"ingestion_summary_{last['name']}.pdf", mime="application/pdf")

st.divider()
st.subheader("Database contents")
tables = ic.list_tables(db_path)
if tables.empty:
    st.write("No tables yet.")
else:
    st.dataframe(tables, hide_index=True)
    pick = st.selectbox("Preview a table", list(tables["table"]))
    st.dataframe(ic.read_table(db_path, pick))
