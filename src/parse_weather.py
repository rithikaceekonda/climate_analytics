
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/weather")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(RAW_DIR.glob("hyderabad_daily_*.csv"))

if not files:
    raise FileNotFoundError(
        "No daily weather CSV files found. "
        "Run src/download_weather.py first."
    )

frames = []

for file in files:
    print(f"Reading {file.name}...")
    df = pd.read_csv(file, low_memory=False)
    df.columns = df.columns.str.strip()

    required = {"DATE", "TEMP", "MAX", "MIN", "PRCP"}
    if not required.issubset(df.columns):
        raise ValueError(f"Unexpected columns in {file.name}")

    frames.append(df)

weather = pd.concat(frames, ignore_index=True)

# Parse dates and convert weather measurements to numbers.
weather["DATE"] = pd.to_datetime(weather["DATE"], errors="coerce")

numeric_columns = [
    "TEMP", "DEWP", "SLP", "STP", "VISIB",
    "WDSP", "MXSPD", "GUST", "MAX", "MIN",
    "PRCP", "SNDP"
]

for column in numeric_columns:
    if column in weather.columns:
        weather[column] = pd.to_numeric(
            weather[column], errors="coerce"
        )

# Replace NOAA's missing-value markers.
missing_markers = [9999.9, 999.9, 99.99, 999.99]

for column in numeric_columns:
    if column in weather.columns:
        weather[column] = weather[column].replace(
            missing_markers, float("nan")
        )

# Remove invalid dates and duplicate daily observations.
weather = weather.dropna(subset=["DATE", "TEMP"])
weather = weather.drop_duplicates(subset=["STATION", "DATE"])
weather = weather.sort_values("DATE").reset_index(drop=True)

# NOAA GSOD temperatures are in Fahrenheit.
for column in ["TEMP", "DEWP", "MAX", "MIN"]:
    if column in weather.columns:
        weather[column + "_C"] = (
            weather[column] - 32
        ) * 5 / 9

# NOAA GSOD precipitation is in inches.
weather["PRCP_MM"] = weather["PRCP"] * 25.4

# Add date features for analysis and visualization.
weather["YEAR"] = weather["DATE"].dt.year
weather["MONTH"] = weather["DATE"].dt.month
weather["DAY"] = weather["DATE"].dt.day

# Keep the useful fields for our project.
columns_to_keep = [
    "STATION", "DATE", "NAME", "LATITUDE", "LONGITUDE",
    "TEMP_C", "MAX_C", "MIN_C", "DEWP_C",
    "PRCP_MM", "WDSP", "MXSPD", "GUST", "VISIB",
    "SLP", "STP", "SNDP", "FRSHTT",
    "YEAR", "MONTH", "DAY"
]

weather = weather[
    [column for column in columns_to_keep if column in weather.columns]
]


csv_path = OUTPUT_DIR / "hyderabad_weather_clean.csv"
parquet_path = OUTPUT_DIR / "hyderabad_weather_clean.parquet"

# Keep DATE as YYYY-MM-DD text for Spark compatibility.
weather["DATE"] = weather["DATE"].dt.strftime("%Y-%m-%d")

weather.to_csv(csv_path, index=False)
weather.to_parquet(parquet_path, index=False)

print("\nCleaning completed successfully!")
print("Total records:", len(weather))
print("CSV saved to:", csv_path)
print("Parquet saved to:", parquet_path)
print("\nSample records:")
print(weather.head().to_string(index=False))
print("\nMissing values:")
print(weather.isna().sum().to_string())
