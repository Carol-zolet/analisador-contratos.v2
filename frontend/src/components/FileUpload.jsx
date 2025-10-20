// frontend/src/components/FileUpload.jsx
import React, { useState, useRef } from 'react';
import './FileUpload.css';
import { ACCEPT_EXTS, ACCEPT_MIMES, ACCEPT_LABEL } from '../config/upload';

const FileUpload = ({ onFileSelect }) => {
  // Estado para controlar o feedback visual de "arrastar"
  const [isDragging, setIsDragging] = useState(false);
  // Estado para guardar o nome do ficheiro selecionado
  const [fileName, setFileName] = useState('');
  
  // Referência para o input de ficheiro escondido, para podermos acioná-lo
  const fileInputRef = useRef(null);

  // Função para lidar com o ficheiro selecionado
  const handleFile = (file) => {
    if (!file) {
      return;
    }

    const allowedMimeTypes = ACCEPT_MIMES;
    const allowedExtensions = ACCEPT_EXTS;
    const fileExtension = file.name ? file.name.toLowerCase().slice(file.name.lastIndexOf('.')) : '';

    const isMimeAllowed = allowedMimeTypes.includes(file.type);
    const isExtensionAllowed = allowedExtensions.includes(fileExtension);

    if (isMimeAllowed || isExtensionAllowed) {
      setFileName(file.name);
      onFileSelect(file); // Envia o ficheiro para o componente pai
    } else {
  alert(`Erro: selecione um ficheiro nos formatos ${ACCEPT_LABEL}.`);
      setFileName('');
      onFileSelect(null);
    }
  };

  // --- Eventos de Drag and Drop ---
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation(); // Necessário para o evento onDrop funcionar
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  // Evento para o input de ficheiro tradicional
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    handleFile(file);
  };

  // Aciona o clique no input de ficheiro escondido
  const onBrowseClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="file-upload-container">
      <div 
        className={`file-upload-area ${isDragging ? 'dragging' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={onBrowseClick} // Permite clicar em qualquer lugar da área
      >
        <div className="file-upload-content">
          <span className="file-upload-icon">📄</span>
          <p className="file-upload-text">
            Arraste e solte o seu contrato aqui, ou <strong>clique para selecionar</strong>.
          </p>
          <p className="file-upload-hint">Formatos aceites: {ACCEPT_LABEL}</p>
          <input
            ref={fileInputRef}
            type="file"
            className="file-input"
            onChange={handleFileChange}
            accept={ACCEPT_EXTS.join(',')}
          />
        </div>
      </div>
      {fileName && (
        <div className="file-name-display">
          Ficheiro Selecionado: <strong>{fileName}</strong>
        </div>
      )}
    </div>
  );
};

export default FileUpload;