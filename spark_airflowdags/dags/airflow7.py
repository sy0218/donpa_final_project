from airflow.operators.bash_operator import BashOperator
from airflow import DAG
from datetime import datetime, timedelta
import pytz

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 29),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'timezone': 'Asia/seoul',
}

dag = DAG(
    'spark_submit_dag7',
    default_args=default_args,
    schedule_interval='0 * * * *',  # 정각 마다 실행
    catchup=False,  # 과거 작업은 실행하지 않음
)

# coin_union_csv.py 실행
spark_submit_task = BashOperator(
    task_id='airflow_load_csv',
    bash_command='/usr/local/spark/bin/spark-submit --master yarn --deploy-mode client /home/ubuntu/donpa_data_save_csv/donpa_data_save_csv6.py',
    dag=dag,
)

# fullcoin_push_mongo.py 실행
push_mongo_task = BashOperator(
    task_id='airflow_push_mongo',
    bash_command='/usr/local/spark/bin/spark-submit --master yarn --deploy-mode client --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.0 /home/ubuntu/csv_push_mongo/mongo6.py',  # 파이썬 >실>행
    dag=dag,
)

# Task 간 의존성 설정
spark_submit_task >> push_mongo_task
