# Spec: Monitoramento de Estoque

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Módulo que verifica periodicamente o estoque dos distribuidores e executa ações automáticas: pausar anúncios quando estoque zera ou fica abaixo de um limite, reativar quando estoque volta. Garante que o vendedor nunca venda produto indisponível.

---

## 2. Contexto e Motivação

**Problema:**
🟡 No modelo cross-docking, o vendedor não controla o estoque — ele depende do distribuidor. Se vender produto sem estoque, não consegue entregar, prejudica métricas de reputação e pode ser penalizado pelo marketplace.

**Evidências:**
🟡 Premissa P2 do ideation: marketplaces penalizam vendas sem entrega. Feature central: "monitora estoque do distribuidor e pausa anúncio se zera o estoque".

**Por que agora:**
🟡 Sem monitoramento automático, o modelo cross-docking é inviável em escala.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Verificar estoque dos distribuidores periodicamente via conectores
- [ ] 🟡 G-02: Pausar anúncios automaticamente quando estoque ≤ threshold
- [ ] 🟡 G-03: Reativar anúncios automaticamente quando estoque volta acima do threshold
- [ ] 🟡 G-04: Notificar vendedor sobre ações automáticas executadas

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Vendas de produto sem estoque | 🟡 N/A | 🟡 0 | 🟡 MVP |
| 🟡 Tempo entre estoque zerar e anúncio pausar | 🟡 N/A | 🟡 < 30 minutos | 🟡 MVP |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Previsão de demanda / estoque futuro
- 🟡 NG-02: Compra automática no distribuidor quando estoque fica baixo
- 🟡 NG-03: Monitoramento em tempo real via webhook (distribuidores não oferecem)
- 🟡 NG-04: Gestão de estoque próprio do vendedor

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Ambas personas — o monitoramento é automático; vendedor configura thresholds e recebe notificações.

**Jornada futura (com a feature):**
1. 🟡 Vendedor configura threshold de estoque (padrão: pausar quando ≤ 0)
2. 🟡 Sistema verifica estoque periodicamente
3. 🟡 Quando estoque zera: pausa anúncios e notifica
4. 🟡 Quando estoque volta: reativa anúncios e notifica

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve executar job de verificação de estoque em intervalo configurável (padrão: a cada 30 minutos) | Must | 🟡 Job roda automaticamente; intervalo editável nas configurações |
| 🟡 RF-02 | O sistema deve chamar `fetch_stock()` de cada conector ativo durante o job | Must | 🟡 Estoque atualizado para todos os produtos com conector funcional |
| 🟡 RF-03 | O sistema deve pausar automaticamente anúncios quando estoque do produto ≤ threshold | Must | 🟡 Anúncio muda para status "paused" no marketplace via API; `product_listings.status` atualizado |
| 🟡 RF-04 | O sistema deve reativar automaticamente anúncios quando estoque volta acima do threshold | Must | 🟡 Anúncio muda para "active" no marketplace; vendedor é notificado |
| 🟡 RF-05 | O sistema deve permitir configurar threshold de estoque mínimo (padrão: 0) | Should | 🟡 Configurável globalmente e por produto (override) |
| 🟡 RF-06 | O sistema deve notificar vendedor sobre pausas e reativações via painel (e opcionalmente e-mail) | Must | 🟡 Notificação com: produto, distribuidor, estoque atual, ação tomada, marketplace afetado |
| 🟡 RF-07 | O sistema deve exibir log de ações automáticas (últimas 30 dias) | Should | 🟡 Lista: data/hora, produto, ação (pausou/reativou), motivo, marketplace |
| 🟡 RF-08 | O sistema deve pausar anúncios em TODAS as contas quando estoque de um produto zera | Must | 🟡 Se produto X está publicado em 3 contas ML, os 3 anúncios são pausados |
| 🟡 RF-09 | O sistema deve permitir pausar/retomar monitoramento por distribuidor | Should | 🟡 Toggle on/off por distribuidor nas configurações |

### 6.2 Fluxo Principal (Happy Path)

1. 🟡 Scheduler dispara job de verificação de estoque (a cada 30 min)
2. 🟡 Para cada distribuidor ativo: chama `fetch_stock()`
3. 🟡 Para cada produto com estoque alterado: atualiza `products.stock_quantity`
4. 🟡 Para cada produto cujo estoque ficou ≤ threshold E tem anúncios ativos: chama API do marketplace para pausar
5. 🟡 Para cada produto cujo estoque voltou > threshold E tem anúncios pausados (por estoque): chama API do marketplace para reativar
6. 🟡 Registra ações no log e notifica vendedor
7. 🟡 Resultado: anúncios sincronizados com estoque real

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Distribuidor com estoque indisponível (Pellegrino, Rolemarmaster):**
1. 🟡 `fetch_stock()` retorna null para Pellegrino e Rolemarmaster
2. 🟡 Sistema não executa pausa automática para produtos destes distribuidores
3. 🟡 Badge "Estoque não monitorado" no catálogo
4. 🟡 Vendedor assume risco manualmente

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Frequência de polling | 🟡 Configurável: 15 min a 2 horas (padrão 30 min) | 🟡 Balanceia atualidade vs. carga nos sites |
| 🟡 RNF-02 | Tempo de execução do job completo | 🟡 < 15 minutos para 6 distribuidores | 🟡 Conectores executam em paralelo |
| 🟡 RNF-03 | Latência da pausa no marketplace | 🟡 < 5 minutos após detecção | 🟡 API call imediata; latência é do marketplace processar |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Configuração de monitoramento, painel de notificações, log de ações automáticas, badges no catálogo.

**Estados da UI:**
- 🟡 Monitoramento ativo: badge verde "Monitorando — última verificação há X min"
- 🟡 Alerta de estoque baixo: badge amarelo no produto e no dashboard
- 🟡 Anúncio pausado por estoque: badge vermelho "Pausado — sem estoque"
- 🟡 Estoque não monitorado: badge cinza "Estoque não disponível neste distribuidor"

---

## 9. Modelo de Dados

🟡

```
StockMonitorConfig {
  id: UUID
  user_id: UUID (FK)
  check_interval_minutes: integer   // padrão 30
  default_threshold: integer        // padrão 0
  email_notifications: boolean      // padrão false
  created_at: datetime
  updated_at: datetime
}

StockAction {
  id: UUID
  user_id: UUID (FK)
  product_id: UUID (FK)
  product_listing_id: UUID (FK)
  action: enum                      // "paused" | "reactivated"
  reason: text                      // "Estoque zerou" | "Estoque voltou a 15 unidades"
  stock_before: integer
  stock_after: integer
  executed_at: datetime
}
```

**Migrações necessárias:** 🟡 Sim — criação das tabelas `stock_monitor_configs` e `stock_actions`.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 Conectores de distribuidores (fetch_stock) | 🟡 Obrigatória | 🟡 Estoque não atualiza; anúncios continuam no último estado conhecido |
| 🟡 API Mercado Livre (items/pause, items/activate) | 🟡 Obrigatória | 🟡 Pausa/reativação não funciona; registrar para retry |
| 🟡 API Shopee (items/unlist, items/boost) | 🟡 Obrigatória | 🟡 Idem |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: Conector falha durante verificação de estoque | 🟡 Site fora do ar, login expirado | 🟡 Manter último estoque conhecido; notificar vendedor: "Não foi possível verificar estoque do distribuidor X" |
| 🟡 EC-02: API do marketplace falha ao pausar | 🟡 Rate limit ou indisponibilidade | 🟡 Retry em 5 min; se persistir, alerta urgente ao vendedor |
| 🟡 EC-03: Estoque oscila rápido (zera e volta em minutos) | 🟡 Reposição frequente pelo distribuidor | 🟡 Debounce: só reativar se estoque > threshold por 2 verificações consecutivas para evitar flapping |
| 🟡 EC-04: Produto pausado manualmente pelo vendedor + estoque volta | 🟡 Vendedor pausou por outra razão | 🟡 NÃO reativar automaticamente se a pausa foi manual; respeitar flag `manual_pause` |
| 🟡 EC-05: Distribuidor sem monitoramento de estoque | 🟡 Pellegrino, Rolemarmaster | 🟡 Pular verificação; badge "Não monitorado"; vendedor gerencia manualmente |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** Jobs rodam em background com service account
- 🟡 **Autorização:** Ações automáticas executam no escopo do vendedor
- 🟡 **Dados sensíveis:** N/A
- 🟡 **Auditoria:** Toda pausa/reativação registrada em `stock_actions`

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** Ativar monitoramento distribuidor por distribuidor
- 🟡 **Como reverter:** Desativar job de monitoramento; anúncios permanecem no estado atual
- 🟡 **Monitoramento pós-deploy:** Vendas de produto sem estoque (deve ser 0), pausas/reativações por dia

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | Frequência ideal de polling (trade-off: atualidade vs. carga no site do distribuidor) | 🟡 Médio | 🟡 Sandeco | 🟡 Testar no MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 Polling periódico | 🟡 Webhook (distribuidores não oferecem) | 🟡 Única opção viável sem cooperação do distribuidor |
| 🟡 Debounce de 2 verificações para reativar | 🟡 Reativar imediato | 🟡 Evita flapping que pode parecer manipulação para o marketplace |
| 🟡 Respeitar pausa manual | 🟡 Reativar sempre que estoque voltar | 🟡 Vendedor pode ter pausado por outra razão (preço, sazonalidade) |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`

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
  Testabilidade: 92/100 (peso 25%)
  Clareza:       90/100 (peso 20%)
  Escopo:        88/100 (peso 15%)
  Edge Cases:    90/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Testar frequência de polling ideal empiricamente (OQ-01)
  2. Implementar dashboard de saúde do monitoramento (uptime por conector)
```
