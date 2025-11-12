import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Send,
  User,
  Bot,
  Sparkles,
  Brain,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  BookOpen,
  Search,
  FileText,
  Edit3,
  Download,
  Users,
  ChevronRight,
  ChevronLeft,
  Plus
} from 'lucide-react';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<any>;
}

interface AuthorStyle {
  name: string;
  style: string;
}

interface WebOnboardingAgentProps {
  onComplete: (preferences: any) => void;
  onClose: () => void;
}

const WebOnboardingAgent: React.FC<WebOnboardingAgentProps> = ({
  onComplete,
  onClose
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [preferences, setPreferences] = useState({
    theme: '',
    title: '',
    title_style: '',
    author_style: '',
    research_depth: ''
  });
  const [availableOptions, setAvailableOptions] = useState({
    titleStyles: [],
    researchDepths: [],
    authorStyles: []
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});

  // API call helper
  const apiCall = async (endpoint: string, method: string = 'GET', data?: any) => {
    const token = localStorage.getItem('access_token');
    const url = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/onboarding${endpoint}`;

    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      ...(data && { body: JSON.stringify(data) })
    };

    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  };

  // Load initial options
  useEffect(() => {
    loadInitialOptions();
  }, []);

  const loadInitialOptions = async () => {
    try {
      const [titleStylesRes, researchDepthsRes] = await Promise.all([
        apiCall('/title-styles'),
        apiCall('/research-depths')
      ]);

      setAvailableOptions(prev => ({
        ...prev,
        titleStyles: titleStylesRes.styles || [],
        researchDepths: researchDepthsRes.depths || []
      }));
    } catch (error) {
      console.error('Failed to load options:', error);
      setErrors({ general: 'Failed to load onboarding options' });
    }
  };

  // Theme validation
  const validateTheme = async (theme: string) => {
    if (!theme.trim()) {
      setErrors(prev => ({ ...prev, theme: 'Theme is required' }));
      return;
    }

    setIsLoading(prev => ({ ...prev, theme: true }));
    try {
      const result = await apiCall('/validate-theme', 'POST', { theme });
      setPreferences(prev => ({ ...prev, theme: result.formatted_theme }));
      setErrors(prev => ({ ...prev, theme: '' }));
    } catch (error) {
      setErrors(prev => ({ ...prev, theme: 'Failed to validate theme' }));
    } finally {
      setIsLoading(prev => ({ ...prev, theme: false }));
    }
  };

  // Fetch author styles based on theme
  const fetchAuthorStyles = async () => {
    if (!preferences.theme) return;

    setIsLoading(prev => ({ ...prev, authorStyles: true }));
    try {
      const result = await apiCall('/author-styles', 'POST', {
        theme: preferences.theme
      });
      setAvailableOptions(prev => ({
        ...prev,
        authorStyles: result.authors || []
      }));
    } catch (error) {
      console.error('Failed to fetch author styles:', error);
      // Don't show error to user, will use fallback
    } finally {
      setIsLoading(prev => ({ ...prev, authorStyles: false }));
    }
  };

  // Generate titles
  const generateTitles = async () => {
    if (!preferences.theme || !preferences.title_style) return;

    setIsLoading(prev => ({ ...prev, titles: true }));
    try {
      const result = await apiCall('/generate-titles', 'POST', {
        theme: preferences.theme,
        title_style: preferences.title_style
      });
      // You can show title suggestions to user if needed
      console.log('Generated titles:', result);
    } catch (error) {
      console.error('Failed to generate titles:', error);
    } finally {
      setIsLoading(prev => ({ ...prev, titles: false }));
    }
  };

  // Fetch author styles when theme changes
  useEffect(() => {
    if (preferences.theme) {
      fetchAuthorStyles();
    }
  }, [preferences.theme]);

  // Generate titles when theme and style are set
  useEffect(() => {
    if (preferences.theme && preferences.title_style) {
      generateTitles();
    }
  }, [preferences.theme, preferences.title_style]);

  // Step components
  const ThemeStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">What's your journal theme?</h3>
        <p className="text-gray-600">Enter a topic you'd like to focus on (e.g., anxiety, productivity, mindfulness)</p>
      </div>

      <div>
        <input
          type="text"
          value={preferences.theme}
          onChange={(e) => setPreferences(prev => ({ ...prev, theme: e.target.value }))}
          onBlur={() => validateTheme(preferences.theme)}
          placeholder="e.g., Anxiety, Productivity, Mindfulness"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          disabled={isLoading.theme}
        />
        {errors.theme && (
          <p className="mt-2 text-sm text-red-600">{errors.theme}</p>
        )}
        {preferences.theme && preferences.theme.includes('Journaling for') && (
          <p className="mt-2 text-sm text-green-600">✓ Theme formatted as: {preferences.theme}</p>
        )}
        {isLoading.theme && (
          <div className="mt-2 flex items-center text-sm text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
            Validating theme...
          </div>
        )}
      </div>
    </div>
  );

  const TitleStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Give your journal a title</h3>
        <p className="text-gray-600">Choose a meaningful title for your journal</p>
      </div>

      <div>
        <input
          type="text"
          value={preferences.title}
          onChange={(e) => setPreferences(prev => ({ ...prev, title: e.target.value }))}
          placeholder="e.g., My Mindful Journey, Daily Reflections"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
        {errors.title && (
          <p className="mt-2 text-sm text-red-600">{errors.title}</p>
        )}
      </div>

      <div>
        <h4 className="text-md font-medium text-gray-900 mb-3">Choose a title style</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {availableOptions.titleStyles.map((style: any) => (
            <button
              key={style.id}
              onClick={() => setPreferences(prev => ({ ...prev, title_style: style.id }))}
              className={`p-3 border rounded-lg text-left transition-colors ${
                preferences.title_style === style.id
                  ? 'border-purple-500 bg-purple-50 text-purple-900'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-medium">{style.name}</div>
              <div className="text-sm text-gray-600">{style.description}</div>
            </button>
          ))}
        </div>
        {isLoading.titles && (
          <div className="mt-3 flex items-center text-sm text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
            Generating title ideas...
          </div>
        )}
      </div>
    </div>
  );

  const AuthorStyleStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Choose your writing style</h3>
        <p className="text-gray-600">Select an author whose writing style you'd like for your journal</p>
      </div>

      {isLoading.authorStyles ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin mr-3 text-purple-600" />
          <span className="text-gray-600">Finding authors that match your theme...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {availableOptions.authorStyles.map((author: AuthorStyle, index: number) => (
            <button
              key={index}
              onClick={() => setPreferences(prev => ({ ...prev, author_style: author.style }))}
              className={`p-4 border rounded-lg text-left transition-colors ${
                preferences.author_style === author.style
                  ? 'border-purple-500 bg-purple-50 text-purple-900'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-semibold text-lg">{author.name}</div>
              <div className="text-sm text-gray-600 mt-1">{author.style}</div>
            </button>
          ))}
        </div>
      )}

      {availableOptions.authorStyles.length === 0 && !isLoading.authorStyles && (
        <div className="text-center py-8 text-gray-500">
          No author styles available. Please go back and choose a different theme.
        </div>
      )}
    </div>
  );

  const ResearchDepthStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">How deep should we research?</h3>
        <p className="text-gray-600">Choose the level of research depth for your journal content</p>
      </div>

      <div className="space-y-3">
        {availableOptions.researchDepths.map((depth: any) => (
          <button
            key={depth.id}
            onClick={() => setPreferences(prev => ({ ...prev, research_depth: depth.id }))}
            className={`w-full p-4 border rounded-lg text-left transition-colors ${
              preferences.research_depth === depth.id
                ? 'border-purple-500 bg-purple-50 text-purple-900'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-lg">{depth.name}</div>
                <div className="text-sm text-gray-600 mt-1">
                  {depth.insights} research insights
                </div>
              </div>
              {preferences.research_depth === depth.id && (
                <CheckCircle className="w-6 h-6 text-purple-600" />
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  const ReviewStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Review your preferences</h3>
        <p className="text-gray-600">Please review your journal creation preferences before starting</p>
      </div>

      <div className="bg-gray-50 rounded-lg p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-500">Theme</div>
            <div className="font-medium text-gray-900">{preferences.theme}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Title</div>
            <div className="font-medium text-gray-900">{preferences.title}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Title Style</div>
            <div className="font-medium text-gray-900">{preferences.title_style}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Writing Style</div>
            <div className="font-medium text-gray-900">{preferences.author_style}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Research Depth</div>
            <div className="font-medium text-gray-900">{preferences.research_depth}</div>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Brain className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <div className="font-medium text-blue-900">AI Crew Ready</div>
            <div className="text-sm text-blue-700 mt-1">
              Your preferences are complete! Our AI crew will now create a personalized journal based on your choices.
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const steps: OnboardingStep[] = [
    {
      id: 'theme',
      title: 'Theme Selection',
      description: 'Choose your journal focus area',
      component: ThemeStep
    },
    {
      id: 'title',
      title: 'Title & Style',
      description: 'Name your journal and choose style',
      component: TitleStep
    },
    {
      id: 'author',
      title: 'Writing Style',
      description: 'Select author voice and tone',
      component: AuthorStyleStep
    },
    {
      id: 'depth',
      title: 'Research Depth',
      description: 'Choose content depth level',
      component: ResearchDepthStep
    },
    {
      id: 'review',
      title: 'Review & Start',
      description: 'Review preferences and begin',
      component: ReviewStep
    }
  ];

  const canProceed = () => {
    switch (steps[currentStep].id) {
      case 'theme':
        return preferences.theme && !errors.theme;
      case 'title':
        return preferences.title && preferences.title_style;
      case 'author':
        return preferences.author_style;
      case 'depth':
        return preferences.research_depth;
      case 'review':
        return Object.values(preferences).every(val => val && val.toString().trim());
      default:
        return false;
    }
  };

  const handleNext = async () => {
    if (!canProceed()) {
      return;
    }

    if (currentStep === steps.length - 1) {
      // Complete onboarding
      await handleComplete();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleComplete = async () => {
    setIsProcessing(true);
    try {
      // Step 1: Save preferences and create project
      const result = await apiCall('/save-preferences', 'POST', {
        theme: preferences.theme,
        title: preferences.title,
        title_style: preferences.title_style,
        author_style: preferences.author_style,
        research_depth: preferences.research_depth
      });

      // Step 2: Start CrewAI workflow
      const workflowResponse = await apiCall('/crewai/start-workflow', 'POST', {
        project_id: result.preferences.project_id,
        preferences: result.preferences
      });

      // Pass complete data to parent component
      onComplete({
        ...preferences,
        ...result.preferences,
        project_id: result.preferences.project_id,
        workflow_id: workflowResponse.workflow_id,
        workflow_status: workflowResponse.status,
        estimated_time_minutes: workflowResponse.estimated_time_minutes
      });
    } catch (error) {
      console.error('Failed to start CrewAI workflow:', error);
      setErrors({ general: 'Failed to start journal creation. Please try again.' });
    } finally {
      setIsProcessing(false);
    }
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">AI Journal Onboarding</h3>
              <p className="text-sm text-gray-600">Create your personalized journal with AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Progress Steps */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  index <= currentStep
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {index < currentStep ? '✓' : index + 1}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-12 h-1 mx-2 ${
                    index < currentStep ? 'bg-purple-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="mt-3 text-sm text-gray-600">
            Step {currentStep + 1} of {steps.length}: {steps[currentStep].title}
          </div>
        </div>

        {/* Step Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {errors.general && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                <div className="text-red-700">{errors.general}</div>
              </div>
            </div>
          )}

          <CurrentStepComponent />
        </div>

        {/* Navigation */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className={`px-4 py-2 rounded-lg transition-colors ${
                currentStep === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <ChevronLeft className="w-4 h-4 mr-2 inline" />
              Previous
            </button>

            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>5-10 minutes remaining</span>
            </div>

            <button
              onClick={handleNext}
              disabled={!canProceed() || isProcessing}
              className={`px-6 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                !canProceed() || isProcessing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : currentStep === steps.length - 1
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700'
                  : 'bg-purple-600 text-white hover:bg-purple-700'
              }`}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : currentStep === steps.length - 1 ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Start Journal Creation
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebOnboardingAgent;