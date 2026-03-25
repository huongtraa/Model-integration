import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const predictFlanT5 = async (sentence, word, modelVersion, params) => {
  const response = await api.post('/predict/flan-t5', {
    sentence,
    word,
    model_version: modelVersion,
    k: params.k || 5,
    num_beams: params.num_beams || 10,
  });
  return response.data;
};

export const predictCodeGen = async (prompt, modelVersion, params) => {
  const response = await api.post('/predict/codegen', {
    prompt: prompt,
    model_version: modelVersion,
    max_length: params.max_length || 100,
    temperature: params.temperature || 0.7,
    top_p: params.top_p || 0.9,
  });
  return response.data;
};

export const compareModels = async (modelType, data, params) => {
  const payload = modelType === 't5' 
    ? {
        model_type: 't5',
        sentence: data.sentence,
        word: data.word,
        k: params.k || 5,
        num_beams: params.num_beams || 10,
      }
    : {
        model_type: 'codegen',
        input_text: data.prompt,
        max_length: params.max_length || 100,
        temperature: params.temperature || 0.7,
        top_p: params.top_p || 0.9,
      };

  const response = await api.post('/compare', payload);
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getModels = async () => {
  const response = await api.get('/models');
  return response.data;
};
