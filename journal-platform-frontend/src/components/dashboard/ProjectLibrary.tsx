/**
 * Project Library Dashboard Component
 * Displays user's AI-generated and customized journal projects
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'

interface Project {
  id: number
  title: string
  description?: string
  type: string
  status: string
  theme?: string
  cover_image_url?: string
  word_count: number
  tags: string[]
  created_at?: string
  updated_at?: string
  ai_generated: boolean
  customization_applied: boolean
}

interface ProjectFilters {
  status_filter?: string
  project_type?: string
  search_query?: string
  page: number
  limit: number
}

const ProjectLibrary: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Pagination and filtering
  const [filters, setFilters] = useState<ProjectFilters>({
    page: 1,
    limit: 12
  })
  const [totalCount, setTotalCount] = useState(0)
  const [totalPages, setTotalPages] = useState(0)

  // Available filters
  const statusOptions = [
    { value: '', label: 'All Projects' },
    { value: 'ai_completed', label: 'AI Generated' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'published', label: 'Published' }
  ]

  const typeOptions = [
    { value: '', label: 'All Types' },
    { value: 'personal', label: 'Personal' },
    { value: 'project', label: 'Projects' },
    { value: 'therapeutic', label: 'Therapeutic' },
    { value: 'creative', label: 'Creative' }
  ]

  const fetchProjects = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('No authentication token found')
      }

      const queryParams = new URLSearchParams()
      if (filters.status_filter) queryParams.append('status_filter', filters.status_filter)
      if (filters.project_type) queryParams.append('project_type', filters.project_type)
      if (filters.search_query) queryParams.append('search', filters.search_query)
      queryParams.append('page', filters.page.toString())
      queryParams.append('limit', filters.limit.toString())

      const response = await fetch(`/api/library/projects?${queryParams.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch projects')
      }

      const data = await response.json()
      setProjects(data.projects)
      setTotalCount(data.pagination.total)
      setTotalPages(data.pagination.pages)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  const handleFilterChange = (key: keyof ProjectFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }))
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const searchQuery = formData.get('search') as string
    handleFilterChange('search_query', searchQuery)
  }

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ai_completed':
        return 'bg-blue-100 text-blue-800'
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'published':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ai_generated':
        return '🤖'
      case 'in_progress':
        return '📝'
      case 'completed':
        return '✅'
      case 'published':
        return '📚'
      default:
        return '📄'
    }
  }

  const handleCreateNewProject = () => {
    window.location.href = '/journal/create'
  }

  const handleDuplicateProject = async (projectId: number) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/library/projects/${projectId}/duplicate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to duplicate project')
      }

      // Refresh projects list
      fetchProjects()

    } catch (err) {
      console.error('Failed to duplicate project:', err)
    }
  }

  const handleDeleteProject = async (projectId: number) => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/library/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to delete project')
      }

      // Refresh projects list
      fetchProjects()

    } catch (err) {
      console.error('Failed to delete project:', err)
    }
  }

  const handleExportProject = async (projectId: number, format: string) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/export/create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: projectId,
          format,
          settings: {}
        })
      })

      if (!response.ok) {
        throw new Error('Failed to start export')
      }

      const data = await response.json()
      console.log('Export started:', data)

    } catch (err) {
      console.error('Failed to export project:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">My Project Library</h1>
              <p className="text-gray-600 mt-1">Manage and customize your journal projects</p>
            </div>
            <Button onClick={handleCreateNewProject}>
              Create New Journal
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters and Search */}
        <Card className="mb-6">
          <div className="p-6">
            <form onSubmit={handleSearch} className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <Input
                  name="search"
                  type="search"
                  placeholder="Search projects..."
                  defaultValue={filters.search_query || ''}
                  className="w-full"
                />
              </div>

              {/* Status Filter */}
              <div>
                <label htmlFor="status_filter" className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  id="status_filter"
                  value={filters.status_filter || ''}
                  onChange={(e) => handleFilterChange('status_filter', e.target.value)}
                  className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2"
                >
                  {statusOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Type Filter */}
              <div>
                <label htmlFor="project_type" className="block text-sm font-medium text-gray-700 mb-2">
                  Type
                </label>
                <select
                  id="project_type"
                  value={filters.project_type || ''}
                  onChange={(e) => handleFilterChange('project_type', e.target.value)}
                  className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2"
                >
                  {typeOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Search Button */}
              <div className="lg:mt-6">
                <Button type="submit" variant="outline">
                  Search
                </Button>
              </div>
            </form>
          </div>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <div className="p-4">
              <div className="text-red-800 font-medium">Error</div>
              <div className="text-red-600">{error}</div>
            </div>
          </Card>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading projects...</span>
          </div>
        ) : (
          <>
            {/* Projects Grid */}
            {projects.length === 0 ? (
              <Card className="text-center py-12">
                <div className="text-gray-500 text-lg">No projects found</div>
                <p className="text-gray-400 mt-2">
                  {filters.search_query || filters.status_filter || filters.project_type
                    ? 'Try adjusting your filters or search terms.'
                    : 'Create your first AI journal to get started!'}
                </p>
                <Button onClick={handleCreateNewProject} className="mt-4">
                  Create Your First Journal
                </Button>
              </Card>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {projects.map((project) => (
                  <Card key={project.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                    {/* Cover Image or Placeholder */}
                    <div className="h-48 bg-gradient-to-br from-blue-50 to-indigo-100 relative">
                      {project.cover_image_url ? (
                        <img
                          src={project.cover_image_url}
                          alt={project.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          {project.ai_generated ? (
                            <div className="text-4xl">🤖</div>
                          ) : (
                            <div className="text-4xl">📝</div>
                          )}
                        </div>
                      )}

                      {/* Status Badge */}
                      <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                        {getStatusIcon(project.status)} {project.status.replace('_', ' ').replace(/\b\w/g, ' => $1')}
                      </div>
                    </div>

                    <div className="p-4">
                      {/* Title and Meta */}
                      <div className="mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">{project.title}</h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {project.type}
                          </span>
                          {project.ai_generated && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              AI Generated
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Description */}
                      {project.description && (
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{project.description}</p>
                      )}

                      {/* Tags */}
                      {project.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-3">
                          {project.tags.slice(0, 3).map((tag, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
                            >
                              {tag}
                            </span>
                          ))}
                          {project.tags.length > 3 && (
                            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                              +{project.tags.length - 3}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Stats */}
                      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                        <span>{project.word_count.toLocaleString()} words</span>
                        <span>{project.created_at ? new Date(project.created_at).toLocaleDateString() : 'No date'}</span>
                      </div>

                      {/* Actions */}
                      <div className="flex flex-wrap gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.location.href = `/library/projects/${project.id}`}
                        >
                          View Details
                        </Button>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDuplicateProject(project.id)}
                        >
                          Duplicate
                        </Button>

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleExportProject(project.id, 'pdf')}
                          >
                            Export PDF
                          </Button>

                          {project.ai_generated && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => window.location.href = `/customize/${project.id}`}
                            >
                              Customize
                            </Button>
                          )}
                        </div>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteProject(project.id)}
                          className="text-red-600 border-red-200 hover:bg-red-50"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center space-x-2 mt-8">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(filters.page - 1)}
                  disabled={filters.page <= 1}
                >
                  Previous
                </Button>

                <span className="text-gray-600">
                  Page {filters.page} of {totalPages}
                </span>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(filters.page + 1)}
                  disabled={filters.page >= totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default ProjectLibrary