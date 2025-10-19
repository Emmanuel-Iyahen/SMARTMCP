# airflow/dags/financial_data_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import asyncio
from etl.financial_loader import FinancialDataLoader

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}



def run_etl():
    """Run the ETL class inside Airflow task"""
    loader = FinancialDataLoader()
    df = asyncio.run(loader.load_financial_data())
    if df is not None and not df.empty:
        print(f"✅ Stored {len(df)} rows in Snowflake")
    else:
        print("⚠️ No data fetched from API")

with DAG(
    "financial_data_etl",
    default_args=default_args,
    description="Daily ETL for UK stocks → Snowflake",
    schedule_interval="0 18 * * *",  # every day at 18:00
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["finance", "snowflake", "etl"],
) as dag:

    etl_task = PythonOperator(
        task_id="fetch_process_store",
        python_callable=run_etl
    )
