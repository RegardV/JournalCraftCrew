import React, { useState, useEffect } from 'react';
import { X, ArrowLeft, ArrowRight, Sparkles, BookOpen, PenTool, BarChart3 } from 'lucide-react';

interface JournalPreferences {
  theme: string;
  title: string;
  titleStyle: string;
  authorStyle: string;
  researchDepth: string;
}

interface AuthorSuggestion {
  name: string;
  style: string;
}

interface JournalCreationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (preferences: JournalPreferences) => void;
}

const JournalCreationModal: React.FC<JournalCreationModalProps> = ({
  isOpen,
  onClose,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [preferences, setPreferences] = useState<JournalPreferences>({
    theme: '',
    title: '',
    titleStyle: 'Catchy Questions',
    authorStyle: '',
    researchDepth: 'medium'
  });
  const [authorSuggestions, setAuthorSuggestions] = useState<AuthorSuggestion[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  const predefinedThemes = [
    'Journaling for Anxiety',
    'Journaling for Productivity',
    'Journaling for Happiness',
    'Journaling for Mindfulness',
    'Journaling for Creativity',
    'Journaling for Gratitude',
    'Journaling for Goal Setting',
    'Journaling for Self-Discovery'
  ];

  const titleStyles = [
    'Catchy Questions',
    'Inspirational Quotes',
    'Direct & Actionable',
    'Reflective Prompts',
    'Narrative Style'
  ];

  const researchDepths = [
    { value: 'light', label: 'Light Research', description: '5-7 insights' },
    { value: 'medium', label: 'Medium Research', description: '8-12 insights' },
    { value: 'deep', label: 'Deep Research', description: '15-20 insights' }
  ];

  useEffect(() => {
    if (preferences.theme && currentStep === 2) {
      fetchAuthorSuggestions();
    }
  }, [preferences.theme, currentStep]);

  const fetchAuthorSuggestions = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/journals/author-suggestions?theme=${encodeURIComponent(preferences.theme)}`);
      if (response.ok) {
        const data = await response.json();
        setAuthorSuggestions(data.authors);
      } else {
        // Fallback suggestions
        setAuthorSuggestions([
          { name: 'James Clear', style: 'direct actionable' },
          { name: 'Mark Manson', style: 'blunt irreverent' },
          { name: 'Brené Brown', style: 'empathetic research-driven' },
          { name: 'Robin Sharma', style: 'inspirational narrative' },
          { name: 'Mel Robbins', style: 'direct motivational' }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch author suggestions:', error);
      // Fallback suggestions
      setAuthorSuggestions([
        { name: 'James Clear', style: 'direct actionable' },
        { name: 'Mark Manson', style: 'blunt irreverent' },
        { name: 'Brené Brown', style: 'empathetic research-driven' },
        { name: 'Robin Sharma', style: 'inspirational narrative' },
        { name: 'Mel Robbins', style: 'direct motivational' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    onComplete(preferences);
    onClose();
    // Reset form
    setCurrentStep(1);
    setPreferences({
      theme: '',
      title: '',
      titleStyle: 'Catchy Questions',
      authorStyle: '',
      researchDepth: 'medium'
    });
  };

  const filteredThemes = predefinedThemes.filter(theme =>
    theme.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Create Your AI Journal</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Step Indicators */}
        <div className="flex items-center justify-center p-6 space-x-4">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step <= currentStep
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                {step}
              </div>
              {step < 4 && (
                <div
                  className={`w-12 h-1 ml-2 ${
                    step < currentStep ? 'bg-indigo-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="p-6">
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <BookOpen className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Choose Your Theme</h3>
                <p className="text-gray-600">Select a focus area for your journal</p>
              </div>

              {/* Search */}
              <div>
                <input
                  type="text"
                  placeholder="Search themes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              {/* Theme Options */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {filteredThemes.map((theme) => (
                  <button
                    key={theme}
                    onClick={() => setPreferences({ ...preferences, theme })}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      preferences.theme === theme
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{theme}</div>
                  </button>
                ))}
              </div>

              {/* Custom Theme */}
              <div>
                <input
                  type="text"
                  placeholder="Or create a custom theme..."
                  value={preferences.theme.includes('Journaling for') ? '' : preferences.theme}
                  onChange={(e) => {
                    const value = e.target.value.trim();
                    if (value && !value.includes('Journaling for')) {
                      setPreferences({ ...preferences, theme: `Journaling for ${value}` });
                    } else if (value) {
                      setPreferences({ ...preferences, theme: value });
                    }
                  }}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <PenTool className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Journal Details</h3>
                <p className="text-gray-600">Personalize your journal</p>
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Journal Title
                </label>
                <input
                  type="text"
                  placeholder="e.g., Calm Reflections"
                  value={preferences.title}
                  onChange={(e) => setPreferences({ ...preferences, title: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              {/* Author Style */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Writing Style
                </label>
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    <span className="ml-2 text-gray-600">Loading author suggestions...</span>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {authorSuggestions.map((author) => (
                      <button
                        key={author.name}
                        onClick={() => setPreferences({ ...preferences, authorStyle: author.style })}
                        className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                          preferences.authorStyle === author.style
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="font-medium text-gray-900">{author.name}</div>
                        <div className="text-sm text-gray-600">{author.style}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Configure Options</h3>
                <p className="text-gray-600">Choose your preferences</p>
              </div>

              {/* Title Style */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title Style
                </label>
                <div className="space-y-2">
                  {titleStyles.map((style) => (
                    <button
                      key={style}
                      onClick={() => setPreferences({ ...preferences, titleStyle: style })}
                      className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                        preferences.titleStyle === style
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium text-gray-900">{style}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Research Depth */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Research Depth
                </label>
                <div className="space-y-2">
                  {researchDepths.map((depth) => (
                    <button
                      key={depth.value}
                      onClick={() => setPreferences({ ...preferences, researchDepth: depth.value })}
                      className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                        preferences.researchDepth === depth.value
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium text-gray-900">{depth.label}</div>
                      <div className="text-sm text-gray-600">{depth.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Review & Create</h3>
                <p className="text-gray-600">Review your selections</p>
              </div>

              {/* Summary */}
              <div className="bg-gray-50 rounded-xl p-6 space-y-4">
                <div>
                  <div className="text-sm text-gray-600">Theme</div>
                  <div className="font-medium text-gray-900">{preferences.theme}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Title</div>
                  <div className="font-medium text-gray-900">{preferences.title}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Writing Style</div>
                  <div className="font-medium text-gray-900">{preferences.authorStyle}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Title Style</div>
                  <div className="font-medium text-gray-900">{preferences.titleStyle}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Research Depth</div>
                  <div className="font-medium text-gray-900">
                    {researchDepths.find(d => d.value === preferences.researchDepth)?.label}
                  </div>
                </div>
              </div>

              {/* Processing Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-sm text-blue-800">
                  <strong>Processing Time:</strong> Approximately 3-5 minutes
                </div>
                <div className="text-sm text-blue-600 mt-1">
                  Our AI agents will research, curate, and create your personalized journal
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200">
          <button
            onClick={currentStep === 1 ? onClose : handlePrevious}
            className="px-6 py-3 text-gray-700 hover:text-gray-900 transition-colors"
          >
            {currentStep === 1 ? 'Cancel' : 'Previous'}
          </button>

          <div className="flex items-center space-x-3">
            {currentStep < 4 ? (
              <button
                onClick={handleNext}
                disabled={
                  (currentStep === 1 && !preferences.theme) ||
                  (currentStep === 2 && (!preferences.title || !preferences.authorStyle)) ||
                  (currentStep === 3 && (!preferences.titleStyle || !preferences.researchDepth))
                }
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                Next
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleComplete}
                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Create Journal
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JournalCreationModal;