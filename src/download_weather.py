
from pathlib import Path
import urllib.request
import csv

RAW_DIR = Path("data/raw/weather")
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = (
    "https://www.ncei.noaa.gov/data/"
    "global-summary-of-the-day/access"
)

for year in range(2020, 2026):
    url = f"{BASE_URL}/{year}/43128099999.csv"
    output_file = RAW_DIR / f"hyderabad_daily_{year}.csv"

    print(f"Downloading {year}...")

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ClimateAnalyticsProject/1.0"}
        )

        with urllib.request.urlopen(request, timeout=60) as response:
            content = response.read()

        # Validate that the response is a CSV with the expected header.
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(text.splitlines())

        required_columns = {"DATE", "TEMP", "MAX", "MIN", "PRCP"}
        if not reader.fieldnames or not required_columns.issubset(
            set(reader.fieldnames)
        ):
            print(f"Unexpected CSV format for {year}; skipping.")
            continue

        rows = list(reader)
        if not rows:
            print(f"No daily records returned for {year}; skipping.")
            continue

        output_file.write_bytes(content)
        print(f"Saved {len(rows)} records to {output_file}")

    except Exception as error:
        print(f"Failed for {year}: {error}")

print("Download process finished.")
