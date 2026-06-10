# Interface: Google Drive API (L'Aquila)

> Tipo: HTTP (Google SDK)
> Auth: Service Account
> Pasta: `https://drive.google.com/drive/folders/1fTGWuCD_gB8xj8dveddGE-2XDZOoh1jW`

## Configuração

1. Criar Service Account no Google Cloud Console
2. Gerar chave JSON
3. Compartilhar a pasta do Drive com o email do service account (Viewer)
4. Configurar variável de ambiente: `GOOGLE_SERVICE_ACCOUNT_JSON`

## Operações usadas

### Listar arquivos na pasta

```python
service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id, name, mimeType, modifiedTime)",
    pageSize=1000
)
```

### Download de arquivo (foto)

```python
request = service.files().get_media(fileId=file_id)
```

### Ler planilha (se formato Google Sheets)

Usar Sheets API:
```python
sheets_service.spreadsheets().values().get(
    spreadsheetId=sheet_id,
    range='A1:Z1000'
)
```

Ou se for Excel/CSV no Drive: download + parse local com openpyxl/pandas.

## Estrutura esperada da pasta

> A estrutura exata será mapeada durante a implementação. O conector deve ser flexível para detectar automaticamente:

Hipótese baseada no tipo de dados (fotos + preços + descrição + dados fiscais):

```
L'Aquila/
├── Catálogo.xlsx          # Planilha com SKU, nome, descrição, preço, dados fiscais
├── Fotos/
│   ├── SKU-001/
│   │   ├── foto1.jpg
│   │   └── foto2.jpg
│   ├── SKU-002/
│   │   └── foto1.jpg
│   └── ...
└── (outros arquivos auxiliares)
```

## Erros esperados

| Erro | Causa | Ação |
|------|-------|------|
| 403 Forbidden | Pasta não compartilhada com service account | Log + orientar usuário a compartilhar |
| 404 Not Found | Pasta removida ou ID inválido | Log + alerta |
| 429 Rate Limit | Muitas requests | Retry com backoff; Google Drive: 1000 requests/100s |
| Formato inesperado | Planilha com colunas diferentes do esperado | Log parcial; importar o que conseguir; alertar campos faltantes |

## Quota Google Drive API

- 20.000 queries/dia (suficiente para catálogo de centenas de SKUs)
- Download de arquivos: sem limite explícito, mas respeitar rate limits
