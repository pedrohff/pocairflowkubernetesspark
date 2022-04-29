from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 4, 12),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'working_sample', default_args=default_args, schedule_interval=timedelta(days=1))

start = DummyOperator(task_id='run_this_first', dag=dag)

passing = KubernetesPodOperator(namespace='airflow',
                          image="python:3.6",
                          cmds=["python","-c"],
                          arguments=["print('hello world')"],
                          labels={"foo": "bar"},
                          name="passing-test",
                          task_id="passing-task",
                          get_logs=True,
                          dag=dag,
                          in_cluster=True
                          )

failing = KubernetesPodOperator(namespace='airflow',
                                    image="python:3.6",
                                    cmds=["python","-c"],
                                    arguments=["print('hello world')"],
                                    labels={"foo": "bar"},
                                    name="failing-test",
                                    task_id="failing-task",
                                    get_logs=True,
                                    dag=dag,
                                    in_cluster=True
                                    )

passing.set_upstream(start)
failing.set_upstream(start)
