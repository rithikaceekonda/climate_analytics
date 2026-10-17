
from pathlib import Path
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

input_path = Path(
    "data/processed/hyderabad_weather_clean.parquet"
).resolve()

output_dir = Path("data/processed/spark_output")
output_dir.mkdir(parents=True, exist_ok=True)

if not input_path.exists():
    raise FileNotFoundError(f"Parquet file not found: {input_path}")

spark = (
    SparkSession.builder
    .appName("HyderabadClimateAnalytics")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\nReading cleaned Parquet data...")
    df = spark.read.parquet(input_path.as_posix())

    print("Total records:", df.count())
    df.printSchema()

    print("\nSample records:")
    df.show(5, truncate=False)

    print("\nCalculating monthly weather statistics...")

    monthly = (
        df.groupBy("YEAR", "MONTH")
        .agg(
            F.count("*").alias("days_recorded"),
            F.round(F.avg("TEMP_C"), 2).alias("avg_temp_c"),
            F.round(F.max("MAX_C"), 2).alias("highest_max_temp_c"),
            F.round(F.min("MIN_C"), 2).alias("lowest_min_temp_c"),
            F.round(F.sum("PRCP_MM"), 2).alias("total_precipitation_mm"),
        )
        .orderBy("YEAR", "MONTH")
    )

    monthly.show(72, truncate=False)

    # Convert the small summary table to Pandas and save as CSV.
    monthly_csv = output_dir / "monthly_statistics.csv"
    monthly.toPandas().to_csv(monthly_csv, index=False)
    print("Monthly results saved to:", monthly_csv.resolve())

    print("\nCalculating yearly weather statistics...")

    yearly = (
        df.groupBy("YEAR")
        .agg(
            F.count("*").alias("days_recorded"),
            F.round(F.avg("TEMP_C"), 2).alias("avg_temp_c"),
            F.round(F.max("MAX_C"), 2).alias("highest_max_temp_c"),
            F.round(F.min("MIN_C"), 2).alias("lowest_min_temp_c"),
            F.round(F.sum("PRCP_MM"), 2).alias("total_precipitation_mm"),
        )
        .orderBy("YEAR")
    )

    yearly.show(truncate=False)

    yearly_csv = output_dir / "yearly_statistics.csv"
    yearly.toPandas().to_csv(yearly_csv, index=False)
    print("Yearly results saved to:", yearly_csv.resolve())

    print("\nPySpark analysis completed successfully.")

finally:
    spark.stop()
