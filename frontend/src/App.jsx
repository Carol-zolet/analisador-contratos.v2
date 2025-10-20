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

  const handleFileSelect = (file) => {
    setArquivo(file);
    setResultadoAnalise(null); 
  };

  const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleAnalisarClick = async () => {
    if (!arquivo) {
      alert("Por favor, selecione um arquivo primeiro.");
      return;
    }

    setEstaCarregando(true);
    const formData = new FormData();
    formData.append('file', arquivo); // Envia o arquivo como 'file'

    try {
      // Chama o endpoint único /analisar/
      const response = await fetch(`${apiBaseUrl.replace(/\/$/, '')}/analisar/`, {
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
          <AnalysisResult resultado={resultadoAnalise} />
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