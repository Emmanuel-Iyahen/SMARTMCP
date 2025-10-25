

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://ec2-44-203-197-2.compute-1.amazonaws.com:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const dashboardService = {
  getOverview: () => api.get('/api/dashboard/'),  // Added trailing slash to match your backend
  getSectorData: (sector, timeframe = '7d') => 
    api.get(`/api/dashboard/sector/${sector}?timeframe=${timeframe}`),
  getAlerts: () => api.get('/api/dashboard/alerts'),
  getMetrics: () => api.get('/api/dashboard/metrics'),
  getFinancialTrends: () => api.get('/api/financial-trends'),
};

export const promptService = {
  analyzePrompt: (prompt, sector = null) => 
    api.post('/api/prompts/analyze', { prompt, sector }),
  getSuggestions: (sector = null) => 
    api.get(`/api/prompts/suggestions${sector ? `?sector=${sector}` : ''}`),
  getHistory: (limit = 10, sector = null) => {
    const params = new URLSearchParams();
    params.append('limit', limit);
    if (sector) params.append('sector', sector);
    return api.get(`/api/prompts/history?${params.toString()}`);
  },
  submitFeedback: (analysisId, rating, helpful, comments = '') =>
    api.post('/api/prompts/feedback', { analysisId, rating, helpful, comments }),
};

export const dataSourcesService = {
  getSources: () => api.get('/api/data-sources'),
  getSourceData: (sourceId) => api.get(`/api/data-sources/${sourceId}/latest`),
  getSourceStatus: (sourceId) => api.get(`/api/data-sources/${sourceId}/status`),
  getHistoricalData: (sourceId, startDate, endDate) =>
    api.get(`/api/data-sources/${sourceId}/historical?start_date=${startDate}&end_date=${endDate}`),
};

export default api;