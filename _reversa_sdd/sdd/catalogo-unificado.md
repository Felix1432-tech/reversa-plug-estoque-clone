# Spec: Catálogo Unificado

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Interface unificada que consolida produtos de todos os distribuidores configurados em uma única visão com busca, filtros e seleção em massa. É o ponto central de trabalho do vendedor — onde ele encontra, seleciona e prepara produtos para publicação.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Produtos vêm de 6 distribuidores diferentes, cada um com seu formato. Sem catálogo unificado, o vendedor precisa navegar entre conectores para encontrar produtos.

**Evidências:**
🟡 Jornada da Persona 1 (passo 3): "Navegar no catálogo do distribuidor e selecionar SKUs". Jornada da Persona 2 (passo 2): "Selecionar SKUs em massa dos catálogos de múltiplos distribuidores".

**Por que agora:**
🟡 Elo entre conectores (entrada de dados) e publicação (saída). Sem catálogo, vendedor não consegue selecionar produtos.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Exibir todos os produtos de todos os distribuidores em uma lista unificada
- [ ] 🟡 G-02: Permitir busca por nome, SKU, distribuidor e categoria
- [ ] 🟡 G-03: Permitir seleção em massa (checkbox, selecionar todos, selecionar por filtro)
- [ ] 🟡 G-04: Exibir status de estoque por produto com indicadores visuais

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Tempo para encontrar um produto específico | 🟡 N/A | 🟡 < 5 segundos com busca | 🟡 MVP |
| 🟡 Produtos exibidos por página | 🟡 N/A | 🟡 50 com paginação | 🟡 MVP |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Edição de dados do produto no catálogo (dados vêm do distribuidor, são read-only)
- 🟡 NG-02: Comparação de preços entre distribuidores para mesmo produto
- 🟡 NG-03: Recomendação automática de produtos para publicar
- 🟡 NG-04: Integração direta com catálogo de marketplace (isso é do módulo de publicação)

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Vendedor solo iniciante — precisa navegar de forma simples e visual, entender o que está vendo.
**Usuário secundário:** 🟡 Vendedor multi-conta — precisa de filtros avançados e seleção em massa eficiente para alto volume.

**Jornada atual (sem a feature):**
🟡 Vendedor acessa site de cada distribuidor separadamente, navega catálogos diferentes com layouts diferentes.

**Jornada futura (com a feature):**
1. 🟡 Vendedor acessa catálogo unificado
2. 🟡 Filtra por distribuidor, busca por nome/SKU
3. 🟡 Seleciona produtos desejados (individual ou em massa)
4. 🟡 Envia seleção para publicação

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve listar todos os produtos de todos os distribuidores em uma tabela/grid única | Must | 🟡 Produtos de DPK, Furacão, Pellegrino e L'Aquila aparecem na mesma lista |
| 🟡 RF-02 | O sistema deve exibir por produto: foto thumbnail, nome, SKU, distribuidor, preço do distribuidor, estoque, status | Must | 🟡 Todos os campos visíveis sem precisar abrir detalhe |
| 🟡 RF-03 | O sistema deve permitir busca textual por nome e SKU | Must | 🟡 Busca retorna resultados em < 1 segundo para catálogo de até 10.000 produtos |
| 🟡 RF-04 | O sistema deve permitir filtrar por: distribuidor, faixa de preço, disponibilidade de estoque, já publicado/não publicado | Must | 🟡 Filtros combinam entre si (AND); resultado atualiza em tempo real |
| 🟡 RF-05 | O sistema deve permitir selecionar produtos via checkbox individual | Must | 🟡 Checkbox por linha; contador de selecionados visível |
| 🟡 RF-06 | O sistema deve permitir "Selecionar todos" (da página ou do filtro inteiro) | Must | 🟡 "Selecionar todos os 347 resultados" quando filtro ativo |
| 🟡 RF-07 | O sistema deve exibir indicador visual de estoque: verde (disponível), amarelo (baixo), vermelho (zerado), cinza (indisponível) | Should | 🟡 Cores correspondem aos thresholds: verde > 10, amarelo 1-10, vermelho 0, cinza null |
| 🟡 RF-08 | O sistema deve exibir badge "Já publicado em [ML/Shopee]" nos produtos que já têm anúncio ativo | Should | 🟡 Badge com ícone do marketplace; clicável para ver anúncio |
| 🟡 RF-09 | O sistema deve suportar paginação com 50 itens por página | Must | 🟡 Navegação entre páginas sem perder seleção |
| 🟡 RF-10 | O sistema deve permitir abrir detalhe do produto com todas as informações e fotos em tamanho completo | Should | 🟡 Modal ou página de detalhe com: todas as fotos, descrição completa, peso, medidas, dados fiscais |

### 6.2 Fluxo Principal (Happy Path)

1. 🟡 Vendedor acessa "Catálogo" no menu
2. 🟡 Sistema carrega lista paginada de todos os produtos
3. 🟡 Vendedor filtra por distribuidor "DPK" e busca "filtro de óleo"
4. 🟡 Sistema exibe resultados filtrados com indicadores de estoque
5. 🟡 Vendedor seleciona 30 produtos via "Selecionar todos"
6. 🟡 Vendedor clica em "Publicar selecionados" 
7. 🟡 Resultado: seleção é enviada ao módulo de publicação

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Busca sem resultados:**
1. 🟡 Vendedor busca termo que não existe
2. 🟡 Sistema exibe "Nenhum produto encontrado para '[termo]'. Tente outros termos ou remova filtros."

**Fluxo Alternativo B — Catálogo vazio:**
1. 🟡 Nenhum distribuidor configurado ou nenhuma extração feita
2. 🟡 Sistema exibe "Catálogo vazio. Configure seus distribuidores em Configurações para importar produtos."

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Tempo de carregamento da lista | 🟡 < 2 segundos para 50 itens | 🟡 Com thumbnail das fotos |
| 🟡 RNF-02 | Busca textual | 🟡 < 1 segundo para 10.000 produtos | 🟡 Index full-text no banco |
| 🟡 RNF-03 | Seleção em massa | 🟡 Até 500 produtos selecionados sem degradação | 🟡 Estado mantido no frontend |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Página de catálogo, barra de busca/filtros, tabela/grid de produtos, modal de detalhe, barra de ações em massa.

**Comportamento esperado:**
🟡 Layout de tabela com colunas: checkbox, foto, nome, SKU, distribuidor, preço, estoque (badge colorido), status publicação, ações. Barra superior com busca + filtros. Barra inferior flutuante quando há seleção ativa: "X produtos selecionados — [Publicar] [Limpar seleção]".

**Estados da UI:**
- 🟡 Estado vazio: CTA para configurar distribuidores
- 🟡 Estado de carregamento: skeleton loader nas linhas da tabela
- 🟡 Estado de erro: mensagem de erro com botão "Tentar novamente"
- 🟡 Estado de sucesso: tabela populada com dados e indicadores visuais

---

## 9. Modelo de Dados

🟡 Utiliza a tabela `Product` definida em `conectores-distribuidores.md`. Este módulo é somente leitura sobre esses dados.

Entidade adicional para rastrear publicação:

```
ProductListing {
  id: UUID
  product_id: UUID (FK)          // produto do catálogo
  marketplace_account_id: UUID (FK) // conta onde foi publicado
  marketplace_item_id: string    // ID do anúncio no marketplace
  status: enum                   // "active" | "paused" | "removed"
  created_at: datetime
}
```

**Migrações necessárias:** 🟡 Sim — criação da tabela `product_listings` (compartilhada com módulo de publicação).

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 Módulo conectores-distribuidores | 🟡 Obrigatória | 🟡 Sem produtos importados, catálogo fica vazio |
| 🟡 Object storage (fotos) | 🟡 Should | 🟡 Thumbnails não carregam; dados textuais continuam disponíveis |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: Catálogo muito grande (>10.000 produtos) | 🟡 Múltiplos distribuidores com catálogos extensos | 🟡 Paginação server-side; busca e filtros obrigatórios para performance |
| 🟡 EC-02: Produto sem foto | 🟡 Distribuidor não forneceu imagem | 🟡 Exibir placeholder genérico na thumbnail |
| 🟡 EC-03: Estoque desatualizado | 🟡 Última extração há mais de 24h | 🟡 Badge "Estoque pode estar desatualizado" com horário da última verificação |
| 🟡 EC-04: Seleção em massa + mudança de página | 🟡 Vendedor seleciona na página 1 e vai para página 2 | 🟡 Seleção da página 1 é preservada; contador global reflete total |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** Requer login
- 🟡 **Autorização:** Vendedor só vê produtos dos seus distribuidores
- 🟡 **Dados sensíveis:** Preços do distribuidor são informação comercial sensível — não expor publicamente
- 🟡 **Auditoria:** N/A (módulo read-only)

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** Deploy direto
- 🟡 **Como reverter:** Rollback do deploy; dados no banco não são afetados
- 🟡 **Monitoramento pós-deploy:** Tempo de carregamento de página, taxa de uso de busca vs. filtro

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | Ordenação padrão: por nome, por data de importação, ou por distribuidor? | 🟡 Baixo | 🟡 Sandeco | 🟡 MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 Catálogo read-only (dados vêm dos conectores) | 🟡 Permitir edição manual no catálogo | 🟡 Fonte de verdade é o distribuidor; edição manual cria divergência |
| 🟡 Paginação server-side | 🟡 Carregar tudo no frontend | 🟡 Catálogos podem ter milhares de produtos; performance |
| 🟡 Seleção em massa preserva entre páginas | 🟡 Resetar ao mudar página | 🟡 UX essencial para operação em alto volume |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`
- 🟡 Spec conectores: `_reversa_sdd/sdd/conectores-distribuidores.md`

### Histórico de Revisões
| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-06-10 | reversa-spec-sdd | Criação inicial |

---

## Relatório de Avaliação

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCORE TOTAL: 88/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Breakdown:
  Completude:    90/100 (peso 30%)
  Testabilidade: 88/100 (peso 25%)
  Clareza:       90/100 (peso 20%)
  Escopo:        85/100 (peso 15%)
  Edge Cases:    85/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Definir ordenação padrão (OQ-01)
  2. Considerar busca com fuzzy matching para erros de digitação
```
