# Checklist de Produção

Verificações antes de colocar o connector-service em produção.

## Infraestrutura

- [ ] VPS Hetzner com Docker instalado
- [ ] Portainer ou Coolify acessível e configurado
- [ ] Domínio/subdomínio configurado no Cloudflare (`api-connectors.<dominio>`)
- [ ] Registro A no Cloudflare apontando para IP da VPS
- [ ] Cloudflare Proxy ativado (orange cloud)
- [ ] SSL/TLS mode: Full (strict)

## Banco de dados (Supabase)

- [ ] Projeto Supabase criado
- [ ] Migration executada: `alembic upgrade head`
- [ ] Extensão `pg_trgm` ativada
- [ ] RLS policies aplicadas (`scripts/rls_policies.sql`)
- [ ] Connection string testada (formato `postgresql+asyncpg://...`)
- [ ] Conexão direta (não pooler) ou pgBouncer em transaction mode

## Storage (Backblaze B2)

- [ ] Bucket `product-photos` criado
- [ ] Application Key gerada (Read + Write, escopo no bucket)
- [ ] Endpoint URL confirmado (região correta, ex: `us-west-004`)
- [ ] Cloudflare Bandwidth Alliance ativo (egress grátis)
- [ ] (Opcional) Transform Rule no Cloudflare para URL amigável de fotos

## Google Drive (L'Aquila)

- [ ] Service Account criada no Google Cloud Console
- [ ] Chave JSON gerada e salva como variável de ambiente
- [ ] Pasta do Drive compartilhada com email do service account
- [ ] Drive API habilitada no projeto Google Cloud
- [ ] (Opcional) Sheets API habilitada se a planilha for Google Sheets nativo

## Variáveis de ambiente

- [ ] `DATABASE_URL` configurada
- [ ] `ENCRYPTION_KEY` gerada e salva em local seguro
- [ ] `B2_KEY_ID` e `B2_APPLICATION_KEY` configuradas
- [ ] `B2_BUCKET_NAME` e `B2_ENDPOINT_URL` configuradas
- [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` configurada (se usar L'Aquila)
- [ ] `APP_ENV=production`
- [ ] `LOG_LEVEL=INFO`
- [ ] Nenhuma variável sensível commitada no repositório

## Aplicação

- [ ] Container builda sem erros
- [ ] `/health` retorna `{"status":"ok","version":"1.0.0"}`
- [ ] `/docs` abre documentação OpenAPI
- [ ] CORS configurado para domínio do frontend (trocar `*` por domínio real)

## Segurança

- [ ] `ENCRYPTION_KEY` backup em local seguro (perda = credenciais irrecuperáveis)
- [ ] Credenciais de distribuidores nunca aparecem em logs (filtro ativo)
- [ ] RLS ativo: vendedor A não vê dados do vendedor B
- [ ] Header `X-User-Id` substituído por JWT do Supabase Auth (TODO)
- [ ] Rate limiting no Cloudflare para endpoints sensíveis
- [ ] Firewall da VPS: apenas portas 80, 443 e SSH abertas

## Teste funcional

- [ ] Criar distribuidor DPK via API
- [ ] "Testar conexão" retorna sucesso
- [ ] Executar extração e ver produtos no banco
- [ ] Foto de produto acessível via URL do B2
- [ ] Log de execução consultável via API
- [ ] Importar CSV e ver produtos criados
- [ ] Soft delete: produto ausente na re-extração fica "unavailable"

## Monitoramento

- [ ] Logs do container acessíveis (Portainer ou Coolify)
- [ ] Health check configurado (restart automático se falhar)
- [ ] (Recomendado) Alertas para falhas de conector
- [ ] (Recomendado) Dashboard de métricas (Grafana ou similar)

## Pós-deploy

- [ ] Documentar credenciais de acesso em local seguro
- [ ] Configurar backup automático do Supabase
- [ ] Agendar rotação de chaves B2 a cada 90 dias
- [ ] Planejar refinamento de seletores CSS após primeiro teste real
