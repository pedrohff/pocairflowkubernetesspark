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

As dependências podem ser instaladas utilizando o Makefile (make dependencies).
Caso não tenha uma máquina com MacOS, será necessário a instalação das seguintes ferramentas:
- Helm
- Minikube

Além de adicionar os repositórios dos projetos que vamos precisar:
```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm repo update
```
## Instalação

Com as ferramentas instaladas na máquina, e com este repositório clonado, apenas executando `make kubernetes` serão configurados tudo que precisaremos, já da forma mais integrada possível, mas com algumas observações.

### Minikube

Nosso cluster do Kubernetes é instalado com algumas configurações específicas.
Iniciando pela parte de mount, ligamos o diretório `mount` deste repositório ao diretório da VM `/mnt/airflow/`, para que possamos distribuir entre os pods os diretórios de logs e de dags.
Configuramos a VM para utilizar 6 CPUS e 14GB de RAM. Esses valores são altos, então caso necessário, fique a vontade para diminuí-los.
Com a flag `inscure-registry`, adicionamos alguns repositórios de imagem docker que são utilizados pelo Spark.
Por fim são configurados o `gid` e o `uid`, que são os identificadores de grupo e usuário que serão atribuídos ao **mount**.

### Spark

O operador do Spark sofreu poucas configurações, seguindo em grande parte o padrão.

### Airflow

Antes de aplicar o Helm Chart do Airflow, criamos um StorageAccount e um PersistentVolume para que fiquem associados ao diretório **mount**. Em seguida instalamos o Helm Chart com as configurações que foram documentadas no próprio arquivo `airflow/config.yaml` e aplicamos mais uma regra de RBAC para que o Airflow passe a ter acesso à API do Spark no Kubernetes.

## Funcionamento de uma DAG ligando os três componentes



TODO descrever como habilitar uma task e como a sua execução ocorre nos namespaces.

## Problemas enfrentados

### Recursos

TODO descrever uso do driver vbox

### Connections

### Permissões

TODO descrever necessidade do RBAC

### Logs


