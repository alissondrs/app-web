# App-Web com K3d

# Dependencias
- [Docker](https://docs.docker.com/engine/install/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [k3d](https://k3d.io)

# Instalar o k3d
```bash
curl -s https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash
```

## Criar o cluster k3d
```bash
k3d cluster create app-web --config cluster/cluster.yaml
```

## Acessar o cluster
```bash
k3d kubeconfig get app-web
```
## Deploy da aplicação
```bash
kubectl apply -f deployment/app-web.yaml
kubectl apply -f statefulset/mysql/initdb.yaml
kubectl apply -f statefulset/mysql/mysql.yaml
```
## fazer port foward para o service da app-web
```bash
kubectl port-forward svc/app-web 8080:8080
```
## Testar a aplicação
```bash
curl http://localhost:8080/health
```

## Excluir o cluster
```bash
k3d cluster delete app-web
```

## Referências
- [k3d](https://k3d.io)

