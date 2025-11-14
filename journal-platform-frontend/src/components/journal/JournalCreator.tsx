/**
 * AI Journal Creator Component
 * Handles the AI journal generation workflow
 */

import React, { useState, useCallback } from 'react'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { getApiURL } from '@/lib/apiConfig'

// Types
interface AIGenerationRequest {
  theme: string
  title_style: string
  research_depth: string
  target_audience: string
  include_images: boolean
  export_format: string
}

interface AIGenerationResponse {
  job_id: string
  status: string
  estimated_time: number
}

interface Theme {
  id: string
  name: string
  description: string
}

interface TitleStyle {
  id: string
  name: string
  description: string
}

// Mock data - will come from API
const AVAILABLE_THEMES: Theme[] = [
  { id: 'mindfulness', name: 'Mindfulness', description: 'Daily mindfulness and meditation exercises' },
  { id: 'productivity', name: 'Productivity', description: 'Focus on goals and achievement' },
  { id: 'creativity', name: 'Creativity', description: 'Unlock creative potential' },
  { id: 'gratitude', name: 'Gratitude', description: 'Daily gratitude practice' },
  { id: 'fitness', name: 'Fitness', description: 'Health and wellness tracking' },
  { id: 'finance', name: 'Finance', description: 'Financial planning and mindfulness' }
]

const TITLE_STYLES: TitleStyle[] = [
  { id: 'inspirational', name: 'Inspirational', description: 'Motivating and uplifting tone' },
  { id: 'practical', name: 'Practical', description: 'Straightforward and actionable' },
  { id: 'creative', name: 'Creative', description: 'Artistic and expressive' },
  { id: 'scientific', name: 'Scientific', description: 'Evidence-based and analytical' },
  { id: 'spiritual', name: 'Spiritual', description: 'Mindfulness and inner growth' }
]

const RESEARCH_DEPTH_OPTIONS = [
  { value: 'basic', label: 'Basic (Quick start)' },
  { value: 'standard', label: 'Standard (Recommended)' },
  { value: 'comprehensive', label: 'Comprehensive (Deep dive)' }
]

const TARGET_AUDIENCE_OPTIONS = [
  { value: 'general', label: 'General Audience' },
  { value: 'beginners', label: 'Beginners' },
  { value: 'intermediate', label: 'Intermediate Users' },
  { value: 'advanced', label: 'Advanced Practitioners' }
]

const EXPORT_FORMATS = [
  { value: 'pdf', label: 'PDF (Standard)' },
  { value: 'epub', label: 'EPUB (Digital)' },
  { value: 'kdp', label: 'KDP (Amazon Publishing)' }
]

export const JournalCreator: React.FC = () => {
  const [selectedTheme, setSelectedTheme] = useState<string>('mindfulness')
  const [titleStyle, setTitleStyle] = useState<string>('inspirational')
  const [researchDepth, setResearchDepth] = useState<string>('standard')
  const [targetAudience, setTargetAudience] = useState<string>('general')
  const [includeImages, setIncludeImages] = useState<boolean>(true)
  const [exportFormat, setExportFormat] = useState<string>('pdf')

  const [isGenerating, setIsGenerating] = useState<boolean>(false)
  const [generationJob, setGenerationJob] = useState<AIGenerationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<number>(0)
  const [currentStage, setCurrentStage] = useState<string>('')
  const [currentAgent, setCurrentAgent] = useState<string>('')
  const [logs, setLogs] = useState<Array<{ timestamp: string; level: string; agent: string; message: string }>>([])

  const handleGenerateJournal = useCallback(async () => {
    try {
      setIsGenerating(true)
      setError(null)
      setProgress(0)
      setCurrentStage('Starting AI generation...')
      setCurrentAgent('')
      setLogs([{
        timestamp: new Date().toLocaleTimeString(),
        level: 'INFO',
        agent: 'System',
        message: '🚀 Initializing journal creation workflow...'
      }])

      const request: AIGenerationRequest = {
        theme: selectedTheme,
        title_style: titleStyle,
        research_depth: researchDepth,
        target_audience: targetAudience,
        include_images: includeImages,
        export_format: exportFormat
      }

      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/ai/generate-journal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to start journal generation')
      }

      const data: AIGenerationResponse = await response.json()
      setGenerationJob(data)

      // Start WebSocket connection for progress updates
      startProgressTracking(data.job_id)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setIsGenerating(false)
    }
  }, [selectedTheme, titleStyle, researchDepth, targetAudience, includeImages, exportFormat])

  const startProgressTracking = useCallback((jobId: string) => {
    const token = localStorage.getItem('access_token')
    const apiURL = getApiURL();
    const wsUrl = `${apiURL.replace('http://', 'ws://').replace('https://', 'wss://')}/ws/job/${jobId}?token=${token}`

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket connected for job progress')
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'connection_established') {
          console.log('Connection confirmed for job tracking')
        } else if (data.progress !== undefined || data.progress_percentage !== undefined) {
          // Handle new backend format with logs
          const progressValue = data.progress || data.progress_percentage || 0
          const stageMessage = data.message || data.current_stage || 'Processing...'
          const agent = data.currentAgent || 'System'

          setProgress(progressValue)
          setCurrentStage(stageMessage)
          setCurrentAgent(agent)

          // Add log entry if available
          if (data.log || data.latestLog) {
            const logEntry = data.log || data.latestLog
            const timestamp = new Date().toLocaleTimeString()
            setLogs(prev => [...prev.slice(-19), {
              timestamp,
              level: 'INFO',
              agent,
              message: logEntry
            }])
          }

          // Add logs array if available
          if (data.logs && Array.isArray(data.logs)) {
            setLogs(prev => {
              const combined = [...prev, ...data.logs]
              // Keep only last 50 entries
              return combined.slice(-50)
            })
          }
        } else if (data.status === 'completed') {
          setIsGenerating(false)
          setProgress(100)
          setCurrentStage('Journal generation completed!')

          // Add completion log
          const timestamp = new Date().toLocaleTimeString()
          setLogs(prev => [...prev, {
            timestamp,
            level: 'SUCCESS',
            agent: 'System',
            message: '✅ Journal creation completed successfully!'
          }])

          ws.close()
        } else if (data.status === 'failed' || data.status === 'error') {
          setIsGenerating(false)
          setError(data.message || data.error_message || 'Generation failed')

          // Add error log
          const timestamp = new Date().toLocaleTimeString()
          setLogs(prev => [...prev, {
            timestamp,
            level: 'ERROR',
            agent: 'System',
            message: `❌ ${data.message || data.error_message || 'Generation failed'}`
          }])

          ws.close()
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError('Failed to connect to progress tracking')
        setIsGenerating(false)
      }

      ws.onclose = () => {
        console.log('WebSocket connection closed')
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setError('Failed to establish real-time connection')
      setIsGenerating(false)
    }
  }, [])

  const handleCancelGeneration = useCallback(async () => {
    if (!generationJob) return

    try {
      const token = localStorage.getItem('access_token')
      await fetch(`/api/ai/cancel/${generationJob.job_id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      setIsGenerating(false)
      setGenerationJob(null)
      setProgress(0)
      setCurrentStage('')

    } catch (err) {
      console.error('Failed to cancel generation:', err)
    }
  }, [generationJob])

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Create Your AI Journal
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Our AI will create a complete 30-day journaling experience tailored to your preferences.
          Choose your theme, style, and depth to get started.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="text-red-800 font-medium">Error</div>
          <div className="text-red-600 mt-1">{error}</div>
        </div>
      )}

      {/* Progress Display */}
      {(isGenerating || generationJob) && (
        <Card className="bg-blue-50 border-blue-200">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-blue-900">
                AI Generation Progress
              </h3>
              {generationJob && !isGenerating && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCancelGeneration}
                  className="text-red-600 border-red-200 hover:bg-red-50"
                >
                  Cancel
                </Button>
              )}
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-blue-100 rounded-full h-2 mb-4">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="text-blue-800 font-medium text-center">
              {currentStage} ({progress}%)
            </div>

            {/* CLI Output Display */}
            {logs.length > 0 && (
              <div className="mt-6">
                <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm max-h-64 overflow-y-auto">
                  <div className="text-green-400 mb-2 font-bold">$ Journal Craft Crew CLI Output</div>
                  <div className="space-y-1">
                    {logs.map((log, index) => (
                      <div key={index} className="text-gray-300 flex items-start space-x-2">
                        <span className="text-gray-500 text-xs">{log.timestamp}</span>
                        <span className={
                          log.level === 'ERROR' ? 'text-red-400' :
                          log.level === 'SUCCESS' ? 'text-green-400' :
                          log.level === 'INFO' ? 'text-blue-400' :
                          'text-gray-300'
                        }>
                          {log.level}
                        </span>
                        {log.agent && log.agent !== 'System' && (
                          <span className="text-yellow-400">[{log.agent}]</span>
                        )}
                        <span className="text-gray-100">{log.message}</span>
                      </div>
                    ))}
                  </div>
                  {isGenerating && (
                    <div className="flex items-center space-x-2 mt-2">
                      <div className="animate-pulse text-green-400">█</div>
                      <span className="text-gray-400">Processing...</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {isGenerating && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-blue-700">Generating your journal...</span>
                  {currentAgent && (
                    <span className="text-blue-600 text-sm ml-2">
                      (Agent: {currentAgent})
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Configuration Options */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Theme Selection */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Choose Your Theme
            </h3>
            <div className="space-y-3">
              {AVAILABLE_THEMES.map((theme) => (
                <label
                  key={theme.id}
                  className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50"
                >
                  <input
                    type="radio"
                    value={theme.id}
                    checked={selectedTheme === theme.id}
                    onChange={(e) => setSelectedTheme(e.target.value)}
                    className="mt-1 text-blue-600 focus:ring-blue-500"
                    disabled={isGenerating}
                  />
                  <div>
                    <div className="font-medium text-gray-900">{theme.name}</div>
                    <div className="text-sm text-gray-600">{theme.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </Card>

        {/* Title Style Selection */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Title Style
            </h3>
            <div className="space-y-3">
              {TITLE_STYLES.map((style) => (
                <label
                  key={style.id}
                  className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50"
                >
                  <input
                    type="radio"
                    value={style.id}
                    checked={titleStyle === style.id}
                    onChange={(e) => setTitleStyle(e.target.value)}
                    className="mt-1 text-blue-600 focus:ring-blue-500"
                    disabled={isGenerating}
                  />
                  <div>
                    <div className="font-medium text-gray-900">{style.name}</div>
                    <div className="text-sm text-gray-600">{style.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </Card>

        {/* Research Depth */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Research Depth
            </h3>
            <div className="space-y-2">
              {RESEARCH_DEPTH_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center space-x-3 p-2 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50"
                >
                  <input
                    type="radio"
                    value={option.value}
                    checked={researchDepth === option.value}
                    onChange={(e) => setResearchDepth(e.target.value)}
                    className="text-blue-600 focus:ring-blue-500"
                    disabled={isGenerating}
                  />
                  <span className="font-medium text-gray-900">{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        </Card>

        {/* Additional Options */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Additional Options
            </h3>
            <div className="space-y-4">
              {/* Include Images */}
              <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={includeImages}
                  onChange={(e) => setIncludeImages(e.target.checked)}
                  className="w-4 h-4 text-blue-600 focus:ring-blue-500 rounded"
                  disabled={isGenerating}
                />
                <div>
                  <div className="font-medium text-gray-900">Include AI-Generated Images</div>
                  <div className="text-sm text-gray-600">Add visual elements to your journal</div>
                </div>
              </label>

              {/* Export Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Export Format
                </label>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isGenerating}
                >
                  {EXPORT_FORMATS.map((format) => (
                    <option key={format.value} value={format.value}>
                      {format.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Generate Button */}
      <div className="text-center">
        <Button
          onClick={handleGenerateJournal}
          disabled={isGenerating}
          className="px-8 py-3 text-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isGenerating ? 'Generating...' : 'Create AI Journal'}
        </Button>
      </div>
    </div>
  )
}