// Authentication Modal for Login and Registration

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import type { UserRegistration } from '@/types/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { login, register, isLoading, error, clearError } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    profile_type: 'personal_journaler' as const,
  });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      if (isLoginMode) {
        await login(formData.email, formData.password);
      } else {
        const userData: UserRegistration = {
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name,
          profile_type: formData.profile_type,
        };
        await register(userData);
      }
      onClose();
    } catch (error) {
      // Error is handled by the auth context
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-gray-100 overflow-hidden">
        <div className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold gradient-text mb-2">
              {isLoginMode ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="text-color-text-light">
              {isLoginMode ? 'Sign in to continue to your journal workspace' : 'Start your journaling journey today'}
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLoginMode && (
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-color-text mb-2">
                  Full Name
                </label>
                <Input
                  id="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => handleInputChange('full_name', e.target.value)}
                  required={!isLoginMode}
                  placeholder="Enter your full name"
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-color-text mb-2">
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-color-text mb-2">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                required
                placeholder="•••••••••"
              />
            </div>

            {!isLoginMode && (
              <div>
                <label htmlFor="profile_type" className="block text-sm font-medium text-color-text mb-2">
                  Profile Type
                </label>
                <select
                  id="profile_type"
                  value={formData.profile_type}
                  onChange={(e) => handleInputChange('profile_type', e.target.value)}
                  className="w-full px-4 py-3 border border-color-border rounded-xl focus:outline-none focus:ring-2 focus:ring-color-primary focus:border-color-primary bg-color-bg-muted text-color-text"
                >
                  <option value="personal_journaler">📝 Personal Journaler</option>
                  <option value="content_creator">✍️ Content Creator</option>
                  <option value="therapist">🧠 Therapist</option>
                  <option value="educator">🎓 Educator</option>
                </select>
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-3 border border-color-border rounded-xl text-color-text hover:bg-color-bg-muted transition-colors font-medium"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-3 btn-primary rounded-xl font-medium disabled:opacity-50"
                disabled={isLoading}
              >
                {isLoading ? 'Please wait...' : (isLoginMode ? 'Sign In' : 'Create Account')}
              </button>
            </div>
          </form>

          <div className="mt-8 text-center pt-6 border-t border-color-border">
            <button
              type="button"
              onClick={() => setIsLoginMode(!isLoginMode)}
              className="text-color-primary hover:text-color-primary-dark text-sm font-medium transition-colors"
            >
              {isLoginMode ? "New to Journal Craft Crew? Create account" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}