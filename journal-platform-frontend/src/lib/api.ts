// API Client for Unified Backend Integration

import type {
  APIConfig,
  APIClient,
  UserRegistration,
  UserLogin,
  AuthResponse,
  TokenData,
  AITheme,
  AITitleStyle,
  AIGenerationRequest,
  AIGenerationResponse,
  AIProgressResponse,
  ProjectLibraryResponse,
  Project,
  CustomizationSettings,
  HealthResponse,
  SystemInfo,
  WebSocketProgressMessage,
  APIError
} from '@/types/api';

class UnifiedBackendAPI implements APIClient {
  private baseURL: string;
  private defaultConfig: APIConfig;

  constructor() {
    // Use relative URLs in development so Vite proxy works, absolute URL in production
    this.baseURL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'https://localhost:6770');
    this.defaultConfig = {
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    config: Partial<APIConfig> = {}
  ): Promise<T> {
    const url = `${config.baseURL || this.defaultConfig.baseURL}${endpoint}`;
    const headers = {
      ...this.defaultConfig.headers,
      ...config.headers,
      ...options.headers,
    };

    // Add Authorization header if token exists
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData: APIError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`,
          status: response.status,
        }));

        // Handle validation errors specifically
        if (response.status === 422 && errorData.additional_context?.validation_errors) {
          const validationErrors = errorData.additional_context.validation_errors;
          const errorMessage = validationErrors
            .map((err: any) => `${err.field}: ${err.message}`)
            .join(', ');
          throw new Error(`Validation failed: ${errorMessage}`);
        }

        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async get<T>(endpoint: string, config: Partial<APIConfig> = {}): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, config);
  }

  async post<T>(endpoint: string, data?: any, config: Partial<APIConfig> = {}): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }, config);
  }

  async put<T>(endpoint: string, data?: any, config: Partial<APIConfig> = {}): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }, config);
  }

  async delete<T>(endpoint: string, config: Partial<APIConfig> = {}): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' }, config);
  }

  // Authentication Methods
  async register(userData: UserRegistration): Promise<AuthResponse> {
    return this.post<AuthResponse>('/api/auth/register', userData);
  }

  async login(credentials: UserLogin): Promise<TokenData> {
    return this.post<TokenData>('/api/auth/login', credentials);
  }

  // AI Generation Methods
  async getThemes(): Promise<{ themes: AITheme[]; count: number }> {
    return this.get<{ themes: AITheme[]; count: number }>('/api/ai/themes');
  }

  async getTitleStyles(): Promise<{ title_styles: AITitleStyle[]; count: number }> {
    return this.get<{ title_styles: AITitleStyle[]; count: number }>('/api/ai/title-styles');
  }

  async generateJournal(request: AIGenerationRequest): Promise<AIGenerationResponse> {
    return this.post<AIGenerationResponse>('/api/ai/generate-journal', request);
  }

  async getGenerationProgress(jobId: string): Promise<AIProgressResponse> {
    return this.get<AIProgressResponse>(`/api/ai/progress/${jobId}`);
  }

  // Project Library Methods
  async getProjects(): Promise<ProjectLibraryResponse> {
    return this.get<ProjectLibraryResponse>('/api/library/projects');
  }

  async getProject(projectId: string): Promise<{ project: Project; success: boolean }> {
    return this.get<{ project: Project; success: boolean }>(`/api/library/projects/${projectId}`);
  }

  async updateProject(projectId: string, settings: CustomizationSettings): Promise<{ project: Project; success: boolean; message: string }> {
    return this.put<{ project: Project; success: boolean; message: string }>(`/api/library/projects/${projectId}`, settings);
  }

  async deleteProject(projectId: string): Promise<{ success: boolean; message: string }> {
    return this.delete<{ success: boolean; message: string }>(`/api/library/projects/${projectId}`);
  }

  async getLLMProjects(): Promise<{ projects: any[]; count: number; source?: string; message?: string; error?: string }> {
    return this.get<{ projects: any[]; count: number; source?: string; message?: string; error?: string }>('/api/library/llm-projects');
  }

  // Journal Library Methods
  async getJournalLibrary(): Promise<{ projects: any[]; count: number; last_scan?: string; success: boolean }> {
    return this.get<{ projects: any[]; count: number; last_scan?: string; success: boolean }>('/api/library/llm-projects');
  }

  async getJournalFiles(projectId: string): Promise<{ project_id: string; files: any[]; success: boolean }> {
    return this.get<{ project_id: string; files: any[]; success: boolean }>(`/api/journals/${projectId}/files`);
  }

  async getJournalMetadata(projectId: string): Promise<{ project: any; success: boolean }> {
    return this.get<{ project: any; success: boolean }>(`/api/journals/${projectId}/metadata`);
  }

  async getJournalDownloadUrl(projectId: string, filePath: string): Promise<string> {
    return `${this.defaultConfig.baseURL}/api/journals/${projectId}/download/${filePath}`;
  }

  // System Health Methods
  async getHealth(): Promise<HealthResponse> {
    return this.get<HealthResponse>('/health');
  }

  async getSystemInfo(): Promise<SystemInfo> {
    return this.get<SystemInfo>('/');
  }

  // WebSocket Methods
  createWebSocketConnection(jobId: string): WebSocket {
    const wsUrl = this.baseURL.replace('http://', 'ws://').replace('https://', 'wss://');
    return new WebSocket(`${wsUrl}/ws/job/${jobId}`);
  }

  // Token Management
  setToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  removeToken(): void {
    localStorage.removeItem('access_token');
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      // Basic JWT token validation (check expiration)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp > now;
    } catch {
      return false;
    }
  }

  // Error Handling
  static isAuthError(error: unknown): error is APIError & { status?: number } {
    return error instanceof Error && (
      error.message.includes('401') ||
      error.message.includes('Could not validate credentials') ||
      error.message.includes('Not authenticated')
    );
  }

  static isNetworkError(error: unknown): error is Error {
    return error instanceof Error && (
      error.message.includes('Network error') ||
      error.message.includes('Failed to fetch')
    );
  }
}

// Create singleton instance
export const apiClient = new UnifiedBackendAPI();

// Export specific API methods for easier usage
export const authAPI = {
  register: (userData: UserRegistration) => apiClient.register(userData),
  login: (credentials: UserLogin) => apiClient.login(credentials),
  getToken: () => apiClient.getToken(),
  setToken: (token: string) => apiClient.setToken(token),
  removeToken: () => apiClient.removeToken(),
  isAuthenticated: () => apiClient.isAuthenticated(),
};

export const aiAPI = {
  getThemes: () => apiClient.getThemes(),
  getTitleStyles: () => apiClient.getTitleStyles(),
  generateJournal: (request: AIGenerationRequest) => apiClient.generateJournal(request),
  getProgress: (jobId: string) => apiClient.getGenerationProgress(jobId),
  createWebSocket: (jobId: string) => apiClient.createWebSocketConnection(jobId),
};

export const projectAPI = {
  getProjects: () => apiClient.getProjects(),
  getProject: (projectId: string) => apiClient.getProject(projectId),
  updateProject: (projectId: string, settings: CustomizationSettings) => apiClient.updateProject(projectId, settings),
  deleteProject: (projectId: string) => apiClient.deleteProject(projectId),
  getLLMProjects: () => apiClient.getLLMProjects(),
};

export const journalAPI = {
  getLibrary: () => apiClient.getJournalLibrary(),
  getFiles: (projectId: string) => apiClient.getJournalFiles(projectId),
  getMetadata: (projectId: string) => apiClient.getJournalMetadata(projectId),
  getDownloadUrl: (projectId: string, filePath: string) => apiClient.getJournalDownloadUrl(projectId, filePath),
};

export const systemAPI = {
  getHealth: () => apiClient.getHealth(),
  getSystemInfo: () => apiClient.getSystemInfo(),
};

export default apiClient;