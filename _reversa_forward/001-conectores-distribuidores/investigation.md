# Investigation: Conectores de Distribuidores

> Identificador: `001-conectores-distribuidores`
> Data: `2026-06-10`

## 1. Pesquisa de fundo

### 1.1 RPA/Scraping em Python — Estado da arte

| Ferramenta | Prós | Contras | Veredito |
|------------|------|---------|----------|
| **Playwright** | Async nativo, multi-browser, stealth plugins disponíveis, API moderna, headless estável | Imagem Docker grande (~1.5GB com Chromium) | 🟢 Escolhido |
| Selenium | Maduro, ampla documentação | Sync por padrão, WebDriver instável, mais lento | 🔴 Descartado |
| Puppeteer (via pyppeteer) | Rápido, bom para Chrome | Bridge Python instável, manutenção irregular | 🔴 Descartado |
| Scrapy | Excelente para sites estáticos | Sem suporte a JS-rendered pages sem Splash | 🔴 Descartado |
| httpx + BeautifulSoup | Leve, rápido | Não funciona com SPAs ou sites JS-heavy | 🔴 Descartado para sites auth |

### 1.2 Google Drive API — Opções de autenticação

| Método | Prós | Contras | Veredito |
|--------|------|---------|----------|
| **Service Account** | Sem flow interativo, ideal para backend, acesso via share da pasta | Requer que a pasta seja compartilhada com o service account email | 🟢 Escolhido |
| OAuth 2.0 (user) | Acesso completo ao Drive do usuário | Exige flow interativo, token refresh, mais complexo | 🔴 Descartado |
| API Key | Simples | Apenas para arquivos públicos | 🔴 Descartado |

### 1.3 Object Storage — Backblaze B2 vs alternativas

| Serviço | Custo/GB/mês | Egress | S3-compatible | Veredito |
|---------|-------------|--------|---------------|----------|
| **Backblaze B2** | $0.006 | Grátis com Cloudflare (Bandwidth Alliance) | Sim | 🟢 Escolhido (já na infra) |
| AWS S3 | $0.023 | $0.09/GB | Sim | 🔴 Mais caro, desnecessário |
| MinIO self-hosted | $0 (server) | N/A | Sim | 🔴 Overhead operacional |
| Supabase Storage | $0.021 | Incluso até 2GB | Sim | 🟡 Alternativa viável, mas Backblaze é mais barato para volume |

### 1.4 Criptografia de credenciais

| Abordagem | Prós | Contras | Veredito |
|-----------|------|---------|----------|
| **Fernet (cryptography lib)** | Simples, seguro (AES-128-CBC + HMAC), chave única | AES-128, não AES-256 (suficiente para MVP) | 🟢 MVP |
| AES-256-GCM manual | AES-256 conforme spec | Mais código, risco de implementação errada | 🟡 Pós-MVP se auditoria exigir |
| Vault | Enterprise-grade | Infra extra, overkill para single-tenant | 🔴 Descartado |
| Supabase Vault (pgsodium) | Nativo do Supabase, AES-256 | Funcionalidade em beta; depende de extensão | 🟡 Avaliar quando estável |

### 1.5 Scheduler — Opções avaliadas

| Ferramenta | Prós | Contras | Veredito |
|------------|------|---------|----------|
| **APScheduler** | In-process, jobstore Postgres, async support | Single-process (sem distributed locking nativo) | 🟢 MVP |
| Celery + Redis | Distributed, mature | Redis extra, complexidade de setup | 🟡 Pós-MVP para escala |
| cron do host | Zero overhead | Sem visibilidade, sem retry, sem logs | 🔴 Descartado |
| Airflow | Enterprise-grade DAGs | Overkill para 7 jobs simples | 🔴 Descartado |

## 2. Padrões aplicáveis

### 2.1 Strategy Pattern para conectores

Cada conector é uma strategy que implementa `BaseConnector`. O registry mapeia `distributor_type` → classe concreta. Permite adicionar novos distribuidores sem modificar código existente (Open/Closed Principle).

```
BaseConnector (ABC)
├── DPKConnector
├── FuracaoConnector
├── RUFATOConnector
├── ISAPAConnector
├── PellegrinoConnector
├── LAquilaDriveConnector
├── RolemarmasterConnector
└── CSVImportConnector
```

### 2.2 Repository Pattern para dados

`ProductRepository` encapsula queries ao Supabase. Método `upsert_products(distributor_config_id, products: list[ProductData])` faz INSERT ON CONFLICT UPDATE em batch.

### 2.3 Circuit Breaker para resiliência

Após 3 falhas consecutivas em um conector, marca como `status = "circuit_open"` e não tenta novamente por 1 hora. Health check periódico reseta o circuito.

### 2.4 Retry com Backoff exponencial

Decorator `@retry(max_attempts=3, backoff=[5, 15, 45])` aplicado em operações de rede (login, navegação, download de fotos).

## 3. Estrutura de diretórios proposta

```
connector-service/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── alembic/                    # migrations
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app + startup/shutdown
│   ├── config.py               # Settings via pydantic-settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── distributors.py # CRUD distribuidores
│   │   │   ├── connectors.py   # Executar/testar conectores
│   │   │   └── logs.py         # Consultar logs
│   │   └── deps.py             # Dependencies (DB, auth)
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py             # BaseConnector (ABC)
│   │   ├── registry.py         # Mapeia type → class
│   │   ├── dpk.py
│   │   ├── furacao.py
│   │   ├── rufato.py
│   │   ├── isapa.py
│   │   ├── pellegrino.py
│   │   ├── laquila_drive.py
│   │   ├── rolemarmaster.py
│   │   └── csv_import.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── distributor.py      # DistributorConfig SQLAlchemy model
│   │   ├── product.py          # Product model
│   │   └── connector_log.py    # ConnectorLog model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── distributor.py      # Pydantic request/response
│   │   ├── product.py          # ProductData (schema normalizado)
│   │   └── connector_log.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── connector_runner.py # Orquestra execução de conectores
│   │   ├── photo_storage.py    # Upload para Backblaze B2
│   │   ├── encryption.py       # Fernet encrypt/decrypt
│   │   └── scheduler.py        # APScheduler setup
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── distributor_repo.py
│   │   ├── product_repo.py
│   │   └── log_repo.py
│   └── db/
│       ├── __init__.py
│       ├── session.py          # AsyncSession factory
│       └── base.py             # SQLAlchemy Base
├── tests/
│   ├── conftest.py
│   ├── test_connectors/
│   ├── test_api/
│   └── test_services/
└── scripts/
    └── seed_distributors.py    # Seed com tipos de distribuidores
```

## 4. Dockerfile base

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
RUN playwright install chromium --with-deps

COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 5. Dependências principais

| Pacote | Versão mínima | Função |
|--------|--------------|--------|
| fastapi | 0.111+ | Framework HTTP |
| uvicorn | 0.30+ | ASGI server |
| playwright | 1.44+ | Browser automation |
| sqlalchemy[asyncio] | 2.0+ | ORM async |
| asyncpg | 0.29+ | Driver Postgres async |
| alembic | 1.13+ | Migrations |
| pydantic | 2.7+ | Schema validation |
| pydantic-settings | 2.3+ | Config via env vars |
| boto3 | 1.34+ | Backblaze B2 (S3-compatible) |
| google-api-python-client | 2.130+ | Google Drive API |
| cryptography | 42+ | Fernet encryption |
| apscheduler | 3.10+ | Job scheduling |
| openpyxl | 3.1+ | Leitura de Excel |
| python-multipart | 0.0.9+ | Upload de arquivos |
| httpx | 0.27+ | HTTP client async |

## 6. Histórico

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-10 | Versão inicial | reversa-plan |
