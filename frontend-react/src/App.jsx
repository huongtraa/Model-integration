import { useState, useEffect } from 'react';
import T5Tab from './components/T5Tab';
import CodeGenTab from './components/CodeGenTab';
import { getHealth, getModels } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('t5');
  const [healthStatus, setHealthStatus] = useState(null);
  const [modelsInfo, setModelsInfo] = useState(null);

  useEffect(() => {
    // Check backend health on mount
    const checkHealth = async () => {
      try {
        const health = await getHealth();
        setHealthStatus(health);
      } catch (err) {
        setHealthStatus({ status: 'error', message: 'Backend not available' });
      }
    };

    const fetchModels = async () => {
      try {
        const models = await getModels();
        setModelsInfo(models);
      } catch (err) {
        console.error('Failed to fetch models info:', err);
      }
    };

    checkHealth();
    fetchModels();
  }, []);

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.headerTitle}>Model Integration Demo</h1>
          <div style={styles.headerSubtitle}>
            T5 Lexical Simplification & CodeGen Code Generation
          </div>
        </div>
        
        {healthStatus && (
          <div style={{
            ...styles.healthBadge,
            ...(healthStatus.status === 'healthy' ? styles.healthBadgeOk : styles.healthBadgeError),
          }}>
            {healthStatus.status === 'healthy' ? '🟢 Backend Online' : '🔴 Backend Offline'}
          </div>
        )}
      </header>

      {/* Tab Navigation */}
      <div style={styles.tabContainer}>
        <button
          onClick={() => setActiveTab('t5')}
          style={{
            ...styles.tab,
            ...(activeTab === 't5' ? styles.tabActive : {}),
          }}
        >
          🔤 T5 Lexical Simplification
        </button>
        <button
          onClick={() => setActiveTab('codegen')}
          style={{
            ...styles.tab,
            ...(activeTab === 'codegen' ? styles.tabActive : {}),
          }}
        >
          💻 CodeGen Code Generation
        </button>
      </div>

      {/* Tab Content */}
      <div style={styles.content}>
        {activeTab === 't5' ? <T5Tab /> : <CodeGenTab />}
      </div>

      {/* Footer */}
      <footer style={styles.footer}>
        <div style={styles.footerContent}>
          {modelsInfo && (
            <div style={styles.modelsInfo}>
              <strong>Available Models:</strong>
              <ul style={styles.modelsList}>
                {Object.entries(modelsInfo).map(([key, value]) => (
                  <li key={key}>
                    <strong>{key}:</strong> {value}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div style={styles.footerText}>
            Model Integration Demo • FastAPI Backend • React Frontend
          </div>
        </div>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  header: {
    background: 'white',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    padding: '20px 30px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: '32px',
    fontWeight: 'bold',
    margin: 0,
    color: '#1a1a1a',
  },
  headerSubtitle: {
    fontSize: '14px',
    color: '#666',
    marginTop: '5px',
  },
  healthBadge: {
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: '500',
  },
  healthBadgeOk: {
    background: '#e8f5e9',
    color: '#2e7d32',
    border: '1px solid #a5d6a7',
  },
  healthBadgeError: {
    background: '#ffebee',
    color: '#c62828',
    border: '1px solid #ef9a9a',
  },
  tabContainer: {
    background: 'white',
    display: 'flex',
    borderBottom: '2px solid #e0e0e0',
    padding: '0 30px',
  },
  tab: {
    padding: '15px 30px',
    fontSize: '16px',
    fontWeight: '500',
    background: 'transparent',
    border: 'none',
    borderBottom: '3px solid transparent',
    cursor: 'pointer',
    transition: 'all 0.2s',
    color: '#666',
  },
  tabActive: {
    color: '#667eea',
    borderBottomColor: '#667eea',
  },
  content: {
    flex: 1,
    background: 'white',
    padding: '30px',
  },
  footer: {
    background: 'rgba(255, 255, 255, 0.95)',
    padding: '20px 30px',
    borderTop: '1px solid #e0e0e0',
  },
  footerContent: {
    maxWidth: '900px',
    margin: '0 auto',
  },
  modelsInfo: {
    marginBottom: '15px',
    fontSize: '14px',
    color: '#555',
  },
  modelsList: {
    margin: '8px 0',
    paddingLeft: '20px',
  },
  footerText: {
    textAlign: 'center',
    color: '#999',
    fontSize: '13px',
  },
};

export default App;
