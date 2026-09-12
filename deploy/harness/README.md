# Integração Harness CD

Este diretório descreve o contrato do pipeline; connectors e credenciais devem
ser criados na conta Harness, nunca versionados neste repositório.

## Connectors

1. **GitHub**: acesso somente leitura ao repositório `alissondrs/app-web`.
2. **Docker Hub**: leitura da imagem `alissondrs/app-web`.
3. **Kubernetes**: acesso somente ao namespace `app-web` no cluster lab.

## Pipeline recomendado

1. Receber `IMAGE_TAG` por webhook ou execução manual após merge em `develop`.
2. Validar que a imagem `develop-sha-*` existe no Docker Hub.
3. Aplicar os manifests em `deploy/kubernetes` no ambiente `lab`.
4. Aguardar `Deployment/app-web` ficar disponível.
5. Executar smoke test em `/health`.
6. Promover somente após o PR `develop` → `main` ser aprovado e mesclado.
7. No pipeline de produção, consumir apenas uma imagem `prod-sha-*`.
8. Em falha, executar `kubectl rollout undo deployment/app-web`.

O secret `APP_PASSWORD` e os secrets do MySQL devem ser criados pelo Harness
usando secret references ou previamente no namespace. Não use os antigos
manifests `k8s/kubernetes/*/secret.yaml`, que continham credenciais em texto
puro.
