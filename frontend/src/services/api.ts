/**
 * API service for communicating with backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface ApiError {
  detail: string;
}

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: 'An error occurred',
      }));
      throw new Error(error.detail);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Authentication
  async login(email: string, password: string) {
    const response = await this.request<{ access_token: string; refresh_token: string }>(
      '/api/v1/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    );
    this.setToken(response.access_token);
    return response;
  }

  async register(email: string, password: string, fullName?: string, organization?: string) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName, organization }),
    });
  }

  async logout() {
    await this.request('/api/v1/auth/logout', { method: 'POST' });
    this.clearToken();
  }

  // PDF Management
  async uploadPDF(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request('/api/v1/pdfs/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async listPDFs(skip = 0, limit = 50) {
    return this.request(`/api/v1/pdfs?skip=${skip}&limit=${limit}`);
  }

  async getPDF(pdfId: string) {
    return this.request(`/api/v1/pdfs/${pdfId}`);
  }

  async deletePDF(pdfId: string) {
    return this.request(`/api/v1/pdfs/${pdfId}`, { method: 'DELETE' });
  }

  // Analysis
  async startAnalysis(pdfId: string) {
    return this.request(`/api/v1/analysis/${pdfId}/analyze`, {
      method: 'POST',
    });
  }

  async getAnalysis(pdfId: string) {
    return this.request(`/api/v1/analysis/${pdfId}`);
  }

  async getIssues(pdfId: string, severity?: string) {
    const params = severity ? `?severity=${severity}` : '';
    return this.request(`/api/v1/analysis/${pdfId}/issues${params}`);
  }

  // Remediation
  async generateRemediation(issueId: string, context?: any) {
    return this.request(`/api/v1/remediation/${issueId}/generate`, {
      method: 'POST',
      body: JSON.stringify({ context }),
    });
  }

  async getRemediation(issueId: string) {
    return this.request(`/api/v1/remediation/${issueId}`);
  }

  async approveRemediation(issueId: string) {
    return this.request(`/api/v1/remediation/${issueId}/approve`, {
      method: 'PATCH',
    });
  }

  async generateBulkRemediation(pdfId: string) {
    return this.request(`/api/v1/remediation/bulk/generate?pdf_id=${pdfId}`, {
      method: 'POST',
    });
  }

  // Reports
  async getReport(pdfId: string) {
    return this.request(`/api/v1/reports/${pdfId}`);
  }

  async getAnalytics() {
    return this.request('/api/v1/reports/analytics/summary');
  }

  async exportReport(pdfId: string, format = 'json') {
    return this.request(`/api/v1/reports/${pdfId}/export?format=${format}`, {
      method: 'POST',
    });
  }

  // Health checks
  async healthCheck() {
    return this.request('/health');
  }
}

export const apiService = new ApiService();
export default apiService;
