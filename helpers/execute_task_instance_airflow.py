import datetime
import pendulum
from airflow.models import DAG
from airflow.models.taskinstance import TaskInstance
from sqlalchemy.orm.exc import NoResultFound
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.utils.state import DagRunState
from airflow.utils.types import DagRunType

DATA_INTERVAL_START = pendulum.datetime(2022, 4, 13, tz="UTC")
DATA_INTERVAL_END = DATA_INTERVAL_START + datetime.timedelta(days=1)

TEST_DAG_ID = "sparkoperatoqfqwefrtest"
TEST_TASK_ID = "execute"
dag = DAG(
    dag_id=TEST_DAG_ID,
    schedule_interval="@daily",
    default_args={"start_date": DATA_INTERVAL_START, 'owner':'gabriel.pereira@picpay.com'},)

op1 =  SparkKubernetesOperator(
    task_id='execute',
    kubernetes_conn_id="kubernetes_default",
    namespace="default",
    application_file=open("/opt/airflow/dags/sparksample.yaml").read(),
    do_xcom_push=True,
    dag=dag,
)


dagrun = dag.create_dagrun(
        state=DagRunState.RUNNING,
        execution_date=DATA_INTERVAL_START,
        data_interval=(DATA_INTERVAL_START, DATA_INTERVAL_END),
        start_date=DATA_INTERVAL_END,
        run_type=DagRunType.MANUAL,
    )
ti = dagrun.get_task_instance(task_id=TEST_TASK_ID)
ti.task = dag.get_task(task_id=TEST_TASK_ID)
ti.run(ignore_ti_state=True)

# print('Running task...')
# ti.run(ignore_ti_state=True)
