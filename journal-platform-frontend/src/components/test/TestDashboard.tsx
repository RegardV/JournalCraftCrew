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

const TestDashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<'dashboard' | 'settings'>('dashboard');

  const stats = [
    {
      title: 'Total Journals',
      value: '0',
      change: 'Ready to create',
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
      value: '0',
      change: 'Create your first',
      icon: Users,
      color: 'from-green-500 to-green-600',
      trend: 'neutral'
    }
  ];

  const recentProjects: Array<{
  id: string;
  title: string;
  description: string;
  status: string;
  progress: number;
  lastEdit: string;
  wordCount: string;
  filePath?: string;
}> = [];

  if (activeView === 'settings') {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-heading">Test Settings</h1>
            <p className="text-gray-600">Manage account settings (Test Mode)</p>
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
            Test User Profile
          </h3>
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Name</p>
              <p className="font-medium">Test User</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Email</p>
              <p className="font-medium">test@example.com</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Account Type</p>
              <p className="font-medium">Test Account - No Authentication Required</p>
            </div>
          </div>
        </div>

        <div className="content-card">
          <h3 className="text-subheading font-semibold mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Test Settings
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <span className="font-medium">Dark Mode</span>
              <button className="btn btn-outline">Enable</button>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <span className="font-medium">Email Notifications</span>
              <button className="btn btn-outline">Configure</button>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <span className="font-medium">Language</span>
              <select className="input w-auto">
                <option>English</option>
                <option>Spanish</option>
                <option>French</option>
              </select>
            </div>
          </div>
        </div>

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>Test Mode:</strong> This is a development interface without authentication.
            Go to <Link to="/" className="text-yellow-600 underline">home page</Link> to test the actual authentication flow.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Test Mode Header */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 p-6 rounded-2xl shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-yellow-800">Test Mode</h2>
              <p className="text-sm text-yellow-700">No authentication required - Development preview</p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              to="/"
              className="btn btn-outline flex items-center justify-center gap-2"
            >
              <Home className="w-4 h-4" />
              Live Site
            </Link>
            <Link
              to="/auth/login"
              className="btn btn-outline flex items-center justify-center gap-2"
            >
              <LogIn className="w-4 h-4" />
              Test Login
            </Link>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="text-center lg:text-left">
          <h1 className="text-display gradient-text mb-4">
            Welcome to Journal Craft Crew!
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl">
            Explore the dashboard features (Test Mode - No Login Required)
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 lg:shrink-0">
          <button className="btn btn-primary flex items-center justify-center gap-2 text-lg px-6 py-3 shadow-lg hover:shadow-xl hover-lift">
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
              <p className="font-medium">Completed "Mindfulness Journey" journal</p>
              <p className="text-sm text-gray-600">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
            <div>
              <p className="font-medium">Started new project: "Productivity Mastery"</p>
              <p className="text-sm text-gray-600">1 day ago</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
            <div>
              <p className="font-medium">Updated settings preferences</p>
              <p className="text-sm text-gray-600">3 days ago</p>
            </div>
          </div>
        </div>
      </div>

      {/* Test Mode Footer */}
      <div className="mt-8 p-4 bg-gray-100 rounded-lg text-center">
        <p className="text-sm text-gray-600 mb-2">
          <strong>Test Dashboard:</strong> This interface allows you to explore all features without authentication.
        </p>
        <p className="text-xs text-gray-500">
          Use the navigation buttons above to test the live site or authentication flow.
        </p>
      </div>
    </div>
  );
};

export default TestDashboard;