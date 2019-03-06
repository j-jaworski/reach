"""
DAG to run the policy tool on every organisation.
"""

import datetime

from airflow import DAG
import airflow.utils.dates

from scraper.airflow.tasks.run_spiders_operator import RunSpiderOperator


ORGANISATIONS = [
    'who_iris',
    'nice',
    'gov_uk',
    'msf',
    'unicef',
    'parliament',
]

args = {
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=5),
}

dag = DAG(
    dag_id='policytool_dag',
    default_args=args,
    schedule_interval='0 0 * * 0'
)


for organisation in ORGANISATIONS:
    run_spider = RunSpiderOperator(
        task_id='run_{spider}_spider'.format(spider=organisation),
        organisation=organisation,
        dag=dag,
    )