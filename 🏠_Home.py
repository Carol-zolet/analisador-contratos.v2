import streamlit as st
from database import criar_tabelas

# Cria as tabelas na inicialização, se não existirem
criar_tabelas()

st.set_page_config(
    layout="wide",
    page_title="Analisador 26fit",
    page_icon="https://www.26fit.com.br/imagens/logo.png"
)

# --- CSS PERSONALIZADO (TEMA 26 FIT - VERSÃO PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    #MainMenu, footer, header { visibility: hidden; }
    
    .main {
        background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
    }

    .main .block-container { 
        padding: 2rem; 
        max-width: 1200px;
    }

    h1 {
        color: #1a1a1a;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3rem;
    }

    .stMarkdown {
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- LAYOUT DA PÁGINA ---
st.markdown("""
<div class="hero-section">
    <div class="subheader">Ferramenta Interna 26 FIT</div>
    <h1>Analisador Jurídico de Contratos</h1>
    <p>
        O assistente de IA para acelerar a revisão de contratos de locação, 
        identificando riscos e pontos de atenção com foco na proteção da nossa marca.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">⚙️</div>
        <h3>Diagnóstico por Regras</h3>
        <p>Um motor de regras varre o documento em busca de mais de 15 tipos de cláusulas de risco pré-definidas, gerando um score de perigo instantâneo.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">🧠</div>
        <h3>Análise Profunda com IA</h3>
        <p>O Google Gemini realiza uma análise jurídica completa, interpretando o contexto, identificando ambiguidades e sugerindo alterações nas cláusulas.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="cta-box">
    <h2>Pronto para Começar?</h2>
    <p>Navegue para a página "Analisador" na barra lateral para fazer o upload do seu primeiro contrato.</p>
</div>
""", unsafe_allow_html=True)