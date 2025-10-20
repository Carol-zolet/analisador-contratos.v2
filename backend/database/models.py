from sqlalchemy import Column, Integer, String, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class AnaliseContrato(Base):
    __tablename__ = 'analises_contratos'

    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String, index=True)
    score_risco = Column(Integer)
    resumo_riscos = Column(JSON)
    analise_completa_ia = Column(String)
    data_analise = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<AnÃ¡lise(id={self.id}, arquivo='{self.nome_arquivo}')>"

class Analise(Base):
    __tablename__ = "analises"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String, index=True)
    resultado = Column(JSON)
    clausulas_problematicas = Column(JSON)
    sugestoes = Column(JSON)
    data_analise = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class AnaliseCache(Base):
    __tablename__ = "analises_cache"
    __table_args__ = (UniqueConstraint("hash_arquivo", name="uq_hash_arquivo"),)

    id = Column(Integer, primary_key=True, index=True)
    hash_arquivo = Column(String, nullable=False, index=True)
    nome_arquivo = Column(String, nullable=False)
    resumo_texto = Column(String)
    resultado_regras = Column(JSON)
    analise_ia = Column(String)
    data_analise = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

