import re
import pdfplumber
import docx  # ⬅️ NOVA IMPORTAÇÃO
from typing import Dict, List, Tuple

def extrair_texto_local(caminho_pdf: str) -> Tuple[str, str]:
    """Extrai texto de um PDF local"""
    try:
        texto = ""
        
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto += texto_pagina + "\n"
        
        if not texto.strip():
            return "", "PDF vazio ou texto não extraível (pode ser imagem escaneada)"
        
        return texto, ""
        
    except Exception as e:
        return "", f"Erro ao extrair texto do PDF: {str(e)}"

# ==============================================================================
# ⬇️ FUNÇÃO NOVA E CORRIGIDA QUE FALTAVA ⬇️
# ==============================================================================
def extrair_texto_adendo(caminho_arquivo: str) -> Tuple[str, str]:
    """Extrai texto de diferentes tipos de arquivo (PDF, DOCX)."""
    try:
        texto = ""
        caminho_lower = caminho_arquivo.lower()

        if caminho_lower.endswith('.pdf'):
            # Reutiliza a mesma lógica da função original para PDFs
            with pdfplumber.open(caminho_arquivo) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n"

        elif caminho_lower.endswith('.docx'):
            # Usa a nova biblioteca para ler arquivos .docx
            documento = docx.Document(caminho_arquivo)
            for paragraph in documento.paragraphs:
                texto += paragraph.text + "\n"
        
        else:
            return "", "Formato de arquivo não suportado. Use PDF ou DOCX."

        if not texto.strip():
            return "", "Arquivo vazio ou texto não extraível."
            
        return texto, ""
        
    except Exception as e:
        return "", f"Erro ao extrair texto do arquivo: {str(e)}"


def extrair_clausulas_chave(texto: str) -> Dict:
    """
    Análise COMPLETA de contratos de locação comercial para ACADEMIAS.
    Identifica cláusulas problemáticas em 15+ categorias críticas.
    """
    score = 0
    pontos_atencao = []
    texto_lower = texto.lower()
    
    # ============================================
    # CATEGORIA 1: PRAZO E DIREITO À RENOVAÇÃO
    # ============================================
    
    # 1.1 Prazo inferior a 5 anos (impede ação renovatória)
    prazo_match = re.search(r'prazo.*?(\d+)\s*(ano|anos|meses|mês)', texto_lower)
    if prazo_match:
        numero = int(prazo_match.group(1))
        unidade = prazo_match.group(2)
        meses_totais = numero if 'mês' in unidade or 'meses' in unidade else numero * 12
        
        if meses_totais < 60:  # Menos de 5 anos
            score += 25
            pontos_atencao.append({
                "tipo": "CRÍTICO",
                "categoria": "Prazo Contratual",
                "descricao": f"Prazo de apenas {numero} {unidade} - inferior ao mínimo de 5 anos para direito à renovação compulsória",
                "impacto": "Perda do ponto comercial e de todo investimento em equipamentos, reformas e clientela ao final do contrato",
                "artigo_legal": "Art. 51, Lei 8.245/91",
                "recomendacao": "EXIGIR prazo mínimo de 5 anos ininterruptos ou garantia de renovação automática"
            })
    
    # 1.2 Cláusula de renúncia ao direito de renovação
    if re.search(r'(renuncia|abdica|dispensa).*direito.*(renova[çc][ãa]o|prorrogação)', texto_lower) or \
       re.search(r'sem.*direito.*(renova[çc][ãa]o|prorrogação)', texto_lower):
        score += 30
        pontos_atencao.append({
            "tipo": "CRÍTICO",
            "categoria": "Direito à Renovação",
            "descricao": "Contrato contém renúncia expressa ao direito de renovação compulsória",
            "impacto": "Locador pode exigir desocupação ao término sem qualquer compensação, mesmo com investimentos realizados",
            "artigo_legal": "Art. 51 e 71, Lei 8.245/91",
            "recomendacao": "REMOVER esta cláusula e incluir direito expresso à Ação Renovatória"
        })
    
    # 1.3 Prazo de aviso prévio curto
    aviso_match = re.search(r'aviso.*pr[ée]vio.*?(\d+)\s*(dia|mês)', texto_lower)
    if aviso_match and int(aviso_match.group(1)) < 90:
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Aviso Prévio",
            "descricao": f"Prazo de aviso prévio de apenas {aviso_match.group(1)} {aviso_match.group(2)}",
            "impacto": "Prazo insuficiente para realocação de academia (equipamentos, transferência de alunos, novo ponto)",
            "recomendacao": "Negociar aviso prévio mínimo de 180 dias para ambas as partes"
        })
    
    # ============================================
    # CATEGORIA 2: MULTAS E PENALIDADES
    # ============================================
    
    # 2.1 Multa rescisória abusiva
    multa_rescisao = re.search(r'multa.*rescis[óo]ria.*(6|12|18|24|seis|doze|dezoito|vinte e quatro)\s*(mes|alugu[eé])', texto_lower)
    if multa_rescisao:
        score += 30
        pontos_atencao.append({
            "tipo": "CRÍTICO",
            "categoria": "Multa Rescisória",
            "descricao": "Multa rescisória abusiva identificada (6+ aluguéis)",
            "impacto": "Oneração excessiva em caso de necessidade de rescisão (ex: problemas estruturais, mudança de negócio)",
            "artigo_legal": "Art. 4º, Lei 8.245/91 e CDC",
            "recomendacao": "Limitar multa a 3 aluguéis, calculada proporcionalmente ao tempo restante do contrato"
        })
    
    # 2.2 Multa por atraso superior a 10%
    multa_atraso = re.search(r'multa.*(atraso|mora|inadimpl[êe]ncia).*(20|30|40|50|vinte|trinta)%', texto_lower)
    if multa_atraso:
        score += 20
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Multa por Atraso",
            "descricao": "Multa moratória superior ao limite legal de 10%",
            "impacto": "Oneração excessiva em caso de eventual atraso pontual no pagamento",
            "artigo_legal": "Art. 52, §1º, CDC",
            "recomendacao": "Limitar multa a 10% + juros de 1% a.m. + correção monetária"
        })
    
    # 2.3 Juros abusivos
    juros_match = re.search(r'juros.*?(\d+)%', texto_lower)
    if juros_match and int(juros_match.group(1)) > 1:
        score += 10
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Juros Moratórios",
            "descricao": f"Juros de mora de {juros_match.group(1)}% ao mês (acima do legal)",
            "impacto": "Juros excessivos em caso de atraso no pagamento",
            "artigo_legal": "Art. 406, Código Civil",
            "recomendacao": "Limitar juros a 1% ao mês"
        })
    
    # ============================================
    # CATEGORIA 3: BENFEITORIAS E REFORMAS
    # ============================================
    
    # 3.1 Proibição de indenização por benfeitorias
    if re.search(r'benfeitoria.*(sem|n[ãa]o).*indeniza[çc][ãa]o', texto_lower) or \
       re.search(r'n[ãa]o.*ter[áa].*direito.*indeniza[çc][ãa]o.*benfeitoria', texto_lower):
        score += 25
        pontos_atencao.append({
            "tipo": "CRÍTICO",
            "categoria": "Benfeitorias",
            "descricao": "Contrato proíbe indenização por benfeitorias úteis e necessárias",
            "impacto": "Academia investe em reformas, instalações elétricas, hidráulicas, piso, espelhos, ar-condicionado e perde tudo sem indenização",
            "artigo_legal": "Arts. 35 e 36, Lei 8.245/91",
            "recomendacao": "INCLUIR direito à indenização ou retenção por benfeitorias úteis/necessárias autorizadas por escrito"
        })
    
    # 3.2 Necessidade de autorização prévia para qualquer alteração
    if re.search(r'(qualquer|toda).*altera[çc][ãa]o.*autoriza[çc][ãa]o.*pr[ée]via', texto_lower):
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Autorização para Reformas",
            "descricao": "Necessidade de autorização prévia para qualquer alteração no imóvel",
            "impacto": "Limitação na personalização da academia (pintura, fixação de espelhos, instalação de equipamentos)",
            "recomendacao": "Especificar que benfeitorias não estruturais (pintura, decoração, instalações) podem ser feitas mediante notificação, sem necessidade de autorização"
        })
    
    # 3.3 Obrigação de remover benfeitorias ao final
    if re.search(r'(remover|retirar|desfazer).*benfeitoria', texto_lower):
        score += 20
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Remoção de Benfeitorias",
            "descricao": "Obrigação de remover benfeitorias ao final do contrato",
            "impacto": "Custo adicional de remoção de instalações fixas (espelhos, pisos emborrachados, ar-condicionado) + custo de restauração",
            "recomendacao": "Negociar que benfeitorias autorizadas permaneçam no imóvel sem ônus de remoção"
        })
    
    # 3.4 Limitação excessiva de carga estrutural
    if re.search(r'(proib|n[ãa]o.*permit).*carga.*(estrutural|piso)', texto_lower):
        score += 18
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Carga Estrutural",
            "descricao": "Restrições sobre carga estrutural podem inviabilizar equipamentos de musculação",
            "impacto": "Impossibilidade de instalar equipamentos pesados essenciais para operação da academia",
            "recomendacao": "Solicitar laudo estrutural atestando capacidade mínima de 500 kg/m² e incluir no contrato"
        })
    
    # ============================================
    # CATEGORIA 4: VENDA DO IMÓVEL
    # ============================================
    
    # 4.1 Cláusula de rescisão automática em caso de venda
    if re.search(r'(venda|aliena[çc][ãa]o).*im[óo]vel.*(rescis[ãa]o|rescind|extingue)', texto_lower):
        score += 30
        pontos_atencao.append({
            "tipo": "CRÍTICO",
            "categoria": "Venda do Imóvel",
            "descricao": "Contrato pode ser rescindido automaticamente se o imóvel for vendido",
            "impacto": "Perda súbita do ponto comercial, clientela e investimentos realizados sem indenização",
            "artigo_legal": "Art. 8º, Lei 8.245/91 - direito de preferência",
            "recomendacao": "INCLUIR cláusula de direito de preferência na compra + manutenção do contrato pelo novo proprietário (art. 8º, Lei 8.245/91)"
        })
    
    # 4.2 Ausência de direito de preferência na compra
    if not re.search(r'direito.*prefer[êe]ncia', texto_lower):
        score += 20
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Direito de Preferência",
            "descricao": "Ausência de cláusula de direito de preferência na compra do imóvel",
            "impacto": "Locatário não terá prioridade de compra caso proprietário decida vender",
            "artigo_legal": "Art. 27 e 33, Lei 8.245/91",
            "recomendacao": "INCLUIR direito de preferência com prazo mínimo de 30 dias para manifestação"
        })
    
    # 4.3 Direito do locador de mostrar o imóvel sem restrições
    if re.search(r'(mostrar|visita).*im[óo]vel.*(qualquer|todo).*hor[áa]rio', texto_lower):
        score += 12
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Visitação do Imóvel",
            "descricao": "Locador pode mostrar imóvel a qualquer momento sem restrições",
            "impacto": "Interrupção das atividades da academia e constrangimento aos alunos",
            "recomendacao": "Limitar visitas a horários específicos (ex: após 20h) e mediante aviso prévio de 48h"
        })
    
    # ============================================
    # CATEGORIA 5: USO E DESTINAÇÃO DO IMÓVEL
    # ============================================
    
    # 5.1 Restrição de horário de funcionamento
    horario_match = re.search(r'funcionamento.*(\d{1,2}).*às.*(\d{1,2})', texto_lower)
    if horario_match:
        hora_inicial = int(horario_match.group(1))
        hora_final = int(horario_match.group(2))
        if hora_final < 22 or hora_inicial > 6:
            score += 25
            pontos_atencao.append({
                "tipo": "CRÍTICO",
                "categoria": "Horário de Funcionamento",
                "descricao": f"Restrição de horário de funcionamento ({hora_inicial}h às {hora_final}h)",
                "impacto": "Inviabiliza operação de academia 24h ou horários estendidos (madrugada/manhã cedo), reduzindo receita",
                "recomendacao": "Negociar funcionamento 24h ou mínimo de 5h às 23h, essencial para academias modernas"
            })
    
    # 5.2 Proibição de atividades essenciais para academia
    if re.search(r'(proib|vedam|n[ãa]o.*permit).*(música|som|aparelho.*sonoro)', texto_lower):
        score += 20
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Uso do Imóvel - Som",
            "descricao": "Proibição ou restrição severa de som/música ambiente",
            "impacto": "Som ambiente é essencial para ambiente de academia (aulas coletivas, motivação)",
            "recomendacao": "Negociar permissão para som em decibéis razoáveis (até 70dB) com isolamento acústico"
        })
    
    # 5.3 Limitação de capacidade de pessoas
    capacidade_match = re.search(r'capacidade.*m[áa]xima.*?(\d+).*pessoas', texto_lower)
    if capacidade_match and int(capacidade_match.group(1)) < 50:
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Capacidade do Imóvel",
            "descricao": f"Limitação de capacidade a apenas {capacidade_match.group(1)} pessoas",
            "impacto": "Restringe crescimento da base de alunos e receita da academia",
            "recomendacao": "Negociar capacidade proporcional à área (mínimo 1 pessoa a cada 5m²)"
        })
    
    # 5.4 Proibição de sublocação/franquia
    if re.search(r'(proib|vedam|n[ãa]o.*permit).*subloca[çc][ãa]o', texto_lower):
        score += 10
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Sublocação",
            "descricao": "Proibição total de sublocação ou parcerias comerciais",
            "impacto": "Impede parcerias com personal trainers, fisioterapeutas, nutricionistas (receitas complementares)",
            "recomendacao": "Permitir sublocação parcial de espaços mediante autorização prévia"
        })
    
    # ============================================
    # CATEGORIA 6: RESPONSABILIDADES E DESPESAS
    # ============================================
    
    # 6.1 IPTU por conta do locatário
    if re.search(r'locat[áa]rio.*responsável.*iptu', texto_lower) or \
       re.search(r'iptu.*[ée].*encargo.*locat[áa]rio', texto_lower):
        score += 10
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "IPTU",
            "descricao": "IPTU por conta do locatário (embora comum, é obrigação legal do proprietário)",
            "impacto": "Custo adicional mensal que pode variar conforme reavaliação do imóvel",
            "artigo_legal": "Art. 22, II, Lei 8.245/91 - IPTU pode ser transferido",
            "recomendacao": "Se aceitar pagar IPTU, exigir que seja descontado do aluguel ou negociar valor fixo mensal"
        })
    
    # 6.2 Despesas extraordinárias de condomínio
    if re.search(r'locat[áa]rio.*responsável.*(despesa|encargo).*extraordin[áa]ri', texto_lower):
        score += 20
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Despesas Extraordinárias",
            "descricao": "Despesas extraordinárias de condomínio por conta do locatário",
            "impacto": "Custos imprevisíveis (reformas estruturais, pintura externa, elevador) podem onerar o negócio",
            "artigo_legal": "Art. 22, VIII, Lei 8.245/91",
            "recomendacao": "REMOVER esta cláusula - despesas extraordinárias são de responsabilidade do proprietário"
        })
    
    # 6.3 Seguro incêndio estrutural por conta do locatário
    if re.search(r'locat[áa]rio.*responsável.*seguro.*inc[êe]ndio', texto_lower):
        score += 8
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Seguro Incêndio",
            "descricao": "Seguro incêndio estrutural por conta do locatário",
            "impacto": "Custo adicional que protege o patrimônio do proprietário, não do locatário",
            "recomendacao": "Proprietário deve arcar com seguro estrutural; locatário faz seguro de equipamentos e responsabilidade civil"
        })
    
    # 6.4 Manutenções estruturais por conta do locatário
    if re.search(r'locat[áa]rio.*responsável.*(reparo|manuten[çc][ãa]o).*(estrutura|telhado|fachada|funda[çc][ãa]o)', texto_lower):
        score += 25
        pontos_atencao.append({
            "tipo": "CRÍTICO",
            "categoria": "Manutenção Estrutural",
            "descricao": "Responsabilidade por manutenções estruturais transferida ao locatário",
            "impacto": "Custos altíssimos com reparos em estrutura, telhado, fundação - obrigação legal do proprietário",
            "artigo_legal": "Art. 22, Lei 8.245/91",
            "recomendacao": "REMOVER completamente - manutenções estruturais são SEMPRE do proprietário"
        })
    
    # ============================================
    # CATEGORIA 7: ÁREAS EXTERNAS E COMUNS
    # ============================================
    
    # 7.1 Ausência de área externa/estacionamento
    if not re.search(r'(estacionamento|vaga|garagem)', texto_lower):
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Estacionamento",
            "descricao": "Contrato não menciona estacionamento ou vagas para alunos",
            "impacto": "Academias necessitam estacionamento adequado - ausência impacta captação de alunos",
            "recomendacao": "Garantir mínimo de 1 vaga a cada 50m² de área útil, preferencialmente incluídas no aluguel"
        })
    
    # 7.2 Restrição de uso de áreas externas
    if re.search(r'(proib|n[ãa]o.*permit).*área.*externa', texto_lower):
        score += 18
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Uso de Área Externa",
            "descricao": "Proibição de uso de áreas externas (jardins, pátios, calçadas)",
            "impacto": "Impede atividades outdoor (funcional, yoga, alongamento), aulas ao ar livre e treinos externos",
            "recomendacao": "Negociar uso compartilhado de áreas externas em horários específicos"
        })
    
    # 7.3 Limitação de sinalização externa
    if re.search(r'(proib|restri[çc]).*(placa|faixa|letreiro|sinaliza[çc][ãa]o)', texto_lower):
        score += 12
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Sinalização",
            "descricao": "Restrições severas para placas, letreiros e identificação visual externa",
            "impacto": "Dificulta identificação da academia, impactando marketing e captação de novos alunos",
            "recomendacao": "Garantir direito a placa luminosa na fachada e sinalização direcional"
        })
    
    # ============================================
    # CATEGORIA 8: INFRAESTRUTURA E INSTALAÇÕES
    # ============================================
    
    # 8.1 Insuficiência energética
    if re.search(r'carga.*el[ée]trica.*(\d+).*kva', texto_lower):
        match = re.search(r'(\d+)\s*kva', texto_lower)
        if match and int(match.group(1)) < 50:
            score += 20
            pontos_atencao.append({
                "tipo": "ALTO",
                "categoria": "Infraestrutura Elétrica",
                "descricao": f"Carga elétrica de apenas {match.group(1)} kVA (insuficiente para academia)",
                "impacto": "Impossibilidade de operar equipamentos, ar-condicionado, iluminação e som simultaneamente",
                "recomendacao": "EXIGIR carga mínima de 75 kVA (trifásico) + laudo elétrico antes de assinar"
            })
    
    # 8.2 Ausência de vestiários adequados
    if not re.search(r'(vestiário|banheiro|sanitário)', texto_lower):
        score += 12
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Vestiários",
            "descricao": "Contrato não especifica vestiários ou instalações sanitárias",
            "impacto": "Vestiários adequados (masculino/feminino com chuveiros) são obrigatórios para academias",
            "recomendacao": "Garantir mínimo de 2 vestiários completos com chuveiros (masculino/feminino)"
        })
    
    # 8.3 Proibição de alterações hidráulicas
    if re.search(r'(proib|vedam).*altera[çc][ãa]o.*hidr[áa]ulic', texto_lower):
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Instalações Hidráulicas",
            "descricao": "Proibição de alterações na rede hidráulica",
            "impacto": "Impossibilita instalação de bebedouros, chuveiros adicionais e pontos de água para limpeza",
            "recomendacao": "Permitir alterações hidráulicas mediante projeto aprovado e recomposição ao final"
        })
    
    # 8.4 Pé-direito insuficiente
    pe_direito_match = re.search(r'p[ée].*direito.*?(\d+\.?\d*)m', texto_lower)
    if pe_direito_match and float(pe_direito_match.group(1)) < 2.8:
        score += 18
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Pé-direito",
            "descricao": f"Pé-direito de apenas {pe_direito_match.group(1)}m (inferior ao recomendado)",
            "impacto": "Sensação de ambiente apertado, limitação para equipamentos verticais e exercícios com saltos",
            "recomendacao": "Ideal: mínimo 3,5m de pé-direito para sensação de amplitude"
        })
    
    # ============================================
    # CATEGORIA 9: ACESSIBILIDADE
    # ============================================
    
    # 9.1 Ausência de acessibilidade
    if not re.search(r'(acessibilidade|acess[íi]vel|rampa|elevador)', texto_lower):
        score += 18
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Acessibilidade",
            "descricao": "Contrato não menciona conformidade com normas de acessibilidade",
            "impacto": "NBR 9050 e Estatuto da Pessoa com Deficiência exigem acessibilidade - risco de multas e processos",
            "artigo_legal": "Lei 13.146/2015 (Estatuto da Pessoa com Deficiência)",
            "recomendacao": "EXIGIR que o imóvel tenha rampa de acesso, banheiro adaptado e circulação acessível"
        })
    
    # ============================================
    # CATEGORIA 10: LICENÇAS E REGULARIZAÇÃO
    # ============================================
    
    # 10.1 Responsabilidade por alvará por conta do locatário
    if re.search(r'locat[áa]rio.*responsável.*(alvar[áa]|licen[çc])', texto_lower):
        score += 8
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Alvará de Funcionamento",
            "descricao": "Responsabilidade pela obtenção de alvará transferida ao locatário",
            "impacto": "Normal, mas pode haver impossibilidade de obter alvará por pendências do imóvel",
            "recomendacao": "Incluir cláusula de rescisão sem multa se alvará for negado por problemas estruturais do imóvel"
        })
    
    # 10.2 Imóvel sem habite-se ou regularização
    if re.search(r'(sem|n[ãa]o.*possui).*(habite-se|regulariza[çc][ãa]o)', texto_lower):
        score += 25
        pontos_atencao.append({
            "tipo": "CRÍTICO",
            "categoria": "Regularização do Imóvel",
            "descricao": "Imóvel sem habite-se ou certidão de regularização",
            "impacto": "Impossibilidade de obter alvará de funcionamento, multas da prefeitura, risco de interdição",
            "recomendacao": "NÃO ASSINAR contrato de imóvel irregular - exigir certidão de regularização"
        })
    
    # ============================================
    # CATEGORIA 11: GARANTIAS LOCATÍCIAS
    # ============================================
    
    # 11.1 Exigência de múltiplas garantias
    garantias_encontradas = []
    if re.search(r'(cau[çc][ãa]o|dep[óo]sito)', texto_lower):
        garantias_encontradas.append("caução")
    if re.search(r'fiador', texto_lower):
        garantias_encontradas.append("fiador")
    if re.search(r'seguro.*fiança', texto_lower):
        garantias_encontradas.append("seguro-fiança")
    
    if len(garantias_encontradas) >= 2:
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Garantias Locatícias",
            "descricao": f"Exigência de múltiplas garantias: {', '.join(garantias_encontradas)}",
            "impacto": "Oneração desnecessária - uma garantia é suficiente",
            "artigo_legal": "Art. 37, Lei 8.245/91",
            "recomendacao": "Negociar apenas UMA garantia (preferencialmente seguro-fiança)"
        })
    
    # 11.2 Valor de caução excessivo
    caucao_match = re.search(r'cau[çc][ãa]o.*?(\d+)\s*(alugu[eé]|mês)', texto_lower)
    if caucao_match and int(caucao_match.group(1)) > 3:
        score += 12
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Valor da Caução",
            "descricao": f"Caução de {caucao_match.group(1)} aluguéis (acima do usual)",
            "impacto": "Imobilização excessiva de capital de giro necessário para operação da academia",
            "recomendacao": "Negociar caução máxima de 3 aluguéis com correção monetária"
        })
    
    # ============================================
    # CATEGORIA 12: REAJUSTE DE ALUGUEL
    # ============================================
    
    # 12.1 Reajuste anual sem índice definido
    if re.search(r'reajuste.*anual', texto_lower) and not re.search(r'(igp-m|ipca|inpc)', texto_lower):
        score += 18
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Reajuste de Aluguel",
            "descricao": "Cláusula de reajuste anual sem índice oficial definido",
            "impacto": "Insegurança jurídica - locador pode aplicar reajuste arbitrário",
            "artigo_legal": "Art. 18, Lei 8.245/91",
            "recomendacao": "Definir índice oficial (IGP-M ou IPCA) e periodicidade anual"
        })
    
    # 12.2 Reajuste superior a índices oficiais
    if re.search(r'reajuste.*(acima|superior|maior)', texto_lower):
        score += 20
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Reajuste Abusivo",
            "descricao": "Reajuste de aluguel acima de índices oficiais",
            "impacto": "Aumento desproporcional do custo fixo, podendo inviabilizar a operação",
            "recomendacao": "Limitar reajuste ao IGP-M ou IPCA, o que for menor"
        })
    
    # 12.3 Possibilidade de revisão antes do prazo
    if re.search(r'revis[ãa]o.*qualquer.*tempo', texto_lower):
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Revisão de Aluguel",
            "descricao": "Cláusula permite revisão de aluguel a qualquer momento",
            "impacto": "Imprevisibilidade financeira e risco de aumento arbitrário",
            "recomendacao": "Fixar reajuste APENAS anual pelo índice acordado, sem possibilidade de revisão"
        })
    
    # ============================================
    # CATEGORIA 13: VISTORIA E ESTADO DO IMÓVEL
    # ============================================
    
    # 13.1 Ausência de laudo de vistoria
    if not re.search(r'vistoria|laudo', texto_lower):
        score += 15
        pontos_atencao.append({
            "tipo": "ALTO",
            "categoria": "Vistoria Inicial",
            "descricao": "Contrato não menciona laudo de vistoria detalhado",
            "impacto": "Ao final, locatário pode ser cobrado por danos preexistentes",
            "recomendacao": "EXIGIR laudo de vistoria detalhado com fotos, assinado por ambas as partes, ANTES de assinar contrato"
        })
    
    # 13.2 Imóvel entregue em condições precárias
    if re.search(r'(estado.*atual|como.*est[áa])', texto_lower):
        score += 12
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Estado do Imóvel",
            "descricao": "Imóvel será entregue 'no estado atual' sem reformas",
            "impacto": "Locatário assume custos de adequação que podem ser elevados",
            "recomendacao": "Negociar carência de aluguel proporcional aos investimentos em adequação"
        })
    
    # ============================================
    # CATEGORIA 14: RESPONSABILIDADE CIVIL
    # ============================================
    
    # 14.1 Responsabilidade por acidentes de terceiros
    if re.search(r'locat[áa]rio.*responsável.*acidente.*terceiro', texto_lower):
        score += 10
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Responsabilidade Civil",
            "descricao": "Responsabilidade total por acidentes com terceiros atribuída ao locatário",
            "impacto": "Se acidente for por falha estrutural do imóvel, responsabilidade deve ser compartilhada",
            "recomendacao": "Especificar que locatário responde apenas por acidentes decorrentes de sua atividade, não de falhas estruturais"
        })
    
    # ============================================
    # CATEGORIA 15: FORO E CLÁUSULAS FINAIS
    # ============================================
    
    # 15.1 Foro em cidade distante
    foro_match = re.search(r'foro.*comarca.*?([A-ZÀÁÉÍÓÚ][a-zàáéíóú\s]+)', texto_lower)
    if foro_match and not re.search(r'(s[ãa]o paulo|rio de janeiro|sua cidade)', foro_match.group(1).lower()):
        score += 8
        pontos_atencao.append({
            "tipo": "MÉDIO",
            "categoria": "Foro",
            "descricao": f"Foro definido em {foro_match.group(1)} (pode ser distante)",
            "impacto": "Custos e dificuldade logística para eventual ação judicial",
            "recomendacao": "Negociar foro na comarca onde o imóvel está localizado"
        })
    
    # ============================================
    # CÁLCULO FINAL E CLASSIFICAÇÃO
    # ============================================
    
    nivel_risco = "BAIXO"
    recomendacao_geral = "Contrato aparentemente equilibrado. Revisar pontos destacados antes de assinar."
    
    if score >= 70:
        nivel_risco = "CRÍTICO"
        recomendacao_geral = "⛔ NÃO ASSINAR este contrato sem renegociação URGENTE de cláusulas críticas. Alto risco de prejuízo."
    elif score >= 45:
        nivel_risco = "ALTO"
        recomendacao_geral = "⚠️ Contrato contém cláusulas desfavoráveis significativas. Negociar antes de assinar."
    elif score >= 25:
        nivel_risco = "MÉDIO"
        recomendacao_geral = "⚡ Revisar e negociar pontos destacados para maior segurança jurídica."
    
    return {
        "score": min(score, 100),
        "nivel_risco": nivel_risco,
        "pontos_atencao": pontos_atencao,
        "total_clausulas_problematicas": len(pontos_atencao),
        "recomendacao_geral": recomendacao_geral,
        "categorias_afetadas": list(set([p["categoria"] for p in pontos_atencao]))
    }