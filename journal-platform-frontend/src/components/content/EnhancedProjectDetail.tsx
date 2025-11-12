/**
 * Enhanced Project Detail Component
 * Shows journal content with AI analysis, enhancement studio, and workflow integration
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  BookOpen,
  Download,
  Eye,
  Calendar,
  FileText,
  Image,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  Sparkles,
  Zap,
  Target,
  BarChart3,
  Edit3,
  RefreshCw,
  Play,
  Pause,
  Settings,
  AlertTriangle,
  Star,
  Hash,
  FolderOpen,
  Activity
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/Tabs';
import CrewAIWorkflowProgress from '../projects/CrewAIWorkflowProgress';

interface Project {
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
    research_depth: number;
    content_structure: number;
    visual_appeal: number;
    presentation_quality: number;
    overall_quality: number;
  };
  completionMap: {
    research_agent: number;
    content_curator_agent: number;
    editor_agent: number;
    media_agent: number;
    pdf_builder_agent: number;
  };
  recommendations: Array<{
    id: string;
    type: string;
    priority: 'high' | 'medium' | 'low';
    title: string;
    description: string;
    agents: string[];
    estimated_time: number;
    impact_score: number;
  }>;
  enhancementPotential: number;
  missingComponents: string[];
  existingFiles: Array<{
    name: string;
    type: string;
    size: number;
  }>;
}

interface ActiveWorkflow {
  workflowId: string;
  type: string;
  status: string;
  progress: number;
  agents: string[];
  estimatedTimeRemaining?: number;
}

interface EnhancedProjectDetailProps {
  projectId: number;
  onBack: () => void;
}

const EnhancedProjectDetail: React.FC<EnhancedProjectDetailProps> = ({
  projectId,
  onBack
}) => {
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [activeWorkflow, setActiveWorkflow] = useState<ActiveWorkflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [selectedRecommendations, setSelectedRecommendations] = useState<string[]>([]);
  const [currentTab, setCurrentTab] = useState('content');

  // Fetch project details and analysis
  useEffect(() => {
    fetchProjectDetails();
  }, [projectId]);

  const fetchProjectDetails = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      // Fetch project details
      const projectResponse = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/projects/${projectId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (projectResponse.ok) {
        const projectData = await projectResponse.json();
        setProject(projectData);
      }

      // Fetch AI analysis
      await fetchProjectAnalysis();

    } catch (error) {
      console.error('Error fetching project details:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectAnalysis = async () => {
    try {
      setLoadingAnalysis(true);
      const token = localStorage.getItem('access_token');

      const analysisResponse = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/journal-content/analyze-project/${projectId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        setAnalysis(analysisData.analysis);
      }

    } catch (error) {
      console.error('Error fetching project analysis:', error);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const handleEnhanceProject = async (enhancementType: string, recommendationId?: string) => {
    try {
      const token = localStorage.getItem('access_token');

      const requestBody: any = {
        project_id: projectId,
        enhancement_type: enhancementType
      };

      if (recommendationId) {
        requestBody.selected_recommendations = [recommendationId];
      }

      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/journal-content/enhance-project`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(requestBody)
        }
      );

      if (response.ok) {
        const workflowData = await response.json();
        setActiveWorkflow({
          workflowId: workflowData.workflow_id,
          type: enhancementType,
          status: 'started',
          progress: 0,
          agents: [],
          estimatedTimeRemaining: workflowData.estimated_time
        });

        // Switch to workflow tab
        setCurrentTab('workflow');
      } else {
        throw new Error('Failed to start enhancement workflow');
      }

    } catch (error) {
      console.error('Error starting enhancement:', error);
    }
  };

  const handleQuickEnhance = async (enhancementType: string) => {
    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/journal-content/quick-enhance/${projectId}?enhancement_type=${enhancementType}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const workflowData = await response.json();
        setActiveWorkflow({
          workflowId: workflowData.workflow_id,
          type: enhancementType,
          status: 'started',
          progress: 0,
          agents: [],
          estimatedTimeRemaining: 10 // Default for quick enhancements
        });

        setCurrentTab('workflow');
      }

    } catch (error) {
      console.error('Error starting quick enhancement:', error);
    }
  };

  const handleWorkflowComplete = (result: any) => {
    setActiveWorkflow(null);
    // Refresh analysis to see the improvements
    fetchProjectAnalysis();
  };

  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAgentIcon = (agentType: string) => {
    switch (agentType) {
      case 'research_agent': return <Search className="w-5 h-5" />;
      case 'content_curator_agent': return <FileText className="w-5 h-5" />;
      case 'editor_agent': return <Edit3 className="w-5 h-5" />;
      case 'media_agent': return <Image className="w-5 h-5" />;
      case 'pdf_builder_agent': return <Download className="w-5 h-5" />;
      default: return <Zap className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Loading project details...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-4" />
          <p>Project not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={onBack}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </Button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{project.title}</h1>
                <p className="text-sm text-gray-600">{project.description}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {analysis && (
                <Button
                  onClick={() => fetchProjectAnalysis()}
                  disabled={loadingAnalysis}
                  variant="outline"
                  size="sm"
                  className="flex items-center space-x-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loadingAnalysis ? 'animate-spin' : ''}`} />
                  <span>Refresh Analysis</span>
                </Button>
              )}
              <Button
                onClick={() => handleEnhanceProject('improve_quality')}
                className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700"
              >
                <Sparkles className="w-4 h-4" />
                <span>Enhance Content</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-3">
            <Tabs value={currentTab} onValueChange={setCurrentTab}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="content">Content</TabsTrigger>
                <TabsTrigger value="analysis">Analysis</TabsTrigger>
                <TabsTrigger value="enhance">Enhance</TabsTrigger>
                <TabsTrigger value="workflow">AI Workflow</TabsTrigger>
              </TabsList>

              {/* Content Tab */}
              <TabsContent value="content" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Journal Content</CardTitle>
                    <CardDescription>View and manage your journal content files</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* File list */}
                      {analysis?.existingFiles?.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            {getAgentIcon(file.type)}
                            <div>
                              <p className="font-medium">{file.name}</p>
                              <p className="text-sm text-gray-500">{file.type}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-sm text-gray-500">
                              {(file.size / 1024).toFixed(1)} KB
                            </span>
                            <Button variant="outline" size="sm">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button variant="outline" size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Analysis Tab */}
              <TabsContent value="analysis" className="mt-6">
                {analysis ? (
                  <div className="space-y-6">
                    {/* Quality Scores */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Quality Assessment</CardTitle>
                        <CardDescription>AI-powered quality analysis of your journal content</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {Object.entries(analysis.qualityScores).map(([key, value]) => (
                            <div key={key} className="text-center">
                              <div className={`text-2xl font-bold ${getQualityColor(value)}`}>
                                {value}%
                              </div>
                              <div className="text-sm text-gray-600 capitalize">
                                {key.replace('_', ' ')}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Agent Completion */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Agent Contributions</CardTitle>
                        <CardDescription>Which CrewAI agents have contributed to this project</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {Object.entries(analysis.completionMap).map(([agent, percentage]) => (
                            <div key={agent} className="flex items-center space-x-4">
                              {getAgentIcon(agent)}
                              <div className="flex-1">
                                <div className="flex justify-between text-sm mb-1">
                                  <span className="capitalize">{agent.replace('_', ' ')}</span>
                                  <span>{percentage}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-blue-600 h-2 rounded-full"
                                    style={{ width: `${percentage}%` }}
                                  />
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">No analysis available yet</p>
                      <Button onClick={fetchProjectAnalysis} disabled={loadingAnalysis}>
                        {loadingAnalysis ? 'Analyzing...' : 'Run Analysis'}
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Enhancement Tab */}
              <TabsContent value="enhance" className="mt-6">
                {analysis?.recommendations ? (
                  <div className="space-y-4">
                    {analysis.recommendations.map((recommendation) => (
                      <Card key={recommendation.id}>
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h3 className="font-semibold">{recommendation.title}</h3>
                                <span className={`text-xs px-2 py-1 rounded-full ${
                                  recommendation.priority === 'high'
                                    ? 'bg-red-100 text-red-700'
                                    : recommendation.priority === 'medium'
                                    ? 'bg-yellow-100 text-yellow-700'
                                    : 'bg-green-100 text-green-700'
                                }`}>
                                  {recommendation.priority} priority
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 mb-3">{recommendation.description}</p>
                              <div className="flex items-center space-x-4 text-sm text-gray-500">
                                <div className="flex items-center space-x-1">
                                  <Clock className="w-4 h-4" />
                                  <span>{recommendation.estimated_time} min</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <Star className="w-4 h-4" />
                                  <span>Impact: {recommendation.impact_score}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <Users className="w-4 h-4" />
                                  <span>{recommendation.agents.length} agents</span>
                                </div>
                              </div>
                            </div>
                            <Button
                              onClick={() => handleEnhanceProject('custom', recommendation.id)}
                              size="sm"
                              className="bg-purple-600 hover:bg-purple-700"
                            >
                              Apply Enhancement
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">No enhancement recommendations available</p>
                      <Button onClick={() => handleQuickEnhance('improve_quality')}>
                        Quick Enhancement
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Workflow Tab */}
              <TabsContent value="workflow" className="mt-6">
                {activeWorkflow ? (
                  <Card>
                    <CardHeader>
                      <CardTitle>AI Enhancement Workflow</CardTitle>
                      <CardDescription>
                        Track your AI enhancement progress in real-time
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CrewAIWorkflowProgress
                        workflowId={activeWorkflow.workflowId}
                        onComplete={handleWorkflowComplete}
                      />
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">No active AI workflows</p>
                      <div className="space-y-2">
                        <Button onClick={() => handleQuickEnhance('add_images')}>
                          Add Images
                        </Button>
                        <Button onClick={() => handleQuickEnhance('improve_writing')} variant="outline">
                          Improve Writing
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-6">
              {/* Project Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Project Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">Created: {project.creationDate}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">Modified: {project.lastModified}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Hash className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">Theme: {project.theme}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">{project.pageCount} pages</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FolderOpen className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">{project.fileSize}</span>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button
                    onClick={() => handleQuickEnhance('add_images')}
                    variant="outline"
                    className="w-full justify-start"
                  >
                    <Image className="w-4 h-4 mr-2" />
                    Add Images
                  </Button>
                  <Button
                    onClick={() => handleQuickEnhance('improve_writing')}
                    variant="outline"
                    className="w-full justify-start"
                  >
                    <Edit3 className="w-4 h-4 mr-2" />
                    Improve Writing
                  </Button>
                  <Button
                    onClick={() => handleQuickEnhance('expand_content')}
                    variant="outline"
                    className="w-full justify-start"
                  >
                    <BookOpen className="w-4 h-4 mr-2" />
                    Expand Content
                  </Button>
                  <Button
                    onClick={() => handleQuickEnhance('create_pdf')}
                    variant="outline"
                    className="w-full justify-start"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Create PDF
                  </Button>
                </CardContent>
              </Card>

              {/* Enhancement Potential */}
              {analysis && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Enhancement Potential</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600 mb-2">
                        {analysis.enhancementPotential}%
                      </div>
                      <p className="text-sm text-gray-600">Overall enhancement opportunity</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedProjectDetail;