import { useState } from 'react';
import { predictCodeGen, compareModels } from '../services/api';

const CodeGenTab = () => {
  const [mode, setMode] = useState('single'); // 'single' or 'compare'
  const [prompt, setPrompt] = useState('');
  const [modelVersion, setModelVersion] = useState('v2');
  const [maxLength, setMaxLength] = useState(100);
  const [temperature, setTemperature] = useState(0.7);
  const [topP, setTopP] = useState(0.9);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const examples = [
    "def fibonacci(n):",
    "class Calculator:",
    "# Function to sort a list",
    "import numpy as np\n\ndef matrix_multiply(",
  ];

  const handlePredict = async () => {
    if (!prompt.trim()) {
      setError('Please enter a code prompt');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params = {
        max_length: maxLength,
        temperature: temperature,
        top_p: topP,
      };

      if (mode === 'single') {
        const data = await predictCodeGen(prompt, modelVersion, params);
        setResult({ type: 'single', data });
      } else {
        const data = await compareModels('codegen', { prompt }, params);
        setResult({ type: 'compare', data });
      }
    } catch (err) {
      const errorDetail = err.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        // FastAPI validation errors
        setError(errorDetail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('; '));
      } else {
        setError(errorDetail || err.message || 'Failed to get prediction');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadExample = (example) => {
    setPrompt(example);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>CodeGen Code Generation</h2>
      
      {/* Mode Toggle */}
      <div style={styles.modeToggle}>
        <button
          onClick={() => setMode('single')}
          style={{
            ...styles.modeButton,
            ...(mode === 'single' ? styles.modeButtonActive : {}),
          }}
        >
          Single Model
        </button>
        <button
          onClick={() => setMode('compare')}
          style={{
            ...styles.modeButton,
            ...(mode === 'compare' ? styles.modeButtonActive : {}),
          }}
        >
          Compare V1 vs V2
        </button>
      </div>

      {/* Input Section */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Input</h3>
        
        <div style={styles.inputGroup}>
          <label style={styles.label}>Code Prompt:</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter a code prompt or partial code..."
            style={styles.codeTextarea}
            rows={6}
          />
        </div>

        {/* Examples */}
        <div style={styles.examplesContainer}>
          <span style={styles.examplesLabel}>Examples:</span>
          {examples.map((ex, idx) => (
            <button
              key={idx}
              onClick={() => loadExample(ex)}
              style={styles.exampleButton}
            >
              Example {idx + 1}
            </button>
          ))}
        </div>
      </div>

      {/* Parameters Section */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Parameters</h3>
        
        {mode === 'single' && (
          <div style={styles.inputGroup}>
            <label style={styles.label}>Model Version:</label>
            <select
              value={modelVersion}
              onChange={(e) => setModelVersion(e.target.value)}
              style={styles.select}
            >
              <option value="v1">V1 (Random Weights)</option>
              <option value="v2">V2 (Pretrained)</option>
            </select>
          </div>
        )}

        <div style={styles.paramGroup}>
          <label style={styles.label}>
            Max Length: <span style={styles.paramValue}>{maxLength}</span>
          </label>
          <input
            type="range"
            min="20"
            max="200"
            step="10"
            value={maxLength}
            onChange={(e) => setMaxLength(parseInt(e.target.value))}
            style={styles.slider}
          />
        </div>

        <div style={styles.paramRow}>
          <div style={styles.paramGroup}>
            <label style={styles.label}>
              Temperature: <span style={styles.paramValue}>{temperature.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0.1"
              max="2.0"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              style={styles.slider}
            />
          </div>

          <div style={styles.paramGroup}>
            <label style={styles.label}>
              Top-P: <span style={styles.paramValue}>{topP.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              value={topP}
              onChange={(e) => setTopP(parseFloat(e.target.value))}
              style={styles.slider}
            />
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handlePredict}
        disabled={loading}
        style={{
          ...styles.button,
          ...(loading ? styles.buttonDisabled : {}),
        }}
      >
        {loading ? 'Generating...' : 'Generate Code'}
      </button>

      {/* Error */}
      {error && (
        <div style={styles.error}>
          ⚠️ {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={styles.results}>
          <h3 style={styles.sectionTitle}>Results</h3>
          
          {result.type === 'single' ? (
            <div style={styles.resultCard}>
              <div style={styles.resultHeader}>
                <strong>Model:</strong> {result.data.model_version.toUpperCase()}
              </div>
              <div style={styles.resultContent}>
                <div style={styles.resultRow}>
                  <strong>Prompt:</strong>
                  <pre style={styles.codeBlock}>{result.data.input_text}</pre>
                </div>
                <div style={styles.resultRow}>
                  <strong>Generated Code:</strong>
                  <pre style={styles.codeBlock}>{result.data.generated_text}</pre>
                </div>
              </div>
            </div>
          ) : (
            <div style={styles.compareContainer}>
              <div style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <strong>V1 (Random Weights)</strong>
                </div>
                <div style={styles.resultContent}>
                  <div style={styles.resultRow}>
                    <strong>Generated Code:</strong>
                    <pre style={styles.codeBlock}>{result.data.v1.generated_text}</pre>
                  </div>
                </div>
              </div>

              <div style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <strong>V2 (Pretrained)</strong>
                </div>
                <div style={styles.resultContent}>
                  <div style={styles.resultRow}>
                    <strong>Generated Code:</strong>
                    <pre style={styles.codeBlock}>{result.data.v2.generated_text}</pre>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '20px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#1a1a1a',
  },
  modeToggle: {
    display: 'flex',
    gap: '10px',
    marginBottom: '30px',
  },
  modeButton: {
    padding: '10px 20px',
    fontSize: '14px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    background: 'white',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  modeButtonActive: {
    background: '#2196F3',
    color: 'white',
    borderColor: '#2196F3',
  },
  section: {
    background: '#f9f9f9',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  sectionTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '15px',
    color: '#333',
  },
  inputGroup: {
    marginBottom: '15px',
  },
  label: {
    display: 'block',
    marginBottom: '5px',
    fontWeight: '500',
    color: '#555',
  },
  codeTextarea: {
    width: '100%',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxSizing: 'border-box',
    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
    resize: 'vertical',
    background: '#f5f5f5',
  },
  select: {
    width: '100%',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
  },
  examplesContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px',
    alignItems: 'center',
    marginTop: '15px',
  },
  examplesLabel: {
    fontWeight: '500',
    color: '#555',
  },
  exampleButton: {
    padding: '6px 12px',
    fontSize: '13px',
    background: '#e3f2fd',
    border: '1px solid #90caf9',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  paramRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    marginTop: '15px',
  },
  paramGroup: {
    display: 'flex',
    flexDirection: 'column',
  },
  paramValue: {
    fontWeight: 'bold',
    color: '#2196F3',
  },
  slider: {
    width: '100%',
    marginTop: '8px',
  },
  button: {
    width: '100%',
    padding: '15px',
    fontSize: '16px',
    fontWeight: 'bold',
    background: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  buttonDisabled: {
    background: '#ccc',
    cursor: 'not-allowed',
  },
  error: {
    marginTop: '15px',
    padding: '15px',
    background: '#ffebee',
    color: '#c62828',
    borderRadius: '8px',
    border: '1px solid #ef9a9a',
  },
  results: {
    marginTop: '30px',
  },
  resultCard: {
    background: 'white',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '15px',
  },
  resultHeader: {
    fontSize: '16px',
    marginBottom: '15px',
    paddingBottom: '10px',
    borderBottom: '2px solid #f0f0f0',
  },
  resultContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  resultRow: {
    lineHeight: '1.6',
  },
  codeBlock: {
    background: '#f5f5f5',
    padding: '15px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    overflow: 'auto',
    fontSize: '13px',
    fontFamily: 'Monaco, Consolas, "Courier New", monospace',
    lineHeight: '1.5',
    marginTop: '8px',
  },
  compareContainer: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
  },
};

export default CodeGenTab;
