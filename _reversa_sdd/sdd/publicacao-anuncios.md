# Spec: Publicação de Anúncios

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Módulo responsável por publicar anúncios nos marketplaces a partir de produtos selecionados no catálogo unificado. Aplica configuração de margem, faz throttling para evitar bloqueios, e mantém vínculo entre produto do distribuidor e anúncio publicado.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Publicar anúncios manualmente é o maior gargalo da operação cross-docking. Copiar dados do distribuidor, formatar para cada marketplace, subir fotos e configurar preço um a um limita severamente a escala.

**Evidências:**
🟡 Plug Estoque cobra créditos por publicação em massa. Meta do projeto: 500 anúncios sem limite artificial. Estratégia definida: seleção em massa, publicação gradual.

**Por que agora:**
🟡 Core business da plataforma — sem publicação, o vendedor não vende.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Publicar anúncios no Mercado Livre e Shopee a partir de produtos do catálogo
- [ ] 🟡 G-02: Configuração de margem/markup por produto, categoria ou lote
- [ ] 🟡 G-03: Publicação gradual com throttling configurável para evitar bloqueios
- [ ] 🟡 G-04: Sem limite artificial de quantidade de anúncios

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Anúncios publicados com sucesso por lote | 🟡 N/A | 🟡 > 95% | 🟡 MVP |
| 🟡 Total de anúncios ativos | 🟡 0 | 🟡 500 | 🟡 3 meses |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Otimização de títulos/descrições para SEO do marketplace
- 🟡 NG-02: A/B testing de anúncios
- 🟡 NG-03: Publicação em Amazon e TikTok (pós-MVP)
- 🟡 NG-04: Edição de anúncio diretamente no marketplace (só via plataforma)

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Ambas personas — solo publica poucos anúncios; multi-conta publica em massa.

**Jornada futura (com a feature):**
1. 🟡 Vendedor seleciona produtos no catálogo
2. 🟡 Escolhe conta(s) de marketplace e configura margem
3. 🟡 Confirma publicação
4. 🟡 Sistema publica gradualmente em background
5. 🟡 Vendedor acompanha progresso na fila de publicação

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve permitir configurar margem de lucro como percentual sobre preço do distribuidor | Must | 🟡 Preço final = preço distribuidor × (1 + margem%). Configurável por produto, por categoria ou por lote |
| 🟡 RF-02 | O sistema deve criar anúncio no Mercado Livre via API com: título, descrição, fotos, preço, categoria, peso, medidas | Must | 🟡 Anúncio publicado e visível no ML com todos os dados corretos |
| 🟡 RF-03 | O sistema deve criar anúncio no Shopee via API com os mesmos dados | Must | 🟡 Anúncio publicado e visível no Shopee |
| 🟡 RF-04 | O sistema deve implementar fila de publicação com throttling configurável | Must | 🟡 Delay mínimo entre publicações: configurável (padrão 30 segundos); máximo de anúncios por hora configurável |
| 🟡 RF-05 | O sistema deve permitir escolher em qual(is) conta(s) de marketplace publicar | Must | 🟡 Dropdown com contas conectadas; pode selecionar múltiplas |
| 🟡 RF-06 | O sistema deve distribuir anúncios entre contas quando múltiplas selecionadas | Should | 🟡 Distribuição round-robin ou por escolha manual do vendedor |
| 🟡 RF-07 | O sistema deve exibir fila de publicação com status por item: pendente, publicando, publicado, erro | Must | 🟡 Lista visível com barra de progresso geral |
| 🟡 RF-08 | O sistema deve permitir pausar, retomar e cancelar a fila de publicação | Must | 🟡 Pausar congela a fila; retomar continua do ponto; cancelar remove pendentes (publicados ficam) |
| 🟡 RF-09 | O sistema deve mapear categorias do marketplace automaticamente a partir dos dados do produto | Should | 🟡 Sugestão automática de categoria com opção de override manual |
| 🟡 RF-10 | O sistema deve vincular cada anúncio publicado ao produto do catálogo | Must | 🟡 Tabela `product_listings` atualizada; badge "Publicado" aparece no catálogo |
| 🟡 RF-11 | O sistema deve permitir republicar anúncio que falhou | Must | 🟡 Botão "Tentar novamente" no item com erro |

### 6.2 Fluxo Principal (Happy Path)

1. 🟡 Vendedor seleciona 50 produtos no catálogo e clica "Publicar"
2. 🟡 Sistema exibe tela de configuração: conta(s) destino, margem de lucro, delay entre publicações
3. 🟡 Vendedor configura margem de 30% e seleciona 2 contas ML
4. 🟡 Vendedor confirma publicação
5. 🟡 Sistema cria 50 itens na fila com status "Pendente"
6. 🟡 Worker processa fila: para cada item, chama API do ML, cria anúncio, atualiza status
7. 🟡 Delay de 30 segundos entre cada publicação
8. 🟡 Vendedor acompanha progresso: "23/50 publicados"
9. 🟡 Resultado: 50 anúncios ativos no ML, distribuídos entre as 2 contas

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Publicação com erro parcial:**
1. 🟡 Dos 50 anúncios, 3 falham (categoria inválida, foto rejeitada)
2. 🟡 Sistema marca como "Erro" com detalhe do motivo
3. 🟡 Os 47 restantes são publicados normalmente
4. 🟡 Vendedor pode corrigir e republicar os 3 com erro

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Throughput de publicação | 🟡 Configurável: 1-120 anúncios/hora por conta | 🟡 Padrão conservador: 60/hora (1 por minuto) |
| 🟡 RNF-02 | Resiliência da fila | 🟡 Fila persiste em banco; restart do sistema retoma processamento | 🟡 Sem perda de itens em caso de crash |
| 🟡 RNF-03 | Upload de fotos | 🟡 Até 10 fotos por anúncio, total < 30MB | 🟡 Fotos já armazenadas localmente pelo conector |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Modal de configuração de publicação, página de fila de publicação, gestão de anúncios.

**Estados da UI:**
- 🟡 Fila vazia: "Nenhuma publicação em andamento. Selecione produtos no catálogo para começar."
- 🟡 Publicando: barra de progresso + lista de itens com status individual
- 🟡 Erro: item com badge vermelho, mensagem de erro e botão "Tentar novamente"
- 🟡 Concluído: resumo: "50 publicados, 3 com erro"

---

## 9. Modelo de Dados

🟡

```
PublishQueue {
  id: UUID
  user_id: UUID (FK)
  created_at: datetime
  status: enum                    // "processing" | "paused" | "completed" | "cancelled"
  total_items: integer
  completed_items: integer
  error_items: integer
  config: jsonb                   // { margin_percent, delay_seconds, max_per_hour }
}

PublishQueueItem {
  id: UUID
  queue_id: UUID (FK)
  product_id: UUID (FK)
  marketplace_account_id: UUID (FK)
  status: enum                    // "pending" | "publishing" | "published" | "error"
  final_price: decimal            // preço com margem aplicada
  marketplace_item_id: string     // ID do anúncio no marketplace (após publicação)
  error_message: text             // mensagem de erro (se houver)
  published_at: datetime
  created_at: datetime
}
```

**Migrações necessárias:** 🟡 Sim — criação das tabelas `publish_queues` e `publish_queue_items`.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 API Mercado Livre (items/publish) | 🟡 Obrigatória | 🟡 Publicação no ML fica indisponível; fila pausa automaticamente |
| 🟡 API Shopee (items/add) | 🟡 Obrigatória | 🟡 Publicação no Shopee fica indisponível |
| 🟡 Catálogo unificado (products) | 🟡 Obrigatória | 🟡 Sem produtos, não há o que publicar |
| 🟡 Multi-conta marketplace | 🟡 Obrigatória | 🟡 Sem contas conectadas, não há onde publicar |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: API do marketplace retorna rate limit | 🟡 Muitas publicações em curto período | 🟡 Pausar fila automaticamente; aguardar cooldown (ex: 5 min); retomar; notificar vendedor |
| 🟡 EC-02: Categoria do produto não encontrada no marketplace | 🟡 Produto sem mapeamento de categoria | 🟡 Marcar como erro com mensagem "Categoria não encontrada"; vendedor seleciona manualmente |
| 🟡 EC-03: Foto rejeitada pelo marketplace | 🟡 Dimensão/formato/tamanho incompatível | 🟡 Tentar redimensionar automaticamente; se falhar, publicar sem a foto rejeitada e registrar alerta |
| 🟡 EC-04: Token da conta expirado durante publicação | 🟡 Refresh de token falhou | 🟡 Pausar itens desta conta na fila; marcar conta como "Reconexão necessária"; continuar publicando em outras contas |
| 🟡 EC-05: Produto sem estoque quando chega sua vez na fila | 🟡 Estoque zerou entre seleção e publicação | 🟡 Pular item com status "Ignorado — sem estoque"; não publicar anúncio de produto indisponível |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** Requer login
- 🟡 **Autorização:** Vendedor só publica em suas contas com seus produtos
- 🟡 **Dados sensíveis:** Preços com margem são informação comercial; tokens de API usados em background
- 🟡 **Auditoria:** Registrar: criação de fila, publicações com sucesso, erros, pausas

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** ML primeiro, Shopee depois
- 🟡 **Como reverter:** Pausar fila; anúncios já publicados continuam no marketplace
- 🟡 **Monitoramento pós-deploy:** Taxa de sucesso de publicação, rate limits atingidos, erros por tipo

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | Qual delay ideal entre publicações para evitar bloqueio no ML? | 🟡 Alto | 🟡 Sandeco | 🟡 Testar no MVP |
| 🟡 OQ-02 | ML exige que o seller seja dono real do produto? Risco de conta bloqueada por cross-docking? | 🟡 Alto | 🟡 Sandeco | 🟡 Antes do MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 Fila persistida em banco | 🟡 Fila in-memory (Redis/RabbitMQ) | 🟡 Simplicidade no MVP; sem dependência extra; sobrevive a restart |
| 🟡 Throttling configurável | 🟡 Delay fixo | 🟡 Cada marketplace tem limites diferentes; vendedor pode ajustar conforme experiência |
| 🟡 Round-robin entre contas | 🟡 Vendedor escolhe conta por produto | 🟡 Mais prático para publicação em massa; override manual disponível |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`
- 🟡 API ML Items: https://developers.mercadolivre.com.br/pt_br/publicar-produtos
- 🟡 API Shopee Items: https://open.shopee.com/documents

### Histórico de Revisões
| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-06-10 | reversa-spec-sdd | Criação inicial |

---

## Relatório de Avaliação

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORE TOTAL: 90/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Breakdown:
  Completude:    92/100 (peso 30%)
  Testabilidade: 90/100 (peso 25%)
  Clareza:       90/100 (peso 20%)
  Escopo:        88/100 (peso 15%)
  Edge Cases:    88/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Testar empiricamente delay ideal no ML (OQ-01)
  2. Validar riscos de cross-docking com termos de uso do ML (OQ-02)
```
