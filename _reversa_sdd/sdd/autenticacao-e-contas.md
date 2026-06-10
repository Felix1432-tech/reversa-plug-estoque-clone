# Spec: Autenticação e Contas

> Selo 🟡 PLANEJADO em todos os itens.

**Versão:** 1.0
**Status:** Rascunho
**Autor:** reversa-spec-sdd
**Data:** 2026-06-10
**Reviewers:** N/A

---

## 1. Resumo

🟡 Módulo de autenticação e gerenciamento de conta do vendedor. Permite cadastro, login, recuperação de senha e gestão de perfil. É a porta de entrada da plataforma — sem conta autenticada, nenhuma outra funcionalidade é acessível.

---

## 2. Contexto e Motivação

**Problema:**
🟡 A plataforma precisa identificar cada vendedor para associar suas contas de marketplace, credenciais de distribuidores e configurações de margem. Sem autenticação, não há como isolar dados entre vendedores (crítico para futuro SaaS).

**Evidências:**
🟡 Requisito implícito de toda a operação — dashboard, pedidos, anúncios e conectores dependem de um usuário autenticado.

**Por que agora:**
🟡 Primeiro componente a ser implementado — pré-requisito para todos os outros.

---

## 3. Goals (Objetivos)

- [ ] 🟡 G-01: Permitir que um vendedor crie conta e faça login de forma segura
- [ ] 🟡 G-02: Permitir recuperação de senha por e-mail
- [ ] 🟡 G-03: Permitir edição de dados do perfil (nome, e-mail, senha)

**Métricas de sucesso:**

| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| 🟡 Taxa de cadastro concluído | 🟡 N/A (sistema novo) | 🟡 > 90% dos que iniciam | 🟡 MVP |
| 🟡 Tempo de login | 🟡 N/A | 🟡 < 3 segundos | 🟡 MVP |

---

## 4. Non-Goals (Fora do Escopo)

- 🟡 NG-01: Login social (Google, Facebook) — não no MVP
- 🟡 NG-02: Sistema de permissões/roles (admin, viewer) — não necessário enquanto for uso próprio
- 🟡 NG-03: Multi-tenant com isolamento por organização — futuro SaaS, não agora
- 🟡 NG-04: 2FA (autenticação de dois fatores) — desejável mas não MVP

---

## 5. Usuários e Personas

**Usuário primário:** 🟡 Vendedor solo iniciante — CLT buscando renda extra, iniciante em tecnologia, precisa de fluxo simples e direto.
**Usuário secundário:** 🟡 Vendedor multi-conta — experiente, quer acesso rápido sem fricção.

**Jornada atual (sem a feature):**
🟡 Sem a plataforma, não existe conta — o vendedor gerencia tudo manualmente em abas separadas.

**Jornada futura (com a feature):**
1. 🟡 Vendedor acessa a URL da plataforma
2. 🟡 Cria conta com e-mail e senha
3. 🟡 Faz login e é redirecionado ao dashboard

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| 🟡 RF-01 | O sistema deve permitir cadastro com nome, e-mail e senha | Must | 🟡 Ao submeter formulário válido, conta é criada e usuário recebe confirmação |
| 🟡 RF-02 | O sistema deve validar unicidade de e-mail no cadastro | Must | 🟡 Ao tentar cadastrar e-mail já existente, exibir mensagem "E-mail já cadastrado" |
| 🟡 RF-03 | O sistema deve exigir senha com mínimo de 8 caracteres | Must | 🟡 Senhas com menos de 8 caracteres são rejeitadas com mensagem clara |
| 🟡 RF-04 | O sistema deve permitir login com e-mail e senha | Must | 🟡 Credenciais válidas geram token JWT e redirecionam ao dashboard |
| 🟡 RF-05 | O sistema deve permitir recuperação de senha via e-mail | Must | 🟡 Ao solicitar, e-mail com link de redefinição é enviado em até 1 minuto |
| 🟡 RF-06 | O sistema deve permitir edição de nome e senha no perfil | Should | 🟡 Alterações salvas com sucesso são refletidas imediatamente |
| 🟡 RF-07 | O sistema deve manter sessão ativa por 7 dias (remember me) | Should | 🟡 Após 7 dias sem atividade, usuário é redirecionado ao login |
| 🟡 RF-08 | O sistema deve fazer logout e invalidar o token | Must | 🟡 Após logout, requisições com token antigo retornam 401 |

### 6.2 Fluxo Principal (Happy Path)

1. 🟡 O usuário acessa a tela de cadastro
2. 🟡 O usuário preenche nome, e-mail e senha
3. 🟡 O sistema valida os dados (e-mail único, senha ≥ 8 chars)
4. 🟡 O sistema cria a conta e autentica automaticamente
5. 🟡 O usuário é redirecionado ao dashboard
6. 🟡 Resultado: usuário autenticado com sessão ativa

### 6.3 Fluxos Alternativos

**Fluxo Alternativo A — Login de usuário existente:**
1. 🟡 Usuário acessa tela de login
2. 🟡 Preenche e-mail e senha
3. 🟡 Sistema valida credenciais e gera token JWT
4. 🟡 Redireciona ao dashboard

**Fluxo Alternativo B — Recuperação de senha:**
1. 🟡 Usuário clica em "Esqueci minha senha"
2. 🟡 Informa e-mail cadastrado
3. 🟡 Sistema envia e-mail com link de redefinição (válido por 1 hora)
4. 🟡 Usuário clica no link e define nova senha
5. 🟡 Sistema atualiza senha e redireciona ao login

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| 🟡 RNF-01 | Performance de login | 🟡 < 3 segundos P95 | 🟡 Incluindo validação e geração de token |
| 🟡 RNF-02 | Armazenamento de senha | 🟡 bcrypt com salt, cost ≥ 10 | 🟡 Nunca armazenar em texto plano |
| 🟡 RNF-03 | Token JWT | 🟡 Expiração: 7 dias, assinado com chave secreta | 🟡 Refresh token opcional no MVP |

---

## 8. Design e Interface

**Componentes afetados:** 🟡 Tela de cadastro, tela de login, tela de recuperação de senha, página de perfil.

**Comportamento esperado:**
🟡 Formulários simples e diretos. Campo de e-mail com validação em tempo real. Indicador de força de senha.

**Estados da UI:**
- 🟡 Estado vazio: formulário limpo pronto para preenchimento
- 🟡 Estado de carregamento: botão desabilitado com spinner durante requisição
- 🟡 Estado de erro: mensagem vermelha abaixo do campo com erro específico
- 🟡 Estado de sucesso: redirecionamento automático ao dashboard (cadastro/login) ou mensagem de confirmação (recuperação de senha)

---

## 9. Modelo de Dados

🟡

```
User {
  id: UUID               // identificador único
  name: string           // nome do vendedor
  email: string (unique) // e-mail, usado como login
  password_hash: string  // hash bcrypt da senha
  created_at: datetime   // data de criação
  updated_at: datetime   // última atualização
}

PasswordResetToken {
  id: UUID               // identificador único
  user_id: UUID (FK)     // referência ao usuário
  token: string (unique) // token aleatório seguro
  expires_at: datetime   // validade (1 hora após criação)
  used: boolean          // se já foi usado
}
```

**Migrações necessárias:** 🟡 Sim — criação das tabelas `users` e `password_reset_tokens`.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| 🟡 Serviço de e-mail (SMTP/SendGrid/SES) | 🟡 Obrigatória para recuperação de senha | 🟡 Recuperação de senha fica indisponível; login e cadastro funcionam normalmente |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| 🟡 EC-01: E-mail duplicado no cadastro | 🟡 Usuário tenta cadastrar e-mail já existente | 🟡 Exibir "E-mail já cadastrado" sem revelar se a conta existe (segurança) |
| 🟡 EC-02: Senha fraca | 🟡 Senha com menos de 8 caracteres | 🟡 Rejeitar com mensagem "Senha deve ter no mínimo 8 caracteres" |
| 🟡 EC-03: Token de recuperação expirado | 🟡 Usuário clica no link após 1 hora | 🟡 Exibir "Link expirado. Solicite nova recuperação de senha." |
| 🟡 EC-04: Credenciais inválidas no login | 🟡 E-mail ou senha incorretos | 🟡 Exibir "E-mail ou senha incorretos" (sem indicar qual está errado) |
| 🟡 EC-05: Serviço de e-mail indisponível | 🟡 Falha no envio do e-mail de recuperação | 🟡 Exibir "Erro ao enviar e-mail. Tente novamente em alguns minutos." e registrar log |
| 🟡 EC-06: Brute force no login | 🟡 Mais de 5 tentativas falhas em 15 minutos | 🟡 Bloquear temporariamente (15 min) com mensagem "Muitas tentativas. Tente novamente em 15 minutos." |

---

## 12. Segurança e Privacidade

- 🟡 **Autenticação:** JWT com expiração de 7 dias
- 🟡 **Autorização:** Todas as rotas exceto cadastro, login e recuperação de senha exigem token válido
- 🟡 **Dados sensíveis:** Senha armazenada como hash bcrypt; e-mail é PII mas necessário para operação
- 🟡 **Auditoria:** Registrar em log: criação de conta, login, falhas de login, alteração de senha

---

## 13. Plano de Rollout

- 🟡 **Estratégia:** Deploy direto (uso próprio, sem necessidade de rollout gradual no MVP)
- 🟡 **Como reverter:** Rollback do deploy; dados de usuários preservados no banco
- 🟡 **Monitoramento pós-deploy:** Taxa de erros no login, tempo de resposta, falhas de envio de e-mail

---

## 14. Open Questions

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| 🟡 OQ-01 | Qual serviço de e-mail usar (SMTP próprio, SendGrid, SES)? | 🟡 Médio | 🟡 Sandeco | 🟡 Antes do MVP |
| 🟡 OQ-02 | Confirmação de e-mail no cadastro é necessária no MVP? | 🟡 Baixo | 🟡 Sandeco | 🟡 Antes do MVP |

---

## 15. Decisões Tomadas (Decision Log)

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| 🟡 JWT para sessão | 🟡 Session cookies server-side | 🟡 JWT é stateless, mais simples para MVP e compatível com futura API mobile |
| 🟡 Sem login social no MVP | 🟡 OAuth com Google | 🟡 Simplifica implementação; público inicial é uso próprio |
| 🟡 Sem 2FA no MVP | 🟡 TOTP / SMS | 🟡 Complexidade desnecessária para uso próprio; adicionar quando virar SaaS |

---

## Apêndice

### Referências
- 🟡 PRD: `_reversa_sdd/prd.md`
- 🟡 Personas: `_reversa_sdd/personas.md`

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
  Testabilidade: 90/100 (peso 25%)
  Clareza:       88/100 (peso 20%)
  Escopo:        85/100 (peso 15%)
  Edge Cases:    85/100 (peso 10%)

Gaps críticos:
  - Nenhum bloqueador identificado

Sugestões (por impacto):
  1. Definir serviço de e-mail (OQ-01) antes da implementação
  2. Considerar rate limiting mais granular (por IP + e-mail)
```
