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

Com o diretório de DAGs mapeado corretamente, na tela inicial do Airflow é possível habilitar a DAG com nome *sparksample*.
Uma vez habilitada, será iniciado um *worker* no formato de um Pod no namespace Airflow. Esse worker vai executar o comando `airflow task run ...` para executar a task inicial que vai solicitar o início de um job Spark; essa task vai iniciar um SparkApplication, que é possível de verificar observando o resultado do comando `kubectl get sparkapp -n default`. O SparkApp vai iniciar um Pod também no namespace default, e quando concluído, o SparkKubernetesSensor será finalizado em conjunto.

## Problemas enfrentados

### Recursos

Na configuração do Minikube, foi recomendado utilizar o *driver* do Docker. Porém mesmo alocando muito recurso para o Docker, ele não aguentava o funcionamento, e por várias vezes reiniciava o cluster do Kubernetes por completo. Logo, troquei para utilizar o VBox.

### Connections

Foi um longo caminho para reconhecer que o SparkKubernetesOperator (operator no contexto do Airflow) utilizava de um Connection - conceito desconhecido para mim - que precisava ser configurado via interface do Airflow. Não estava muito bem documentado no operator como deveria ser configurado esse Connection, nem os erros ficavam claros - uma vez que os logs das tasks foi uma das últimas coisas que acabei descobrindo durante a pesquisa. Assim inicialmente configurei a Connection manualmente, verificando que necessitava apenas ter o nome `kubernetes_default`, e ter o checkbox marcado `in cluster config`.
Naturalmente fui pesquisar como poderia automatizar a configuração dessa connection, e foi possível a partir de uma variável como constava na documentação (não tão clara) do [operator](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/connections/kubernetes.html#howto-connection-kubernetes).

### Permissões

O primeiro problema relacionado a permissão, foi ao solicitar uma execução de um SparkApplication via Airflow. Assim foi necessário dar a permissão ao airflow para que possa executar comandos utilizando a API do SparkOperator, como consta no arquivo `airflow/rbac.yaml`.
Outro problema surgiu ao verificar que as SparkApplication's só podem ser executadas em certos *namespaces*. Houve também o trabalho de dar permissão a um ServiceAccount para que execute tais apps no *namespace* default. Confesso que poderia ter estudado melhor a estrutura do Helm Chart do Spark Operator, que é o responsável por essas regras, mas fica para um outro momento.

### Logs

A falta de logs das execuções das tarefas foi o principal agressor nessa pesquisa. Isso se deu principalmente à minha falta de conhecimento do Airflow, mas também por ele não direcionar os logs de execução das tasks para o **stdout**, e sim armazendo-os locamente em disco.
Isso justificou a criação do StorageAccount e PersistentVolume. A criação dos volumes, storageaccount e mounts não foi simples pois exigiu uma configuração não só no Kubernetes diretamente, como no Helm Chart, e **também** no minikube. Sem essa configuração de **uid** e **gid**, os pods não teriam permissão para escrever nos diretórios compartilhados.
