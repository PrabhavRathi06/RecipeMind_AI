import { useState } from 'react';
import './index.css';
import ExtractTab from './components/ExtractTab';
import HistoryTab from './components/HistoryTab';

type Tab = 'extract' | 'history';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('extract');

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <div className="app-logo">
          <div className="logo-icon">RM</div>
          <div>
            <div className="logo-text">Recipe<span>Mind</span> AI</div>          </div>
        </div>
      </header>

      <nav className="tabs-container">
        <button
          id="tab-extract"
          className={`tab-btn ${activeTab === 'extract' ? 'active' : ''}`}
          onClick={() => setActiveTab('extract')}
        >
          Extract Recipe
        </button>
        <button
          id="tab-history"
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          Saved Recipes
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'extract' && <ExtractTab />}
        {activeTab === 'history' && <HistoryTab />}
      </main>
    </div>
  );
}

export default App;
