# Onboarding: Conectores de Distribuidores

> Identificador: `001-conectores-distribuidores`
> Data: `2026-06-10`

## Pré-requisitos

- Docker instalado na máquina local (para dev) ou acesso à VPS Hetzner com Portainer
- Conta Supabase com projeto criado
- Conta Backblaze B2 com bucket `product-photos` criado
- Credenciais de pelo menos 1 distribuidor (DPK recomendado para primeiro teste)
- (Opcional) Service account Google para conector L'Aquila

## Passo a passo — Ambiente local

### 1. Clonar e configurar

```bash
git clone <repo-url>
cd connector-service
cp .env.example .env
```

Preencher `.env`:

```env
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/<db>
ENCRYPTION_KEY=<gerar com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
B2_KEY_ID=<backblaze key id>
B2_APPLICATION_KEY=<backblaze app key>
B2_BUCKET_NAME=product-photos
B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
GOOGLE_SERVICE_ACCOUNT_JSON=<path ou JSON inline>
```

### 2. Subir com Docker

```bash
docker compose up --build
```

O serviço sobe em `http://localhost:8000`. Documentação OpenAPI em `/docs`.

### 3. Executar migrations

```bash
docker compose exec app alembic upgrade head
```

### 4. Configurar primeiro distribuidor

```bash
# Via API (ou via frontend quando disponível)
curl -X POST http://localhost:8000/api/v1/distributors \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt>" \
  -d '{
    "distributor_type": "dpk",
    "credentials": {
      "login": "seu_login",
      "password": "sua_senha"
    }
  }'
```

### 5. Testar conexão

```bash
curl -X POST http://localhost:8000/api/v1/distributors/<id>/test \
  -H "Authorization: Bearer <jwt>"

# Resposta esperada:
# {"status": "success", "message": "Login bem-sucedido no DPK"}
```

### 6. Executar extração

```bash
curl -X POST http://localhost:8000/api/v1/distributors/<id>/run \
  -H "Authorization: Bearer <jwt>"

# Resposta: {"log_id": "<uuid>", "status": "running"}
```

### 7. Verificar resultado

```bash
# Consultar log da execução
curl http://localhost:8000/api/v1/logs/<log_id> \
  -H "Authorization: Bearer <jwt>"

# Resposta esperada:
# {
#   "status": "success",
#   "products_found": 150,
#   "products_created": 150,
#   "products_updated": 0,
#   "errors_count": 0,
#   "started_at": "...",
#   "finished_at": "..."
# }

# Listar produtos extraídos
curl "http://localhost:8000/api/v1/products?distributor_type=dpk&limit=10" \
  -H "Authorization: Bearer <jwt>"
```

### 8. Verificar fotos no B2

Acessar o Backblaze B2 console e confirmar que as fotos foram uploadadas no bucket `product-photos` com path: `<user_id>/<distributor_type>/<sku>/<filename>`.

## Passo a passo — Deploy produção (Coolify)

### 1. Criar app no Coolify

- Tipo: Docker
- Source: repositório Git
- Branch: `main`
- Dockerfile path: `./Dockerfile`

### 2. Configurar variáveis de ambiente no Coolify

Mesmas do `.env` acima, com valores de produção.

### 3. Configurar domínio no Cloudflare

- Criar registro A: `api-connectors.<dominio>` → IP da VPS
- Proxy: ativado (orange cloud)
- SSL: Full (strict)

### 4. Configurar domínio no Coolify

- Domain: `api-connectors.<dominio>`
- HTTPS: automático (via Cloudflare)

### 5. Deploy

Push para `main` → Coolify detecta, builda e deploya automaticamente.

### 6. Verificar

```bash
curl https://api-connectors.<dominio>/health
# {"status": "ok", "version": "1.0.0"}
```

## Checklist de validação

- [ ] Container sobe sem erros
- [ ] `/health` retorna 200
- [ ] `/docs` abre documentação OpenAPI
- [ ] Criar distribuidor DPK via API
- [ ] "Testar conexão" retorna sucesso
- [ ] Executar extração e ver ≥1 produto no banco
- [ ] Foto de produto acessível via URL do B2
- [ ] Log de execução consultável via API
- [ ] RLS funciona: usuário A não vê dados do usuário B

## Histórico

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-10 | Versão inicial | reversa-plan |
