/**
 * Enhanced Content Library Component
 * Displays journal cards with AI analysis insights and enhancement capabilities
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getApiURL } from '@/lib/apiConfig';
import {
  Search,
  Filter,
  Grid3x3,
  List,
  Calendar,
  Tag,
  ChevronDown,
  RefreshCw,
  Plus,
  BarChart3,
  SortAsc,
  Star,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Button } from '../ui/Button';
import EnhancedJournalCard from './EnhancedJournalCard';
import EnhancedProjectDetail from './EnhancedProjectDetail';

interface JournalContent {
  id: number;
  title: string;
  description: string;
  theme: string;
  creationDate: string;
  lastModified: string;
  status: string;
  fileSize: string;
  pageCount: number;
}

interface AIAnalysis {
  qualityScores: {
    overall_quality: number;
    research_depth: number;
    content_structure: number;
    visual_appeal: number;
    presentation_quality: number;
  };
  completionMap: Record<string, number>;
  recommendations: Array<any>;
  enhancementPotential: number;
  missingComponents: string[];
}

interface ProjectWithAnalysis extends JournalContent {
  analysis?: AIAnalysis;
}

interface EnhancedContentLibraryProps {
  className?: string;
}

const EnhancedContentLibrary: React.FC<EnhancedContentLibraryProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [projects, setProjects] = useState<ProjectWithAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'quality' | 'title'>('date');
  const [filterStatus, setFilterStatus] = useState<'all' | 'high_quality' | 'enhanceable' | 'incomplete'>('all');
  const [selectedProject, setSelectedProject] = useState<ProjectWithAnalysis | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Fetch projects with analysis
  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${getApiURL()}/api/library/llm-projects`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        const projectsWithAnalysis = await Promise.all(
          data.projects.map(async (project: JournalContent) => {
            try {
              const analysisResponse = await fetch(
                `${getApiURL()}/api/journal-content/analyze-project/${project.id}`,
                {
                  headers: {
                    'Authorization': `Bearer ${token}`
                  }
                }
              );

              if (analysisResponse.ok) {
                const analysisData = await analysisResponse.json();
                return {
                  ...project,
                  analysis: analysisData.analysis
                };
              }
            } catch (error) {
              console.error(`Failed to analyze project ${project.id}:`, error);
            }
            return project;
          })
        );

        setProjects(projectsWithAnalysis);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Refresh analysis for all projects
  const refreshAnalysis = useCallback(async () => {
    setLoadingAnalysis(true);
    await fetchProjects();
    setLoadingAnalysis(false);
  }, [fetchProjects]);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // Filter and sort projects
  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.theme.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter = filterStatus === 'all' ||
      (filterStatus === 'high_quality' && project.analysis?.qualityScores.overall_quality >= 80) ||
      (filterStatus === 'enhanceable' && (project.analysis?.enhancementPotential || 0) > 50) ||
      (filterStatus === 'incomplete' && (project.analysis?.missingComponents.length || 0) > 0);

    return matchesSearch && matchesFilter;
  });

  const sortedProjects = [...filteredProjects].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime();
      case 'quality':
        return (b.analysis?.qualityScores.overall_quality || 0) - (a.analysis?.qualityScores.overall_quality || 0);
      case 'title':
        return a.title.localeCompare(b.title);
      default:
        return 0;
    }
  });

  const handleProjectSelect = (project: ProjectWithAnalysis) => {
    setSelectedProject(project);
  };

  const handleProjectEnhance = (project: ProjectWithAnalysis, enhancementType?: string) => {
    // Navigate to project detail with enhancement options
    navigate(`/projects/${project.id}`, {
      state: { enhancementAction: enhancementType }
    });
  };

  const handleProjectAnalyze = (project: ProjectWithAnalysis) => {
    navigate(`/projects/${project.id}`);
  };

  const handleProjectPreview = (project: ProjectWithAnalysis) => {
    // Implement preview functionality
    console.log('Preview project:', project);
  };

  const handleProjectDownload = (project: ProjectWithAnalysis) => {
    // Implement download functionality
    console.log('Download project:', project);
  };

  const handleCreateNew = () => {
    navigate('/dashboard?create=true');
  };

  // Calculate statistics
  const stats = {
    total: projects.length,
    highQuality: projects.filter(p => p.analysis?.qualityScores.overall_quality >= 80).length,
    enhanceable: projects.filter(p => (p.analysis?.enhancementPotential || 0) > 50).length,
    incomplete: projects.filter(p => (p.analysis?.missingComponents.length || 0) > 0).length,
    averageQuality: projects.length > 0
      ? Math.round(projects.reduce((sum, p) => sum + (p.analysis?.qualityScores.overall_quality || 0), 0) / projects.length)
      : 0
  };

  if (selectedProject) {
    return (
      <EnhancedProjectDetail
        projectId={selectedProject.id}
        onBack={() => setSelectedProject(null)}
      />
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Journal Library</h1>
              <p className="text-sm text-gray-600 mt-1">
                Manage and enhance your AI-powered journal content
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                onClick={refreshAnalysis}
                disabled={loadingAnalysis}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${loadingAnalysis ? 'animate-spin' : ''}`} />
                <span>Refresh Analysis</span>
              </Button>
              <Button
                onClick={handleCreateNew}
                className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700"
              >
                <Plus className="w-4 h-4" />
                <span>Create New Journal</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Projects</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="text-blue-600">
                <BarChart3 className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High Quality</p>
                <p className="text-2xl font-bold text-green-600">{stats.highQuality}</p>
              </div>
              <div className="text-green-600">
                <CheckCircle className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Enhanceable</p>
                <p className="text-2xl font-bold text-purple-600">{stats.enhanceable}</p>
              </div>
              <div className="text-purple-600">
                <TrendingUp className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Incomplete</p>
                <p className="text-2xl font-bold text-orange-600">{stats.incomplete}</p>
              </div>
              <div className="text-orange-600">
                <AlertCircle className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Quality</p>
                <p className="text-2xl font-bold text-blue-600">{stats.averageQuality}%</p>
              </div>
              <div className="text-blue-600">
                <Star className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="flex-1 max-w-lg">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search journals..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center space-x-3">
              {/* Filter Status */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Projects</option>
                <option value="high_quality">High Quality</option>
                <option value="enhanceable">Enhanceable</option>
                <option value="incomplete">Incomplete</option>
              </select>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="date">Sort by Date</option>
                <option value="quality">Sort by Quality</option>
                <option value="title">Sort by Title</option>
              </select>

              {/* View Mode */}
              <div className="flex items-center border border-gray-300 rounded-lg">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  <Grid3x3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 ${viewMode === 'list' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Projects Grid/List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-purple-600" />
              <p className="text-gray-600">Loading your journal library...</p>
            </div>
          </div>
        ) : sortedProjects.length === 0 ? (
          <div className="text-center py-20">
            <div className="bg-white rounded-lg p-8 shadow-sm max-w-md mx-auto">
              <div className="text-gray-400 mb-4">
                <BarChart3 className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No journals found</h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || filterStatus !== 'all'
                  ? 'Try adjusting your filters or search terms'
                  : 'Get started by creating your first AI-powered journal'
                }
              </p>
              <Button onClick={handleCreateNew} className="bg-purple-600 hover:bg-purple-700">
                <Plus className="w-4 h-4 mr-2" />
                Create New Journal
              </Button>
            </div>
          </div>
        ) : (
          <div className={`grid gap-6 ${
            viewMode === 'grid'
              ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
              : 'grid-cols-1'
          }`}>
            {sortedProjects.map((project) => (
              <EnhancedJournalCard
                key={project.id}
                content={project}
                analysis={project.analysis}
                onSelect={() => handleProjectSelect(project)}
                onPreview={() => handleProjectPreview(project)}
                onDownload={() => handleProjectDownload(project)}
                onEnhance={(content, recommendationId) => handleProjectEnhance(content, recommendationId)}
                onAnalyze={() => handleProjectAnalyze(project)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedContentLibrary;