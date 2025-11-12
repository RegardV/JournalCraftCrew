/**
 * Enhanced Journal Card Component
 * Shows AI analysis insights and contextual action buttons
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from '../ui/Card';
import { Button } from '../ui/Button';
import {
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
  MoreHorizontal,
  Heart,
  Share2,
  Edit3
} from 'lucide-react';

interface JournalContent {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'incomplete' | 'enhanceable';
  creationDate: string;
  fileSize: string;
  pageCount: number;
  theme?: string;
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
}

interface EnhancedJournalCardProps {
  content: JournalContent;
  analysis?: AIAnalysis;
  onSelect?: (content: JournalContent) => void;
  onPreview?: (content: JournalContent) => void;
  onDownload?: (content: JournalContent) => void;
  onEnhance?: (content: JournalContent, recommendationId?: string) => void;
  onAnalyze?: (content: JournalContent) => void;
  className?: string;
}

const EnhancedJournalCard: React.FC<EnhancedJournalCardProps> = ({
  content,
  analysis,
  onSelect,
  onPreview,
  onDownload,
  onEnhance,
  onAnalyze,
  className = ''
}) => {
  const [showActions, setShowActions] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // Calculate status badge color and text
  const getStatusBadge = () => {
    if (!analysis) return { color: 'bg-gray-100 text-gray-700', text: 'Analyze' };

    const quality = analysis.qualityScores.overall_quality;
    if (quality >= 80) {
      return { color: 'bg-green-100 text-green-700', text: 'High Quality' };
    } else if (quality >= 60) {
      return { color: 'bg-blue-100 text-blue-700', text: 'Good Quality' };
    } else {
      return { color: 'bg-yellow-100 text-yellow-700', text: 'Enhance Available' };
    }
  };

  // Get primary action based on analysis
  const getPrimaryAction = () => {
    if (!analysis) {
      return {
        label: 'Analyze Content',
        icon: BarChart3,
        action: 'analyze',
        color: 'bg-blue-600 hover:bg-blue-700',
        description: 'Get AI insights and recommendations'
      };
    }

    const missingComponents = analysis.missingComponents.length;
    const qualityScore = analysis.qualityScores.overall_quality;
    const potential = analysis.enhancementPotential;

    if (missingComponents > 0) {
      return {
        label: 'Complete Journal',
        icon: CheckCircle,
        action: 'complete',
        color: 'bg-orange-600 hover:bg-orange-700',
        description: `Finish ${missingComponents} missing components`
      };
    } else if (qualityScore < 70) {
      return {
        label: 'Enhance Quality',
        icon: TrendingUp,
        action: 'enhance',
        color: 'bg-purple-600 hover:bg-purple-700',
        description: 'Improve content with AI enhancements'
      };
    } else if (potential > 50) {
      return {
        label: 'AI Variants',
        icon: Sparkles,
        action: 'variant',
        color: 'bg-pink-600 hover:bg-pink-700',
        description: 'Create AI-powered variations'
      };
    } else {
      return {
        label: 'View Content',
        icon: Eye,
        action: 'view',
        color: 'bg-gray-600 hover:bg-gray-700',
        description: 'View journal content and details'
      };
    }
  };

  // Get secondary actions
  const getSecondaryActions = () => {
    const actions = [];

    if (analysis) {
      // Add quick enhancement actions based on recommendations
      const topRecommendations = analysis.recommendations.slice(0, 2);
      topRecommendations.forEach((rec, index) => {
        if (rec.priority === 'high') {
          actions.push({
            label: rec.title,
            icon: Zap,
            action: 'quick_enhance',
            data: { recommendationId: rec.id },
            color: 'bg-gray-100 hover:bg-gray-200 text-gray-700'
          });
        }
      });
    }

    // Add standard actions if there's room
    if (actions.length < 2) {
      actions.push({
        label: 'Download',
        icon: Download,
        action: 'download',
        color: 'bg-gray-100 hover:bg-gray-200 text-gray-700'
      });
    }

    return actions;
  };

  const statusBadge = getStatusBadge();
  const primaryAction = getPrimaryAction();
  const secondaryActions = getSecondaryActions();
  const PrimaryIcon = primaryAction.icon;

  const handlePrimaryAction = () => {
    switch (primaryAction.action) {
      case 'analyze':
        onAnalyze?.(content);
        break;
      case 'complete':
        onEnhance?.(content, 'complete_missing');
        break;
      case 'enhance':
        onEnhance?.(content, 'improve_quality');
        break;
      case 'variant':
        onEnhance?.(content, 'add_variant');
        break;
      case 'view':
      default:
        onSelect?.(content);
        break;
    }
  };

  const handleSecondaryAction = (action: any) => {
    switch (action.action) {
      case 'quick_enhance':
        onEnhance?.(content, action.data.recommendationId);
        break;
      case 'download':
        onDownload?.(content);
        break;
      case 'preview':
        onPreview?.(content);
        break;
      default:
        onSelect?.(content);
        break;
    }
  };

  return (
    <Card className={`hover:shadow-lg transition-shadow cursor-pointer ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 mb-1">
              {content.title}
            </CardTitle>
            <CardDescription className="text-sm text-gray-600 line-clamp-2">
              {content.description}
            </CardDescription>
          </div>

          <div className="flex flex-col items-end space-y-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusBadge.color}`}>
              {statusBadge.text}
            </span>
            {content.theme && (
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                {content.theme}
              </span>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* AI Analysis Insights */}
        {analysis && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">AI Analysis</span>
              </div>
              <span className="text-xs text-blue-700">
                {analysis.qualityScores.overall_quality}% Quality
              </span>
            </div>

            {/* Quality Progress Bar */}
            <div className="mb-3">
              <div className="flex justify-between text-xs text-blue-700 mb-1">
                <span>Overall Quality</span>
                <span>{analysis.qualityScores.overall_quality}%</span>
              </div>
              <div className="w-full bg-blue-100 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${analysis.qualityScores.overall_quality}%` }}
                />
              </div>
            </div>

            {/* Component Completion */}
            {analysis.missingComponents.length > 0 && (
              <div className="text-xs text-blue-800">
                <strong>Missing:</strong> {analysis.missingComponents.join(', ')}
              </div>
            )}

            {/* Enhancement Potential */}
            {analysis.enhancementPotential > 30 && (
              <div className="text-xs text-blue-800 mt-2">
                <strong>Enhancement Potential:</strong> {analysis.enhancementPotential}%
              </div>
            )}
          </div>
        )}

        {/* Project Metadata */}
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <Calendar className="w-4 h-4" />
              <span>{content.creationDate}</span>
            </div>
            <div className="flex items-center space-x-1">
              <FileText className="w-4 h-4" />
              <span>{content.pageCount} pages</span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsFavorite(!isFavorite);
              }}
              className={`p-1 rounded hover:bg-gray-100 transition-colors ${
                isFavorite ? 'text-red-500 fill-current' : 'text-gray-400'
              }`}
            >
              <Heart className="w-4 h-4" />
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowActions(!showActions);
              }}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Primary Action Button */}
        <Button
          onClick={handlePrimaryAction}
          className={`w-full ${primaryAction.color} text-white flex items-center justify-center space-x-2`}
        >
          <PrimaryIcon className="w-4 h-4" />
          <span>{primaryAction.label}</span>
        </Button>

        {/* Secondary Actions */}
        {showActions && secondaryActions.length > 0 && (
          <div className="flex space-x-2">
            {secondaryActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSecondaryAction(action);
                  }}
                  className={`flex-1 ${action.color} border-current`}
                >
                  <Icon className="w-3 h-3 mr-1" />
                  <span className="text-xs">{action.label}</span>
                </Button>
              );
            })}
          </div>
        )}

        {/* Action Description */}
        <p className="text-xs text-gray-500 text-center italic">
          {primaryAction.description}
        </p>
      </CardContent>
    </Card>
  );
};

export default EnhancedJournalCard;