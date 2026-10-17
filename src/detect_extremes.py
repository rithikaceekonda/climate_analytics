
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/processed/hyderabad_weather_clean.csv")
OUTPUT_DIR = Path("data/processed/extreme_weather")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input dataset not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
df["MAX_C"] = pd.to_numeric(df["MAX_C"], errors="coerce")
df["PRCP_MM"] = pd.to_numeric(df["PRCP_MM"], errors="coerce")

# Project-defined thresholds, not official warning thresholds.
HEAT_THRESHOLD_C = 40.0
HEAVY_RAIN_THRESHOLD_MM = 50.0

df["extreme_heat"] = df["MAX_C"] >= HEAT_THRESHOLD_C
df["heavy_rain"] = df["PRCP_MM"] >= HEAVY_RAIN_THRESHOLD_MM

df["event_type"] = "Normal"
df.loc[df["extreme_heat"], "event_type"] = "Extreme Heat"
df.loc[df["heavy_rain"], "event_type"] = "Heavy Rainfall"

# Identify days that meet both thresholds.
both = df["extreme_heat"] & df["heavy_rain"]
df.loc[both, "event_type"] = "Extreme Heat + Heavy Rainfall"

# Save every observation with its detection flags.
flags_file = OUTPUT_DIR / "weather_with_extreme_flags.csv"
df.to_csv(flags_file, index=False)

# Save only observations flagged as extreme.
extremes = df[df["extreme_heat"] | df["heavy_rain"]].copy()
extremes = extremes.sort_values("DATE")

extremes_file = OUTPUT_DIR / "extreme_weather_days.csv"
extremes.to_csv(extremes_file, index=False)

print("\nExtreme-weather detection completed.")
print("Total observations:", len(df))
print("Extreme-heat days:", int(df["extreme_heat"].sum()))
print("Heavy-rainfall days:", int(df["heavy_rain"].sum()))
print("Days meeting both thresholds:", int(both.sum()))
print("Unique extreme-weather days:", len(extremes))

print("\nEvent counts:")
print(extremes["event_type"].value_counts().to_string())

print("\nTop 10 extreme-weather observations:")
print(
    extremes[
        ["DATE", "MAX_C", "PRCP_MM", "event_type"]
    ].head(10).to_string(index=False)
)

print("\nSaved files:")
print(flags_file)
print(extremes_file)
