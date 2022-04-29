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
    'sparksample',
    default_args={'max_active_runs': 1},
    description='submit spark-pi as sparkApplication on kubernetes',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 4, 26),
    catchup=True,
)

sparkApplicationFile = open("/opt/airflow/dags/sparksample.yaml").read()
sparkApplicationFile = sparkApplicationFile.replace("SAMPLE_JOB_NAME", "job-pi-"+datetime.now().strftime("%H-%M-%S"))

t1 = SparkKubernetesOperator(
    task_id='execute',
    kubernetes_conn_id="kubernetes_default",
    namespace="default",
    application_file=sparkApplicationFile,
    do_xcom_push=True,
    dag=dag,
)

t2 = SparkKubernetesSensor(
    task_id='monitor',
    namespace="default",
    application_name="{{ task_instance.xcom_pull(task_ids='execute')['metadata']['name'] }}",
    dag=dag,
    attach_log=True,
)
t1 >> t2

