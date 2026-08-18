import os
import logging

logger = logging.getLogger("airflow.task")

def task_failure_slack_alert(context):
    """
    Failure callback function triggered by Airflow whenever a task fails.
    In production, this posts payload blocks to a Slack webhook URL.
    """
    dag_id = context.get("task_instance").dag_id
    task_id = context.get("task_instance").task_id
    execution_date = context.get("execution_date")
    exception = context.get("exception")

    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/MOCK/SLACK/WEBHOOK")

    alert_msg = f"""
    🚨 *FOODFLOW PIPELINE FAILURE ALERT* 🚨
    *DAG:* `{dag_id}`
    *Task:* `{task_id}`
    *Execution Time:* `{execution_date}`
    *Error Exception:* `{exception}`
    *Action Required:* Check DuckDB warehouse lock or source API status.
    """

    logger.error(f"[SLACK ALERT DISPATCHED] -> {alert_msg}")
    print(f"\n[Mock Slack Dispatch to {slack_webhook_url}]:\n{alert_msg}\n")