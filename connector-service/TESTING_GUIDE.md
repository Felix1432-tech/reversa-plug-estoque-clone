# Guia de Testes

## Estrutura de testes

```
tests/
├── conftest.py                      # Fixtures compartilhadas
├── test_connectors/
│   └── test_base.py                 # BaseConnector, retry decorator
├── test_services/
│   └── test_encryption.py           # EncryptionService
├── test_repositories/               # (a completar com banco de teste)
└── test_api/                        # (a completar com test client)
```

## Executar testes

### Via Docker

```bash
cd connector-service
docker compose exec app pytest -v
```

### Via ambiente local (sem Docker)

```bash
cd connector-service

# Criar virtualenv
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Instalar dependências
pip install -e ".[dev]"

# Executar testes
pytest -v
```

### Com cobertura

```bash
pytest --cov=app --cov-report=term-missing -v
```

## Testes existentes

### test_connectors/test_base.py

| Teste | O que valida |
|-------|-------------|
| `test_base_connector_cannot_be_instantiated` | `BaseConnector` é abstrato — não pode ser instanciado diretamente |
| `test_subclass_without_methods_raises` | Subclasse que não implementa todos os métodos levanta `TypeError` |
| `test_subclass_with_all_methods` | Subclasse completa instancia corretamente |
| `test_product_data_defaults` | `ProductData` tem defaults sensatos (None, lista vazia) |
| `test_retry_decorator_succeeds_on_second_attempt` | Retry funciona após falha temporária |
| `test_retry_decorator_exhausts_attempts` | Após esgotar tentativas, exceção é propagada |

### test_services/test_encryption.py

| Teste | O que valida |
|-------|-------------|
| `test_encrypt_decrypt_roundtrip` | Encrypt → Decrypt retorna dados originais |
| `test_encrypted_data_differs_from_plaintext` | Dados criptografados não contêm texto original |
| `test_decrypt_with_wrong_key_raises` | Chave errada levanta `ValueError` |
| `test_encrypt_produces_bytes` | Resultado do encrypt é `bytes` |

## Testes manuais — API

Após subir o serviço (`docker compose up`), usar curl ou a interface `/docs`:

### 1. Health check

```bash
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0"}
```

### 2. Cadastrar distribuidor

```bash
curl -X POST http://localhost:8000/api/v1/distributors \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 00000000-0000-0000-0000-000000000001" \
  -d '{
    "distributor_type": "dpk",
    "credentials": {"login": "seu_email", "password": "sua_senha"}
  }'
```

### 3. Testar conexão

```bash
curl -X POST http://localhost:8000/api/v1/distributors/<id>/test \
  -H "X-User-Id: 00000000-0000-0000-0000-000000000001"
# {"status":"success","message":"Login bem-sucedido no DPK"}
```

### 4. Executar extração

```bash
curl -X POST http://localhost:8000/api/v1/distributors/<id>/run \
  -H "X-User-Id: 00000000-0000-0000-0000-000000000001"
# {"log_id":"<uuid>","status":"running"}
```

### 5. Verificar log

```bash
curl http://localhost:8000/api/v1/logs/<log_id> \
  -H "X-User-Id: 00000000-0000-0000-0000-000000000001"
```

### 6. Listar produtos

```bash
curl "http://localhost:8000/api/v1/products?distributor_type=dpk&limit=5" \
  -H "X-User-Id: 00000000-0000-0000-0000-000000000001"
```

### 7. Importar CSV

```bash
curl -X POST http://localhost:8000/api/v1/import/csv \
  -H "X-User-Id: 00000000-0000-0000-0000-000000000001" \
  -F "file=@catalogo.csv" \
  -F "distributor_config_id=<id>" \
  -F 'column_mapping={"sku":"codigo","name":"nome","price":"preco","stock":"estoque"}'
```

## Testes a implementar

| Prioridade | Teste | Motivo |
|-----------|-------|--------|
| Alta | Integration tests com banco real | Validar upsert, soft delete, RLS |
| Alta | Test de cada conector com mock de Playwright | Validar parsing de seletores |
| Média | API tests com httpx.AsyncClient | Validar endpoints end-to-end |
| Média | Test de photo_storage com localstack/mock S3 | Validar upload para B2 |
| Baixa | Test do scheduler | Validar agendamento de jobs |
