# core/adendo_ai_analyzer.py

import os
from dotenv import load_dotenv
from typing import Optional # ⬅️ ADICIONE ESTA LINHA

load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_DISPONIVEL = True
except ImportError:
    GEMINI_DISPONIVEL = False

def configurar_api_gemini_adendo():
    """Configura API do Google Gemini para análise de adendos"""
    if not GEMINI_DISPONIVEL:
        return False
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False


def analisar_adendo_com_ia(texto_adendo: str, texto_contrato_original: str = None) -> str:
    Análise de adendo contratual usando IA (Google Gemini)
    Compara com contrato original se fornecido
    """
    if not GEMINI_DISPONIVEL or not configurar_api_gemini_adendo():
        return "⚠️ API de IA não configurada. Configure GEMINI_API_KEY no arquivo .env"
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Prompt específico para adendos
        if texto_contrato_original:
            prompt = f"""
Você é um advogado especialista em direito contratual, especificamente em contratos de locação comercial.

Analise o ADENDO abaixo e compare com o CONTRATO ORIGINAL fornecido.

Sua análise deve identificar:

1. **ALTERAÇÕES CRÍTICAS**: Mudanças que prejudicam significativamente o locatário
2. **IMPACTO FINANCEIRO**: Aumentos de custos, novas taxas, alterações em valores
3. **DIREITOS SUPRIMIDOS**: Direitos originais que foram removidos ou limitados
4. **NOVAS OBRIGAÇÕES**: Responsabilidades adicionais impostas ao locatário
5. **CLÁUSULAS LEONINAS**: Cláusulas abusivas ou excessivamente favoráveis ao locador
6. **ASPECTOS POSITIVOS**: Se houver, destaque melhorias para o locatário
7. **RECOMENDAÇÃO FINAL**: Assinar, negociar ou recusar

**FORMATO DA RESPOSTA:**
Use markdown formatado com:
- ## para títulos principais
- ### para subtítulos
- ⚠️ para alertas críticos
- ✅ para pontos positivos
- 📊 para dados numéricos
- 💡 para recomendações

---

**CONTRATO ORIGINAL:**
{texto_contrato_original[:3000]}...

**ADENDO PROPOSTO:**
{texto_adendo}

---

**ANÁLISE JURÍDICA:**
"""
        else:
            prompt = f"""
Você é um advogado especialista em direito contratual, especificamente em contratos de locação comercial.

Analise o ADENDO CONTRATUAL abaixo.

Sua análise deve identificar:

1. **NATUREZA DO ADENDO**: O que está sendo alterado
2. **IMPACTO PARA O LOCATÁRIO**: Favorável, neutro ou desfavorável
3. **RISCOS JURÍDICOS**: Cláusulas problemáticas ou abusivas
4. **ASPECTOS FINANCEIROS**: Alterações em valores, taxas, multas
5. **DIREITOS E OBRIGAÇÕES**: Mudanças nas responsabilidades das partes
6. **RECOMENDAÇÃO**: Análise sobre assinar, negociar pontos específicos ou recusar

**FORMATO DA RESPOSTA:**
Use markdown formatado com:
- ## para títulos principais
- ### para subtítulos
- ⚠️ para alertas
- ✅ para pontos positivos
- 💡 para recomendações

---

**ADENDO:**
{texto_adendo}

---

**ANÁLISE JURÍDICA:**
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Erro ao processar análise com IA: {str(e)}"