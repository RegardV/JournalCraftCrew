import React, { useState, useEffect, useRef } from 'react';
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
  Activity
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

interface CrewAIProgressProps {
  jobId: string;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

const CrewAIProgressVisualization: React.FC<CrewAIProgressProps> = ({ jobId, onComplete, onError }) => {
  const [messages, setMessages] = useState<CrewAIMessage[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [showModal, setShowModal] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string>('');
  const [currentCrew, setCurrentCrew] = useState<string>('');
  const [currentSequence, setCurrentSequence] = useState<string>('');
  const [overallProgress, setOverallProgress] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const outputContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const agentConfig = {
    'Manager': { icon: Users, color: 'purple', gradient: 'from-purple-500 to-purple-600' },
    'Onboarding Agent': { icon: BookOpen, color: 'blue', gradient: 'from-blue-500 to-blue-600' },
    'Discovery Agent': { icon: Search, color: 'green', gradient: 'from-green-500 to-green-600' },
    'Research Agent': { icon: Brain, color: 'indigo', gradient: 'from-indigo-500 to-indigo-600' },
    'Content Curator': { icon: FileText, color: 'yellow', gradient: 'from-yellow-500 to-yellow-600' },
    'Editor': { icon: Edit3, color: 'pink', gradient: 'from-pink-500 to-pink-600' },
    'Media Agent': { icon: Code, color: 'teal', gradient: 'from-teal-500 to-teal-600' },
    'PDF Builder': { icon: Download, color: 'orange', gradient: 'from-orange-500 to-orange-600' }
  };

  useEffect(() => {
    if (!jobId) return;

    const wsUrl = `ws://localhost:6770/ws/journal/${jobId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected for CrewAI visualization:', jobId);
      setIsConnected(true);
      setMessages(prev => [...prev, {
        type: 'crew_info',
        timestamp: new Date(),
        crew: 'Journal Craft Crew',
        sequence: 'Initializing AI workflow...',
        message: 'CrewAI agents ready to start journal creation'
      }]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

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
            sequence: data.current_stage || data.agent,
            output: data.message || `${data.agent} is working...`,
            progress: data.progress_percentage || 0,
            status: data.status
          };

          if (data.agent) setCurrentAgent(data.agent);
        } else if (data.thinking) {
          // Agent thinking process
          newMessage = {
            type: 'agent_thinking',
            timestamp: new Date(),
            agent: currentAgent,
            crew: currentCrew,
            sequence: currentSequence,
            output: data.thinking
          };
        } else if (data.output) {
          // Agent output
          newMessage = {
            type: 'agent_output',
            timestamp: new Date(),
            agent: currentAgent,
            crew: currentCrew,
            sequence: currentSequence,
            output: data.output
          };
        } else if (data.sequence) {
          // Sequence update
          newMessage = {
            type: 'sequence_update',
            timestamp: new Date(),
            crew: currentCrew,
            sequence: data.sequence,
            message: data.message || `Starting: ${data.sequence}`
          };
          setCurrentSequence(data.sequence);
        } else if (data.status === 'completed') {
          // Overall completion
          newMessage = {
            type: 'completion',
            timestamp: new Date(),
            crew: currentCrew,
            sequence: 'Workflow Complete',
            message: 'Journal creation completed successfully!',
            progress: 100,
            status: 'completed'
          };

          if (onComplete) {
            setTimeout(() => {
              onComplete(data);
            }, 2000);
          }
        } else if (data.status === 'failed') {
          // Error handling
          newMessage = {
            type: 'error',
            timestamp: new Date(),
            agent: currentAgent,
            crew: currentCrew,
            sequence: currentSequence,
            message: data.error_message || 'An error occurred',
            status: 'failed'
          };

          if (onError) {
            onError(data.error_message || 'Unknown error occurred');
          }
        } else {
          // Generic progress update
          newMessage = {
            type: 'sequence_update',
            timestamp: new Date(),
            crew: 'Journal Craft Crew',
            sequence: data.current_stage || 'Processing...',
            message: data.message || 'Working on your journal...',
            progress: data.progress_percentage || 0
          };
        }

        setMessages(prev => [...prev, newMessage]);

        if (data.progress_percentage !== undefined) {
          setOverallProgress(data.progress_percentage);
        }

      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        setMessages(prev => [...prev, {
          type: 'error',
          timestamp: new Date(),
          crew: 'System',
          sequence: 'Error',
          message: 'Failed to process progress update'
        }]);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      setMessages(prev => [...prev, {
        type: 'error',
        timestamp: new Date(),
        crew: 'System',
        sequence: 'Connection Error',
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
  }, [jobId, currentAgent, currentCrew, currentSequence, onComplete, onError]);

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
      case 'crew_info': return <Users className="w-4 h-4 text-purple-500" />;
      case 'agent_start': return <Play className="w-4 h-4 text-green-500" />;
      case 'agent_thinking': return <Brain className="w-4 h-4 text-blue-500 animate-pulse" />;
      case 'agent_output': return <FileText className="w-4 h-4 text-indigo-500" />;
      case 'agent_complete': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'sequence_update': return <ChevronRight className="w-4 h-4 text-blue-500" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'completion': return <CheckCircle className="w-4 h-4 text-green-500" />;
      default: return <Terminal className="w-4 h-4 text-gray-500" />;
    }
  };

  const handleClose = () => {
    setShowModal(false);
  };

  if (!showModal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-6xl h-[85vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">CrewAI Journal Creation</h3>
              <p className="text-sm text-gray-600">Real-time AI workflow visualization</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${
              isConnected
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {isConnected ? 'Connected' : 'Connecting...'}
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Overall Progress</span>
            <span className="text-sm font-bold text-gray-900">{overallProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden flex min-h-0 max-h-full">
          {/* Crew & Sequence Panel */}
          <div className="w-80 border-r border-gray-200 bg-gray-50 p-4">
            <div className="space-y-4">
              {/* Current Crew */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                  <Users className="w-4 h-4 mr-2" />
                  Current Crew
                </h4>
                <div className="p-3 bg-white rounded-lg border border-gray-200">
                  <div className="font-medium text-gray-900">Journal Craft Crew</div>
                  <div className="text-sm text-gray-600">8 AI Agents Working</div>
                </div>
              </div>

              {/* Current Sequence */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                  <Terminal className="w-4 h-4 mr-2" />
                  Current Sequence
                </h4>
                <div className="p-3 bg-white rounded-lg border border-gray-200">
                  <div className="font-medium text-gray-900">{currentSequence || 'Initializing...'}</div>
                  {currentAgent && (
                    <div className="text-sm text-gray-600 mt-1">Agent: {currentAgent}</div>
                  )}
                </div>
              </div>

              {/* Agent Status */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                  <Activity className="w-4 h-4 mr-2" />
                  Agent Status
                </h4>
                <div className="space-y-2">
                  {Object.entries(agentConfig).map(([agent, config]) => (
                    <div
                      key={agent}
                      className={`p-2 rounded-lg border flex items-center space-x-2 ${
                        currentAgent === agent
                          ? 'border-purple-300 bg-purple-50'
                          : 'border-gray-200 bg-white'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-full bg-gradient-to-br ${config.gradient} flex items-center justify-center`}>
                        <config.icon className="w-3 h-3 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-medium text-gray-900 truncate">{agent}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Output Panel */}
          <div className="flex-1 flex flex-col min-h-0">
            <div className="p-4 border-b border-gray-200 bg-white flex-shrink-0">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-gray-700 flex items-center">
                  <FileDown className="w-4 h-4 mr-2" />
                  Live Output Stream
                </h4>
                <div className="text-xs text-gray-500">
                  {messages.length} messages
                </div>
              </div>
            </div>

            <div
              ref={outputContainerRef}
              className="flex-1 overflow-y-auto overflow-x-hidden p-4 bg-gray-900 font-mono text-sm min-h-0 max-h-full"
            >
              <div className="space-y-2 max-w-full">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-gray-800 border border-gray-700 hover:border-gray-600 transition-colors w-full max-w-full overflow-hidden"
                  >
                    <div className="mt-1 flex-shrink-0">
                      {getMessageIcon(message.type)}
                    </div>
                    <div className="flex-1 min-w-0 overflow-hidden">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(message.timestamp)}
                        </span>
                        {message.agent && (
                          <span className="px-2 py-1 bg-purple-900 text-purple-200 text-xs rounded-full">
                            {message.agent}
                          </span>
                        )}
                        {message.sequence && (
                          <span className="text-xs text-blue-400">
                            {message.sequence}
                          </span>
                        )}
                      </div>
                      <div className="text-gray-300 whitespace-pre-wrap break-all break-words overflow-wrap-anywhere max-w-full">
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
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Job ID: {jobId.slice(0, 8)}...
            </div>
            <div className="flex items-center space-x-2">
              {overallProgress === 100 ? (
                <button
                  onClick={handleClose}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>View Journal</span>
                </button>
              ) : (
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CrewAIProgressVisualization;