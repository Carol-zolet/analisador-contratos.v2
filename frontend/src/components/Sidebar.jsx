import React from 'react'; // <-- A LINHA QUE CORRIGE O ERRO
import { Link } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Analisador de Contratos</h2>
      </div>
      <nav className="sidebar-nav">
        <Link to="/">📄 Analisador</Link>
      </nav>
    </div>
  );
}

export default Sidebar;