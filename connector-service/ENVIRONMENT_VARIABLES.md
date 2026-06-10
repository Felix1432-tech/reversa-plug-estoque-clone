# Variáveis de Ambiente

Referência completa das variáveis de ambiente do connector-service.

## Variáveis obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | Connection string do Supabase Postgres (async) | `postgresql+asyncpg://postgres:senha@db.xxx.supabase.co:5432/postgres` |
| `ENCRYPTION_KEY` | Chave Fernet para criptografia de credenciais | `gAAAAABh...` (44 chars, base64) |
| `B2_KEY_ID` | Key ID do Backblaze B2 | `004a1b2c3d4e5f6` |
| `B2_APPLICATION_KEY` | Application Key do Backblaze B2 | `K004xxxxxxxxxxxx` |

## Variáveis opcionais

| Variável | Descrição | Default |
|----------|-----------|---------|
| `B2_BUCKET_NAME` | Nome do bucket no B2 para fotos | `product-photos` |
| `B2_ENDPOINT_URL` | Endpoint S3-compatible do B2 | `https://s3.us-west-004.backblazeb2.com` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON da service account Google (para conector L'Aquila) | `""` (vazio = conector L'Aquila desabilitado) |
| `APP_ENV` | Ambiente da aplicação | `development` |
| `LOG_LEVEL` | Nível de logging | `INFO` |

## Como gerar

### ENCRYPTION_KEY

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Gera uma chave Fernet válida (AES-128-CBC + HMAC-SHA256). Guardar em local seguro. Se a chave for perdida, todas as credenciais de distribuidores armazenadas ficam irrecuperáveis.

### DATABASE_URL

Formato: `postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>`

No Supabase:
1. Dashboard > **Settings** > **Database**
2. Copiar **Connection string** (URI)
3. Substituir `postgresql://` por `postgresql+asyncpg://`
4. Usar **Direct connection** (não pooler) ou configurar pgBouncer para transaction mode

### B2_KEY_ID e B2_APPLICATION_KEY

1. Backblaze B2 > **App Keys** > **Add a New Application Key**
2. Name: `connector-service`
3. Bucket: `product-photos` (ou All)
4. Type: Read and Write
5. Copiar Key ID e Application Key

### GOOGLE_SERVICE_ACCOUNT_JSON

1. Google Cloud Console > **IAM & Admin** > **Service Accounts**
2. Create Service Account: `connector-laquila`
3. **Keys** > **Add Key** > **Create new key** > JSON
4. Copiar conteúdo do JSON como valor da variável (inline, sem quebras de linha)
5. Compartilhar a pasta do Google Drive com o email do service account (Viewer)

## Arquivo .env (desenvolvimento local)

```env
DATABASE_URL=postgresql+asyncpg://postgres:sua_senha@db.xxx.supabase.co:5432/postgres
ENCRYPTION_KEY=gAAAAABh_sua_chave_fernet_aqui
B2_KEY_ID=004a1b2c3d4e5f6
B2_APPLICATION_KEY=K004xxxxxxxxxxxx
B2_BUCKET_NAME=product-photos
B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
APP_ENV=development
LOG_LEVEL=DEBUG
```

## Seguranca

- **Nunca commitar `.env`** no repositório (já está no `.gitignore` via `.env.example`)
- **Nunca logar** variáveis sensíveis — o `CredentialFilter` no `main.py` bloqueia automaticamente
- Em produção, usar o gerenciador de secrets do Coolify/Portainer em vez de arquivo `.env`
- Rotacionar `ENCRYPTION_KEY` exige re-criptografar todas as credenciais armazenadas
