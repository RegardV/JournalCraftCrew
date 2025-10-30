import React, { useState, useEffect } from 'react';
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
import { Link } from 'react-router-dom';
import { projectAPI } from '@/lib/api';
import JournalCreationModal from '@/components/journal/JournalCreationModal';
import JournalProgress from '@/components/journal/JournalProgress';

interface DashboardProps {
  user?: {
    name: string;
    email: string;
  };
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const [activeView, setActiveView] = useState<'dashboard' | 'settings'>('dashboard');
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
  const [isJournalModalOpen, setIsJournalModalOpen] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  useEffect(() => {
    // Fetch LLM projects when component mounts
    const fetchLLMProjects = async () => {
      try {
        const response = await projectAPI.getLLMProjects();
        if (response.projects && response.projects.length > 0) {
          const formattedProjects = response.projects.map((project: any) => ({
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

  const handleCreateJournal = () => {
    setIsJournalModalOpen(true);
  };

  const handleJournalCreation = async (preferences: any) => {
    try {
      const response = await fetch('/api/journals/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(preferences)
      });

      if (response.ok) {
        const data = await response.json();
        setActiveJobId(data.jobId);
      } else {
        console.error('Failed to create journal:', await response.text());
        alert('Failed to create journal. Please try again.');
      }
    } catch (error) {
      console.error('Error creating journal:', error);
      alert('An error occurred while creating your journal. Please try again.');
    }
  };

  const handleJournalComplete = (result: any) => {
    setActiveJobId(null);
    // Refresh the recent projects list
    window.location.reload();
  };

  const handleJournalError = (error: string) => {
    setActiveJobId(null);
    console.error('Journal creation error:', error);
    alert(`Journal creation failed: ${error}`);
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

  if (activeView === 'settings') {
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
            <div key={index} className="metric-card hover-lift group">
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
          <button className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group">
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="font-medium">Generate New Journal</span>
              <span className="text-sm text-gray-600">Start with AI-powered content</span>
            </div>
          </button>

          <button className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group">
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="font-medium">Browse Templates</span>
              <span className="text-sm text-gray-600">Choose from pre-built themes</span>
            </div>
          </button>

          <button className="p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group">
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
          <button className="btn btn-ghost">
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
              <div key={project.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
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

      {/* Journal Creation Modal */}
      <JournalCreationModal
        isOpen={isJournalModalOpen}
        onClose={() => setIsJournalModalOpen(false)}
        onComplete={handleJournalCreation}
      />

      {/* Journal Progress Modal */}
      {activeJobId && (
        <JournalProgress
          jobId={activeJobId}
          onComplete={handleJournalComplete}
          onError={handleJournalError}
        />
      )}
    </div>
  );
};

export default Dashboard;