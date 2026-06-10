# Connector Service

Serviço de extração de catálogos de distribuidores brasileiros via RPA (Playwright) e Google Drive API. Parte central da plataforma de marketplace cross-docking.

## O que faz

- Extrai SKU, fotos, descrição, preço, estoque, peso, medidas e dados fiscais de 7 distribuidores
- Armazena fotos no Backblaze B2 (S3-compatible)
- Persiste dados normalizados no Supabase (Postgres)
- Expõe API REST para gerenciar distribuidores, executar extrações e consultar resultados
- Agenda execuções periódicas via APScheduler
- Suporta importação manual via CSV/Excel como fallback

## Distribuidores suportados

| Distribuidor | Tipo | Dados extraídos |
|-------------|------|-----------------|
| DPK | RPA/Playwright | SKU, fotos, descrição, preço, estoque, peso, medidas |
| Furacão | RPA/Playwright | SKU, fotos, descrição, preço, estoque, peso, medidas |
| RUFATO | RPA/Playwright | Catálogo completo |
| ISAPA | RPA/Playwright | Catálogo completo |
| Pellegrino | RPA/Playwright | Fotos, descrição (sem estoque) |
| L'Aquila | Google Drive API | Fotos, preços, descrição, dados fiscais |
| Rolemarmaster | RPA/Playwright | Catálogo (sem estoque) |

## Stack

- **Python 3.12+** com **FastAPI** (async)
- **Playwright** (Chromium headless) para RPA
- **SQLAlchemy 2.0** + **asyncpg** para banco de dados
- **Supabase** (Postgres gerenciado) com Row Level Security
- **Backblaze B2** para armazenamento de fotos
- **Cloudflare** para DNS, SSL e proteção
- **Docker** para containerização e deploy

## Quick Start (desenvolvimento local)

```bash
# 1. Clonar
git clone https://github.com/Felix1432-tech/reversa-plug-estoque-clone.git
cd reversa-plug-estoque-clone/connector-service

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais reais

# 3. Subir com Docker
docker compose up --build

# 4. Executar migrations
docker compose exec app alembic upgrade head

# 5. Aplicar RLS no Supabase (executar no SQL Editor do Supabase)
# Ver: scripts/rls_policies.sql

# 6. Acessar
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

## Endpoints principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/distributors` | Cadastrar distribuidor |
| `GET` | `/api/v1/distributors` | Listar distribuidores |
| `PUT` | `/api/v1/distributors/{id}` | Atualizar credenciais |
| `DELETE` | `/api/v1/distributors/{id}` | Remover distribuidor |
| `POST` | `/api/v1/distributors/{id}/test` | Testar conexão |
| `POST` | `/api/v1/distributors/{id}/run` | Executar extração |
| `GET` | `/api/v1/logs` | Listar logs de execução |
| `GET` | `/api/v1/logs/{id}` | Detalhe de um log |
| `GET` | `/api/v1/products` | Listar produtos extraídos |
| `POST` | `/api/v1/import/csv` | Importar via CSV/Excel |
| `GET` | `/health` | Health check |

## Documentação complementar

- [ARCHITECTURE.md](./ARCHITECTURE.md) — Diagrama e componentes
- [DEPLOY_COOLIFY.md](./DEPLOY_COOLIFY.md) — Deploy via Coolify (Hostinger)
- [DEPLOY_PORTAINER.md](./DEPLOY_PORTAINER.md) — Deploy via Portainer (Hetzner VPS)
- [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) — Variáveis de ambiente
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) — Guia de testes
- [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) — Checklist de produção

## Licença

Projeto privado.
