from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("WeatherDataInspection") \
    .master("local[*]") \
    .getOrCreate()

# Read all Hyderabad yearly CSV files
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("data/raw/weather/*.csv")

print("\n========== SCHEMA ==========")
df.printSchema()

print("\n========== FIRST 10 RECORDS ==========")
df.show(10, truncate=False)

print("\n========== NUMBER OF RECORDS ==========")
print(df.count())

print("\n========== COLUMNS ==========")
for column in df.columns:
    print(column)

spark.stop()