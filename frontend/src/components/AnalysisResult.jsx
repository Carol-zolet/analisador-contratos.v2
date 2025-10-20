import React from 'react';
import DOMPurify from 'dompurify';
import './AnalysisResult.css';

// Um componente para exibir cada "ponto de atenção" de forma organizada
function PontoAtencao({ ponto }) {
  const getRiskColor = (tipo) => {
    switch (tipo) {
      case 'CRÍTICO': return '#ff4d4f'; // Vermelho
      case 'ALTO': return '#faad14';    // Laranja
      case 'MÉDIO': return '#1890ff';   // Azul
      default: return '#52c41a';       // Verde
    }
  };

  return (
    <div className="ponto-atencao" style={{ borderLeft: `5px solid ${getRiskColor(ponto.tipo)}` }}>
      <h4><span style={{ color: getRiskColor(ponto.tipo) }}>{ponto.tipo}</span>: {ponto.categoria}</h4>
      <p><strong>Descrição:</strong> {ponto.descricao}</p>
      <p><strong>Impacto Potencial:</strong> {ponto.impacto}</p>
      <p><strong>Recomendação:</strong> {ponto.recomendacao}</p>
      {ponto.artigo_legal && <small><strong>Base Legal:</strong> {ponto.artigo_legal}</small>}
    </div>
  );
}

const clampScorePercent = (valor) => {
  const num = Number(valor);
  if (Number.isNaN(num)) return 0;
  return Math.min(100, Math.max(0, num));
};

const getScoreColor = (score) => {
  if (score >= 75) return 'linear-gradient(90deg,#52c41a,#1890ff)';
  if (score >= 50) return 'linear-gradient(90deg,#ffc107,#fa8c16)';
  return 'linear-gradient(90deg,#ff4d4f,#d9363e)';
};

const getRiskBadgeColor = (nivel) => {
  if (!nivel) return '#6c757d';
  const n = nivel.toString().toUpperCase();
  if (n.includes('CR') || n.includes('ALTO')) return '#dc3545';
  if (n.includes('M') || n.includes('MÉDIO')) return '#faad14';
  return '#52c41a';
};

const escapeHtml = (value = '') =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

const formatInlineMarkdown = (value = '') =>
  escapeHtml(value).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

const formatAiMarkdown = (markdown) => {
  if (!markdown) return '';

  const lines = markdown.split(/\r?\n/);
  const html = [];
  let inUnordered = false;
  let inOrdered = false;

  const closeLists = () => {
    if (inUnordered) {
      html.push('</ul>');
      inUnordered = false;
    }
    if (inOrdered) {
      html.push('</ol>');
      inOrdered = false;
    }
  };

  lines.forEach((line) => {
    const trimmed = line.trim();

    if (!trimmed) {
      closeLists();
      return;
    }

    if (/^#{2,3}\s+/.test(trimmed)) {
      closeLists();
      const heading = trimmed.replace(/^#{2,3}\s+/, '');
      html.push(`<h4>${formatInlineMarkdown(heading)}</h4>`);
      return;
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      if (!inOrdered) {
        closeLists();
        html.push('<ol>');
        inOrdered = true;
      }
      const content = trimmed.replace(/^\d+\.\s+/, '');
      html.push(`<li>${formatInlineMarkdown(content)}</li>`);
      return;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      if (!inUnordered) {
        closeLists();
        html.push('<ul>');
        inUnordered = true;
      }
      const content = trimmed.replace(/^[-*]\s+/, '');
      html.push(`<li>${formatInlineMarkdown(content)}</li>`);
      return;
    }

    closeLists();
    html.push(`<p>${formatInlineMarkdown(trimmed)}</p>`);
  });

  closeLists();
  return html.join('');
};

// O componente principal de resultados, agora corrigido
function AnalysisResult({ resultado }) {
  // Segurança: fornecer defaults caso 'resultado' seja null/undefined
  const {
    nivelRisco = 'DESCONHECIDO',
    scoreRisco = 0,
    pontosAtencao = [],
    totalClausulasProblem = 0,
    analiseIA = 'Nenhuma análise da IA disponível.'
  } = resultado || {};

  // Preferir nomeArquivo (backend) e cair para nomeAdendo se existir
  const nomeArquivo = (resultado && (resultado.nomeArquivo || resultado.nomeAdendo)) || 'Arquivo sem nome';

  const scorePercent = clampScorePercent(scoreRisco);
  const riskBadgeColor = getRiskBadgeColor(nivelRisco);
  const formattedAiHtml = React.useMemo(() => {
    const html = formatAiMarkdown(analiseIA);
    return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
  }, [analiseIA]);

  const cacheHit = Boolean(resultado && resultado.cacheHit);

  return (
    <div className="results-container">
      <h2>
        Resultado da Análise do Arquivo: "{nomeArquivo}"
        {cacheHit && (
          <span
            title="Resultado carregado do cache para maior rapidez"
            style={{
              marginLeft: 12,
              fontSize: 12,
              background: '#e6f7ff',
              color: '#1890ff',
              padding: '4px 8px',
              borderRadius: 999,
              verticalAlign: 'middle',
            }}
          >
            cache
          </span>
        )}
      </h2>

      {/* Seção do Score de Risco */}
      <div className="score-summary">
        <div className="score-card">
          <div className="score-left">
            <div className="score-number">{scorePercent}</div>
            <div className="score-sub">/100</div>
          </div>

          <div className="score-right">
            <div className="score-bar">
              <div
                className="score-fill"
                style={{ width: `${scorePercent}%`, background: getScoreColor(scorePercent) }}
              />
            </div>
            <div className="score-meta">
              <div className="risk-badge" style={{ background: riskBadgeColor, color: '#fff' }}>
                {nivelRisco}
              </div>
              <div className="small-info">Cláusulas problemáticas: <strong>{totalClausulasProblem}</strong></div>
            </div>
          </div>
        </div>
      </div>

      {/* Seção da Análise da Inteligência Artificial */}
      <div className="ai-analysis">
        <div className="section-header">
          <span className="section-icon" aria-hidden="true">🤖</span>
          <div className="section-titles">
            <h3>Análise da IA (Gemini)</h3>
            <p>Resumo estratégico elaborado automaticamente</p>
          </div>
        </div>
        <div className="ai-box">
          <article
            className="ai-text"
            dangerouslySetInnerHTML={{ __html: formattedAiHtml }}
          />
        </div>
      </div>

      {/* Seção dos Pontos de Atenção Detalhados */}
      <div className="attention-points">
        <h3>Pontos de Atenção Detalhados</h3>
        {pontosAtencao && pontosAtencao.length > 0 ? (
          pontosAtencao.map((ponto, index) => (
            <PontoAtencao key={index} ponto={ponto} />
          ))
        ) : (
          <p>Nenhum ponto de atenção específico encontrado pela análise de regras.</p>
        )}
      </div>
    </div>
  );
}

export default AnalysisResult;