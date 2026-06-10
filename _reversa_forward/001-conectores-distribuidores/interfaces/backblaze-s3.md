# Interface: Backblaze B2 (S3-compatible)

> Tipo: HTTP (S3 SDK)
> Endpoint: `https://s3.<region>.backblazeb2.com`
> Auth: B2 Application Key (via boto3)

## Configuração

```env
B2_KEY_ID=<key_id>
B2_APPLICATION_KEY=<app_key>
B2_BUCKET_NAME=product-photos
B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
```

## Operações usadas

### Upload de foto

- **Método:** `s3.put_object()` ou `s3.upload_fileobj()`
- **Path pattern:** `{user_id}/{distributor_type}/{sku}/{filename}`
- **Content-Type:** `image/jpeg`, `image/png`, `image/webp`
- **ACL:** Bucket com public read habilitado (ou signed URLs)
- **Timeout:** 30s por foto, retry 3x com backoff

### URL pública

Com Cloudflare Bandwidth Alliance (egress grátis):
```
https://<bucket>.s3.<region>.backblazeb2.com/{path}
```

Ou via Cloudflare Transform Rule:
```
https://photos.<dominio>/{path}
```

### Delete de foto

Raramente usado (soft delete de produto não remove foto). Cleanup via lifecycle rule se necessário no futuro.

## Erros esperados

| Erro | Causa | Ação |
|------|-------|------|
| 403 Forbidden | Key inválida ou bucket errado | Log + alerta |
| 408 Request Timeout | Upload lento | Retry com backoff |
| 503 Service Unavailable | B2 temporariamente indisponível | Retry; manter URL original do distribuidor como fallback |

## Estimativa de volume

- ~7 distribuidores × ~500 SKUs/média × ~5 fotos/SKU = ~17.500 fotos
- Tamanho médio: ~200KB/foto = ~3.5GB total
- Custo B2: ~$0.02/mês (storage) + $0 egress (Cloudflare)
