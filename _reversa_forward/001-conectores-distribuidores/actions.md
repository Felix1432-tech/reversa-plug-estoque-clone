# Actions: Conectores de Distribuidores

> Identificador: `001-conectores-distribuidores`
> Data: `2026-06-10`
> Roadmap: `_reversa_forward/001-conectores-distribuidores/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 35 |
| Paralelizáveis (`[//]`) | 16 |
| Maior cadeia de dependência | 7 (T001 → T004 → T008 → T014 → T015 → T030 → T033) |

## Fase 1 — Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar scaffold do projeto: `pyproject.toml` com todas as dependências (fastapi, playwright, sqlalchemy, boto3, etc.), estrutura de diretórios (`app/`, `tests/`, `alembic/`, `scripts/`) e arquivos `__init__.py` | - | - | `connector-service/pyproject.toml` | 🟢 | `[ ]` |
| T002 | Criar `Dockerfile` multi-stage baseado em `mcr.microsoft.com/playwright/python` + `docker-compose.yml` com serviço `app` e variáveis de ambiente | - | `[//]` | `connector-service/Dockerfile` | 🟢 | `[ ]` |
| T003 | Criar módulo `app/config.py` com `Settings` via pydantic-settings: DATABASE_URL, ENCRYPTION_KEY, B2_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME, B2_ENDPOINT_URL, GOOGLE_SERVICE_ACCOUNT_JSON | T001 | - | `app/config.py` | 🟢 | `[ ]` |
| T004 | Criar módulo `app/db/session.py` com AsyncSession factory (SQLAlchemy 2.0 + asyncpg) e `app/db/base.py` com Base declarativa | T003 | - | `app/db/session.py` | 🟢 | `[ ]` |
| T005 | Configurar Alembic para async: `alembic.ini` + `alembic/env.py` com suporte a asyncpg | T004 | - | `alembic/env.py` | 🟢 | `[ ]` |
| T006 | Criar migration inicial: tabelas `distributor_configs`, `products`, `connector_logs` com índices e constraints conforme `data-delta.md` | T005 | - | `alembic/versions/001_initial.py` | 🟢 | `[ ]` |
| T007 | Criar script SQL para RLS policies no Supabase: policies para as 3 tabelas filtrando por `auth.uid() = user_id` | T006 | - | `scripts/rls_policies.sql` | 🟢 | `[ ]` |

## Fase 2 — Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Criar `tests/conftest.py` com fixtures: async test client (httpx), banco de teste (SQLAlchemy async), factory de `DistributorConfig` e `Product` | T004 | - | `tests/conftest.py` | 🟢 | `[ ]` |
| T009 | Criar testes para `BaseConnector`: verificar que subclasse sem implementação levanta `TypeError`, verificar assinatura dos métodos | T008, T014 | `[//]` | `tests/test_connectors/test_base.py` | 🟢 | `[ ]` |
| T010 | Criar testes para `EncryptionService`: encrypt → decrypt roundtrip, chave inválida levanta erro, dados criptografados são diferentes do original | T008, T016 | `[//]` | `tests/test_services/test_encryption.py` | 🟢 | `[ ]` |
| T011 | Criar testes para `ProductRepository.upsert_products`: insert de novos, update de existentes, soft delete de ausentes, UNIQUE constraint respeitada | T008, T017 | `[//]` | `tests/test_repositories/test_product_repo.py` | 🟢 | `[ ]` |

## Fase 3 — Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | Criar modelos SQLAlchemy: `DistributorConfig` em `app/models/distributor.py` | T004 | `[//]` | `app/models/distributor.py` | 🟢 | `[ ]` |
| T013 | Criar modelos SQLAlchemy: `Product` em `app/models/product.py` e `ConnectorLog` em `app/models/connector_log.py` | T004 | `[//]` | `app/models/product.py` | 🟢 | `[ ]` |
| T014 | Criar `app/connectors/base.py`: classe abstrata `BaseConnector` com métodos `authenticate()`, `fetch_catalog()`, `fetch_stock()`, `health_check()` e decorator `@retry` com backoff exponencial | T001 | - | `app/connectors/base.py` | 🟢 | `[ ]` |
| T015 | Criar `app/connectors/registry.py`: dict `CONNECTOR_REGISTRY` mapeando `distributor_type` → classe concreta, função `get_connector(type) → BaseConnector` | T014 | - | `app/connectors/registry.py` | 🟢 | `[ ]` |
| T016 | Criar `app/services/encryption.py`: `EncryptionService` com `encrypt(data: dict) → bytes` e `decrypt(token: bytes) → dict` usando Fernet, chave da env var | T003 | - | `app/services/encryption.py` | 🟡 | `[ ]` |
| T017 | Criar `app/repositories/product_repo.py`: `ProductRepository` com `upsert_products(config_id, products)` (INSERT ON CONFLICT UPDATE em batch) e `mark_absent_unavailable(config_id, found_skus)` | T012, T013 | - | `app/repositories/product_repo.py` | 🟢 | `[ ]` |
| T018 | Criar `app/repositories/distributor_repo.py`: CRUD de `DistributorConfig` com encrypt/decrypt de credentials | T012, T016 | - | `app/repositories/distributor_repo.py` | 🟢 | `[ ]` |
| T019 | Criar `app/repositories/log_repo.py`: criar log de execução, atualizar contadores, listar últimas 30 por distribuidor | T013 | - | `app/repositories/log_repo.py` | 🟢 | `[ ]` |
| T020 | Criar `app/services/photo_storage.py`: `PhotoStorageService` com `upload_photo(user_id, dist_type, sku, filename, data) → url` via boto3 S3-compatible para Backblaze B2 | T003 | - | `app/services/photo_storage.py` | 🟢 | `[ ]` |
| T021 | Criar `app/schemas/`: Pydantic v2 schemas para `DistributorCreate`, `DistributorResponse`, `ProductData` (schema normalizado), `ConnectorLogResponse`, `ProductResponse` | T001 | `[//]` | `app/schemas/` | 🟢 | `[ ]` |
| T022 | Criar `app/services/connector_runner.py`: `ConnectorRunner` que orquestra execução — instancia conector, cria log, chama authenticate → fetch_catalog, faz upsert, upload fotos, marca ausentes, finaliza log | T014, T017, T019, T020 | - | `app/services/connector_runner.py` | 🟢 | `[ ]` |
| T023 | Implementar `app/connectors/dpk.py`: `DPKConnector` com login via Playwright, paginação do catálogo, extração de SKU/nome/descrição/fotos/preço/estoque/peso/medidas, seletores em dict configurável | T022 | - | `app/connectors/dpk.py` | 🟡 | `[ ]` |
| T024 | Implementar `app/connectors/furacao.py`: `FuracaoConnector` com mesmo padrão do DPK adaptado ao layout do Furacão | T022 | `[//]` | `app/connectors/furacao.py` | 🟡 | `[ ]` |
| T025 | Implementar `app/connectors/pellegrino.py`: `PellegrinoConnector` — fotos e descrição; `stock_quantity = None` | T022 | `[//]` | `app/connectors/pellegrino.py` | 🟡 | `[ ]` |
| T026 | Implementar `app/connectors/laquila_drive.py`: `LAquilaDriveConnector` via Google Drive API com service account — listar pasta, ler planilha, download fotos | T022 | `[//]` | `app/connectors/laquila_drive.py` | 🟡 | `[ ]` |
| T027 | Implementar `app/connectors/rufato.py` e `app/connectors/isapa.py`: conectores RPA com seletores a mapear durante implementação | T022 | `[//]` | `app/connectors/rufato.py` | 🟡 | `[ ]` |
| T028 | Implementar `app/connectors/rolemarmaster.py`: conector RPA, sem estoque (`stock_quantity = None`) | T022 | `[//]` | `app/connectors/rolemarmaster.py` | 🟡 | `[ ]` |
| T029 | Implementar `app/connectors/csv_import.py`: `CSVImportConnector` que recebe arquivo + column_mapping, parseia com openpyxl/csv, normaliza para `ProductData` | T022 | `[//]` | `app/connectors/csv_import.py` | 🟢 | `[ ]` |

## Fase 4 — Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T030 | Criar `app/main.py`: FastAPI app com lifespan (startup: init DB, scheduler; shutdown: cleanup Playwright), include routers, CORS middleware | T004, T022 | - | `app/main.py` | 🟢 | `[ ]` |
| T031 | Criar `app/api/routes/distributors.py`: endpoints POST/GET/PUT/DELETE /distributors + POST /distributors/{id}/test + POST /distributors/{id}/run | T018, T022, T030 | - | `app/api/routes/distributors.py` | 🟢 | `[ ]` |
| T032 | Criar `app/api/routes/logs.py`: GET /logs + GET /logs/{id} e `app/api/routes/products.py`: GET /products com filtros (distributor_type, status, search) e paginação | T019, T017, T030 | `[//]` | `app/api/routes/logs.py` | 🟢 | `[ ]` |
| T033 | Criar `app/api/routes/import_csv.py`: POST /import/csv com multipart upload e `app/api/routes/health.py`: GET /health | T029, T030 | `[//]` | `app/api/routes/import_csv.py` | 🟢 | `[ ]` |
| T034 | Criar `app/services/scheduler.py`: APScheduler com jobstore Postgres, jobs configuráveis por distribuidor (intervalo padrão: 6h), integração com ConnectorRunner | T022, T030 | - | `app/services/scheduler.py` | 🟡 | `[ ]` |

## Fase 5 — Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T035 | Configurar logging estruturado (JSON) com contexto por execução (distributor_type, log_id), garantir que credenciais nunca aparecem em logs | T030 | - | `app/main.py` | 🟢 | `[ ]` |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
-->

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-10 | Versão inicial gerada por `/reversa-to-do` | reversa |
