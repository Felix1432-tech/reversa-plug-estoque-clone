# Deploy via Coolify (Hostinger)

Guia para deploy do connector-service usando Coolify na hospedagem Hostinger.

## Pré-requisitos

- Coolify instalado e acessível
- Repositório Git conectado ao Coolify
- Supabase configurado com migrations executadas
- Bucket Backblaze B2 criado
- Subdomínio Cloudflare configurado

## Passo 1 — Criar aplicação no Coolify

1. Acessar painel Coolify
2. **New Resource** > **Application**
3. Configurar source:
   - **Source:** Git Repository
   - **Repository:** `https://github.com/Felix1432-tech/reversa-plug-estoque-clone`
   - **Branch:** `main`
   - **Build Pack:** Docker
   - **Dockerfile Location:** `connector-service/Dockerfile`
   - **Docker Compose Location:** (deixar vazio — usar Dockerfile direto)
   - **Base Directory:** `connector-service`

## Passo 2 — Configurar variáveis de ambiente

No painel da aplicação, aba **Environment Variables**, adicionar:

```
DATABASE_URL=postgresql+asyncpg://postgres:<password>@<supabase-host>:5432/postgres
ENCRYPTION_KEY=<gerar com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
B2_KEY_ID=<backblaze key id>
B2_APPLICATION_KEY=<backblaze app key>
B2_BUCKET_NAME=product-photos
B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
GOOGLE_SERVICE_ACCOUNT_JSON=<json da service account>
APP_ENV=production
LOG_LEVEL=INFO
```

Marcar todas como **Build & Runtime**.

## Passo 3 — Configurar domínio

1. No Coolify, aba **Settings** da aplicação:
   - **Domain:** `api-connectors.<seu-dominio>.com`
   - **HTTPS:** Habilitado (Coolify gera certificado ou usa Cloudflare)

2. No Cloudflare:
   - Criar registro **A**: `api-connectors` → IP da VPS Hostinger
   - **Proxy status:** Proxied (orange cloud)
   - **SSL/TLS:** Full (strict)

## Passo 4 — Configurar health check

No Coolify, aba **Health Check**:
- **Path:** `/health`
- **Port:** `8000`
- **Interval:** `30s`

## Passo 5 — Deploy

1. Clicar **Deploy** no Coolify
2. Acompanhar build logs
3. Aguardar status "Running"

## Passo 6 — Executar migrations

Após o container subir, executar via terminal do Coolify (ou SSH):

```bash
# Via Coolify terminal
docker exec <container_id> alembic upgrade head
```

Ou adicionar ao Dockerfile como entrypoint alternativo:

```dockerfile
# Adicionar antes do CMD se quiser auto-migrate
RUN alembic upgrade head
```

## Passo 7 — Aplicar RLS no Supabase

Acessar **SQL Editor** no Supabase e executar o conteúdo de `scripts/rls_policies.sql`.

## Passo 8 — Verificar

```bash
# Health check
curl https://api-connectors.<dominio>/health
# Esperado: {"status":"ok","version":"1.0.0"}

# OpenAPI docs
# Abrir no browser: https://api-connectors.<dominio>/docs
```

## Auto-deploy

Coolify suporta deploy automático via webhook. Para ativar:

1. Aba **Settings** > **Auto Deploy** > Enabled
2. Copiar webhook URL
3. No GitHub, **Settings** > **Webhooks** > adicionar o webhook
4. Trigger: `push` events na branch `main`

Cada push para `main` dispara rebuild automático.

## Troubleshooting

| Problema | Causa provável | Solução |
|----------|---------------|---------|
| Build falha no Playwright | Imagem base não encontrada | Verificar tag da imagem no Dockerfile |
| Container reinicia em loop | `DATABASE_URL` inválido | Verificar variável de ambiente |
| 502 Bad Gateway | App não subiu na porta 8000 | Verificar logs do container |
| SSL error | Cloudflare SSL mode errado | Mudar para Full (strict) |
| Migration falha | Extensão pg_trgm indisponível | Ativar no Supabase: Dashboard > Database > Extensions |
