import { useState } from 'react';
import { predictFlanT5, compareModels } from '../services/api';

const T5Tab = () => {
  const [mode, setMode] = useState('single'); // 'single' or 'compare'
  const [sentence, setSentence] = useState('');
  const [word, setWord] = useState('');
  const [modelVersion, setModelVersion] = useState('v2');
  const [k, setK] = useState(5);
  const [numBeams, setNumBeams] = useState(10);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const examples = [
    { sentence: "He commenced the project yesterday.", word: "commenced" },
    { sentence: "The scientist made an astounding discovery last year.", word: "astounding" },
    { sentence: "She was reluctant to accept the offer.", word: "reluctant" },
  ];

  const handlePredict = async () => {
    if (!sentence.trim() || !word.trim()) {
      setError('Please enter both sentence and word');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (mode === 'single') {
        const data = await predictFlanT5(sentence, word, modelVersion, { k, num_beams: numBeams });
        setResult({ type: 'single', data });
      } else {
        const data = await compareModels('t5', { sentence, word }, { k, num_beams: numBeams });
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
    setSentence(example.sentence);
    setWord(example.word);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>T5 Lexical Simplification</h2>
      
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
          <label style={styles.label}>Sentence:</label>
          <textarea
            value={sentence}
            onChange={(e) => setSentence(e.target.value)}
            placeholder="Enter a sentence with a complex word..."
            style={styles.textarea}
            rows={3}
          />
        </div>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Complex Word:</label>
          <input
            type="text"
            value={word}
            onChange={(e) => setWord(e.target.value)}
            placeholder="Enter the word to simplify..."
            style={styles.input}
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
              {ex.word}
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
              <option value="v1">V1 (Pretrained)</option>
              <option value="v2">V2 (Fine-tuned)</option>
            </select>
          </div>
        )}

        <div style={styles.paramRow}>
          <div style={styles.paramGroup}>
            <label style={styles.label}>
              Top-K: <span style={styles.paramValue}>{k}</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={k}
              onChange={(e) => setK(parseInt(e.target.value))}
              style={styles.slider}
            />
          </div>

          <div style={styles.paramGroup}>
            <label style={styles.label}>
              Num Beams: <span style={styles.paramValue}>{numBeams}</span>
            </label>
            <input
              type="range"
              min="1"
              max="20"
              value={numBeams}
              onChange={(e) => setNumBeams(parseInt(e.target.value))}
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
        {loading ? 'Generating...' : 'Generate Simplifications'}
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
                  <strong>Sentence:</strong> {result.data.parameters.sentence}
                </div>
                <div style={styles.resultRow}>
                  <strong>Complex Word:</strong> <span style={styles.highlightWord}>{result.data.parameters.word}</span>
                </div>
                <div style={styles.resultRow}>
                  <strong>Candidates:</strong>
                  <div style={styles.candidatesList}>
                    {result.data.parameters.candidates.map((candidate, idx) => (
                      <span key={idx} style={styles.candidateTag}>
                        {idx + 1}. {candidate}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={styles.compareContainer}>
              <div style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <strong>V1 (Pretrained)</strong>
                </div>
                <div style={styles.resultContent}>
                  <div style={styles.resultRow}>
                    <strong>Candidates:</strong>
                    <div style={styles.candidatesList}>
                      {result.data.v1.parameters.candidates.map((candidate, idx) => (
                        <span key={idx} style={styles.candidateTag}>
                          {idx + 1}. {candidate}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div style={styles.resultCard}>
                <div style={styles.resultHeader}>
                  <strong>V2 (Fine-tuned)</strong>
                </div>
                <div style={styles.resultContent}>
                  <div style={styles.resultRow}>
                    <strong>Candidates:</strong>
                    <div style={styles.candidatesList}>
                      {result.data.v2.parameters.candidates.map((candidate, idx) => (
                        <span key={idx} style={styles.candidateTag}>
                          {idx + 1}. {candidate}
                        </span>
                      ))}
                    </div>
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
    background: '#4CAF50',
    color: 'white',
    borderColor: '#4CAF50',
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
  input: {
    width: '100%',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxSizing: 'border-box',
  },
  textarea: {
    width: '100%',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxSizing: 'border-box',
    fontFamily: 'inherit',
    resize: 'vertical',
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
  },
  paramGroup: {
    display: 'flex',
    flexDirection: 'column',
  },
  paramValue: {
    fontWeight: 'bold',
    color: '#4CAF50',
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
    background: '#4CAF50',
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
    gap: '12px',
  },
  resultRow: {
    lineHeight: '1.6',
  },
  highlightWord: {
    background: '#fff59d',
    padding: '2px 6px',
    borderRadius: '4px',
    fontWeight: 'bold',
  },
  candidatesList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginTop: '8px',
  },
  candidateTag: {
    display: 'inline-block',
    padding: '6px 12px',
    background: '#e8f5e9',
    border: '1px solid #a5d6a7',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: '500',
  },
  compareContainer: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
  },
};

export default T5Tab;
