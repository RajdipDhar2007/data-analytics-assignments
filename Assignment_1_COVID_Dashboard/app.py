"""Assignment 1 - COVID-19 Dashboard (Streamlit + ReportLab).

Run:  streamlit run app.py
"""
import streamlit as st

import covid_charts as cc

st.set_page_config(page_title="COVID-19 Dashboard", page_icon="🦠", layout="wide")


@st.cache_data
def get_data():
    return cc.load_country_latest(), cc.load_daily()


country, daily = get_data()
min_d, max_d = daily["Date"].min().date(), daily["Date"].max().date()

# ----------------------------------------------------------------------- sidebar
st.sidebar.header("Filters")
all_regions = sorted(country["WHO Region"].unique())
regions = st.sidebar.multiselect("WHO Region", all_regions, default=all_regions)
metric = st.sidebar.selectbox("Metric (bar & pie charts)", cc.METRICS)
top_n = st.sidebar.slider("Top N countries", 5, 25, 10)
series = st.sidebar.multiselect("Lines to show", cc.METRICS,
                                default=["Confirmed", "Deaths", "Recovered", "Active"])
dates = st.sidebar.date_input("Date range (line chart)", value=(min_d, max_d),
                              min_value=min_d, max_value=max_d)
log_scale = st.sidebar.checkbox("Log scale (line chart)")

# While the user is mid-selection, date_input can return a single date.
start, end = (dates[0], dates[1]) if len(dates) == 2 else (min_d, max_d)

if not regions:
    st.warning("Select at least one WHO region in the sidebar.")
    st.stop()
if not series:
    st.warning("Select at least one line for the trend chart.")
    st.stop()

view = country[country["WHO Region"].isin(regions)]

# -------------------------------------------------------------------------- page
st.title("🦠 COVID-19 Dashboard")
st.caption(f"Kaggle COVID-19 dataset - snapshot as of {max_d:%d %b %Y} "
           f"({len(view)} countries in the current selection)")

kpis = cc.kpi_totals(view)
for col, m in zip(st.columns(4), cc.METRICS):
    col.metric(m, f"{kpis[m]:,}")

bar_fig = cc.bar_top_countries(view, metric, top_n)
pie_fig = cc.pie_by_region(view, metric)
trend = cc.daily_trend(daily, regions, start, end)
line_fig = cc.line_trend(trend, series, log_scale)

left, right = st.columns(2)
with left:
    st.subheader("Bar chart")
    st.pyplot(bar_fig)
with right:
    st.subheader("Pie chart")
    st.pyplot(pie_fig)

st.subheader("Line chart")
st.pyplot(line_fig)

top_table = view.nlargest(top_n, metric)[["Country/Region"] + cc.METRICS]
with st.expander("Show data table"):
    st.dataframe(top_table, hide_index=True)

# --------------------------------------------------------------------- PDF export
st.divider()
filters_text = f"{len(regions)} of {len(all_regions)} WHO regions | metric: {metric} | top {top_n}"
pdf_bytes = cc.build_pdf(
    kpis,
    {"bar": cc.fig_to_png(bar_fig), "line": cc.fig_to_png(line_fig), "pie": cc.fig_to_png(pie_fig)},
    filters_text, top_table, f"{max_d:%d %b %Y}",
)
st.download_button("📄 Download this dashboard as PDF", pdf_bytes,
                   file_name="covid19_dashboard_report.pdf", mime="application/pdf")
