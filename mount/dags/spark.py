from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

# [START import_module]
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor

# [END import_module]


# [START instantiate_dag]

dag = DAG(
    'spark_pyai',
    default_args={'max_active_runs': 1},
    description='submit spark-pi as sparkApplication on kubernetes',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 4, 23),
    catchup=False,
)

start = KubernetesPodOperator(namespace='airflow',image="python:3.6",
                          cmds=["python","-c"],
                          arguments=["print('hello world')"],
                          labels={"foo": "bar"},
                          name="passing-test",
                          task_id="passing-task",
                          get_logs=True,
                          dag=dag,
                          in_cluster=True
                          )

t1 = SparkKubernetesOperator(
    task_id='execute',
    kubernetes_conn_id="kubernetes_default",
    namespace="default",
    application_file=open("/opt/airflow/dags/sparksample.yaml").read(),
    do_xcom_push=True,
    dag=dag,
)

t2 = SparkKubernetesSensor(
    task_id='monitor',
    namespace="default",
    application_name="{{ task_instance.xcom_pull(task_ids='execute')['metadata']['name'] }}",
    dag=dag,
)
start >> t1 >> t2

