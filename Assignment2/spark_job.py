from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import json

# Read AWS credentials from aws.json
with open('aws.json', 'r') as f:
    configuration = json.load(f)

# Read Spark URL from spark.json
with open('spark.json', 'r') as f:
    spark_url = json.load(f)['url']

# Read Kafka broker address from kafka.json
with open('kafka.json', 'r') as f:
    kafka_url = json.load(f)['kafkaBroker']

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("KafkaToS3") \
        .master(spark_url) \
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                "org.apache.hadoop:hadoop-aws:3.3.4") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.access.key", configuration.get('AWS_ACCESS_KEY')) \
        .config("spark.hadoop.fs.s3a.secret.key", configuration.get('AWS_SECRET_KEY')) \
        .config('spark.hadoop.fs.s3a.endpoint', configuration.get('S3_ENDPOINT')) \
        .config('spark.hadoop.fs.s3a.aws.credentials.provider',
                'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider') \
        .getOrCreate()

    # Adjust the log level to minimize the console output on executors
    spark.sparkContext.setLogLevel('WARN')

    # Define schemas
    vehicleSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("speed", DoubleType(), True),
        StructField("length", DoubleType(), True),
        StructField("elevation", DoubleType(), True),
        StructField("make", StringType(), True),
        StructField("model", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("fuelType", StringType(), True)
    ])

    failureSchema = StructType([
        StructField("id", StringType(), True),
        StructField("deviceId", StringType(), True),
        StructField("incidentId", StringType(), True),
        StructField("type", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("description", StringType(), True)
    ])

    weatherSchema = StructType([
        StructField("temperature", DoubleType(), True),
        StructField("weatherCondition", StringType(), True),
        StructField("windSpeed", DoubleType(), True),
        StructField("humidity", IntegerType(), True),
        StructField("airQualityIndex", IntegerType(), True),
        StructField("timestamp", TimestampType(), True)
    ])

    def read_kafka_topic(topic, schema, source_name):
        return (spark.readStream
                .format('kafka')
                .option('kafka.bootstrap.servers', kafka_url)
                .option('subscribe', topic)
                .option('startingOffsets', 'earliest')
                .option('failOnDataLoss', 'false')
                .load()
                .selectExpr('CAST(value AS STRING)')
                .select(from_json(col('value'), schema).alias('data'))
                .select('data.*')
                .withColumn("source", lit(source_name))
                .withWatermark('timestamp', '2 minutes'))

    def streamWriter(input_df, checkpoint_folder, output_path):
        return (input_df.coalesce(1)
                .writeStream
                .format('csv')
                .option('checkpointLocation', checkpoint_folder)
                .option('path', output_path)
                .option('header', 'true')
                .outputMode('append')
                .start())

    vehicleDF = read_kafka_topic('vehicle_data', vehicleSchema, "vehicle")
    failuresDF = read_kafka_topic('failures_data', failureSchema, "failures")
    weatherDF = read_kafka_topic('weather_data', weatherSchema, "weather")

    common_output_path = 's3a://g23ai1052/new/'

    query1 = streamWriter(vehicleDF, 's3a://g23ai1052/new/checkpoints/vehicle_data', common_output_path)
    query2 = streamWriter(failuresDF, 's3a://g23ai1052/new/checkpoints/failures_data', common_output_path)
    query3 = streamWriter(weatherDF, 's3a://g23ai1052/new/checkpoints/weather_data', common_output_path)

    query1.awaitTermination()
    query2.awaitTermination()
    query3.awaitTermination()

if __name__ == "__main__":
    main()
