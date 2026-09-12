# Deploy Kubernetes no ambiente lab

Os manifests desta pasta não contêm credenciais. Antes do primeiro deploy,
crie os secrets no namespace do ambiente:

```bash
kubectl create namespace app-web --dry-run=client -o yaml | kubectl apply -f -
kubectl -n app-web create secret generic app-web-secrets \
  --from-literal=APP_PASSWORD="$APP_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n app-web create secret generic mysql-secrets \
  --from-literal=MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
  --from-literal=MYSQL_PASSWORD="$APP_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
```

O Harness deve substituir a imagem `alissondrs/app-web:sha-REPLACE_ME` pela tag
imutável publicada pelo workflow `build-publish.yml` antes de aplicar os
manifests.
