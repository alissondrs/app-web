# App Web no Kubernetes

Manifestos para rodar a versao `1.0.4` da aplicacao em um cluster k3d/k3s.

## Dependencias

- [Docker](https://docs.docker.com/engine/install/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [k3d](https://k3d.io)

## Estrutura

```text
kubernetes/
├── app/
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── secret.yaml
│   └── service.yaml
├── cluster/
│   └── cluster.yaml
├── mysql/
│   ├── configmap-initdb.yaml
│   ├── secret.yaml
│   ├── service-headless.yaml
│   ├── service.yaml
│   └── statefulset.yaml
└── kustomization.yaml
```

## O que mudou

- app e mysql agora estao separados em pastas proprias
- a aplicacao usa a imagem `alissondrs/app-web:1.0.4`
- configuracoes nao sensiveis foram movidas para `ConfigMap`
- senhas foram movidas para `Secret`
- o MySQL usa service headless para o `StatefulSet` e um service normal para acesso da app
- foram adicionados `startupProbe`, `readinessProbe`, `livenessProbe` e `resources`

## Criar o cluster k3d

```bash
k3d cluster create --config cluster/cluster.yaml
```

## Aplicar os manifests

Na pasta `k8s/kubernetes`:

```bash
kubectl apply -k .
```

## Verificar os recursos

```bash
kubectl get pods
kubectl get svc
kubectl get configmap
kubectl get secret
```

## Rodar a imagem local 1.0.4 no cluster

Se a imagem `alissondrs/app-web:1.0.4` ainda nao estiver publicada no Docker Hub, voce pode usar a imagem local do branch atual:

```bash
cd /Users/alisson/labs-env/projects/app-web
docker build -t alissondrs/app-web:1.0.4 .
k3d image import alissondrs/app-web:1.0.4 -c k8s-cluster
```

## Acessar a aplicacao

```bash
kubectl port-forward svc/app-web 8080:8080
```

Em outro terminal:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/users/
```

## Atualizar a imagem da app

Para trocar a versao da app, ajuste o campo `image` em `app/deployment.yaml`.

## Observacoes

- os arquivos `secret.yaml` atuais sao adequados para estudo e ambiente local; para ambientes reais, prefira um gerenciador de segredos
- o MySQL foi fixado em `mysql:5.7.44` para evitar mudancas inesperadas por `latest`

## Excluir o cluster

```bash
k3d cluster delete k8s-cluster
```

