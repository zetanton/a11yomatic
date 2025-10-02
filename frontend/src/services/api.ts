import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/api/v1/auth/register', data),
  
  login: (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// PDF API
export const pdfAPI = {
  upload: (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/v1/pdfs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    });
  },
  
  list: () => api.get('/api/v1/pdfs/'),
  
  get: (id: string) => api.get(`/api/v1/pdfs/${id}`),
  
  delete: (id: string) => api.delete(`/api/v1/pdfs/${id}`),
};

// Analysis API
export const analysisAPI = {
  analyze: (pdfId: string) =>
    api.post(`/api/v1/analysis/${pdfId}/analyze`),
  
  getResults: (pdfId: string) =>
    api.get(`/api/v1/analysis/${pdfId}`),
  
  getIssues: (pdfId: string, severity?: string) => {
    const params = severity ? { severity } : {};
    return api.get(`/api/v1/analysis/${pdfId}/issues`, { params });
  },
};

// Remediation API
export const remediationAPI = {
  generate: (issueId: string) =>
    api.post(`/api/v1/remediation/${issueId}`),
  
  get: (issueId: string) =>
    api.get(`/api/v1/remediation/${issueId}`),
  
  approve: (issueId: string, approved: boolean) =>
    api.put(`/api/v1/remediation/${issueId}/approve`, { approved }),
};

// Reports API
export const reportsAPI = {
  get: (pdfId: string) =>
    api.get(`/api/v1/reports/${pdfId}`),
  
  exportJSON: (pdfId: string) =>
    api.get(`/api/v1/reports/${pdfId}/export/json`),
  
  getAnalytics: () =>
    api.get('/api/v1/reports/analytics'),
};

export default api;


