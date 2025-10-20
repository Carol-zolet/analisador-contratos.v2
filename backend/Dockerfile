# Estágio 1: Builder com dependências de compilação
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema necessárias para o PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Estágio 2: Imagem final de produção
FROM python:3.11-slim

WORKDIR /app

# Copia apenas as dependências instaladas do estágio anterior
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copia o código da sua aplicação
COPY . .

# Expõe a porta que a API irá usar
EXPOSE 8000

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]