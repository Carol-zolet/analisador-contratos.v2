// frontend/src/App.jsx

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Importando os componentes
import Sidebar from './components/Sidebar';
import FileUpload from './components/FileUpload';
import AnalysisResult from './components/AnalysisResult';
import './index.css';

// --- Componente da Página do Analisador (Versão Simplificada) ---
function Analisador() {
  const [arquivo, setArquivo] = useState(null);
  const [resultadoAnalise, setResultadoAnalise] = useState(null);
  const [estaCarregando, setEstaCarregando] = useState(false);
  const [ultimoResultadoSemIA, setUltimoResultadoSemIA] = useState(null);

  const handleFileSelect = (file) => {
    setArquivo(file);
    setResultadoAnalise(null); 
  };

  const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleAnalisarClick = async (opts = { forceAi: false }) => {
    if (!arquivo) {
      alert("Por favor, selecione um arquivo primeiro.");
      return;
    }

    setEstaCarregando(true);
    const formData = new FormData();
    formData.append('file', arquivo); // Envia o arquivo como 'file'

    try {
      // Chama o endpoint único /analisar/
      const url = `${apiBaseUrl.replace(/\/$/, '')}/analisar/${opts.forceAi ? '?force_ai=true' : ''}`;
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail || 'Verifique se o backend está a funcionar.';
        throw new Error(`Falha na comunicação: ${detail}`);
      }

      const data = await response.json();
      setResultadoAnalise(data);
      // Se IA indisponível, guardamos o resultado para retry
      const iaText = (data && data.analiseIA) || '';
      const hasIaError = typeof iaText === 'string' && /❌|erro|quota|429/i.test(iaText);
      if (hasIaError) setUltimoResultadoSemIA(data);

    } catch (error) {
      setResultadoAnalise({ erro: `Erro na Análise: ${error.message}` });
    } finally {
      setEstaCarregando(false); 
    }
  };

  return (
    <div>
      <h1>Análise de Contrato | 26fit</h1>
  <p>Envie seu contrato (PDF ou DOCX) para análise de risco.</p>
      
      {/* Apenas um componente de upload */}
      <FileUpload onFileSelect={handleFileSelect} />
      
      {arquivo && (
        <div className="file-info">
          <p>Arquivo pronto para análise: <strong>{arquivo.name}</strong></p>
          <button onClick={handleAnalisarClick} disabled={estaCarregando}>
            {estaCarregando ? "Analisando..." : "Analisar Agora"}
          </button>
        </div>
      )}

      {/* Área de Resultados (O componente AnalysisResult já está correto desde a última vez) */}
      {resultadoAnalise && (
        resultadoAnalise.erro ? (
          <div className="results-container">
              <h2>Erro na Análise</h2>
              <p style={{color: 'red'}}>{resultadoAnalise.erro}</p>
          </div>
        ) : (
          <>
            {/* Botão de tentar IA novamente quando houver erro de IA */}
            {(() => {
              const iaText = (resultadoAnalise && resultadoAnalise.analiseIA) || '';
              const hasIaError = typeof iaText === 'string' && /❌|erro|quota|429/i.test(iaText);
              if (!hasIaError) return null;
              return (
                <div style={{ margin: '12px 0' }}>
                  <button
                    onClick={() => handleAnalisarClick({ forceAi: true })}
                    disabled={estaCarregando}
                    title="Solicita apenas a análise da IA reaproveitando o texto e regras do cache"
                  >
                    {estaCarregando ? 'Requisitando IA...' : 'Tentar IA novamente'}
                  </button>
                </div>
              );
            })()}
            <AnalysisResult resultado={resultadoAnalise} />
          </>
        )
      )}
    </div>
  );
}

// --- Componente da Página do Dashboard ---
// --- Componente Principal ---
function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Analisador />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;