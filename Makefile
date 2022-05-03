test:
	echo "${hellovar} world"
	echo "$(PWD)"


dependencies:
	brew install helm
	brew install minikube
	brew install --cask virtualbox
	helm repo add apache-airflow https://airflow.apache.org
	helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
	helm repo update

kubernetes:
	minikube delete
	minikube start --mount-string="$(PWD)/mount:/mnt/airflow" --mount --cpus 6 --memory 14g --driver virtualbox --insecure-registry="ghcr.io,gcr.io" --mount-gid 0 --mount-uid 50000
	helm upgrade --install sparkop spark-operator/spark-operator -n spark-operator -f spark/op-config.yaml --create-namespace --version 1.1.20 --set webhook.enable=true --timeout 10m0s
	kubectl apply -f airflow/logs-pv.yaml
	helm upgrade --install airflow apache-airflow/airflow -n airflow -f airflow/config.yaml --create-namespace --version 1.5.0 --timeout 10m0s
	kubectl ns airflow
	kubectl apply -f airflow/rbac.yaml



helm-show-chart:
	helm show chart apache-airflow/airflow

helm-airflow-versions:
	helm search repo apache-airflow/airflow -l
