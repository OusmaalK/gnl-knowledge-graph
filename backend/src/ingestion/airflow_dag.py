from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'gnl-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alertes@gnl-company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'gnl_ingestion_daily',
    default_args=default_args,
    description='Importation quotidienne des données GNL',
    schedule_interval='@daily',
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=['gnl', 'ingestion']
)

def import_fournisseurs():
    from src.ingestion.import_csv import Neo4jIngestion
    ingestion = Neo4jIngestion()
    ingestion.import_all()

def import_incidents():
    from src.ingestion.import_json import JSONIngestion
    ingestion = JSONIngestion()
    ingestion.import_all()

task_fournisseurs = PythonOperator(
    task_id='import_fournisseurs',
    python_callable=import_fournisseurs,
    dag=dag
)

task_incidents = PythonOperator(
    task_id='import_incidents',
    python_callable=import_incidents,
    dag=dag
)

task_fournisseurs >> task_incidents