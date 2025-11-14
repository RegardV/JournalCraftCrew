import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate, useParams } from 'react-router-dom';
import { getJobWebSocketURL, getApiURL } from '@/lib/apiConfig';
import {
  X,
  CheckCircle2,
  Clock,
  Loader2,
  Bot,
  FileText,
  Sparkles,
  Brain,
  Wand2,
  Eye,
  ArrowLeft,
  Home,
  Download,
  Terminal,
  Zap,
  AlertCircle
} from 'lucide-react';

interface AgentProgress {
  id: string;
  name: string;
  role: string;
  status: 'waiting' | 'active' | 'thinking' | 'completed' | 'error';
  icon: React.ReactNode;
  progress: number;
  output?: string;
  startTime?: Date;
  completionTime?: Date;
  estimatedTime: number;
}

interface CrewAIMessage {
  type: 'agent_start' | 'agent_thinking' | 'agent_output' | 'agent_complete' | 'sequence_update' | 'error' | 'completion';
  agent?: string;
  output?: string;
  message?: string;
  progress?: number;
}

const EnhancedAIWorkflowPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { workflowId } = useParams<{ workflowId: string }>();
  const jobId = searchParams.get('jobId');
  const navigate = useNavigate();

  const actualWorkflowId = workflowId || jobId || 'default-workflow';

  const [agents, setAgents] = useState<AgentProgress[]>([
    {
      id: 'onboarding',
      name: 'Onboarding Agent',
      role: 'Personalization Specialist',
      status: 'waiting',
      icon: <Bot className="w-5 h-5" />,
      progress: 0,
      estimatedTime: 2
    },
    {
      id: 'research',
      name: 'Research Agent',
      role: 'Content Discovery Expert',
      status: 'waiting',
      icon: <Brain className="w-5 h-5" />,
      progress: 0,
      estimatedTime: 4
    },
    {
      id: 'content',
      name: 'Content Curator',
      role: 'Journal Structure Architect',
      status: 'waiting',
      icon: <FileText className="w-5 h-5" />,
      progress: 0,
      estimatedTime: 3
    },
    {
      id: 'media',
      name: 'Media Generator',
      role: 'Visual Enhancement Designer',
      status: 'waiting',
      icon: <Eye className="w-5 h-5" />,
      progress: 0,
      estimatedTime: 2
    },
    {
      id: 'quality',
      name: 'Quality Assurance',
      role: 'Final Review Specialist',
      status: 'waiting',
      icon: <Wand2 className="w-5 h-5" />,
      progress: 0,
      estimatedTime: 1
    }
  ]);

  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [totalEstimatedTime] = useState(12); // Total minutes estimated
  const [isError, setIsError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const intervalRef = useRef<number | null>(null);

  // Save completed journal to library
  const saveCompletedJournal = async (completionData: any) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No authentication token found');
        return;
      }

      // Extract journal content from completion data or agent outputs
      const journalContent = completionData.output ||
        agents.find(agent => agent.output)?.output ||
        'Journal created successfully by AI agents.';

      const journalData = {
        title: `AI Journal ${new Date().toLocaleDateString()}`,
        content: journalContent,
        theme: 'ai-generated',
        workflow_id: actualWorkflowId,
        completion_time: new Date().toISOString(),
        agents_completed: agents.filter(a => a.status === 'completed').length
      };

      const response = await fetch(`${getApiURL()}/api/journals/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(journalData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Journal saved successfully:', result);
        // Optionally update UI to show save success
      } else {
        console.error('Failed to save journal:', response.status);
      }
    } catch (error) {
      console.error('Error saving completed journal:', error);
    }
  };

  // WebSocket connection
  useEffect(() => {
    if (!actualWorkflowId) return;

    const wsUrl = getJobWebSocketURL(actualWorkflowId);
    console.log('Connecting to Enhanced AI Workflow WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Enhanced AI Workflow WebSocket connected');
      setIsConnected(true);
      setSocket(ws);
      setIsError(false);
      setErrorMessage('');
    };

    ws.onmessage = (event) => {
      try {
        const data: CrewAIMessage = JSON.parse(event.data);
        console.log('Enhanced Workflow message:', data);

        switch (data.type) {
          case 'agent_start':
            setAgents(prev => prev.map(agent =>
              agent.name === data.agent
                ? { ...agent, status: 'active', progress: 10, startTime: new Date() }
                : agent
            ));
            break;

          case 'agent_thinking':
            setAgents(prev => prev.map(agent =>
              agent.name === data.agent
                ? { ...agent, status: 'thinking', progress: 50 }
                : agent
            ));
            break;

          case 'agent_output':
            setAgents(prev => prev.map(agent =>
              agent.name === data.agent
                ? { ...agent, status: 'active', progress: 75, output: data.output }
                : agent
            ));
            break;

          case 'agent_complete':
            setAgents(prev => prev.map(agent =>
              agent.name === data.agent
                ? { ...agent, status: 'completed', progress: 100, completionTime: new Date() }
                : agent
            ));
            break;

          case 'sequence_update':
            setOverallProgress(data.progress || 0);
            break;

          case 'completion':
            setIsCompleted(true);
            setOverallProgress(100);
            setAgents(prev => prev.map(agent => ({ ...agent, status: 'completed', progress: 100 })));
            // Automatically save completed workflow to journal library
            saveCompletedJournal(data);
            break;

          case 'error':
            setIsError(true);
            setErrorMessage(data.message || 'An error occurred during workflow execution');
            break;
        }

        // Update overall progress based on completed agents
        setAgents(prev => {
          const completedAgents = prev.filter(a => a.status === 'completed').length;
          const totalAgents = prev.length;
          const progress = Math.round((completedAgents / totalAgents) * 100);
          setOverallProgress(progress);
          return prev;
        });

      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        setIsError(true);
        setErrorMessage('Failed to process workflow message');
      }
    };

    ws.onerror = (error) => {
      console.error('Enhanced AI Workflow WebSocket error:', error);
      setIsConnected(false);
      setIsError(true);
      setErrorMessage('Connection to workflow server failed');
    };

    ws.onclose = () => {
      console.log('Enhanced AI Workflow WebSocket disconnected');
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [actualWorkflowId]);

  // Timer
  useEffect(() => {
    if (isConnected && !isCompleted && !isError) {
      intervalRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isConnected, isCompleted, isError]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.ceil(seconds / 60);
    return `${mins}m`;
  };

  const getStatusColor = (status: AgentProgress['status']) => {
    switch (status) {
      case 'waiting': return 'text-gray-400 border-gray-200 bg-gray-50';
      case 'active': return 'text-purple-600 border-purple-300 bg-purple-50';
      case 'thinking': return 'text-blue-600 border-blue-300 bg-blue-50';
      case 'completed': return 'text-green-600 border-green-300 bg-green-50';
      default: return 'text-gray-400 border-gray-200 bg-gray-50';
    }
  };

  const getStatusIcon = (status: AgentProgress['status']) => {
    switch (status) {
      case 'waiting': return <Clock className="w-4 h-4" />;
      case 'active':
      case 'thinking': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'completed': return <CheckCircle2 className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getStatusText = (status: AgentProgress['status']) => {
    switch (status) {
      case 'waiting': return 'Queued';
      case 'active': return 'Processing';
      case 'thinking': return 'Analyzing';
      case 'completed': return 'Completed';
      default: return 'Unknown';
    }
  };

  const activeAgents = agents.filter(a => a.status === 'active' || a.status === 'thinking');
  const completedAgents = agents.filter(a => a.status === 'completed');

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                AI Journal Creation
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigate('/dashboard')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Home className="w-5 h-5 text-gray-600" />
              </button>
              <button
                onClick={() => navigate('/settings')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Terminal className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agent Progress Cards */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-gray-900">Agent Team Progress</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-600">
                    {activeAgents.length} active
                  </span>
                  <span className="text-sm font-medium text-green-600">
                    {completedAgents.length} completed
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {agents.map((agent, index) => (
                  <div
                    key={agent.id}
                    className={`border rounded-xl p-4 transition-all duration-300 ${getStatusColor(agent.status)}`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${
                          agent.status !== 'waiting' ? 'bg-white/50' : 'bg-gray-100'
                        }`}>
                          {agent.icon}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            {getStatusIcon(agent.status)}
                            <span className="capitalize">{getStatusText(agent.status)}</span>
                            <span className="text-xs text-gray-400">•</span>
                            <span className="text-xs text-gray-400">{agent.estimatedTime} min</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{agent.role}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-gray-900">{agent.progress}%</div>
                        {agent.startTime && (
                          <div className="text-xs text-gray-500">
                            {agent.completionTime
                              ? `Completed in ${formatDuration(
                                  Math.floor((agent.completionTime.getTime() - agent.startTime.getTime()) / 1000)
                                )}`
                              : `${formatDuration(
                                  Math.floor((new Date().getTime() - agent.startTime.getTime()) / 1000)
                                )} so far`
                            }
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Agent Progress Bar */}
                    <div className="w-full bg-gray-200/50 rounded-full h-2 mb-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          agent.status === 'completed' ? 'bg-green-500' :
                          agent.status === 'thinking' ? 'bg-blue-500 animate-pulse' :
                          agent.status === 'active' ? 'bg-purple-500' : 'bg-gray-300'
                        }`}
                        style={{ width: `${agent.progress}%` }}
                      />
                    </div>

                    {/* Agent Output */}
                    {agent.output && (
                      <div className="mt-3 p-3 bg-white/50 rounded-lg text-sm text-gray-700 border border-gray-200">
                        <div className="flex items-center gap-2 mb-2">
                          <Terminal className="w-3 h-3 text-gray-500" />
                          <span className="text-xs font-medium text-gray-600">Latest Output</span>
                        </div>
                        <p className="text-gray-700 leading-relaxed">{agent.output}</p>
                      </div>
                    )}

                    {/* Error State */}
                    {agent.status === 'error' && (
                      <div className="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
                        <div className="flex items-center gap-2 text-red-600 text-sm">
                          <AlertCircle className="w-4 h-4" />
                          <span>Agent encountered an error</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Active Process Display */}
            {activeAgents.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Current Process</h3>
                <div className="space-y-3">
                  {activeAgents.map(agent => (
                    <div key={agent.id} className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />
                      <div className="flex-1">
                        <div className="font-medium text-purple-900">{agent.name}</div>
                        <div className="text-sm text-purple-700">{agent.role}</div>
                      </div>
                      <Zap className="w-5 h-5 text-purple-600" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Progress Summary Sidebar */}
          <div className="space-y-6">
            {/* Overall Progress */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Overall Progress</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Completion</span>
                    <span className="text-lg font-bold text-purple-600">{overallProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${overallProgress}%` }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <div className="text-xs text-gray-500">Time Elapsed</div>
                    <div className="text-lg font-semibold text-gray-900">{formatTime(elapsedTime)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Est. Total</div>
                    <div className="text-lg font-semibold text-gray-900">{totalEstimatedTime}m</div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <span className="text-sm text-gray-600">Connection</span>
                  <span className={`text-sm font-medium ${
                    isConnected ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>

            {/* Status Card */}
            <div className={`bg-white rounded-2xl shadow-lg p-6 border-2 ${
              isError ? 'border-red-200' :
              isCompleted ? 'border-green-200' : 'border-gray-200'
            }`}>
              <div className="flex items-center space-x-3">
                {isError ? (
                  <div className="p-2 bg-red-100 rounded-lg">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                  </div>
                ) : isCompleted ? (
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle2 className="w-6 h-6 text-green-600" />
                  </div>
                ) : (
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Brain className="w-6 h-6 text-purple-600" />
                  </div>
                )}
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900">
                    {isError ? 'Workflow Error' : isCompleted ? 'Workflow Complete' : 'In Progress'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {isError ? errorMessage :
                     isCompleted ? 'Your journal has been successfully created!' :
                     'Your AI agents are creating your journal...'}
                  </p>
                </div>
              </div>

              {isCompleted && (
                <div className="mt-4 flex flex-col space-y-2">
                  <button
                    onClick={() => navigate('/dashboard?view=library')}
                    className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    View Library
                  </button>
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Back to Dashboard
                  </button>
                </div>
              )}
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Agents</span>
                  <span className="font-medium text-gray-900">{agents.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Completed</span>
                  <span className="font-medium text-green-600">{completedAgents.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">In Progress</span>
                  <span className="font-medium text-purple-600">{activeAgents.length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAIWorkflowPage;