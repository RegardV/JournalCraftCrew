// Authentication Context for Unified Backend Integration

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { authAPI } from '@/lib/api';
import type {
  AuthState,
  AuthContextType,
  UserRegistration,
  UserLogin
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

      if (token && authAPI.isAuthenticated()) {
        try {
          // We could add a token validation endpoint, but for now just check if token exists and is not expired
          const payload = JSON.parse(atob(token.split('.')[1]));
          const user = {
            id: payload.user_id,
            email: '', // We'd need to fetch user details or include them in token
            full_name: '',
            profile_type: '',
            ai_credits: 0,
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
        authAPI.removeToken();
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

  // Refresh token method (placeholder)
  const refreshToken = async (): Promise<void> => {
    try {
      const token = authAPI.getToken();
      if (!token) {
        throw new Error('No token to refresh');
      }

      // In a real implementation, you'd call a refresh token endpoint
      // For now, just check if token is still valid
      if (!authAPI.isAuthenticated()) {
        logout();
        throw new Error('Token expired');
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