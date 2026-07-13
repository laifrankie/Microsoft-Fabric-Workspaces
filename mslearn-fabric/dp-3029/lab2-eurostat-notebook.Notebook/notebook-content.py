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
# META     },
# META     "environment": {
# META       "environmentId": "733ece04-9b40-9ddf-40d6-277b7e975d06",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# MARKDOWN ********************

#  # Explore Eurostat population data.
#  Use this notebook to explore population data from Eurostat

# CELL ********************

 %%code
    
 Download the following file from this URL:
    
 https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/proj_23np$defaultview/?format=TSV
     
 Then write the file to the default lakehouse into a folder named temp. Create the folder if it doesn't exist yet.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

import requests
import os

# Define the URL and the local path
url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/proj_23np$defaultview/?format=TSV"
local_path = "/lakehouse/default/Files/temp/"
file_name = "proj_23np.tsv"
file_path = os.path.join(local_path, file_name)

# Create the temporary directory if it doesn't exist
if not os.path.exists(local_path):
    os.makedirs(local_path)

# Download the file
response = requests.get(url)
response.raise_for_status()  # Check that the request was successful

# Write the content to the file
with open(file_path, "wb") as file:
    file.write(response.content)

print(f"File downloaded and saved to {file_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC Load the file 'Files/temp/proj_23np.tsv' into a spark dataframe.
# MAGIC 
# MAGIC The fields are separated with a tab.
# MAGIC 
# MAGIC Show the contents of the DataFrame using display method.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

# Load the tab-separated values file into a spark dataframe and display its contents
file_path = "Files/temp/proj_23np.tsv"

spark_df = spark.read.format("csv") \
    .option("header", "true") \
    .option("sep", "\t") \
    .load(file_path)

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC From the currently loaded DataFrame, split the first field 'freq,projection,sex,age,unit,geo\TIME_PERIOD' using a comma into 6 separate fields. Then, remove the original column.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

from pyspark.sql.functions import split, col

# Split the combined column into six individual columns
split_col = split(col('freq,projection,sex,age,unit,geo\\TIME_PERIOD'), ',')

spark_df = spark_df \
    .withColumn('freq', split_col.getItem(0)) \
    .withColumn('projection', split_col.getItem(1)) \
    .withColumn('sex', split_col.getItem(2)) \
    .withColumn('age', split_col.getItem(3)) \
    .withColumn('unit', split_col.getItem(4)) \
    .withColumn('geo', split_col.getItem(5)) \
    .drop('freq,projection,sex,age,unit,geo\\TIME_PERIOD')

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC From the currently loaded DataFrame, remove the fields 'freq', 'age', 'unit'.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

# Remove the fields 'freq', 'age', 'unit' from the loaded DataFrame
spark_df = spark_df.drop('freq', 'age', 'unit')

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC From the currently loaded DataFrame, the fields 'projection', 'sex', 'geo' should be positioned first.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

# Reorder the fields so 'projection', 'sex', 'geo' are first
cols = spark_df.columns
desired_order = ['projection', 'sex', 'geo'] + [col for col in cols if col not in ['projection', 'sex', 'geo']]
spark_df = spark_df.select(desired_order)

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC The 'projection' field contains codes that should be replaced with the following values:
# MAGIC     _'BSL' -> 'Baseline projections'.
# MAGIC     _'LFRT' -> 'Sensitivity test: lower fertility'.
# MAGIC     _'LMRT' -> 'Sensitivity test: lower mortality'.
# MAGIC     _'HMIGR' -> 'Sensitivity test: higher migration'.
# MAGIC     _'LMIGR' -> 'Sensitivity test: lower migration'.
# MAGIC     _'NMIGR' -> 'Sensitivity test: no migration'.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

from pyspark.sql.functions import when

# Replace codes in 'projection' field with their corresponding values
spark_df = spark_df.withColumn(
    "projection",
    when(spark_df["projection"] == "BSL", "Baseline projections")
    .when(spark_df["projection"] == "LFRT", "Sensitivity test: lower fertility")
    .when(spark_df["projection"] == "LMRT", "Sensitivity test: lower mortality")
    .when(spark_df["projection"] == "HMIGR", "Sensitivity test: higher migration")
    .when(spark_df["projection"] == "LMIGR", "Sensitivity test: lower migration")
    .when(spark_df["projection"] == "NMIGR", "Sensitivity test: no migration")
    .otherwise(spark_df["projection"])
)

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC Filter the 'geo' field and remove values 'EA20' and 'EU27_2020' (these are not countries).

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

# Filter out rows where 'geo' is 'EA20' or 'EU27_2020'
spark_df = spark_df.filter(~spark_df['geo'].isin(['EA20', 'EU27_2020']))

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC Filter the 'sex' field and remove 'T' (these are totals).

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

# Filter out rows where 'sex' is 'T'
spark_df = spark_df.filter(spark_df['sex'] != 'T')

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC Strip spaces from all field names in the dataframe.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

# Strip spaces from all column names in the DataFrame
for old_name in spark_df.columns:
    new_name = old_name.strip()
    if old_name != new_name:
        spark_df = spark_df.withColumnRenamed(old_name, new_name)

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC Convert the data type of all the year fields to integer.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

from pyspark.sql.functions import col

# Identify year columns by checking if the column name consists of 4 digits
year_columns = [c for c in spark_df.columns if c.isdigit() and len(c) == 4]

for year_col in year_columns:
    spark_df = spark_df.withColumn(year_col, col(year_col).cast("integer"))

display(spark_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%code
# MAGIC 
# MAGIC Save the dataframe as a new table named 'Population' in the default lakehouse.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

# Save the dataframe as a new table named 'Population' in the default lakehouse
spark_df.write.format("delta").saveAsTable("Population")
# If you want to overwrite the table in future runs, use:
# spark_df.write.mode("overwrite").format("delta").saveAsTable("Population")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#### ATTENTION: AI-generated code can include errors or operations you didn't intend. Review the code in this cell carefully before running it.

import plotly.graph_objs as go

# Perform the SQL query to get projected population trends for geo BE, summing up male and female numbers
result = spark.sql(
    """
    SELECT projection, sex, geo, SUM(`2022`) as `2022`, SUM(`2023`) as `2023`, SUM(`2025`) as `2025`,
        SUM(`2030`) as `2030`, SUM(`2035`) as `2035`, SUM(`2040`) as `2040`,
        SUM(`2045`) as `2045`, SUM(`2050`) as `2050`
    FROM Population
    WHERE geo = 'BE' AND projection = 'Baseline projections'
    GROUP BY projection, sex, geo
    """
)
df = result.groupBy("projection").sum()
df = df.orderBy("projection").toPandas()

# Extract data for the line chart
years = df.columns[1:].tolist()
values = df.iloc[0, 1:].tolist()

# Create the plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=years, y=values, mode='lines+markers', name='Projected Population'))

# Update the layout
fig.update_layout(
    title='Projected Population Trends for Geo BE (Belgium) from 2022 to 2050',
    xaxis_title='Year',
    yaxis_title='Population',
    template='plotly_dark'
)

# Display the plot
fig.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
