# Spec: Multi-Conta Marketplace

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Módulo que permite ao vendedor conectar e gerenciar múltiplas contas de marketplace (Mercado Livre e Shopee no MVP) a partir de um único painel. Cada conta é vinculada via OAuth e mantém tokens de acesso atualizados automaticamente.

---

## 2. Contexto e Motivação

**Problema:**
🟡 Vendedores experientes operam múltiplas contas no Mercado Livre para diversificar risco e escalar vendas. Hoje gerenciam cada conta em abas/sessões separadas, alternando manualmente. Isso limita a escala e aumenta chance de erro.

**Evidências:**
🟡 Persona "Vendedor multi-conta" opera várias contas simultaneamente e precisa de painel único. Feature essencial para diferencial da plataforma.

**Por que agora:**
🟡 Pré-requisito para publicação de anúncios e gestão de pedidos — sem contas de marketplace conectadas, nenhuma operação é possível.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Permitir conectar múltiplas contas do Mercado Livre via OAuth
- [ ] 🟡 G-02: Permitir conectar múltiplas contas do Shopee via OAuth
- [ ] 🟡 G-03: Manter tokens de acesso atualizados automaticamente (refresh token)
- [ ] 🟡 G-04: Exibir status de conexão de cada conta em tempo real

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Contas conectáveis por vendedor | 🟡 N/A | 🟡 Sem limite | 🟡 MVP |
| 🟡 Taxa de refresh de token com sucesso | 🟡 N/A | 🟡 > 99% | 🟡 MVP |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Amazon e TikTok Shop — pós-MVP
- 🟡 NG-02: Migração automática de anúncios entre contas
- 🟡 NG-03: Criação de contas no marketplace a partir da plataforma
- 🟡 NG-04: Gestão de reputação/métricas de saúde da conta no marketplace

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Vendedor multi-conta — precisa conectar 3+ contas do ML e ver tudo consolidado.
**Usuário secundário:** 🟡 Vendedor solo iniciante — conecta 1 conta do ML para começar.

**Jornada atual (sem a feature):**
🟡 Vendedor abre cada marketplace em aba separada, faz login manual em cada conta, gerencia individualmente.

**Jornada futura (com a feature):**
1. 🟡 Vendedor acessa configurações de marketplaces
2. 🟡 Clica em "Conectar conta" e autoriza via OAuth
3. 🟡 Conta aparece na lista com status "Conectada"
4. 🟡 Todas as contas ficam disponíveis nos módulos de anúncio, pedidos e dashboard

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve permitir conectar conta do Mercado Livre via OAuth 2.0 | Must | 🟡 Ao completar fluxo OAuth, access_token e refresh_token são armazenados e a conta aparece como "Conectada" |
| 🟡 RF-02 | O sistema deve permitir conectar conta do Shopee via OAuth | Must | 🟡 Mesmo critério do RF-01 para Shopee |
| 🟡 RF-03 | O sistema deve renovar access_token automaticamente antes da expiração | Must | 🟡 Token é renovado pelo menos 1 hora antes de expirar; se falhar, marcar conta como "Reconexão necessária" |
| 🟡 RF-04 | O sistema deve exibir lista de contas conectadas com status | Must | 🟡 Lista mostra: nome da conta, marketplace, status (Conectada/Reconexão necessária/Desconectada), data de conexão |
| 🟡 RF-05 | O sistema deve permitir desconectar uma conta | Must | 🟡 Ao desconectar, tokens são revogados e conta removida da lista; anúncios associados ficam órfãos com alerta |
| 🟡 RF-06 | O sistema deve permitir reconectar conta com token expirado | Must | 🟡 Botão "Reconectar" redireciona ao fluxo OAuth e atualiza tokens |
| 🟡 RF-07 | O sistema deve armazenar tokens de forma segura (criptografados) | Must | 🟡 Tokens nunca expostos em logs, API responses ou frontend |
| 🟡 RF-08 | O sistema deve permitir conectar múltiplas contas do mesmo marketplace | Should | 🟡 Vendedor pode ter 5 contas do ML e 2 do Shopee conectadas simultaneamente |

### 6.2 Fluxo Principal (Happy Path)

1. 🟡 Vendedor acessa "Configurações > Marketplaces"
2. 🟡 Clica em "Conectar conta do Mercado Livre"
3. 🟡 Sistema redireciona para tela de autorização do ML
4. 🟡 Vendedor autoriza o aplicativo
5. 🟡 ML redireciona de volta com authorization code
6. 🟡 Sistema troca code por access_token + refresh_token
7. 🟡 Sistema obtém dados da conta (nickname, seller_id) via API do ML
8. 🟡 Conta aparece na lista com status "Conectada"
9. 🟡 Resultado: conta disponível para publicação, pedidos e dashboard

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Reconexão:**
1. 🟡 Token expira e refresh falha
2. 🟡 Sistema marca conta como "Reconexão necessária"
3. 🟡 Vendedor clica em "Reconectar"
4. 🟡 Fluxo OAuth é repetido
5. 🟡 Novos tokens substituem os antigos

**Fluxo Alternativo B — Desconexão:**
1. 🟡 Vendedor clica em "Desconectar" em uma conta
2. 🟡 Sistema exibe confirmação: "Desconectar removerá o acesso. Anúncios desta conta não serão mais gerenciados."
3. 🟡 Vendedor confirma
4. 🟡 Tokens revogados, conta removida da lista

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Latência do fluxo OAuth | 🟡 < 5 segundos (excluindo tempo do usuário na tela do ML) | 🟡 Callback + troca de token + obtenção de dados |
| 🟡 RNF-02 | Armazenamento de tokens | 🟡 Criptografia AES-256 at rest | 🟡 Tokens são credenciais sensíveis |
| 🟡 RNF-03 | Refresh de token | 🟡 Job executado a cada 1 hora | 🟡 Verifica tokens que expiram nas próximas 2 horas |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Página de configurações de marketplaces, card de conta conectada, modal de confirmação de desconexão.

**Comportamento esperado:**
🟡 Lista de contas conectadas com cards. Cada card mostra: avatar/nome da conta, marketplace (ícone), status (badge colorido), botões de ação.

**Estados da UI:**
- 🟡 Estado vazio: "Nenhuma conta conectada. Clique em 'Conectar conta' para começar."
- 🟡 Estado de carregamento: spinner durante fluxo OAuth
- 🟡 Estado de erro: badge "Reconexão necessária" em vermelho com botão de reconectar
- 🟡 Estado de sucesso: badge "Conectada" em verde

---

## 9. Modelo de Dados

🟡

```
MarketplaceAccount {
  id: UUID                    // identificador único
  user_id: UUID (FK)          // referência ao vendedor
  marketplace: enum           // "mercado_livre" | "shopee"
  external_account_id: string // seller_id no marketplace
  account_name: string        // nickname/nome da conta
  access_token: string (enc)  // token criptografado AES-256
  refresh_token: string (enc) // refresh token criptografado
  token_expires_at: datetime  // expiração do access_token
  status: enum                // "connected" | "needs_reconnect" | "disconnected"
  connected_at: datetime      // data de conexão
  updated_at: datetime        // última atualização
}
```

**Migrações necessárias:** 🟡 Sim — criação da tabela `marketplace_accounts`.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 API OAuth Mercado Livre | 🟡 Obrigatória | 🟡 Impossível conectar novas contas ML; contas existentes continuam funcionando até token expirar |
| 🟡 API OAuth Shopee | 🟡 Obrigatória | 🟡 Impossível conectar novas contas Shopee |
| 🟡 Módulo de autenticação (autenticacao-e-contas) | 🟡 Obrigatória | 🟡 Sem autenticação, não há vendedor para vincular contas |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: Usuário cancela OAuth | 🟡 Fecha a tela de autorização do ML ou clica "Negar" | 🟡 Redirecionar de volta com mensagem "Conexão cancelada. Tente novamente quando quiser." |
| 🟡 EC-02: Token de refresh expirado/revogado | 🟡 ML revoga acesso ou refresh token expira | 🟡 Marcar conta como "Reconexão necessária"; pausar operações automáticas nessa conta; notificar vendedor |
| 🟡 EC-03: Conta do ML já conectada por outro vendedor | 🟡 Mesma conta ML autorizada em dois vendedores | 🟡 Permitir (cada vendedor tem seu token); futuramente avaliar se é cenário desejável |
| 🟡 EC-04: API do ML fora do ar durante OAuth | 🟡 Timeout na troca de code por token | 🟡 Exibir "Mercado Livre está temporariamente indisponível. Tente novamente em alguns minutos." |
| 🟡 EC-05: Vendedor tenta desconectar conta com anúncios ativos | 🟡 Desconexão com anúncios publicados | 🟡 Exibir alerta: "Esta conta tem X anúncios ativos que não serão mais gerenciados. Deseja continuar?" |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** Vendedor deve estar logado para gerenciar contas
- 🟡 **Autorização:** Vendedor só vê e gerencia suas próprias contas
- 🟡 **Dados sensíveis:** access_token e refresh_token são credenciais de terceiros — criptografados AES-256 at rest, nunca logados ou expostos via API
- 🟡 **Auditoria:** Registrar: conexão de conta, desconexão, falhas de refresh, reconexões

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** Deploy direto (uso próprio)
- 🟡 **Como reverter:** Rollback do deploy; tokens existentes preservados no banco
- 🟡 **Monitoramento pós-deploy:** Taxa de sucesso de refresh de tokens, número de contas em "Reconexão necessária"

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | Quantas contas ML o Sandeco vai conectar inicialmente? | 🟡 Baixo | 🟡 Sandeco | 🟡 Antes do MVP |
| 🟡 OQ-02 | API do Shopee exige empresa registrada para obter credenciais de app? | 🟡 Alto | 🟡 Sandeco | 🟡 Antes do MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 OAuth 2.0 para conexão | 🟡 Armazenar login/senha do marketplace | 🟡 OAuth é o padrão dos marketplaces; mais seguro; não viola termos de uso |
| 🟡 Criptografia AES-256 para tokens | 🟡 Armazenar em texto plano | 🟡 Tokens são credenciais de alto valor; comprometimento expõe contas do vendedor |
| 🟡 Sem limite de contas por vendedor | 🟡 Limite de 5 contas | 🟡 Uso próprio não precisa de limite; quando virar SaaS, limite pode ser por plano |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`
- 🟡 API Mercado Livre: https://developers.mercadolivre.com.br/
- 🟡 API Shopee: https://open.shopee.com/

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
  Testabilidade: 90/100 (peso 25%)
  Clareza:       88/100 (peso 20%)
  Escopo:        85/100 (peso 15%)
  Edge Cases:    85/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Verificar requisitos de registro de app na Shopee (OQ-02)
  2. Definir comportamento quando marketplace depreca versão da API OAuth
```
