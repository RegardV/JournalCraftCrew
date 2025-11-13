import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useSearchParams } from 'react-router-dom';
import { KeyIcon, EyeIcon, EyeSlashIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import {
  Plus,
  BookOpen,
  BarChart3,
  Users,
  Clock,
  Sparkles,
  FileText,
  Image,
  Settings,
  User,
  TrendingUp,
  Zap,
  Activity,
  LogIn,
  Home,
  ArrowRight
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { projectAPI } from '@/lib/api';
import JournalProgress from '@/components/journal/JournalProgress';
import ContentLibrary from '@/components/content/ContentLibrary';
import UnifiedJournalCreator from '@/components/journal/UnifiedJournalCreator';

interface DashboardProps {
  user?: {
    name: string;
    email: string;
  };
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const { token, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeView, setActiveView] = useState<'dashboard' | 'library' | 'settings' | 'analytics' | 'active-projects'>('dashboard');

  // Handle URL parameters for view switching
  useEffect(() => {
    const view = searchParams.get('view');
    if (view && ['dashboard', 'library', 'settings', 'analytics', 'active-projects'].includes(view)) {
      setActiveView(view as any);
    }
  }, [searchParams]);

  // Maintain a list of orphaned projects that should be filtered out (persisted in localStorage)
  const [orphanedProjectIds, setOrphanedProjectIds] = useState<Set<string>>(() => {
    // Start fresh - clear any existing orphaned data since we removed fake data
    localStorage.removeItem('orphanedJournalIds');
    return new Set();
  });

  // API Key state
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [apiKeyStatus, setApiKeyStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [apiKeyMessage, setApiKeyMessage] = useState('');
  const [recentProjects, setRecentProjects] = useState<Array<{
    id: string;
    title: string;
    description: string;
    status: string;
    progress: number;
    lastEdit: string;
    wordCount: string;
    filePath?: string;
  }>>([]);

  // Journal creation state
  const [showUnifiedCreator, setShowUnifiedCreator] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [userPreferences, setUserPreferences] = useState<any>(null);

  useEffect(() => {
    // Fetch LLM projects when component mounts
    const fetchLLMProjects = async () => {
      try {
        const response = await projectAPI.getLLMProjects();
        if (response.projects && response.projects.length > 0) {
          const formattedProjects = response.projects
            .filter((project: any) => !orphanedProjectIds.has(project.id))
            .map((project: any) => ({
              id: project.id,
              title: project.title,
              description: project.description,
              status: project.status,
              progress: project.progress || 100,
              lastEdit: new Date(project.created_at).toLocaleDateString(),
              wordCount: project.word_count || 'N/A',
              files: project.files || []
            }));
          setRecentProjects(formattedProjects);
        }
      } catch (error) {
        console.error('Error fetching LLM projects:', error);
      }
    };

    if (activeView === 'dashboard') {
      fetchLLMProjects();
    }
  }, [activeView]);

  // Effect to check API key status when component mounts and token changes
  useEffect(() => {
    if (!isAuthenticated || !token) return;

    const checkApiKeyStatus = async () => {
      try {
        const response = await fetch('http://localhost:6770/api/settings/api-key', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.has_api_key) {
            setApiKeyMessage('API key is configured and ready to use');
            setApiKeyStatus('saved');
          }
        }
      } catch (error) {
        console.error('Failed to check API key status:', error);
      }
    };

    checkApiKeyStatus();
  }, [isAuthenticated, token]);

  const handleCreateJournal = () => {
    setShowUnifiedCreator(true);
  };

  const handleJournalCreation = async (preferences: any) => {
    try {
      // Direct journal creation for testing
      console.log('Creating journal with preferences:', preferences);

      // Format preferences to match backend API structure
      const formattedPreferences = {
        preferences: {
          theme: preferences.theme || preferences.selectedTheme,
          title: preferences.title || preferences.projectTitle,
          titleStyle: preferences.titleStyle || preferences.title_style,
          authorStyle: preferences.authorStyle || preferences.author_style,
          researchDepth: preferences.researchDepth || preferences.research_depth
        }
      };

      console.log('Sending formatted request:', formattedPreferences);

      // Check if user is authenticated
      if (!isAuthenticated || !token) {
        throw new Error('Authentication required. Please log in first.');
      }

      // Close unified creator and navigate to workflow progress
      setShowUnifiedCreator(false);

      // Start CrewAI workflow through new unified system
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:6770'}/api/crewai/start-workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_preferences: preferences
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('CrewAI workflow started:', data);

        // Navigate to the AI workflow page with the workflow ID
        navigate(`/ai-workflow/${data.workflow_id}`, {
          state: { workflowData: data }
        });
      } else {
        const errorText = await response.text();
        console.error('Failed to start CrewAI workflow:', errorText);

        if (response.status === 401) {
          alert('Authentication required. Please log in first.');
        } else {
          alert(`Failed to start journal creation: ${errorText}`);
        }
      }
    } catch (error) {
      console.error('Error creating journal:', error);
      alert('Network error. Please check your connection and try again.');
    }
  };

  const handleJournalComplete = (result: any) => {
    setActiveJobId(null);
    // Refresh the recent projects list instead of full reload
    const fetchLLMProjects = async () => {
      try {
        const response = await projectAPI.getLLMProjects();
        if (response.projects && response.projects.length > 0) {
          const formattedProjects = response.projects
            .filter((project: any) => !orphanedProjectIds.has(project.id))
            .map((project: any) => ({
              id: project.id,
              title: project.title,
              description: project.description,
              status: project.status,
              progress: project.progress || 100,
              lastEdit: new Date(project.created_at).toLocaleDateString(),
              wordCount: project.word_count || 'N/A',
              files: project.files || []
            }));
          setRecentProjects(formattedProjects);
        }
      } catch (error) {
        console.error('Error refreshing projects:', error);
      }
    };

    fetchLLMProjects();

    // Show success notification with library guidance
    const goToLibrary = confirm(
      '🎉 Journal created successfully!\n\nYour journal is now ready in your Content Library where you can:\n• Download the complete PDF\n• Preview all pages\n• View AI agent details\n• Access all your generated content\n\nWould you like to visit your Content Library now?'
    );

    if (goToLibrary) {
      setActiveView('library');
    }
  };

  const handleJournalError = (error: string) => {
    setActiveJobId(null);
    console.error('Journal creation error:', error);
    alert(`Journal creation failed: ${error}`);
  };

  // API Key Management Functions
  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) {
      setApiKeyStatus('error');
      setApiKeyMessage('Please enter a valid API key');
      return;
    }

    setApiKeyStatus('saving');
    setApiKeyMessage('');

    try {
      const response = await fetch('http://localhost:6770/api/settings/api-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          apiKey: apiKey.trim(),
          provider: 'openai'
        })
      });

      if (response.ok) {
        setApiKeyStatus('saved');
        setApiKeyMessage('API key saved successfully!');
        // Clear the input for security
        setApiKey('');
        setTimeout(() => {
          setApiKeyStatus('idle');
          setApiKeyMessage('');
        }, 3000);
      } else {
        const error = await response.json();
        setApiKeyStatus('error');
        setApiKeyMessage(error.error?.message || 'Failed to save API key');
      }
    } catch (error) {
      setApiKeyStatus('error');
      setApiKeyMessage('Network error. Please try again.');
      console.error('API key save error:', error);
    }
  };

  const handleTestApiKey = async () => {
    console.log('Test button clicked!');
    console.log('API key value:', apiKey);
    console.log('Token available:', !!token);

    if (!apiKey.trim()) {
      setApiKeyStatus('error');
      setApiKeyMessage('Please enter an API key to test');
      return;
    }

    setApiKeyStatus('saving');
    setApiKeyMessage('Testing API key...');

    try {
      const response = await fetch('http://localhost:6770/api/settings/test-api-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          apiKey: apiKey.trim(),
          provider: 'openai'
        })
      });

      if (response.ok) {
        const result = await response.json();
        setApiKeyStatus('saved');
        setApiKeyMessage('API key is valid and working!');
      } else {
        const error = await response.json();
        setApiKeyStatus('error');
        setApiKeyMessage(error.error?.message || 'Invalid API key');
      }
    } catch (error) {
      setApiKeyStatus('error');
      setApiKeyMessage('Network error. Please try again.');
      console.error('API key test error:', error);
    }
  };

  const handleProjectStatus = async (projectId: string) => {
    try {
      const response = await fetch(`http://localhost:6770/api/journals/status/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Project Status: ${data.status}\nProgress: ${data.progress}%\n${data.message || ''}`);
      } else {
        alert('Failed to fetch project status');
      }
    } catch (error) {
      console.error('Error checking project status:', error);
      alert('Error checking project status');
    }
  };

  const handleDeleteProject = async (projectId: string, projectTitle: string) => {
    if (window.confirm(`Are you sure you want to delete "${projectTitle}"? This action cannot be undone.`)) {
      try {
        // Use the universal delete endpoint that handles all project ID formats
        const deleteUrl = `http://localhost:6770/api/library/projects/${projectId}`;

        const response = await fetch(deleteUrl, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          // Refresh the projects list
          window.location.reload();
        } else if (response.status === 404) {
          // Project not found in backend - mark as orphaned and refresh UI
          console.log(`Project ${projectId} not found in backend, marking as orphaned`);
          const newOrphanedIds = new Set(orphanedProjectIds).add(projectId);
          setOrphanedProjectIds(newOrphanedIds);
          localStorage.setItem('orphanedJournalIds', JSON.stringify([...newOrphanedIds]));
          alert('Project removed from library (content was already missing)');
          window.location.reload();
        } else {
          const error = await response.json();
          alert(`Failed to delete project: ${error.detail || 'Unknown error'}`);
        }
      } catch (error) {
        console.error('Delete error:', error);
        // For network errors, still try to refresh UI if it's a 404-like situation
        if (error.message && error.message.includes('404')) {
          const newOrphanedIds = new Set(orphanedProjectIds).add(projectId);
          setOrphanedProjectIds(newOrphanedIds);
          localStorage.setItem('orphanedJournalIds', JSON.stringify([...newOrphanedIds]));
          alert('Project removed from library (content was already missing)');
          window.location.reload();
        } else {
          alert('Failed to delete project. Please try again.');
        }
      }
    }
  };

  const handleStatCardClick = (statTitle: string) => {
    switch (statTitle) {
      case 'Total Journals':
        setActiveView('library');
        break;
      case 'Words Written':
        setActiveView('analytics');
        break;
      case 'Active Projects':
        setActiveView('active-projects');
        break;
      default:
        // For any other stat card, go to analytics
        setActiveView('analytics');
        break;
    }
  };

  const stats = [
    {
      title: 'Total Journals',
      value: recentProjects.length.toString(),
      change: recentProjects.length > 0 ? `${recentProjects.length} projects` : 'Ready to create',
      icon: BookOpen,
      color: 'from-blue-500 to-blue-600',
      trend: 'neutral'
    },
    {
      title: 'Words Written',
      value: '0',
      change: 'Start writing',
      icon: FileText,
      color: 'from-indigo-500 to-indigo-600',
      trend: 'neutral'
    },
    {
      title: 'Active Projects',
      value: recentProjects.length.toString(),
      change: recentProjects.length > 0 ? 'Working on projects' : 'Create your first',
      icon: Users,
      color: 'from-green-500 to-green-600',
      trend: 'neutral'
    }
  ];

  if (activeView === 'library') {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setActiveView('dashboard')}
            className="btn btn-ghost"
          >
            ← Back to Dashboard
          </button>
          <button
            onClick={() => handleCreateJournal()}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create New Journal
          </button>
        </div>
        <ContentLibrary />
      </div>
    );
  }

  if (activeView === 'settings') {
    console.log('Settings view rendered');
    console.log('Token available in settings:', !!token);
    console.log('Current API key status:', apiKeyStatus);
    console.log('Current API key value:', apiKey);

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-heading">Settings</h1>
            <p className="text-gray-600">Manage your account and preferences</p>
          </div>
          <button
            onClick={() => setActiveView('dashboard')}
            className="btn btn-outline"
          >
            Back to Dashboard
          </button>
        </div>
        <div className="content-card">
          <h3 className="text-subheading font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5" />
            User Profile
          </h3>
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Name</p>
              <p className="font-medium">{user?.name || 'Demo User'}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Email</p>
              <p className="font-medium">{user?.email || 'demo@example.com'}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Account Type</p>
              <p className="font-medium">Premium Account - AI Journal Generation</p>
            </div>
          </div>
        </div>

        <div className="content-card">
          <h3 className="text-subheading font-semibold mb-4 flex items-center gap-2">
            <KeyIcon className="w-5 h-5" />
            OpenAI API Configuration
          </h3>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <div className="relative">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showApiKey ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Your OpenAI API key is used for AI journal generation. It's stored securely and never shared.
              </p>
            </div>

            {apiKeyMessage && (
              <div className={`p-4 rounded-lg flex items-start gap-3 ${
                apiKeyStatus === 'saved'
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : apiKeyStatus === 'error'
                  ? 'bg-red-50 text-red-800 border border-red-200'
                  : 'bg-blue-50 text-blue-800 border border-blue-200'
              }`}>
                {apiKeyStatus === 'saved' ? (
                  <CheckCircleIcon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                ) : apiKeyStatus === 'error' ? (
                  <ExclamationTriangleIcon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                ) : (
                  <div className="h-5 w-5 mt-0.5 flex-shrink-0 border-2 border-blue-400 border-t-transparent animate-spin rounded-full" />
                )}
                <p className="text-sm">{apiKeyMessage}</p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={handleSaveApiKey}
                disabled={apiKeyStatus === 'saving'}
                className="btn btn-primary flex items-center gap-2"
              >
                {apiKeyStatus === 'saving' ? (
                  <>
                    <div className="h-4 w-4 border-2 border-white border-t-transparent animate-spin rounded-full" />
                    Saving...
                  </>
                ) : (
                  <>
                    <KeyIcon className="h-4 w-4" />
                    Save API Key
                  </>
                )}
              </button>
              <button
                onClick={() => {
                  console.log('Button clicked!');
                  console.log('Disabled:', apiKeyStatus === 'saving' || !apiKey.trim());
                  console.log('API key status:', apiKeyStatus);
                  console.log('API key trim:', apiKey.trim());
                  handleTestApiKey();
                }}
                disabled={apiKeyStatus === 'saving' || !apiKey.trim()}
                className="btn btn-outline flex items-center gap-2"
              >
                {apiKeyStatus === 'saving' ? (
                  <>
                    <div className="h-4 w-4 border-2 border-gray-600 border-t-transparent animate-spin rounded-full" />
                    Testing...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="h-4 w-4" />
                    Test Key
                  </>
                )}
              </button>
            </div>

            <div className="border-t pt-4">
              <h4 className="font-medium mb-2">How to get your API key:</h4>
              <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
                <li>Go to <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">OpenAI API Keys</a></li>
                <li>Click "Create new secret key"</li>
                <li>Give it a name (e.g., "Journal Craft Crew")</li>
                <li>Copy the key and paste it above</li>
                <li>Save the key to enable AI journal generation</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (activeView === 'analytics') {
    // Calculate analytics data
    const completedProjects = recentProjects.filter(p => p.status === 'completed' || p.progress === 100);
    const inProgressProjects = recentProjects.filter(p => p.status === 'in_progress' || (p.progress > 0 && p.progress < 100));
    const totalWords = recentProjects.reduce((total, project) => {
      const words = parseInt(project.wordCount) || 0;
      return total + words;
    }, 0);
    const avgWordsPerProject = recentProjects.length > 0 ? Math.round(totalWords / recentProjects.length) : 0;

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-heading">Analytics Dashboard</h1>
            <p className="text-gray-600">Track your journal creation progress and writing insights</p>
          </div>
          <button
            onClick={() => setActiveView('dashboard')}
            className="btn btn-outline"
          >
            Back to Dashboard
          </button>
        </div>

        {/* Main Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="content-card hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Journals</p>
                <p className="text-3xl font-bold text-gray-900">{recentProjects.length}</p>
                <p className="text-xs text-gray-500 mt-1">All time creations</p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <BookOpen className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>

          <div className="content-card hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Completed</p>
                <p className="text-3xl font-bold text-gray-900">{completedProjects.length}</p>
                <p className="text-xs text-green-600 mt-1">
                  {recentProjects.length > 0 ? `${Math.round((completedProjects.length / recentProjects.length) * 100)}% completion rate` : 'No projects yet'}
                </p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                <CheckCircleIcon className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>

          <div className="content-card hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">In Progress</p>
                <p className="text-3xl font-bold text-gray-900">{inProgressProjects.length}</p>
                <p className="text-xs text-yellow-600 mt-1">Active projects</p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg">
                <Clock className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>

          <div className="content-card hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Words</p>
                <p className="text-3xl font-bold text-gray-900">{totalWords.toLocaleString()}</p>
                <p className="text-xs text-purple-600 mt-1">~{avgWordsPerProject} avg per journal</p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <FileText className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Usage Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="content-card">
            <h3 className="text-subheading font-semibold mb-6 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Usage Insights
            </h3>

            {recentProjects.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="w-8 h-8 text-gray-400" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Start Creating Journals</h4>
                <p className="text-gray-600 mb-4">Begin your AI-powered journaling journey to see your writing analytics here</p>
                <a
                  href="/ai-workflow"
                  className="btn btn-primary inline-flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  Create Your First Journal
                </a>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Project Status Distribution */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Project Status</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Completed</span>
                      <span className="text-sm font-medium">{completedProjects.length} journals</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full"
                        style={{ width: `${recentProjects.length > 0 ? (completedProjects.length / recentProjects.length) * 100 : 0}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">In Progress</span>
                      <span className="text-sm font-medium">{inProgressProjects.length} journals</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-yellow-500 to-orange-600 h-2 rounded-full"
                        style={{ width: `${recentProjects.length > 0 ? (inProgressProjects.length / recentProjects.length) * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Writing Statistics */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Writing Statistics</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{avgWordsPerProject.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Avg Words/Journal</div>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{totalWords.toLocaleString()}</div>
                      <div className="text-sm text-gray-600">Total Words Written</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Recent Activity Timeline */}
          <div className="content-card">
            <h3 className="text-subheading font-semibold mb-6 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Recent Activity
            </h3>

            {recentProjects.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Activity className="w-8 h-8 text-blue-400" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">No Activity Yet</h4>
                <p className="text-gray-600">Your journal creation activity will appear here</p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentProjects.slice(0, 5).map((project, index) => (
                  <div key={project.id} className="flex gap-3">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                      project.status === 'completed' || project.progress === 100
                        ? 'bg-green-500'
                        : 'bg-yellow-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{project.title}</p>
                      <p className="text-sm text-gray-600 truncate">{project.description}</p>
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                        <span>{project.wordCount} words</span>
                        <span>•</span>
                        <span>{project.lastEdit}</span>
                        <span>•</span>
                        <span className={`font-medium ${
                          project.status === 'completed' || project.progress === 100
                            ? 'text-green-600'
                            : 'text-yellow-600'
                        }`}>
                          {project.status === 'completed' || project.progress === 100 ? 'Completed' : 'In Progress'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}

                {recentProjects.length > 5 && (
                  <button
                    onClick={() => setActiveView('library')}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-2"
                  >
                    View all {recentProjects.length} projects →
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="content-card">
          <h3 className="text-subheading font-semibold mb-6">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/ai-workflow"
              className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group"
            >
              <div className="flex flex-col items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <span className="font-medium">Create New Journal</span>
                <span className="text-sm text-gray-600">Generate AI-powered content</span>
              </div>
            </a>

            <button
              onClick={() => setActiveView('library')}
              className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all group"
            >
              <div className="flex flex-col items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <span className="font-medium">Browse Library</span>
                <span className="text-sm text-gray-600">View all your journals</span>
              </div>
            </button>

            <button
              onClick={() => setActiveView('active-projects')}
              className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-yellow-500 hover:bg-yellow-50 transition-all group"
            >
              <div className="flex flex-col items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Clock className="w-6 h-6 text-white" />
                </div>
                <span className="font-medium">Active Projects</span>
                <span className="text-sm text-gray-600">Track in-progress journals</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (activeView === 'active-projects') {
    // Filter projects to show only active/in-progress ones
    const activeProjects = recentProjects.filter(project =>
      project.status === 'in_progress' ||
      project.status === 'active' ||
      (project.progress > 0 && project.progress < 100)
    );

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-heading">Active Projects</h1>
            <p className="text-gray-600">Projects currently in progress</p>
          </div>
          <button
            onClick={() => setActiveView('dashboard')}
            className="btn btn-outline"
          >
            Back to Dashboard
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="content-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Active Projects</p>
                <p className="text-2xl font-bold text-gray-900">{activeProjects.length}</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                <Clock className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="content-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Avg Progress</p>
                <p className="text-2xl font-bold text-gray-900">
                  {activeProjects.length > 0
                    ? Math.round(activeProjects.reduce((sum, p) => sum + p.progress, 0) / activeProjects.length)
                    : 0}%
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="content-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Words</p>
                <p className="text-2xl font-bold text-gray-900">
                  {activeProjects.reduce((total, project) => {
                    const words = parseInt(project.wordCount) || 0;
                    return total + words;
                  }, 0)}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        <div className="content-card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-subheading font-semibold">Active Projects</h3>
            {activeProjects.length > 0 && (
              <button
                onClick={() => setActiveView('library')}
                className="btn btn-ghost"
              >
                View All Projects
              </button>
            )}
          </div>

          {activeProjects.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Clock className="w-10 h-10 text-gray-400" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-3">No Active Projects</h4>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                You don't have any projects in progress right now. Start a new AI-powered journal or check your completed projects.
              </p>
              <div className="flex justify-center gap-3">
                <a
                  href="/ai-workflow"
                  className="btn btn-primary flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  Start AI Generation
                </a>
                <button
                  onClick={() => setActiveView('library')}
                  className="btn btn-outline"
                >
                  View All Projects
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {activeProjects.map((project) => (
                <div
                  key={project.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{project.title}</h4>
                      <p className="text-sm text-gray-600">{project.description}</p>
                      <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                        <span>{project.wordCount} words</span>
                        <span>•</span>
                        <span>{project.lastEdit}</span>
                        <span>•</span>
                        <span className="text-yellow-600 font-medium">In Progress</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">{project.progress}%</div>
                      <div className="text-xs text-gray-600">{project.status}</div>
                    </div>
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-yellow-500 to-orange-600 h-2 rounded-full transition-all"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                    <button
                      onClick={() => handleProjectStatus(project.id)}
                      className="p-2 hover:bg-gray-200 rounded-lg transition-colors ml-4"
                      title="View status"
                    >
                      <Eye className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() => handleDeleteProject(project.id, project.title)}
                      className="p-2 hover:bg-red-100 hover:text-red-600 rounded-lg transition-colors"
                      title="Delete project"
                    >
                      <Trash2 className="w-4 h-4 text-gray-600 hover:text-red-600" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="text-center lg:text-left">
          <h1 className="text-display gradient-text mb-4">
            Welcome back, {user?.name || 'User'}!
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl">
            Ready to create your next AI-powered journal?
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 lg:shrink-0">
          <button
            onClick={() => handleCreateJournal()}
            className="btn btn-primary flex items-center justify-center gap-2 text-lg px-6 py-3 shadow-lg hover:shadow-xl hover-lift"
          >
            <Plus className="w-5 h-5" />
            Create New Journal
          </button>
          <button
            onClick={() => setActiveView('library')}
            className="btn btn-outline flex items-center justify-center gap-2 px-6 py-3"
          >
            <FileText className="w-5 h-5" />
            Content Library
          </button>
          <button
            onClick={() => setActiveView('settings')}
            className="btn btn-outline flex items-center justify-center gap-2 px-6 py-3"
          >
            <Settings className="w-5 h-5" />
            Settings
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="metric-card hover-lift group cursor-pointer"
              onClick={() => handleStatCardClick(stat.title)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-gray-600 mb-2 font-medium">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</p>
                  <p className={`text-sm ${
                    stat.trend === 'up' ? 'text-green-600' :
                    stat.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {stat.change}
                  </p>
                </div>
                <div className={`w-14 h-14 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-all duration-200`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="content-card">
        <h3 className="text-subheading font-semibold mb-6">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => handleCreateJournal()}
            className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group"
          >
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="font-medium">Generate New Journal</span>
              <span className="text-sm text-gray-600">Start with AI-powered content</span>
            </div>
          </button>

          <button
            onClick={() => setActiveView('library')}
            className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group"
          >
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="font-medium">Browse Templates</span>
              <span className="text-sm text-gray-600">Choose from pre-built themes</span>
            </div>
          </button>

          <button
            onClick={() => setActiveView('analytics')}
            className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group"
          >
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <span className="font-medium">View Analytics</span>
              <span className="text-sm text-gray-600">Track your progress</span>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Projects */}
      <div className="content-card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-subheading font-semibold">Recent Projects</h3>
          <button
            onClick={() => setActiveView('library')}
            className="btn btn-ghost"
          >
            View All
          </button>
        </div>

        {recentProjects.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <FileText className="w-10 h-10 text-gray-400" />
            </div>
            <h4 className="text-xl font-semibold text-gray-900 mb-3">No projects yet</h4>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Create your first AI-powered journal to get started with personalized content generation
            </p>
            <button
              onClick={() => handleCreateJournal()}
              className="btn btn-primary flex items-center gap-2 mx-auto text-lg px-8 py-3 shadow-lg hover:shadow-xl hover-lift"
            >
              <Plus className="w-5 h-5" />
              Create New Journal
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {recentProjects.map((project) => (
              <div
                key={project.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => handleProjectStatus(project.id)}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{project.title}</h4>
                    <p className="text-sm text-gray-600">{project.description}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span>{project.wordCount} words</span>
                      <span>•</span>
                      <span>{project.lastEdit}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{project.progress}%</div>
                    <div className="text-xs text-gray-600">{project.status}</div>
                  </div>
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all"
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Activity Section */}
      <div className="content-card">
        <h3 className="text-subheading font-semibold mb-6 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Recent Activity
        </h3>
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div>
              <p className="font-medium">Journal generation completed</p>
              <p className="text-sm text-gray-600">Your AI-powered journal was successfully created with personalized content</p>
              <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
            <div>
              <p className="font-medium">API key configured</p>
              <p className="text-sm text-gray-600">OpenAI API key successfully added to your account settings</p>
              <p className="text-xs text-gray-500 mt-1">3 days ago</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
            <div>
              <p className="font-medium">Account created</p>
              <p className="text-sm text-gray-600">Welcome to Journal Craft Crew! Your account is ready to create amazing journals</p>
              <p className="text-xs text-gray-500 mt-1">1 week ago</p>
            </div>
          </div>
        </div>
      </div>

      {/* Unified Journal Creator - Replaces all old creation modals */}
      {showUnifiedCreator && (
        <UnifiedJournalCreator
          onComplete={handleJournalCreation}
          onClose={() => setShowUnifiedCreator(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;