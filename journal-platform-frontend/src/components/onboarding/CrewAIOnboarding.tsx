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
  Users
} from 'lucide-react';

interface OnboardingMessage {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  agent?: string;
  isTyping?: boolean;
}

interface CrewAIOnboardingProps {
  preferences: {
    theme: string;
    title: string;
    titleStyle: string;
    authorStyle: string;
    researchDepth: string;
  };
  onOnboardingComplete: (crewaiInstructions: any) => void;
  onClose: () => void;
}

const CrewAIOnboarding: React.FC<CrewAIOnboardingProps> = ({
  preferences,
  onOnboardingComplete,
  onClose
}) => {
  const [messages, setMessages] = useState<OnboardingMessage[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>('Onboarding Agent');
  const [isProcessing, setIsProcessing] = useState(false);
  const [onboardingProgress, setOnboardingProgress] = useState(0);
  const [crewaiInstructions, setCrewaiInstructions] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const agentConfig = {
    'Onboarding Agent': {
      icon: Users,
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600',
      role: 'Analyzing and planning your journal creation'
    },
    'Discovery Agent': {
      icon: Search,
      color: 'green',
      gradient: 'from-green-500 to-green-600',
      role: 'Researching your chosen theme and style'
    },
    'Planning Agent': {
      icon: Brain,
      color: 'indigo',
      gradient: 'from-indigo-500 to-indigo-600',
      role: 'Creating the perfect journal structure'
    }
  };

  useEffect(() => {
    // Start the onboarding conversation
    startOnboarding();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startOnboarding = async () => {
    // Initial greeting from Onboarding Agent
    setTimeout(() => {
      addAgentMessage(
        'Onboarding Agent',
        `Hello! I'm your Onboarding Agent, and I'll help translate your preferences into a perfect plan for our AI Crew.\n\nLet me analyze what you're looking for:\n\n🎯 **Theme**: ${preferences.theme}\n📝 **Title Style**: ${preferences.titleStyle}\n✍️ **Author Voice**: ${preferences.authorStyle}\n🔍 **Research Depth**: ${preferences.researchDepth}\n\nGive me a moment to understand exactly what you want...`,
        true
      );
    }, 500);

    // Simulate analysis
    setTimeout(() => {
      addTypingMessage('Onboarding Agent');
    }, 2000);

    setTimeout(() => {
      addAgentMessage(
        'Onboarding Agent',
        `Perfect! I understand you want a **${preferences.theme}** journal with **${preferences.authorStyle}**'s writing style and **${preferences.titleStyle}** approach. Our **${preferences.researchDepth}** research will ensure it's comprehensive and tailored to your needs.\n\nLet me bring in our Discovery Agent to research this combination and create the perfect plan...`,
        true
      );
    }, 4000);

    // Start discovery phase
    setTimeout(() => {
      setCurrentAgent('Discovery Agent');
      addTypingMessage('Discovery Agent');
    }, 6000);

    setTimeout(() => {
      const discoveryResponse = generateDiscoveryResponse();
      addAgentMessage('Discovery Agent', discoveryResponse, true);
      setOnboardingProgress(33);
    }, 8000);

    // Planning phase
    setTimeout(() => {
      setCurrentAgent('Planning Agent');
      addTypingMessage('Planning Agent');
    }, 12000);

    setTimeout(() => {
      const planningResponse = generatePlanningResponse();
      addAgentMessage('Planning Agent', planningResponse, true);
      setOnboardingProgress(66);
    }, 14000);

    // Final instructions
    setTimeout(() => {
      setCurrentAgent('Onboarding Agent');
      addTypingMessage('Onboarding Agent');
    }, 18000);

    setTimeout(() => {
      const finalInstructions = generateFinalInstructions();
      addAgentMessage('Onboarding Agent', finalInstructions, true);
      setCrewaiInstructions(finalInstructions);
      setOnboardingProgress(100);
      setIsProcessing(false);
    }, 20000);
  };

  const generateDiscoveryResponse = () => {
    const themeInsights = {
      'Journaling for Anxiety': {
        research: 'cognitive behavioral therapy, mindfulness exercises, anxiety management techniques',
        focus: 'grounding techniques, breathing exercises, thought pattern awareness'
      },
      'Journaling for Productivity': {
        research: 'goal setting frameworks, time management studies, habit formation research',
        focus: 'daily prioritization, progress tracking, accountability systems'
      },
      'Journaling for Mindfulness': {
        research: 'meditation practices, present moment awareness, mindfulness-based stress reduction',
        focus: 'sensory awareness, emotional regulation, mindful daily activities'
      },
      'Journaling for Creativity': {
        research: 'creative thinking methods, brainstorming techniques, innovation psychology',
        focus: 'creative prompts, idea generation, overcoming creative blocks'
      }
    };

    const themeInfo = themeInsights[preferences.theme as keyof typeof themeInsights] || {
      research: 'evidence-based practices and proven methodologies',
      focus: 'personal growth and self-improvement'
    };

    return `🔍 **Discovery Complete!**\n\nI've researched the perfect combination of **${preferences.theme}** with **${preferences.authorStyle}**'s approach. Here's what I found:\n\n**Research Focus**: ${themeInfo.research}\n**Key Emphasis**: ${themeInfo.focus}\n\n**Style Match**: ${preferences.authorStyle}'s voice will blend perfectly with ${preferences.theme} - the tone will be ${getAuthorStyleDescription(preferences.authorStyle)} while addressing your mindfulness goals.\n\nThis combination will create a powerful, personalized journaling experience!`;
  };

  const generatePlanningResponse = () => {
    return `📋 **Perfect Plan Created!**\n\nBased on your preferences and my research, I've designed the ideal 30-day journal structure:\n\n**🗓️ Structure**: Progressive 30-day journey\n**📚 Daily Format**: ${preferences.titleStyle}\n**✍️ Writing Style**: ${preferences.authorStyle}\n**🔍 Content Type**: ${preferences.researchDepth} research-backed exercises\n\n**Daily Elements**:\n• Morning reflection prompts\n• Midday mindfulness exercises\n• Evening integration questions\n• Weekly progress reviews\n\n**Special Features**:\n• Personalized quotes from ${preferences.authorStyle}\n• Evidence-based exercises for ${preferences.theme}\n• Progressive difficulty curve\n• Trackable progress metrics\n\nOur AI Crew is ready to create this masterpiece!`;
  };

  const generateFinalInstructions = () => {
    return {
      crew_plan: {
        title: preferences.title || `${preferences.theme} - 30 Day Journey`,
        theme: preferences.theme,
        title_style: preferences.titleStyle,
        author_style: preferences.authorStyle,
        research_depth: preferences.researchDepth,
        structure: {
          duration: '30 days',
          daily_format: preferences.titleStyle,
          progression: 'gradual difficulty increase',
          research_integration: 'evidence-based practices'
        },
        content_focus: {
          primary: preferences.theme,
          methodology: preferences.authorStyle,
          exercises: generateExercisePlan(preferences.theme, preferences.authorStyle)
        },
        agent_workflow: {
          onboarding: 'Analyze user preferences and create structured plan',
          discovery: 'Research theme and author style combination',
          research: 'Gather evidence-based content and exercises',
          curation: 'Structure 30-day journal with progressive elements',
          editing: 'Refine content to match author voice perfectly',
          media: 'Create visual elements and formatting',
          pdf: 'Generate polished final journal'
        }
      },
      estimated_time: preferences.researchDepth === 'light' ? '5-10 minutes' :
                     preferences.researchDepth === 'medium' ? '15-20 minutes' : '30-45 minutes',
      confidence_score: 95
    };
  };

  const getAuthorStyleDescription = (style: string) => {
    const descriptions: Record<string, string> = {
      'James Clear': 'direct, actionable, and habit-focused',
      'Brené Brown': 'empathetic, research-driven, and vulnerability-focused',
      'Robin Sharma': 'inspirational, narrative, and wisdom-oriented',
      'Mel Robbins': 'direct, motivational, and action-oriented',
      'Tony Robbins': 'empowering, strategic, and transformational'
    };
    return descriptions[style] || 'personalized and engaging';
  };

  const generateExercisePlan = (theme: string, author: string) => {
    return `30 progressive exercises combining ${theme} principles with ${author}'s methodology, increasing in complexity and depth`;
  };

  const addAgentMessage = (agent: string, content: string, saveToHistory: boolean = true) => {
    const newMessage: OnboardingMessage = {
      id: Date.now().toString(),
      type: 'agent',
      content,
      timestamp: new Date(),
      agent,
      isTyping: false
    };

    if (saveToHistory) {
      setMessages(prev => [...prev, newMessage]);
    }
  };

  const addTypingMessage = (agent: string) => {
    const typingMessage: OnboardingMessage = {
      id: Date.now().toString(),
      type: 'agent',
      content: '',
      timestamp: new Date(),
      agent,
      isTyping: true
    };
    setMessages(prev => [...prev, typingMessage]);

    // Remove typing indicator after delay
    setTimeout(() => {
      setMessages(prev => prev.filter(msg => msg.id !== typingMessage.id));
    }, 2000);
  };

  const handleStartCreation = () => {
    if (crewaiInstructions) {
      onOnboardingComplete(crewaiInstructions);
    }
  };

  const getAgentIcon = (agentName: string) => {
    const config = agentConfig[agentName as keyof typeof agentConfig];
    const Icon = config?.icon || Bot;
    return <Icon className="w-5 h-5" />;
  };

  const getAgentColor = (agentName: string) => {
    const config = agentConfig[agentName as keyof typeof agentConfig];
    return config?.gradient || 'from-gray-500 to-gray-600';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">CrewAI Onboarding</h3>
              <p className="text-sm text-gray-600">AI agents understanding your vision</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Onboarding Progress</span>
            <span className="text-sm font-bold text-gray-900">{onboardingProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${onboardingProgress}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-2">
            {currentAgent} is {onboardingProgress < 100 ? 'working' : 'ready'}...
          </div>
        </div>

        {/* Current Agent Status */}
        <div className="px-6 py-4 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 bg-gradient-to-br ${getAgentColor(currentAgent)} rounded-lg flex items-center justify-center`}>
              {getAgentIcon(currentAgent)}
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">{currentAgent}</div>
              <div className="text-sm text-gray-600">
                {agentConfig[currentAgent as keyof typeof agentConfig]?.role}
              </div>
            </div>
            {onboardingProgress < 100 && (
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-purple-600" />
                <span className="text-sm text-purple-600">Processing...</span>
              </div>
            )}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.type === 'user'
                  ? 'bg-blue-500'
                  : `bg-gradient-to-br ${getAgentColor(message.agent || '')}`
              }`}>
                {message.type === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  getAgentIcon(message.agent || '')
                )}
              </div>

              <div className={`flex-1 max-w-3xl ${
                message.type === 'user' ? 'items-end' : 'items-start'
              }`}>
                {message.type === 'agent' && (
                  <div className="text-xs text-gray-500 mb-1">
                    {message.agent} • {message.timestamp.toLocaleTimeString()}
                  </div>
                )}

                {message.isTyping ? (
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                ) : (
                  <div className={`p-4 rounded-2xl ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>
                )}
              </div>
            </div>
          ))}

          <div ref={messagesEndRef} />
        </div>

        {/* User Preferences Summary */}
        <div className="p-6 bg-gray-50 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">Theme</div>
              <div className="font-medium text-gray-900">{preferences.theme}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">Title Style</div>
              <div className="font-medium text-gray-900">{preferences.titleStyle}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">Author Voice</div>
              <div className="font-medium text-gray-900">{preferences.authorStyle}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">Research</div>
              <div className="font-medium text-gray-900">{preferences.researchDepth}</div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {onboardingProgress === 100
                ? '✅ Onboarding complete! Ready to create your journal.'
                : `🤖 AI agents are creating your personalized plan...`
              }
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>

              {onboardingProgress === 100 ? (
                <button
                  onClick={handleStartCreation}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Start Journal Creation
                </button>
              ) : (
                <button
                  disabled
                  className="px-6 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed flex items-center space-x-2"
                >
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CrewAIOnboarding;