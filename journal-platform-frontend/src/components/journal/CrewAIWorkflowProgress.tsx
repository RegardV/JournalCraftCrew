import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Loader2,
  CheckCircle,
  AlertCircle,
  Clock,
  Users,
  Search,
  Brain,
  Edit3,
  Image,
  FileText,
  Download,
  ChevronDown,
  ChevronRight,
  Pause,
  Play,
  Square
} from 'lucide-react';

interface WorkflowStep {
  step_id: string;
  step_name: string;
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress_percentage: number;
  start_time?: string;
  end_time?: string;
  result_data?: any;
  error_message?: string;
}

interface AgentProgress {
  agent_name: string;
  current_step: number;
  total_steps: number;
  progress_percentage: number;
  current_subtask?: string;
  completed_subtasks: number;
  total_subtasks: number;
  start_time: string;
  estimated_completion?: string;
}

interface WorkflowStatus {
  workflow_id: string;
  project_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_step: number;
  progress_percentage: number;
  steps: WorkflowStep[];
  start_time: string;
  estimated_completion?: string;
  result_data?: any;
  message?: string;
  timestamp?: string;
  // Enhanced fields for detailed tracking
  agent_progress?: Record<string, AgentProgress>;
  notifications?: Array<{
    type: string;
    message: string;
    timestamp: string;
    agent_id?: string;
    subtask?: string;
  }>;
}

interface CrewAIWorkflowProgressProps {
  workflowId: string;
  projectId: number;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
  onClose?: () => void;
}

const CrewAIWorkflowProgress: React.FC<CrewAIWorkflowProgressProps> = ({
  workflowId,
  projectId,
  onComplete,
  onError,
  onClose
}) => {
  const [workflow, setWorkflow] = useState<WorkflowStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [isCancelling, setIsCancelling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);

  // Agent icons and colors
  const agentConfig = {
    "Discovery Agent": { icon: Search, color: "green" },
    "Research Agent": { icon: Brain, color: "blue" },
    "Content Curator Agent": { icon: FileText, color: "purple" },
    "Editor Agent": { icon: Edit3, color: "orange" },
    "Media Agent": { icon: Image, color: "pink" },
    "PDF Builder Agent": { icon: Download, color: "indigo" }
  };

  // Initial workflow status fetch
  useEffect(() => {
    fetchWorkflowStatus();
  }, [workflowId]);

  // Set up WebSocket for real-time updates
  useEffect(() => {
    if (workflowId) {
      connectWebSocket();
    }

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [workflowId]);

  // Poll for updates every 2 seconds as fallback
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isConnected && workflow?.status === 'running') {
        fetchWorkflowStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isConnected, workflow?.status]);

  const fetchWorkflowStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/crewai/workflow-status/${workflowId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const status = await response.json();
      setWorkflow(status);

      // Handle workflow completion
      if (status.status === 'completed' && onComplete) {
        onComplete(status.result_data);
      } else if (status.status === 'failed' && onError) {
        onError(status.steps.find(s => s.status === 'failed')?.error_message || 'Workflow failed');
      }
    } catch (err) {
      console.error('Failed to fetch workflow status:', err);
      setError('Failed to fetch workflow status');
    }
  };

  const connectWebSocket = () => {
    try {
      const token = localStorage.getItem('access_token');
      const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/${workflowId}?token=${token}`;

      websocketRef.current = new WebSocket(wsUrl);

      websocketRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('WebSocket connected for workflow updates');
      };

      websocketRef.current.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data);
          if (update.workflow_id === workflowId) {
            setWorkflow(prev => {
              const current = prev || {
                workflow_id: workflowId,
                project_id: projectId,
                status: 'pending',
                current_step: 0,
                progress_percentage: 0,
                steps: [],
                start_time: new Date().toISOString(),
                notifications: [],
                agent_progress: {}
              };

              // Handle different message types
              switch (update.type) {
                case 'workflow_start':
                  return {
                    ...current,
                    status: 'running',
                    notifications: [...(current.notifications || []), {
                      type: 'info',
                      message: 'Workflow started successfully',
                      timestamp: update.timestamp,
                      details: `Estimated duration: ${update.estimated_duration_minutes} minutes`
                    }]
                  };

                case 'workflow_complete':
                  if (onComplete) onComplete(update.result_data);
                  return {
                    ...current,
                    status: 'completed',
                    progress_percentage: 100,
                    result_data: update.result_data,
                    notifications: [...(current.notifications || []), {
                      type: 'success',
                      message: 'Workflow completed successfully!',
                      timestamp: update.timestamp,
                      details: `Total duration: ${Math.round(update.total_duration)} seconds`
                    }]
                  };

                case 'workflow_error':
                  if (onError) onError(update.error_message);
                  return {
                    ...current,
                    status: 'failed',
                    notifications: [...(current.notifications || []), {
                      type: 'error',
                      message: 'Workflow failed',
                      timestamp: update.timestamp,
                      details: update.error_message
                    }]
                  };

                case 'workflow_cancelled':
                  return {
                    ...current,
                    status: 'cancelled',
                    notifications: [...(current.notifications || []), {
                      type: 'warning',
                      message: 'Workflow cancelled',
                      timestamp: update.timestamp,
                      details: update.reason || 'Cancelled by user'
                    }]
                  };

                case 'agent_start':
                  return {
                    ...current,
                    agent_progress: {
                      ...current.agent_progress,
                      [update.agent_id]: {
                        agent_name: update.agent_id,
                        current_step: 0,
                        total_steps: 100,
                        progress_percentage: 0,
                        completed_subtasks: 0,
                        total_subtasks: 0,
                        start_time: update.timestamp
                      }
                    },
                    notifications: [...(current.notifications || []), {
                      type: 'info',
                      message: `${update.agent_id} started`,
                      timestamp: update.timestamp,
                      agent_id: update.agent_id
                    }]
                  };

                case 'agent_progress':
                  return {
                    ...current,
                    progress_percentage: update.progress?.progress_percentage || current.progress_percentage,
                    agent_progress: {
                      ...current.agent_progress,
                      [update.agent_id]: update.progress
                    }
                  };

                case 'agent_complete':
                  return {
                    ...current,
                    notifications: [...(current.notifications || []), {
                      type: 'success',
                      message: `${update.agent_id} completed`,
                      timestamp: update.timestamp,
                      agent_id: update.agent_id,
                      details: update.result_summary
                    }]
                  };

                case 'agent_error':
                  return {
                    ...current,
                    notifications: [...(current.notifications || []), {
                      type: 'error',
                      message: `${update.agent_id} failed`,
                      timestamp: update.timestamp,
                      agent_id: update.agent_id,
                      details: update.error_message
                    }]
                  };

                case 'step_start':
                  return {
                    ...current,
                    notifications: [...(current.notifications || []), {
                      type: 'info',
                      message: `Started: ${update.subtask}`,
                      timestamp: update.timestamp,
                      agent_id: update.agent_id,
                      subtask: update.subtask
                    }]
                  };

                case 'step_complete':
                  return {
                    ...current,
                    notifications: [...(current.notifications || []), {
                      type: 'success',
                      message: `Completed: ${update.progress?.current_subtask || 'step'}`,
                      timestamp: update.timestamp,
                      agent_id: update.agent_id,
                      subtask: update.progress?.current_subtask
                    }]
                  };

                case 'system_notification':
                  return {
                    ...current,
                    notifications: [...(current.notifications || []), {
                      type: 'info',
                      message: update.message,
                      timestamp: update.timestamp
                    }]
                  };

                default:
                  // Legacy compatibility
                  return { ...current, ...update };
              }
            });
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      websocketRef.current.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
      };

      websocketRef.current.onerror = (error) => {
        setIsConnected(false);
        console.error('WebSocket error:', error);
        setError('WebSocket connection failed');
      };

    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to establish real-time connection');
    }
  };

  const cancelWorkflow = async () => {
    if (isCancelling) return;

    setIsCancelling(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/crewai/cancel-workflow/${workflowId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to cancel workflow: ${response.statusText}`);
      }

      if (onClose) onClose();
    } catch (err) {
      console.error('Failed to cancel workflow:', err);
      setError('Failed to cancel workflow');
    } finally {
      setIsCancelling(false);
    }
  };

  const toggleStepExpansion = (stepId: string) => {
    setExpandedSteps(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stepId)) {
        newSet.delete(stepId);
      } else {
        newSet.add(stepId);
      }
      return newSet;
    });
  };

  const getStepIcon = (step: WorkflowStep) => {
    const config = agentConfig[step.agent as keyof typeof agentConfig];
    if (!config) return Users;

    const Icon = config.icon;
    return Icon;
  };

  const getStepColor = (step: WorkflowStep) => {
    const config = agentConfig[step.agent as keyof typeof agentConfig];
    if (!config) return "gray";

    switch (step.status) {
      case 'completed': return config.color;
      case 'running': return config.color;
      case 'failed': return "red";
      default: return "gray";
    }
  };

  const formatDuration = (startTime: string, endTime?: string) => {
    if (!startTime) return "--";

    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000);

    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  if (!workflow) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl max-w-md w-full p-6">
          <div className="flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
          </div>
          <p className="text-center mt-4 text-gray-600">Loading workflow status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">CrewAI Workflow Progress</h3>
              <p className="text-sm text-gray-600">AI agents creating your journal</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Connection Status */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Real-time updates connected' : 'Using polling updates'}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Workflow ID: {workflowId}
            </div>
          </div>
        </div>

        {/* Overall Progress */}
        <div className="px-6 py-4 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Overall Progress</span>
            <span className="text-sm font-bold text-gray-900">{workflow.progress_percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${workflow.progress_percentage}%` }}
            />
          </div>
          <div className="mt-2 text-sm text-gray-600">
            Status: <span className="font-medium capitalize">{workflow.status}</span>
            {workflow.message && ` • ${workflow.message}`}
          </div>
        </div>

        {/* Enhanced Steps with Real-time Progress */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Steps Column */}
            <div className="lg:col-span-2 space-y-3">
              {workflow.steps.map((step, index) => {
                const isExpanded = expandedSteps.has(step.step_id);
                const Icon = getStepIcon(step);
                const color = getStepColor(step);

                // Get enhanced agent progress if available
                const agentProgress = workflow.agent_progress?.[step.agent.toLowerCase().replace(' ', '_')];

                return (
                  <div
                    key={step.step_id}
                    className={`border rounded-lg overflow-hidden ${
                      step.status === 'running' ? 'border-purple-300 bg-purple-50' :
                      step.status === 'completed' ? 'border-green-300 bg-green-50' :
                      step.status === 'failed' ? 'border-red-300 bg-red-50' :
                      'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div
                      className="p-4 cursor-pointer"
                      onClick={() => toggleStepExpansion(step.step_id)}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-${color}-100`}>
                            <Icon className={`w-5 h-5 text-${color}-600`} />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{step.step_name}</div>
                            <div className="text-sm text-gray-600">{step.agent}</div>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3">
                          <div className="text-right">
                            <div className="text-sm font-medium text-gray-900">
                              {agentProgress ? `${agentProgress.progress_percentage}%` : `${step.progress_percentage}%`}
                            </div>
                            {agentProgress?.current_subtask && (
                              <div className="text-xs text-purple-600 truncate max-w-32">
                                {agentProgress.current_subtask}
                              </div>
                            )}
                            {step.start_time && !agentProgress && (
                              <div className="text-xs text-gray-500">
                                {formatDuration(step.start_time, step.end_time)}
                              </div>
                            )}
                          </div>

                          {step.status === 'running' && <Loader2 className="w-4 h-4 animate-spin text-purple-600" />}
                          {step.status === 'completed' && <CheckCircle className="w-4 h-4 text-green-600" />}
                          {step.status === 'failed' && <AlertCircle className="w-4 h-4 text-red-600" />}
                          {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                        </div>
                      </div>

                      {/* Enhanced Progress Bar */}
                      <div className="space-y-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-500 ${
                              step.status === 'completed' ? 'bg-green-500' :
                              step.status === 'running' ? 'bg-purple-500' :
                              step.status === 'failed' ? 'bg-red-500' :
                              'bg-gray-300'
                            }`}
                            style={{ width: `${agentProgress?.progress_percentage || step.progress_percentage}%` }}
                          />
                        </div>

                        {/* Subtask Progress */}
                        {agentProgress && agentProgress.total_subtasks > 0 && (
                          <div className="flex items-center justify-between text-xs text-gray-600">
                            <span>Subtasks: {agentProgress.completed_subtasks}/{agentProgress.total_subtasks}</span>
                            <span>Step {agentProgress.current_step}/{agentProgress.total_steps}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className="px-4 pb-4 border-t border-gray-200">
                        <div className="pt-3 space-y-3">
                          {/* Enhanced Progress Details */}
                          {agentProgress && (
                            <div className="space-y-2">
                              <h4 className="text-sm font-medium text-gray-900">Agent Progress Details</h4>
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Current Step:</span>
                                  <span className="text-gray-900">{agentProgress.current_step}/{agentProgress.total_steps}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Subtasks:</span>
                                  <span className="text-gray-900">{agentProgress.completed_subtasks}/{agentProgress.total_subtasks}</span>
                                </div>
                              </div>
                            </div>
                          )}

                          {step.start_time && (
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-600">Started:</span>
                              <span className="text-gray-900">
                                {new Date(step.start_time).toLocaleString()}
                              </span>
                            </div>
                          )}

                          {step.end_time && (
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-600">Completed:</span>
                              <span className="text-gray-900">
                                {new Date(step.end_time).toLocaleString()}
                              </span>
                            </div>
                          )}

                          {step.error_message && (
                            <div className="text-sm">
                              <span className="text-gray-600">Error:</span>
                              <div className="mt-1 p-2 bg-red-50 border border-red-200 rounded text-red-700 text-xs">
                                {step.error_message}
                              </div>
                            </div>
                          )}

                          {step.result_data && (
                            <div className="text-sm">
                              <span className="text-gray-600">Result:</span>
                              <div className="mt-1 p-2 bg-gray-50 border border-gray-200 rounded text-gray-700 text-xs max-h-32 overflow-y-auto">
                                <pre className="whitespace-pre-wrap">
                                  {JSON.stringify(step.result_data, null, 2)}
                                </pre>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Notifications Panel */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-medium text-gray-900">Real-time Updates</h3>
                  <p className="text-sm text-gray-600">Latest notifications</p>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {workflow.notifications && workflow.notifications.length > 0 ? (
                    <div className="divide-y divide-gray-200">
                      {workflow.notifications.slice().reverse().map((notification, index) => (
                        <div key={index} className="p-3 hover:bg-gray-50">
                          <div className="flex items-start space-x-2">
                            <div className={`w-2 h-2 rounded-full mt-1.5 ${
                              notification.type === 'success' ? 'bg-green-500' :
                              notification.type === 'error' ? 'bg-red-500' :
                              notification.type === 'warning' ? 'bg-yellow-500' :
                              'bg-blue-500'
                            }`}></div>
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium text-gray-900">
                                {notification.message}
                              </div>
                              {notification.details && (
                                <div className="text-xs text-gray-600 mt-1">
                                  {notification.details}
                                </div>
                              )}
                              {notification.agent_id && (
                                <div className="text-xs text-purple-600 mt-1">
                                  Agent: {notification.agent_id}
                                </div>
                              )}
                              <div className="text-xs text-gray-500 mt-1">
                                {new Date(notification.timestamp).toLocaleTimeString()}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 text-center text-gray-500">
                      <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                        <Activity className="w-6 h-6 text-gray-400" />
                      </div>
                      <p className="text-sm">Waiting for updates...</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="px-6 py-4 bg-red-50 border-t border-red-200">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <div className="font-medium text-red-900">Connection Error</div>
                <div className="text-sm text-red-700 mt-1">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {workflow.status === 'completed' ? (
                <span className="text-green-600">✅ Workflow completed successfully!</span>
              ) : workflow.status === 'failed' ? (
                <span className="text-red-600">❌ Workflow failed</span>
              ) : workflow.status === 'cancelled' ? (
                <span className="text-orange-600">⏹️ Workflow cancelled</span>
              ) : (
                <span className="flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>In progress...</span>
                </span>
              )}
            </div>

            <div className="flex items-center space-x-3">
              {workflow.status === 'running' && (
                <button
                  onClick={cancelWorkflow}
                  disabled={isCancelling}
                  className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                    isCancelling
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-red-100 text-red-700 hover:bg-red-200'
                  }`}
                >
                  {isCancelling ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Cancelling...
                    </>
                  ) : (
                    <>
                      <Square className="w-4 h-4" />
                      Cancel Workflow
                    </>
                  )}
                </button>
              )}

              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {workflow.status === 'completed' ? 'Close' : 'Hide'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CrewAIWorkflowProgress;