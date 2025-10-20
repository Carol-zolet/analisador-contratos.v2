from core.extractor import extrair_texto_local

# Teste com seu PDF
texto, erro = extrair_texto_local("caminho/do/seu/contrato.pdf")

if erro:
    print(f"❌ Erro: {erro}")
else:
    print(f"✅ Texto extraído com sucesso!")
    print(f"📄 Total de caracteres: {len(texto)}")
    print(f"📝 Preview: {texto[:200]}...")