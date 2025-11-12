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
  Plus,
  Zap,
  Target,
  Layers,
  Rocket,
  Info,
  Star,
  TrendingUp
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

interface WorkflowType {
  id: string;
  name: string;
  description: string;
  agents: string[];
  estimatedTime: number;
  icon: React.ComponentType<any>;
  features: string[];
  recommended?: boolean;
}

interface CrewAIAgent {
  id: string;
  name: string;
  role: string;
  description: string;
  icon: React.ComponentType<any>;
  capabilities: string[];
  estimatedTime: number;
}

interface EnhancedWebOnboardingAgentProps {
  onComplete: (preferences: any) => void;
  onClose: () => void;
}

// CrewAI Agent Information
const CREWAI_AGENTS: CrewAIAgent[] = [
  {
    id: 'onboarding',
    name: 'Onboarding Agent',
    role: 'User Experience Specialist',
    description: 'Collects your preferences and guides you through the journal creation process',
    icon: User,
    capabilities: ['Preference collection', 'Dynamic author style selection', 'Project setup'],
    estimatedTime: 2
  },
  {
    id: 'discovery',
    name: 'Discovery Agent',
    role: 'Creative Title Generator',
    description: 'Generates unique, compelling title ideas based on your theme and style preferences',
    icon: Target,
    capabilities: ['Title generation', 'SEO optimization', 'Style alignment'],
    estimatedTime: 3
  },
  {
    id: 'research',
    name: 'Research Agent',
    role: 'Theme Research Specialist',
    description: 'Gathers evidence-based insights and research specific to your journal theme',
    icon: Search,
    capabilities: ['Theme-specific research', 'Evidence-based insights', 'Expert opinions'],
    estimatedTime: 8
  },
  {
    id: 'content_curator',
    name: 'Content Curator Agent',
    role: 'Journal Structure Architect',
    description: 'Creates comprehensive 30-day journal structure with themed daily entries',
    icon: FileText,
    capabilities: ['30-day structure', 'Lead magnet creation', 'Content organization'],
    estimatedTime: 10
  },
  {
    id: 'editor',
    name: 'Editor Agent',
    role: 'Content Polish Specialist',
    description: 'Refines and polishes content for clarity, engagement, and positive tone',
    icon: Edit3,
    capabilities: ['Content polishing', 'Sentiment analysis', 'Style application'],
    estimatedTime: 6
  },
  {
    id: 'media',
    name: 'Media Agent',
    role: 'Visual Asset Generator',
    description: 'Creates images and visual elements to enhance your journal experience',
    icon: Sparkles,
    capabilities: ['Image generation', 'Visual assets', 'Media optimization'],
    estimatedTime: 5
  },
  {
    id: 'pdf_builder',
    name: 'PDF Builder Agent',
    role: 'Document Production Specialist',
    description: 'Transforms content into professionally formatted PDF documents',
    icon: Download,
    capabilities: ['Professional PDFs', 'Typography', 'EPUB/KDP formats'],
    estimatedTime: 4
  },
  {
    id: 'manager',
    name: 'Manager Agent',
    role: 'Workflow Orchestrator',
    description: 'Coordinates all agents and manages the complete workflow process',
    icon: Brain,
    capabilities: ['Agent coordination', 'Quality control', 'User interaction'],
    estimatedTime: 1
  }
];

// Workflow Types
const WORKFLOW_TYPES: WorkflowType[] = [
  {
    id: 'express',
    name: 'Express Workflow',
    description: 'Quick journal creation with essential AI agents',
    agents: ['onboarding', 'discovery', 'content_curator', 'pdf_builder'],
    estimatedTime: 15,
    icon: Rocket,
    features: ['4 essential agents', 'Basic customization', 'Fast delivery'],
    recommended: true
  },
  {
    id: 'standard',
    name: 'Standard Workflow',
    description: 'Complete journal creation with research and editing',
    agents: ['onboarding', 'discovery', 'research', 'content_curator', 'editor', 'pdf_builder'],
    estimatedTime: 30,
    icon: Zap,
    features: ['6 specialized agents', 'Deep research', 'Professional editing']
  },
  {
    id: 'comprehensive',
    name: 'Comprehensive Workflow',
    description: 'Full AI-powered experience with all 9 CrewAI agents',
    agents: ['onboarding', 'discovery', 'research', 'content_curator', 'editor', 'media', 'pdf_builder', 'manager'],
    estimatedTime: 40,
    icon: Layers,
    features: ['All 9 agents', 'Visual assets', 'Premium quality', 'Multiple formats']
  }
];

const EnhancedWebOnboardingAgent: React.FC<EnhancedWebOnboardingAgentProps> = ({
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
    research_depth: '',
    workflow_type: 'standard' // Default to standard workflow
  });
  const [availableOptions, setAvailableOptions] = useState({
    titleStyles: [],
    researchDepths: [],
    authorStyles: []
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});

  // Enhanced onboarding steps with CrewAI agent showcase
  const steps: OnboardingStep[] = [
    {
      id: 'workflow',
      title: 'AI Workflow Selection',
      description: 'Choose your AI-powered journal creation experience',
      component: WorkflowTypeStep
    },
    {
      id: 'agents',
      title: 'Meet Your AI Team',
      description: 'Discover the CrewAI agents that will create your journal',
      component: AgentsShowcaseStep
    },
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

  // Workflow Type Selection Component
  const WorkflowTypeStep = () => {
    const selectedWorkflow = WORKFLOW_TYPES.find(w => w.id === preferences.workflow_type);
    const selectedAgents = CREWAI_AGENTS.filter(agent =>
      selectedWorkflow?.agents.includes(agent.id)
    );

    return (
      <div className="space-y-6">
        <div className="text-center">
          <h3 className="text-xl font-semibold mb-2">Choose Your AI Experience</h3>
          <p className="text-gray-600">Select the level of AI assistance for your journal creation</p>
        </div>

        <div className="grid gap-4">
          {WORKFLOW_TYPES.map((workflow) => {
            const Icon = workflow.icon;
            const isSelected = preferences.workflow_type === workflow.id;
            const workflowAgents = CREWAI_AGENTS.filter(agent => workflow.agents.includes(agent.id));

            return (
              <div
                key={workflow.id}
                onClick={() => setPreferences(prev => ({ ...prev, workflow_type: workflow.id }))}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  isSelected ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-6 h-6 ${isSelected ? 'text-purple-600' : 'text-gray-600'}`} />
                    <div>
                      <h4 className="font-semibold flex items-center gap-2">
                        {workflow.name}
                        {workflow.recommended && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                            Recommended
                          </span>
                        )}
                      </h4>
                      <p className="text-sm text-gray-600">{workflow.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{workflow.estimatedTime} min</div>
                    <div className="text-xs text-gray-500">{workflow.agents.length} agents</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex flex-wrap gap-1">
                    {workflow.features.map((feature, idx) => (
                      <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {feature}
                      </span>
                    ))}
                  </div>
                  {isSelected && (
                    <div className="mt-3 p-3 bg-white rounded border">
                      <div className="text-sm font-medium text-gray-700 mb-2">Active Agents:</div>
                      <div className="grid grid-cols-2 gap-2">
                        {workflowAgents.map(agent => {
                          const AgentIcon = agent.icon;
                          return (
                            <div key={agent.id} className="flex items-center space-x-2 text-xs">
                              <AgentIcon className="w-3 h-3 text-purple-600" />
                              <span>{agent.name}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {selectedWorkflow && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Info className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">Selected Workflow</span>
            </div>
            <div className="text-sm text-blue-800">
              <strong>{selectedWorkflow.name}</strong> will use {selectedAgents.length} specialized AI agents
              to create your journal in approximately {selectedWorkflow.estimatedTime} minutes.
            </div>
          </div>
        )}
      </div>
    );
  };

  // Agents Showcase Component
  const AgentsShowcaseStep = () => {
    const selectedWorkflow = WORKFLOW_TYPES.find(w => w.id === preferences.workflow_type);
    const activeAgents = selectedWorkflow ?
      CREWAI_AGENTS.filter(agent => selectedWorkflow.agents.includes(agent.id)) :
      CREWAI_AGENTS;

    return (
      <div className="space-y-6">
        <div className="text-center">
          <h3 className="text-xl font-semibold mb-2">Meet Your AI Team</h3>
          <p className="text-gray-600">
            {activeAgents.length} specialized CrewAI agents will work together to create your journal
          </p>
        </div>

        <div className="grid gap-4 max-h-96 overflow-y-auto">
          {activeAgents.map((agent, index) => {
            const Icon = agent.icon;
            return (
              <div key={agent.id} className="border rounded-lg p-4 bg-white">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-purple-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold">{agent.name}</h4>
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        ~{agent.estimatedTime} min
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mb-2">{agent.role}</div>
                    <p className="text-sm text-gray-700 mb-3">{agent.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {agent.capabilities.map((capability, idx) => (
                        <span key={idx} className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded">
                          {capability}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-600" />
            <span className="text-sm font-medium text-green-900">AI-Powered Excellence</span>
          </div>
          <div className="text-sm text-green-800">
            Each agent brings specialized expertise to ensure your journal is professional,
            engaging, and perfectly tailored to your preferences.
          </div>
        </div>
      </div>
    );
  };

  // Theme Step Component (Enhanced with agent preview)
  const ThemeStep = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Journal Theme
        </label>
        <input
          type="text"
          value={preferences.theme}
          onChange={(e) => setPreferences(prev => ({ ...prev, theme: e.target.value }))}
          placeholder="e.g., mindfulness, productivity, creativity..."
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 ${
            errors.theme ? 'border-red-300' : 'border-gray-300'
          }`}
        />
        {errors.theme && (
          <p className="text-red-500 text-sm mt-1">{errors.theme}</p>
        )}
      </div>

      {preferences.theme && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Bot className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">AI Agent Preview</span>
          </div>
          <div className="text-sm text-blue-800">
            <strong>Research Agent</strong> will gather evidence-based insights about "{preferences.theme}"
            and <strong>Content Curator Agent</strong> will create themed daily entries.
          </div>
        </div>
      )}
    </div>
  );

  // Other step components (simplified for brevity - would be enhanced similarly)
  const TitleStep = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Journal Title
        </label>
        <input
          type="text"
          value={preferences.title}
          onChange={(e) => setPreferences(prev => ({ ...prev, title: e.target.value }))}
          placeholder="Enter your journal title..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Title Style
        </label>
        <select
          value={preferences.title_style}
          onChange={(e) => setPreferences(prev => ({ ...prev, title_style: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">Select style...</option>
          <option value="inspirational">Inspirational</option>
          <option value="practical">Practical</option>
          <option value="creative">Creative</option>
          <option value="professional">Professional</option>
        </select>
      </div>
    </div>
  );

  const AuthorStyleStep = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Writing Style
        </label>
        <select
          value={preferences.author_style}
          onChange={(e) => setPreferences(prev => ({ ...prev, author_style: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">Select writing style...</option>
          <option value="inspirational">Inspirational</option>
          <option value="professional">Professional</option>
          <option value="conversational">Conversational</option>
          <option value="academic">Academic</option>
        </select>
      </div>
    </div>
  );

  const ResearchDepthStep = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Research Depth
        </label>
        <div className="grid grid-cols-3 gap-4">
          {[
            { id: 'light', name: 'Light', desc: '5 insights', time: '5 min' },
            { id: 'medium', name: 'Standard', desc: '15 insights', time: '10 min' },
            { id: 'deep', name: 'Deep', desc: '25 insights', time: '15 min' }
          ].map(depth => (
            <div
              key={depth.id}
              onClick={() => setPreferences(prev => ({ ...prev, research_depth: depth.id }))}
              className={`border rounded-lg p-3 cursor-pointer text-center ${
                preferences.research_depth === depth.id ? 'border-purple-500 bg-purple-50' : 'border-gray-200'
              }`}
            >
              <div className="font-medium">{depth.name}</div>
              <div className="text-sm text-gray-600">{depth.desc}</div>
              <div className="text-xs text-gray-500">{depth.time}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ReviewStep = () => {
    const selectedWorkflow = WORKFLOW_TYPES.find(w => w.id === preferences.workflow_type);

    return (
      <div className="space-y-6">
        <div className="text-center">
          <h3 className="text-xl font-semibold mb-2">Ready to Start</h3>
          <p className="text-gray-600">Review your preferences and begin your AI-powered journal creation</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-6 space-y-4">
          <h4 className="font-semibold">Your Journal Preferences</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm font-medium text-gray-500">Workflow:</span>
              <div className="font-medium">{selectedWorkflow?.name}</div>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Theme:</span>
              <div className="font-medium">{preferences.theme || 'Not set'}</div>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Title:</span>
              <div className="font-medium">{preferences.title || 'Not set'}</div>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Research Depth:</span>
              <div className="font-medium capitalize">{preferences.research_depth || 'Not set'}</div>
            </div>
          </div>

          <div className="pt-4 border-t">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-500">Estimated Time</div>
                <div className="text-lg font-semibold">{selectedWorkflow?.estimatedTime || 30} minutes</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-500">AI Agents</div>
                <div className="text-lg font-semibold">{selectedWorkflow?.agents.length || 6} agents</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">
              Ready to create your AI-powered journal!
            </span>
          </div>
        </div>
      </div>
    );
  };

  const canProceed = () => {
    switch (steps[currentStep].id) {
      case 'workflow':
        return preferences.workflow_type;
      case 'agents':
        return true; // Agents showcase is informational
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
    if (currentStep === steps.length - 1) {
      // Complete onboarding
      setIsProcessing(true);
      try {
        await onComplete(preferences);
      } catch (error) {
        console.error('Onboarding completion error:', error);
      } finally {
        setIsProcessing(false);
      }
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const currentStepComponent = steps[currentStep].component;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">AI Journal Creation</h2>
            <p className="text-gray-600 mt-1">Powered by CrewAI 9-Agent System</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Steps */}
        <div className="px-6 py-4 border-b">
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
          <div className="flex justify-between mt-2">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`text-xs ${
                  index <= currentStep ? 'text-purple-600 font-medium' : 'text-gray-500'
                }`}
              >
                {step.title}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {steps[currentStep].title}
            </h3>
            <p className="text-gray-600">{steps[currentStep].description}</p>
          </div>

          <div className="min-h-[300px]">
            {React.createElement(currentStepComponent, {
              preferences,
              setPreferences,
              errors,
              setErrors,
              isLoading,
              setIsLoading
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentStep === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center space-x-2">
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </div>
          </button>

          <button
            onClick={handleNext}
            disabled={!canProceed() || isProcessing}
            className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
              canProceed() && !isProcessing
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>{currentStep === steps.length - 1 ? 'Start Creation' : 'Next'}</span>
                {currentStep < steps.length - 1 && <ChevronRight className="w-4 h-4" />}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedWebOnboardingAgent;