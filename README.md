# PoC Airflow + Kubernetes + SparkOperator

Essa PoC teve como objetivo os seguintes pontos:
- Configurar um cluster do Kubernetes local;
- Configurar o Airflow, utilizando o helm;
- Configurar o Spark Operator no K8S utilizando o helm;
- Ter um ambiente em que os diretórios fossem compartilhados com a máquina local:
  - O diretório de DAGs do Airflow fica localmente, mas compartilhado com a VM do Kubernetes e com os pods do Airflow;
  - O mesmo para o diretório de logs do Airflow, visto que os logs de execução das tarefas que vão para o stdout dos pods não são claros, e acabam ocultando parte principal das tasks. Aqui há também a preocupação de que os logs das tasks sobressaiam o ciclo de vida dos pods, assim podemos ver o que ocorreu durante o ciclo de vida da task;
- Executar DAGs que contenham tasks utilizando o SparkKubernetesOperator+SparkKubernetesSensor.


## Dependências

## Funcionamento de uma DAG ligando os três componentes

TODO descrever como habilitar uma task e como a sua execução ocorre nos namespaces.

## Problemas enfrentados

### Recursos

TODO descrever uso do driver vbox

### Connections

### Permissões

TODO descrever necessidade do RBAC

### Logs


