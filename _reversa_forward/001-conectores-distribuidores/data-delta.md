# Data Delta: Conectores de Distribuidores

> Identificador: `001-conectores-distribuidores`
> Data: `2026-06-10`
> Banco: Supabase (Postgres)

## 1. Resumo

3 tabelas novas no schema `public` do Supabase. Nenhuma tabela existente alterada (greenfield). Row Level Security (RLS) ativo em todas as tabelas, filtrando por `user_id`.

## 2. Tabelas novas

### 2.1 `distributor_configs`

```sql
CREATE TABLE distributor_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  distributor_type TEXT NOT NULL CHECK (distributor_type IN (
    'dpk', 'furacao', 'rufato', 'isapa', 'pellegrino', 'laquila', 'rolemarmaster'
  )),
  credentials BYTEA NOT NULL,          -- Fernet-encrypted JSON {login, password} ou {service_account_key}
  status TEXT NOT NULL DEFAULT 'not_configured' CHECK (status IN (
    'configured', 'not_configured', 'error', 'circuit_open'
  )),
  last_sync_at TIMESTAMPTZ,
  last_error TEXT,
  settings JSONB DEFAULT '{}',         -- Config específica (ex: drive_folder_id, polling_interval)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE(user_id, distributor_type)    -- 1 config por distribuidor por vendedor
);

-- RLS
ALTER TABLE distributor_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own configs" ON distributor_configs
  FOR ALL USING (auth.uid() = user_id);

-- Índices
CREATE INDEX idx_distconfig_user ON distributor_configs(user_id);
CREATE INDEX idx_distconfig_type ON distributor_configs(distributor_type);
```

### 2.2 `products`

```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  distributor_config_id UUID NOT NULL REFERENCES distributor_configs(id) ON DELETE CASCADE,
  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  price NUMERIC(12, 2),
  stock_quantity INTEGER,              -- NULL se distribuidor não fornece estoque
  weight NUMERIC(8, 3),               -- kg
  height NUMERIC(8, 2),               -- cm
  width NUMERIC(8, 2),                -- cm
  length NUMERIC(8, 2),               -- cm
  photos JSONB DEFAULT '[]',          -- ["https://b2.backblaze.../photo1.jpg", ...]
  fiscal_data JSONB DEFAULT '{}',     -- {ncm, gtin, ean, ...}
  raw_data JSONB DEFAULT '{}',        -- Dados brutos originais do distribuidor
  status TEXT NOT NULL DEFAULT 'available' CHECK (status IN (
    'available', 'unavailable'         -- soft delete via status
  )),
  last_stock_check_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE(distributor_config_id, sku)
);

-- RLS via join com distributor_configs
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own products" ON products
  FOR ALL USING (
    distributor_config_id IN (
      SELECT id FROM distributor_configs WHERE user_id = auth.uid()
    )
  );

-- Índices
CREATE INDEX idx_products_distconfig ON products(distributor_config_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops);
```

**Nota:** O índice trigram (`gin_trgm_ops`) requer a extensão `pg_trgm`. Ativar no Supabase: `CREATE EXTENSION IF NOT EXISTS pg_trgm;`

### 2.3 `connector_logs`

```sql
CREATE TABLE connector_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  distributor_config_id UUID NOT NULL REFERENCES distributor_configs(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'running' CHECK (status IN (
    'running', 'success', 'partial', 'error'
  )),
  products_found INTEGER DEFAULT 0,
  products_created INTEGER DEFAULT 0,
  products_updated INTEGER DEFAULT 0,
  errors_count INTEGER DEFAULT 0,
  error_details JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS via join
ALTER TABLE connector_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own logs" ON connector_logs
  FOR ALL USING (
    distributor_config_id IN (
      SELECT id FROM distributor_configs WHERE user_id = auth.uid()
    )
  );

-- Índices
CREATE INDEX idx_connlogs_distconfig ON connector_logs(distributor_config_id);
CREATE INDEX idx_connlogs_started ON connector_logs(started_at DESC);

-- Cleanup: manter apenas últimas 30 execuções por distribuidor (via cron ou trigger)
```

## 3. Upsert pattern

```sql
-- Upsert de produtos (executado pelo conector após extração)
INSERT INTO products (distributor_config_id, sku, name, description, price, stock_quantity,
                      weight, height, width, length, photos, fiscal_data, raw_data, status)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 'available')
ON CONFLICT (distributor_config_id, sku)
DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  price = EXCLUDED.price,
  stock_quantity = EXCLUDED.stock_quantity,
  weight = EXCLUDED.weight,
  height = EXCLUDED.height,
  width = EXCLUDED.width,
  length = EXCLUDED.length,
  photos = EXCLUDED.photos,
  fiscal_data = EXCLUDED.fiscal_data,
  raw_data = EXCLUDED.raw_data,
  status = 'available',
  updated_at = now();
```

## 4. Soft delete de produtos ausentes

```sql
-- Após extração: marcar produtos que NÃO apareceram na extração como indisponível
UPDATE products
SET status = 'unavailable', updated_at = now()
WHERE distributor_config_id = $1
  AND sku NOT IN (SELECT unnest($2::text[]))  -- $2 = array de SKUs encontrados
  AND status = 'available';
```

## 5. Extensões Supabase necessárias

| Extensão | Uso |
|----------|-----|
| `pg_trgm` | Busca fuzzy por nome de produto |
| `pgcrypto` | `gen_random_uuid()` (já ativo por padrão no Supabase) |

## 6. Backup e retenção

- Backups automáticos do Supabase (configuração existente)
- Logs de conector: reter últimas 30 por distribuidor (cron job SQL ou trigger)
- Fotos no B2: sem expiração (lifecycle rule: keep forever)

## 7. Histórico

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-10 | Versão inicial | reversa-plan |
