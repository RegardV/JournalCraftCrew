/**
 * Journal Customization Interface
 * Live preview with theme, layout, font, and cover customization
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'

interface Project {
  id: number
  title: string
  description?: string
  theme?: string
  layout?: string
  font_size?: string
  font_family?: string
  page_numbers?: boolean
  table_of_contents?: boolean
  cover_image_url?: string
  custom_css?: string
  tags?: string[]
}

interface CustomizationSettings {
  title?: string
  description?: string
  layout?: string
  font_size?: string
  font_family?: string
  page_numbers?: boolean
  table_of_contents?: boolean
  cover_image_url?: string
  custom_css?: string
  tags?: string[]
  theme_colors?: {
    primary: string
    secondary: string
    accent: string
    background: string
    text_color: string
  }
}

const JournalCustomizer: React.FC = () => {
  // Project data - would come from API props
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  // Customization settings
  const [customSettings, setCustomSettings] = useState<CustomizationSettings>({
    layout: 'single-column',
    font_size: 'medium',
    font_family: 'serif',
    page_numbers: true,
    table_of_contents: false,
    theme_colors: {
      primary: '#2563eb',
      secondary: '#4472ca',
      accent: '#10b981',
      background: '#ffffff',
      text_color: '#1f2937'
    }
  })

  // Live preview state
  const [showPreview, setShowPreview] = useState(false)
  const [previewContent, setPreviewContent] = useState<string>('')

  // Available options
  const layoutOptions = [
    { value: 'single-column', label: 'Single Column', icon: '📄' },
    { value: 'two-column', label: 'Two Columns', icon: '📖' },
    { value: 'minimal', label: 'Minimal', icon: '✨' },
    { value: 'creative', label: 'Creative', icon: '🎨' }
  ]

  const fontSizeOptions = [
    { value: 'small', label: 'Small', sample: 'Aa' },
    { value: 'medium', label: 'Medium', sample: 'Aa' },
    { value: 'large', label: 'Large', sample: 'Aa' },
    { value: 'x-large', label: 'Extra Large', sample: 'Aa' }
  ]

  const fontFamilyOptions = [
    { value: 'serif', label: 'Serif', sample: 'Aa Bb Cc' },
    { value: 'sans-serif', label: 'Sans Serif', sample: 'Aa Bb Cc' },
    { value: 'monospace', label: 'Monospace', sample: 'Aa Bb Cc' },
    { value: 'cursive', label: 'Cursive', sample: 'Aa Bb Cc' },
    { value: 'display', label: 'Display', sample: 'Aa Bb Cc' }
  ]

  const presetThemes = [
    {
      name: 'Ocean Blue',
      colors: {
        primary: '#0ea5e9',
        secondary: '#38bdf8',
        accent: '#06b6d4',
        background: '#f0f9ff',
        text_color: '#0c4a6e'
      }
    },
    {
      name: 'Forest Green',
      colors: {
        primary: '#059669',
        secondary: '#10b981',
        accent: '#34d399',
        background: '#ecfdf5',
        text_color: '#064e3b'
      }
    },
    {
      name: 'Sunset Orange',
      colors: {
        primary: '#ea580c',
        secondary: '#f97316',
        accent: '#dc2626',
        background: '#fff7ed',
        text_color: '#9a3412'
      }
    },
    {
      name: 'Royal Purple',
      colors: {
        primary: '#7c3aed',
        secondary: '#a78bfa',
        accent: '#8b5cf6',
        background: '#ede9fe',
        text_color: '#6d28d9'
      }
    }
  ]

  // Mock project data - in real app, this would come from URL params
  useEffect(() => {
    // Simulate loading project data
    setTimeout(() => {
      setProject({
        id: 1,
        title: 'My Mindfulness Journal',
        description: 'A 30-day journey into daily mindfulness practice',
        theme: 'mindfulness',
        layout: 'single-column',
        font_size: 'medium',
        font_family: 'serif',
        page_numbers: true,
        table_of_contents: false,
        cover_image_url: '',
        custom_css: '',
        tags: ['mindfulness', 'daily', 'reflection']
      })
      setLoading(false)
    }, 1000)
  }, [])

  const generatePreview = useCallback(() => {
    if (!customSettings.title) return

    const currentDate = new Date().toLocaleDateString()
    const sampleContent = `
      <div style="font-family: ${customSettings.font_family || 'serif'}; color: ${customSettings.theme_colors?.text_color || '#1f2937'}; background-color: ${customSettings.theme_colors?.background || '#ffffff'}; padding: 20px; line-height: 1.6;">
        <h1 style="font-size: 24px; margin-bottom: 16px; color: ${customSettings.theme_colors?.primary || '#2563eb'};">${customSettings.title || 'My Journal'}</h1>
        <p style="font-size: ${customSettings.font_size === 'small' ? '14px' : customSettings.font_size === 'large' ? '18px' : '16px'}; margin-bottom: 20px;">${currentDate}</p>
        <div style="border-top: 2px solid ${customSettings.theme_colors?.secondary || '#4472ca'}; padding-top: 20px; margin-top: 20px;">
          <h2 style="font-size: 20px; color: ${customSettings.theme_colors?.primary || '#2563eb'};">Daily Reflection</h2>
          <p style="margin-bottom: 16px;">Today I am grateful for...</p>
          <p style="margin-bottom: 16px;">What brought me joy today...</p>
          <p style="margin-bottom: 16px;">What did I learn about myself...</p>
        </div>
        ${customSettings.page_numbers ? '<div style="margin-top: 40px; text-align: center; color: #6b7280; font-size: 12px;">Page 1</div>' : ''}
      </div>
    `

    setPreviewContent(content)
  }, [customSettings])

  const handleSettingChange = (key: keyof CustomizationSettings, value: any) => {
    setCustomSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleThemePreset = (theme: typeof presetThemes[0]) => {
    setCustomSettings(prev => ({
      ...prev,
      theme_colors: theme.colors
    }))
  }

  const handleSaveCustomization = async () => {
    if (!project) return

    setSaving(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/library/projects/${project.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(customSettings)
      })

      if (!response.ok) {
        throw new Error('Failed to save customization')
      }

      // Update local project state
      setProject(prev => prev ? { ...prev, ...customSettings } : null)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save customization')
    } finally {
      setSaving(false)
    }
  }

  const handleExport = async (format: string) => {
    if (!project) return

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/export/create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: project.id,
          format,
          settings: customSettings
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading project...</span>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-lg mb-4">Project not found</div>
          <Button onClick={() => window.location.href = '/library'}>
            Back to Library
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Customize: {project.title}</h1>
              <p className="text-gray-600 mt-1">Personalize your journal with themes, fonts, and layouts</p>
            </div>
            <div className="flex space-x-3">
              <Button onClick={() => setShowPreview(!showPreview)}>
                {showPreview ? 'Hide Preview' : 'Show Preview'}
              </Button>
              <Button onClick={handleSaveCustomization} disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Customization Panel */}
          <div className="space-y-6">
            {/* Project Details */}
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Details</h3>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title</label>
                    <Input
                      id="title"
                      value={customSettings.title || ''}
                      onChange={(e) => handleSettingChange('title', e.target.value)}
                      placeholder="My Journal"
                    />
                  </div>

                  <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
                    <textarea
                      id="description"
                      value={customSettings.description || ''}
                      onChange={(e) => handleSettingChange('description', e.target.value)}
                      rows={3}
                      className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="A description of your journal project..."
                    />
                  </div>

                  <div>
                    <label htmlFor="tags" className="block text-sm font-medium text-gray-700">Tags</label>
                    <Input
                      id="tags"
                      value={(customSettings.tags || []).join(', ')}
                      onChange={(e) => handleSettingChange('tags', e.target.value.split(',').map(tag => tag.trim()))}
                      placeholder="mindfulness, daily, reflection"
                    />
                  </div>
                </div>
              </div>
            </Card>

            {/* Layout Settings */}
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Layout Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="layout" className="block text-sm font-medium text-gray-700">Layout Style</label>
                    <select
                      id="layout"
                      value={customSettings.layout || 'single-column'}
                      onChange={(e) => handleSettingChange('layout', e.target.value)}
                      className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      {layoutOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.icon} {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="font_size" className="block text-sm font-medium text-gray-700">Font Size</label>
                    <select
                      id="font_size"
                      value={customSettings.font_size || 'medium'}
                      onChange={(e) => handleSettingChange('font_size', e.target.value)}
                      className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      {fontSizeOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} ({option.sample})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="font_family" className="block text-sm font-medium text-gray-700">Font Family</label>
                    <select
                      id="font_family"
                      value={customSettings.font_family || 'serif'}
                      onChange={(e) => handleSettingChange('font_family', e.target.value)}
                      className="w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      {fontFamilyOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} ({option.sample})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-3">
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        id="page_numbers"
                        checked={customSettings.page_numbers || false}
                        onChange={(e) => handleSettingChange('page_numbers', e.target.checked)}
                        className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm font-medium text-gray-700">Include Page Numbers</span>
                    </label>

                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        id="table_of_contents"
                        checked={customSettings.table_of_contents || false}
                        onChange={(e) => handleSettingChange('table_of_contents', e.target.checked)}
                        className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm font-medium text-gray-700">Include Table of Contents</span>
                    </label>
                  </div>
                </div>
              </div>
            </Card>

            {/* Theme Colors */}
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Theme Colors</h3>

                {/* Preset Themes */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-3">Quick Theme Presets</label>
                  <div className="grid grid-cols-2 gap-3">
                    {presetThemes.map((theme, index) => (
                      <button
                        key={index}
                        onClick={() => handleThemePreset(theme)}
                        className="p-3 border-2 rounded-lg transition-colors hover:border-blue-500 focus:ring-2 focus:ring-blue-500"
                        style={{
                          borderColor: theme.colors.primary,
                          backgroundColor: `${theme.colors.background}20`
                        }}
                      >
                        <div className="text-sm font-medium mb-2">{theme.name}</div>
                        <div className="flex space-x-2">
                          {Object.values(theme.colors).slice(0, 4).map((color, colorIndex) => (
                            <div
                              key={colorIndex}
                              className="w-6 h-6 rounded border border-gray-300"
                              style={{ backgroundColor: color }}
                            />
                          ))}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Custom Color Pickers */}
                <div className="space-y-3">
                  <div>
                    <label htmlFor="primary_color" className="block text-sm font-medium text-gray-700">Primary Color</label>
                    <input
                      id="primary_color"
                      type="color"
                      value={customSettings.theme_colors?.primary || '#2563eb'}
                      onChange={(e) => handleSettingChange('theme_colors', {
                        ...customSettings.theme_colors,
                        primary: e.target.value
                      })}
                      className="h-10 w-full border border-gray-300 rounded cursor-pointer"
                    />
                  </div>

                  <div>
                    <label htmlFor="accent_color" className="block text-sm font-medium text-gray-700">Accent Color</label>
                    <input
                      id="accent_color"
                      type="color"
                      value={customSettings.theme_colors?.accent || '#10b981'}
                      onChange={(e) => handleSettingChange('theme_colors', {
                        ...customSettings.theme_colors,
                        accent: e.target.value
                      })}
                      className="h-10 w-full border border-gray-300 rounded cursor-pointer"
                    />
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Preview Panel */}
          {showPreview && (
            <div className="lg:sticky lg:top-8">
              <Card className="h-full">
                <div className="p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Live Preview</h3>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={generatePreview}
                    >
                      Refresh Preview
                    </Button>
                  </div>

                  <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
                    <div
                      className="p-4 bg-white"
                      style={{
                        fontFamily: customSettings.font_family || 'serif',
                        fontSize: customSettings.font_size === 'small' ? '14px' : customSettings.font_size === 'large' ? '18px' : '16px',
                        color: customSettings.theme_colors?.text_color || '#1f2937',
                        backgroundColor: customSettings.theme_colors?.background || '#ffffff'
                      }}
                      dangerouslySetInnerHTML={{ __html: previewContent || '<p>Click "Refresh Preview" to see your customization</p>' }}
                    />
                  </div>

                  <div className="mt-4 text-center text-sm text-gray-500">
                    This preview shows how your journal will look with the current settings
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>

        {/* Export Options */}
        <div className="mt-8">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Options</h3>
              <div className="flex flex-wrap gap-3">
                <Button
                  variant="outline"
                  onClick={() => handleExport('pdf')}
                >
                  Export as PDF
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleExport('epub')}
                >
                  Export as EPUB
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleExport('kdp')}
                >
                  Export for KDP
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-600 text-white p-4 rounded-lg shadow-lg max-w-sm">
          <div className="font-medium">Error</div>
          <div className="text-sm">{error}</div>
        </div>
      )}
    </div>
  )
}

export default JournalCustomizer