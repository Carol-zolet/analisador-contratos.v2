import streamlit as st
import tempfile
import os
import time
from extractor import extrair_texto_local, extrair_clausulas_chave
from ai_analyzer import analisar_contrato_com_ia, AI_ENABLED
from database import salvar_analise

st.set_page_config(
    page_title="Analisador de Contratos - 26fit", 
    page_icon="📄", 
    layout="wide"
)

# --- CSS PERSONALIZADO (TEMA 26 FIT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Oculta elementos padrão do Streamlit */
    #MainMenu, footer, header { visibility: hidden; }

    /* Estilos gerais */
    h1, h2, h3, p, div, span, button, input { font-family: 'Inter', sans-serif; }
    h1 { color: #1a1a1a; font-weight: 800; margin-bottom: 1.5rem; }
    h2 { color: #1a1a1a; font-weight: 700; margin-top: 2rem; }

    /* Cabeçalho do app */
    .header-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .header-box h1 {
        color: #ffd200;
        font-size: 2.5rem;
        margin: 0;
    }
    .header-box p {
        color: #ffffff;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }

    /* Loader personalizado */
    .stProgress .st-bd {
        height: 10px;
        border-radius: 5px;
    }
    .stProgress .st-bs {
        background: linear-gradient(90deg, #ffd200, #ffed4e);
        height: 100%;
    }

    /* Cards das seções */
    .stat-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border-left: 4px solid #ffd200;
        margin-bottom: 1rem;
    }
    .stat-card h3 {
        color: #1a1a1a;
        font-weight: 700;
        font-size: 1.3rem;
        margin-top: 0;
    }
    .stat-card p {
        color: #555555;
        font-size: 1rem;
        margin-bottom: 0;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1a1a1a;
    }
    .risk-high {
        color: #ff4d4d;
    }
    .risk-medium {
        color: #ff9900;
    }
    .risk-low {
        color: #4dff4d;
    }

    /* Containers de alertas */
    .alert-critical {
        background: linear-gradient(to right, rgba(255,77,77,0.1), rgba(255,77,77,0.02));
        border-left: 4px solid #ff4d4d;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .alert-warning {
        background: linear-gradient(to right, rgba(255,153,0,0.1), rgba(255,153,0,0.02));
        border-left: 4px solid #ff9900;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .alert-info {
        background: linear-gradient(to right, rgba(0,153,255,0.1), rgba(0,153,255,0.02));
        border-left: 4px solid #0099ff;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .alert-title {
        font-weight: 700;
        margin-bottom: 0.3rem;
        font-size: 1.1rem;
    }
    .alert-detail {
        margin: 0.5rem 0;
        opacity: 0.9;
    }
    .alert-context {
        background: rgba(255,255,255,0.5);
        padding: 0.75rem;
        border-radius: 4px;
        font-style: italic;
        font-size: 0.9rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("""
<div class="header-box">
    <h1>📄 Analisador de Contratos</h1>
    <p>Faça upload do contrato para análise automática de riscos com IA</p>
</div>
""", unsafe_allow_html=True)

# --- CORPO PRINCIPAL ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Upload do Contrato")
    uploaded_file = st.file_uploader("Selecione um contrato em PDF", type=["pdf"])
    
    if uploaded_file:
        # Criar arquivo temporário para processamento
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name
        
        with st.spinner('📄 Extraindo texto do PDF...'):
            texto_contrato, erro = extrair_texto_local(temp_path)
            # Removendo arquivo temporário
            os.unlink(temp_path)
            
            if erro:
                st.error(f"Erro ao processar o PDF: {erro}")
                st.stop()
            
            if not texto_contrato or len(texto_contrato) < 500:
                st.error("O arquivo parece estar vazio ou não contém texto suficiente para análise.")
                st.stop()
        
        with st.spinner('🔍 Analisando cláusulas e riscos...'):
            # Barra de progresso animada
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Análise automática por regras
            resultados = extrair_clausulas_chave(texto_contrato)
        
        # Checkbox para análise por IA
        usar_ia = st.checkbox("Realizar análise detalhada com IA", value=True)
        analise_ia_texto = ""
        
        if usar_ia and st.button("📊 Gerar Análise Completa"):
            with st.spinner('🧠 Processando com IA avançada...'):
                if AI_ENABLED:
                    analise_ia_texto = analisar_contrato_com_ia(texto_contrato)
                else:
                    analise_ia_texto = "Módulo de IA não habilitado. Consulte o administrador."
            
            # Salvar na base de dados
            if resultados and analise_ia_texto:
                try:
                    salvar_analise(
                        nome_arquivo=uploaded_file.name,
                        score=resultados["resumo_riscos"]["score_risco"],
                        resumo=resultados,
                        analise_ia=analise_ia_texto
                    )
                    st.success("✅ Análise salva com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar análise: {e}")
        
        # Exibição do texto extraído
        with st.expander("Ver texto extraído do contrato"):
            st.text_area("Conteúdo completo", texto_contrato, height=400)

with col2:
    if uploaded_file and resultados:
        # --- RESUMO RISCOS ---
        st.subheader("Resumo de Riscos")
        
        col_score, col_rec = st.columns(2)
        with col_score:
            score = resultados["resumo_riscos"]["score_risco"]
            risk_class = "risk-low" if score < 15 else "risk-medium" if score < 30 else "risk-high"
            st.markdown(f"""
            <div class="stat-card">
                <h3>Score de Risco</h3>
                <div class="metric-value {risk_class}">{score}/100</div>
                <p>Baseado em {resultados["resumo_riscos"]["total_criticos"]} riscos críticos, 
                   {resultados["resumo_riscos"]["total_graves"]} graves e 
                   {resultados["resumo_riscos"]["total_moderados"]} moderados</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_rec:
            recomendacao = resultados["resumo_riscos"]["recomendacao_geral"]
            rec_color = "risk-low" if recomendacao == "✅ APARENTEMENTE SEGURO" else "risk-medium" if recomendacao == "⚡ REVISAR COM CUIDADO" else "risk-high"
            st.markdown(f"""
            <div class="stat-card">
                <h3>Recomendação</h3>
                <div class="metric-value {rec_color}">{recomendacao}</div>
                <p>Avaliação baseada em análise automática de cláusulas</p>
            </div>
            """, unsafe_allow_html=True)
        
        # --- DADOS ESSENCIAIS ---
        if resultados["dados_essenciais"]:
            st.subheader("📋 Dados Essenciais")
            for dado in resultados["dados_essenciais"]:
                st.markdown(f"**{dado['tipo']}:** {dado['valor']}")
        
        # --- ALERTAS CRÍTICOS ---
        if resultados["alertas_criticos"]:
            st.subheader("🚨 Alertas Críticos")
            for alerta in resultados["alertas_criticos"]:
                st.markdown(f"""
                <div class="alert-critical">
                    <div class="alert-title">⛔ {alerta['categoria']}</div>
                    <div class="alert-detail">{alerta['detalhe']}</div>
                    <div class="alert-context">{alerta['contexto']}...</div>
                </div>
                """, unsafe_allow_html=True)
        
        # --- ALERTAS GRAVES ---
        if resultados["alertas_graves"]:
            st.subheader("⚠️ Alertas Graves")
            for alerta in resultados["alertas_graves"]:
                st.markdown(f"""
                <div class="alert-warning">
                    <div class="alert-title">⚠️ {alerta['categoria']}</div>
                    <div class="alert-detail">{alerta['detalhe']}</div>
                    <div class="alert-context">{alerta['contexto']}...</div>
                </div>
                """, unsafe_allow_html=True)
        
        # --- ALERTAS MODERADOS ---
        if resultados["alertas_moderados"]:
            st.subheader("ℹ️ Alertas Moderados")
            for alerta in resultados["alertas_moderados"]:
                st.markdown(f"""
                <div class="alert-info">
                    <div class="alert-title">ℹ️ {alerta['categoria']}</div>
                    <div class="alert-detail">{alerta['detalhe']}</div>
                    <div class="alert-context">{alerta['contexto']}...</div>
                </div>
                """, unsafe_allow_html=True)
        
        # --- PONTOS POSITIVOS ---
        if resultados["pontos_positivos"]:
            st.subheader("✅ Pontos Positivos")
            for ponto in resultados["pontos_positivos"]:
                st.success(ponto)
        
        # --- ANÁLISE DE IA ---
        if analise_ia_texto:
            st.subheader("🧠 Análise Jurídica Avançada (IA)")
            st.markdown(analise_ia_texto)