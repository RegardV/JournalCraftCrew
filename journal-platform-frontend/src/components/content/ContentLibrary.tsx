import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  X,
  Download,
  Eye,
  FileText,
  Grid3x3,
  List,
  Search,
  Filter,
  Calendar,
  Tag,
  User,
  ChevronDown,
  ChevronRight,
  MoreVertical,
  Heart,
  Share2,
  FolderOpen,
  Edit,
  Trash2,
  Copy,
  ExternalLink,
  AlertCircle,
  RefreshCw,
  Plus
} from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';
import { journalAPI } from '@/lib/api';
import { getApiURL } from '@/lib/apiConfig';
import UnifiedJournalCreator from '@/components/journal/UnifiedJournalCreator';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

interface ContentItem {
  id: string;
  title: string;
  description: string;
  type: 'journal' | 'pdf' | 'article' | 'notes';
  createdAt: string;
  updatedAt: string;
  author?: string;
  tags: string[];
  filePath?: string;
  downloadUrl?: string;
  thumbnailUrl?: string;
  wordCount?: number;
  pageCount?: number;
  size?: string;
  status: 'completed' | 'processing' | 'draft';
  theme?: string;
  crewGenerated?: boolean;
  favorite?: boolean;
  metadata?: Record<string, any>;
}

interface ContentLibraryProps {
  className?: string;
}

const ContentLibrary: React.FC<ContentLibraryProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { token, isAuthenticated } = useAuth();
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState<'createdAt' | 'title' | 'updatedAt'>('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showPreview, setShowPreview] = useState(false);
  const [pdfDocument, setPdfDocument] = useState<any>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Maintain a list of orphaned items that should be filtered out (persisted in localStorage)
  const [orphanedItemIds, setOrphanedItemIds] = useState<Set<string>>(() => {
    // Start fresh - clear any existing orphaned data since we removed fake data
    localStorage.removeItem('orphanedJournalIds');
    return new Set();
  });

  // Journal creation modal state
  const [isJournalModalOpen, setIsJournalModalOpen] = useState(false);

  // Handle journal creation from ContentLibrary
  const handleJournalCreation = async (preferences: any) => {
    try {
      console.log('Creating journal from ContentLibrary with preferences:', preferences);

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

      const response = await fetch(`${getApiURL()}/api/journals/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formattedPreferences)
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Journal creation started:', data);

        // Handle both jobId and job_id response formats
        const jobId = data.jobId || data.job_id;

        // Close the modal
        setIsJournalModalOpen(false);

        // Navigate to the AI workflow page with the job ID
        navigate(`/ai-workflow?jobId=${jobId}`);

        // Refresh the library to show the new journal
        setTimeout(() => {
          loadJournalLibrary();
        }, 1000);
      } else {
        const errorText = await response.text();
        console.error('Failed to create journal:', errorText);

        if (response.status === 401) {
          alert('Authentication required. Please log in first.');
        } else {
          alert(`Failed to create journal: ${errorText}`);
        }
      }
    } catch (error) {
      console.error('Error creating journal:', error);
      alert('Network error. Please check your connection and try again.');
    }
  };

  // Load journal library data from API
  const loadJournalLibrary = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await journalAPI.getLibrary();

      if (response.projects) {
        // Transform backend projects to ContentItem format
        const transformedContents: ContentItem[] = response.projects
          .filter((project: any) => {
            const projectId = project.id || project.project_id;
            // Filter out items that have been marked as orphaned
            return !orphanedItemIds.has(projectId);
          })
          .map((project: any) => {
            // Extract theme and create more descriptive title/description
            const theme = project.theme || project.preferences?.theme || 'Journaling';
            const titleStyle = project.preferences?.titleStyle || 'Personal Growth';
            const authorStyle = project.preferences?.authorStyle || 'inspirational narrative';
            const researchDepth = project.preferences?.researchDepth || 'medium';

            // Create more descriptive title
            let descriptiveTitle = project.title || project.name;
            if (!descriptiveTitle || descriptiveTitle === 'Untitled Journal') {
              descriptiveTitle = `${theme.charAt(0).toUpperCase() + theme.slice(1)} Journal`;
            }

            // Create more descriptive description
            let descriptiveDescription = project.description;
            if (!descriptiveDescription || descriptiveDescription === 'Generated journal content') {
              descriptiveDescription = `A comprehensive ${researchDepth} journal focused on ${theme.toLowerCase()}, created with ${titleStyle} style and ${authorStyle} tone.`;
            }

            return {
              id: project.id || project.project_id,
              title: descriptiveTitle,
              description: descriptiveDescription,
              type: 'journal' as const,
              createdAt: project.created_at || project.date_created || new Date().toISOString(),
              updatedAt: project.updated_at || project.last_modified || project.created_at || new Date().toISOString(),
              author: 'AI Content Team',
              tags: project.tags || [theme.toLowerCase(), 'ai-generated', titleStyle.toLowerCase()],
              filePath: project.main_file || project.file_path,
              downloadUrl: project.main_file ? `${getApiURL()}/api/journals/${project.id}/download/${project.main_file}` : undefined,
              wordCount: project.word_count,
              pageCount: project.page_count,
              size: project.file_size || 'Unknown',
              status: project.status === 'completed' ? 'completed' : 'processing' as const,
              theme: theme,
              crewGenerated: true,
              favorite: false,
              metadata: {
                theme: theme,
                titleStyle: titleStyle,
                authorStyle: authorStyle,
                researchDepth: researchDepth,
                project_id: project.id,
                files: project.files || [],
                generation_time: project.generation_time,
                crew_agents: project.crew_agents || ['Research Specialist', 'Content Curator', 'Editor', 'PDF Builder'],
                preferences: project.preferences || {}
              }
            };
          });

        setContents(transformedContents);
      } else {
        setError('Failed to load journal library');
      }
    } catch (error) {
      console.error('Error loading journal library:', error);
      setError(error instanceof Error ? error.message : 'Failed to load journal library');
    } finally {
      setLoading(false);
    }
  };

  // Refresh library data
  const refreshLibrary = async () => {
    setRefreshing(true);
    await loadJournalLibrary();
    setRefreshing(false);
  };

  // Initial load
  useEffect(() => {
    loadJournalLibrary();
  }, []);

  const loadPdf = async (url: string) => {
    try {
      const loadingTask = pdfjsLib.getDocument(url);
      const pdf = await loadingTask.promise;
      setPdfDocument(pdf);
      setTotalPages(pdf.numPages);
      setCurrentPage(1);
      renderPage(pdf, 1);
    } catch (error) {
      console.error('Error loading PDF:', error);
    }
  };

  const renderPage = async (pdf: any, pageNumber: number) => {
    if (!canvasRef.current) return;

    try {
      const page = await pdf.getPage(pageNumber);
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      const viewport = page.getViewport({ scale: 1.5 });
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      const renderContext = {
        canvasContext: context!,
        viewport: viewport
      };

      await page.render(renderContext).promise;
    } catch (error) {
      console.error('Error rendering page:', error);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      if (pdfDocument) {
        renderPage(pdfDocument, newPage);
      }
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      if (pdfDocument) {
        renderPage(pdfDocument, newPage);
      }
    }
  };

  const filteredContents = contents.filter(content => {
    const matchesSearch = content.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         content.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTags = selectedTags.length === 0 ||
                       selectedTags.some(tag => content.tags.includes(tag));
    return matchesSearch && matchesTags;
  }).sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];
    const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  const allTags = Array.from(new Set(contents.flatMap(content => content.tags)));

  const handlePreview = (content: ContentItem) => {
    setSelectedItem(content);
    setShowPreview(true);
    if (content.downloadUrl) {
      loadPdf(content.downloadUrl);
    }
  };

  const handleDownload = async (content: ContentItem) => {
    if (!content.downloadUrl) {
      alert('Download not available for this item');
      return;
    }

    try {
      // Add authentication token to download URL
      const token = localStorage.getItem('access_token');
      const downloadUrl = new URL(content.downloadUrl);
      if (token) {
        downloadUrl.searchParams.set('token', token);
      }

      // Create download link
      const link = document.createElement('a');
      link.href = downloadUrl.toString();
      link.download = `${content.title}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file. Please try again.');
    }
  };

  const toggleFavorite = (contentId: string) => {
    setContents(prev => prev.map(content =>
      content.id === contentId
        ? { ...content, favorite: !content.favorite }
        : content
    ));
  };

  const handleDeleteContent = async (contentId: string, contentTitle: string) => {
    if (window.confirm(`Are you sure you want to delete "${contentTitle}"? This action cannot be undone.`)) {
      try {
        // Use the universal delete endpoint that handles all project ID formats
        const deleteUrl = `${getApiURL()}/api/library/projects/${contentId}`;

        const response = await fetch(deleteUrl, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (response.ok) {
          // Remove from local state
          setContents(prev => prev.filter(content => content.id !== contentId));
          alert('Journal deleted successfully');
        } else if (response.status === 404) {
          // Project not found in backend - mark as orphaned and remove from UI
          console.log(`Project ${contentId} not found in backend, marking as orphaned`);
          const newOrphanedIds = new Set(orphanedItemIds).add(contentId);
          setOrphanedItemIds(newOrphanedIds);
          localStorage.setItem('orphanedJournalIds', JSON.stringify([...newOrphanedIds]));
          setContents(prev => prev.filter(content => content.id !== contentId));
          alert('Journal removed from library (content was already missing)');
        } else {
          const error = await response.json();
          alert(`Failed to delete journal: ${error.detail || 'Unknown error'}`);
        }
      } catch (error) {
        console.error('Delete error:', error);
        // For network errors, still try to remove from UI if it's a 404-like situation
        if (error.message && error.message.includes('404')) {
          const newOrphanedIds = new Set(orphanedItemIds).add(contentId);
          setOrphanedItemIds(newOrphanedIds);
          localStorage.setItem('orphanedJournalIds', JSON.stringify([...newOrphanedIds]));
          setContents(prev => prev.filter(content => content.id !== contentId));
          alert('Journal removed from library (content was already missing)');
        } else {
          alert('Failed to delete journal. Please try again.');
        }
      }
    }
  };

  const ContentCard = ({ content }: { content: ContentItem }) => (
    <div className="bg-white rounded-lg border border-gray-200 hover:border-indigo-300 hover:shadow-lg transition-all duration-200 p-4 cursor-pointer group">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
            content.type === 'journal' ? 'bg-blue-100' :
            content.type === 'pdf' ? 'bg-red-100' : 'bg-gray-100'
          }`}>
            <FileText className={`w-4 h-4 ${
              content.type === 'journal' ? 'text-blue-600' :
              content.type === 'pdf' ? 'text-red-600' : 'text-gray-600'
            }`} />
          </div>
          <div>
            <h3 className="font-medium text-gray-900 group-hover:text-indigo-600 line-clamp-1">
              {content.title}
            </h3>
            <p className="text-sm text-gray-500">
              {content.author || 'Unknown Author'}
            </p>
            {content.metadata?.theme && (
              <p className="text-xs text-indigo-600 font-medium capitalize">
                Theme: {content.metadata.theme}
              </p>
            )}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            toggleFavorite(content.id);
          }}
          className="p-1 rounded-full hover:bg-gray-100 transition-colors"
        >
          <Heart className={`w-4 h-4 ${
            content.favorite ? 'fill-red-500 text-red-500' : 'text-gray-400'
          }`} />
        </button>
      </div>

      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {content.description}
      </p>

      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-4 text-xs text-gray-500">
          {content.wordCount && (
            <span>{content.wordCount.toLocaleString()} words</span>
          )}
          {content.pageCount && (
            <span>{content.pageCount} pages</span>
          )}
          {content.size && (
            <span>{content.size}</span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {content.status === 'processing' && (
            <div className="flex items-center space-x-1 text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>Processing</span>
            </div>
          )}
          {content.status === 'completed' && (
            <div className="flex items-center space-x-1 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
              <span>Completed</span>
            </div>
          )}
          {content.crewGenerated && (
            <div className="flex items-center space-x-1 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
              <span>CrewAI</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {content.tags.slice(0, 3).map(tag => (
          <span
            key={tag}
            className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
          >
            {tag}
          </span>
        ))}
        {content.tags.length > 3 && (
          <span className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
            +{content.tags.length - 3}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-500">
          {new Date(content.createdAt).toLocaleDateString()}
        </span>
        <div className="flex items-center space-x-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handlePreview(content);
            }}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
            title="Preview"
          >
            <Eye className="w-4 h-4 text-gray-600" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDownload(content);
            }}
            className="p-1 rounded hover:bg-gray-100 transition-colors"
            title="Download"
          >
            <Download className="w-4 h-4 text-gray-600" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteContent(content.id, content.title);
            }}
            className="p-1 rounded hover:bg-red-100 hover:text-red-600 transition-colors"
            title="Delete journal"
          >
            <Trash2 className="w-4 h-4 text-gray-600 hover:text-red-600" />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Content Library</h2>
          <p className="text-gray-600">
            {loading ? 'Loading your journals...' : `Manage and organize ${contents.length} journal${contents.length !== 1 ? 's' : ''}`}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsJournalModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create New Journal
          </button>
          <button
            onClick={refreshLibrary}
            disabled={refreshing}
            className="p-2 rounded-lg transition-colors text-gray-400 hover:text-gray-600 disabled:opacity-50"
            title="Refresh library"
          >
            <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'grid'
                ? 'bg-indigo-100 text-indigo-600'
                : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Grid3x3 className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list'
                ? 'bg-indigo-100 text-indigo-600'
                : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <List className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${
              showFilters ? 'rotate-180' : ''
            }`} />
          </button>
        </div>

        {showFilters && (
          <div className="space-y-4 pt-4 border-t border-gray-200">
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="createdAt">Created Date</option>
                  <option value="title">Title</option>
                  <option value="updatedAt">Updated Date</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Order
                </label>
                <select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="desc">Newest First</option>
                  <option value="asc">Oldest First</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {allTags.map(tag => (
                  <button
                    key={tag}
                    onClick={() => {
                      if (selectedTags.includes(tag)) {
                        setSelectedTags(prev => prev.filter(t => t !== tag));
                      } else {
                        setSelectedTags(prev => [...prev, tag]);
                      }
                    }}
                    className={`px-3 py-1 rounded-full text-sm transition-colors ${
                      selectedTags.includes(tag)
                        ? 'bg-indigo-100 text-indigo-700'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Content Grid/List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <RefreshCw className="w-8 h-8 text-gray-400 animate-spin" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Loading your journals</h3>
          <p className="text-gray-600">Please wait while we fetch your content...</p>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading content</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={refreshLibrary}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        </div>
      ) : filteredContents.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No content found</h3>
          <p className="text-gray-600 mb-4">
            {searchQuery || selectedTags.length > 0
              ? 'Try adjusting your search or filters'
              : 'Create your first journal to get started'
            }
          </p>
          {!searchQuery && selectedTags.length === 0 && (
            <button
              onClick={() => setIsJournalModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors mx-auto"
            >
              <Plus className="w-4 h-4" />
              Create New Journal
            </button>
          )}
        </div>
      ) : (
        <div className={
          viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
        }>
          {filteredContents.map(content => (
            <div key={content.id} onClick={() => {
              console.log('Navigating to project detail for ID:', content.id)
              navigate(`/library/projects/${content.id}`)
            }}>
              <ContentCard content={content} />
            </div>
          ))}
        </div>
      )}

      {/* PDF Preview Modal */}
      {showPreview && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{selectedItem.title}</h3>
                <p className="text-sm text-gray-600">{selectedItem.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleDownload(selectedItem)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Download"
                >
                  <Download className="w-5 h-5 text-gray-600" />
                </button>
                <button
                  onClick={() => setShowPreview(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-600" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-hidden flex">
              <div className="flex-1 overflow-auto p-6">
                {selectedItem.downloadUrl ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={handlePreviousPage}
                          disabled={currentPage <= 1}
                          className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronRight className="w-4 h-4 rotate-180" />
                        </button>
                        <span className="text-sm text-gray-600">
                          Page {currentPage} of {totalPages}
                        </span>
                        <button
                          onClick={handleNextPage}
                          disabled={currentPage >= totalPages}
                          className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="flex justify-center">
                      <canvas
                        ref={canvasRef}
                        className="border border-gray-300 shadow-lg"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">Preview not available for this content</p>
                      <button
                        onClick={() => handleDownload(selectedItem)}
                        className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        Download Instead
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="w-80 border-l border-gray-200 p-6 bg-gray-50">
                <h4 className="font-semibold text-gray-900 mb-4">Content Details</h4>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-600">Type</label>
                    <p className="font-medium capitalize">{selectedItem.type}</p>
                  </div>
                  {selectedItem.author && (
                    <div>
                      <label className="text-sm text-gray-600">Author</label>
                      <p className="font-medium">{selectedItem.author}</p>
                    </div>
                  )}
                  {selectedItem.wordCount && (
                    <div>
                      <label className="text-sm text-gray-600">Word Count</label>
                      <p className="font-medium">{selectedItem.wordCount.toLocaleString()}</p>
                    </div>
                  )}
                  {selectedItem.pageCount && (
                    <div>
                      <label className="text-sm text-gray-600">Page Count</label>
                      <p className="font-medium">{selectedItem.pageCount}</p>
                    </div>
                  )}
                  {selectedItem.size && (
                    <div>
                      <label className="text-sm text-gray-600">File Size</label>
                      <p className="font-medium">{selectedItem.size}</p>
                    </div>
                  )}
                  <div>
                    <label className="text-sm text-gray-600">Created</label>
                    <p className="font-medium">
                      {new Date(selectedItem.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Tags</label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedItem.tags.map(tag => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  {selectedItem.crewGenerated && (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                      <div className="flex items-center space-x-2 text-purple-700 mb-2">
                        <span className="text-sm font-medium">CrewAI Generated</span>
                      </div>
                      {selectedItem.metadata?.crew_agents && (
                        <div className="text-xs text-purple-600">
                          <div className="font-medium mb-1">AI Agents Used:</div>
                          <div className="space-y-1">
                            {selectedItem.metadata.crew_agents.map((agent: string, index: number) => (
                              <div key={index} className="flex items-center space-x-1">
                                <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
                                <span>{agent}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedItem.metadata?.generation_time && (
                        <div className="text-xs text-purple-600 mt-2">
                          <div className="font-medium">Generation Time:</div>
                          <div>{selectedItem.metadata.generation_time}</div>
                        </div>
                      )}
                    </div>
                  )}
                  {selectedItem.theme && (
                    <div>
                      <label className="text-sm text-gray-600">Theme</label>
                      <p className="font-medium capitalize">{selectedItem.theme}</p>
                    </div>
                  )}
                  {selectedItem.metadata?.titleStyle && (
                    <div>
                      <label className="text-sm text-gray-600">Title Style</label>
                      <p className="font-medium capitalize">{selectedItem.metadata.titleStyle}</p>
                    </div>
                  )}
                  {selectedItem.metadata?.authorStyle && (
                    <div>
                      <label className="text-sm text-gray-600">Writing Style</label>
                      <p className="font-medium">{selectedItem.metadata.authorStyle}</p>
                    </div>
                  )}
                  {selectedItem.metadata?.researchDepth && (
                    <div>
                      <label className="text-sm text-gray-600">Research Depth</label>
                      <p className="font-medium capitalize">{selectedItem.metadata.researchDepth}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Journal Creation Modal */}
      {isJournalModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-900">Create New Journal</h2>
              <button
                onClick={() => setIsJournalModalOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <UnifiedJournalCreator
              onComplete={handleJournalCreation}
              onClose={() => setIsJournalModalOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentLibrary;