import React, { useState, useEffect, useRef, useCallback } from 'react';
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
import AIWorkflowModal from '@/components/journal/AIWorkflowModal';
import { getWritingStylesForTheme } from './WritingStyles';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<any>;
}

interface AuthorStyle {
  name: string;
  style: string;
  examples: string[];
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
  initialPreferences?: any;
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
  onClose,
  initialPreferences
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [preferences, setPreferences] = useState({
    theme: '',
    title: '',
    title_style: '',
    author_style: '',
    research_depth: '',
    workflow_type: 'standard', // Default to standard workflow
    ...initialPreferences // Merge with initial preferences if provided
  });
  const [availableOptions, setAvailableOptions] = useState({
    titleStyles: [],
    researchDepths: [],
    authorStyles: []
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});
  const [generatingAuthorStyles, setGeneratingAuthorStyles] = useState(false);
  const [authorStyleOptions, setAuthorStyleOptions] = useState<AuthorStyle[]>([]);
  const [showAIWorkflow, setShowAIWorkflow] = useState(false);
  const [workflowJobId, setWorkflowJobId] = useState<string>('');

  // Refs for input fields to maintain focus
  const themeInputRef = useRef<HTMLInputElement>(null);
  const titleInputRef = useRef<HTMLInputElement>(null);

  // Stable change handlers that maintain focus
  const handleThemeChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPreferences(prev => ({ ...prev, theme: value }));
    // Keep focus on the input
    setTimeout(() => {
      if (themeInputRef.current) {
        themeInputRef.current.focus();
      }
    }, 0);
  }, []);

  const handleTitleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPreferences(prev => ({ ...prev, title: value }));
    // Keep focus on the input
    setTimeout(() => {
      if (titleInputRef.current) {
        titleInputRef.current.focus();
      }
    }, 0);
  }, []);

  // AI-powered author style generation function
  const generateAuthorStyles = async () => {
    if (!preferences.theme) return;

    setGeneratingAuthorStyles(true);
    setAuthorStyleOptions([]);

    try {
      // Simulate AI call with theme-based style generation
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Generate styles based on theme
      const themeBasedStyles = getWritingStylesForTheme(preferences.theme);
      setAuthorStyleOptions(themeBasedStyles);
    } catch (error) {
      console.error('Failed to generate author styles:', error);
      setErrors(prev => ({
        ...prev,
        author_style: 'Failed to generate writing styles. Please try again.'
      }));
    } finally {
      setGeneratingAuthorStyles(false);
    }
  };

  // Helper function to generate writing style classifications based on theme (returns 5 style types with examples)
  const getAuthorStylesForTheme = (theme: string): AuthorStyle[] => {
    const styleMap: Record<string, AuthorStyle[]> = {
      'mindfulness': [
        {
          name: 'Zen Contemplative Style',
          style: 'Gentle presence with mindful awareness and compassionate observation',
          examples: ['Breathing in, I calm my body and mind...', 'Return to your true home in the present moment...', 'Walk as if you are kissing the Earth with each step...']
        },
        {
          name: 'Jon Kabat-Zinn (2021)',
          style: 'Scientific mindfulness with focus on present moment awareness and non-judgmental observation',
          examples: ['Notice what\'s arising in this moment...', 'Bring curiosity to your experience...', 'There is more right with you than wrong...']
        },
        {
          name: 'Tara Brach (2022)',
          style: 'Buddhist psychology with radical compassion and acceptance of imperfection',
          examples: ['Allow this moment to be exactly as it is...', 'Recognize the belonging that\'s here...', 'Trust in your basic goodness...']
        },
        {
          name: 'Pema Chödrön (2020)',
          style: 'Tibetan Buddhist wisdom with gentle encouragement to stay with difficult emotions',
          examples: ['Stay with the discomfort...', 'Lean into the sharp points...', 'This very moment is the perfect teacher...']
        },
        {
          name: 'Jack Kornfield (2023)',
          style: 'Heart-centered Buddhist psychology with stories and practical wisdom',
          examples: ['The heart knows the way...', 'Your troubles are blessings in disguise...', 'Compassion is our true nature...']
        }
      ],
      'productivity': [
        {
          name: 'James Clear (2023)',
          style: 'Atomic habits approach with focus on small improvements and systems thinking',
          examples: ['What 1% improvement can you make today?', 'Build systems, not just goals...', 'Your habits shape your identity...']
        },
        {
          name: 'Cal Newport (2022)',
          style: 'Deep work philosophy with emphasis on focused concentration and digital minimalism',
          examples: ['What deep work will you accomplish?', 'Eliminate shallow work...', 'Focus is the new IQ...']
        },
        {
          name: 'Tim Ferriss (2021)',
          style: 'Biohacking and efficiency with emphasis on lifestyle optimization and rapid learning',
          examples: ['What\'s the 80/20 of this task?', 'Test assumptions and measure results...', 'Less is more...']
        },
        {
          name: 'Stephen Covey (2020)',
          style: 'Principle-centered leadership with focus on effectiveness and time management',
          examples: ['Begin with the end in mind...', 'What are your highest priorities?', 'Sharpen the saw...']
        },
        {
          name: 'David Allen (2022)',
          style: 'Getting Things Done methodology with focus on externalizing commitments',
          examples: ['What\'s your next action?', 'Capture everything in trusted system...', 'Your mind is for having ideas, not holding them...']
        }
      ],
      'creativity': [
        {
          name: 'Elizabeth Gilbert (2023)',
          style: 'Big Magic creativity with fearless curiosity and relationship with inspiration',
          examples: ['What does your creative genius want?', 'Make things for the delight of making them...', 'Your creativity is a gift...']
        },
        {
          name: 'Austin Kleon (2022)',
          style: 'Steal like an artist approach with emphasis on remixing and sharing work',
          examples: ['What can you remix today?', 'Share your process...', 'Creativity is subtraction...']
        },
        {
          name: 'Twyla Tharp (2021)',
          style: 'Creative habits and ritual with focus on discipline and artistic practice',
          examples: ['What\'s your creative muscle?', 'Show up and do the work...', 'Creativity is a habit...']
        },
        {
          name: 'Rick Rubin (2023)',
          style: 'Mystical and minimal approach with focus on removing obstacles to creativity',
          examples: ['What can you remove to reveal the essence?', 'The song already exists...', 'Become a conduit...']
        },
        {
          name: 'Julia Cameron (2020)',
          style: 'The Artist\'s Way method with focus on morning pages and creative recovery',
          examples: ['What does your inner artist need today?', 'Take yourself on an artist date...', 'Creativity is a spiritual path...']
        }
      ],
      'gratitude': [
        {
          name: 'Brené Brown (2023)',
          style: 'Research-based gratitude with vulnerability and wholehearted living',
          examples: ['What are you grateful for right now?', 'Practice gratitude even when it\'s hard...', 'Gratitude makes sense of our past...']
        },
        {
          name: 'Oprah Winfrey (2022)',
          style: 'Inspirational gratitude with storytelling and personal transformation',
          examples: ['What\'s your gratitude list today?', 'Turn your wounds into wisdom...', 'Thank you is the best prayer...']
        },
        {
          name: 'Louie Schwartzberg (2021)',
          style: 'Photographic gratitude with focus on beauty and mindfulness of nature',
          examples: ['Notice the beauty in this moment...', 'Gratitude unlocks the fullness of life...', 'Open your eyes to wonder...']
        },
        {
          name: 'Deepak Chopra (2020)',
          style: 'Spiritual gratitude with consciousness and awareness of abundance',
          examples: ['What abundance surrounds you?', 'Gratitude opens the heart...', 'Be present in the miracle of life...']
        },
        {
          name: 'Kristin Neff (2023)',
          style: 'Self-compassion with gratitude and mindful acceptance of imperfection',
          examples: ['How can you be kind to yourself today?', 'Embrace your humanity...', 'Self-compassion is a form of gratitude...']
        }
      ],
      'fitness': [
        {
          name: 'Ben Bergeron (2023)',
          style: 'CrossFit mindset with discipline, accountability, and embracing discomfort',
          examples: ['What will make you 1% better today?', 'Fall in love with the process...', 'If you want what most people don\'t have...']
        },
        {
          name: 'Dr. Andrew Huberman (2022)',
          style: 'Neuroscience-based fitness with focus on protocols and biological optimization',
          examples: ['How can you optimize your biology today?', 'Use morning sunlight...', 'Leverage your nervous system...']
        },
        {
          name: 'Rich Roll (2021)',
          style: 'Plant-powered endurance with holistic wellness and mental resilience',
          examples: ['What limits can you push past today?', 'Fuel your greatness...', 'The journey begins with a single step...']
        },
        {
          name: 'Kayla Itsines (2023)',
          style: 'Empowering fitness with body confidence and consistent progress',
          examples: ['What makes you feel strong today?', 'Your body can do amazing things...', 'Progress over perfection...']
        },
        {
          name: 'Tony Horton (2020)',
          style: 'Beach body motivation with variety and bringing your best self',
          examples: ['Do your best and forget the rest...', 'How can you push play today?', 'Variety keeps things interesting...']
        }
      ],
      'learning': [
        {
          name: 'Barbara Oakley (2023)',
          style: 'Learning how to learn with focused and diffuse thinking modes',
          examples: ['What can you learn in focused mode?', 'Take regular breaks for diffuse thinking...', 'Chunk your learning...']
        },
        {
          name: 'Josh Kaufman (2022)',
          style: 'Rapid skill acquisition with 20 hours to learn anything',
          examples: ['What skill can you learn this month?', 'Deconstruct the skill...', 'Learn just enough to self-correct...']
        },
        {
          name: 'Carol Dweck (2021)',
          style: 'Growth mindset with focus on learning from challenges',
          examples: ['What challenges help you grow?', 'Embrace the word "yet"...', 'Your brain can form new connections...']
        },
        {
          name: 'Tim Ferriss (2020)',
          style: 'Meta-learning with deconstruction and 80/20 application',
          examples: ['What\'s the minimum effective dose?', 'Learn by doing...', 'Reduce learning friction...']
        },
        {
          name: 'Cal Newport (2023)',
          style: 'Deep learning with focused attention and deliberate practice',
          examples: ['What can you master today?', 'Practice with intention...', 'Learning requires active engagement...']
        }
      ],
      'relationships': [
        {
          name: 'Dr. John Gottman (2023)',
          style: 'Research-based relationships with emotional connection and bidirectional influence',
          examples: ['What small gesture can strengthen your bond today?', 'Turn toward each other...', 'Love is a verb...']
        },
        {
          name: 'Brené Brown (2022)',
          style: 'Vulnerability and courage with authentic connection',
          examples: ['How can you show up vulnerably today?', 'Choose courage over comfort...', 'Connection is why we\'re here...']
        },
        {
          name: 'Esther Perel (2021)',
          style: 'Psychological perspective on desire, identity, and relational dynamics',
          examples: ['What nourishes your connection?', 'Balance autonomy and togetherness...', 'Maintain curiosity about each other...']
        },
        {
          name: 'Gary Chapman (2020)',
          style: 'Five Love Languages with understanding and speaking partner\'s emotional language',
          examples: ['How can you show love in your partner\'s language today?', 'Fill each other\'s love tank...', 'People give and receive love differently...']
        },
        {
          name: 'Harville Hendrix (2023)',
          style: 'Imago relationship therapy with conscious partnership and healing',
          examples: ['How can you be more present with your partner?', 'Stretch for the other\'s growth...', 'Your relationship is your spiritual practice...']
        }
      ],
      'finance': [
        {
          name: 'Robert Kiyosaki (2023)',
          style: 'Financial education with asset-building and entrepreneurial mindset',
          examples: ['How can you build assets today?', 'Mind your own business...', 'Play the cash flow game...']
        },
        {
          name: 'Dave Ramsey (2022)',
          style: 'Debt-free living with budgeting and wealth building principles',
          examples: ['What debt can you eliminate today?', 'Live on less than you make...', 'Build wealth the old-fashioned way...']
        },
        {
          name: 'Tony Robbins (2021)',
          style: 'Financial freedom with psychology of wealth and strategic investing',
          examples: ['What wealth blueprint are you following?', 'Model success...', 'Change your state to change your finances...']
        },
        {
          name: 'Vicki Robin (2020)',
          style: 'Financial independence with purpose and life energy alignment',
          examples: ['Does this purchase align with your values?', 'Calculate your true hourly wage...', 'Life energy is your primary resource...']
        },
        {
          name: 'Morgan Housel (2023)',
          style: 'Psychological finance with understanding behavior vs. intelligence',
          examples: ['What financial story are you telling yourself?', 'Optimize for happiness, not just returns...', 'Your time horizon determines your results...']
        }
      ]
    };

    // Default styles if theme not found
    const defaultStyles: AuthorStyle[] = [
      {
        name: 'James Clear (2023)',
        style: 'Atomic habits approach with focus on small improvements and systems thinking',
        examples: ['What 1% improvement can you make today?', 'Build systems, not just goals...', 'Your habits shape your identity...']
      },
      {
        name: 'Brené Brown (2022)',
        style: 'Research-based vulnerability with courage and wholehearted living',
        examples: ['What does courage look like today?', 'Embrace imperfection...', 'Vulnerability is courage...']
      },
      {
        name: 'Elizabeth Gilbert (2021)',
        style: 'Creative magic with fearless curiosity and relationship with inspiration',
        examples: ['What does your creative genius want?', 'Make things for the delight of making them...', 'Your creativity is a gift...']
      },
      {
        name: 'Thich Nhat Hanh (2020)',
        style: 'Zen master mindfulness with gentle presence and compassionate awareness',
        examples: ['Breathing in, I calm my body...', 'Return to your true home...', 'Walk as if you are kissing the Earth...']
      },
      {
        name: 'Dr. Andrew Huberman (2023)',
        style: 'Neuroscience-based optimization with focus on protocols and biological performance',
        examples: ['How can you optimize your biology today?', 'Use morning sunlight...', 'Leverage your nervous system...']
      }
    ];

    return styleMap[theme] || defaultStyles;
  };

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

  // Theme Step Component (Enhanced with suggestions and agent preview)
  const ThemeStep = () => {
    const popularThemes = [
      { name: 'mindfulness', description: 'Cultivate awareness and inner peace' },
      { name: 'productivity', description: 'Achieve goals and stay focused' },
      { name: 'creativity', description: 'Unlock artistic potential' },
      { name: 'gratitude', description: 'Practice daily thankfulness' },
      { name: 'fitness', description: 'Track health and wellness' },
      { name: 'learning', description: 'Document educational growth' },
      { name: 'relationships', description: 'Explore personal connections' },
      { name: 'finance', description: 'Manage money and wealth' }
    ];

    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Journal Theme
          </label>
          <div className="space-y-3">
            <input
              ref={themeInputRef}
              type="text"
              value={preferences.theme}
              onChange={handleThemeChange}
              placeholder="Enter your journal theme (e.g., mindfulness, productivity, creativity...)"
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 ${
                errors.theme ? 'border-red-300' : 'border-gray-300'
              }`}
            />

            <div className="text-xs text-gray-500">
              💡 Type any theme or choose from popular options below
            </div>

            {/* Popular Theme Suggestions */}
            <div className="grid grid-cols-2 gap-2 mt-3">
              {popularThemes.map((theme) => (
                <button
                  key={theme.name}
                  onClick={() => setPreferences(prev => ({ ...prev, theme: theme.name }))}
                  className={`text-left p-2 text-sm border rounded hover:bg-gray-50 transition-colors ${
                    preferences.theme === theme.name
                      ? 'border-purple-500 bg-purple-50 text-purple-700'
                      : 'border-gray-200'
                  }`}
                >
                  <div className="font-medium">{theme.name}</div>
                  <div className="text-xs text-gray-500">{theme.description}</div>
                </button>
              ))}
            </div>
          </div>

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
  };

  // Other step components (simplified for brevity - would be enhanced similarly)
  const TitleStep = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Journal Title
        </label>
        <input
          ref={titleInputRef}
          type="text"
          value={preferences.title}
          onChange={handleTitleChange}
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
        <div className="space-y-3">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Bot className="w-4 h-4" />
            <span>Top 5 writing styles for {preferences.theme || 'your selected theme'} (most effective approaches)</span>
          </div>

          {generatingAuthorStyles ? (
            <div className="flex items-center space-x-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
              <span className="text-sm text-blue-800">Analyzing writing styles for {preferences.theme || 'your theme'}...</span>
            </div>
          ) : authorStyleOptions.length > 0 ? (
            <div className="space-y-2">
              <div className="text-xs text-gray-500">Top 5 writing styles for {preferences.theme} (most effective approaches):</div>
              {authorStyleOptions.map((style, index) => (
                <label key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name="author_style"
                    value={style.name}
                    checked={preferences.author_style === style.name}
                    onChange={(e) => setPreferences(prev => ({ ...prev, author_style: e.target.value }))}
                    className="text-purple-600 focus:ring-purple-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{style.name}</div>
                    <div className="text-sm text-gray-600">{style.description}</div>
                    <div className="text-xs text-gray-500">Examples: {style.examples.join(", ")}</div>
                  </div>
                </label>
              ))}

              <button
                onClick={generateAuthorStyles}
                className="text-sm text-purple-600 hover:text-purple-700 flex items-center space-x-1"
              >
                <Sparkles className="w-3 h-3" />
                <span>Regenerate styles</span>
              </button>
            </div>
          ) : (
            <button
              onClick={generateAuthorStyles}
              disabled={!preferences.theme}
              className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>Discover Writing Styles for This Theme</span>
            </button>
          )}
        </div>

        {preferences.author_style && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-800">
                Selected: <strong>{preferences.author_style}</strong>
              </span>
            </div>
          </div>
        )}
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
      // Start AI workflow
      setIsProcessing(true);
      try {
        // Generate a unique job ID for the workflow
        const jobId = `workflow_${new Date().toISOString().replace(/[:.]/g, '_')}`;
        setWorkflowJobId(jobId);

        // Call the original onComplete to start the backend workflow
        await onComplete(preferences);

        // Show the AI workflow modal
        setShowAIWorkflow(true);
      } catch (error) {
        console.error('Workflow start error:', error);
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

      {/* AI Workflow Modal */}
      <AIWorkflowModal
        isOpen={showAIWorkflow}
        onClose={() => {
          setShowAIWorkflow(false);
          onClose();
        }}
        workflowId={workflowJobId}
        jobData={preferences}
      />
    </div>
  );
};

export default EnhancedWebOnboardingAgent;