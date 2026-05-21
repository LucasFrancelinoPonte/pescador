# Form Pescador

MVP em Flask para coleta socioeconômica de pescadores, com foco no formulário multi-step, login simples e interface pronta para deploy na Vercel.

## Rodar localmente

1. Crie e ative o ambiente virtual.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente com base em `.env.example`.
4. Inicie a aplicação local com:

```bash
python app.py
```

Se preferir, também funciona com `flask --app app run`.

## Configuração de ambiente

Copie `.env.example` para `.env` e ajuste, no mínimo:

- `SECRET_KEY`
- `SESSION_SECRET`
- `FLASK_ENV`

Em produção, defina também `SESSION_COOKIE_SECURE=true`.

## Deploy na Vercel

1. Garanta que `vercel.json` e `api/index.py` estejam no repositório.
2. Instale as dependências.
3. Execute:

```bash
vercel
```

O app usa `create_app()` e expõe a aplicação Flask sem `app.run()` no entrypoint serverless.

O arquivo `vercel.json` mantém o fallback de rotas para que o refresh das páginas do Flask não quebre em 404.

## Estrutura principal

- `api/index.py`: entrypoint serverless da Vercel.
- `app/routes/`: blueprints Flask.
- `app/templates/`: telas Jinja2.
- `app/static/`: CSS, JS e outros assets.

## Observações do MVP

- O formulário principal continua frontend-first.
- A persistência definitiva ainda não está ativa.
- Integrações futuras com banco, auditoria, exportação e importação devem entrar nos blocos comentados da factory e das rotas auxiliares.