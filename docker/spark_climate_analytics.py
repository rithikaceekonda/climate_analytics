
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, year, month, avg, max as spark_max,
    min as spark_min, count, round as spark_round
)

spark = (
    SparkSession.builder
    .appName("HyderabadClimateAnalytics")
    .master("spark://spark-master:7077")
    .config(
        "spark.jars",
        "/opt/spark/extra-jars/hadoop-aws-3.3.4.jar,"
        "/opt/spark/extra-jars/aws-java-sdk-bundle-1.12.262.jar"
    )
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", "climateadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "ClimateLab2026!")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config(
        "spark.hadoop.fs.s3a.impl",
        "org.apache.hadoop.fs.s3a.S3AFileSystem"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

try:
    input_path = (
        "s3a://climate-processed/hyderabad_weather_clean.parquet"
    )

    weather = spark.read.parquet(input_path)

    print("\n===== DATASET SCHEMA =====")
    weather.printSchema()

    print("\n===== TOTAL RECORDS =====")
    print(weather.count())

    print("\n===== SAMPLE RECORDS =====")
    weather.show(5, truncate=False)

    print("\n===== YEARLY CLIMATE STATISTICS =====")
    yearly = (
        weather
        .withColumn("YEAR", year(col("DATE").cast("date")))
        .groupBy("YEAR")
        .agg(
            count("*").alias("RECORDS"),
            spark_round(avg("MAX_C"), 2).alias("AVG_MAX_TEMP_C"),
            spark_round(spark_max("MAX_C"), 2).alias("HIGHEST_TEMP_C"),
            spark_round(spark_min("MIN_C"), 2).alias("LOWEST_MIN_TEMP_C"),
            spark_round(avg("PRCP_MM"), 2).alias("AVG_PRECIPITATION_MM")
        )
        .orderBy("YEAR")
    )

    yearly.show(20, truncate=False)

    print("\n===== MONTHLY CLIMATE STATISTICS =====")
    monthly = (
        weather
        .withColumn("YEAR", year(col("DATE").cast("date")))
        .withColumn("MONTH", month(col("DATE").cast("date")))
        .groupBy("YEAR", "MONTH")
        .agg(
            count("*").alias("RECORDS"),
            spark_round(avg("MAX_C"), 2).alias("AVG_MAX_TEMP_C"),
            spark_round(avg("PRCP_MM"), 2).alias("AVG_PRECIPITATION_MM")
        )
        .orderBy("YEAR", "MONTH")
    )

    
    monthly.show(100, truncate=False)

    # Save yearly statistics to MinIO
    yearly_output = "s3a://climate-curated/yearly_statistics/"
    yearly.write.mode("overwrite").parquet(yearly_output)
    print(f"Yearly statistics saved to {yearly_output}")

    # Save monthly statistics to MinIO
    monthly_output = "s3a://climate-curated/monthly_statistics/"
    monthly.write.mode("overwrite").parquet(monthly_output)
    print(f"Monthly statistics saved to {monthly_output}")

    print("\nSUCCESS: Distributed climate analytics completed.")


finally:
    spark.stop()
