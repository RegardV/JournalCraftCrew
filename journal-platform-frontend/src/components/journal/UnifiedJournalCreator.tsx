/**
 * Unified Journal Creator Component
 * Replaces multiple journal creation workflows with a single CrewAI-powered interface
 */

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
} from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import EnhancedWebOnboardingAgent from '../onboarding/EnhancedWebOnboardingAgent';
import CrewAIWorkflowProgress from './CrewAIWorkflowProgress';
import {
  Sparkles,
  Rocket,
  Zap,
  Layers,
  Users,
  Clock,
  Star,
  ChevronRight,
  BookOpen,
  Target,
  Brain
} from 'lucide-react';

// Types
interface JournalCreatorProps {
  className?: string;
  onComplete?: (preferences: any) => void;
  onClose?: () => void;
  initialPreferences?: any;
}

interface QuickStartOption {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  workflowType: 'express' | 'standard' | 'comprehensive';
  estimatedTime: number;
  color: string;
  themes: string[];
}

// Quick start options for immediate journal creation
const QUICK_START_OPTIONS: QuickStartOption[] = [
  {
    id: 'mindfulness-express',
    name: 'Mindfulness Journal',
    description: 'Daily mindfulness and meditation exercises',
    icon: Brain,
    workflowType: 'express',
    estimatedTime: 15,
    color: 'blue',
    themes: ['mindfulness', 'meditation', 'stress-reduction']
  },
  {
    id: 'productivity-standard',
    name: 'Productivity Planner',
    description: 'Goal achievement and daily productivity tracking',
    icon: Target,
    workflowType: 'standard',
    estimatedTime: 30,
    color: 'green',
    themes: ['productivity', 'goals', 'achievement']
  },
  {
    id: 'creativity-comprehensive',
    name: 'Creative Expression',
    description: 'Unlock creative potential with comprehensive content',
    icon: Sparkles,
    workflowType: 'comprehensive',
    estimatedTime: 40,
    color: 'purple',
    themes: ['creativity', 'art', 'innovation']
  },
  {
    id: 'gratitude-express',
    name: 'Gratitude Practice',
    description: 'Daily gratitude and positive reflection',
    icon: Star,
    workflowType: 'express',
    estimatedTime: 15,
    color: 'yellow',
    themes: ['gratitude', 'positivity', 'appreciation']
  }
];

const UnifiedJournalCreator: React.FC<JournalCreatorProps> = ({
  className,
  onComplete,
  onClose,
  initialPreferences: externalInitialPreferences
}) => {
  const navigate = useNavigate();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [activeWorkflow, setActiveWorkflow] = useState<string | null>(null);
  const [workflowType, setWorkflowType] = useState<'express' | 'standard' | 'comprehensive'>('standard');
  const [initialPreferences, setInitialPreferences] = useState<any>(externalInitialPreferences || null);

  // Handle quick start option selection
  const handleQuickStart = useCallback((option: QuickStartOption) => {
    setWorkflowType(option.workflowType);
    setInitialPreferences({
      workflow_type: option.workflowType,
      theme: option.themes[0],
      title: option.name,
      title_style: 'inspirational',
      research_depth: option.workflowType === 'express' ? 'light' : option.workflowType === 'comprehensive' ? 'deep' : 'medium'
    });
    setShowOnboarding(true);
  }, []);

  // Handle custom journal creation
  const handleCustomCreate = useCallback(() => {
    setInitialPreferences({
      workflow_type: 'standard'
    });
    setShowOnboarding(true);
  }, []);

  // Handle onboarding completion
  const handleOnboardingComplete = useCallback(async (preferences: any) => {
    try {
      // If an external onComplete handler is provided, use it
      if (onComplete) {
        await onComplete(preferences);
        return;
      }

      // Default behavior: navigate to workflow
      const token = localStorage.getItem('access_token');

      // Step 1: Save onboarding preferences and create project
      const saveResponse = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/onboarding/save-preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          theme: preferences.theme,
          title: preferences.title,
          title_style: preferences.title_style,
          author_style: preferences.author_style,
          research_depth: preferences.research_depth
        })
      });

      if (!saveResponse.ok) {
        throw new Error(`Failed to save preferences: ${saveResponse.status}`);
      }

      const saveData = await saveResponse.json();
      const projectId = saveData.preferences.project_id;

      if (!projectId) {
        throw new Error('No project ID returned from onboarding save');
      }

      // Step 2: Start CrewAI workflow with the created project
      const workflowResponse = await fetch(`${import.meta.env.VITE_API_URL || ''}/api/crewai/start-workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          project_id: projectId,
          preferences: preferences
        })
      });

      if (!workflowResponse.ok) {
        throw new Error(`Failed to start workflow: ${workflowResponse.status}`);
      }

      const workflowData = await workflowResponse.json();

      // Close onboarding and show workflow progress
      setShowOnboarding(false);
      setActiveWorkflow(workflowData.workflow_id);

      // Navigate to workflow progress page
      navigate(`/ai-workflow/${workflowData.workflow_id}`, {
        state: { workflowData, projectId }
      });

    } catch (error) {
      console.error('Failed to start CrewAI workflow:', error);
      // Handle error (show message to user)
    }
  }, [navigate, onComplete]);

  // Handle workflow completion
  const handleWorkflowComplete = useCallback((result: any) => {
    setActiveWorkflow(null);

    // Navigate to project detail or library
    if (result.project_id) {
      navigate(`/projects/${result.project_id}`);
    } else {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI-Powered Journal Creation
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Create professional journals with our 9-agent CrewAI system.
          Choose quick start options or customize every detail.
        </p>
      </div>

      {/* Active Workflow Progress */}
      {activeWorkflow && (
        <Card className="border-purple-200 bg-purple-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <span>Active Journal Creation</span>
            </CardTitle>
            <CardDescription>
              Your AI agents are working on your journal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CrewAIWorkflowProgress
              workflowId={activeWorkflow}
              onComplete={handleWorkflowComplete}
            />
          </CardContent>
        </Card>
      )}

      {/* Quick Start Options */}
      {!activeWorkflow && !showOnboarding && (
        <>
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Quick Start Templates
            </h2>
            <p className="text-gray-600 mb-6">
              Choose a pre-configured journal template to get started immediately
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {QUICK_START_OPTIONS.map((option) => {
              const Icon = option.icon;
              return (
                <Card
                  key={option.id}
                  className="cursor-pointer transition-all hover:shadow-lg hover:scale-105 border-2 hover:border-purple-300"
                  onClick={() => handleQuickStart(option)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                      option.color === 'blue' ? 'bg-blue-100' :
                      option.color === 'green' ? 'bg-green-100' :
                      option.color === 'purple' ? 'bg-purple-100' :
                      option.color === 'yellow' ? 'bg-yellow-100' :
                      'bg-gray-100'
                    }`}>
                        <Icon className={`w-6 h-6 ${
                          option.color === 'blue' ? 'text-blue-600' :
                          option.color === 'green' ? 'text-green-600' :
                          option.color === 'purple' ? 'text-purple-600' :
                          option.color === 'yellow' ? 'text-yellow-600' :
                          'text-gray-600'
                        }`} />
                      </div>
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>{option.estimatedTime}m</span>
                      </div>
                    </div>
                    <CardTitle className="text-lg">{option.name}</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-gray-600 mb-3">{option.description}</p>
                    <div className="flex items-center justify-between">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        option.color === 'blue' ? 'bg-blue-50 text-blue-700' :
                        option.color === 'green' ? 'bg-green-50 text-green-700' :
                        option.color === 'purple' ? 'bg-purple-50 text-purple-700' :
                        option.color === 'yellow' ? 'bg-yellow-50 text-yellow-700' :
                        'bg-gray-50 text-gray-700'
                      }`}>
                        {option.workflowType}
                      </span>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </>
      )}

      {/* Custom Creation Option */}
      {!activeWorkflow && !showOnboarding && (
        <Card className="border-dashed border-2 border-gray-300 hover:border-purple-400 transition-colors">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Create Custom Journal
              </h3>
              <p className="text-gray-600 mb-4">
                Design your journal from scratch with complete control over themes, styles, and features
              </p>
              <Button
                onClick={handleCustomCreate}
                className="bg-purple-600 hover:bg-purple-700 text-white"
              >
                <BookOpen className="w-4 h-4 mr-2" />
                Start Custom Creation
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* CrewAI System Information */}
      {!activeWorkflow && !showOnboarding && (
        <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="w-5 h-5 text-purple-600" />
              <span>Powered by CrewAI 9-Agent System</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">9</div>
                <div className="text-sm text-gray-600">Specialized AI Agents</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">30+</div>
                <div className="text-sm text-gray-600">Minutes of Creation</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">100%</div>
                <div className="text-sm text-gray-600">Unique Content</div>
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-700">
              Our CrewAI system includes specialized agents for research, content creation, editing,
              visual design, and professional formatting to create truly unique, high-quality journals.
            </div>
          </CardContent>
        </Card>
      )}

      {/* Header with close button */}
      {onClose && (
        <div className="flex justify-end mb-4">
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-gray-500 rotate-180" />
          </button>
        </div>
      )}

      {/* Enhanced Onboarding Modal */}
      {showOnboarding && (
        <EnhancedWebOnboardingAgent
          onComplete={handleOnboardingComplete}
          onClose={() => setShowOnboarding(false)}
          initialPreferences={initialPreferences}
        />
      )}
    </div>
  );
};

export default UnifiedJournalCreator;