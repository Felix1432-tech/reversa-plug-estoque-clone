# PRD: Plug Estoque Clone

> Selo 🟡 PLANEJADO. Documento gerado a partir de ideation + personas.

**Versão:** 1.0
**Data:** 2026-06-10T00:00:00-03:00
**Autor:** reversa-drafter
**Status:** rascunho

---

## 1. Problema

🟡 Vendedores de marketplace querem operar no modelo cross-docking (vender primeiro, comprar depois) sem investir em estoque próprio. Hoje, para fazer isso, precisam:
- Acessar manualmente os sites de cada distribuidor para consultar catálogo e estoque
- Copiar dados de produtos (SKU, fotos, descrição, peso, medidas) um a um
- Criar anúncios manualmente em cada marketplace
- Monitorar estoque dos distribuidores para não vender produto indisponível
- Gerenciar múltiplas contas e marketplaces em abas separadas

Esse processo manual limita a escala, gera erros (venda sem estoque) e consome tempo que poderia ser usado para crescer o negócio.

### Quem sente

🟡 **Vendedor solo iniciante** — CLT que quer renda extra vendendo online mas não tem capital para estoque. Sente o problema ao tentar começar: a barreira de entrada é alta demais sem uma ferramenta que automatize a operação.

🟡 **Vendedor multi-conta** — Já opera no Mercado Livre com várias contas e quer escalar. Sente o problema diariamente: gerenciar distribuidores, anúncios e pedidos em múltiplas contas manualmente é insustentável acima de certo volume.

---

## 2. Personas-alvo

🟡 Referência completa em [`personas.md`](./personas.md). Resumo:

- **Vendedor solo iniciante**: 🟡 CLT buscando renda extra, iniciante em e-commerce, precisa de ferramenta simples que elimine a barreira de investimento em estoque
- **Vendedor multi-conta**: 🟡 Vendedor experiente com múltiplas contas no ML, avançado, precisa de painel unificado para escalar operação sem perder controle

---

## 3. Métricas de sucesso

🟡

| Métrica | Unidade | Alvo | Prazo |
|---|---|---|---|
| 🟡 Anúncios ativos nos marketplaces | 🟡 quantidade | 🟡 500 | 🟡 3 meses |
| 🟡 Limite de anúncios na plataforma | 🟡 booleano | 🟡 Sem limite artificial | 🟡 desde o MVP |
| 🟡 Distribuidores integrados | 🟡 quantidade | 🟡 6 (DPK, Furacão, Pellegrino, L'Aquila, RUFATO, ISAPA) | 🟡 3 meses |
| 🟡 Marketplaces suportados | 🟡 quantidade | 🟡 2 (Mercado Livre + Shopee) no MVP | 🟡 3 meses |

---

## 4. Escopo (in)

🟡 Funcionalidades incluídas no MVP:

- 🟡 **Autenticação e gestão de conta** — cadastro, login, gerenciamento de perfil
- 🟡 **Multi-conta marketplace** — conectar e gerenciar múltiplas contas do Mercado Livre, Shopee (Amazon e TikTok pós-MVP)
- 🟡 **Conectores de distribuidores (arquitetura modular):**
  - 🟡 DPK — conector via RPA/scraping com login (SKU + estoque completo)
  - 🟡 Furacão — conector via RPA/scraping com login (SKU + estoque completo)
  - 🟡 RUFATO — conector via RPA/scraping com login
  - 🟡 ISAPA — conector via RPA/scraping com login
  - 🟡 Pellegrino — conector via RPA/scraping com login (fotos + descrição; estoque via automação futura)
  - 🟡 L'Aquila — conector via Google Drive API (fotos + preços + descrição + dados fiscais)
- 🟡 **Catálogo unificado** — visualização consolidada dos produtos de todos os distribuidores com busca e filtros
- 🟡 **Seleção em massa e publicação gradual** — selecionar SKUs em lote, publicar aos poucos (throttling) para evitar bloqueio dos marketplaces
- 🟡 **Importação de dados do produto** — puxar do distribuidor: SKU, fotos, descrição, clip, peso, medidas, dados fiscais
- 🟡 **Configuração de margem** — definir markup por produto, categoria ou lote
- 🟡 **Monitoramento de estoque** — polling periódico do estoque do distribuidor; pausa automática do anúncio quando estoque zera ou fica abaixo do limite
- 🟡 **Gestão de anúncios** — listar, editar, pausar, reativar anúncios publicados
- 🟡 **Gestão de pedidos** — receber pedido do marketplace, encaminhar ao distribuidor, acompanhar status
- 🟡 **Dashboard** — visão consolidada de vendas, lucro, anúncios ativos, estoque crítico, performance por conta/marketplace

---

## 5. Não-objetivos (out)

🟡 Explicitamente FORA do escopo do MVP:

- 🟡 App mobile nativo (web responsivo é suficiente)
- 🟡 Sistema financeiro/fiscal completo (emissão de NF, contabilidade)
- 🟡 Logística própria (depende do distribuidor despachar)
- 🟡 Chat com cliente final do marketplace
- 🟡 Análise de concorrentes (feature futura)
- 🟡 Clonagem de anúncios de terceiros
- 🟡 Marketplace Amazon e TikTok (pós-MVP)
- 🟡 Modelo SaaS multi-tenant (primeiro uso próprio, SaaS depois)

---

## 6. Restrições

🟡

| Tipo | Descrição |
|---|---|
| 🟡 Técnica | 🟡 [INDEFINIDO, validar com usuário] — stack não definida |
| 🟡 Prazo | 🟡 3 meses para 500 anúncios ativos |
| 🟡 Compliance | 🟡 Termos de uso dos marketplaces (limites de publicação em massa); termos de uso dos sites dos distribuidores (scraping) |
| 🟡 Orçamento | 🟡 [INDEFINIDO, validar com usuário] |

---

## 7. Dependências externas

🟡 Serviços, APIs e dados externos dos quais o produto depende:

- 🟡 **API Mercado Livre** — publicação de anúncios, gestão de pedidos, webhooks de venda
- 🟡 **API Shopee** — publicação de anúncios, gestão de pedidos
- 🟡 **Sites dos distribuidores (acesso autenticado com login/senha):**
  - 🟡 DPK (dpk.com.br) — catálogo + estoque completo
  - 🟡 Furacão (vendas.furacao.com.br) — catálogo + estoque completo
  - 🟡 RUFATO — catálogo via RPA/scraping com login
  - 🟡 ISAPA — catálogo via RPA/scraping com login
  - 🟡 Pellegrino (compreonline.pellegrino.com.br) — fotos + descrição (estoque via automação futura)
- 🟡 **Google Drive API** — acesso ao catálogo L'Aquila (fotos, preços, descrição, dados fiscais)
- 🟡 **Serviço de scraping/RPA** — Puppeteer, Playwright ou similar para extração de dados dos distribuidores

---

## 8. Riscos

🟡

| Risco | Impacto | Probabilidade | Mitigação proposta |
|---|---|---|---|
| 🟡 Distribuidores mudarem layout/estrutura do site | 🟡 Alto — quebra a importação de catálogo | 🟡 Média | 🟡 Conectores modulares independentes; alertas de falha; fallback para importação manual (planilha) |
| 🟡 Marketplaces bloquearem publicação em massa | 🟡 Alto — anúncios não sobem | 🟡 Média | 🟡 Throttling controlado: seleção em massa, publicação gradual com delays configuráveis |
| 🟡 SLA de envio do distribuidor incompatível com marketplace | 🟡 Alto — reputação do vendedor cai | 🟡 Baixa | 🟡 Filtrar distribuidores por prazo de envio; alertas quando prazo excede limite do marketplace |
| 🟡 Credenciais do distribuidor expirarem ou 2FA bloquear | 🟡 Médio — conector para de funcionar | 🟡 Alta | 🟡 Alertas de sessão expirada; re-autenticação manual simplificada |
| 🟡 Termos de uso proibirem scraping | 🟡 Médio — risco legal | 🟡 Baixa (uso próprio) | 🟡 Uso restrito a conta própria; migrar para API quando disponível |

---

## 9. Critérios de aceite (alto nível)

🟡 Critérios para validar o MVP como funcional:

- 🟡 **Dado** um vendedor solo iniciante sem estoque, **Quando** ele acessa o catálogo do distribuidor DPK na plataforma e seleciona 50 SKUs, **Então** os 50 anúncios são publicados no Mercado Livre com fotos, descrição, peso e preço com margem configurada, de forma gradual (sem bloqueio).

- 🟡 **Dado** um vendedor multi-conta com 3 contas no Mercado Livre, **Quando** o estoque de um produto zera no distribuidor Furacão, **Então** os anúncios desse produto são pausados automaticamente em todas as contas em até 30 minutos.

- 🟡 **Dado** um vendedor com produtos publicados, **Quando** ele acessa o dashboard, **Então** vê consolidado: total de anúncios ativos, vendas do dia, lucro estimado e alertas de estoque crítico, por conta e por marketplace.

- 🟡 **Dado** um vendedor que recebe uma venda no Mercado Livre, **Quando** o pedido entra na plataforma, **Então** o sistema identifica o distribuidor correto e apresenta os dados para encaminhamento do pedido.

---

## Pendências de cobertura

🟡 Itens que precisam de validação humana antes do próximo passo:

1. 🟡 **Stack técnica** — linguagem, framework frontend/backend, banco de dados, hospedagem não definidos
2. 🟡 **Orçamento** — sem limite definido para infraestrutura e ferramentas
3. 🟡 **Estoque Pellegrino** — automação de atualização de estoque a definir (polling? webhook? manual?)
4. 🟡 **Frequência de polling** — de quanto em quanto tempo o sistema verifica estoque nos distribuidores

---

Gerado por reversa-drafter em 2026-06-10T00:00:00-03:00
Fontes: ideation.md, personas.md
