import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;

      if (status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      } else if (status === 403) {
        // Forbidden
        console.error('Access forbidden:', error.response.data);
      } else if (status === 404) {
        // Not found
        console.error('Resource not found:', error.response.data);
      } else if (status >= 500) {
        // Server error
        console.error('Server error:', error.response.data);
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from server:', error.request);
    } else {
      // Error in request configuration
      console.error('Request error:', error.message);
    }

    return Promise.reject(error);
  }
);

// Convenience methods
export const apiService = {
  // Authentication
  auth: {
    login: (email: string, password: string) =>
      api.post('/auth/login', { email, password }),
    register: (data: any) => api.post('/auth/register', data),
    logout: () => api.post('/auth/logout'),
    refreshToken: () => api.post('/auth/refresh'),
  },

  // Manuscripts
  manuscripts: {
    list: (params?: any) => api.get('/manuscripts', { params }),
    get: (id: number) => api.get(`/manuscripts/${id}`),
    create: (data: any) => api.post('/manuscripts', data),
    update: (id: number, data: any) => api.patch(`/manuscripts/${id}`, data),
    delete: (id: number) => api.delete(`/manuscripts/${id}`),
    submit: (id: number) => api.post(`/manuscripts/${id}/submit`),
    uploadFile: (id: number, file: File, type: string) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);
      return api.post(`/manuscripts/${id}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    getParticipants: (id: number) => api.get(`/manuscripts/${id}/participants`),
    addParticipant: (id: number, data: { user_id: number; role: string; stage?: string }) =>
      api.post(`/manuscripts/${id}/participants`, null, { params: data }),
    removeParticipant: (id: number, userId: number, role: string) =>
      api.delete(`/manuscripts/${id}/participants/${userId}/${role}`),
  },

  // Reviews
  reviews: {
    list: (params?: any) => api.get('/reviews', { params }),
    get: (id: number) => api.get(`/reviews/${id}`),
    create: (data: any) => api.post('/reviews', data),
    update: (id: number, data: any) => api.patch(`/reviews/${id}`, data),
    submit: (id: number) => api.post(`/reviews/${id}/submit`),
  },

  // Reviewer Matching
  reviewerMatching: {
    getMatches: (manuscriptId: number) =>
      api.get(`/manuscripts/${manuscriptId}/reviewer-matches`),
    inviteReviewers: (manuscriptId: number, reviewerIds: number[]) =>
      api.post(`/manuscripts/${manuscriptId}/invite-reviewers`, { reviewerIds }),
  },

  // Analytics
  analytics: {
    getDashboard: (range?: string) => api.get('/analytics', { params: { range } }),
    getManuscriptStats: () => api.get('/analytics/manuscripts'),
    getReviewerStats: () => api.get('/analytics/reviewers'),
    exportData: (format: 'csv' | 'pdf') =>
      api.get('/analytics/export', { params: { format }, responseType: 'blob' }),
  },

  // Users
  users: {
    list: (params?: any) => api.get('/users', { params }),
    get: (id: number) => api.get(`/users/${id}`),
    update: (id: number, data: any) => api.patch(`/users/${id}`, data),
    delete: (id: number) => api.delete(`/users/${id}`),
  },

  // Articles (public)
  articles: {
    list: (params?: any) => api.get('/articles', { params }),
    get: (manuscriptId: string) => api.get(`/articles/${manuscriptId}`),
    featured: () => api.get('/articles/featured'),
    search: (query: string, params?: any) =>
      api.get('/articles/search', { params: { q: query, ...params } }),
  },

  // Journal Stats (public)
  stats: {
    get: () => api.get('/stats'),
  },

  // Discussions
  discussions: {
    list: (params?: any) => api.get('/discussions', { params }),
    get: (id: number) => api.get(`/discussions/${id}`),
    create: (data: any) => api.post('/discussions', data),
    addMessage: (id: number, data: { message: string; file_ids?: number[] }) =>
      api.post(`/discussions/${id}/messages`, data),
    addParticipants: (id: number, data: { user_ids: number[] }) =>
      api.post(`/discussions/${id}/participants`, data),
    removeParticipant: (id: number, userId: number) =>
      api.delete(`/discussions/${id}/participants/${userId}`),
    close: (id: number) => api.post(`/discussions/${id}/close`),
    reopen: (id: number) => api.post(`/discussions/${id}/reopen`),
  },

  // Copyediting
  copyediting: {
    list: (params?: any) => api.get('/copyediting/assignments', { params }),
    get: (id: number) => api.get(`/copyediting/assignments/${id}`),
    create: (data: any) => api.post('/copyediting/assignments', data),
    update: (id: number, data: any) => api.patch(`/copyediting/assignments/${id}`, data),
    complete: (id: number, data: any) => api.post(`/copyediting/assignments/${id}/complete`, data),
    uploadFile: (id: number, file: File, version: string) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('version', version);
      return api.post(`/copyediting/assignments/${id}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
  },

  // Production
  production: {
    list: (params?: any) => api.get('/production/assignments', { params }),
    get: (id: number) => api.get(`/production/assignments/${id}`),
    create: (data: any) => api.post('/production/assignments', data),
    update: (id: number, data: any) => api.patch(`/production/assignments/${id}`, data),
    complete: (id: number, data: any) => api.post(`/production/assignments/${id}/complete`, data),
    generateGalley: (manuscriptId: number, data: any) =>
      api.post(`/production/manuscripts/${manuscriptId}/generate-galley`, data),
    uploadGalley: (manuscriptId: number, file: File, format: string) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('format', format);
      return api.post(`/production/manuscripts/${manuscriptId}/galleys`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
  },

  // Issues
  issues: {
    list: (params?: any) => api.get('/issues', { params }),
    get: (id: number) => api.get(`/issues/${id}`),
    create: (data: any) => api.post('/issues', data),
    update: (id: number, data: any) => api.patch(`/issues/${id}`, data),
    delete: (id: number) => api.delete(`/issues/${id}`),
    publish: (id: number, data?: any) => api.post(`/issues/${id}/publish`, data),
    getTableOfContents: (id: number) => api.get(`/issues/${id}/toc`),
    addArticle: (id: number, data: { manuscript_id: number; section?: string }) =>
      api.post(`/issues/${id}/articles`, data),
    removeArticle: (id: number, manuscriptId: number) =>
      api.delete(`/issues/${id}/articles/${manuscriptId}`),
    reorderArticles: (id: number, data: { article_orders: any[] }) =>
      api.post(`/issues/${id}/reorder`, data),
    uploadCover: (id: number, file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return api.post(`/issues/${id}/cover`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
  },
};

export default api;
