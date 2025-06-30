# Databricks notebook source
spark.read.parquet("dbfs:/mnt/modelnonuc/2025-06-17-Export-jobid-34179827290231/checkpoint/models/*.parquet").createOrReplaceTempView("models")


# COMMAND ----------

# MAGIC %sql
# MAGIC select * from models
# MAGIC -- select count(distinct(model)) from models -- model=1202
# MAGIC -- select count(distinct(experiment_id)) from models -- experiment=771

# COMMAND ----------

spark.read.parquet("dbfs:/mnt/modelnonuc/2025-06-17-Export-jobid-34179827290231/checkpoint/experiments").createOrReplaceTempView("experiments")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from experiments
# MAGIC -- select count(distinct(experiment_id)) from experiments --1774

# COMMAND ----------



# COMMAND ----------

from pyspark.sql.functions import regexp_extract, col

log_df = spark.read.text("dbfs:/mnt/modelnonuc/2025-06-17-Export-jobid-34179827290231/jobrunid-548033559076165/*/export_all_*.log")

# Define regex pattern
pattern = r"^(\d{2}-\w{3}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - \[([^\]:]+):(\d+)\] - (.*)$"

# Parse fields using regex
parsed_df = log_df.select(
    regexp_extract('value', pattern, 1).alias('timestamp'),
    regexp_extract('value', pattern, 2).alias('level'),
    regexp_extract('value', pattern, 3).alias('module'),
    regexp_extract('value', pattern, 4).alias('line_no'),
    regexp_extract('value', pattern, 5).alias('message')
)

parsed_df.createOrReplaceTempView("df")
display(parsed_df)

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select line_no,count(*),first(module) from df where level="ERROR" group by line_no

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from df where level="ERROR" and  line_no=78

# COMMAND ----------


