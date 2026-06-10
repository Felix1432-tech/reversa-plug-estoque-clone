# Deploy via Portainer (Hetzner VPS)

Guia para deploy do connector-service usando Portainer nas VPS Hetzner.

## Pré-requisitos

- Portainer instalado e acessível na VPS
- Docker Engine rodando na VPS
- Supabase configurado com migrations executadas
- Bucket Backblaze B2 criado
- Subdomínio Cloudflare configurado

## Opção A — Deploy via Stack (docker-compose)

### Passo 1 — Criar stack no Portainer

1. Acessar Portainer > **Stacks** > **Add stack**
2. **Name:** `connector-service`
3. **Build method:** Web editor
4. Colar o conteúdo:

```yaml
services:
  app:
    image: ghcr.io/felix1432-tech/connector-service:latest
    # OU build local:
    # build:
    #   context: .
    #   dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:<password>@<supabase-host>:5432/postgres
      - ENCRYPTION_KEY=<sua-chave-fernet>
      - B2_KEY_ID=<backblaze-key-id>
      - B2_APPLICATION_KEY=<backblaze-app-key>
      - B2_BUCKET_NAME=product-photos
      - B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
      - GOOGLE_SERVICE_ACCOUNT_JSON=<json-service-account>
      - APP_ENV=production
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
```

4. Clicar **Deploy the stack**

### Passo 2 — Verificar

No Portainer, ir em **Containers** e verificar que o container está `running` e healthy.

## Opção B — Deploy via build manual na VPS

### Passo 1 — Clonar na VPS

```bash
ssh root@<ip-vps>
cd /opt
git clone https://github.com/Felix1432-tech/reversa-plug-estoque-clone.git
cd reversa-plug-estoque-clone/connector-service
```

### Passo 2 — Configurar .env

```bash
cp .env.example .env
nano .env
# Preencher com valores de produção
```

### Passo 3 — Build e subir

```bash
docker compose up -d --build
```

### Passo 4 — Migrations

```bash
docker compose exec app alembic upgrade head
```

### Passo 5 — Verificar

```bash
docker compose ps
# STATUS: Up (healthy)

curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0"}
```

## Configurar Cloudflare

1. No Cloudflare DNS, criar registro:
   - **Type:** A
   - **Name:** `api-connectors`
   - **Content:** IP da VPS Hetzner
   - **Proxy status:** Proxied

2. SSL/TLS > **Full (strict)**

3. (Opcional) Security > WAF > criar regra de rate limiting:
   - Path: `/api/v1/distributors/*/run`
   - Rate: 10 requests/minuto
   - Action: Block

## Atualização

```bash
ssh root@<ip-vps>
cd /opt/reversa-plug-estoque-clone
git pull origin main
cd connector-service
docker compose up -d --build
docker compose exec app alembic upgrade head
```

Ou via Portainer: **Stacks** > `connector-service` > **Pull and redeploy**.

## Monitoramento via Portainer

- **Container logs:** Stacks > connector-service > container > Logs
- **Stats:** CPU, memória, rede em tempo real
- **Health:** Badge verde/vermelho no painel de containers
- **Restart policy:** `unless-stopped` garante que o container reinicia após crash

## Troubleshooting

| Problema | Causa provável | Solução |
|----------|---------------|---------|
| Container não sobe | Porta 8000 já em uso | `docker ps` para ver quem usa, ou mudar porta no compose |
| OOM Kill | Playwright consome muita RAM | Aumentar RAM da VPS ou limitar conectores simultâneos |
| Build lento | Imagem Playwright é grande (~1.5GB) | Usar cache de layers: `docker compose build --cache-from` |
| DNS não resolve | Cloudflare não propagou | Aguardar 5min ou verificar registro A |
