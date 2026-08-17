from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.utils.dates import days_ago

default_args = {
  'owner': 'airflow'
}

with DAG('databricks_dag',
  start_date = days_ago(1),
  schedule_interval = "@hourly",
  catchup=False,
  default_args = default_args
) as dag:

 transform_data = DatabricksRunNowOperator(
    task_id = 'transform_data',
    databricks_conn_id = 'databricks_default',
    job_id ="1062991436615878"
  )