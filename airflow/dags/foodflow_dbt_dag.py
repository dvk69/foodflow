import os
import subprocess
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

try:
    from alerts import task_failure_slack_alert
except ImportError:
    from plugins.alerts import task_failure_slack_alert

DBT_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dbt_foodflow"))

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=15),
    "on_failure_callback": task_failure_slack_alert,
}

def execute_dbt_run():
    """Runs dbt models via CLI subprocess"""
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", "."],
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"dbt run failed:\n{result.stderr}")

def execute_dbt_test():
    """Runs dbt quality assertions via CLI subprocess"""
    result = subprocess.run(
        ["dbt", "test", "--profiles-dir", "."],
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"dbt test quality failure:\n{result.stderr}")

with DAG(
    dag_id="foodflow_dbt_transform_pipeline",
    default_args=default_args,
    description="Transforms raw DuckDB tables into SLA-backed Golden Marts",
    schedule_interval=None,  # Triggered automatically by ingestion DAG
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["foodflow", "dbt", "golden_marts"],
) as dag:

    t1_dbt_run = PythonOperator(
        task_id="dbt_run_models",
        python_callable=execute_dbt_run,
    )

    t2_dbt_test = PythonOperator(
        task_id="dbt_test_quality_assertions",
        python_callable=execute_dbt_test,
    )

    t1_dbt_run >> t2_dbt_test