/**
 * Enhanced User Registration Component
 * Supports dual user types: personal journaler vs content creator
 */

import React, { useState } from 'react'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'

interface UserRegistrationData {
  email: string
  password: string
  full_name?: string
  profile_type: 'personal_journaler' | 'content_creator'
}

const EnhancedRegistration: React.FC = () => {
  const [formData, setFormData] = useState<UserRegistrationData>({
    email: '',
    password: '',
    full_name: '',
    profile_type: 'personal_journaler'
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(1) // 1: Account Info, 2: Profile Selection, 3: Complete

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))

    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validatePassword = (password: string): boolean => {
    return password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password)
  }

  const validateStep = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (step === 1) {
      if (!formData.email) {
        newErrors.email = 'Email is required'
      } else if (!validateEmail(formData.email)) {
        newErrors.email = 'Please enter a valid email address'
      }

      if (!formData.password) {
        newErrors.password = 'Password is required'
      } else if (!validatePassword(formData.password)) {
        newErrors.password = 'Password must be at least 8 characters and include uppercase, lowercase, and numbers'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateStep()) {
      if (step < 3) {
        setStep(step + 1)
      }
    }
  }

  const handlePrevious = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateStep()) {
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      const data = await response.json()

      // Store token for immediate login
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('user_data', JSON.stringify(data.user))
      }

      // Redirect to dashboard or onboarding
      window.location.href = '/dashboard'

    } catch (error) {
      setErrors({ submit: error instanceof Error ? error.message : 'An error occurred during registration' })
    } finally {
      setIsLoading(false)
    }
  }

  const ProfileTypeSelector = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Choose Your Account Type
      </h3>

      <div className="grid gap-4">
        {/* Personal Journaler Option */}
        <label
          className={`
            relative flex cursor-pointer rounded-lg border-2 p-4 transition-all
            ${formData.profile_type === 'personal_journaler'
              ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }
          `}
        >
          <input
            type="radio"
            name="profile_type"
            value="personal_journaler"
            checked={formData.profile_type === 'personal_journaler'}
            onChange={(e) => setFormData(prev => ({ ...prev, profile_type: e.target.value as UserRegistrationData['profile_type'] }))}
            className="sr-only"
            disabled={isLoading}
          />

          <div className="flex-1">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C12 2.253 13 1 12v8c0-5.523-4.477-10-10-10S7.477 0 13 0V6a3 3 0 00-3-3z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l8 8v10H7V7l6-6z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Personal Journaler</h4>
            </div>

            <div className="space-y-2">
              <p className="text-gray-700">
                Perfect for individuals who want to maintain a personal journaling practice.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Daily mindfulness and reflection exercises</li>
                <li>• Use your own OpenAI API key</li>
                <li>• Personal journal library</li>
                <li>• Basic export options</li>
              </ul>
            </div>
          </div>
        </label>

        {/* Content Creator Option */}
        <label
          className={`
            relative flex cursor-pointer rounded-lg border-2 p-4 transition-all
            ${formData.profile_type === 'content_creator'
              ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }
          `}
        >
          <input
            type="radio"
            name="profile_type"
            value="content_creator"
            checked={formData.profile_type === 'content_creator'}
            onChange={(e) => setFormData(prev => ({ ...prev, profile_type: e.target.value as UserRegistrationData['profile_type'] }))}
            className="sr-only"
            disabled={isLoading}
          />

          <div className="flex-1">
            <div className="flex items-center mb-2">
              <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2 2v6a2 2 0 012 2h6a2 2 0 002-2V7a2 2 0 00-2-2z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l8 8v10H7V7l6-6z" />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Content Creator</h4>
            </div>

            <div className="space-y-2">
              <p className="text-gray-700">
                Create and sell journaling content, courses, and templates.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Use your own OpenAI API key</li>
                <li>• Advanced customization tools</li>
                <li>• Commercial publishing options</li>
                <li>• Template marketplace access</li>
              </ul>
            </div>
          </div>
        </label>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6">
        <div className="text-center">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create Your Account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join thousands of users discovering the power of AI-assisted journaling
          </p>
        </div>

        <Card className="mt-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Step 1: Basic Information */}
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                    Full Name (Optional)
                  </label>
                  <Input
                    id="full_name"
                    name="full_name"
                    type="text"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    placeholder="John Doe"
                    disabled={isLoading}
                    error={errors.full_name}
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email Address
                  </label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="you@example.com"
                    disabled={isLoading}
                    error={errors.email}
                    required
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                    Password
                  </label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="•••••••••"
                    disabled={isLoading}
                    error={errors.password}
                    required
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Must be at least 8 characters with uppercase, lowercase, and numbers
                  </p>
                </div>
              </div>
            )}

            {/* Step 2: Profile Type Selection */}
            {step === 2 && <ProfileTypeSelector />}

            {/* Step 3: Review */}
            {step === 3 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Review Your Information</h3>

                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Account Type:</span>
                    <span className="font-medium capitalize">{formData.profile_type.replace('_', ' ')}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Email:</span>
                    <span className="font-medium">{formData.email}</span>
                  </div>

                  {formData.full_name && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Name:</span>
                      <span className="font-medium">{formData.full_name}</span>
                    </div>
                  )}
                </div>

                <div className="text-sm text-gray-600">
                  By creating an account, you agree to our Terms of Service and Privacy Policy.
                </div>
              </div>
            )}

            {/* Error Display */}
            {errors.submit && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-800">{errors.submit}</div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between">
              <div>
                {step > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handlePrevious}
                    disabled={isLoading}
                  >
                    Previous
                  </Button>
                )}
              </div>

              <div className="flex space-x-3">
                {step < 3 && (
                  <Button
                    type="button"
                    onClick={handleNext}
                    disabled={isLoading}
                  >
                    Next
                  </Button>
                )}

                {step === 3 && (
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full"
                  >
                    {isLoading ? 'Creating Account...' : 'Create Account'}
                  </Button>
                )}
              </div>
            </div>
          </form>
        </Card>

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in here
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default EnhancedRegistration