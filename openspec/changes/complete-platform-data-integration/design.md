# Complete Platform Integration - Technical Design

## Architecture Overview

This design document outlines the technical architecture for integrating the Journal Craft Crew frontend dashboard with the backend API, enabling complete data flow and user functionality.

## System Architecture

### Current State
```
Frontend (React) ❌ Backend (FastAPI)
    │                     │
    └── No data flow ─────┘
    │
    ├── Empty dashboard state
    ├── Non-functional buttons
    └── No journal creation workflow
```

### Target State
```
Frontend (React) ✅ Backend (FastAPI) ✅ CrewAI System
    │                     │                 │
    └── Real-time API ────┘                 │
    │                                       │
    ├── WebSocket connections ──────────────┘
    │
    ├── Live dashboard data
    ├── Functional journal creation
    ├── Real-time progress tracking
    └── Journal library access
```

## Component Architecture

### Frontend Components

#### 1. Dashboard Data Layer
```typescript
// hooks/useDashboardData.ts
export const useDashboardData = () => {
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshData = useCallback(async () => {
    try {
      setLoading(true);
      const [llmProjects, userProjects] = await Promise.all([
        projectAPI.getLLMProjects(),
        projectAPI.getProjects()
      ]);

      setProjects(llmProjects.projects || []);
      setStats(calculateStats(llmProjects.projects, userProjects));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  return { projects, stats, loading, error, refreshData };
};
```

#### 2. Journal Creation Flow
```typescript
// components/journal/JournalCreationFlow.tsx
interface JournalCreationFlowProps {
  onComplete: (jobId: string) => void;
  onError: (error: string) => void;
}

const JournalCreationFlow: React.FC<JournalCreationFlowProps> = ({ onComplete, onError }) => {
  const [currentStep, setCurrentStep] = useState<'modal' | 'progress' | 'complete'>('modal');
  const [jobId, setJobId] = useState<string | null>(null);

  const handleJournalSubmit = async (preferences: JournalPreferences) => {
    try {
      const response = await apiClient.createJournal(preferences);
      setJobId(response.job_id);
      setCurrentStep('progress');
      onComplete(response.job_id);
    } catch (error) {
      onError(error.message);
    }
  };

  return (
    <>
      {currentStep === 'modal' && (
        <JournalCreationModal onSubmit={handleJournalSubmit} />
      )}
      {currentStep === 'progress' && jobId && (
        <JournalProgress jobId={jobId} onComplete={() => setCurrentStep('complete')} />
      )}
      {currentStep === 'complete' && (
        <JournalResults jobId={jobId} />
      )}
    </>
  );
};
```

#### 3. Progress Visualization
```typescript
// components/journal/AgentProgressTracker.tsx
interface AgentProgressTrackerProps {
  agent: 'research' | 'curation' | 'editing' | 'pdf';
  status: 'pending' | 'active' | 'completed' | 'error';
  progress: number;
  message: string;
}

const AgentProgressTracker: React.FC<AgentProgressTrackerProps> = ({
  agent,
  status,
  progress,
  message
}) => {
  const getAgentIcon = (agentType: string) => {
    switch (agentType) {
      case 'research': return Search;
      case 'curation': return BookOpen;
      case 'editing': return Edit3;
      case 'pdf': return FileText;
      default: return Activity;
    }
  };

  const Icon = getAgentIcon(agent);

  return (
    <div className={`agent-tracker ${status}`}>
      <div className="agent-icon-container">
        <Icon className={`w-6 h-6 ${status === 'active' ? 'animate-pulse' : ''}`} />
      </div>
      <div className="agent-details">
        <h4 className="font-medium capitalize">{agent} Agent</h4>
        <p className="text-sm text-gray-600">{message}</p>
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="progress-text">{progress}%</span>
        </div>
      </div>
    </div>
  );
};
```

### Backend Architecture

#### 1. Job Management System
```python
# services/job_manager.py
class JobManager:
    def __init__(self):
        self.active_jobs: Dict[str, Job] = {}
        self.job_queue = asyncio.Queue()
        self.websocket_connections: Dict[str, List[WebSocket]] = {}

    async def create_job(self, user_id: str, preferences: dict) -> str:
        """Create a new journal creation job."""
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            user_id=user_id,
            preferences=preferences,
            status="queued",
            created_at=datetime.now()
        )

        self.active_jobs[job_id] = job
        await self.job_queue.put(job)

        return job_id

    async def execute_job(self, job: Job):
        """Execute a journal creation job with CrewAI."""
        try:
            await self.update_job_status(job.id, "processing", "Starting journal creation...")

            # CrewAI workflow integration
            result = await self.run_crewai_workflow(job.preferences, job.id)

            await self.update_job_status(job.id, "completed", "Journal creation completed!", result)

        except Exception as e:
            await self.update_job_status(job.id, "failed", f"Journal creation failed: {str(e)}")

    async def run_crewai_workflow(self, preferences: dict, job_id: str):
        """Integrate with existing CrewAI system."""
        # Convert web preferences to CrewAI format
        crew_prefs = self.convert_preferences(preferences)

        # Broadcast progress through WebSocket
        async def progress_callback(agent: str, progress: int, message: str):
            await self.broadcast_progress(job_id, {
                "currentAgent": agent,
                "progress": progress,
                "message": message,
                "estimatedTimeRemaining": self.calculate_time_remaining(agent, progress)
            })

        # Execute CrewAI workflow with progress tracking
        result = await execute_phase1_crew(crew_prefs, progress_callback)
        return result
```

#### 2. WebSocket Integration
```python
# services/websocket_manager.py
class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """Connect a WebSocket to a specific job."""
        await websocket.accept()

        if job_id not in self.connections:
            self.connections[job_id] = []

        self.connections[job_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, job_id: str):
        """Disconnect a WebSocket from a job."""
        if job_id in self.connections:
            self.connections[job_id].remove(websocket)

            if not self.connections[job_id]:
                del self.connections[job_id]

    async def broadcast_to_job(self, job_id: str, message: dict):
        """Broadcast a message to all connections for a job."""
        if job_id in self.connections:
            disconnected = []

            for websocket in self.connections[job_id]:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.append(websocket)

            # Clean up disconnected connections
            for ws in disconnected:
                await self.disconnect(ws, job_id)
```

## Data Flow Architecture

### Journal Creation Flow
```
1. User clicks "Create New Journal"
   ↓
2. JournalCreationModal opens
   ↓
3. User selects preferences and submits
   ↓
4. POST /api/journals/create
   {
     "theme": "Journaling for Anxiety",
     "title": "Calm Reflections",
     "authorStyle": "empathetic",
     "researchDepth": "medium"
   }
   ↓
5. Backend creates job and returns job_id
   ↓
6. Frontend opens JournalProgress component
   ↓
7. WebSocket connection established: ws://localhost:6770/ws/journal/{job_id}
   ↓
8. Backend executes CrewAI workflow with progress callbacks
   ↓
9. Real-time progress updates sent via WebSocket
   ↓
10. Frontend displays agent progress in real-time
   ↓
11. Completion notification sent
   ↓
12. Results displayed with download options
```

### Dashboard Data Flow
```
1. Dashboard component mounts
   ↓
2. useEffect triggers data fetching
   ↓
3. Parallel API calls:
   - GET /api/library/llm-projects (for all generated journals)
   - GET /api/library/projects (for user projects)
   - GET /api/user/stats (for user statistics)
   ↓
4. Data formatted and displayed in UI
   ↓
5. Real-time updates via WebSocket for active jobs
   ↓
6. User can interact with projects and download files
```

## API Design

### Endpoints

#### Journal Creation
```python
POST /api/journals/create
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "theme": "string",
  "title": "string",
  "authorStyle": "string",
  "researchDepth": "light|medium|deep",
  "titleStyle": "string"
}

Response:
{
  "job_id": "string",
  "status": "started|queued",
  "estimated_time": 300
}
```

#### Job Status
```python
GET /api/journals/status/{job_id}
Authorization: Bearer {token}

Response:
{
  "job_id": "string",
  "status": "queued|processing|completed|failed",
  "progress": 0-100,
  "current_agent": "research|curation|editing|pdf",
  "message": "string",
  "estimated_time_remaining": 300,
  "result": {
    "files": ["string"],
    "pdf_path": "string"
  }
}
```

#### File Download
```python
GET /api/journals/{project_id}/download/{file_path:path}
Authorization: Bearer {token}

Response: File stream with appropriate headers
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="{filename}"
```

### WebSocket Protocol

#### Connection
```
ws://localhost:6770/ws/journal/{job_id}
Authorization: Bearer {token} (via query parameter)
```

#### Message Format
```json
{
  "type": "progress|status|error|completion",
  "job_id": "string",
  "current_agent": "research|curation|editing|pdf|completed|error",
  "progress": 0-100,
  "message": "string",
  "estimated_time_remaining": 300,
  "result": {
    "files": ["journal.pdf", "lead_magnet.pdf"],
    "project_path": "/path/to/project"
  }
}
```

## Security Considerations

### Authentication & Authorization
- All API endpoints protected with JWT authentication
- WebSocket connections authenticated via query parameter
- File access restricted to project owner
- Job access restricted to creating user

### Input Validation
- Sanitize all user inputs in journal creation
- Validate file paths to prevent directory traversal
- Rate limit journal creation requests
- Validate WebSocket connection parameters

### Data Protection
- User data isolated by user ID
- File access controlled by ownership
- Job data automatically cleaned up after completion
- WebSocket connections encrypted with WSS in production

## Performance Optimization

### Frontend Optimizations
- Implement React.memo for expensive components
- Use useCallback for event handlers
- Lazy load journal library components
- Implement virtual scrolling for large project lists
- Cache API responses with SWR or React Query

### Backend Optimizations
- Implement connection pooling for database
- Cache file metadata for repeated access
- Use async/await for all I/O operations
- Implement job queuing to prevent resource exhaustion
- Add response compression for file downloads

### WebSocket Optimizations
- Implement connection pooling and heartbeat monitoring
- Batch progress updates to reduce message frequency
- Use binary messages for large data transfers
- Implement automatic reconnection with exponential backoff

## Error Handling Strategy

### Frontend Error Handling
```typescript
// Error boundary for component errors
class JournalCreationErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Journal creation error:', error, errorInfo);
    // Log error to monitoring service
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

### Backend Error Handling
```python
# Centralized error handling
@app.exception_handler(JournalCreationError)
async def journal_creation_error_handler(request: Request, exc: JournalCreationError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "journal_creation_failed",
            "message": str(exc),
            "details": exc.details if hasattr(exc, 'details') else None
        }
    )

# WebSocket error handling
async def handle_websocket_error(websocket: WebSocket, job_id: str, error: Exception):
    await websocket.send_json({
        "type": "error",
        "job_id": job_id,
        "message": f"An error occurred: {str(error)}",
        "recoverable": isinstance(error, RecoverableError)
    })
```

## Deployment Considerations

### Environment Configuration
- Frontend: Configure API URL based on environment
- Backend: Configure database, file storage, and WebSocket settings
- CrewAI: Configure LLM API keys and model settings
- Monitoring: Add health checks and metrics collection

### Scaling Considerations
- Horizontal scaling for backend API instances
- Redis for WebSocket connection management across instances
- File storage in S3 or similar for production
- Database scaling for user and project data

### Monitoring & Logging
- Application performance monitoring (APM)
- WebSocket connection monitoring
- CrewAI workflow execution tracking
- File access and download logging

This technical design provides a comprehensive foundation for implementing the complete platform integration, ensuring robust architecture, security, performance, and maintainability.