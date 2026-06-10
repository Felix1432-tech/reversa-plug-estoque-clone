# Requirements: Conectores de Distribuidores

> Identificador: `001-conectores-distribuidores`
> Data: `2026-06-10`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Arquitetura modular de conectores que extrai catálogo (SKU, fotos, descrição, peso, medidas, preço, dados fiscais) e estoque de 7 distribuidores brasileiros. Cada distribuidor tem um conector independente com interface padronizada. Suporta 3 tipos de fonte: RPA/scraping com login, Google Drive API e importação manual de planilha (fallback). É o componente fundamental da plataforma — sem dados dos distribuidores, nenhum outro módulo funciona.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/sdd/conectores-distribuidores.md#resumo` | Arquitetura modular, 3 tipos de fonte, interface padronizada Connector | 🟡 |
| `_reversa_sdd/prd.md#escopo` | 6 distribuidores mapeados: DPK, Furacão, RUFATO, ISAPA, Pellegrino (RPA), L'Aquila (Drive) | 🟡 |
| `_reversa_sdd/prd.md#dependencias-externas` | Sites autenticados com login/senha + Google Drive API | 🟡 |
| `_reversa_sdd/ideation.md#notas` | +Rolemarmaster (RPA, sem estoque) — adicionado durante pipeline | 🟡 |
| `_reversa_sdd/sdd/conectores-distribuidores.md#modelo-dados` | Entidades: DistributorConfig, Product, ConnectorLog | 🟡 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| 🟡 Vendedor solo iniciante | Importar catálogo de distribuidores para começar a vender sem estoque | Configura credenciais do DPK, roda extração, vê produtos no catálogo unificado |
| 🟡 Vendedor multi-conta | Escalar operação com múltiplos distribuidores em paralelo | Configura 7 distribuidores, monitora logs de extração, usa fallback quando conector falha |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** Todo conector deve implementar a interface padrão `Connector` com métodos: `authenticate()`, `fetch_catalog()`, `fetch_stock()`, `health_check()` 🟡
   - Origem: `_reversa_sdd/sdd/conectores-distribuidores.md#RF-01`
   - Tipo: nova

2. **RN-02:** Credenciais dos distribuidores (login/senha) devem ser armazenadas criptografadas (AES-256 at rest) 🟡
   - Origem: `_reversa_sdd/sdd/conectores-distribuidores.md#RF-09`
   - Tipo: nova

3. **RN-03:** Produtos removidos do catálogo do distribuidor são marcados como "indisponível" (soft delete), nunca removidos do banco 🟡
   - Origem: `_reversa_sdd/sdd/conectores-distribuidores.md#decisoes`
   - Tipo: nova

4. **RN-04:** Fotos dos produtos devem ser baixadas e armazenadas localmente para independência do site do distribuidor 🟡
   - Origem: `_reversa_sdd/sdd/conectores-distribuidores.md#RF-12`
   - Tipo: nova

5. **RN-05:** Conectores executam de forma isolada — falha em um não afeta os demais 🟡
   - Origem: `_reversa_sdd/sdd/conectores-distribuidores.md#RNF-03`
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | O sistema deve implementar interface padrão `Connector` com `authenticate()`, `fetch_catalog()`, `fetch_stock()`, `health_check()` | Must | Todos os conectores implementam a mesma interface; são intercambiáveis | 🟡 |
| RF-02 | O sistema deve ter conector RPA para DPK (dpk.com.br) que extrai: SKU, nome, descrição, fotos, preço, estoque, peso, medidas | Must | Extração de ≥100 SKUs em uma execução com dados completos | 🟡 |
| RF-03 | O sistema deve ter conector RPA para Furacão (vendas.furacao.com.br) com mesmo escopo | Must | Mesmo critério do RF-02 | 🟡 |
| RF-04 | O sistema deve ter conector RPA para RUFATO com login/senha | Must | Extração de catálogo disponível no site | 🟡 |
| RF-05 | O sistema deve ter conector RPA para ISAPA com login/senha | Must | Extração de catálogo disponível no site | 🟡 |
| RF-06 | O sistema deve ter conector RPA para Pellegrino (compreonline.pellegrino.com.br) — fotos e descrição; estoque indisponível inicialmente | Must | Fotos e descrição extraídas; campo estoque = null | 🟡 |
| RF-07 | O sistema deve ter conector Google Drive para L'Aquila — fotos, preços, descrição, dados fiscais | Must | Dados lidos de pasta/planilha compartilhada no Drive | 🟡 |
| RF-08 | O sistema deve ter conector RPA para Rolemarmaster (rolemarmaster.com) — login/senha, sem estoque | Should | Catálogo extraído; estoque = null | 🟡 |
| RF-09 | O sistema deve permitir importação manual via CSV/Excel como fallback | Should | Upload gera produtos com mapeamento de colunas configurável | 🟡 |
| RF-10 | O sistema deve armazenar credenciais criptografadas (AES-256) | Must | Credenciais nunca expostas em logs, API ou frontend | 🟡 |
| RF-11 | O sistema deve permitir testar credenciais antes de salvar ("Testar conexão") | Must | Botão retorna sucesso/falha em ≤30 segundos | 🟡 |
| RF-12 | O sistema deve registrar log detalhado por execução (início, fim, SKUs, erros) | Must | Histórico das últimas 30 execuções consultável pelo vendedor | 🟡 |
| RF-13 | O sistema deve baixar e armazenar fotos localmente (object storage) | Should | Fotos disponíveis mesmo quando site do distribuidor está fora | 🟡 |
| RF-14 | O sistema deve normalizar dados de todos os distribuidores para formato padrão `ProductData` | Must | Schema único independente da fonte | 🟡 |
| RF-15 | O sistema deve fazer upsert: novo produto → insert; existente → update campos alterados | Must | Sem duplicatas; histórico de mudanças preservado | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Extração completa de catálogo em < 10 min por distribuidor | Depende do tamanho do catálogo e velocidade do site | 🟡 |
| Resiliência | 3 tentativas com backoff exponencial (5s, 15s, 45s) em falha de rede | Padrão de retry para scraping | 🟡 |
| Isolamento | Cada conector roda em container Docker independente | Deploy via Portainer/Coolify nas VPS Hetzner | 🟢 |
| Segurança | Credenciais criptografadas AES-256 at rest, nunca logadas | Credenciais de terceiros são alto risco | 🟡 |
| Observabilidade | Log por execução com contadores (novos, atualizados, erros) | Necessário para debug e monitoramento | 🟡 |
| Storage | Fotos de produtos armazenadas em Backblaze B2 (S3-compatible) | Independência do site do distribuidor; CDN via Cloudflare | 🟢 |
| Banco de dados | Supabase (Postgres gerenciado) para todas as entidades | Infraestrutura existente do projeto | 🟢 |
| Deploy | Containers Docker via Coolify/Portainer em VPS Hetzner | Deploy automatizado com subdomínios Cloudflare | 🟢 |
| DNS/SSL | Subdomínio dedicado via Cloudflare (ex: api.dominio.com) | SSL automático, proteção DDoS | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Extração bem-sucedida do catálogo DPK
  Dado que o conector DPK está configurado com credenciais válidas
  Quando o sistema executa fetch_catalog()
  Então pelo menos 100 produtos são importados com SKU, nome, descrição, foto, preço e estoque preenchidos

Cenário: Falha de login no distribuidor
  Dado que as credenciais do Furacão estão inválidas
  Quando o sistema executa authenticate()
  Então o status do conector muda para "error" e o vendedor recebe notificação "Login falhou no distribuidor Furacão"

Cenário: Produto removido do catálogo do distribuidor
  Dado que o produto SKU-123 existia na extração anterior
  Quando a nova extração não encontra SKU-123
  Então o produto é marcado como "indisponível" (soft delete) e anúncios associados são sinalizados

Cenário: Site do distribuidor mudou layout
  Dado que os seletores CSS do conector Pellegrino não encontram elementos
  Quando o sistema executa fetch_catalog()
  Então a execução é marcada como "error", log detalhado é registrado, e vendedor é notificado com sugestão de importação manual

Cenário: Importação manual via CSV
  Dado que o conector automático falhou
  Quando o vendedor faz upload de CSV com colunas SKU, nome, preço, estoque
  Então os produtos são importados no catálogo do distribuidor selecionado após mapeamento de colunas
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 Interface Connector | Must | Fundação da arquitetura modular |
| RF-02 Conector DPK | Must | Distribuidor com dados mais completos, ideal para validação |
| RF-03 Conector Furacão | Must | Segundo distribuidor com dados completos |
| RF-04 Conector RUFATO | Must | Já referenciado no Plug Estoque original |
| RF-05 Conector ISAPA | Must | Já referenciado no Plug Estoque original |
| RF-06 Conector Pellegrino | Must | Fotos e descrição são o mínimo viável |
| RF-07 Conector L'Aquila (Drive) | Must | Tipo diferente de fonte, valida a modularidade |
| RF-08 Conector Rolemarmaster | Should | Adicionado depois; pode esperar segunda iteração |
| RF-09 Importação CSV | Should | Fallback importante mas não bloqueia MVP |
| RF-10 Criptografia de credenciais | Must | Segurança básica obrigatória |
| RF-14 Normalização ProductData | Must | Sem schema único, catálogo unificado não funciona |
| RNF Isolamento de conectores | Should | Importante para estabilidade mas MVP pode tolerar execução sequencial |

## 9. Esclarecimentos

### Sessão 2026-06-10

- **Q:** Qual é a estrutura do Google Drive da L'Aquila?
  **R:** Pasta compartilhada acessível via link: `https://drive.google.com/drive/folders/1fTGWuCD_gB8xj8dveddGE-2XDZOoh1jW`. Estrutura interna a ser mapeada durante implementação do conector. Usuário tem acesso completo.

- **Q:** Quais são as URLs de login de RUFATO e ISAPA?
  **R:** Usuário possui login e senha de todos os distribuidores. URLs específicas dos portais serão fornecidas durante a implementação de cada conector. Não é bloqueante para o planejamento.

- **Q:** Qual stack técnica para os conectores RPA?
  **R:** Python (FastAPI para backend + Playwright para RPA). Decisão baseada em: Playwright é superior para automação web, FastAPI é performático e assíncrono, Python tem excelente suporte a Google Drive API. Frontend a definir (React recomendado).

- **Q:** Qual a infraestrutura de deploy e armazenamento?
  **R:** Infraestrutura confirmada pelo usuário:
  - **Compute:** 2 VPS Hetzner com Docker + Portainer
  - **Deploy:** Hostinger com Coolify para deploy automatizado
  - **DNS/SSL:** Cloudflare (subdomínios ilimitados, SSL, proteção DDoS)
  - **Object Storage:** Backblaze B2 (S3-compatible) para fotos de produtos e backups
  - **Banco de dados:** Supabase (Postgres gerenciado)
  - **Containers:** Arquitetura Docker-first, deploy via Portainer e Coolify

## 10. Lacunas

> Todas as dúvidas da versão inicial foram resolvidas na sessão de 2026-06-10. Nenhuma lacuna bloqueante restante.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-06-10 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-06-10 | Esclarecimentos: Drive L'Aquila, credenciais distribuidores, stack técnica (Python/FastAPI/Playwright) | reversa-clarify |
| 2026-06-10 | Infraestrutura de produção: Hetzner VPS, Coolify, Cloudflare, Backblaze B2, Supabase. RNFs atualizados. | reversa-clarify |
