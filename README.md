# Webhook get_date_time (versão final)

## 🚀 Descrição
Webhook simples em Flask que retorna a data e hora atuais no formato ISO 8601, configurado com fuso horário `America/Sao_Paulo`.

## 🧩 Endpoints
- `/` → Página de status ("Webhook funcionando!")
- `/get-datetime` → Retorna data e hora atual em JSON

### Exemplo de resposta:
```json
{
  "datetime": "2025-10-15T00:35:42-0300",
  "formatted": "15/10/2025 00:35:42",
  "timezone": "America/Sao_Paulo",
  "status": "success"
}
```

## ⚙️ Deploy no Railway
1. Acesse https://railway.app
2. Crie novo projeto → *Deploy from ZIP*
3. Envie este arquivo `.zip`
4. Após o deploy, acesse:
   `https://seu-projeto.up.railway.app/get-datetime`
