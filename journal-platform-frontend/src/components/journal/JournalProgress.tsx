import React, { useState, useEffect } from 'react';
import { X, CheckCircle, Clock, AlertCircle, Loader2, FileText, Brain, Edit3, Download } from 'lucide-react';

interface JournalProgress {
  jobId: string;
  status: 'starting' | 'research' | 'curation' | 'editing' | 'pdf' | 'completed' | 'error';
  progress: number;
  currentAgent: string;
  message: string;
  estimatedTimeRemaining: number;
  error?: string;
}

interface JournalProgressProps {
  jobId: string;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

const JournalProgress: React.FC<JournalProgressProps> = ({ jobId, onComplete, onError }) => {
  const [progress, setProgress] = useState<JournalProgress | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [showModal, setShowModal] = useState(true);

  const agentConfig = {
    starting: { icon: Clock, color: 'gray', label: 'Initializing' },
    research: { icon: Brain, color: 'blue', label: 'Research Agent' },
    curation: { icon: FileText, color: 'indigo', label: 'Content Curator' },
    editing: { icon: Edit3, color: 'purple', label: 'Editor' },
    pdf: { icon: Download, color: 'green', label: 'PDF Builder' },
    completed: { icon: CheckCircle, color: 'green', label: 'Completed' },
    error: { icon: AlertCircle, color: 'red', label: 'Error' }
  };

  useEffect(() => {
    if (!jobId) return;

    const wsUrl = `ws://localhost:8000/ws/journal/${jobId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected for job:', jobId);
    };

    ws.onmessage = (event) => {
      try {
        const progressUpdate = JSON.parse(event.data);
        setProgress(progressUpdate);

        if (progressUpdate.status === 'completed' && onComplete) {
          setTimeout(() => {
            onComplete(progressUpdate);
          }, 2000);
        }

        if (progressUpdate.status === 'error' && onError) {
          onError(progressUpdate.error || 'Unknown error occurred');
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setProgress({
        jobId,
        status: 'error',
        progress: 0,
        currentAgent: 'Connection',
        message: 'Connection error. Please check your internet connection.',
        estimatedTimeRemaining: 0,
        error: 'WebSocket connection failed'
      });
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected for job:', jobId);
    };

    setSocket(ws);

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [jobId, onComplete, onError]);

  // Fallback polling for browsers without WebSocket support
  useEffect(() => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      const pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`/api/journals/status/${jobId}`);
          if (response.ok) {
            const progressUpdate = await response.json();
            setProgress(progressUpdate);

            if (progressUpdate.status === 'completed' && onComplete) {
              onComplete(progressUpdate);
              clearInterval(pollInterval);
            }

            if (progressUpdate.status === 'error' && onError) {
              onError(progressUpdate.error || 'Unknown error occurred');
              clearInterval(pollInterval);
            }
          }
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, 3000);

      return () => clearInterval(pollInterval);
    }
  }, [socket, jobId, onComplete, onError]);

  if (!showModal) return null;

  if (!progress) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl max-w-md w-full p-6">
          <div className="flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
            <span className="ml-3 text-gray-700">Connecting to journal creation service...</span>
          </div>
        </div>
      </div>
    );
  }

  const currentAgentConfig = agentConfig[progress.status];
  const AgentIcon = currentAgentConfig.icon;

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const getProgressColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      case 'starting': return 'bg-gray-400';
      default: return 'bg-indigo-500';
    }
  };

  const handleClose = () => {
    if (progress.status === 'completed') {
      setShowModal(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900">Creating Your Journal</h3>
          {(progress.status === 'completed' || progress.status === 'error') && (
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          )}
        </div>

        {/* Current Agent Status */}
        <div className="flex items-center space-x-4 mb-6">
          <div className={`w-12 h-12 bg-${currentAgentConfig.color}-100 rounded-xl flex items-center justify-center`}>
            <AgentIcon className={`w-6 h-6 text-${currentAgentConfig.color}-600`} />
          </div>
          <div className="flex-1">
            <div className="font-medium text-gray-900">{currentAgentConfig.label}</div>
            <div className="text-sm text-gray-600">{progress.message}</div>
          </div>
          {progress.status !== 'completed' && progress.status !== 'error' && (
            <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          )}
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Progress</span>
            <span className="text-sm font-medium text-gray-900">{progress.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(progress.status)}`}
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>

        {/* Agent Flow Visualization */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            {Object.entries(agentConfig).slice(1, -1).map(([status, config], index) => {
              const Icon = config.icon;
              const isCompleted = progress.status !== 'error' && (
                Object.keys(agentConfig).indexOf(progress.status) > Object.keys(agentConfig).indexOf(status)
              );
              const isCurrent = progress.status === status;

              return (
                <React.Fragment key={status}>
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                        isCompleted
                          ? 'bg-green-100'
                          : isCurrent
                          ? `bg-${config.color}-100`
                          : 'bg-gray-100'
                      }`}
                    >
                      <Icon
                        className={`w-4 h-4 ${
                          isCompleted
                            ? 'text-green-600'
                            : isCurrent
                            ? `text-${config.color}-600`
                            : 'text-gray-400'
                        }`}
                      />
                    </div>
                    <span className="text-xs text-gray-600 mt-1 text-center hidden sm:block">
                      {config.label}
                    </span>
                  </div>
                  {index < Object.entries(agentConfig).slice(1, -1).length - 1 && (
                    <div
                      className={`flex-1 h-1 mx-1 ${
                        isCompleted ? 'bg-green-200' : 'bg-gray-200'
                      }`}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Time Remaining */}
        {progress.status !== 'completed' && progress.status !== 'error' && (
          <div className="mb-4">
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="w-4 h-4 mr-2" />
              <span>
                {progress.estimatedTimeRemaining > 0
                  ? `Estimated time remaining: ${formatTime(progress.estimatedTimeRemaining)}`
                  : 'Calculating time remaining...'}
              </span>
            </div>
          </div>
        )}

        {/* Status Messages */}
        {progress.status === 'completed' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <div className="flex items-center text-green-800">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span className="font-medium">Journal created successfully!</span>
            </div>
            <div className="text-sm text-green-600 mt-1">
              Your personalized journal is ready for download.
            </div>
          </div>
        )}

        {progress.status === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center text-red-800">
              <AlertCircle className="w-5 h-5 mr-2" />
              <span className="font-medium">Something went wrong</span>
            </div>
            <div className="text-sm text-red-600 mt-1">
              {progress.error || 'An unexpected error occurred during journal creation.'}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Job ID: {jobId.slice(0, 8)}...
          </div>
          {progress.status === 'completed' && (
            <button
              onClick={handleClose}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              View Journal
            </button>
          )}
          {progress.status === 'error' && (
            <button
              onClick={handleClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default JournalProgress;