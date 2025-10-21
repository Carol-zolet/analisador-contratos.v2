import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

PROMPT_IA = """
Você é um advogado especialista em contratos de locação comercial. Analise o contrato abaixo protegendo o LOCATÁRIO, utilizando uma abordagem baseada em regras e melhores práticas do direito imobiliário.

**TEXTO DO CONTRATO:**
{texto}

**ESTRUTURA DA ANÁLISE (DETALHADA E ORIENTADA POR REGRAS):**

## 📊 RESUMO EXECUTIVO
- Avaliação geral do contrato em 2-3 linhas
- **Nível de risco geral:** CRÍTICO / ALTO / MÉDIO / BAIXO
- **Recomendação principal:** [ação objetiva]

## ⚖️ ANÁLISE POR REGRAS ESSENCIAIS
Avalie cada item abaixo, indicando se está presente, ausente, ou inadequado. Justifique brevemente e aponte riscos e sugestões:
- **Cláusula de rescisão**
- **Multas e penalidades**
- **Reajuste de aluguel**
- **Garantias locatícias** (caução, fiador, seguro)
- **Direito de renovação**
- **Responsabilidade por benfeitorias**
- **Despesas ordinárias e extraordinárias**
- **Prazo contratual**
- **Cláusula de exclusividade**
- **Foro para resolução de conflitos**

## ⚠️ RISCOS CRÍTICOS E PONTOS DE ATENÇÃO
Liste até 7 riscos ou pontos de atenção, cada um com:
- **[NÍVEL]** Título do Risco (Página X, se possível)
    - **Descrição:** Explique o risco em 1-2 linhas
    - **Impacto:** Consequências práticas para o locatário
    - **Solução/Recomendação:** O que pode ser feito para mitigar

## 🎯 AÇÕES RECOMENDADAS
Liste 5-7 ações prioritárias e práticas que o locatário deve tomar antes de assinar o contrato.

## 📚 FUNDAMENTAÇÃO LEGAL
Se possível, cite os principais artigos da Lei do Inquilinato (Lei 8.245/91) ou outras normas aplicáveis para cada ponto relevante.

**IMPORTANTE:**
- Seja direto, use **negrito** para destacar pontos-chave
- Estruture a resposta em tópicos claros
- Use linguagem acessível, sem juridiquês excessivo
- Limite a resposta a no máximo 1200 palavras
"""

def configurar_api_gemini():
    # Tenta ler da variável de ambiente primeiro
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    print(f"DEBUG: GEMINI_API_KEY={os.getenv('GEMINI_API_KEY')[:10] if os.getenv('GEMINI_API_KEY') else 'None'}...")
    print(f"DEBUG: GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY')[:10] if os.getenv('GOOGLE_API_KEY') else 'None'}...")
    
    # Se não encontrar, tenta ler do arquivo secreto do Render
    if not api_key:
        try:
            secret_path = "/etc/secrets/GEMINI_API_KEY"
            print(f"DEBUG: Tentando ler de {secret_path}")
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    api_key = f.read().strip()
                print(f"DEBUG: Arquivo secreto lido, key={api_key[:10] if api_key else 'vazio'}...")
            else:
                print("DEBUG: Arquivo secreto não existe")
        except Exception as e:
            print(f"DEBUG: Erro ao ler arquivo secreto: {e}")
    
    if not api_key:
        print("DEBUG: Nenhuma API key encontrada!")
        return False
    
    try:
        genai.configure(api_key=api_key)
        print("DEBUG: API configurada com sucesso!")
        return True
    except Exception as e:
        print(f"DEBUG: Erro ao configurar API: {e}")
        return False

def analisar_contrato_com_ia(texto: str) -> str:
    if not configurar_api_gemini():
        return "❌ **Erro:** A chave da API do Gemini não foi configurada."
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        resposta = model.generate_content(PROMPT_IA.format(texto=texto))
        return resposta.text
    except Exception as e:
        # Log detalhado do erro para debugging
        import traceback
        erro_detalhado = traceback.format_exc()
        print(f"ERRO GEMINI: {erro_detalhado}")
        return f"❌ **Erro na análise com Gemini:** {str(e)}"