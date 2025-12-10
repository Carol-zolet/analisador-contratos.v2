# backend/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
from pathlib import Path
import hashlib
import logging

# Garante que os módulos no diretório 'core' e 'database' sejam encontrados
sys.path.append(str(Path(__file__).parent))

# --- Importações Corrigidas e Simplificadas ---
# Carregamos apenas o necessário para o endpoint único
# 'extrair_texto_adendo' é a função que lê PDF e DOCX
from core.extractor import extrair_texto_adendo, extrair_clausulas_chave
from core.ai_analyzer import analisar_contrato_com_ia, configurar_api_gemini

# Funções e modelos do banco de dados
from database.database import (
    engine,
    buscar_analise_por_hash,
    salvar_analise_cache,
)
from database import models

# Cria as tabelas no banco de dados apenas se habilitado (dev)
if os.getenv("AUTO_CREATE_TABLES", "true").lower() in {"1", "true", "yes"}:
    models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Analisador de Contratos API")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [
    origin.strip()
    for origin in allowed_origins_env.split(",")
    if origin.strip()
] or ["http://localhost:5173"]

# Configuração do CORS para permitir a comunicação com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================================================
# ENDPOINT ÚNICO: ANÁLISE DE CONTRATO (Qualquer Formato)
# =======================================================

@app.post("/analisar/", tags=["Análise de Contratos"])
async def analisar_arquivo_endpoint(
    file: UploadFile = File(...),
    force_ai: bool = Query(False, description="Força reprocessamento da IA mesmo quando houver cache."),
):
    """Recebe um arquivo (PDF ou DOCX) e executa a análise completa."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo enviado sem nome.")
        
    # --- Validação de formatos suportados ---
    allowed_exts = {e.strip().lstrip('.').lower() for e in os.getenv('ALLOWED_EXTS', 'pdf,docx').split(',') if e.strip()}
    extensao = file.filename.split('.')[-1].lower()
    if extensao not in allowed_exts:
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado. Use PDF ou DOCX.")

    # Limite de tamanho do upload (MB), configurável por env
    try:
        max_mb = float(os.getenv("MAX_UPLOAD_MB", "15"))
    except ValueError:
        max_mb = 15.0
    max_bytes = int(max_mb * 1024 * 1024)
    
    caminho_temporario = None
    try:
        # Usa a extensão correta para o arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extensao}") as tmp:
            conteudo = await file.read()

            # Validação de tamanho (proteção simples de memória/abuso)
            if len(conteudo) > max_bytes:
                raise HTTPException(status_code=413, detail=f"Arquivo excede o limite de {int(max_mb)}MB.")
            hash_arquivo = hashlib.sha256(conteudo).hexdigest()

            cache_salvo = buscar_analise_por_hash(hash_arquivo)
            if cache_salvo and not force_ai:
                resultado_cache = cache_salvo.resultado_regras or {}
                score_cache = resultado_cache.get("score", 0)
                total_clausulas = resultado_cache.get(
                    "total_clausulas_problematicas",
                    len(resultado_cache.get("pontos_atencao", []) or []),
                )
                return {
                    "sucesso": True,
                    "nomeArquivo": file.filename,
                    "textoExtraido": cache_salvo.resumo_texto or "",
                    "scoreRisco": score_cache,
                    "nivelRisco": resultado_cache.get("nivel_risco", "DESCONHECIDO"),
                    "pontosAtencao": resultado_cache.get("pontos_atencao", []),
                    "totalClausulasProblem": total_clausulas,
                    "analiseIA": cache_salvo.analise_ia or "API de IA não configurada.",
                    "cacheHit": True,
                }

            tmp.write(conteudo)
            caminho_temporario = tmp.name
        
        # --- Usa a função de extração que lê PDF e DOCX ---
        texto_extraido, erro_extracao = extrair_texto_adendo(caminho_temporario)
        
        if erro_extracao:
            raise HTTPException(status_code=400, detail=erro_extracao)
        
        # --- Verificação de Mínimo de Texto ---
        if not texto_extraido or len(texto_extraido.strip()) < 100:
            raise HTTPException(status_code=400, detail="Texto extraído insuficiente. Verifique se o arquivo não é uma imagem escaneada.")
        
        # O resto da lógica de análise
        analise_regras = None
        if cache_salvo and force_ai and (cache_salvo.resultado_regras):
            # Reutiliza as regras do cache para evitar recomputo desnecessário
            analise_regras = cache_salvo.resultado_regras
        else:
            analise_regras = extrair_clausulas_chave(texto_extraido)
        
        analise_ia_texto = "API de IA não configurada."
        if configurar_api_gemini():
            analise_ia_texto = analisar_contrato_com_ia(texto_extraido)
        
        resumo_texto = texto_extraido[:500] + ("..." if len(texto_extraido) > 500 else "")

        resposta = {
            "sucesso": True,
            "nomeArquivo": file.filename,
            "textoExtraido": resumo_texto,
            "scoreRisco": analise_regras["score"],
            "nivelRisco": analise_regras["nivel_risco"],
            "pontosAtencao": analise_regras["pontos_atencao"],
            "totalClausulasProblem": analise_regras["total_clausulas_problematicas"],
            "analiseIA": analise_ia_texto
        }

        salvar_analise_cache(
            hash_arquivo=hash_arquivo,
            nome_arquivo=file.filename,
            resumo_texto=resumo_texto,
            resultado_regras=analise_regras,
            analise_ia=analise_ia_texto,
        )

        return resposta
        
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Erro inesperado no endpoint /analisar")
        # Evitar revelar detalhes internos ao cliente
        raise HTTPException(status_code=500, detail="Erro interno do servidor. Tente novamente mais tarde.")
    finally:
        if caminho_temporario and os.path.exists(caminho_temporario):
            os.unlink(caminho_temporario)

# ============================================
# ENDPOINT ROOT: VERIFICAÇÃO DE STATUS
# ============================================

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "API do Analisador de Contratos no ar!",
        "versao": "1.5 (Simplificada)",
        "endpoints": {
            "analise_contrato": "/analisar/",
            "docs": "/docs"
        }
    }