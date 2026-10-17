
from pyspark.sql import SparkSession

MINIO_ACCESS_KEY = "climateadmin"
MINIO_SECRET_KEY = "ClimateLab2026!"

spark = (
    SparkSession.builder
    .appName("ClimateMinIOConnectionTest")
    .master("spark://spark-master:7077")
    .config("spark.jars", "/opt/spark/extra-jars/hadoop-aws-3.3.4.jar,/opt/spark/extra-jars/aws-java-sdk-bundle-1.12.262.jar")
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

try:
    path = "s3a://climate-processed/"
    fs = spark.sparkContext._jvm.org.apache.hadoop.fs.FileSystem.get(
        spark.sparkContext._jvm.java.net.URI(path),
        spark.sparkContext._jsc.hadoopConfiguration()
    )

    print("\nFiles found in climate-processed:")
    for item in fs.listStatus(spark.sparkContext._jvm.org.apache.hadoop.fs.Path(path)):
        print(item.getPath().toString())

    print("\nSUCCESS: Spark connected to MinIO.")
finally:
    spark.stop()
