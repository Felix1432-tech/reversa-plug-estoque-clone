# Interface: Sites de Distribuidores (RPA)

> Tipo: HTTP (browser automation via Playwright)
> Auth: Login/senha por site

## Sites mapeados

| Distribuidor | URL | Tipo de auth | Dados disponíveis |
|-------------|-----|-------------|-------------------|
| DPK | `https://www.dpk.com.br/#/` | Login/senha | SKU, nome, descrição, fotos, preço, estoque, peso, medidas |
| Furacão | `https://vendas.furacao.com.br/vendas/sav/produtos` | Login/senha | SKU, nome, descrição, fotos, preço, estoque, peso, medidas |
| RUFATO | URL a mapear | Login/senha | Catálogo completo (detalhes na implementação) |
| ISAPA | URL a mapear | Login/senha | Catálogo completo (detalhes na implementação) |
| Pellegrino | `https://compreonline.pellegrino.com.br/` | Login/senha | Fotos, descrição (estoque indisponível) |
| Rolemarmaster | `https://rolemarmaster.com/` | Login/senha | Catálogo sem estoque |

## Fluxo RPA padrão

```
1. Navegar para página de login
2. Preencher campos login/senha
3. Submeter formulário
4. Aguardar redirecionamento (verificar sucesso)
5. Navegar para página de catálogo/produtos
6. Paginar: para cada página de resultados
   6.1. Extrair lista de SKUs com dados visíveis
   6.2. (Se necessário) Entrar na página de detalhe de cada produto
   6.3. Extrair dados completos: fotos, descrição, peso, medidas, dados fiscais
   6.4. Download de fotos → upload para B2
7. Retornar lista de ProductData normalizados
```

## Configuração de seletores

Cada conector armazena seus seletores CSS/XPath em um dict de configuração para facilitar manutenção quando o site muda layout:

```python
SELECTORS = {
    "login_form": {
        "username": "#email",
        "password": "#password",
        "submit": "button[type=submit]"
    },
    "catalog": {
        "product_list": ".product-card",
        "product_link": "a.product-link",
        "next_page": ".pagination .next"
    },
    "product_detail": {
        "sku": ".product-sku",
        "name": "h1.product-name",
        "description": ".product-description",
        "price": ".product-price",
        "stock": ".stock-quantity",
        "weight": ".product-weight",
        "photos": "img.product-photo"
    }
}
```

## Anti-detecção

| Técnica | Implementação |
|---------|---------------|
| Stealth mode | `playwright-stealth` plugin (remove webdriver flags) |
| User-Agent rotation | Pool de 5+ user-agents reais |
| Delays humanos | `random.uniform(1.0, 3.0)` entre ações |
| Viewport realista | `1920x1080` ou similar |
| Chromium only | Evita fingerprint de browser atípico |

## Timeouts

| Operação | Timeout | Retry |
|----------|---------|-------|
| Navegação para página | 30s | 3x backoff (5s, 15s, 45s) |
| Login | 15s | 3x |
| Extração de página | 30s | 3x |
| Download de foto | 15s | 3x |
| Extração total por distribuidor | 10 min (hard limit) | Não (registrar partial) |

## Erros por distribuidor

| Cenário | Detecção | Ação |
|---------|----------|------|
| Login inválido | URL pós-login = URL de login OU mensagem de erro visível | `status = "error"`, notificar |
| CAPTCHA | Elemento CAPTCHA detectado (`iframe[src*=recaptcha]`, `#captcha`) | Abortar, sugerir CSV |
| Layout mudou | Zero produtos extraídos OU seletores retornam vazio | `status = "error"`, log detalhado |
| Bloqueio IP | HTTP 403 ou redirect para página de bloqueio | Retry com delay maior; se persistir, alertar |
| Rate limit do site | HTTP 429 ou delay crescente nas respostas | Aumentar delay entre requests |
| Session expirou mid-extraction | Redirect para login durante extração | Re-autenticar e continuar do ponto |
