import streamlit as st
import pandas as pd
from database import buscar_todas_analises

st.set_page_config(layout="wide", page_title="Dashboard de Análises")

# --- CSS PERSONALIZADO (TEMA 26 FIT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Oculta elementos padrão do Streamlit */
    #MainMenu, footer, header { visibility: hidden; }

    /* Fundo geral */
    .main { background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%); }

    /* Container principal */
    .main .block-container { max-width: 1400px; }

    /* Tipografia */
    h1, h2, h3, p, div, span, button, input { font-family: 'Inter', sans-serif; }
    h1 { color: #1a1a1a; font-weight: 800; font-size: 3rem; }
    h2 { color: #1a1a1a; font-weight: 700; margin-top: 2rem; }
    h3 { color: #1a1a1a; font-weight: 700; }

    /* DataFrames */
    [data-testid="stDataFrame"] thead tr th {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: #ffd200 !important;
        font-weight: 700;
        text-transform: uppercase;
    }
    [data-testid="stDataFrame"] tbody tr:hover { background-color: #fffbf0; }

    /* Card de estatísticas */
    .stats-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.06);
        border-left: 4px solid #ffd200;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Dashboard de Análises Salvas")

if st.button("🔄 Recarregar Dados"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def carregar_dados():
    analises = buscar_todas_analises()
    dados_formatados = [
        {
            "ID": a.id, "Arquivo": a.nome_arquivo, "Score de Risco": a.score_risco,
            "Data": a.data_analise.strftime("%d/%m/%Y %H:%M"),
            "Recomendação": a.resumo_riscos.get("resumo_riscos", {}).get("recomendacao_geral", "N/A"),
            "Análise IA": a.analise_completa_ia
        } for a in analises
    ]
    return pd.DataFrame(dados_formatados)

df = carregar_dados()

if df.empty:
    st.warning("Nenhuma análise foi salva no banco de dados ainda.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("Total de Análises", len(df))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("Score Médio de Risco", f"{df['Score de Risco'].mean():.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("Análise Mais Recente", df["Data"].iloc[0])
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 Pesquisar e Ver Detalhes")
    
    filtro_arquivo = st.text_input("Filtrar por nome do arquivo:")
    df_filtrado = df[df["Arquivo"].str.contains(filtro_arquivo, case=False, na=False)] if filtro_arquivo else df

    st.dataframe(df_filtrado[["ID", "Arquivo", "Score de Risco", "Recomendação", "Data"]], hide_index=True)

    opcoes_analise = [f"ID {row.ID}: {row.Arquivo}" for _, row in df_filtrado.iterrows()]
    analise_selecionada = st.selectbox("Selecione uma análise para ver os detalhes:", options=opcoes_analise)

    if analise_selecionada:
        id_selecionado = int(analise_selecionada.split(":")[0].replace("ID", "").strip())
        dados_completos = df[df["ID"] == id_selecionado].iloc[0]
        with st.expander(f"Análise Completa da IA para: **{dados_completos['Arquivo']}**", expanded=True):
            st.markdown(dados_completos["Análise IA"])