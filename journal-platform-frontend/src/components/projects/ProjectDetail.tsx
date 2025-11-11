/**
 * Project Detail Component
 * Displays all generated files for a journal project with download functionality
 */

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import Header from '../layout/Header'
import Sidebar from '../layout/Sidebar'

interface ProjectFile {
  name: string
  path: string
  type: string
  size: number
  section: 'PDF_output' | 'media' | 'Json_output' | 'LLM_output'
}

interface ProjectDetail {
  id: string
  title: string
  theme: string
  author_style: string
  status: string
  created_at: string
  files: ProjectFile[]
  file_count: number
  has_pdfs: string[]
  sections: {
    PDF_output: ProjectFile[]
    media: ProjectFile[]
    Json_output: ProjectFile[]
    LLM_output: ProjectFile[]
  }
}

const ProjectDetail: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<ProjectDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'PDF_output' | 'media' | 'Json_output' | 'LLM_output'>('PDF_output')

  useEffect(() => {
    console.log('ProjectDetail component mounted with projectId:', projectId)
    if (projectId) {
      loadProjectDetail(projectId)
    }
  }, [projectId])

  const loadProjectDetail = async (projectId: string) => {
    console.log('Loading project detail for projectId:', projectId)
    try {
      setLoading(true)
      setError(null)

      const token = localStorage.getItem('access_token')
      console.log('Token found:', !!token)
      if (!token) {
        throw new Error('Authentication required')
      }

      // Get project files from the same endpoint that ContentLibrary uses
      console.log('Fetching files from:', `/api/library/llm-projects`)
      const libraryResponse = await fetch(`/api/library/llm-projects`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!libraryResponse.ok) {
        throw new Error('Failed to load project files')
      }

      const libraryData = await libraryResponse.json()
      console.log('Library data received:', libraryData)

      // Find the specific project from the library data
      const projectData = libraryData.projects?.find(p => p.id === projectId)
      console.log('Found project data:', projectData)

      if (!projectData) {
        throw new Error('Project not found in library')
      }

      // Organize files by sections
      const allFiles = projectData.files || []
      const sections = {
        PDF_output: allFiles.filter(f => f.path.includes('PDF_output')),
        media: allFiles.filter(f => f.path.includes('media')),
        Json_output: allFiles.filter(f => f.path.includes('Json_output')),
        LLM_output: allFiles.filter(f => f.path.includes('LLM_output'))
      }

      setProject({
        id: projectId,
        title: projectData.title || 'Untitled Project',
        theme: projectData.theme || 'Unknown',
        author_style: projectData.author_style || 'Unknown',
        status: projectData.status || 'completed',
        created_at: projectData.created_at || new Date().toISOString(),
        files: allFiles,
        file_count: allFiles.length,
        has_pdfs: projectData.has_pdfs || [],
        sections
      })

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (filePath: string, fileName: string) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/journals/${projectId}/download/${encodeURIComponent(filePath)}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to download file')
      }

      // Create blob and download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

    } catch (err) {
      console.error('Download failed:', err)
      alert('Failed to download file')
    }
  }

  const getFileIcon = (type: string) => {
    if (type === '.pdf') return '📄'
    if (type === '.json') return '📋'
    if (type === '.png' || type === '.jpg' || type === '.jpeg') return '🖼️'
    if (type === '.txt') return '📝'
    return '📁'
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'pdfs': return 'bg-red-100 text-red-800 border-red-200'
      case 'media': return 'bg-green-100 text-green-800 border-green-200'
      case 'data': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'pdfs': return 'PDF Documents'
      case 'media': return 'Images & Media'
      case 'data': return 'Data & JSON'
      default: return 'Other Files'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-6"></div>
          <p className="text-color-text-light text-lg">Loading project details...</p>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">❌</div>
          <p className="text-color-text-light text-lg mb-4">{error || 'Project not found'}</p>
          <Button onClick={() => navigate('/dashboard')} variant="outline">
            Back to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen gradient-bg">
      <div className="header-container">
        <div className="section-container">
          <Header
            user={undefined} // Will be filled from auth context
            onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)}
            isMobileMenuOpen={isSidebarOpen}
          />
        </div>
      </div>

      <div className="flex">
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        <main className="flex-1 p-6 md:ml-80">
          <div className="section-container">
            {/* Header */}
            <div className="mb-8">
              <Button
                onClick={() => navigate('/dashboard')}
                variant="outline"
                className="mb-4"
              >
                ← Back to Library
              </Button>

              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-4xl font-bold text-gray-900 mb-2">
                    {project.title}
                  </h1>
                  <div className="flex items-center space-x-4 text-gray-600 mb-4">
                    <span className="text-sm">
                      🎨 Theme: <strong>{project.theme}</strong>
                    </span>
                    <span className="text-sm">
                      ✍️ Style: <strong>{project.author_style}</strong>
                    </span>
                    <span className="text-sm">
                      📅 Created: <strong>{new Date(project.created_at).toLocaleDateString()}</strong>
                    </span>
                    <span className="text-sm">
                      📁 Files: <strong>{project.file_count}</strong>
                    </span>
                  </div>
                  {project.has_pdfs.length > 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                        ✅ Complete with {project.has_pdfs.length} PDF(s)
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Tabbed Files Section */}
            <div className="space-y-6">
              {project.files.length === 0 ? (
                <Card className="text-center py-12">
                  <div className="text-gray-400 text-6xl mb-4">📁</div>
                  <p className="text-gray-600 text-lg">No files found for this project</p>
                </Card>
              ) : (
                <>
                  {/* Tabs */}
                  <div className="border-b border-gray-200">
                    <nav className="-mb-px flex space-x-8">
                      {[
                        { id: 'PDF_output', label: '📄 PDF Documents', count: project.sections.PDF_output.length },
                        { id: 'media', label: '🖼️ Images', count: project.sections.media.length },
                        { id: 'Json_output', label: '📋 JSON Data', count: project.sections.Json_output.length },
                        { id: 'LLM_output', label: '📝 Content Files', count: project.sections.LLM_output.length }
                      ].map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id as any)}
                          className={`${
                            activeTab === tab.id
                              ? 'border-blue-500 text-blue-600'
                              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                          } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                        >
                          <span>{tab.label}</span>
                          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                            {tab.count}
                          </span>
                        </button>
                      ))}
                    </nav>
                  </div>

                  {/* Tab Content */}
                  <Card>
                    {/* PDF Output Tab */}
                    {activeTab === 'PDF_output' && (
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">📄 PDF Documents</h3>
                        {project.sections.PDF_output.length === 0 ? (
                          <p className="text-gray-500 text-center py-8">No PDF files found</p>
                        ) : (
                          <div className="space-y-3">
                            {project.sections.PDF_output.map((file, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                              >
                                <div className="flex items-center space-x-3">
                                  <span className="text-2xl">📄</span>
                                  <div>
                                    <div className="font-medium text-gray-900">
                                      {file.name}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                      {formatFileSize(file.size)}
                                    </div>
                                  </div>
                                </div>
                                <Button
                                  onClick={() => handleDownload(file.path, file.name)}
                                  size="sm"
                                >
                                  Download
                                </Button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Media Tab */}
                    {activeTab === 'media' && (
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">🖼️ Images & Media</h3>
                        {project.sections.media.length === 0 ? (
                          <p className="text-gray-500 text-center py-8">No media files found</p>
                        ) : (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {project.sections.media.map((file, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                              >
                                <div className="flex items-center space-x-3">
                                  <span className="text-2xl">🖼️</span>
                                  <div>
                                    <div className="font-medium text-gray-900">
                                      {file.name}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                      {formatFileSize(file.size)}
                                    </div>
                                  </div>
                                </div>
                                <Button
                                  onClick={() => handleDownload(file.path, file.name)}
                                  size="sm"
                                >
                                  Download
                                </Button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* JSON Output Tab */}
                    {activeTab === 'Json_output' && (
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">📋 JSON Data Files</h3>
                        {project.sections.Json_output.length === 0 ? (
                          <p className="text-gray-500 text-center py-8">No JSON files found</p>
                        ) : (
                          <div className="space-y-3">
                            {project.sections.Json_output.map((file, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                              >
                                <div className="flex items-center space-x-3">
                                  <span className="text-2xl">{getFileIcon(file.type)}</span>
                                  <div>
                                    <div className="font-medium text-gray-900">
                                      {file.name}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                      {formatFileSize(file.size)}
                                    </div>
                                  </div>
                                </div>
                                <Button
                                  onClick={() => handleDownload(file.path, file.name)}
                                  size="sm"
                                >
                                  Download
                                </Button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* LLM Output Tab */}
                    {activeTab === 'LLM_output' && (
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">📝 Content Files</h3>
                        {project.sections.LLM_output.length === 0 ? (
                          <p className="text-gray-500 text-center py-8">No content files found</p>
                        ) : (
                          <div className="space-y-3">
                            {project.sections.LLM_output.map((file, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                              >
                                <div className="flex items-center space-x-3">
                                  <span className="text-2xl">{getFileIcon(file.type)}</span>
                                  <div>
                                    <div className="font-medium text-gray-900">
                                      {file.name}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                      {formatFileSize(file.size)}
                                    </div>
                                  </div>
                                </div>
                                <Button
                                  onClick={() => handleDownload(file.path, file.name)}
                                  size="sm"
                                >
                                  Download
                                </Button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </Card>
                </>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default ProjectDetail