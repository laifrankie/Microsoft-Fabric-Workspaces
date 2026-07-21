# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "da9d64f5-6f97-42f1-843b-e8bebf438c5a",
# META       "default_lakehouse_name": "lh_dp3029",
# META       "default_lakehouse_workspace_id": "191f9394-3785-4e15-b427-96135e136a7f",
# META       "known_lakehouses": [
# META         {
# META           "id": "da9d64f5-6f97-42f1-843b-e8bebf438c5a"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Architecture
# 
# Notebook #1 - demo_change-data-feed
# - Create Table
# - Simulate Updates
# 
# Lakehouse Table
# - Delta Change Data Feed (CDF)
# 
# 
# Notebook #2 (Streaming Job) - demo_streaming-reader
# - Capture INSERT / UPDATE / DELETE
# 
#     --> Console Output (for testing)
# 
#     --> Eventstream Custom Endpoint
# 
#     --> Eventhouse


# MARKDOWN ********************

# #### Step 1 - Create a Test Table

# CELL ********************

spark.sql("""
CREATE TABLE IF NOT EXISTS demo_orders
(
    order_id INT,
    customer STRING,
    amount DOUBLE,
    status STRING
)
USING DELTA
""")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Enable Change Data Feed
spark.sql("""
ALTER TABLE demo_orders
SET TBLPROPERTIES (
    delta.enableChangeDataFeed = true
)
""")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Verify - You should see:
# delta.enableChangeDataFeed = true
spark.sql("""
SHOW TBLPROPERTIES demo_orders
""").show(truncate=False)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Step 2 - Insert Test Data

# CELL ********************

spark.sql("""
INSERT INTO demo_orders VALUES
(1,'Frankie',100,'Open'),
(2,'Mary',200,'Open')
""")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Step 3 - Create a Streaming Reader

# CELL ********************

# Read the Change Data Feed
cdf = (
    spark.readStream
         .option("readChangeFeed", "true")
         .table("demo_orders")
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Inspect schema
# You should see metadata columns similar to:
#   _change_type
#   _commit_version
#   _commit_timestamp

cdf.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Step 4 - Output Changes to Console

# CELL ********************

query = (
    cdf.writeStream
       .format("console")
       .outputMode("append")
       .start()
)

#query.awaitTermination()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

display(
    spark.read
         .option("readChangeFeed", "true")
         .option("startingVersion", 1)
         .table("demo_orders")
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

display(
    spark.sql("""
    DESCRIBE HISTORY demo_orders
    """)
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Step 5 - Generate Updates

# CELL ********************

spark.sql("""
UPDATE demo_orders
SET amount = 992
WHERE order_id = 1
""")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

spark.sql("""
DELETE FROM demo_orders
WHERE order_id = 2
""")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

spark.sql("""
INSERT INTO demo_orders
VALUES (3,'Candy',500,'Open')
""")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = (
    spark.read
         .option("readChangeFeed", "true")
         .option("startingVersion", 1)
         .table("demo_orders")
)

df.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df.select(
    "_change_type",
    "_commit_version",
    "_commit_timestamp",
    "order_id",
    "amount"
).show(truncate=False)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

filtered = (
    spark.readStream
         .option("readChangeFeed", "true")
         .table("demo_orders")
         .filter("""
             _change_type in
             ('insert',
              'update_postimage',
              'delete')
         """)
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import *

events = filtered.select(
    to_json(
        struct(
            col("_change_type").alias("operation"),
            col("order_id"),
            col("customer"),
            col("amount"),
            col("status"),
            col("_commit_timestamp").alias("eventTime")
        )
    ).alias("payload")
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
