# Spec: Gestão de Pedidos

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Módulo que recebe pedidos dos marketplaces, identifica o distribuidor correto, apresenta os dados para o vendedor encaminhar a compra, e acompanha o status de envio. Centraliza todos os pedidos de todas as contas em um painel único.

---

## 2. Contexto e Motivação

**Problema:**
🟡 No modelo cross-docking, cada venda gera um pedido que o vendedor precisa repassar manualmente ao distribuidor. Com múltiplas contas e múltiplos distribuidores, rastrear quem fornece o quê e qual o status de cada pedido vira caos.

**Evidências:**
🟡 Jornada Persona 1 (passo 5): "Receber notificação de venda e encaminhar pedido ao distribuidor". Jornada Persona 2 (passo 5): "Receber pedidos centralizados e despachar para o distribuidor correto".

**Por que agora:**
🟡 Sem gestão de pedidos, a operação pós-venda é manual e não escala.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Receber pedidos do Mercado Livre e Shopee automaticamente
- [ ] 🟡 G-02: Identificar automaticamente o distribuidor de cada item do pedido
- [ ] 🟡 G-03: Centralizar todos os pedidos de todas as contas em painel único
- [ ] 🟡 G-04: Permitir rastrear status do pedido (novo → comprado no distribuidor → enviado → entregue)

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Pedidos processados automaticamente | 🟡 N/A | 🟡 100% dos pedidos recebidos aparecem no painel | 🟡 MVP |
| 🟡 Tempo entre venda e visualização no painel | 🟡 N/A | 🟡 < 5 minutos | 🟡 MVP |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Compra automática no distribuidor (vendedor faz manualmente)
- 🟡 NG-02: Geração de nota fiscal
- 🟡 NG-03: Gestão de devoluções/trocas
- 🟡 NG-04: Chat com comprador
- 🟡 NG-05: Cálculo de frete (marketplace gerencia)

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Ambas personas — solo gerencia poucos pedidos; multi-conta gerencia alto volume.

**Jornada futura (com a feature):**
1. 🟡 Venda acontece no marketplace
2. 🟡 Sistema recebe webhook/polling e registra pedido
3. 🟡 Vendedor vê pedido no painel com dados do distribuidor
4. 🟡 Vendedor compra no distribuidor e marca como "Comprado"
5. 🟡 Vendedor adiciona código de rastreio e marca como "Enviado"

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve receber pedidos do ML via webhooks (notifications API) ou polling | Must | 🟡 Pedido aparece no painel em até 5 minutos após venda |
| 🟡 RF-02 | O sistema deve receber pedidos do Shopee via webhooks ou polling | Must | 🟡 Mesmo critério |
| 🟡 RF-03 | O sistema deve identificar automaticamente o distribuidor de cada item usando vínculo product → distributor | Must | 🟡 Coluna "Distribuidor" preenchida automaticamente no pedido |
| 🟡 RF-04 | O sistema deve exibir lista de pedidos com: data, marketplace, conta, comprador, itens, valor, status, distribuidor | Must | 🟡 Lista paginada com filtros por status, marketplace, conta, data |
| 🟡 RF-05 | O sistema deve permitir atualizar status do pedido: Novo → Comprado → Enviado → Entregue | Must | 🟡 Vendedor muda status manualmente; timestamp registrado |
| 🟡 RF-06 | O sistema deve permitir adicionar código de rastreio e atualizar no marketplace | Must | 🟡 Código de rastreio enviado ao ML/Shopee via API; comprador recebe atualização |
| 🟡 RF-07 | O sistema deve exibir dados do distribuidor no pedido para facilitar a compra (nome do distribuidor, SKU original, preço do distribuidor) | Must | 🟡 Vendedor vê claramente onde comprar e quanto vai pagar |
| 🟡 RF-08 | O sistema deve calcular e exibir lucro estimado por pedido (preço de venda - preço do distribuidor - taxas do marketplace) | Should | 🟡 Valor aproximado; taxa do marketplace pode ser estimada |
| 🟡 RF-09 | O sistema deve notificar vendedor sobre novos pedidos via painel | Must | 🟡 Badge de notificação com contagem de pedidos novos |

### 6.2 Fluxo Principal (Happy Path)

1. 🟡 Comprador faz pedido no Mercado Livre
2. 🟡 ML envia webhook para o sistema
3. 🟡 Sistema registra pedido com dados: comprador, itens, endereço, valor
4. 🟡 Sistema identifica distribuidor pelo vínculo product_listing → product → distributor_config
5. 🟡 Pedido aparece no painel com status "Novo" e dados do distribuidor
6. 🟡 Vendedor acessa site do distribuidor, faz a compra manualmente
7. 🟡 Vendedor marca pedido como "Comprado" no painel
8. 🟡 Distribuidor envia produto; vendedor recebe código de rastreio
9. 🟡 Vendedor adiciona código de rastreio no painel → sistema envia ao ML
10. 🟡 Pedido marcado como "Enviado"
11. 🟡 Resultado: comprador recebe rastreio, vendedor tem controle total

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Pedido com múltiplos itens de distribuidores diferentes:**
1. 🟡 Pedido contém item A (DPK) e item B (Furacão)
2. 🟡 Sistema exibe ambos distribuidores no pedido
3. 🟡 Vendedor compra em cada distribuidor separadamente
4. 🟡 Pode precisar consolidar envio — sinalizado como alerta

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Latência de recebimento de pedido | 🟡 < 5 minutos via webhook; < 15 minutos via polling | 🟡 Webhook preferencial |
| 🟡 RNF-02 | Retenção de pedidos | 🟡 12 meses | 🟡 Histórico para análise de lucro |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Lista de pedidos, detalhe do pedido, modal de código de rastreio, notificações.

**Estados da UI:**
- 🟡 Sem pedidos: "Nenhum pedido recebido ainda. Seus pedidos aparecerão aqui automaticamente."
- 🟡 Pedido novo: badge "Novo" em destaque, com dados do distribuidor visíveis
- 🟡 Pedido em andamento: timeline visual (Novo → Comprado → Enviado → Entregue)
- 🟡 Erro: "Falha ao atualizar rastreio no marketplace. Tente novamente."

---

## 9. Modelo de Dados

🟡

```
Order {
  id: UUID
  user_id: UUID (FK)
  marketplace_account_id: UUID (FK)
  marketplace_order_id: string        // ID do pedido no marketplace
  marketplace: enum                   // "mercado_livre" | "shopee"
  buyer_name: string
  buyer_address: jsonb                // endereço de entrega
  total_amount: decimal               // valor total pago pelo comprador
  marketplace_fee: decimal            // taxa do marketplace (estimada)
  status: enum                        // "new" | "purchased" | "shipped" | "delivered" | "cancelled"
  tracking_code: string               // código de rastreio
  notes: text                         // notas do vendedor
  received_at: datetime               // quando o pedido foi recebido
  purchased_at: datetime              // quando o vendedor comprou no distribuidor
  shipped_at: datetime                // quando marcou como enviado
  delivered_at: datetime
  created_at: datetime
  updated_at: datetime
}

OrderItem {
  id: UUID
  order_id: UUID (FK)
  product_id: UUID (FK)              // vínculo com produto do catálogo
  product_listing_id: UUID (FK)      // vínculo com anúncio
  distributor_config_id: UUID (FK)   // distribuidor deste item
  quantity: integer
  sale_price: decimal                // preço de venda (com margem)
  distributor_price: decimal         // preço do distribuidor
  estimated_profit: decimal          // sale_price - distributor_price - estimated_fee
}
```

**Migrações necessárias:** 🟡 Sim — criação das tabelas `orders` e `order_items`.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 API ML (orders, shipments) | 🟡 Obrigatória | 🟡 Pedidos ML não são recebidos; polling como fallback |
| 🟡 API Shopee (orders) | 🟡 Obrigatória | 🟡 Pedidos Shopee não são recebidos |
| 🟡 Catálogo (products, product_listings) | 🟡 Obrigatória | 🟡 Sem vínculo, distribuidor não é identificado automaticamente |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: Pedido de produto sem vínculo com distribuidor | 🟡 Anúncio criado manualmente fora da plataforma | 🟡 Pedido registrado com distribuidor "Não identificado"; vendedor resolve manualmente |
| 🟡 EC-02: Webhook não chega | 🟡 Falha no webhook do ML | 🟡 Polling de backup a cada 15 minutos busca pedidos novos |
| 🟡 EC-03: Pedido cancelado pelo comprador | 🟡 Cancelamento no marketplace | 🟡 Status atualizado para "Cancelado"; se já comprou no distribuidor, alerta ao vendedor |
| 🟡 EC-04: Múltiplos itens de distribuidores diferentes | 🟡 Pedido com mix de fornecedores | 🟡 Alerta: "Pedido com itens de distribuidores diferentes — pode exigir envios separados" |
| 🟡 EC-05: Falha ao enviar código de rastreio ao marketplace | 🟡 API do marketplace indisponível | 🟡 Retry em 5 min; rastreio salvo localmente; alerta se persistir |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** Requer login; webhooks autenticados por assinatura
- 🟡 **Autorização:** Vendedor só vê pedidos das suas contas
- 🟡 **Dados sensíveis:** Nome e endereço do comprador são PII — armazenar com acesso restrito
- 🟡 **Auditoria:** Registrar: recebimento de pedido, mudanças de status, envio de rastreio

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** ML primeiro (webhook), Shopee depois
- 🟡 **Como reverter:** Desativar webhook; pedidos existentes preservados
- 🟡 **Monitoramento pós-deploy:** Pedidos recebidos vs. pedidos no marketplace, latência de recebimento

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | ML exige TLS e domínio verificado para receber webhooks? | 🟡 Alto | 🟡 Sandeco | 🟡 Antes do MVP |
| 🟡 OQ-02 | Como estimar taxa do marketplace para cálculo de lucro? | 🟡 Médio | 🟡 Sandeco | 🟡 MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 Webhook + polling de backup | 🟡 Só polling | 🟡 Webhook é mais rápido; polling garante resiliência |
| 🟡 Compra no distribuidor manual | 🟡 Compra automática | 🟡 Muito risco automatizar compra; vendedor decide caso a caso |
| 🟡 Lucro estimado (não exato) | 🟡 Integração com sistema financeiro | 🟡 Taxas do marketplace variam; estimativa basta para MVP |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`
- 🟡 API ML Orders: https://developers.mercadolivre.com.br/pt_br/gestao-de-vendas

### Histórico de Revisões
| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-06-10 | reversa-spec-sdd | Criação inicial |

---

## Relatório de Avaliação

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORE TOTAL: 89/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Breakdown:
  Completude:    92/100 (peso 30%)
  Testabilidade: 88/100 (peso 25%)
  Clareza:       90/100 (peso 20%)
  Escopo:        87/100 (peso 15%)
  Edge Cases:    88/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Validar requisitos de webhook do ML (OQ-01) — pode exigir HTTPS com domínio
  2. Definir modelo de estimativa de taxa do marketplace (OQ-02)
```
