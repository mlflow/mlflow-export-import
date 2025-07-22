from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType

import time

df = spark.read.option("header", "true").csv("dbfs:/databricks-datasets/retail-org/customers/customers.csv")

@udf(StringType())
def to_upper_udf(name):
    time.sleep(0.01)
    return name.upper() if name else None

df = df.withColumn("name_upper", to_upper_udf(col("customer_name")))

df = df.repartition(200)

df.cache()
df = df.filter(col("state") == "CA")

results = df.collect()

df.write.mode("overwrite").csv("dbfs:/tmp/inefficient_output")