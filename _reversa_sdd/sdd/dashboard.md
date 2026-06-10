# Spec: Dashboard

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Painel consolidado que apresenta visão geral da operação: vendas, lucro estimado, anúncios ativos, estoque crítico e performance por conta e marketplace. É a tela principal após login — o centro de comando do vendedor.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Sem visão consolidada, vendedor precisa acessar cada marketplace e cada distribuidor para entender como está a operação. Impossível tomar decisões rápidas sem dados centralizados.

**Evidências:**
🟡 Jornada Persona 1 (passo 7): "Verificar dashboard de vendas e lucro no final do dia". Jornada Persona 2 (passo 6): "Analisar performance por conta/marketplace no dashboard unificado".

**Por que agora:**
🟡 Feature de alto valor percebido — primeira coisa que o vendedor vê ao entrar. Consolida valor de todos os outros módulos.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Exibir métricas de vendas consolidadas (total, por conta, por marketplace)
- [ ] 🟡 G-02: Exibir lucro estimado (receita - custo distribuidor - taxa marketplace)
- [ ] 🟡 G-03: Exibir status dos anúncios (ativos, pausados, com erro)
- [ ] 🟡 G-04: Alertar sobre estoque crítico e ações automáticas recentes

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Tempo de carregamento do dashboard | 🟡 N/A | 🟡 < 3 segundos | 🟡 MVP |
| 🟡 Dados exibidos | 🟡 N/A | 🟡 Atualizados em até 30 minutos | 🟡 MVP |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Relatórios exportáveis (PDF, Excel)
- 🟡 NG-02: Dashboards customizáveis (drag & drop de widgets)
- 🟡 NG-03: Comparação com períodos anteriores (MoM, YoY)
- 🟡 NG-04: Métricas de reputação do marketplace

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Vendedor multi-conta — precisa de visão por conta para comparar performance.
**Usuário secundário:** 🟡 Vendedor solo — precisa de visão simples e motivacional (quanto vendeu, quanto lucrou).

**Jornada futura (com a feature):**
1. 🟡 Vendedor faz login
2. 🟡 Dashboard carrega com dados consolidados
3. 🟡 Vendedor identifica alertas, verifica vendas do dia, toma decisões

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve exibir cards de resumo: vendas hoje, vendas mês, lucro estimado hoje, lucro estimado mês | Must | 🟡 4 cards no topo com valores numéricos atualizados |
| 🟡 RF-02 | O sistema deve exibir contadores de anúncios: total ativos, pausados (por estoque), pausados (manual), com erro | Must | 🟡 Contadores com cores: verde (ativos), amarelo (pausados), vermelho (erro) |
| 🟡 RF-03 | O sistema deve exibir lista de alertas: estoque crítico, contas com reconexão necessária, erros de publicação | Must | 🟡 Lista ordenada por urgência; clicável para ação |
| 🟡 RF-04 | O sistema deve exibir tabela de performance por conta: conta, marketplace, anúncios ativos, vendas, lucro | Must | 🟡 Uma linha por conta conectada com métricas |
| 🟡 RF-05 | O sistema deve permitir filtrar por período: hoje, 7 dias, 30 dias | Should | 🟡 Toggle que atualiza todos os cards e tabelas |
| 🟡 RF-06 | O sistema deve exibir últimos 10 pedidos recebidos com status | Should | 🟡 Mini-lista com: data, marketplace, valor, status |
| 🟡 RF-07 | O sistema deve exibir status dos conectores de distribuidores: última extração, status, erros | Should | 🟡 Mini-painel com badge por distribuidor |

### 6.2 Fluxo Principal (Happy Path)

1. 🟡 Vendedor faz login
2. 🟡 Sistema redireciona ao dashboard
3. 🟡 Dashboard carrega dados agregados dos últimos 30 dias
4. 🟡 Vendedor vê cards de resumo no topo
5. 🟡 Vendedor vê alertas (se houver)
6. 🟡 Vendedor vê performance por conta
7. 🟡 Vendedor clica em alerta para tomar ação
8. 🟡 Resultado: visão completa da operação em uma tela

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Dashboard vazio (primeiro acesso):**
1. 🟡 Vendedor acabou de criar conta
2. 🟡 Dashboard mostra: "Bem-vindo! Comece conectando sua conta de marketplace e configurando seus distribuidores."
3. 🟡 CTAs para: Conectar marketplace, Configurar distribuidor

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Tempo de carregamento | 🟡 < 3 segundos para renderizar todos os cards | 🟡 Queries agregadas otimizadas |
| 🟡 RNF-02 | Refresh de dados | 🟡 Dados refletem estado de até 30 min atrás | 🟡 Sem necessidade de real-time para MVP |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Página principal (dashboard), cards de métrica, tabela de performance, lista de alertas, mini-lista de pedidos.

**Layout:**
🟡 Topo: 4 cards de resumo (vendas hoje, vendas mês, lucro hoje, lucro mês)
Meio-esquerda: tabela de performance por conta
Meio-direita: alertas e ações pendentes
Inferior: últimos pedidos + status dos conectores

**Estados da UI:**
- 🟡 Estado vazio: onboarding com CTAs
- 🟡 Estado de carregamento: skeleton loaders nos cards
- 🟡 Estado de erro: mensagem de erro com retry
- 🟡 Estado normal: dados populados com indicadores visuais

---

## 9. Modelo de Dados

🟡 Este módulo é read-only sobre dados dos outros módulos. Não cria tabelas próprias. Queries agregam de:

- `orders` + `order_items` → vendas e lucro
- `product_listings` → contagem de anúncios por status
- `stock_actions` → alertas de estoque
- `marketplace_accounts` → status de conexão
- `connector_logs` → status dos conectores

Tabela auxiliar opcional para cache:

```
DashboardCache {
  user_id: UUID (FK)
  metric_key: string       // "sales_today" | "profit_month" | etc.
  value: decimal
  computed_at: datetime
}
```

**Migrações necessárias:** 🟡 Opcional — tabela de cache para performance. Pode iniciar sem cache.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 Módulo gestão-pedidos (orders) | 🟡 Obrigatória | 🟡 Cards de vendas e lucro ficam zerados |
| 🟡 Módulo publicação-anúncios (product_listings) | 🟡 Obrigatória | 🟡 Contadores de anúncios ficam zerados |
| 🟡 Módulo monitoramento-estoque (stock_actions) | 🟡 Obrigatória | 🟡 Alertas de estoque não aparecem |
| 🟡 Módulo multi-conta (marketplace_accounts) | 🟡 Obrigatória | 🟡 Tabela de performance vazia |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: Nenhuma venda ainda | 🟡 Vendedor novo ou sem vendas no período | 🟡 Cards mostram R$ 0,00 com mensagem: "Nenhuma venda no período selecionado" |
| 🟡 EC-02: Query de agregação lenta | 🟡 Volume alto de pedidos/anúncios | 🟡 Usar cache; exibir "Atualizado há X minutos"; skeleton loader enquanto computa |
| 🟡 EC-03: Conta desconectada | 🟡 Token expirado | 🟡 Alerta no dashboard: "Conta X precisa de reconexão" com botão de ação |
| 🟡 EC-04: Dados inconsistentes (lucro negativo) | 🟡 Margem configurada menor que taxa do marketplace | 🟡 Exibir lucro negativo em vermelho com alerta: "Atenção: margem insuficiente em X produtos" |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** Requer login
- 🟡 **Autorização:** Vendedor só vê dados das suas contas
- 🟡 **Dados sensíveis:** Valores financeiros são informação sensível do vendedor
- 🟡 **Auditoria:** N/A (módulo read-only)

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** Deploy direto; dashboard cresce conforme módulos são ativados
- 🟡 **Como reverter:** Rollback do deploy; dados no banco não são afetados
- 🟡 **Monitoramento pós-deploy:** Tempo de carregamento, erros de query

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | Moeda exibida: sempre BRL ou suportar múltiplas? | 🟡 Baixo | 🟡 Sandeco | 🟡 MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 Dashboard fixo (não customizável) | 🟡 Dashboard com drag & drop de widgets | 🟡 Simplicidade; layout fixo cobre as necessidades de ambas personas |
| 🟡 Dados de até 30 min atrás | 🟡 Real-time com websockets | 🟡 Complexidade desnecessária para MVP; polling periódico já atualiza dados |
| 🟡 Cache opcional | 🟡 Sempre cache | 🟡 Começar sem cache; implementar se performance exigir |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`
- 🟡 Referência visual: https://seller.plugestoque.com.br/dashboard

### Histórico de Revisões
| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-06-10 | reversa-spec-sdd | Criação inicial |

---

## Relatório de Avaliação

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORE TOTAL: 87/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Breakdown:
  Completude:    90/100 (peso 30%)
  Testabilidade: 85/100 (peso 25%)
  Clareza:       88/100 (peso 20%)
  Escopo:        85/100 (peso 15%)
  Edge Cases:    85/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Definir fórmula exata de lucro estimado (receita - custo - taxa) com exemplos
  2. Considerar gráfico de vendas por dia (visual de tendência)
```
