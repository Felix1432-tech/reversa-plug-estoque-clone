# Ideation, Plug Estoque Clone

> Selo 🟡 PLANEJADO em todos os itens, sujeito a validação.

## Brief original
Criar um sistema igual ao Plug Estoque (https://seller.plugestoque.com.br) — plataforma de gestão para vendedores/sellers com dashboard, controle de estoque, pedidos e integrações com marketplaces.

Referência visual: https://seller.plugestoque.com.br/dashboard

## Problema
🟡 Vendedores querem vender em marketplaces (Mercado Livre, Shopee, Amazon, TikTok) sem precisar investir em estoque próprio. Hoje precisam monitorar manualmente o estoque dos distribuidores, correm risco de vender produto sem disponibilidade, e perdem tempo subindo anúncios um a um. A ferramenta resolve isso automatizando: puxa do distribuidor os SKUs, fotos, descrição, clips, peso e medidas, sobe direto nos marketplaces, monitora o estoque do distribuidor em tempo real e pausa o anúncio automaticamente quando o estoque zera ou fica baixo. Modelo cross-docking: vende primeiro, compra depois.

## Valor entregue
🟡 Vender em marketplace sem investir em estoque, usando catálogo do distribuidor direto — com publicação em massa e monitoramento automático de disponibilidade.

## Alternativas existentes
🟡 **Plug Estoque** (https://seller.plugestoque.com.br): ferramenta mais próxima, permite subir anúncios em massa a partir de catálogos de distribuidores (RUFATO, ISAPA). Limitação principal: cobra por créditos para publicação, o que encarece a operação em escala. Não suporta Amazon e TikTok.

🟡 **Plugg.To**: hub de integração com 80+ marketplaces, mas focado em sincronização de loja própria com marketplaces, não no modelo cross-docking com catálogo de distribuidor.

🟡 Nenhuma alternativa conhecida integra os catálogos de múltiplos distribuidores (Pellegrino, DPK, Furacão, L'Aquila) com publicação ilimitada e sem cobrança por crédito.

## Público-alvo (bruto)
🟡 Primeiro uso próprio (Sandeco como vendedor de marketplace sem estoque). Se validado, potencial para virar SaaS voltado a outros vendedores de marketplace que operam no modelo cross-docking/dropshipping com distribuidores brasileiros.

## Métricas de sucesso
🟡 500 anúncios ativos nos marketplaces em 3 meses — sem limites artificiais de quantidade de anúncios na plataforma.

## Premissas a validar
🟡 **P1 — Acesso contínuo aos catálogos dos distribuidores.** Se RUFATO, ISAPA, Pellegrino, DPK, Furacão ou L'Aquila mudarem a forma de acesso ao catálogo (API, site, planilha), a integração quebra. Mitigação: arquitetura de conectores modulares por distribuidor.

🟡 **P2 — Marketplaces não bloquearem publicação em massa.** Mercado Livre, Shopee, Amazon e TikTok podem detectar e penalizar publicação automatizada em volume. Mitigação: estratégia de "seleção em massa, publicação gradual" (throttling controlado).

🟡 **P3 — Viabilidade do modelo cross-docking na prática.** Depende de o distribuidor conseguir despachar rápido o suficiente para cumprir os SLAs dos marketplaces. Se o prazo de envio do distribuidor for longo demais, as métricas de reputação do vendedor caem.

## Notas
🟡 Distribuidores-alvo identificados e seus catálogos online:
- **RUFATO** — já integrado no Plug Estoque (referência)
- **ISAPA** — já integrado no Plug Estoque (referência)
- **Pellegrino** — https://compreonline.pellegrino.com.br/
- **DPK** — https://www.dpk.com.br/#/
- **Furacão** — https://vendas.furacao.com.br/vendas/sav/produtos
- **L'Aquila** — https://www.laquila.com.br/

🟡 Marketplaces-alvo: Mercado Livre (prioritário), Shopee, Amazon, TikTok Shop.

🟡 Diferencial competitivo principal vs. Plug Estoque: sem cobrança por crédito, anúncios ilimitados, mais distribuidores integrados, mais marketplaces suportados.

---
Gerado por reversa-ideator em 2026-06-10T00:00:00-03:00
Fonte: newproject-brief.md
