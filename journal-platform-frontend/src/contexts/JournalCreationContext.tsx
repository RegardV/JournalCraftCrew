// Journal Creation Context for AI-powered journal generation

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import { aiAPI } from '@/lib/api';
import type {
  JournalCreationState,
  JournalCreationContextType,
  AITheme,
  AITitleStyle,
  WebSocketProgressMessage
} from '@/types/api';

// Journal creation action types
type JournalCreationAction =
  | { type: 'LOAD_THEMES_START' }
  | { type: 'LOAD_THEMES_SUCCESS'; payload: AITheme[] }
  | { type: 'LOAD_THEMES_ERROR'; payload: string }
  | { type: 'LOAD_TITLE_STYLES_START' }
  | { type: 'LOAD_TITLE_STYLES_SUCCESS'; payload: AITitleStyle[] }
  | { type: 'LOAD_TITLE_STYLES_ERROR'; payload: string }
  | { type: 'SET_THEME'; payload: string }
  | { type: 'SET_TITLE_STYLE'; payload: string }
  | { type: 'SET_DESCRIPTION'; payload: string }
  | { type: 'GENERATION_START' }
  | { type: 'GENERATION_PROGRESS'; payload: { job_id: string; status: string; progress: number; stage: string; currentAgent?: string; logs?: Array<{ timestamp: string; level: string; agent: string; message: string }>; latestLog?: string; estimatedTimeRemaining?: number } }
  | { type: 'GENERATION_COMPLETE' }
  | { type: 'GENERATION_ERROR'; payload: string }
  | { type: 'RESET_CREATION' };

// Journal creation reducer
const journalCreationReducer = (
  state: JournalCreationState,
  action: JournalCreationAction
): JournalCreationState => {
  switch (action.type) {
    case 'LOAD_THEMES_START':
      return {
        ...state,
        error: null,
      };
    case 'LOAD_THEMES_SUCCESS':
      return {
        ...state,
        themes: action.payload,
        error: null,
      };
    case 'LOAD_THEMES_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'LOAD_TITLE_STYLES_START':
      return {
        ...state,
        error: null,
      };
    case 'LOAD_TITLE_STYLES_SUCCESS':
      return {
        ...state,
        titleStyles: action.payload,
        error: null,
      };
    case 'LOAD_TITLE_STYLES_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'SET_THEME':
      return {
        ...state,
        selectedTheme: action.payload,
      };
    case 'SET_TITLE_STYLE':
      return {
        ...state,
        selectedTitleStyle: action.payload,
      };
    case 'SET_DESCRIPTION':
      return {
        ...state,
        description: action.payload,
      };
    case 'GENERATION_START':
      return {
        ...state,
        isGenerating: true,
        error: null,
        currentJob: null,
      };
    case 'GENERATION_PROGRESS':
      return {
        ...state,
        isGenerating: true,
        currentJob: action.payload,
        error: null,
      };
    case 'GENERATION_COMPLETE':
      return {
        ...state,
        isGenerating: false,
        currentJob: null,
        error: null,
      };
    case 'GENERATION_ERROR':
      return {
        ...state,
        isGenerating: false,
        currentJob: null,
        error: action.payload,
      };
    case 'RESET_CREATION':
      return {
        ...state,
        selectedTheme: null,
        selectedTitleStyle: null,
        description: '',
        isGenerating: false,
        currentJob: null,
        error: null,
      };
    default:
      return state;
  }
};

// Initial journal creation state
const initialJournalCreationState: JournalCreationState = {
  themes: [],
  titleStyles: [],
  selectedTheme: null,
  selectedTitleStyle: null,
  description: '',
  isGenerating: false,
  currentJob: null,
  error: null,
};

// Create context
const JournalCreationContext = createContext<JournalCreationContextType | undefined>(undefined);

// Journal creation provider component
interface JournalCreationProviderProps {
  children: ReactNode;
}

export const JournalCreationProvider: React.FC<JournalCreationProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(journalCreationReducer, initialJournalCreationState);

  // Load themes on mount
  useEffect(() => {
    loadThemes();
    loadTitleStyles();
  }, []);

  // Load themes method
  const loadThemes = async (): Promise<void> => {
    try {
      dispatch({ type: 'LOAD_THEMES_START' });

      const response = await aiAPI.getThemes();
      dispatch({ type: 'LOAD_THEMES_SUCCESS', payload: response.themes });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load themes';
      dispatch({ type: 'LOAD_THEMES_ERROR', payload: errorMessage });
    }
  };

  // Load title styles method
  const loadTitleStyles = async (): Promise<void> => {
    try {
      dispatch({ type: 'LOAD_TITLE_STYLES_START' });

      const response = await aiAPI.getTitleStyles();
      dispatch({ type: 'LOAD_TITLE_STYLES_SUCCESS', payload: response.title_styles });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load title styles';
      dispatch({ type: 'LOAD_TITLE_STYLES_ERROR', payload: errorMessage });
    }
  };

  // Set selected theme
  const setSelectedTheme = (theme: string): void => {
    dispatch({ type: 'SET_THEME', payload: theme });
  };

  // Set selected title style
  const setSelectedTitleStyle = (style: string): void => {
    dispatch({ type: 'SET_TITLE_STYLE', payload: style });
  };

  // Set description
  const setDescription = (description: string): void => {
    dispatch({ type: 'SET_DESCRIPTION', payload: description });
  };

  // Start journal generation
  const startGeneration = async (): Promise<string> => {
    if (!state.selectedTheme || !state.selectedTitleStyle) {
      throw new Error('Please select both a theme and title style');
    }

    try {
      dispatch({ type: 'GENERATION_START' });

      const response = await aiAPI.generateJournal({
        theme: state.selectedTheme,
        title_style: state.selectedTitleStyle,
        description: state.description || undefined,
      });

      // Set up WebSocket connection for progress updates
      const ws = aiAPI.createWebSocket(response.job_id);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Handle backend format (direct job status) or frontend format (wrapped message)
          if (data.status || data.progress !== undefined) {
            // Backend format - direct job status
            dispatch({
              type: 'GENERATION_PROGRESS',
              payload: {
                job_id: data.jobId || job_id,
                status: data.status || 'processing',
                progress: data.progress || 0,
                stage: data.message || data.currentAgent || 'Processing...',
                currentAgent: data.currentAgent,
                logs: data.logs,
                latestLog: data.log,
                estimatedTimeRemaining: data.estimatedTimeRemaining,
              },
            });

            // Check if completed
            if (data.status === 'completed') {
              dispatch({ type: 'GENERATION_COMPLETE' });
              ws.close();
            } else if (data.status === 'error') {
              dispatch({
                type: 'GENERATION_ERROR',
                payload: data.message || 'Generation failed',
              });
              ws.close();
            }
          } else {
            // Frontend format - wrapped message
            const message: WebSocketProgressMessage = data;

            if (message.type === 'progress') {
              dispatch({
                type: 'GENERATION_PROGRESS',
                payload: {
                  job_id: message.job_id,
                  status: 'processing',
                  progress: message.progress || 0,
                  stage: message.stage || 'Processing...',
                  currentAgent: message.currentAgent,
                  logs: message.logs,
                  latestLog: message.log,
                  estimatedTimeRemaining: message.estimatedTimeRemaining,
                },
              });
            } else if (message.type === 'completed') {
              dispatch({ type: 'GENERATION_COMPLETE' });
              ws.close();
            } else if (message.type === 'error') {
              dispatch({
                type: 'GENERATION_ERROR',
                payload: message.message || 'Generation failed',
              });
              ws.close();
            }
          }
        } catch (error) {
          console.error('WebSocket message parsing error:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        dispatch({
          type: 'GENERATION_ERROR',
          payload: 'Connection error during generation',
        });
        ws.close();
      };

      ws.onclose = () => {
        // WebSocket closed normally or due to error
      };

      // Set initial job info
      dispatch({
        type: 'GENERATION_PROGRESS',
        payload: {
          job_id: response.job_id,
          status: response.status,
          progress: 0,
          stage: 'Initializing...',
        },
      });

      return response.job_id;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start generation';
      dispatch({ type: 'GENERATION_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Reset creation state
  const resetCreation = (): void => {
    dispatch({ type: 'RESET_CREATION' });
  };

  const value: JournalCreationContextType = {
    ...state,
    loadThemes,
    loadTitleStyles,
    setSelectedTheme,
    setSelectedTitleStyle,
    setDescription,
    startGeneration,
    resetCreation,
  };

  return (
    <JournalCreationContext.Provider value={value}>
      {children}
    </JournalCreationContext.Provider>
  );
};

// Custom hook to use journal creation context
export const useJournalCreation = (): JournalCreationContextType => {
  const context = useContext(JournalCreationContext);
  if (context === undefined) {
    throw new Error('useJournalCreation must be used within a JournalCreationProvider');
  }
  return context;
};

export default JournalCreationContext;