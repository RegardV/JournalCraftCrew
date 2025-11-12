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
      const storedUser = localStorage.getItem('user_data');

      if (token) {
        // Check if token is expired
        if (authAPI.isAuthenticated()) {
          try {
            let user = null;

            // Try to use stored user data first
            if (storedUser) {
              try {
                user = JSON.parse(storedUser);
              } catch (parseError) {
                console.error('Failed to parse stored user data:', parseError);
                localStorage.removeItem('user_data');
              }
            }

            // If no stored user data, create a basic user from token (fallback)
            if (!user) {
              const payload = JSON.parse(atob(token.split('.')[1]));
              user = {
                id: payload.user_id,
                email: payload.email || `user_${payload.user_id}@example.com`,
                full_name: payload.full_name || payload.name || `User ${payload.user_id}`,
                profile_type: payload.profile_type || 'personal_journaler',
                ai_credits: payload.ai_credits || 10,
                subscription: payload.subscription || 'free',
              };

              // Store the user data for future use
              localStorage.setItem('user_data', JSON.stringify(user));
            }

            dispatch({
              type: 'AUTH_SUCCESS',
              payload: { user, token },
            });
          } catch (error) {
            // Token is invalid, remove it
            authAPI.removeToken();
            localStorage.removeItem('user_data');
            dispatch({ type: 'LOGOUT' });
          }
        } else {
          // Token expired, remove it and user data
          authAPI.removeToken();
          localStorage.removeItem('user_data');
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

      // Extract user data from the JWT token payload
      const payload = JSON.parse(atob(response.access_token.split('.')[1]));
      const user = {
        id: payload.user_id,
        email: payload.email || email,
        full_name: payload.full_name || payload.name || email.split('@')[0],
        profile_type: payload.profile_type || 'personal_journaler',
        ai_credits: payload.ai_credits || 10,
        subscription: payload.subscription || 'free',
      };

      // Store user data in localStorage to maintain session
      localStorage.setItem('user_data', JSON.stringify(user));

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
        // Store user data in localStorage
        localStorage.setItem('user_data', JSON.stringify(response.user));
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
    localStorage.removeItem('user_data');
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