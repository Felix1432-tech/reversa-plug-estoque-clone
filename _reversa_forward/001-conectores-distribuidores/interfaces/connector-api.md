# Interface: Connector REST API

> Tipo: HTTP (REST)
> Base URL: `https://api-connectors.<dominio>/api/v1`
> Auth: Bearer JWT

## Endpoints

### POST /distributors

Cadastrar configuração de distribuidor.

**Request:**
```json
{
  "distributor_type": "dpk",
  "credentials": {
    "login": "user@email.com",
    "password": "senha123"
  },
  "settings": {}
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "distributor_type": "dpk",
  "status": "configured",
  "created_at": "2026-06-10T00:00:00Z"
}
```

**Erros:**
| Código | Causa | Body |
|--------|-------|------|
| 400 | `distributor_type` inválido | `{"detail": "Tipo de distribuidor inválido"}` |
| 409 | Distribuidor já configurado para este usuário | `{"detail": "Distribuidor já configurado"}` |

---

### GET /distributors

Listar distribuidores configurados pelo usuário.

**Response 200:**
```json
[
  {
    "id": "uuid",
    "distributor_type": "dpk",
    "status": "configured",
    "last_sync_at": "2026-06-10T10:00:00Z",
    "last_error": null
  }
]
```

---

### PUT /distributors/{id}

Atualizar credenciais ou settings.

**Request:**
```json
{
  "credentials": {
    "login": "novo_login",
    "password": "nova_senha"
  }
}
```

**Response 200:** Distributor atualizado.

---

### DELETE /distributors/{id}

Remover configuração (cascade: remove produtos e logs).

**Response 204:** No content.

---

### POST /distributors/{id}/test

Testar credenciais (faz login sem extração completa).

**Response 200:**
```json
{"status": "success", "message": "Login bem-sucedido no DPK"}
```

**Response 200 (falha):**
```json
{"status": "error", "message": "Login falhou: credenciais inválidas"}
```

**Timeout:** 30 segundos.

---

### POST /distributors/{id}/run

Disparar extração completa do catálogo.

**Response 202:**
```json
{"log_id": "uuid", "status": "running"}
```

**Idempotência:** Se já há execução `running` para este distribuidor, retorna 409 com o `log_id` existente.

---

### GET /logs

Listar logs de execução (últimas 30 por distribuidor).

**Query params:** `distributor_id` (opcional), `limit` (default 30), `offset` (default 0)

**Response 200:**
```json
[
  {
    "id": "uuid",
    "distributor_type": "dpk",
    "status": "success",
    "products_found": 150,
    "products_created": 10,
    "products_updated": 140,
    "errors_count": 0,
    "started_at": "2026-06-10T10:00:00Z",
    "finished_at": "2026-06-10T10:05:30Z"
  }
]
```

---

### GET /logs/{id}

Detalhe de um log específico (inclui `error_details`).

---

### GET /products

Listar produtos extraídos.

**Query params:** `distributor_type`, `status`, `search` (nome), `limit`, `offset`

**Response 200:**
```json
{
  "items": [...],
  "total": 1500,
  "limit": 20,
  "offset": 0
}
```

---

### POST /import/csv

Upload de CSV/Excel como fallback.

**Request:** `multipart/form-data` com campo `file` + `distributor_config_id` + `column_mapping` (JSON).

**Response 202:**
```json
{"log_id": "uuid", "status": "processing"}
```

---

### GET /health

Health check.

**Response 200:**
```json
{"status": "ok", "version": "1.0.0"}
```
