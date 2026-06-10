# Roadmap: Conectores de Distribuidores

> Identificador: `001-conectores-distribuidores`
> Data: `2026-06-10`
> Requirements: `_reversa_forward/001-conectores-distribuidores/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

🟢 Backend Python/FastAPI servindo API REST para CRUD de distribuidores, execução de conectores e consulta de logs. Cada conector é uma classe que implementa a interface abstrata `Connector` (authenticate, fetch_catalog, fetch_stock, health_check). Conectores RPA usam Playwright headless; conector L'Aquila usa Google Drive API. O serviço roda em container Docker, deployado via Coolify na VPS Hetzner. Banco de dados Supabase (Postgres). Fotos de produtos armazenadas em Backblaze B2 via SDK S3-compatible. DNS e SSL via Cloudflare com subdomínio dedicado (ex: `api-connectors.dominio.com`). Execuções agendadas via scheduler interno (APScheduler ou similar). Fallback de importação CSV/Excel via endpoint de upload.

## 2. Princípios aplicados

> Projeto greenfield — sem `principles.md` pré-existente. Os princípios abaixo são derivados das decisões de arquitetura registradas no SDD.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| 🟡 Modularidade (1 conector = 1 módulo) | Cada distribuidor é uma classe isolada; adicionar/remover não afeta os demais | respeita |
| 🟡 Falha isolada | Exceção em um conector não propaga para os demais (try/except por conector) | respeita |
| 🟡 Dados persistentes (soft delete) | Produto removido do distribuidor → `status = "unavailable"`, nunca DELETE | respeita |
| 🟡 Credenciais seguras | AES-256 at rest no Supabase; nunca em logs ou responses | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Python 3.12+ com FastAPI como framework HTTP | Assíncrono nativo, excelente para I/O-bound (scraping), tipagem forte com Pydantic, ecossistema maduro para Drive API e Playwright | Flask (sync, menos performático), Django (overhead desnecessário para API pura) | 🟢 |
| D-02 | Playwright headless para conectores RPA | Superior a Selenium em velocidade e estabilidade; suporta múltiplos browsers; API async nativa | Selenium (mais lento, API sync), Puppeteer (Node.js, exigiria bridge), Scrapy (sem suporte a JS-rendered pages) | 🟢 |
| D-03 | Supabase (Postgres) como banco de dados | Já disponível na infra do usuário; Postgres gerenciado com Row Level Security, backups automáticos, API REST nativa | SQLite (sem concorrência), MySQL (sem jsonb nativo), MongoDB (desnecessário para schema semi-estruturado) | 🟢 |
| D-04 | Backblaze B2 para storage de fotos | S3-compatible, já disponível na infra; custo baixo; CDN via Cloudflare Transform Rules | MinIO self-hosted (overhead operacional), filesystem local (sem CDN, ponto único de falha) | 🟢 |
| D-05 | Docker container único para o serviço de conectores | Simplifica deploy via Coolify/Portainer; Playwright incluso na imagem; escalável horizontalmente se necessário | VM bare-metal (sem isolamento), Kubernetes (overkill para MVP) | 🟢 |
| D-06 | APScheduler para agendamento de execuções | Leve, em-processo, persistência via Postgres (jobstore); sem necessidade de infra extra | Celery + Redis (overhead para MVP), cron do host (sem visibilidade), Airflow (enterprise, overkill) | 🟡 |
| D-07 | Pydantic v2 como schema de normalização (ProductData) | Validação + serialização em um lugar; integração nativa com FastAPI; performance superior ao v1 | Dataclasses (sem validação), marshmallow (mais verboso) | 🟢 |
| D-08 | Fernet (AES-128-CBC via cryptography lib) para criptografia de credenciais em MVP; migrar para AES-256-GCM se necessário | Fernet é seguro, simples e auditável; chave derivada de variável de ambiente | Vault (overhead operacional para MVP), KMS (custo/complexidade) | 🟡 |
| D-09 | Google Drive API via service account com share da pasta | Mais simples que OAuth flow para acesso a pasta compartilhada; sem interação do usuário | OAuth user-based (exige flow interativo), download manual (sem automação) | 🟡 |
| D-10 | Subdomínio Cloudflare `api-connectors.<dominio>` com proxy ativo | SSL automático, proteção DDoS, cache de assets estáticos, rate limiting via Cloudflare rules | Domínio raiz (conflito com frontend), IP direto (sem proteção) | 🟢 |

## 4. Premissas

> Todas as dúvidas foram resolvidas na sessão de clarify. Nenhuma premissa pendente.

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| — | — | — |

## 5. Delta arquitetural

> Projeto greenfield. Não há legado. Todos os componentes abaixo são novos.

| Componente | Arquivo de origem | Tipo de mudança | Resumo |
|------------|-------------------|-----------------|--------|
| `connector-service` | `_reversa_sdd/sdd/conectores-distribuidores.md` | componente-novo | Serviço FastAPI com API REST para gerenciar distribuidores, executar conectores e consultar logs |
| `connector-base` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-01` | componente-novo | Classe abstrata `BaseConnector` com interface padrão |
| `connector-dpk` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-02` | componente-novo | Conector RPA para DPK via Playwright |
| `connector-furacao` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-03` | componente-novo | Conector RPA para Furacão via Playwright |
| `connector-rufato` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-04` | componente-novo | Conector RPA para RUFATO via Playwright |
| `connector-isapa` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-05` | componente-novo | Conector RPA para ISAPA via Playwright |
| `connector-pellegrino` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-06` | componente-novo | Conector RPA para Pellegrino via Playwright (sem estoque) |
| `connector-laquila` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-07` | componente-novo | Conector Google Drive API para L'Aquila |
| `connector-rolemarmaster` | `requirements.md#RF-08` | componente-novo | Conector RPA para Rolemarmaster (sem estoque) |
| `photo-storage` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-12` | componente-novo | Módulo de upload para Backblaze B2 via boto3 |
| `csv-importer` | `_reversa_sdd/sdd/conectores-distribuidores.md#RF-08` | componente-novo | Importação manual CSV/Excel como fallback |
| `scheduler` | `_reversa_sdd/sdd/conectores-distribuidores.md#6.2` | componente-novo | APScheduler para execuções periódicas |

## 6. Delta no modelo de dados

- Resumo: 3 tabelas novas (`distributor_configs`, `products`, `connector_logs`) no Supabase Postgres com índices otimizados, RLS por `user_id`, e constraint UNIQUE(distributor_config_id, sku) para upsert.
- Detalhe completo em: `_reversa_forward/001-conectores-distribuidores/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Connector REST API | HTTP | `_reversa_forward/001-conectores-distribuidores/interfaces/connector-api.md` |
| Backblaze B2 (S3) | HTTP (SDK) | `_reversa_forward/001-conectores-distribuidores/interfaces/backblaze-s3.md` |
| Google Drive API | HTTP (SDK) | `_reversa_forward/001-conectores-distribuidores/interfaces/google-drive.md` |
| Sites distribuidores (RPA) | HTTP (browser) | `_reversa_forward/001-conectores-distribuidores/interfaces/distributor-sites.md` |

## 8. Plano de migração

1. 🟢 Criar tabelas no Supabase via migration SQL: `distributor_configs`, `products`, `connector_logs`
2. 🟢 Configurar RLS policies: cada vendedor só acessa seus próprios registros
3. 🟢 Criar bucket no Backblaze B2: `product-photos` com lifecycle rule (sem expiração)
4. 🟢 Configurar Cloudflare: subdomínio `api-connectors.<dominio>` → IP da VPS Hetzner
5. 🟡 Gerar service account Google para acesso ao Drive da L'Aquila
6. 🟢 Build da imagem Docker com Playwright pré-instalado (mcr.microsoft.com/playwright/python como base)
7. 🟢 Deploy via Coolify com variáveis de ambiente: `DATABASE_URL`, `B2_KEY_ID`, `B2_APPLICATION_KEY`, `ENCRYPTION_KEY`, `GOOGLE_SERVICE_ACCOUNT_JSON`

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Distribuidor muda layout do site, quebrando seletores CSS | alto | alto | Versionamento de seletores em config separada; detecção automática de quebra (zero produtos = alerta); fallback CSV | 
| CAPTCHA ou anti-bot em distribuidor | alto | médio | Detecção de CAPTCHA no fluxo; abortar com mensagem clara; sugerir importação manual |
| Playwright headless detectado como bot | médio | médio | Stealth plugin (`playwright-stealth`); user-agent rotation; delays humanos entre ações |
| Rate limiting do Backblaze B2 | baixo | baixo | Upload em batch com throttle; retry com backoff |
| Supabase connection pool esgotado durante extração paralela | médio | baixo | Limitar conexões por conector; usar connection pooler do Supabase (pgBouncer) |
| Credenciais do distribuidor mudam sem aviso | alto | médio | Health check periódico (diário); alerta imediato ao vendedor |
| Imagem Docker pesada (Playwright ~1.5GB) | baixo | alto (é certo) | Multi-stage build; cache de layers; single browser (chromium only) |

## 10. Critério de pronto

- [ ] Interface `BaseConnector` implementada com testes unitários
- [ ] Pelo menos 2 conectores RPA funcionais (DPK + Furacão) com extração end-to-end
- [ ] Conector L'Aquila (Drive) funcional
- [ ] API REST para CRUD de distribuidores + execução + logs
- [ ] Fotos armazenadas no Backblaze B2 e acessíveis via URL pública/signed
- [ ] Tabelas criadas no Supabase com RLS ativo
- [ ] Container Docker rodando via Coolify na VPS Hetzner
- [ ] Subdomínio Cloudflare configurado e acessível via HTTPS
- [ ] Log de execução consultável via API
- [ ] Teste de credenciais ("Testar conexão") funcional para todos os conectores implementados
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-10 | Versão inicial gerada por `/reversa-plan` | reversa |
