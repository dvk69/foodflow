import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# Add project root to sys.path so Airflow can import from ingestion module
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ingestion import iot_generator, usda_extractor, epa_extractor, instacart_generator, run_ingestion
try:
    from alerts import task_failure_slack_alert
except ImportError:
    from plugins.alerts import task_failure_slack_alert

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,  # Automatically retry twice on transient failure
    "retry_delay": timedelta(seconds=10),  # Backoff delay
    "on_failure_callback": task_failure_slack_alert,
}

with DAG(
    dag_id="foodflow_ingestion_pipeline",
    default_args=default_args,
    description="Extracts multi-source telemetry & domain data into DuckDB raw schema",
    schedule_interval="0 2 * * *",  # Runs daily at 02:00 AM UTC
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["foodflow", "ingestion", "raw"],
) as dag:

    t1_extract_iot = PythonOperator(
        task_id="extract_iot_stream",
        python_callable=iot_generator.run,
    )

    t2_extract_usda = PythonOperator(
        task_id="extract_usda_foodkeeper",
        python_callable=usda_extractor.run,
    )

    t3_extract_epa = PythonOperator(
        task_id="extract_epa_baselines",
        python_callable=epa_extractor.run,
    )

    t4_extract_instacart = PythonOperator(
        task_id="extract_instacart_baskets",
        python_callable=instacart_generator.run,
    )

    t5_load_duckdb = PythonOperator(
        task_id="load_duckdb_raw_tables",
        python_callable=run_ingestion.run_all_ingestion,
    )

    # Trigger downstream dbt transformation DAG once ingestion completes
    t6_trigger_dbt = TriggerDagRunOperator(
        task_id="trigger_dbt_transformation_dag",
        trigger_dag_id="foodflow_dbt_transform_pipeline",
    )

    # Define parallel execution dependencies
    [t1_extract_iot, t2_extract_usda, t3_extract_epa, t4_extract_instacart] >> t5_load_duckdb >> t6_trigger_dbt