from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hyderabad Climate Analytics",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "processed" / "hyderabad_weather_clean.csv"
EXTREME_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "extreme_weather"
    / "weather_with_extreme_flags.csv"
)

HEAT_THRESHOLD_C = 40.0
RAIN_THRESHOLD_MM = 50.0

# ---------- Visual theme ----------
st.markdown(
    """
    <style>
    /*
       Use Streamlit's active theme variables instead of fixed light-mode
       colors. This keeps text, cards, sidebar and hero readable in both
       Light and Dark modes.
    */
    .stApp {
        background: var(--background-color, #f5f8fc);
        color: var(--text-color, #142b4a);
    }
    [data-testid="stHeader"] {
        background: var(--background-color, #f5f8fc);
    }
    [data-testid="stSidebar"] {
        background: var(--secondary-background-color, #edf4ff) !important;
        color: var(--text-color, #142b4a) !important;
        border-right: 1px solid var(--border-color, rgba(128, 145, 165, .25));
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] [data-testid="stRadio"] label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label * {
        color: var(--text-color, #142b4a) !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: var(--text-color);
    }
    h1, h2, h3 {
        letter-spacing: -0.025em;
    }
    .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 20px;
        border: 1px solid var(--border-color, rgba(128, 145, 165, .25));
        background: var(--secondary-background-color, #ffffff);
        margin-bottom: 1.1rem;
    }
    .hero-kicker {
        color: var(--primary-color, #2563eb);
        font-size: .78rem;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: .11em;
    }
    .hero h1 {
        color: var(--text-color);
        margin: .3rem 0 .45rem 0;
        font-size: clamp(1.8rem, 3vw, 2.55rem);
    }
    .hero p {
        color: var(--text-color);
        opacity: .82;
        margin: 0;
        max-width: 850px;
        font-size: 1rem;
    }
    .section-note {
        color: var(--text-color);
        opacity: .75;
        font-size: .91rem;
        margin-top: -.35rem;
    }
    div[data-testid="stMetric"] {
        background: var(--secondary-background-color, #ffffff);
        color: var(--text-color);
        border: 1px solid var(--border-color, rgba(128, 145, 165, .25));
        border-radius: 15px;
        padding: 1rem 1.05rem;
        box-shadow: 0 3px 12px rgba(29, 59, 94, .07);
    }
    /* Keep metric labels readable even when the app theme and CSS disagree. */
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricDelta"] {
        color: #52657d !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        color: #183153 !important;
    }
    /* Consistent, high-contrast buttons in both Streamlit themes. */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"] {
        background: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    .stButton > button *,
    .stDownloadButton > button *,
    [data-testid="stBaseButton-secondary"] *,
    [data-testid="stBaseButton-primary"] * {
        color: #ffffff !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {
        background: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
        color: #ffffff !important;
    }
    /* Dark-mode cards keep their labels and values light on a dark surface. */
    html[data-theme="dark"] div[data-testid="stMetricLabel"],
    html[data-theme="dark"] div[data-testid="stMetricLabel"] *,
    body[data-theme="dark"] div[data-testid="stMetricLabel"],
    body[data-theme="dark"] div[data-testid="stMetricLabel"] * {
        color: #cbd5e1 !important;
    }
    html[data-theme="dark"] div[data-testid="stMetricValue"],
    html[data-theme="dark"] div[data-testid="stMetricValue"] *,
    body[data-theme="dark"] div[data-testid="stMetricValue"],
    body[data-theme="dark"] div[data-testid="stMetricValue"] * {
        color: #f8fafc !important;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-color, rgba(128, 145, 165, .25));
        border-radius: 12px;
        overflow: hidden;
    }
    .status-pill {
        display: inline-block;
        padding: .25rem .6rem;
        border-radius: 999px;
        background: var(--secondary-background-color, #eaf7ef);
        color: var(--text-color);
        font-size: .8rem;
        font-weight: 700;
    }
    .small-muted {
        color: var(--text-color);
        opacity: .72;
        font-size: .84rem;
    }
    hr {
        border-color: var(--border-color, rgba(128, 145, 165, .25));
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Data loading and normalization ----------
@st.cache_data(show_spinner="Loading local weather data…")
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    data = pd.read_csv(DATA_FILE)
    if "DATE" not in data.columns:
        raise ValueError("The cleaned dataset does not contain a DATE column.")

    data["DATE"] = pd.to_datetime(data["DATE"], errors="coerce")

    for column in ["TEMP_C", "MAX_C", "MIN_C", "PRCP_MM"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    # Always derive flags from the same cleaned dataset used by the filters.
    # Joining a previously generated flags file can create unmatched DATE rows
    # (or overwrite valid flags with nulls), causing event filters to return no rows.
    if "MAX_C" not in data.columns:
        data["MAX_C"] = pd.NA
    if "PRCP_MM" not in data.columns:
        data["PRCP_MM"] = pd.NA

    data["extreme_heat"] = data["MAX_C"].ge(HEAT_THRESHOLD_C).fillna(False)
    data["heavy_rain"] = data["PRCP_MM"].ge(RAIN_THRESHOLD_MM).fillna(False)

    for column in ["extreme_heat", "heavy_rain"]:
        if column not in data.columns:
            data[column] = False
        data[column] = (
            data[column]
            .astype("string")
            .str.strip()
            .str.lower()
            .map({"true": True, "false": False, "1": True, "0": False})
            .fillna(False)
            .astype(bool)
        )

    # Keep event labels consistent, including dates with both event types.
    data["event_type"] = "Normal"
    data.loc[data["extreme_heat"], "event_type"] = "Extreme Heat"
    data.loc[data["heavy_rain"], "event_type"] = "Heavy Rainfall"
    both = data["extreme_heat"] & data["heavy_rain"]
    data.loc[both, "event_type"] = "Extreme Heat + Heavy Rainfall"

    return data.dropna(subset=["DATE"]).sort_values("DATE").reset_index(drop=True)


@st.cache_data(ttl=60, show_spinner="Reading Spark outputs from MinIO…")
def load_curated_parquet(prefix: str) -> pd.DataFrame:
    """Read Spark-generated Parquet objects from the local MinIO endpoint."""
    import boto3
    import pyarrow.parquet as pq
    from botocore.config import Config

    client = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="climateadmin",
        aws_secret_access_key="ClimateLab2026!",
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    paginator = client.get_paginator("list_objects_v2")
    objects = []
    for page in paginator.paginate(Bucket="climate-curated", Prefix=prefix):
        objects.extend(
            obj for obj in page.get("Contents", [])
            if obj["Key"].lower().endswith(".parquet")
            and not Path(obj["Key"]).name.startswith((".", "_"))
        )

    if not objects:
        return pd.DataFrame()

    frames = []
    for obj in objects:
        response = client.get_object(Bucket="climate-curated", Key=obj["Key"])
        payload = response["Body"].read()
        if payload:
            frames.append(pq.read_table(BytesIO(payload)).to_pandas())

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def normalize_spark_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize common uppercase/lowercase Spark output schemas for display."""
    if frame.empty:
        return frame
    result = frame.copy()
    result.columns = [str(column).strip().upper() for column in result.columns]
    aliases = {
        "DAYS_RECORDED": "RECORDS",
        "DAYS_RECORDED_COUNT": "RECORDS",
        "AVG_TEMP_C": "AVG_MAX_TEMP_C",
        "HIGHEST_MAX_TEMP_C": "HIGHEST_TEMP_C",
        "LOWEST_MIN_TEMP_C": "LOWEST_TEMP_C",
        "TOTAL_PRECIPITATION_MM": "AVG_PRECIPITATION_MM",
    }
    result = result.rename(columns={k: v for k, v in aliases.items() if k in result.columns and v not in result.columns})
    return result


def show_empty_chart(message: str) -> None:
    st.info(message)


# ---------- Load the local dataset ----------
try:
    df = load_data()
except Exception as error:
    st.error(f"Could not load the local weather dataset: {error}")
    st.stop()

if df.empty:
    st.warning("The dataset contains no usable weather records.")
    st.stop()

# ---------- Sidebar navigation and filters ----------
st.sidebar.markdown("## 🌦️ Climate Analytics")
st.sidebar.caption("Hyderabad · NOAA GSOD")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Weather Trends", "Extreme Events", "Data Explorer", "System Architecture"],
    label_visibility="collapsed",
)
st.sidebar.divider()
st.sidebar.subheader("Filters")

min_date = df["DATE"].min().date()
max_date = df["DATE"].max().date()
selected_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_range, (tuple, list)):
    if len(selected_range) == 2:
        start_date, end_date = selected_range
    elif len(selected_range) == 1:
        start_date = end_date = selected_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = selected_range

filtered = df[
    (df["DATE"].dt.date >= start_date)
    & (df["DATE"].dt.date <= end_date)
].copy()

event_filter = st.sidebar.selectbox(
    "Event type",
    ["All days", "Extreme Heat", "Heavy Rainfall", "Any extreme"],
)
if event_filter == "Extreme Heat":
    filtered = filtered[filtered["extreme_heat"]]
elif event_filter == "Heavy Rainfall":
    filtered = filtered[filtered["heavy_rain"]]
elif event_filter == "Any extreme":
    filtered = filtered[filtered["extreme_heat"] | filtered["heavy_rain"]]

# Header
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Climate intelligence · Hyderabad, India</div>
      <h1>Weather Analytics & Extreme Event Detection</h1>
      <p>Explore historical weather observations, investigate project-defined heat and rainfall events,
      and compare local results with distributed Apache Spark analytics stored in MinIO.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    f"Showing {start_date:%d %b %Y} – {end_date:%d %b %Y} · "
    f"Source station: Begumpet Airport · {len(filtered):,} records in the current selection"
)

if filtered.empty:
    st.info(
        "No observations match the selected date range and event type. "
        "The dashboard remains available; choose a wider date range or select 'All days'."
    )

# ---------- Overview ----------
if not filtered.empty and page == "Overview":
    st.subheader("Climate at a glance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Days in selection",
        f"{len(filtered):,}",
        help="Number of daily weather records remaining after the date range and event-type filters. Missing calendar dates are not counted.",
    )
    temp_mean = filtered["TEMP_C"].mean() if "TEMP_C" in filtered else float("nan")
    c2.metric(
        "Average temperature",
        f"{temp_mean:.1f} °C" if pd.notna(temp_mean) else "N/A",
        help="Mean of the recorded daily mean-temperature values (TEMP_C) in the current selection. Rows with missing temperatures are excluded from this calculation.",
    )
    max_temp = filtered["MAX_C"].max() if "MAX_C" in filtered else float("nan")
    c3.metric(
        "Hottest maximum",
        f"{max_temp:.1f} °C" if pd.notna(max_temp) else "N/A",
        help="Highest recorded daily maximum temperature (MAX_C) among the selected rows.",
    )
    precip = filtered["PRCP_MM"].sum(min_count=1) if "PRCP_MM" in filtered else float("nan")
    c4.metric(
        "Recorded precipitation",
        f"{precip:.1f} mm" if pd.notna(precip) else "N/A",
        help="Sum of available daily precipitation values (PRCP_MM) in the current selection. Missing precipitation values are not treated as measured zero rainfall.",
    )
    st.caption("All overview metrics below reflect the selected date range and event type. Hover over a metric label for its definition.")

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("Daily temperature")
        if filtered["TEMP_C"].notna().any():
            chart = filtered.set_index("DATE")[["TEMP_C"]].sort_index()
            st.line_chart(chart, y="TEMP_C", color="#2563eb")
        else:
            show_empty_chart("No temperature values are available for this selection.")
    with right:
        st.subheader("Daily precipitation")
        if filtered["PRCP_MM"].notna().any():
            chart = filtered.set_index("DATE")[["PRCP_MM"]].sort_index()
            st.bar_chart(chart, y="PRCP_MM", color="#0ea5e9")
        else:
            show_empty_chart("No precipitation values are available for this selection.")

    st.divider()
    st.subheader("Extreme-event snapshot")
    e1, e2, e3 = st.columns(3)
    e1.metric(
        f"Hot days (≥ {HEAT_THRESHOLD_C:.0f}°C)",
        f"{int(filtered['extreme_heat'].sum()):,}",
        help=f"Count of selected days where the recorded daily maximum temperature (MAX_C) is at least {HEAT_THRESHOLD_C:.0f}°C.",
    )
    e2.metric(
        f"Heavy-rain days (≥ {RAIN_THRESHOLD_MM:.0f} mm)",
        f"{int(filtered['heavy_rain'].sum()):,}",
        help=f"Count of selected days where recorded daily precipitation (PRCP_MM) is at least {RAIN_THRESHOLD_MM:.0f} mm.",
    )
    e3.metric(
        "Days with either event",
        f"{int((filtered['extreme_heat'] | filtered['heavy_rain']).sum()):,}",
        help="Count of unique selected days meeting the heat threshold OR the heavy-rain threshold. A day meeting both rules is counted once.",
    )
    st.caption("These counts reflect the current filters. Thresholds are illustrative project rules, not official meteorological alerts.")

    st.subheader("Latest detected events")
    events = filtered[filtered["extreme_heat"] | filtered["heavy_rain"]].copy()
    columns = [c for c in ["DATE", "MAX_C", "PRCP_MM", "event_type"] if c in events.columns]
    if events.empty:
        st.info("No extreme events match the current filters.")
    else:
        events["DATE"] = events["DATE"].dt.strftime("%Y-%m-%d")
        st.dataframe(events[columns].sort_values("DATE", ascending=False).head(12), use_container_width=True, hide_index=True)

# ---------- Trends ----------
elif not filtered.empty and page == "Weather Trends":
    st.subheader("Weather trends")
    st.markdown('<p class="section-note">Compare daily observations with monthly and yearly summaries.</p>', unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Daily temperature (°C)**")
        temperature_columns = [c for c in ["MAX_C", "TEMP_C", "MIN_C"] if c in filtered.columns and filtered[c].notna().any()]
        if temperature_columns:
            st.line_chart(filtered.sort_values("DATE").set_index("DATE")[temperature_columns])
        else:
            show_empty_chart("No temperature series available.")
    with t2:
        st.markdown("**Daily precipitation (mm)**")
        if filtered["PRCP_MM"].notna().any():
            st.bar_chart(filtered.sort_values("DATE").set_index("DATE")[["PRCP_MM"]], color="#0ea5e9")
        else:
            show_empty_chart("No precipitation series available.")

    st.divider()
    st.subheader("Monthly temperature and rainfall")
    monthly = filtered.assign(MONTH_START=filtered["DATE"].dt.to_period("M").dt.to_timestamp()).groupby("MONTH_START", as_index=True).agg(
        AVG_TEMP_C=("TEMP_C", "mean"),
        HIGHEST_MAX_C=("MAX_C", "max"),
        TOTAL_PRCP_MM=("PRCP_MM", lambda values: values.sum(min_count=1)),
    ).round(2)
    left, right = st.columns(2)
    with left:
        st.markdown("**Average temperature by month**")
        if monthly["AVG_TEMP_C"].notna().any():
            st.line_chart(monthly[["AVG_TEMP_C"]], color="#f59e0b")
        else:
            show_empty_chart("No monthly temperature data available.")
    with right:
        st.markdown("**Recorded rainfall by month**")
        if monthly["TOTAL_PRCP_MM"].notna().any():
            st.bar_chart(monthly[["TOTAL_PRCP_MM"]], color="#0ea5e9")
        else:
            show_empty_chart("No monthly precipitation data available.")
    with st.expander("View monthly summary table"):
        st.dataframe(monthly.reset_index(), use_container_width=True, hide_index=True)

# ---------- Extreme Events ----------
elif not filtered.empty and page == "Extreme Events":
    st.subheader("Extreme-weather event explorer")
    st.markdown(
        f'<p class="section-note">Project rules: maximum temperature ≥ {HEAT_THRESHOLD_C:.0f}°C; daily precipitation ≥ {RAIN_THRESHOLD_MM:.0f} mm. These are not official warning thresholds.</p>',
        unsafe_allow_html=True,
    )
    events = filtered[filtered["extreme_heat"] | filtered["heavy_rain"]].copy()
    a, b, c = st.columns(3)
    a.metric("Extreme-heat days", f"{int(filtered['extreme_heat'].sum()):,}")
    b.metric("Heavy-rain days", f"{int(filtered['heavy_rain'].sum()):,}")
    c.metric("Combined event days", f"{int((filtered['extreme_heat'] & filtered['heavy_rain']).sum()):,}")

    event_view = st.radio("Show events", ["All events", "Extreme Heat", "Heavy Rainfall"], horizontal=True)
    if event_view == "Extreme Heat":
        events = events[events["extreme_heat"]]
    elif event_view == "Heavy Rainfall":
        events = events[events["heavy_rain"]]

    event_cols = [c for c in ["DATE", "TEMP_C", "MAX_C", "MIN_C", "PRCP_MM", "event_type"] if c in events.columns]
    if events.empty:
        st.info("No events found for the selected period and event type.")
    else:
        st.dataframe(
            events[event_cols].sort_values("DATE", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download event records",
            data=events.to_csv(index=False).encode("utf-8"),
            file_name="hyderabad_extreme_events.csv",
            mime="text/csv",
        )

# ---------- Data Explorer ----------
elif not filtered.empty and page == "Data Explorer":
    st.subheader("Data explorer")
    st.markdown('<p class="section-note">Inspect the selected observations and understand the completeness of the underlying data.</p>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    d1.metric("Rows in selection", f"{len(filtered):,}")
    d2.metric("Columns", f"{len(filtered.columns):,}")
    d3.metric("Duplicate rows in selection", f"{int(filtered.duplicated().sum()):,}")

    st.markdown("**Selected weather records**")
    display = filtered.copy()
    display["DATE"] = display["DATE"].dt.strftime("%Y-%m-%d")
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.download_button(
        "Download selected records (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="hyderabad_weather_filtered.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown("**Missing values in the full cleaned dataset**")
    missing = df.isna().sum().rename("Missing values").to_frame()
    missing["Missing %"] = (missing["Missing values"] / max(len(df), 1) * 100).round(2)
    missing = missing[missing["Missing values"] > 0].sort_values("Missing values", ascending=False)
    if missing.empty:
        st.success("No missing values in the loaded dataset.")
    else:
        st.dataframe(missing, use_container_width=True)
    st.caption(
        f"Loaded dataset: {len(df):,} records from {df['DATE'].min():%Y-%m-%d} to {df['DATE'].max():%Y-%m-%d}. "
        "Missing daily observations are not imputed."
    )

# ---------- Spark + MinIO ----------
if page == "System Architecture":
    st.subheader("Distributed analytics: Apache Spark + MinIO")
    st.markdown(
        '<p class="section-note">Spark aggregates are read from the existing MinIO bucket; this page does not rerun or overwrite the Spark job.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="border:1px solid var(--border-color, rgba(128,145,165,.25));background:var(--secondary-background-color);color:var(--text-color);border-radius:16px;padding:1rem 1.1rem;margin:.5rem 0 1rem 0;">
        <div style="display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;">
          <span style="background:var(--background-color);color:var(--text-color);border:1px solid var(--border-color, rgba(128,145,165,.25));padding:.6rem .8rem;border-radius:10px;font-weight:700;">NOAA daily CSV</span>
          <span style="color:var(--text-color);">→</span>
          <span style="background:var(--background-color);color:var(--text-color);border:1px solid var(--border-color, rgba(128,145,165,.25));padding:.6rem .8rem;border-radius:10px;font-weight:700;">Python cleaning</span>
          <span style="color:var(--text-color);">→</span>
          <span style="background:var(--background-color);color:var(--text-color);border:1px solid var(--border-color, rgba(128,145,165,.25));padding:.6rem .8rem;border-radius:10px;font-weight:700;">Parquet</span>
          <span style="color:var(--text-color);">→</span>
          <span style="background:var(--background-color);color:var(--text-color);border:1px solid var(--border-color, rgba(128,145,165,.25));padding:.6rem .8rem;border-radius:10px;font-weight:700;">Spark cluster</span>
          <span style="color:var(--text-color);">→</span>
          <span style="background:var(--background-color);color:var(--text-color);border:1px solid var(--border-color, rgba(128,145,165,.25));padding:.6rem .8rem;border-radius:10px;font-weight:700;">MinIO</span>
          <span style="color:var(--text-color);">→</span>
          <span style="background:var(--background-color);color:var(--text-color);border:1px solid var(--border-color, rgba(128,145,165,.25));padding:.6rem .8rem;border-radius:10px;font-weight:700;">Streamlit</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Refresh Spark results from MinIO"):
        load_curated_parquet.clear()

    try:
        yearly_results = normalize_spark_columns(load_curated_parquet("yearly_statistics/"))
        monthly_results = normalize_spark_columns(load_curated_parquet("monthly_statistics/"))
        st.success("Connected to MinIO and queried the curated output prefixes.")
        if not yearly_results.empty:
            st.markdown("#### Yearly Spark statistics")
            st.dataframe(yearly_results, use_container_width=True, hide_index=True)
            year_col = "YEAR" if "YEAR" in yearly_results.columns else None
            measure_candidates = ["AVG_MAX_TEMP_C", "AVG_TEMP_C", "HIGHEST_TEMP_C", "TOTAL_PRECIPITATION_MM", "AVG_PRECIPITATION_MM"]
            measure = next((col for col in measure_candidates if col in yearly_results.columns), None)
            if year_col and measure:
                chart_data = yearly_results.sort_values(year_col).set_index(year_col)[[measure]]
                st.line_chart(chart_data)
        else:
            st.warning("No yearly Parquet files were found under climate-curated/yearly_statistics/.")

        if not monthly_results.empty:
            st.markdown("#### Monthly Spark statistics")
            st.dataframe(monthly_results, use_container_width=True, hide_index=True)
            if {"YEAR", "MONTH"}.issubset(monthly_results.columns):
                monthly_results["PERIOD"] = (
                    monthly_results["YEAR"].astype(int).astype(str)
                    + "-"
                    + monthly_results["MONTH"].astype(int).astype(str).str.zfill(2)
                )
                measure_candidates = ["AVG_MAX_TEMP_C", "AVG_TEMP_C", "HIGHEST_TEMP_C", "TOTAL_PRECIPITATION_MM", "AVG_PRECIPITATION_MM"]
                measure = next((col for col in measure_candidates if col in monthly_results.columns), None)
                if measure:
                    chart_data = monthly_results.sort_values(["YEAR", "MONTH"]).set_index("PERIOD")[[measure]]
                    st.line_chart(chart_data)
        else:
            st.warning("No monthly Parquet files were found under climate-curated/monthly_statistics/.")

    except Exception as error:
        st.error("Spark results could not be loaded from MinIO.")
        st.caption(f"Details: {type(error).__name__}: {error}")
        st.info(
            "The local weather dashboard remains available. Check that Docker is running, "
            "MinIO is reachable at localhost:9000, the climate-curated bucket exists, "
            "and boto3/pyarrow are installed in this Python environment."
        )

    st.divider()
    st.markdown("#### Integration status checklist")
    st.write("• Local weather data: loaded successfully for this dashboard session.")
    st.write("• Extreme-event flags: derived from the saved flags file when available, with threshold-based fallback.")
    st.write("• Spark output: fetched from MinIO on this page; cached for 60 seconds.")
    st.caption("This dashboard reads existing Spark output files. It does not submit Spark jobs or alter MinIO objects.")

# Footer
st.divider()
st.caption(
    "Source: NOAA Global Summary of the Day (GSOD), Begumpet Airport, Hyderabad. "
    "Project-defined event thresholds are illustrative and are not official weather alerts. "
    "Daily records and some meteorological fields may be missing in the source."
)
