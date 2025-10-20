# Analisador de Contratos 26fit

Aplicação Full-Stack (FastAPI + React/Vite) para análise de contratos (PDF/DOCX) com regras e IA (Gemini), incluindo cache por hash.

## Estrutura
- `backend/`: FastAPI, SQLAlchemy, Alembic, extração de texto, integração Gemini
- `frontend/`: React + Vite, upload de arquivo, exibição de resultados

## Variáveis de Ambiente

Backend (FastAPI):
- `DATABASE_URL` (ex: `sqlite:///./default.db` ou Postgres)
- `ALLOWED_ORIGINS` (ex: `http://localhost:5173,https://seusite.vercel.app`)
- `ALLOWED_EXTS` (default: `pdf,docx`)
- `MAX_UPLOAD_MB` (default: `15`)
- `AUTO_CREATE_TABLES` (default: `true` para dev; em prod use Alembic)
- `GEMINI_API_KEY` (requerido para IA)

Frontend (Vite):
- `VITE_API_URL` (ex: `http://localhost:8000` ou URL pública do backend)

## Rodando Localmente

1) Backend
```powershell
cd .\backend
$env:ALLOWED_ORIGINS="http://localhost:5173"
$env:ALLOWED_EXTS="pdf,docx"
$env:MAX_UPLOAD_MB="15"
# opcional em dev: usa create_all
$env:AUTO_CREATE_TABLES="true"
uvicorn main:app --reload
```

2) Frontend
```powershell
cd .\frontend
npm install
$env:VITE_API_URL="http://localhost:8000"
npm run dev
```

## Migrações de Banco (Alembic)

- Configure `sqlalchemy.url` no `backend/alembic.ini` ou use env `SQLALCHEMY_URL`.
- Comandos:
```powershell
cd .\backend
alembic upgrade head
```

## Deploy

- Backend: hospedar em serviço de sua escolha (Railway/Render/Azure/VM). Defina envs acima e permita CORS para o domínio da Vercel.
- Frontend (Vercel):
  - Root Directory: `frontend`
  - Build Command: `npm run build`
  - Output Directory: `dist`
  - Env: `VITE_API_URL=https://SEU_BACKEND`

## Segurança e Limites
- Upload limitado por `MAX_UPLOAD_MB` (413 se exceder).
- CORS configurável (`ALLOWED_ORIGINS`).
- Extensões aceitas configuráveis (`ALLOWED_EXTS`), padrão PDF/DOCX.
- Sanitização da saída de IA com DOMPurify no frontend.

## Troubleshooting
- CORS bloqueado: ajuste `ALLOWED_ORIGINS` no backend e redeploy.
- 413 ao enviar arquivo: reduza o tamanho do arquivo ou aumente `MAX_UPLOAD_MB` com cautela.
- IA sem resposta: verifique `GEMINI_API_KEY` e conectividade; o sistema segue com análise de regras.
- Cache não aciona: o cache depende do hash do conteúdo; pequenas alterações geram novo registro.

---

Contribuições futuras: hashing/streaming por chunks, timeouts no Gemini, logs estruturados e IDs de requisição.
