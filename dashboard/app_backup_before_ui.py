
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hyderabad Climate Analytics",
    page_icon="🌦️",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "processed" / "hyderabad_weather_clean.csv"
EXTREME_FILE = (
    BASE_DIR / "data" / "processed" / "extreme_weather"
    / "weather_with_extreme_flags.csv"
)

st.title("🌦️ Hyderabad Climate Analytics")
st.caption(
    "Historical weather analysis and project-defined extreme-weather detection"
)

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    data = pd.read_csv(DATA_FILE)
    data["DATE"] = pd.to_datetime(data["DATE"], errors="coerce")

    for column in ["TEMP_C", "MAX_C", "MIN_C", "PRCP_MM"]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    if EXTREME_FILE.exists():
        flags = pd.read_csv(EXTREME_FILE)
        flags["DATE"] = pd.to_datetime(flags["DATE"], errors="coerce")

        # Use detection flags when available.
        extra_columns = [
            "DATE", "extreme_heat", "heavy_rain", "event_type"
        ]
        available = [c for c in extra_columns if c in flags.columns]

        data = data.merge(
            flags[available].drop_duplicates(subset=["DATE"]),
            on="DATE",
            how="left",
        )
    else:
        data["extreme_heat"] = data["MAX_C"] >= 40
        data["heavy_rain"] = data["PRCP_MM"] >= 50
        data["event_type"] = "Normal"
        data.loc[data["extreme_heat"], "event_type"] = "Extreme Heat"
        data.loc[data["heavy_rain"], "event_type"] = "Heavy Rainfall"
        both = data["extreme_heat"] & data["heavy_rain"]
        data.loc[both, "event_type"] = "Extreme Heat + Heavy Rainfall"

    for column in ["extreme_heat", "heavy_rain"]:
        if column in data.columns:
            data[column] = (
                data[column]
                .astype("string")
                .str.lower()
                .map({"true": True, "false": False})
                .fillna(False)
                .astype(bool)
            )

    return data.dropna(subset=["DATE"]).sort_values("DATE")


try:
    df = load_data()
except Exception as error:
    st.error(f"Could not load the weather dataset: {error}")
    st.stop()

if df.empty:
    st.warning("The dataset contains no usable weather records.")
    st.stop()

st.sidebar.header("Filters")

min_date = df["DATE"].min().date()
max_date = df["DATE"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = df[
        (df["DATE"].dt.date >= start_date)
        & (df["DATE"].dt.date <= end_date)
    ].copy()
else:
    filtered = df[df["DATE"].dt.date == date_range].copy()

event_options = ["All days", "Extreme Heat", "Heavy Rainfall", "Any extreme"]
event_filter = st.sidebar.selectbox("Weather event", event_options)

if event_filter == "Extreme Heat":
    filtered = filtered[filtered["extreme_heat"]]
elif event_filter == "Heavy Rainfall":
    filtered = filtered[filtered["heavy_rain"]]
elif event_filter == "Any extreme":
    filtered = filtered[
        filtered["extreme_heat"] | filtered["heavy_rain"]
    ]

st.subheader("Weather overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Days in selection", f"{len(filtered):,}")

if "TEMP_C" in filtered:
    c2.metric(
        "Average temperature",
        f"{filtered['TEMP_C'].mean():.1f} °C"
        if filtered["TEMP_C"].notna().any() else "N/A",
    )

if "MAX_C" in filtered:
    c3.metric(
        "Highest maximum temperature",
        f"{filtered['MAX_C'].max():.1f} °C"
        if filtered["MAX_C"].notna().any() else "N/A",
    )

if "PRCP_MM" in filtered:
    c4.metric(
        "Total recorded precipitation",
        f"{filtered['PRCP_MM'].sum():.1f} mm"
        if filtered["PRCP_MM"].notna().any() else "N/A",
    )

if filtered.empty:
    st.info("No observations match these filters.")
    st.stop()

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Daily average temperature")
    if filtered["TEMP_C"].notna().any():
        temperature = (
            filtered.set_index("DATE")[["TEMP_C"]]
            .sort_index()
        )
        st.line_chart(temperature, y="TEMP_C")
    else:
        st.info("No temperature values available.")

with right:
    st.subheader("Daily precipitation")
    if filtered["PRCP_MM"].notna().any():
        precipitation = (
            filtered.set_index("DATE")[["PRCP_MM"]]
            .sort_index()
        )
        st.bar_chart(precipitation, y="PRCP_MM")
    else:
        st.info("No precipitation values available.")

st.divider()

st.subheader("Monthly temperature trends")

monthly = (
    filtered.dropna(subset=["DATE", "TEMP_C"])
    .assign(MONTH_START=lambda x: x["DATE"].dt.to_period("M").dt.to_timestamp())
    .groupby("MONTH_START", as_index=False)
    .agg(
        average_temperature_c=("TEMP_C", "mean"),
        maximum_temperature_c=("MAX_C", "max"),
    )
    .set_index("MONTH_START")
    .round(2)
)

if not monthly.empty:
    st.line_chart(monthly)
else:
    st.info("No monthly temperature data available.")

st.divider()

st.subheader("Extreme-weather summary")

heat_days = int(filtered["extreme_heat"].sum())
rain_days = int(filtered["heavy_rain"].sum())

e1, e2 = st.columns(2)
e1.metric("Extreme-heat days (≥ 40°C)", heat_days)
e2.metric("Heavy-rain days (≥ 50 mm)", rain_days)

extremes = filtered[
    filtered["extreme_heat"] | filtered["heavy_rain"]
].copy()

display_columns = [
    "DATE", "TEMP_C", "MAX_C", "PRCP_MM", "event_type"
]
display_columns = [c for c in display_columns if c in extremes.columns]

st.dataframe(
    extremes[display_columns].sort_values("DATE", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download filtered weather data",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="hyderabad_weather_filtered.csv",
    mime="text/csv",
)

st.caption(
    "Source: NOAA Global Summary of the Day, Begumpet Airport, Hyderabad. "
    "Extreme-event thresholds are illustrative project rules, not official alerts."
)

st.divider()
st.header("☁️ Distributed Big Data Analytics")
st.caption(
    "Monthly and yearly aggregates computed by Apache Spark "
    "and stored in MinIO object storage."
)

@st.cache_data(ttl=60)
def load_curated_parquet(prefix):
    import io
    import pyarrow.parquet as pq
    import boto3

    client = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="climateadmin",
        aws_secret_access_key="ClimateLab2026!",
        config=__import__("botocore.config", fromlist=["Config"]).Config(
            signature_version="s3v4"
        ),
        region_name="us-east-1",
    )

    paginator = client.get_paginator("list_objects_v2")
    objects = []
    for page in paginator.paginate(
        Bucket="climate-curated",
        Prefix=prefix,
    ):
        objects.extend(
            item for item in page.get("Contents", [])
            if item["Key"].endswith(".parquet")
        )

    if not objects:
        return pd.DataFrame()

    frames = []
    for item in objects:
        response = client.get_object(
            Bucket="climate-curated",
            Key=item["Key"],
        )
        table = pq.read_table(io.BytesIO(response["Body"].read()))
        frames.append(table.to_pandas())

    return pd.concat(frames, ignore_index=True)


try:
    yearly_results = load_curated_parquet("yearly_statistics/")
    monthly_results = load_curated_parquet("monthly_statistics/")

    if not yearly_results.empty:
        st.subheader("Yearly climate statistics")
        st.dataframe(yearly_results, use_container_width=True, hide_index=True)

        if "YEAR" in yearly_results.columns and "AVG_MAX_TEMP_C" in yearly_results.columns:
            chart_data = yearly_results.set_index("YEAR")[["AVG_MAX_TEMP_C"]]
            st.line_chart(chart_data)

    if not monthly_results.empty:
        st.subheader("Monthly climate statistics")
        st.dataframe(monthly_results, use_container_width=True, hide_index=True)

        if {"YEAR", "MONTH", "AVG_MAX_TEMP_C"}.issubset(monthly_results.columns):
            monthly_results["PERIOD"] = (
                monthly_results["YEAR"].astype(int).astype(str)
                + "-"
                + monthly_results["MONTH"].astype(int).astype(str).str.zfill(2)
            )
            chart_data = monthly_results.set_index("PERIOD")[["AVG_MAX_TEMP_C"]]
            st.line_chart(chart_data)

    if yearly_results.empty and monthly_results.empty:
        st.info(
            "No curated Parquet outputs were found in MinIO. "
            "Run the Spark analytics job first."
        )

except Exception as error:
    st.warning(f"Could not load Spark results from MinIO: {error}")
    st.info(
        "Check that Docker is running and that the curated Parquet "
        "outputs exist in MinIO."
    )

