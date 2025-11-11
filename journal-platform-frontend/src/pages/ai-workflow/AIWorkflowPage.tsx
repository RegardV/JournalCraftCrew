import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  X,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  FileText,
  Brain,
  Edit3,
  Download,
  Users,
  Code,
  Search,
  BookOpen,
  FileDown,
  ChevronDown,
  ChevronRight,
  Terminal,
  Sparkles,
  Play,
  Activity,
  ArrowLeft,
  Home,
  Settings
} from 'lucide-react';

interface CrewAIMessage {
  type: 'crew_info' | 'agent_start' | 'agent_thinking' | 'agent_output' | 'agent_complete' | 'sequence_update' | 'error' | 'completion';
  timestamp: Date;
  agent?: string;
  crew?: string;
  sequence?: string;
  output?: string;
  message?: string;
  progress?: number;
  status?: string;
}

const AIWorkflowPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const jobId = searchParams.get('jobId');
  const navigate = useNavigate();

  const [messages, setMessages] = useState<CrewAIMessage[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string>('');
  const [currentCrew, setCurrentCrew] = useState<string>('');
  const [currentSequence, setCurrentSequence] = useState<string>('');
  const [overallProgress, setOverallProgress] = useState(0);
  const [workflowStarted, setWorkflowStarted] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentStatuses, setAgentStatuses] = useState<Record<string, 'idle' | 'running' | 'completed' | 'error'>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const outputContainerRef = useRef<HTMLDivElement>(null);

  const agentConfig = {
    'Manager': {
      icon: Users,
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600',
      description: 'Coordinates the entire journal creation workflow',
      cliTag: '[MANAGER]',
      statusIcon: '👥',
      tasks: ['Orchestrating workflow', 'Managing task dependencies', 'Monitoring progress']
    },
    'Onboarding Agent': {
      icon: BookOpen,
      color: 'blue',
      gradient: 'from-blue-500 to-blue-600',
      description: 'Gathers user preferences and sets up the project',
      cliTag: '[ONBOARD]',
      statusIcon: '📚',
      tasks: ['Processing preferences', 'Setting up project structure', 'Initializing workflow parameters']
    },
    'Discovery Agent': {
      icon: Search,
      color: 'green',
      gradient: 'from-green-500 to-green-600',
      description: 'Researches topics and finds relevant content',
      cliTag: '[DISCOVER]',
      statusIcon: '🔍',
      tasks: ['Topic research', 'Content discovery', 'Source analysis']
    },
    'Research Agent': {
      icon: Brain,
      color: 'indigo',
      gradient: 'from-indigo-500 to-indigo-600',
      description: 'Deep analysis and content curation',
      cliTag: '[RESEARCH]',
      statusIcon: '🧠',
      tasks: ['Deep analysis', 'Content curation', 'Quality assessment']
    },
    'Content Curator': {
      icon: FileText,
      color: 'yellow',
      gradient: 'from-yellow-500 to-yellow-600',
      description: 'Organizes and structures the journal content',
      cliTag: '[CURATOR]',
      statusIcon: '📝',
      tasks: ['Content organization', 'Structure planning', 'Flow optimization']
    },
    'Editor': {
      icon: Edit3,
      color: 'pink',
      gradient: 'from-pink-500 to-pink-600',
      description: 'Refines and polishes the writing',
      cliTag: '[EDITOR]',
      statusIcon: '✏️',
      tasks: ['Text refinement', 'Style enhancement', 'Quality improvement']
    },
    'Media Agent': {
      icon: Code,
      color: 'teal',
      gradient: 'from-teal-500 to-teal-600',
      description: 'Handles images and media assets',
      cliTag: '[MEDIA]',
      statusIcon: '🎨',
      tasks: ['Image generation', 'Media optimization', 'Asset management']
    },
    'PDF Builder': {
      icon: Download,
      color: 'orange',
      gradient: 'from-orange-500 to-orange-600',
      description: 'Creates the final PDF output',
      cliTag: '[PDF]',
      statusIcon: '📄',
      tasks: ['PDF generation', 'Format optimization', 'Output validation']
    }
  };

  const workflowPhases = [
    { name: 'Initialization', icon: Settings, duration: '~30s', description: 'Setting up workspace and loading AI models', gradient: 'from-gray-500 to-gray-600' },
    { name: 'Onboarding', icon: BookOpen, duration: '~45s', description: 'Processing your preferences', gradient: 'from-blue-500 to-blue-600' },
    { name: 'Discovery', icon: Search, duration: '~90s', description: 'Researching topics and content', gradient: 'from-green-500 to-green-600' },
    { name: 'Content Curation', icon: FileText, duration: '~120s', description: 'Organizing and structuring content', gradient: 'from-yellow-500 to-yellow-600' },
    { name: 'Writing & Editing', icon: Edit3, duration: '~90s', description: 'Creating and refining journal entries', gradient: 'from-pink-500 to-pink-600' },
    { name: 'Media Generation', icon: Code, duration: '~60s', description: 'Creating images and assets', gradient: 'from-purple-500 to-purple-600' },
    { name: 'PDF Creation', icon: Download, duration: '~45s', description: 'Building final journal files', gradient: 'from-orange-500 to-orange-600' },
    { name: 'Finalization', icon: CheckCircle, duration: '~30s', description: 'Completing and organizing output', gradient: 'from-green-500 to-green-600' }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Helper functions for enhanced CLI formatting
  const formatCLIMessage = (message: string, agent?: string, type?: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const agentInfo = agent && getAgentInfo(agent);
    const cliTag = agentInfo?.cliTag || '[SYSTEM]';
    const statusIcon = agentInfo?.statusIcon || '⚙️';

    switch (type) {
      case 'agent_start':
        return `${timestamp} ${cliTag} ${statusIcon} Starting ${agent}...`;
      case 'agent_thinking':
        return `${timestamp} ${cliTag} 🤔 ${message}`;
      case 'agent_output':
        return `${timestamp} ${cliTag} ✨ ${message}`;
      case 'agent_complete':
        return `${timestamp} ${cliTag} ✅ ${agent} completed successfully`;
      case 'error':
        return `${timestamp} ${cliTag} ❌ ERROR: ${message}`;
      default:
        return `${timestamp} ${cliTag} ${statusIcon} ${message}`;
    }
  };

  const getAgentInfo = (agentName: string) => {
    return agentConfig[agentName as keyof typeof agentConfig];
  };

  const updateAgentStatus = (agent: string, status: 'idle' | 'running' | 'completed' | 'error') => {
    setAgentStatuses(prev => ({ ...prev, [agent]: status }));
  };

  const generateAgentActivityMessage = (agent: string, activity: string) => {
    const config = getAgentInfo(agent);
    if (!config) return activity;

    const tasks = config.tasks;
    const currentTask = tasks[Math.floor(Math.random() * tasks.length)];
    return `${config.cliTag} ${config.statusIcon} ${currentTask}...`;
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!jobId) {
      // Redirect to dashboard if no job ID provided
      navigate('/dashboard');
      return;
    }

    const wsUrl = `ws://localhost:6770/ws/journal/${jobId}`;
    console.log('Connecting to WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected for AI workflow:', jobId);
      setIsConnected(true);
      setWorkflowStarted(true);
      setMessages(prev => [...prev, {
        type: 'crew_info',
        timestamp: new Date(),
        crew: 'Journal Craft Crew',
        sequence: '🚀 Initializing AI workflow...',
        message: 'All CrewAI agents are preparing to start your journal creation',
        progress: 5
      }]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Sanitized logging - never log sensitive data like API keys
        console.log('WebSocket message type:', data.type, 'Status:', data.status, 'Agent:', data.agent);

        // Enhanced message handling for detailed CrewAI visualization
        let newMessage: CrewAIMessage;

        if (data.agent && data.status) {
          // Agent status update
          const agentInfo = agentConfig[data.agent as keyof typeof agentConfig];
          newMessage = {
            type: data.status === 'completed' ? 'agent_complete' : 'agent_start',
            timestamp: new Date(),
            agent: data.agent,
            crew: 'Journal Craft Crew',
            sequence: `🤖 ${data.agent} is ${data.status}...`,
            output: `🎯 ${data.message || `${data.agent} working on your journal...`}`,
            progress: data.progress_percentage || Math.min(overallProgress + 5, 95),
            status: data.status
          };

          if (data.agent) setCurrentAgent(data.agent);
          if (data.progress_percentage) setOverallProgress(data.progress_percentage);
        } else if (data.thinking) {
          // Agent thinking process
          newMessage = {
            type: 'agent_thinking',
            timestamp: new Date(),
            agent: currentAgent,
            crew: currentCrew,
            sequence: `🤔 ${currentAgent} is thinking...`,
            output: `💭 ${data.thinking}`,
            progress: Math.min(overallProgress + 2, 95)
          };
        } else if (data.output) {
          // Agent output
          newMessage = {
            type: 'agent_output',
            timestamp: new Date(),
            agent: currentAgent,
            crew: currentCrew,
            sequence: `✨ ${currentAgent} produced output`,
            output: `📝 ${data.output}`,
            progress: Math.min(overallProgress + 3, 95)
          };
        } else if (data.sequence || data.current_stage) {
          // Sequence update
          const stageName = data.sequence || data.current_stage;
          newMessage = {
            type: 'sequence_update',
            timestamp: new Date(),
            crew: '🎯 Journal Craft Crew',
            sequence: `🚀 ${stageName}`,
            message: data.message || `Now working on: ${stageName}`,
            progress: Math.min(overallProgress + 5, 95)
          };
          setCurrentSequence(stageName);

          // Update current agent based on sequence
          if (stageName.toLowerCase().includes('onboarding')) setCurrentAgent('Onboarding Agent');
          else if (stageName.toLowerCase().includes('research')) setCurrentAgent('Research Agent');
          else if (stageName.toLowerCase().includes('curator')) setCurrentAgent('Content Curator');
          else if (stageName.toLowerCase().includes('editor')) setCurrentAgent('Editor');
          else if (stageName.toLowerCase().includes('media')) setCurrentAgent('Media Agent');
          else if (stageName.toLowerCase().includes('pdf')) setCurrentAgent('PDF Builder');
          else if (stageName.toLowerCase().includes('writing')) setCurrentAgent('Editor');
        } else if (data.status === 'completed') {
          // Overall completion
          newMessage = {
            type: 'completion',
            timestamp: new Date(),
            crew: '🎉 Journal Craft Crew',
            sequence: '✅ Workflow Complete!',
            message: 'Your personalized journal has been created successfully!',
            progress: 100,
            status: 'completed'
          };

          setIsComplete(true);
          setOverallProgress(100);
        } else if (data.status === 'failed') {
          // Error handling
          newMessage = {
            type: 'error',
            timestamp: new Date(),
            agent: currentAgent,
            crew: '❌ System',
            sequence: '❌ Error Occurred',
            message: data.error_message || 'An error occurred during journal creation',
            status: 'failed'
          };

          setError(data.error_message || 'Unknown error occurred');
          setIsComplete(true);
        } else {
          // Generic progress update
          newMessage = {
            type: 'sequence_update',
            timestamp: new Date(),
            crew: '🎯 Journal Craft Crew',
            sequence: data.current_stage || '⚡ Processing...',
            message: data.message || 'Working on your journal...',
            progress: data.progress_percentage || Math.min(overallProgress + 2, 95)
          };

          if (data.progress_percentage) {
            setOverallProgress(data.progress_percentage);
          }
        }

        setMessages(prev => [...prev, newMessage]);

      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        setMessages(prev => [...prev, {
          type: 'error',
          timestamp: new Date(),
          crew: '❌ System',
          sequence: '❌ Error',
          message: 'Failed to process progress update',
          progress: overallProgress
        }]);
        setError('Failed to process progress update');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      setError('Connection to AI workflow lost');
      setMessages(prev => [...prev, {
        type: 'error',
        timestamp: new Date(),
        crew: '❌ System',
        sequence: '❌ Connection Error',
        message: 'Failed to connect to progress tracking'
      }]);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected for job:', jobId);
      setIsConnected(false);
    };

    setSocket(ws);

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [jobId, currentAgent, currentCrew, currentSequence, overallProgress]);

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'crew_info': return <Users className="w-5 h-5 text-purple-500" />;
      case 'agent_start': return <Play className="w-5 h-5 text-green-500" />;
      case 'agent_thinking': return <Brain className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'agent_output': return <FileText className="w-5 h-5 text-indigo-500" />;
      case 'agent_complete': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'sequence_update': return <ChevronRight className="w-5 h-5 text-blue-500" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'completion': return <CheckCircle className="w-5 h-5 text-green-500" />;
      default: return <Terminal className="w-5 h-5 text-gray-500" />;
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const getEstimatedTimeRemaining = () => {
    const totalPhases = workflowPhases.length;
    const currentPhaseIndex = Math.floor((overallProgress / 100) * totalPhases);
    const remainingPhases = totalPhases - currentPhaseIndex - 1;
    const estimatedTime = remainingPhases * 60; // 60 seconds per phase average

    if (estimatedTime < 60) return `${estimatedTime}s`;
    return `${Math.ceil(estimatedTime / 60)}m ${estimatedTime % 60}s`;
  };

  const getCurrentPhase = () => {
    const phaseIndex = Math.floor((overallProgress / 100) * workflowPhases.length);
    return workflowPhases[phaseIndex] || workflowPhases[0];
  };

  if (!jobId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🤖</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">No Job ID Found</h1>
          <p className="text-gray-600 mb-4">Please start a journal creation process first.</p>
          <button
            onClick={handleBackToDashboard}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBackToDashboard}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                title="Back to Dashboard"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">AI Journal Creation Workflow</h1>
                  <p className="text-sm text-gray-400">Real-time CrewAI agent visualization</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center space-x-2 ${
                isConnected
                  ? 'bg-green-900 text-green-300 border border-green-700'
                  : 'bg-yellow-900 text-yellow-300 border border-yellow-700'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'
                }`} />
                <span>{isConnected ? 'Connected' : 'Connecting...'}</span>
              </div>

              <div className="text-sm text-gray-400">
                Job ID: {jobId.slice(0, 8)}...
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Overall Progress */}
            <div className="bg-gray-700 rounded-xl p-6 border border-gray-600">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Overall Progress</h3>
                <span className="text-2xl font-bold text-white">{overallProgress}%</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-purple-500 to-pink-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${overallProgress}%` }}
                />
              </div>
              <div className="mt-3 flex items-center justify-between text-sm">
                <span className="text-gray-400">Est. Time: {getEstimatedTimeRemaining()}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  isComplete
                    ? 'bg-green-900 text-green-300'
                    : 'bg-yellow-900 text-yellow-300'
                }`}>
                  {isComplete ? 'Completed' : 'In Progress'}
                </span>
              </div>
            </div>

            {/* Current Phase */}
            <div className="bg-gray-700 rounded-xl p-6 border border-gray-600">
              <div className="flex items-center space-x-3 mb-4">
                {(() => {
                  const currentPhase = getCurrentPhase();
                  const IconComponent = currentPhase.icon;
                  return (
                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${currentPhase.gradient} flex items-center justify-center`}>
                      <IconComponent className="w-4 h-4 text-white" />
                    </div>
                  );
                })()}
                <div>
                  <h3 className="text-lg font-semibold text-white">Current Phase</h3>
                  <p className="text-sm text-gray-400">{getCurrentPhase().name}</p>
                </div>
              </div>
              <div className="text-sm text-gray-300 mb-2">
                {getCurrentPhase().description}
              </div>
              <div className="text-xs text-gray-500">
                Duration: {getCurrentPhase().duration}
              </div>
            </div>

            {/* Workflow Phases */}
            <div className="bg-gray-700 rounded-xl p-6 border border-gray-600">
              <h3 className="text-lg font-semibold text-white mb-4">Workflow Phases</h3>
              <div className="space-y-2">
                {workflowPhases.map((phase, index) => {
                  const isCompleted = (index + 1) / workflowPhases.length * 100 <= overallProgress;
                  const isCurrent = index === Math.floor(overallProgress / 100 * workflowPhases.length);

                  return (
                    <div
                      key={phase.name}
                      className={`flex items-center space-x-3 p-2 rounded-lg border ${
                        isCompleted
                          ? 'bg-green-900 border-green-700'
                          : isCurrent
                            ? 'bg-purple-900 border-purple-700'
                            : 'bg-gray-800 border-gray-600'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-lg flex items-center justify-center ${
                        isCompleted
                          ? 'bg-green-500'
                          : isCurrent
                            ? 'bg-purple-500 animate-pulse'
                            : 'bg-gray-500'
                      }`}>
                        <phase.icon className="w-3 h-3 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-white">{phase.name}</div>
                        <div className="text-xs text-gray-400">{phase.duration}</div>
                      </div>
                      {isCompleted && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-white">{messages.length}</div>
              <div className="text-xs text-gray-400">Messages</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-white">{Object.keys(agentConfig).length}</div>
              <div className="text-xs text-gray-400">Agents</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-white">{workflowPhases.length}</div>
              <div className="text-xs text-gray-400">Phases</div>
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-white">{Math.floor(overallProgress / 25) + 1}</div>
              <div className="text-xs text-gray-400">Current Step</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex min-h-0">
        {/* Agent Status Panel */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 p-6 overflow-y-auto">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-purple-400" />
            Agent Status
          </h3>

          <div className="space-y-4">
            {Object.entries(agentConfig).map(([agent, config]) => (
              <div
                key={agent}
                className={`p-4 rounded-xl border ${
                  currentAgent === agent
                    ? 'border-purple-400 bg-purple-900'
                    : 'border-gray-600 bg-gray-700'
                } transition-all duration-200 hover:border-gray-500`}
              >
                <div className="flex items-start space-x-3">
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${config.gradient} flex items-center justify-center flex-shrink-0`}>
                    <config.icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white">{agent}</div>
                    <div className="text-sm text-gray-400 mt-1">{config.description}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CLI Output Panel */}
        <div className="flex-1 bg-gray-900 p-6 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <Terminal className="w-5 h-5 mr-2 text-green-400" />
              Live CLI Output
            </h3>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-400">
                {messages.length} messages
              </div>
              <div className="text-xs text-gray-500">
                Auto-scroll: ON
              </div>
            </div>
          </div>

          <div
            ref={outputContainerRef}
            className="flex-1 overflow-y-auto font-mono text-sm space-y-1"
            style={{
              fontFamily: '"Courier New", "Monaco", "Menlo", monospace'
            }}
          >
            <div className="space-y-1">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-start space-x-3 p-3 rounded-lg ${
                    message.type === 'error'
                      ? 'bg-red-900 border border-red-700'
                      : message.type === 'completion'
                      ? 'bg-green-900 border border-green-700'
                      : 'bg-gray-800 border border-gray-700'
                  } transition-all duration-200 hover:border-gray-500`}
                >
                  <div className="mt-1 flex-shrink-0">
                    {getMessageIcon(message.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-xs text-gray-500">
                        [{formatTimestamp(message.timestamp)}]
                      </span>
                      {message.agent && (
                        <span className="px-2 py-1 bg-purple-800 text-purple-200 text-xs rounded-full">
                          {message.agent}
                        </span>
                      )}
                    </div>
                    <div className="text-gray-300 whitespace-pre-wrap break-words">
                      {message.output || message.message}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">
            Job ID: {jobId.slice(0, 8)}... | Messages: {messages.length} | Agents: {Object.keys(agentConfig).length}
          </div>
          <div className="flex items-center space-x-4">
            {isComplete && (
              <button
                onClick={handleBackToDashboard}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
              >
                <Home className="w-4 h-4" />
                <span>Back to Library</span>
              </button>
            )}
            {!isComplete && (
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Creating your journal...</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIWorkflowPage;