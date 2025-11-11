// Authentication Context for Unified Backend Integration

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authAPI } from '@/lib/api';
import type {
  AuthState,
  AuthContextType,
  UserRegistration
} from '@/types/api';

// Auth action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: any; token: string } }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' };

// Auth reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_ERROR':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
};

// Initial auth state
const initialAuthState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialAuthState);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const token = authAPI.getToken();

      if (token) {
        // Check if token is expired
        if (authAPI.isAuthenticated()) {
          try {
            // Parse JWT token to get user info
            const payload = JSON.parse(atob(token.split('.')[1]));

            // For now, create a basic user object from token
            // In production, we might want to fetch full user details from backend
            const user = {
              id: payload.user_id,
              email: `user_${payload.user_id}@example.com`, // Temporary - we'd need to fetch this
              full_name: `User ${payload.user_id}`, // Temporary - we'd need to fetch this
              profile_type: 'personal_journaler',
              ai_credits: 10,
            };

            dispatch({
              type: 'AUTH_SUCCESS',
              payload: { user, token },
            });
          } catch (error) {
            // Token is invalid, remove it
            authAPI.removeToken();
            dispatch({ type: 'LOGOUT' });
          }
        } else {
          // Token expired, remove it and don't show login redirect immediately
          authAPI.removeToken();
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        dispatch({ type: 'LOGOUT' });
      }
    };

    initializeAuth();
  }, []);

  // Login method
  const login = async (email: string, password: string): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const response = await authAPI.login({ email, password });
      authAPI.setToken(response.access_token);

      // For now, create a basic user object from the token
      const payload = JSON.parse(atob(response.access_token.split('.')[1]));
      const user = {
        id: payload.user_id,
        email,
        full_name: 'User', // This would be fetched from user profile endpoint
        profile_type: 'personal_journaler',
        ai_credits: 10,
      };

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, token: response.access_token },
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Register method
  const register = async (userData: UserRegistration): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const response = await authAPI.register(userData);

      if (response.access_token && response.user) {
        authAPI.setToken(response.access_token);
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: { user: response.user, token: response.access_token },
        });
      } else {
        // Registration successful but no auto-login, user needs to login separately
        dispatch({ type: 'LOGOUT' });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  // Logout method
  const logout = (): void => {
    authAPI.removeToken();
    dispatch({ type: 'LOGOUT' });
  };

  // Refresh token method - attempt to re-authenticate if token expired
  const refreshToken = async (): Promise<void> => {
    try {
      const token = authAPI.getToken();
      if (!token) {
        throw new Error('No token to refresh');
      }

      // Check if token is still valid
      if (!authAPI.isAuthenticated()) {
        // Token expired - clear it and let user know they need to log in again
        logout();
        throw new Error('Session expired. Please log in again.');
      }
    } catch (error) {
      logout();
      throw error;
    }
  };

  // Clear error method
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;