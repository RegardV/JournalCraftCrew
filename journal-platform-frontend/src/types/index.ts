// Core platform types for the journaling system

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  subscription: 'free' | 'premium' | 'pro';
  createdAt: Date;
  lastActiveAt: Date;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  marketing: boolean;
  updates: boolean;
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'friends';
  shareAnalytics: boolean;
  allowCollaboration: boolean;
}

export interface ProjectMetadata {
  id: string;
  title: string;
  description: string;
  type: ProjectType;
  theme: string;
  status: ProjectStatus;
  visibility: 'private' | 'shared' | 'public';
  createdAt: Date;
  updatedAt: Date;
  lastEdited: Date;
  userId: string;
  collaborators: Collaborator[];
  tags: string[];
  wordCount: number;
  estimatedReadingTime: number;
  coverImage?: string;
  customSettings: ProjectSettings;
}

export type ProjectType = 'personal' | 'project' | 'therapeutic' | 'creative' | 'travel' | 'family' | 'professional';

export type ProjectStatus = 'draft' | 'in_progress' | 'review' | 'completed' | 'published' | 'archived';

export interface ProjectSettings {
  layout: 'single-column' | 'two-column' | 'magazine';
  fontSize: 'small' | 'medium' | 'large';
  fontFamily: 'serif' | 'sans-serif' | 'mono' | 'journal';
  pageNumbers: boolean;
  tableOfContents: boolean;
  dateFormat: 'us' | 'international' | 'iso';
  customCSS?: string;
}

export interface Collaborator {
  id: string;
  name: string;
  email: string;
  role: 'viewer' | 'editor' | 'owner';
  permissions: Permission[];
  joinedAt: Date;
  lastActiveAt: Date;
}

export type Permission = 'read' | 'write' | 'delete' | 'share' | 'export' | 'manage_collaborators';

export interface Chapter {
  id: string;
  title: string;
  content: string;
  order: number;
  wordCount: number;
  createdAt: Date;
  updatedAt: Date;
  authorId: string;
  tags: string[];
  mood?: string;
  location?: string;
  weather?: string;
  isLocked: boolean;
  subChapters: Chapter[];
}

export interface Journal {
  id: string;
  metadata: ProjectMetadata;
  chapters: Chapter[];
  settings: JournalSettings;
  exportHistory: ExportRecord[];
  analytics: JournalAnalytics;
  version: string;
}

export interface JournalSettings extends ProjectSettings {
  aiAssistant: boolean;
  autoSave: boolean;
  revisionHistory: boolean;
  collaborationMode: 'real-time' | 'batch' | 'disabled';
  aiWritingStyle: 'formal' | 'casual' | 'creative' | 'professional';
  aiCreativity: number; // 0-100 scale
}

export interface ExportRecord {
  id: string;
  format: ExportFormat;
  timestamp: Date;
  fileSize: number;
  downloadUrl?: string;
  status: 'processing' | 'completed' | 'failed' | 'expired';
  settings: ExportSettings;
  kdpPublished?: KDPPublishRecord;
}

export type ExportFormat = 'pdf' | 'epub' | 'mobi' | 'docx' | 'html' | 'txt';

export interface ExportSettings {
  includeImages: boolean;
  includeMetadata: boolean;
  paperSize: 'a4' | 'a5' | 'letter' | 'trade';
  margins: number;
  fontSize: number;
  fontFamily: string;
  coverImage?: string;
  watermark?: string;
  compression: 'none' | 'lossless' | 'high';
}

export interface KDPPublishRecord {
  kdpId: string;
  title: string;
  author: string;
  isbn?: string;
  publishedAt: Date;
  status: 'draft' | 'review' | 'published' | 'withdrawn';
  salesUrl?: string;
  royaltyRate: number;
}

export interface JournalAnalytics {
  views: number;
  downloads: number;
  shares: number;
  comments: number;
  averageReadingTime: number;
  completionRate: number;
  mostViewedChapters: ChapterAnalytics[];
  engagementScore: number;
  lastUpdated: Date;
}

export interface ChapterAnalytics {
  chapterId: string;
  views: number;
  averageReadingTime: number;
  comments: number;
  shares: number;
}

// Theme System Types
export interface Theme {
  id: string;
  name: string;
  description: string;
  category: ThemeCategory;
  colors: ThemeColors;
  typography: ThemeTypography;
  layout: ThemeLayout;
  preview: ThemePreview;
  isPremium: boolean;
  createdAt: Date;
  updatedAt: Date;
  author: string;
}

export type ThemeCategory = 'vintage' | 'modern' | 'minimal' | 'artistic' | 'seasonal' | 'professional';

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  error: string;
  warning: string;
  success: string;
  info: string;
}

export interface ThemeTypography {
  fontFamily: {
    primary: string;
    secondary: string;
    monospace: string;
  };
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
  };
  fontWeight: {
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
  lineHeight: {
    tight: number;
    normal: number;
    relaxed: number;
  };
}

export interface ThemeLayout {
  maxWidth: string;
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    none: string;
    sm: string;
    md: string;
    lg: string;
    full: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

export interface ThemePreview {
  thumbnail: string;
  screenshots: string[];
  demoContent: string;
}

// AI Integration Types
export interface AISuggestion {
  id: string;
  type: SuggestionType;
  content: string;
  originalContent?: string;
  context: string;
  confidence: number;
  reasoning: string;
  timestamp: Date;
  applied: boolean;
  feedback?: SuggestionFeedback;
}

export type SuggestionType =
  | 'grammar'
  | 'style'
  | 'structure'
  | 'content_enhancement'
  | 'reorganization'
  | 'title_suggestion'
  | 'character_development'
  | 'plot_point'
  | 'dialogue_improvement'
  | 'emotional_tone'
  | 'pacing';

export interface SuggestionFeedback {
  helpful: boolean;
  rating: number; // 1-5
  comment?: string;
  timestamp: Date;
}

export interface AIWritingSession {
  id: string;
  projectId: string;
  chapterId?: string;
  startTime: Date;
  endTime?: Date;
  wordCountStart: number;
  wordCountEnd: number;
  suggestionsGenerated: number;
  suggestionsAccepted: number;
  writingStyle: string;
  mood: string;
  productivity: ProductivityMetrics;
}

export interface ProductivityMetrics {
  wordsPerMinute: number;
  activeWritingTime: number; // minutes
  pauseCount: number;
  averagePauseLength: number; // seconds
  focusScore: number; // 0-100
  streakDays: number;
}

// Search and Filtering Types
export interface SearchFilters {
  query?: string;
  projectTypes?: ProjectType[];
  status?: ProjectStatus[];
  tags?: string[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  wordCountRange?: {
    min: number;
    max: number;
  };
  collaborators?: string[];
  themes?: string[];
  sortBy: SortField;
  sortOrder: 'asc' | 'desc';
}

export type SortField =
  | 'title'
  | 'createdAt'
  | 'updatedAt'
  | 'lastEdited'
  | 'wordCount'
  | 'views'
  | 'downloads';

export interface SearchResult {
  projects: ProjectMetadata[];
  total: number;
  facets: SearchFacets;
  suggestions: string[];
}

export interface SearchFacets {
  projectTypes: { [key: string]: number };
  statuses: { [key: string]: number };
  tags: { [key: string]: number };
  themes: { [key: string]: number };
}

// API Response Types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: APIError;
  message?: string;
  pagination?: PaginationInfo;
}

export interface APIError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// WebSocket Message Types for real-time collaboration
export interface WebSocketMessage {
  type: WSMessageType;
  payload: any;
  timestamp: Date;
  userId: string;
  sessionId: string;
}

export type WSMessageType =
  | 'user_join'
  | 'user_leave'
  | 'cursor_move'
  | 'text_change'
  | 'selection_change'
  | 'chapter_add'
  | 'chapter_delete'
  | 'theme_change'
  | 'comment_add'
  | 'comment_resolve';

export interface UserCursor {
  userId: string;
  position: number;
  selection?: { start: number; end: number };
  color: string;
}

export interface TextChange {
  position: number;
  content: string;
  type: 'insert' | 'delete' | 'replace';
  userId: string;
  timestamp: Date;
}

// Component Props Types
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

export interface DropdownProps {
  trigger: React.ReactNode;
  children: React.ReactNode;
  align?: 'left' | 'right' | 'center';
  width?: 'auto' | 'full';
}

export interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}