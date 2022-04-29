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
    'qqqq',
    default_args={'max_active_runs': 1},
    description='submit spark-pi as sparkApplication on kubernetes',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 4, 26),
    catchup=True,
)

from typing import TYPE_CHECKING, Optional, Sequence

from airflow.models import BaseOperator
from airflow.providers.cncf.kubernetes.hooks.kubernetes import KubernetesHook

if TYPE_CHECKING:
    from airflow.utils.context import Context


class SparkPedroOperator(BaseOperator):
    def __init__(
        self,
        *,
        application_file: str,
        namespace: Optional[str] = None,
        kubernetes_conn_id: str = 'kubernetes_default',
        api_group: str = 'sparkoperator.k8s.io',
        api_version: str = 'v1beta2',
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.application_file = application_file
        self.namespace = namespace
        self.kubernetes_conn_id = kubernetes_conn_id
        self.api_group = api_group
        self.api_version = api_version

    def execute(self, context: 'Context'):
        print("opa")
        self.log.info("Creating sparkApplication")
        print("eae")
        hook = KubernetesHook(conn_id=self.kubernetes_conn_id)
        print("hmm")
        response = hook.create_custom_object(
            group=self.api_group,
            version=self.api_version,
            plural="sparkapplications",
            body=self.application_file,
            namespace=self.namespace,
        )
        print("oxe")
        return response


sparkApplicationFile = open("/opt/airflow/dags/sparksample.yaml").read()
sparkApplicationFile = sparkApplicationFile.replace("SAMPLE_JOB_NAME", "job-pi-"+datetime.now().strftime("%H-%M-%S"))

t1 = SparkPedroOperator(
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

