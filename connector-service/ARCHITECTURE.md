# Arquitetura — Connector Service

## Diagrama de componentes

```
                         ┌──────────────────────────────────────────────┐
                         │              Cloudflare                      │
                         │   DNS + SSL + DDoS Protection                │
                         │   api-connectors.<dominio>                   │
                         └────────────────┬─────────────────────────────┘
                                          │ HTTPS
                         ┌────────────────▼─────────────────────────────┐
                         │         VPS Hetzner (Docker)                 │
                         │  ┌─────────────────────────────────────────┐ │
                         │  │      connector-service (container)      │ │
                         │  │                                         │ │
                         │  │  ┌──────────┐  ┌──────────────────────┐│ │
                         │  │  │ FastAPI   │  │     APScheduler      ││ │
                         │  │  │ (uvicorn) │  │  (jobs periódicos)   ││ │
                         │  │  └─────┬─────┘  └──────────┬───────────┘│ │
                         │  │        │                   │            │ │
                         │  │        ▼                   ▼            │ │
                         │  │  ┌─────────────────────────────────────┐│ │
                         │  │  │         ConnectorRunner             ││ │
                         │  │  │  (orquestra execução de conectores) ││ │
                         │  │  └─────────────┬───────────────────────┘│ │
                         │  │                │                        │ │
                         │  │    ┌───────────┼───────────┐            │ │
                         │  │    ▼           ▼           ▼            │ │
                         │  │ ┌──────┐  ┌────────┐  ┌──────────┐     │ │
                         │  │ │ RPA  │  │ Drive  │  │   CSV    │     │ │
                         │  │ │Connec│  │Connec  │  │ Import   │     │ │
                         │  │ │tors  │  │tor     │  │ Connector│     │ │
                         │  │ └──┬───┘  └───┬────┘  └──────────┘     │ │
                         │  │    │          │                         │ │
                         │  └────┼──────────┼─────────────────────────┘ │
                         └───────┼──────────┼───────────────────────────┘
                                 │          │
              ┌──────────────────┘          └──────────────┐
              ▼                                            ▼
   ┌──────────────────────┐                  ┌─────────────────────────┐
   │  Sites Distribuidores │                  │   Google Drive API      │
   │  (Playwright headless)│                  │   (L'Aquila — pasta     │
   │  DPK, Furacão, RUFATO │                  │    compartilhada)       │
   │  ISAPA, Pellegrino,   │                  └─────────────────────────┘
   │  Rolemarmaster        │
   └──────────────────────┘

              ┌─────────────────────────────────────────────┐
              │              Serviços Externos               │
              │                                             │
              │  ┌──────────────┐    ┌───────────────────┐  │
              │  │   Supabase   │    │   Backblaze B2    │  │
              │  │  (Postgres)  │    │  (S3-compatible)  │  │
              │  │              │    │                   │  │
              │  │ - distributor│    │ - product-photos  │  │
              │  │   _configs   │    │   bucket          │  │
              │  │ - products   │    │                   │  │
              │  │ - connector  │    │ CDN via Cloudflare│  │
              │  │   _logs      │    │ Bandwidth Alliance│  │
              │  └──────────────┘    └───────────────────┘  │
              └─────────────────────────────────────────────┘
```

## Camadas da aplicação

```
┌─────────────────────────────────────────────────┐
│  API Layer (FastAPI routes)                      │
│  app/api/routes/                                 │
│  distributors.py, logs.py, products.py,          │
│  import_csv.py, health.py                        │
├─────────────────────────────────────────────────┤
│  Service Layer                                   │
│  app/services/                                   │
│  connector_runner.py, encryption.py,             │
│  photo_storage.py, scheduler.py                  │
├─────────────────────────────────────────────────┤
│  Connector Layer (Strategy Pattern)              │
│  app/connectors/                                 │
│  base.py (ABC), registry.py, dpk.py,            │
│  furacao.py, pellegrino.py, laquila_drive.py,    │
│  rufato.py, rolemarmaster.py, csv_import.py      │
├─────────────────────────────────────────────────┤
│  Repository Layer                                │
│  app/repositories/                               │
│  distributor_repo.py, product_repo.py,           │
│  log_repo.py                                     │
├─────────────────────────────────────────────────┤
│  Data Layer                                      │
│  app/models/ (SQLAlchemy ORM)                    │
│  app/db/ (AsyncSession, Base)                    │
│  app/schemas/ (Pydantic v2)                      │
└─────────────────────────────────────────────────┘
```

## Componentes

### Conectores (`app/connectors/`)

Cada conector implementa `BaseConnector` (ABC) com 4 métodos:

| Método | Descrição |
|--------|-----------|
| `authenticate()` | Login no distribuidor |
| `fetch_catalog()` | Extrai lista de `ProductData` |
| `fetch_stock()` | Retorna `{sku: quantity}` |
| `health_check()` | Verifica se distribuidor está acessível |

O `registry.py` mapeia `distributor_type` (string) para a classe concreta via decorator `@register_connector`. Adicionar um novo distribuidor = criar uma classe + decorator.

**Conectores RPA** usam Playwright headless (Chromium) com:
- Stealth: user-agent rotation, delays humanos entre ações
- Seletores CSS configuráveis em dict por conector
- Retry com backoff exponencial (5s, 15s, 45s)

**Conector Drive** (L'Aquila) usa Google Drive API com service account.

**Conector CSV** processa upload de Excel/CSV com mapeamento de colunas.

### ConnectorRunner (`app/services/connector_runner.py`)

Orquestra a execução completa:
1. Instancia o conector correto via registry
2. Cria log de execução
3. Autentica no distribuidor
4. Extrai catálogo
5. Upload de fotos para B2
6. Upsert de produtos no banco
7. Marca produtos ausentes como indisponíveis (soft delete)
8. Finaliza log com contadores

### Modelo de dados

3 tabelas com Row Level Security:

- **`distributor_configs`** — Configuração por distribuidor por vendedor (credenciais criptografadas)
- **`products`** — Catálogo normalizado com UNIQUE(distributor_config_id, sku)
- **`connector_logs`** — Histórico de execuções com contadores

### Segurança

- Credenciais criptografadas com Fernet (AES-128-CBC + HMAC) at rest
- Filtro de logging impede credenciais de vazar em logs
- RLS no Supabase: vendedor só acessa seus próprios dados
- Cloudflare: SSL, proteção DDoS, rate limiting

### Fluxo de dados

```
Distribuidor (site/Drive)
    │
    ▼ [Playwright / Drive API]
ProductData (dataclass normalizado)
    │
    ├──▶ Fotos ──▶ Backblaze B2 ──▶ URL pública
    │
    └──▶ Dados ──▶ Supabase (upsert) ──▶ API REST ──▶ Frontend
```
