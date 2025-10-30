// API Types matching the unified backend structure

// Authentication Types
export interface UserRegistration {
  email: string;
  password: string;
  full_name: string;
  profile_type: 'personal_journaler' | 'content_creator' | 'therapist' | 'educator';
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: {
    id: string;
    email: string;
    full_name: string;
    profile_type: string;
    ai_credits: number;
  };
  access_token?: string;
  token_type?: string;
}

export interface TokenData {
  access_token: string;
  token_type: string;
}

// AI Generation Types
export interface AITheme {
  id: string;
  name: string;
  description: string;
  estimated_days: number;
}

export interface AITitleStyle {
  id: string;
  name: string;
  examples: string[];
}

export interface AIGenerationRequest {
  theme: string;
  title_style: string;
  description?: string;
}

export interface AIGenerationResponse {
  success: boolean;
  message: string;
  job_id: string;
  estimated_time: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface AIProgressResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress_percentage: number;
  current_stage: string;
  estimated_time_remaining: number;
  created_at: number;
}

// Project Library Types
export interface Project {
  id: string;
  user_id: string;
  title: string;
  theme: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: number;
  updated_at: number;
  customization: {
    layout: 'single-column' | 'two-column' | 'magazine';
    font_size: 'small' | 'medium' | 'large';
    color_scheme: 'default' | 'dark' | 'sepia' | 'forest';
    paper_type: 'standard' | 'premium' | 'recycled';
    binding_type: 'perfect' | 'spiral' | 'hardcover';
  };
  pages_count: number;
  word_count: number;
  export_formats: string[];
}

export interface ProjectLibraryResponse {
  projects: Project[];
  count: number;
  page: number;
  total_pages: number;
}

export interface CustomizationSettings {
  layout?: 'single-column' | 'two-column' | 'magazine';
  font_size?: 'small' | 'medium' | 'large';
  color_scheme?: 'default' | 'dark' | 'sepia' | 'forest';
  paper_type?: 'standard' | 'premium' | 'recycled';
  binding_type?: 'perfect' | 'spiral' | 'hardcover';
}

// System Health Types
export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  timestamp: string;
  data_file: string;
  users_count: number;
  projects_count: number;
}

export interface SystemInfo {
  message: string;
  version: string;
  status: 'running' | 'stopped' | 'maintenance';
  features: string[];
}

// WebSocket Message Types
export interface WebSocketProgressMessage {
  type: 'progress' | 'completed' | 'error';
  job_id: string;
  progress?: number;
  stage?: string;
  project_id?: string;
  message?: string;
  timestamp: number;
}

// API Error Types
export interface APIError {
  detail: string;
  status?: number;
}

// HTTP API Client Types
export interface APIConfig {
  baseURL: string;
  timeout: number;
  headers?: Record<string, string>;
}

export interface APIClient {
  get<T>(endpoint: string, config?: Partial<APIConfig>): Promise<T>;
  post<T>(endpoint: string, data?: any, config?: Partial<APIConfig>): Promise<T>;
  put<T>(endpoint: string, data?: any, config?: Partial<APIConfig>): Promise<T>;
  delete<T>(endpoint: string, config?: Partial<APIConfig>): Promise<T>;
}

// Auth Context Types
export interface AuthState {
  user: {
    id: string;
    email: string;
    full_name: string;
    profile_type: string;
    ai_credits: number;
  } | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (userData: UserRegistration) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

// Journal Creation Context Types
export interface JournalCreationState {
  themes: AITheme[];
  titleStyles: AITitleStyle[];
  selectedTheme: string | null;
  selectedTitleStyle: string | null;
  description: string;
  isGenerating: boolean;
  currentJob: {
    job_id: string;
    status: string;
    progress: number;
    stage: string;
  } | null;
  error: string | null;
}

export interface JournalCreationContextType extends JournalCreationState {
  loadThemes: () => Promise<void>;
  loadTitleStyles: () => Promise<void>;
  setSelectedTheme: (theme: string) => void;
  setSelectedTitleStyle: (style: string) => void;
  setDescription: (description: string) => void;
  startGeneration: () => Promise<string>;
  resetCreation: () => void;
}

// Project Context Types
export interface ProjectState {
  projects: Project[];
  selectedProject: Project | null;
  isLoading: boolean;
  error: string | null;
}

export interface ProjectContextType extends ProjectState {
  loadProjects: () => Promise<void>;
  loadProject: (projectId: string) => Promise<void>;
  updateProject: (projectId: string, settings: CustomizationSettings) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  setSelectedProject: (project: Project | null) => void;
}