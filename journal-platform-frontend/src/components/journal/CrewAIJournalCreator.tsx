import React, { useState, useCallback } from 'react';
import WebOnboardingAgent from '../onboarding/WebOnboardingAgent';
import CrewAIWorkflowProgress from './CrewAIWorkflowProgress';

interface OnboardingResult {
  theme: string;
  title: string;
  title_style: string;
  author_style: string;
  research_depth: string;
  project_id: number;
  workflow_id: string;
  workflow_status: string;
  estimated_time_minutes: number;
  run_directory?: string;
}

interface CrewAIJournalCreatorProps {
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
  onClose?: () => void;
  isOpen: boolean;
}

const CrewAIJournalCreator: React.FC<CrewAIJournalCreatorProps> = ({
  onComplete,
  onError,
  onClose,
  isOpen
}) => {
  const [currentView, setCurrentView] = useState<'onboarding' | 'workflow'>('onboarding');
  const [onboardingResult, setOnboardingResult] = useState<OnboardingResult | null>(null);
  const [workflowError, setWorkflowError] = useState<string | null>(null);

  const handleOnboardingComplete = useCallback((result: OnboardingResult) => {
    console.log('Onboarding completed:', result);
    setOnboardingResult(result);
    setCurrentView('workflow');
  }, []);

  const handleWorkflowComplete = useCallback((result: any) => {
    console.log('Workflow completed:', result);

    // Combine onboarding and workflow results
    const finalResult = {
      ...onboardingResult,
      workflow_result: result,
      completed_at: new Date().toISOString()
    };

    if (onComplete) {
      onComplete(finalResult);
    }

    // Auto-close after a short delay
    setTimeout(() => {
      if (onClose) onClose();
    }, 3000);
  }, [onboardingResult, onComplete, onClose]);

  const handleWorkflowError = useCallback((error: string) => {
    console.error('Workflow error:', error);
    setWorkflowError(error);

    if (onError) {
      onError(error);
    }
  }, [onError]);

  const handleBackToOnboarding = useCallback(() => {
    setCurrentView('onboarding');
    setWorkflowError(null);
  }, []);

  const handleClose = useCallback(() => {
    if (onClose) onClose();
  }, [onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <>
      {/* Onboarding View */}
      {currentView === 'onboarding' && (
        <WebOnboardingAgent
          onComplete={handleOnboardingComplete}
          onClose={handleClose}
        />
      )}

      {/* Workflow Progress View */}
      {currentView === 'workflow' && onboardingResult && (
        <CrewAIWorkflowProgress
          workflowId={onboardingResult.workflow_id}
          projectId={onboardingResult.project_id}
          onComplete={handleWorkflowComplete}
          onError={handleWorkflowError}
          onClose={handleClose}
        />
      )}

      {/* Workflow Error State */}
      {workflowError && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">❌</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Workflow Failed</h3>
              <p className="text-gray-600 mb-6">{workflowError}</p>
              <div className="flex items-center justify-center space-x-3">
                <button
                  onClick={handleBackToOnboarding}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Try Again
                </button>
                <button
                  onClick={handleClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CrewAIJournalCreator;