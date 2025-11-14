import React, { useState, useEffect, useRef } from 'react';
import { X, CheckCircle2, Clock, Loader2, Bot, FileText, Sparkles } from 'lucide-react';
import { getJobWebSocketURL } from '@/lib/apiConfig';

interface AgentProgress {
  id: string;
  name: string;
  status: 'waiting' | 'active' | 'thinking' | 'completed';
  icon: React.ReactNode;
  progress: number;
  output?: string;
  startTime?: Date;
  completionTime?: Date;
}

interface CrewAIMessage {
  type: 'agent_start' | 'agent_thinking' | 'agent_output' | 'agent_complete' | 'completion';
  agent?: string;
  output?: string;
  message?: string;
  progress?: number;
}

interface AIWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  workflowId: string;
  jobData: any;
}

const AIWorkflowModal: React.FC<AIWorkflowModalProps> = ({
  isOpen,
  onClose,
  workflowId,
  jobData
}) => {
  const [agents, setAgents] = useState<AgentProgress[]>([
    {
      id: 'onboarding',
      name: 'Onboarding Agent',
      status: 'waiting',
      icon: <Bot className="w-5 h-5" />,
      progress: 0
    },
    {
      id: 'research',
      name: 'Research Agent',
      status: 'waiting',
      icon: <FileText className="w-5 h-5" />,
      progress: 0
    },
    {
      id: 'content',
      name: 'Content Curator',
      status: 'waiting',
      icon: <Sparkles className="w-5 h-5" />,
      progress: 0
    },
    {
      id: 'media',
      name: 'Media Generator',
      status: 'waiting',
      icon: <Bot className="w-5 h-5" />,
      progress: 0
    }
  ]);

  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket connection
  useEffect(() => {
    if (!isOpen || !workflowId) return;

    const wsUrl = getJobWebSocketURL(workflowId);
    console.log('Connecting to AI Workflow WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('AI Workflow WebSocket connected');
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      try {
        const data: CrewAIMessage = JSON.parse(event.data);
        console.log('Workflow message:', data);

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

          case 'completion':
            setIsCompleted(true);
            setOverallProgress(100);
            setAgents(prev => prev.map(agent => ({ ...agent, status: 'completed', progress: 100 })));
            break;
        }

        // Update overall progress based on active agents
        setAgents(prev => {
          const completedAgents = prev.filter(a => a.status === 'completed').length;
          const totalAgents = prev.length;
          const progress = Math.round((completedAgents / totalAgents) * 100);
          setOverallProgress(progress);
          return prev;
        });

      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [isOpen, workflowId]);

  // Timer
  useEffect(() => {
    if (isConnected && !isCompleted) {
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
  }, [isConnected, isCompleted]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: AgentProgress['status']) => {
    switch (status) {
      case 'waiting': return 'text-gray-400 border-gray-200';
      case 'active': return 'text-purple-600 border-purple-300 bg-purple-50';
      case 'thinking': return 'text-blue-600 border-blue-300 bg-blue-50';
      case 'completed': return 'text-green-600 border-green-300 bg-green-50';
      default: return 'text-gray-400 border-gray-200';
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-purple-50 to-blue-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-600" />
              AI Journal Creation
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {isCompleted ? 'Journal created successfully!' : 'Our AI agents are creating your journal...'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/80 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 bg-gray-50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Overall Progress</span>
            <span className="text-sm font-bold text-purple-600">{overallProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>Agents: {agents.filter(a => a.status === 'completed').length}/{agents.length}</span>
            <span>Time: {formatTime(elapsedTime)}</span>
          </div>
        </div>

        {/* Agent Cards */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid gap-4">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className={`border rounded-xl p-4 transition-all duration-300 ${getStatusColor(agent.status)}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${agent.status !== 'waiting' ? 'bg-white/50' : 'bg-gray-100'}`}>
                      {agent.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        {getStatusIcon(agent.status)}
                        <span className="capitalize">{agent.status}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-gray-900">{agent.progress}%</div>
                    {agent.startTime && (
                      <div className="text-xs text-gray-500">
                        {agent.completionTime
                          ? `Completed in ${formatTime(Math.floor((agent.completionTime.getTime() - agent.startTime.getTime()) / 1000))}`
                          : `${formatTime(Math.floor((new Date().getTime() - agent.startTime.getTime()) / 1000))}`
                        }
                      </div>
                    )}
                  </div>
                </div>

                {/* Agent Progress Bar */}
                <div className="w-full bg-gray-200/50 rounded-full h-1.5 mb-2">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      agent.status === 'completed' ? 'bg-green-500' :
                      agent.status === 'thinking' ? 'bg-blue-500 animate-pulse' :
                      agent.status === 'active' ? 'bg-purple-500' : 'bg-gray-300'
                    }`}
                    style={{ width: `${agent.progress}%` }}
                  />
                </div>

                {/* Agent Output */}
                {agent.output && (
                  <div className="mt-3 p-3 bg-white/50 rounded-lg text-sm text-gray-700">
                    {agent.output}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t bg-gray-50 flex justify-between items-center">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Close
          </button>
          {isCompleted && (
            <button
              onClick={() => {
                // Navigate to journal or library
                onClose();
                // Add navigation logic here
              }}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              View Journal
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIWorkflowModal;