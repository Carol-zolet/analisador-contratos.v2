import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from .models import Base, AnaliseContrato, AnaliseCache

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./default.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def criar_tabelas():
    """Garante que as tabelas existam na base de dados."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating database tables: {e}")


def buscar_analise_por_hash(hash_arquivo: str):
    """Retorna uma análise previamente salva com o mesmo hash."""
    db = SessionLocal()
    try:
        return (
            db.query(AnaliseCache)
            .filter(AnaliseCache.hash_arquivo == hash_arquivo)
            .order_by(desc(AnaliseCache.data_analise))
            .first()
        )
    finally:
        db.close()

def salvar_analise(nome_arquivo: str, score: int, resumo: dict, analise_ia: str):
    """Salva uma análise de contrato na base de dados."""
    db = SessionLocal()
    try:
        nova_analise = AnaliseContrato(
            nome_arquivo=nome_arquivo,
            score_risco=score,
            resumo_riscos=resumo,
            analise_completa_ia=analise_ia
        )
        db.add(nova_analise)
        db.commit()
        db.refresh(nova_analise)
        return nova_analise
    except Exception as e:
        print(f"Erro ao salvar na base de dados: {e}")
        db.rollback()
    finally:
        db.close()


def salvar_analise_cache(
    hash_arquivo: str,
    nome_arquivo: str,
    resumo_texto: str,
    resultado_regras: dict,
    analise_ia: str,
):
    """Guarda o resultado completo de uma análise para reutilização futura."""
    db = SessionLocal()
    try:
        registro = AnaliseCache(
            hash_arquivo=hash_arquivo,
            nome_arquivo=nome_arquivo,
            resumo_texto=resumo_texto,
            resultado_regras=resultado_regras,
            analise_ia=analise_ia,
        )
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro
    except Exception as e:
        print(f"Erro ao salvar cache: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def buscar_todas_analises():
    """Busca todas as análises salvas na base de dados, da mais recente para a mais antiga."""
    db = SessionLocal()
    try:
        analises = db.query(AnaliseContrato).order_by(desc(AnaliseContrato.data_analise)).all()
        return analises
    finally:
        db.close()