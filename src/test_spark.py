from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ClimateAnalytics") \
    .master("local[*]") \
    .getOrCreate()

data = [
    ("Hyderabad", 32.5),
    ("Delhi", 35.2),
    ("Mumbai", 30.8),
    ("Bangalore", 27.4)
]

df = spark.createDataFrame(
    data,
    ["city", "temperature"]
)

df.show()

spark.stop()