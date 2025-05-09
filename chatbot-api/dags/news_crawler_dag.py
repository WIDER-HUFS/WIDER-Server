from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os
import pymysql
from dotenv import load_dotenv
from pendulum import timezone

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # chatbot-api directory
sys.path.append(project_root)
print(f"Project root: {project_root}")

load_dotenv()


# Debug: Print environment variables (remove in production)
print(f"MySQL Host: {os.getenv('MYSQL_HOST')}")
print(f"MySQL User: {os.getenv('MYSQL_USER')}")
print(f"MySQL Database: {os.getenv('MYSQL_DATABASE')}")

from crawler import main as crawler_main

local_tz = timezone("Asia/Seoul")
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10, tzinfo=local_tz),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def set_daily_topic(**context):
    try:
        # Get the topic from crawler
        topic_json = crawler_main()
        print(topic_json)  # 디버깅용
        
        # Connect to MySQL using PyMySQL
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        try:
            with conn.cursor() as cursor:
                # Insert or update the daily topic
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute(
                    """
                    INSERT INTO daily_topic (topic_date, topic, topic_prompt)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    topic = VALUES(topic),
                    topic_prompt = VALUES(topic_prompt)
                    """,
                    (today, topic_json["topic"], topic_json["topic_prompt"])
                )
                conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"Error in set_daily_topic: {str(e)}")
        raise

with DAG(
    'news_crawler_dag',
    default_args=default_args,
    description='Daily news crawling and topic extraction',
    schedule='0 0 * * *',  # Run daily at midnight
    catchup=False
) as dag:

    crawl_and_set_topic = PythonOperator(
        task_id='crawl_and_set_topic',
        python_callable=set_daily_topic
    ) 