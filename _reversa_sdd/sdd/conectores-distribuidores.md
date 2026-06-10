# Spec: Conectores de Distribuidores

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Arquitetura modular de conectores que extrai dados de catálogo (SKU, fotos, descrição, peso, medidas, preço, dados fiscais) e estoque dos distribuidores. Cada distribuidor tem um conector independente. Suporta 3 tipos de fonte: RPA/scraping com login, Google Drive API e importação manual de planilha (fallback).

---

## 2. Contexto e Motivação

**Problema:**
🟡 Cada distribuidor disponibiliza seu catálogo de forma diferente (site autenticado, Google Drive, planilha). Não há API padronizada. O vendedor precisa acessar cada um manualmente para consultar produtos e estoque.

**Evidências:**
🟡 6 distribuidores mapeados, cada um com formato diferente de acesso:
- DPK, Furacão, RUFATO, ISAPA, Pellegrino → sites com login/senha
- L'Aquila → Google Drive com fotos, preços, descrição e dados fiscais

**Por que agora:**
🟡 Componente fundamental — sem dados dos distribuidores, não há catálogo, não há anúncios, não há plataforma.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Extrair catálogo completo (SKU, nome, descrição, fotos, peso, medidas, preço, dados fiscais) de cada distribuidor
- [ ] 🟡 G-02: Extrair nível de estoque atual de cada SKU (quando disponível)
- [ ] 🟡 G-03: Arquitetura modular onde cada conector é independente — adicionar ou remover distribuidor não afeta os demais
- [ ] 🟡 G-04: Fallback para importação manual (CSV/Excel) quando automação falha

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Distribuidores com conector funcional | 🟡 0 | 🟡 4 (DPK, Furacão, Pellegrino, L'Aquila) | 🟡 MVP |
| 🟡 Taxa de sucesso de extração por execução | 🟡 N/A | 🟡 > 95% | 🟡 MVP |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Fazer pedido de compra automaticamente no distribuidor (o vendedor compra manualmente após venda)
- 🟡 NG-02: Negociar preços ou condições com o distribuidor via plataforma
- 🟡 NG-03: Monitoramento de estoque em tempo real via webhook (distribuidores não oferecem isso) — polling é o padrão
- 🟡 NG-04: Tratamento de CAPTCHAs sofisticados (se distribuidor implementar, fallback para importação manual)

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Vendedor (ambas personas) — configura credenciais do distribuidor e seleciona quais distribuidores ativar.

**Jornada atual (sem a feature):**
🟡 Vendedor acessa site de cada distribuidor, faz login, navega manualmente, copia dados de produto um a um.

**Jornada futura (com a feature):**
1. 🟡 Vendedor configura credenciais do distribuidor na plataforma
2. 🟡 Conector extrai catálogo automaticamente
3. 🟡 Produtos aparecem no catálogo unificado prontos para seleção

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve implementar interface padrão `Connector` com métodos: `authenticate()`, `fetch_catalog()`, `fetch_stock()`, `health_check()` | Must | 🟡 Todos os conectores implementam a mesma interface; trocar conector não quebra o sistema |
| 🟡 RF-02 | O sistema deve ter conector RPA para DPK que faz login, navega no catálogo e extrai: SKU, nome, descrição, fotos, preço, estoque, peso, medidas | Must | 🟡 Extração completa de pelo menos 100 SKUs em uma execução |
| 🟡 RF-03 | O sistema deve ter conector RPA para Furacão com mesmo escopo do RF-02 | Must | 🟡 Mesmo critério |
| 🟡 RF-04 | O sistema deve ter conector RPA para RUFATO com login/senha | Must | 🟡 Extração de catálogo disponível no site |
| 🟡 RF-05 | O sistema deve ter conector RPA para ISAPA com login/senha | Must | 🟡 Extração de catálogo disponível no site |
| 🟡 RF-06 | O sistema deve ter conector RPA para Pellegrino que extrai fotos e descrição (estoque indisponível inicialmente) | Must | 🟡 Fotos e descrição extraídas; campo estoque marcado como "indisponível" |
| 🟡 RF-07 | O sistema deve ter conector Google Drive para L'Aquila que lê fotos, preços, descrição e dados fiscais de pasta compartilhada | Must | 🟡 Dados extraídos da estrutura de pastas/planilhas no Drive |
| 🟡 RF-08 | O sistema deve permitir importação manual via CSV/Excel como fallback para qualquer distribuidor | Should | 🟡 Upload de arquivo gera produtos no catálogo com mapeamento de colunas |
| 🟡 RF-09 | O sistema deve armazenar credenciais dos distribuidores de forma segura (criptografadas) | Must | 🟡 Credenciais nunca expostas em logs, API ou frontend |
| 🟡 RF-10 | O sistema deve permitir configurar e testar credenciais de cada distribuidor | Must | 🟡 Botão "Testar conexão" faz login e retorna sucesso/falha em até 30 segundos |
| 🟡 RF-11 | O sistema deve registrar log detalhado de cada execução de conector (início, fim, SKUs extraídos, erros) | Must | 🟡 Log consultável pelo vendedor com histórico das últimas 30 execuções |
| 🟡 RF-12 | O sistema deve baixar e armazenar fotos dos produtos localmente (ou em storage) para não depender do site do distribuidor | Should | 🟡 Fotos disponíveis mesmo quando site do distribuidor está fora do ar |

### 6.2 Fluxo Principal (Happy Path) — Conector RPA

1. 🟡 Scheduler dispara execução do conector DPK
2. 🟡 Conector faz login no site com credenciais armazenadas
3. 🟡 Conector navega pelas páginas de catálogo
4. 🟡 Para cada produto: extrai SKU, nome, descrição, fotos, preço, estoque, peso, medidas
5. 🟡 Dados são normalizados para formato padrão (`ProductData`)
6. 🟡 Sistema faz upsert no banco: novo produto → insert; existente → update campos alterados
7. 🟡 Log de execução registrado com contadores (novos, atualizados, erros)
8. 🟡 Resultado: catálogo do distribuidor atualizado no banco

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Conector Google Drive (L'Aquila):**
1. 🟡 Scheduler dispara execução do conector L'Aquila
2. 🟡 Conector acessa Google Drive via API com service account ou OAuth
3. 🟡 Lê estrutura de pastas (fotos) e planilha (preços, descrição, dados fiscais)
4. 🟡 Normaliza para formato padrão `ProductData`
5. 🟡 Upsert no banco

**Fluxo Alternativo B — Importação manual (fallback):**
1. 🟡 Vendedor acessa "Distribuidores > Importar planilha"
2. 🟡 Faz upload de CSV/Excel
3. 🟡 Sistema detecta colunas e apresenta mapeamento (SKU → coluna A, nome → coluna B, etc.)
4. 🟡 Vendedor confirma mapeamento
5. 🟡 Sistema importa produtos para o catálogo do distribuidor selecionado

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Tempo de extração de catálogo completo | 🟡 < 10 minutos por distribuidor | 🟡 Depende do tamanho do catálogo e velocidade do site |
| 🟡 RNF-02 | Retry em caso de falha de rede | 🟡 3 tentativas com backoff exponencial | 🟡 Delay: 5s, 15s, 45s |
| 🟡 RNF-03 | Execução isolada por conector | 🟡 Falha em um conector não afeta os demais | 🟡 Cada conector roda em processo/container independente |
| 🟡 RNF-04 | Armazenamento de fotos | 🟡 Object storage (S3/MinIO) ou filesystem local | 🟡 Não depender do site do distribuidor para servir fotos |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Página de configuração de distribuidores, card de distribuidor, modal de teste de conexão, tela de importação manual.

**Comportamento esperado:**
🟡 Lista de distribuidores disponíveis. Para cada: status (Configurado/Não configurado/Erro), última execução, SKUs extraídos. Botões: Configurar, Testar, Executar agora, Ver log.

**Estados da UI:**
- 🟡 Estado vazio: "Configure as credenciais dos distribuidores para começar a importar catálogos."
- 🟡 Estado de carregamento: barra de progresso durante extração com contagem de SKUs processados
- 🟡 Estado de erro: badge vermelho com mensagem do erro (ex: "Login falhou", "Site indisponível")
- 🟡 Estado de sucesso: badge verde "Última execução: há X minutos — Y SKUs importados"

---

## 9. Modelo de Dados

🟡

```
DistributorConfig {
  id: UUID                     // identificador único
  user_id: UUID (FK)           // referência ao vendedor
  distributor_type: enum       // "dpk" | "furacao" | "rufato" | "isapa" | "pellegrino" | "laquila"
  credentials: jsonb (enc)     // credenciais criptografadas (login/senha ou OAuth tokens)
  status: enum                 // "configured" | "not_configured" | "error"
  last_sync_at: datetime       // última execução com sucesso
  last_error: text             // último erro (se houver)
  settings: jsonb              // configurações específicas do conector (ex: pasta do Drive)
  created_at: datetime
  updated_at: datetime
}

Product {
  id: UUID                     // identificador único
  distributor_config_id: UUID (FK) // de qual distribuidor veio
  sku: string                  // SKU do distribuidor
  name: string                 // nome do produto
  description: text            // descrição completa
  price: decimal               // preço do distribuidor
  stock_quantity: integer       // estoque atual (null se indisponível)
  weight: decimal              // peso em kg
  height: decimal              // altura em cm
  width: decimal               // largura em cm
  length: decimal              // comprimento em cm
  photos: jsonb                // lista de URLs das fotos armazenadas
  fiscal_data: jsonb           // NCM, GTIN/EAN, etc.
  raw_data: jsonb              // dados brutos originais do distribuidor
  last_stock_check_at: datetime // última verificação de estoque
  created_at: datetime
  updated_at: datetime
  
  UNIQUE(distributor_config_id, sku)
}

ConnectorLog {
  id: UUID
  distributor_config_id: UUID (FK)
  started_at: datetime
  finished_at: datetime
  status: enum                 // "success" | "partial" | "error"
  products_found: integer
  products_created: integer
  products_updated: integer
  errors_count: integer
  error_details: jsonb
}
```

**Migrações necessárias:** 🟡 Sim — criação das tabelas `distributor_configs`, `products` e `connector_logs`.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 Site DPK (dpk.com.br) | 🟡 Obrigatória para conector DPK | 🟡 Catálogo DPK não atualiza; dados existentes continuam disponíveis |
| 🟡 Site Furacão (vendas.furacao.com.br) | 🟡 Obrigatória para conector Furacão | 🟡 Idem |
| 🟡 Site RUFATO | 🟡 Obrigatória para conector RUFATO | 🟡 Idem |
| 🟡 Site ISAPA | 🟡 Obrigatória para conector ISAPA | 🟡 Idem |
| 🟡 Site Pellegrino (compreonline.pellegrino.com.br) | 🟡 Obrigatória para conector Pellegrino | 🟡 Idem |
| 🟡 Google Drive API | 🟡 Obrigatória para conector L'Aquila | 🟡 Idem |
| 🟡 Puppeteer/Playwright | 🟡 Obrigatória para conectores RPA | 🟡 Nenhum conector RPA funciona |
| 🟡 Object Storage (fotos) | 🟡 Should | 🟡 Fotos servidas diretamente do link original (menos confiável) |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: Login falha (credenciais inválidas) | 🟡 Distribuidor mudou senha ou bloqueou conta | 🟡 Marcar conector como "Erro"; notificar vendedor: "Login falhou no distribuidor X. Verifique suas credenciais." |
| 🟡 EC-02: Site do distribuidor mudou layout | 🟡 Seletores CSS/XPath não encontram elementos | 🟡 Registrar erro detalhado no log; marcar execução como "partial" ou "error"; notificar vendedor |
| 🟡 EC-03: CAPTCHA detectado | 🟡 Distribuidor implementou proteção anti-bot | 🟡 Abortar conector com mensagem clara; sugerir importação manual como fallback |
| 🟡 EC-04: Timeout de rede | 🟡 Site do distribuidor lento ou fora do ar | 🟡 Retry com backoff exponencial (3x); se persistir, registrar erro e prosseguir com dados existentes |
| 🟡 EC-05: Produto removido do catálogo do distribuidor | 🟡 SKU existia antes mas não aparece na nova extração | 🟡 Marcar como "indisponível" (soft delete); não remover do banco; pausar anúncios associados |
| 🟡 EC-06: Foto não carrega | 🟡 URL da foto retorna 404 ou timeout | 🟡 Manter foto anterior se existir; registrar no log; produto continua disponível sem foto atualizada |
| 🟡 EC-07: Dados fiscais ausentes | 🟡 Distribuidor não fornece NCM/EAN | 🟡 Campo fica null; vendedor pode preencher manualmente; alerta ao publicar anúncio sem dados fiscais |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** Vendedor deve estar logado para configurar e executar conectores
- 🟡 **Autorização:** Vendedor só acessa seus próprios conectores
- 🟡 **Dados sensíveis:** Credenciais dos distribuidores (login/senha) criptografadas AES-256 at rest; nunca logadas ou expostas
- 🟡 **Auditoria:** Registrar: configuração de credenciais, execuções de conector, erros

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** Conectores entregues incrementalmente (DPK primeiro, depois demais)
- 🟡 **Como reverter:** Desabilitar conector específico; dados já importados permanecem
- 🟡 **Monitoramento pós-deploy:** Taxa de sucesso por conector, tempo de extração, alertas de falha

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | Qual a estrutura exata de pastas/planilha do Google Drive da L'Aquila? | 🟡 Alto | 🟡 Sandeco | 🟡 Antes do MVP |
| 🟡 OQ-02 | RUFATO e ISAPA — qual a URL do portal de login e estrutura do catálogo? | 🟡 Alto | 🟡 Sandeco | 🟡 Antes do MVP |
| 🟡 OQ-03 | Automação de estoque do Pellegrino — polling com que frequência? | 🟡 Médio | 🟡 Sandeco | 🟡 Pós-MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 Arquitetura de conectores modulares (interface padrão) | 🟡 Monolito com if/else por distribuidor | 🟡 Modular permite adicionar/remover distribuidores sem risco; cada conector é testável isoladamente |
| 🟡 RPA/Scraping como método primário | 🟡 Esperar APIs oficiais | 🟡 Distribuidores não oferecem APIs; scraping é viável com login/senha próprio |
| 🟡 Armazenamento local de fotos | 🟡 Hotlinking para site do distribuidor | 🟡 Evita dependência; fotos continuam disponíveis se site cair; necessário para publicar em marketplaces |
| 🟡 Soft delete de produtos removidos | 🟡 Hard delete | 🟡 Produto pode ter anúncios ativos; soft delete permite pausar anúncio sem perder histórico |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`
- 🟡 DPK: https://www.dpk.com.br/#/
- 🟡 Furacão: https://vendas.furacao.com.br/vendas/sav/produtos
- 🟡 Pellegrino: https://compreonline.pellegrino.com.br/
- 🟡 L'Aquila: https://www.laquila.com.br/

### Histórico de Revisões
| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-06-10 | reversa-spec-sdd | Criação inicial |

---

## Relatório de Avaliação

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORE TOTAL: 91/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Breakdown:
  Completude:    93/100 (peso 30%)
  Testabilidade: 90/100 (peso 25%)
  Clareza:       90/100 (peso 20%)
  Escopo:        90/100 (peso 15%)
  Edge Cases:    90/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Mapear estrutura exata do Drive L'Aquila (OQ-01) e portais RUFATO/ISAPA (OQ-02) antes da implementação
  2. Definir estratégia de versionamento de seletores CSS para detectar quebras de layout cedo
```
