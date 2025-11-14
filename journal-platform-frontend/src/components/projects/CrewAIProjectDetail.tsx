import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getApiURL } from '@/lib/apiConfig';
import {
  ArrowLeft,
  Users,
  Search,
  Brain,
  FileText,
  Edit3,
  Image,
  Download,
  Book,
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  Loader2,
  Clock,
  FolderOpen,
  FileText as FileIcon,
  Picture,
  FileDown,
  BarChart3
} from 'lucide-react';

import CrewAIJournalCreator from '../journal/CrewAIJournalCreator';
import CrewAIWorkflowProgress from '../journal/CrewAIWorkflowProgress';

interface ProjectFile {
  name: string;
  type: 'journal' | 'lead_magnet' | 'pdf' | 'media' | 'research' | 'config';
  size: number;
  created_at: string;
  path: string;
}

interface ProjectDetail {
  id: string;
  title: string;
  theme: string;
  status: string;
  created_at: string;
  files: ProjectFile[];
  project_directory?: string;
  workflow_id?: string;
  crewai_preferences?: any;
}

interface CrewAIProjectDetailProps {
  projectId: string;
  onClose?: () => void;
}

const CrewAIProjectDetail: React.FC<CrewAIProjectDetailProps> = ({
  projectId,
  onClose
}) => {
  const navigate = useNavigate();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreatorOpen, setIsCreatorOpen] = useState(false);
  const [workflowData, setWorkflowData] = useState<any>(null);

  // Analyze project state to determine available actions
  const analyzeProjectState = useCallback((files: ProjectFile[]) => {
    const fileTypes = new Set(files.map(f => f.type));
    const hasJournal = fileTypes.has('journal');
    const hasPDF = fileTypes.has('pdf');
    const hasMedia = fileTypes.has('media');
    const hasResearch = fileTypes.has('research');
    const hasConfig = fileTypes.has('config');

    // Determine what's missing
    const missing = [];
    if (!hasResearch) missing.push('research');
    if (!hasJournal) missing.push('content');
    if (!hasMedia) missing.push('media');
    if (!hasPDF) missing.push('pdf');

    return {
      isComplete: missing.length === 0,
      missing,
      fileTypes: Array.from(fileTypes),
      hasResearch,
      hasJournal,
      hasMedia,
      hasPDF,
      hasConfig
    };
  }, []);

  const getAvailableActions = useCallback((state: ReturnType<typeof analyzeProjectState>) => {
    const actions = [];

    // If project is incomplete, offer to continue from where it left off
    if (!state.isComplete) {
      if (!state.hasResearch) {
        actions.push({
          id: 'continue_research',
          title: 'Continue Research',
          description: 'Complete theme research and gather insights',
          icon: Search,
          color: 'blue',
          priority: 1
        });
      }

      if (state.hasResearch && !state.hasJournal) {
        actions.push({
          id: 'continue_content',
          title: 'Generate Content',
          description: 'Create 30-day journal and lead magnet content',
          icon: FileText,
          color: 'purple',
          priority: 2
        });
      }

      if (state.hasJournal && !state.hasMedia) {
        actions.push({
          id: 'generate_media',
          title: 'Generate Media',
          description: 'Create images and visual assets for the journal',
          icon: Image,
          color: 'pink',
          priority: 3
        });
      }

      if ((state.hasJournal || state.hasMedia) && !state.hasPDF) {
        actions.push({
          id: 'generate_pdf',
          title: 'Create PDF',
          description: 'Generate professional PDF documents',
          icon: Download,
          color: 'green',
          priority: 4
        });
      }
    }

    // If project is complete, offer additional actions
    if (state.isComplete) {
      actions.push({
        id: 'regenerate_media',
        title: 'Regenerate Media',
        description: 'Create new images with different styles',
        icon: Image,
        color: 'orange',
        priority: 2
      });

      actions.push({
        id: 'create_pdf_variant',
        title: 'Create PDF Variant',
        description: 'Generate different PDF format or style',
        icon: FileDown,
        color: 'indigo',
        priority: 3
      });

      actions.push({
        id: 'export_content',
        title: 'Export Content',
        description: 'Export raw content for further editing',
        icon: FolderOpen,
        color: 'gray',
        priority: 4
      });
    }

    return actions.sort((a, b) => a.priority - b.priority);
  }, []);

  // Fetch project details
  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        const token = localStorage.getItem('access_token');

        // First try to get project from the library API
        const libraryResponse = await fetch(
          `${getApiURL()}/api/library/llm-projects`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );

        if (libraryResponse.ok) {
          const libraryData = await libraryResponse.json();
          const projectData = libraryData.projects?.find((p: any) =>
            p.id === projectId || p.project_id === projectId
          );

          if (projectData) {
            // Transform the project data to our format
            const transformedProject: ProjectDetail = {
              id: projectData.id || projectData.project_id,
              title: projectData.title || projectData.project_title,
              theme: projectData.theme || 'Unknown',
              status: projectData.status || 'unknown',
              created_at: projectData.created_at || new Date().toISOString(),
              files: projectData.files || [],
              project_directory: projectData.project_directory,
              workflow_id: projectData.workflow_id,
              crewai_preferences: projectData.crewai_preferences
            };

            setProject(transformedProject);
          } else {
            throw new Error('Project not found');
          }
        } else {
          throw new Error('Failed to fetch project details');
        }
      } catch (err) {
        console.error('Error fetching project details:', err);
        setError('Failed to load project details. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjectDetails();
  }, [projectId]);

  const handleAction = async (action: any) => {
    console.log('Handling action:', action.id);

    switch (action.id) {
      case 'continue_research':
      case 'continue_content':
      case 'generate_media':
      case 'generate_pdf':
        // Continue CrewAI workflow from where it left off
        if (project?.crewai_preferences) {
          setIsCreatorOpen(true);
        }
        break;

      case 'regenerate_media':
        // Start new media generation workflow
        if (project) {
          // Create media generation workflow with existing project data
          startWorkflow('media_generation', project);
        }
        break;

      case 'create_pdf_variant':
        // Start PDF generation workflow
        if (project) {
          startWorkflow('pdf_generation', project);
        }
        break;

      case 'export_content':
        // Export raw content for download
        exportContent();
        break;

      default:
        console.warn('Unknown action:', action.id);
    }
  };

  const startWorkflow = (workflowType: string, projectData: ProjectDetail) => {
    // Create workflow data based on project state and action
    const workflowPrefs = {
      ...projectData.crewai_preferences,
      action: workflowType,
      project_directory: projectData.project_directory,
      existing_files: projectData.files
    };

    // Start the CrewAI workflow with continuation data
    setWorkflowData({
      action: workflowType,
      projectId: projectData.id,
      preferences: workflowPrefs
    });

    setIsCreatorOpen(true);
  };

  const exportContent = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${getApiURL()}/api/export/content/${projectId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${project?.title}_content.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Error exporting content:', err);
      setError('Failed to export content. Please try again.');
    }
  };

  const handleCreatorComplete = (result: any) => {
    console.log('Creator workflow completed:', result);
    setIsCreatorOpen(false);
    // Refresh project data
    window.location.reload();
  };

  const handleCreatorError = (error: string) => {
    console.error('Creator workflow error:', error);
    setError(error);
    setIsCreatorOpen(false);
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'journal': return FileText;
      case 'pdf': return FileIcon;
      case 'media': return Picture;
      case 'research': return Brain;
      case 'config': return Book;
      default: return FileIcon;
    }
  };

  const getFileColor = (type: string) => {
    switch (type) {
      case 'journal': return 'text-blue-600';
      case 'pdf': return 'text-red-600';
      case 'media': return 'text-pink-600';
      case 'research': return 'text-purple-600';
      case 'config': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading project details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Project</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.history.back()}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Project Not Found</h2>
          <p className="text-gray-600 mb-4">The requested project could not be found.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const projectState = analyzeProjectState(project.files);
  const availableActions = getAvailableActions(projectState);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.history.back()}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">{project.title}</h1>
                  <p className="text-sm text-gray-600">{project.theme}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                projectState.isComplete
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {projectState.isComplete ? 'Complete' : 'In Progress'}
              </div>
              <div className="text-sm text-gray-500">
                Created {new Date(project.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Project Info & Actions */}
          <div className="lg:col-span-2 space-y-6">
            {/* Project Status */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Status</h2>

              <div className="space-y-4">
                {/* Progress Overview */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Completion Progress</span>
                    <span className="text-sm font-bold text-gray-900">
                      {projectState.isComplete ? '100%' : `${Math.round((projectState.fileTypes.length / 6) * 100)}%`}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        projectState.isComplete ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{ width: projectState.isComplete ? '100%' : `${(projectState.fileTypes.length / 6) * 100}%` }}
                    />
                  </div>
                </div>

                {/* File Types */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Generated Components</h3>
                  <div className="grid grid-cols-3 gap-3">
                    {['research', 'content', 'media', 'pdf', 'config'].map((type) => {
                      const Icon = getFileIcon(type);
                      const hasType = projectState.fileTypes.includes(type);
                      return (
                        <div
                          key={type}
                          className={`flex flex-col items-center p-3 rounded-lg border ${
                            hasType ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50'
                          }`}
                        >
                          <Icon className={`w-6 h-6 mb-2 ${hasType ? 'text-green-600' : 'text-gray-400'}`} />
                          <span className={`text-xs font-medium capitalize ${
                            hasType ? 'text-green-800' : 'text-gray-600'
                          }`}>
                            {type.replace('_', ' ')}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Available Actions */}
                {availableActions.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Available Actions</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {availableActions.map((action) => {
                        const Icon = action.icon;
                        return (
                          <button
                            key={action.id}
                            onClick={() => handleAction(action)}
                            className={`flex items-center space-x-3 p-4 border rounded-lg hover:border-${action.color}-300 hover:bg-${action.color}-50 transition-colors text-left`}
                          >
                            <div className={`w-10 h-10 rounded-lg bg-${action.color}-100 flex items-center justify-center`}>
                              <Icon className={`w-5 h-5 text-${action.color}-600`} />
                            </div>
                            <div>
                              <div className="font-medium text-gray-900">{action.title}</div>
                              <div className="text-sm text-gray-600">{action.description}</div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Project Files */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Files</h2>

              {project.files.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FileIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p>No files generated yet</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {project.files.map((file, index) => {
                    const Icon = getFileIcon(file.type);
                    return (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                      >
                        <div className="flex items-center space-x-3">
                          <Icon className={`w-5 h-5 ${getFileColor(file.type)}`} />
                          <div>
                            <div className="font-medium text-gray-900">{file.name}</div>
                            <div className="text-sm text-gray-500 capitalize">{file.type}</div>
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatFileSize(file.size)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Info */}
          <div className="space-y-6">
            {/* CrewAI Team Status */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">CrewAI Team Status</h2>

              <div className="space-y-4">
                {/* Agent Status Overview */}
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      projectState.hasResearch ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      <Search className={`w-4 h-4 ${projectState.hasResearch ? 'text-green-600' : 'text-gray-400'}`} />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Research Agent</div>
                      <div className="text-sm text-gray-600">
                        {projectState.hasResearch ? 'Research completed' : 'Research pending'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      projectState.hasJournal ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      <FileText className={`w-4 h-4 ${projectState.hasJournal ? 'text-green-600' : 'text-gray-400'}`} />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Content Curator</div>
                      <div className="text-sm text-gray-600">
                        {projectState.hasJournal ? 'Content created' : 'Content pending'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      projectState.hasMedia ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      <Edit3 className={`w-4 h-4 ${projectState.hasMedia ? 'text-green-600' : 'text-gray-400'}`} />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Editor Agent</div>
                      <div className="text-sm text-gray-600">
                        {projectState.hasMedia ? 'Editing complete' : 'Editing pending'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      projectState.hasPDF ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      <Download className={`w-4 h-4 ${projectState.hasPDF ? 'text-green-600' : 'text-gray-400'}`} />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">PDF Builder</div>
                      <div className="text-sm text-gray-600">
                        {projectState.hasPDF ? 'PDF generated' : 'PDF pending'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      projectState.hasConfig ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      <Book className={`w-4 h-4 ${projectState.hasConfig ? 'text-green-600' : 'text-gray-400'}`} />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Media Agent</div>
                      <div className="text-sm text-gray-600">
                        {projectState.hasConfig ? 'Configuration complete' : 'Configuration pending'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Project Info */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h2>

              <div className="space-y-3">
                <div>
                  <div className="text-sm text-gray-600">Project ID</div>
                  <div className="font-medium text-gray-900 font-mono text-xs">
                    {project.id}
                  </div>
                </div>

                {project.project_directory && (
                  <div>
                    <div className="text-sm text-gray-600">Project Directory</div>
                    <div className="font-medium text-gray-900 font-mono text-xs">
                      {project.project_directory}
                    </div>
                  </div>
                )}

                <div>
                  <div className="text-sm text-gray-600">Theme</div>
                  <div className="font-medium text-gray-900">{project.theme}</div>
                </div>

                <div>
                  <div className="text-sm text-gray-600">Status</div>
                  <div className="font-medium text-gray-900">{project.status}</div>
                </div>

                <div>
                  <div className="text-sm text-gray-600">Created</div>
                  <div className="font-medium text-gray-900">
                    {new Date(project.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CrewAI Workflow Modals */}
      {isCreatorOpen && (
        <CrewAIJournalCreator
          isOpen={isCreatorOpen}
          onComplete={handleCreatorComplete}
          onError={handleCreatorError}
          onClose={() => setIsCreatorOpen(false)}
        />
      )}

      {workflowData && (
        <CrewAIWorkflowProgress
          workflowId={workflowData.workflow_id || 'temp-workflow'}
          projectId={projectId}
          onComplete={handleCreatorComplete}
          onError={handleCreatorError}
          onClose={() => {
            setIsCreatorOpen(false);
            setWorkflowData(null);
          }}
        />
      )}
    </div>
  );
};

export default CrewAIProjectDetail;