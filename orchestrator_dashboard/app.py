#!/usr/bin/env python3
"""
Orchestrator Dashboard - Development Session Management
Real-time monitoring and control for Journal Craft Crew development ecosystem
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import subprocess
import threading
import time
import json
import os
import psutil
from datetime import datetime, timedelta
import signal
import sys

app = Flask(__name__)

# Global variables for session tracking
current_session = None
coding_session_log = []
server_processes = {}
orchestrator_agent = None

# Session history tracking
session_history = []
SESSION_DATA_FILE = "sessions.json"

# Proposals and workflow tracking
master_proposals = []
active_sprints = []
workflow_logs = []
auth_requests = []

class CodingSession:
    def __init__(self):
        self.session_id = f"session_{int(time.time())}"
        self.start_time = datetime.now()
        self.status = "active"  # active, closed, paused
        self.current_task = "Starting orchestrator"
        self.assigned_agent = None
        self.progress = 0
        self.log_entries = []
        self.work_directory = os.getcwd()
        self.focus_area = None

        # Enhanced session tracking for continuity
        self.files_modified = []
        self.tasks_completed = []
        self.commands_executed = []
        self.servers_running = {"backend": False, "frontend": False}
        self.notes = ""
        self.context = {}  # Store development context
        self.last_server_states = {}
        self.git_branch = None
        self.python_venv = None
        self.end_time = None
        self.total_duration = 0  # in minutes

class Proposal:
    def __init__(self, id, title, description, priority, status="proposed", created_by="orchestrator"):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority  # P1, P2, P3, P4
        self.status = status  # proposed, approved, in_progress, completed, rejected
        self.created_by = created_by
        self.created_at = datetime.now()
        self.approved_at = None
        self.assigned_agent = None
        self.progress = 0
        self.tasks = []
        self.dependencies = []

class Sprint:
    def __init__(self, id, title, description, duration_days, status="planning"):
        self.id = id
        self.title = title
        self.description = description
        self.duration_days = duration_days
        self.status = status  # planning, active, completed, paused
        self.created_at = datetime.now()
        self.start_date = None
        self.end_date = None
        self.assigned_proposals = []
        self.team_assignments = {}
        self.progress = 0

class WorkflowLog:
    def __init__(self, id, event_type, description, proposal_id=None, sprint_id=None, agent_name=None):
        self.id = id
        self.event_type = event_type  # proposal_created, sprint_assigned, task_completed, etc.
        self.description = description
        self.proposal_id = proposal_id
        self.sprint_id = sprint_id
        self.agent_name = agent_name
        self.timestamp = datetime.now()
        self.metadata = {}

class AuthRequest:
    def __init__(self, id, request_type, description, requested_by, priority="medium"):
        self.id = id
        self.request_type = request_type  # api_access, system_change, deployment, etc.
        self.description = description
        self.requested_by = requested_by
        self.priority = priority
        self.status = "pending"  # pending, approved, rejected, requires_review
        self.created_at = datetime.now()
        self.reviewed_by = None
        self.reviewed_at = None
        self.comments = ""

class OrchestratorAgent:
    def __init__(self):
        self.status = "active"
        self.current_task = "Monitoring development environment"
        self.agent_processes = {
            "InfraDeploy": {"status": "idle", "task": None, "progress": 0},
            "CodeRefactor": {"status": "idle", "task": None, "progress": 0},
            "APITestAgent": {"status": "idle", "task": None, "progress": 0},
            "QualityAssurance": {"status": "idle", "task": None, "progress": 0},
            "ConfigManage": {"status": "idle", "task": None, "progress": 0},
            "MonitorAnalytics": {"status": "idle", "task": None, "progress": 0},
            "SecurityCompliance": {"status": "idle", "task": None, "progress": 0}
        }
        self.roadmap_progress = {
            "P1 (Critical)": {"tasks": 2, "completed": 0, "progress": 0},
            "P2 (High)": {"tasks": 2, "completed": 0, "progress": 0},
            "P3 (Medium)": {"tasks": 2, "completed": 0, "progress": 0},
            "P4 (Low)": {"tasks": 2, "completed": 0, "progress": 0}
        }

    def update_agent_status(self, agent_name, status, task=None, progress=0):
        if agent_name in self.agent_processes:
            self.agent_processes[agent_name]["status"] = status
            self.agent_processes[agent_name]["task"] = task
            self.agent_processes[agent_name]["progress"] = progress
            log_entry(f"Agent {agent_name}: {status} - {task} ({progress}%)")

    def get_agent_status(self, agent_name):
        return self.agent_processes.get(agent_name, {"status": "unknown", "task": None, "progress": 0})

    def update_roadmap_progress(self, priority, completed, total, progress):
        if priority in self.roadmap_progress:
            self.roadmap_progress[priority]["completed"] = completed
            self.roadmap_progress[priority]["tasks"] = total
            self.roadmap_progress[priority]["progress"] = progress
            log_entry(f"Roadmap {priority}: {progress}% complete ({completed}/{total} tasks)")

def log_entry(message):
    """Add entry to session log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "message": message, "type": "info"}
    coding_session_log.append(entry)
    if current_session:
        current_session.log_entries.append(entry)
    print(f"[{timestamp}] {message}")

def is_backend_process(proc):
    """Enhanced backend process detection"""
    cmdline = proc.info.get('cmdline', [])
    if not cmdline:
        return False

    cmdline_str = ' '.join(cmdline)
    # Enhanced patterns for backend detection
    return (
        proc.info['name'] == 'python' and (
            'unified_backend.py' in cmdline_str or
            'journal-platform-backend' in cmdline_str or
            '--port 6770' in cmdline_str
        )
    )

def is_frontend_process(proc):
    """Enhanced frontend process detection"""
    cmdline = proc.info.get('cmdline', [])
    if not cmdline:
        return False

    cmdline_str = ' '.join(cmdline).lower()
    # Enhanced patterns for frontend detection
    return (
        proc.info['name'] == 'node' and (
            'vite' in cmdline_str or
            'npm run dev' in cmdline_str or
            'journal-platform-frontend' in cmdline_str or
            '--port 5173' in cmdline_str
        )
    )

def check_port_status(port, timeout=1):
    """Fallback port-based detection"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def check_server_status():
    """Check status of Journal Craft servers with enhanced detection"""
    status = {
        "backend": {
            "running": False,
            "port": 6770,
            "pid": None,
            "cpu": 0,
            "memory": 0,
            "url": "https://localhost:6770",
            "ssl_enabled": True,
            "uptime": None,
            "status": "stopped",
            "last_check": datetime.now().isoformat()
        },
        "frontend": {
            "running": False,
            "port": 5173,
            "pid": None,
            "cpu": 0,
            "memory": 0,
            "url": "http://localhost:5173",
            "ssl_enabled": False,
            "uptime": None,
            "status": "stopped",
            "last_check": datetime.now().isoformat()
        },
        "orchestrator": {
            "running": True,
            "port": 6771,
            "pid": os.getpid(),
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "url": "http://localhost:6771",
            "ssl_enabled": False,
            "uptime": time.time() - psutil.boot_time(),
            "status": "running",
            "last_check": datetime.now().isoformat()
        }
    }

    # Check backend server with enhanced detection
    backend_found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            if is_backend_process(proc):
                # This is our backend server
                status["backend"]["running"] = True
                status["backend"]["pid"] = proc.info['pid']
                status["backend"]["cpu"] = proc.info['cpu_percent']
                status["backend"]["memory"] = proc.info['memory_percent']
                status["backend"]["uptime"] = time.time() - proc.info['create_time']
                status["backend"]["status"] = "running"
                backend_found = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Fallback: Check if backend port is active
    if not backend_found and check_port_status(6770):
        status["backend"]["running"] = True
        status["backend"]["status"] = "running"
        status["backend"]["cpu"] = 0
        status["backend"]["memory"] = 0
        status["backend"]["uptime"] = 0

    # Check frontend server with enhanced detection
    frontend_found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            if is_frontend_process(proc):
                # This is our frontend server
                status["frontend"]["running"] = True
                status["frontend"]["pid"] = proc.info['pid']
                status["frontend"]["cpu"] = proc.info['cpu_percent']
                status["frontend"]["memory"] = proc.info['memory_percent']
                status["frontend"]["uptime"] = time.time() - proc.info['create_time']
                status["frontend"]["status"] = "running"
                frontend_found = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Fallback: Check if frontend port is active
    if not frontend_found and check_port_status(5173):
        status["frontend"]["running"] = True
        status["frontend"]["status"] = "running"
        status["frontend"]["cpu"] = 0
        status["frontend"]["memory"] = 0
        status["frontend"]["uptime"] = 0

    return status

def start_journal_craft_servers():
    """Start Journal Craft Crew servers"""
    success = {"backend": False, "frontend": False}

    # Check if servers are already running
    status = check_server_status()

    # Start backend server if not running
    if not status["backend"]["running"]:
        log_entry("Starting Journal Craft Crew backend server...")
        try:
            backend_cmd = [
                "cd", "/home/alf/Documents/7.CodeProjects/Journal Craft Crew/journal-platform-backend",
                "source", ".venv/bin/activate",
                "python", "unified_backend.py"
            ]
            process = subprocess.Popen(
                ' '.join(backend_cmd),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            server_processes["backend"] = process
            success["backend"] = True
            log_entry("Backend server started successfully")
        except Exception as e:
            log_entry(f"Failed to start backend server: {e}")
    else:
        log_entry("Backend server is already running")
        success["backend"] = True

    # Start frontend server if not running
    if not status["frontend"]["running"]:
        log_entry("Starting Journal Craft Crew frontend server...")
        try:
            frontend_cmd = [
                "cd", "/home/alf/Documents/7.CodeProjects/Journal Craft Crew/journal-platform-frontend",
                "npm", "run", "dev"
            ]
            process = subprocess.Popen(
                ' '.join(frontend_cmd),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            server_processes["frontend"] = process
            success["frontend"] = True
            log_entry("Frontend server started successfully")
        except Exception as e:
            log_entry(f"Failed to start frontend server: {e}")
    else:
        log_entry("Frontend server is already running")
        success["frontend"] = True

    return success

def restart_journal_craft_servers():
    """Restart Journal Craft Crew servers"""
    log_entry("Restarting Journal Craft Crew servers...")

    # Stop existing servers
    stop_journal_craft_servers()

    # Wait a moment for processes to stop
    time.sleep(2)

    # Start servers
    return start_journal_craft_servers()

def stop_journal_craft_servers():
    """Stop Journal Craft Crew servers"""
    log_entry("Stopping Journal Craft Crew servers...")

    # Find and stop backend process
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and proc.info['name'] == 'python' and 'unified_backend.py' in ' '.join(cmdline):
                log_entry(f"Stopping backend server (PID: {proc.info['pid']})")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Find and stop frontend process
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and proc.info['name'] == 'node' and ('npm run dev' in cmdline or 'vite' in cmdline):
                log_entry(f"Stopping frontend server (PID: {proc.info['pid']})")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    log_entry("Journal Craft Crew servers stopped")

def start_coding_session():
    """Start a new coding session"""
    global current_session
    current_session = CodingSession()
    log_entry(f"Started coding session: {current_session.session_id}")
    return current_session

def get_system_info():
    """Get system information"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "processes": len(list(psutil.process_iter())),
        "uptime": time.time() - psutil.boot_time()
    }

@app.route('/')
def index():
    """Main dashboard page"""
    server_status = check_server_status()
    system_info = get_system_info()

    return render_template('dashboard.html',
                         session=current_session,
                         orchestrator_agent=orchestrator_agent,
                         server_status=server_status,
                         system_info=system_info,
                         coding_log=coding_session_log[-20:])

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new coding session"""
    session = start_coding_session()
    if orchestrator_agent:
        orchestrator_agent.current_task = "New coding session started"
    return jsonify({
        "success": True,
        "session_id": session.session_id,
        "message": f"Started coding session: {session.session_id}"
    })

@app.route('/api/session/status')
def get_session_status():
    """Get current session status"""
    if current_session:
        return jsonify({
            "active": True,
            "session_id": current_session.session_id,
            "start_time": current_session.start_time.isoformat(),
            "current_task": current_session.current_task,
            "assigned_agent": current_session.assigned_agent,
            "progress": current_session.progress,
            "status": current_session.status,
            "work_directory": current_session.work_directory,
            "focus_area": current_session.focus_area,
            "log_entries": current_session.log_entries[-10:]
        })
    else:
        return jsonify({
            "active": False,
            "message": "No active coding session"
        })

def session_to_dict(session):
    """Convert CodingSession to dictionary for JSON serialization"""
    return {
        "session_id": session.session_id,
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "status": session.status,
        "current_task": session.current_task,
        "assigned_agent": session.assigned_agent,
        "progress": session.progress,
        "log_entries": session.log_entries,
        "work_directory": session.work_directory,
        "focus_area": session.focus_area,
        "files_modified": session.files_modified,
        "tasks_completed": session.tasks_completed,
        "commands_executed": session.commands_executed,
        "servers_running": session.servers_running,
        "notes": session.notes,
        "context": session.context,
        "last_server_states": session.last_server_states,
        "git_branch": session.git_branch,
        "python_venv": session.python_venv,
        "total_duration": session.total_duration
    }

def dict_to_session(data):
    """Convert dictionary back to CodingSession object"""
    session = CodingSession()
    session.session_id = data["session_id"]
    session.start_time = datetime.fromisoformat(data["start_time"])
    session.end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
    session.status = data["status"]
    session.current_task = data["current_task"]
    session.assigned_agent = data["assigned_agent"]
    session.progress = data["progress"]
    session.log_entries = data["log_entries"]
    session.work_directory = data["work_directory"]
    session.focus_area = data["focus_area"]
    session.files_modified = data["files_modified"]
    session.tasks_completed = data["tasks_completed"]
    session.commands_executed = data["commands_executed"]
    session.servers_running = data["servers_running"]
    session.notes = data["notes"]
    session.context = data["context"]
    session.last_server_states = data["last_server_states"]
    session.git_branch = data["git_branch"]
    session.python_venv = data["python_venv"]
    session.total_duration = data["total_duration"]
    return session

def save_sessions():
    """Save session history to JSON file"""
    try:
        with open(SESSION_DATA_FILE, 'w') as f:
            json.dump([session_to_dict(session) for session in session_history], f, indent=2)
        log_entry(f"Saved {len(session_history)} sessions to {SESSION_DATA_FILE}")
    except Exception as e:
        log_entry(f"Error saving sessions: {str(e)}")

def load_sessions():
    """Load session history from JSON file"""
    global session_history
    try:
        if os.path.exists(SESSION_DATA_FILE):
            with open(SESSION_DATA_FILE, 'r') as f:
                data = json.load(f)
                session_history = [dict_to_session(session_data) for session_data in data]
                log_entry(f"Loaded {len(session_history)} sessions from {SESSION_DATA_FILE}")
    except Exception as e:
        log_entry(f"Error loading sessions: {str(e)}")
        session_history = []

def capture_session_state():
    """Capture current development state for session continuity"""
    if current_session:
        # Capture server states
        server_status = check_server_status()
        current_session.last_server_states = {
            "backend": server_status["backend"],
            "frontend": server_status["frontend"]
        }

        # Capture git branch if in a git repository
        try:
            import subprocess
            result = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True, cwd=current_session.work_directory)
            if result.returncode == 0:
                current_session.git_branch = result.stdout.strip()
        except:
            current_session.git_branch = None

        # Capture Python virtual environment
        current_session.python_venv = os.environ.get('VIRTUAL_ENV', None)

        # Update duration
        if current_session.start_time:
            duration = datetime.now() - current_session.start_time
            current_session.total_duration = int(duration.total_seconds() / 60)  # in minutes

@app.route('/api/servers/start', methods=['POST'])
def start_servers():
    """Start Journal Craft Crew servers"""
    success = start_journal_craft_servers()
    return jsonify({
        "success": all(success.values()),
        "backend": success["backend"],
        "frontend": success["frontend"],
        "message": "Servers started successfully" if all(success.values()) else "Some servers failed to start"
    })

@app.route('/api/servers/restart', methods=['POST'])
def restart_servers():
    """Restart Journal Craft Crew servers"""
    success = restart_journal_craft_servers()
    return jsonify({
        "success": all(success.values()),
        "backend": success["backend"],
        "frontend": success["frontend"],
        "message": "Servers restarted successfully" if all(success.values()) else "Some servers failed to restart"
    })

@app.route('/api/servers/stop', methods=['POST'])
def stop_servers():
    """Stop Journal Craft Crew servers"""
    stop_journal_craft_servers()
    return jsonify({
        "success": True,
        "message": "Servers stopped successfully"
    })

@app.route('/api/servers/status')
def get_servers_status():
    """Get server status"""
    return jsonify(check_server_status())

# Individual server control endpoints
@app.route('/api/servers/backend/start', methods=['POST'])
def start_backend():
    """Start only the backend server"""
    result = start_backend_server()
    return jsonify(result)

@app.route('/api/servers/backend/stop', methods=['POST'])
def stop_backend():
    """Stop only the backend server"""
    result = stop_backend_server()
    return jsonify(result)

@app.route('/api/servers/backend/restart', methods=['POST'])
def restart_backend():
    """Restart only the backend server"""
    result = restart_backend_server()
    return jsonify(result)

@app.route('/api/servers/frontend/start', methods=['POST'])
def start_frontend():
    """Start only the frontend server"""
    result = start_frontend_server()
    return jsonify(result)

@app.route('/api/servers/frontend/stop', methods=['POST'])
def stop_frontend():
    """Stop only the frontend server"""
    result = stop_frontend_server()
    return jsonify(result)

@app.route('/api/servers/frontend/restart', methods=['POST'])
def restart_frontend():
    """Restart only the frontend server"""
    result = restart_frontend_server()
    return jsonify(result)

# Session Management Endpoints
@app.route('/api/session/close', methods=['POST'])
def close_session():
    """Close current session and save its state"""
    global current_session

    if not current_session:
        return jsonify({
            "success": False,
            "message": "No active session to close"
        })

    try:
        # Capture final session state
        capture_session_state()

        # Mark session as closed and record end time
        current_session.status = "closed"
        current_session.end_time = datetime.now()

        # Add to session history
        session_history.append(current_session)

        # Save sessions to disk
        save_sessions()

        session_id = current_session.session_id
        log_entry(f"Session {session_id} closed and saved")

        # Clear current session
        current_session = None

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": f"Session {session_id} closed and saved successfully",
            "total_sessions": len(session_history)
        })

    except Exception as e:
        log_entry(f"Error closing session: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error closing session: {str(e)}"
        })

@app.route('/api/session/history', methods=['GET'])
def get_session_history():
    """Get session history"""
    try:
        return jsonify({
            "success": True,
            "sessions": [session_to_dict(session) for session in session_history[-10:]],  # Last 10 sessions
            "total_sessions": len(session_history)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting session history: {str(e)}"
        })

@app.route('/api/session/continue/<session_id>', methods=['POST'])
def continue_session(session_id):
    """Continue a previous session"""
    global current_session

    if current_session:
        return jsonify({
            "success": False,
            "message": "Please close the current session before continuing another one"
        })

    try:
        # Find the session to continue
        target_session = None
        for session in session_history:
            if session.session_id == session_id:
                target_session = session
                break

        if not target_session:
            return jsonify({
                "success": False,
                "message": f"Session {session_id} not found"
            })

        # Capture the old session state
        old_session_data = session_to_dict(target_session)

        # Create new session based on old one
        new_session = CodingSession()
        new_session.current_task = f"Continuing from session {session_id}"
        new_session.focus_area = target_session.focus_area
        new_session.work_directory = target_session.work_directory
        new_session.context = target_session.context.copy()
        new_session.last_server_states = target_session.last_server_states.copy()
        new_session.git_branch = target_session.git_branch
        new_session.python_venv = target_session.python_venv
        new_session.notes = f"Continued from session {session_id}\n\nPrevious notes:\n{target_session.notes}"

        # Add previous tasks and commands to new session for context
        new_session.tasks_completed = target_session.tasks_completed.copy()
        new_session.commands_executed = target_session.commands_executed.copy()
        new_session.files_modified = target_session.files_modified.copy()

        # Set as current session
        current_session = new_session

        # Log the continuation
        log_entry(f"Continued session from {session_id}")

        return jsonify({
            "success": True,
            "session_id": new_session.session_id,
            "previous_session_id": session_id,
            "work_directory": new_session.work_directory,
            "git_branch": new_session.git_branch,
            "last_server_states": new_session.last_server_states,
            "context": new_session.context,
            "message": f"Successfully continued from session {session_id}"
        })

    except Exception as e:
        log_entry(f"Error continuing session {session_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error continuing session: {str(e)}"
        })

@app.route('/api/session/update', methods=['POST'])
def update_session():
    """Update current session with new information"""
    global current_session

    if not current_session:
        return jsonify({
            "success": False,
            "message": "No active session to update"
        })

    try:
        data = request.get_json() or {}

        # Update session fields
        if "current_task" in data:
            current_session.current_task = data["current_task"]

        if "focus_area" in data:
            current_session.focus_area = data["focus_area"]

        if "notes" in data:
            current_session.notes = data["notes"]

        if "context" in data:
            current_session.context.update(data["context"])

        if "files_modified" in data:
            current_session.files_modified.extend(data["files_modified"])

        if "tasks_completed" in data:
            current_session.tasks_completed.extend(data["tasks_completed"])

        if "commands_executed" in data:
            current_session.commands_executed.extend(data["commands_executed"])

        # Capture current state
        capture_session_state()

        return jsonify({
            "success": True,
            "message": "Session updated successfully"
        })

    except Exception as e:
        log_entry(f"Error updating session: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error updating session: {str(e)}"
        })

@app.route('/api/orchestrator/status')
def get_orchestrator_status():
    """Get orchestrator agent status"""
    if orchestrator_agent:
        return jsonify({
            "status": orchestrator_agent.status,
            "current_task": orchestrator_agent.current_task,
            "agent_processes": orchestrator_agent.agent_processes,
            "roadmap_progress": orchestrator_agent.roadmap_progress
        })
    else:
        return jsonify({
            "status": "inactive",
            "message": "Orchestrator agent not initialized"
        })

@app.route('/api/orchestrator/assign_agent', methods=['POST'])
def assign_agent():
    """Assign agent to current session"""
    data = request.get_json()
    agent_name = data.get('agent')
    if current_session:
        current_session.assigned_agent = agent_name
        current_session.current_task = f"Working with {agent_name}"
        log_entry(f"Assigned agent {agent_name} to session {current_session.session_id}")
    return jsonify({"success": True, "agent": agent_name})

@app.route('/api/system/info')
def get_system_info_route():
    """Get system information"""
    return jsonify(get_system_info())

@app.route('/api/logs')
def get_logs():
    """Get recent log entries"""
    return jsonify({
        "logs": coding_session_log[-50:],
        "count": len(coding_session_log)
    })

@app.route('/journal-frontend')
def journal_frontend():
    """Redirect to Journal Craft Crew frontend"""
    return jsonify({
        "url": "http://localhost:5173",
        "message": "Journal Craft Crew Frontend",
        "status": "Available" if check_server_status()["frontend"]["running"] else "Not Running"
    })

@app.route('/agent-overview')
def agent_overview():
    """Agent System Overview page"""
    return render_template('agent_overview.html')

# Proposals Management Endpoints
@app.route('/api/proposals')
def get_proposals():
    """Get all master proposals"""
    return jsonify({
        "proposals": [vars(p) for p in master_proposals],
        "count": len(master_proposals)
    })

@app.route('/api/proposals/<int:proposal_id>')
def get_proposal(proposal_id):
    """Get specific proposal details"""
    proposal = next((p for p in master_proposals if p.id == proposal_id), None)
    if proposal:
        return jsonify(vars(proposal))
    return jsonify({"error": "Proposal not found"}), 404

@app.route('/api/proposals', methods=['POST'])
def create_proposal():
    """Create a new proposal"""
    data = request.get_json()
    proposal = Proposal(
        id=len(master_proposals) + 1,
        title=data.get('title'),
        description=data.get('description'),
        priority=data.get('priority'),
        created_by=data.get('created_by', 'orchestrator')
    )
    master_proposals.append(proposal)

    # Log workflow event
    workflow_log = WorkflowLog(
        id=len(workflow_logs) + 1,
        event_type="proposal_created",
        description=f"New proposal '{proposal.title}' created",
        proposal_id=proposal.id,
        agent_name=proposal.created_by
    )
    workflow_logs.append(workflow_log)

    log_entry(f"Created new proposal: {proposal.title}")
    return jsonify({"success": True, "proposal": vars(proposal)})

@app.route('/api/proposals/<int:proposal_id>/approve', methods=['POST'])
def approve_proposal(proposal_id):
    """Approve a proposal"""
    proposal = next((p for p in master_proposals if p.id == proposal_id), None)
    if proposal:
        proposal.status = "approved"
        proposal.approved_at = datetime.now()

        # Log workflow event
        workflow_log = WorkflowLog(
            id=len(workflow_logs) + 1,
            event_type="proposal_approved",
            description=f"Proposal '{proposal.title}' approved",
            proposal_id=proposal_id
        )
        workflow_logs.append(workflow_log)

        log_entry(f"Approved proposal: {proposal.title}")
        return jsonify({"success": True, "proposal": vars(proposal)})
    return jsonify({"error": "Proposal not found"}), 404

# Sprint Management Endpoints
@app.route('/api/sprints')
def get_sprints():
    """Get all active sprints"""
    return jsonify({
        "sprints": [vars(s) for s in active_sprints],
        "count": len(active_sprints)
    })

@app.route('/api/sprints', methods=['POST'])
def create_sprint():
    """Create a new sprint"""
    data = request.get_json()
    sprint = Sprint(
        id=len(active_sprints) + 1,
        title=data.get('title'),
        description=data.get('description'),
        duration_days=data.get('duration_days', 14)
    )
    active_sprints.append(sprint)

    # Log workflow event
    workflow_log = WorkflowLog(
        id=len(workflow_logs) + 1,
        event_type="sprint_created",
        description=f"New sprint '{sprint.title}' created",
        sprint_id=sprint.id,
        agent_name="orchestrator"
    )
    workflow_logs.append(workflow_log)

    log_entry(f"Created new sprint: {sprint.title}")
    return jsonify({"success": True, "sprint": vars(sprint)})

@app.route('/api/sprints/<int:sprint_id>/assign-proposal', methods=['POST'])
def assign_proposal_to_sprint(sprint_id):
    """Assign proposal to sprint"""
    data = request.get_json()
    proposal_id = data.get('proposal_id')

    sprint = next((s for s in active_sprints if s.id == sprint_id), None)
    proposal = next((p for p in master_proposals if p.id == proposal_id), None)

    if sprint and proposal:
        sprint.assigned_proposals.append(proposal_id)
        proposal.status = "in_progress"

        # Log workflow event
        workflow_log = WorkflowLog(
            id=len(workflow_logs) + 1,
            event_type="proposal_assigned_to_sprint",
            description=f"Proposal '{proposal.title}' assigned to sprint '{sprint.title}'",
            proposal_id=proposal_id,
            sprint_id=sprint_id
        )
        workflow_logs.append(workflow_log)

        log_entry(f"Assigned proposal '{proposal.title}' to sprint '{sprint.title}'")
        return jsonify({"success": True})
    return jsonify({"error": "Sprint or proposal not found"}), 404

@app.route('/api/sprints/<int:sprint_id>/assign-team', methods=['POST'])
def assign_team_to_sprint(sprint_id):
    """Assign team members to sprint"""
    data = request.get_json()
    team_assignments = data.get('team_assignments', {})

    sprint = next((s for s in active_sprints if s.id == sprint_id), None)
    if sprint:
        sprint.team_assignments = team_assignments
        sprint.status = "active"

        # Log workflow event
        workflow_log = WorkflowLog(
            id=len(workflow_logs) + 1,
            event_type="team_assigned",
            description=f"Team assigned to sprint '{sprint.title}': {', '.join(team_assignments.keys())}",
            sprint_id=sprint_id
        )
        workflow_logs.append(workflow_log)

        log_entry(f"Assigned team to sprint: {sprint.title}")
        return jsonify({"success": True})
    return jsonify({"error": "Sprint not found"}), 404

# Workflow Logging Endpoints
@app.route('/api/workflow/logs')
def get_workflow_logs():
    """Get workflow logs"""
    return jsonify({
        "logs": [vars(log) for log in workflow_logs[-50:]],  # Last 50 logs
        "count": len(workflow_logs)
    })

@app.route('/api/workflow/log', methods=['POST'])
def create_workflow_log():
    """Create a new workflow log entry"""
    data = request.get_json()
    workflow_log = WorkflowLog(
        id=len(workflow_logs) + 1,
        event_type=data.get('event_type'),
        description=data.get('description'),
        proposal_id=data.get('proposal_id'),
        sprint_id=data.get('sprint_id'),
        agent_name=data.get('agent_name')
    )
    workflow_logs.append(workflow_log)
    log_entry(f"Workflow: {workflow_log.description}")
    return jsonify({"success": True, "log": vars(workflow_log)})

# Authorization Request Endpoints
@app.route('/api/auth/requests')
def get_auth_requests():
    """Get all authorization requests"""
    return jsonify({
        "requests": [vars(req) for req in auth_requests],
        "count": len(auth_requests)
    })

@app.route('/api/auth/requests', methods=['POST'])
def create_auth_request():
    """Create a new authorization request"""
    data = request.get_json()
    auth_req = AuthRequest(
        id=len(auth_requests) + 1,
        request_type=data.get('request_type'),
        description=data.get('description'),
        requested_by=data.get('requested_by'),
        priority=data.get('priority', 'medium')
    )
    auth_requests.append(auth_req)

    # Log workflow event
    workflow_log = WorkflowLog(
        id=len(workflow_logs) + 1,
        event_type="auth_request_created",
        description=f"Authorization request: {auth_req.description}",
        agent_name=auth_req.requested_by
    )
    workflow_logs.append(workflow_log)

    log_entry(f"Created auth request: {auth_req.description}")
    return jsonify({"success": True, "request": vars(auth_req)})

@app.route('/api/auth/requests/<int:request_id>/review', methods=['POST'])
def review_auth_request(request_id):
    """Review and approve/reject authorization request"""
    data = request.get_json()
    action = data.get('action')  # approve or reject
    comments = data.get('comments', '')
    reviewed_by = data.get('reviewed_by', 'orchestrator')

    auth_req = next((req for req in auth_requests if req.id == request_id), None)
    if auth_req:
        auth_req.status = "approved" if action == "approve" else "rejected"
        auth_req.reviewed_by = reviewed_by
        auth_req.reviewed_at = datetime.now()
        auth_req.comments = comments

        # Log workflow event
        workflow_log = WorkflowLog(
            id=len(workflow_logs) + 1,
            event_type="auth_request_reviewed",
            description=f"Authorization request {action}: {auth_req.description}",
            agent_name=reviewed_by
        )
        workflow_logs.append(workflow_log)

        log_entry(f"Authorization request {action}: {auth_req.description}")
        return jsonify({"success": True, "request": vars(auth_req)})
    return jsonify({"error": "Auth request not found"}), 404

# Initialize sample data
def initialize_sample_data():
    """Initialize sample proposals, sprints, and auth requests"""
    if not master_proposals:
        # Sample proposals
        proposal1 = Proposal(
            id=1,
            title="Replace Demo Data with Real AI Integration",
            description="Remove all demo/placeholder data and implement real OpenAI API integration for CrewAI workflows",
            priority="P1",
            status="approved",
            created_by="orchestrator"
        )
        proposal1.approved_at = datetime.now()
        proposal1.assigned_agent = "CodeRefactor"
        proposal1.progress = 75

        proposal2 = Proposal(
            id=2,
            title="Production Security Hardening",
            description="Implement comprehensive security measures including SSL, environment variables, and secure authentication",
            priority="P1",
            status="in_progress",
            created_by="orchestrator"
        )
        proposal2.assigned_agent = "SecurityCompliance"
        proposal2.progress = 60

        proposal3 = Proposal(
            id=3,
            title="Project Cleanup & Code Optimization",
            description="Remove redundant code files and optimize performance across all modules",
            priority="P2",
            status="approved",
            created_by="orchestrator"
        )
        proposal3.assigned_agent = "InfraDeploy"
        proposal3.progress = 45

        master_proposals.extend([proposal1, proposal2, proposal3])

        # Sample sprint
        sprint1 = Sprint(
            id=1,
            title="Sprint 1: Critical Infrastructure",
            description="Focus on P1 critical tasks and security hardening",
            duration_days=14,
            status="active"
        )
        sprint1.start_date = datetime.now()
        sprint1.end_date = sprint1.start_date + timedelta(days=14)
        sprint1.assigned_proposals = [1, 2, 3]
        sprint1.team_assignments = {
            "CodeRefactor": "AI Integration & Demo Data Replacement",
            "SecurityCompliance": "Security Hardening & SSL Implementation",
            "InfraDeploy": "Code Cleanup & Performance Optimization",
            "APITestAgent": "API Testing & Validation"
        }
        sprint1.progress = 65

        active_sprints.append(sprint1)

        # Sample auth requests
        auth1 = AuthRequest(
            id=1,
            request_type="deployment",
            description="Request to deploy CrewAI integration changes to production",
            requested_by="CodeRefactor",
            priority="high"
        )
        auth1.status = "pending"

        auth2 = AuthRequest(
            id=2,
            request_type="api_access",
            description="Request access to OpenAI API for production testing",
            requested_by="SecurityCompliance",
            priority="critical"
        )
        auth2.status = "approved"
        auth2.reviewed_by = "orchestrator"
        auth2.reviewed_at = datetime.now()

        auth_requests.extend([auth1, auth2])

        # Sample workflow logs
        log1 = WorkflowLog(
            id=1,
            event_type="proposal_created",
            description="Critical infrastructure proposal submitted for review",
            proposal_id=1,
            agent_name="orchestrator"
        )

        log2 = WorkflowLog(
            id=2,
            event_type="sprint_created",
            description="Sprint 1 initiated with focus on P1 deliverables",
            sprint_id=1,
            agent_name="orchestrator"
        )

        log3 = WorkflowLog(
            id=3,
            event_type="team_assigned",
            description="Development team assigned to sprint tasks",
            sprint_id=1
        )

        workflow_logs.extend([log1, log2, log3])

# Initialize orchestrator agent
orchestrator_agent = OrchestratorAgent()
log_entry("Orchestrator Dashboard initialized")
initialize_sample_data()
log_entry("Checking Journal Craft Crew server status...")

# Check current server status
initial_status = check_server_status()
if initial_status["backend"]["running"]:
    log_entry("✅ Backend server is running")
else:
    log_entry("⚠️ Backend server is not running")

if initial_status["frontend"]["running"]:
    log_entry("✅ Frontend server is running")
else:
    log_entry("⚠️ Frontend server is not running")

# Enhanced server control functions
def start_backend_server():
    """Start only the backend server"""
    status = check_server_status()
    if status["backend"]["running"]:
        log_entry("Backend server is already running")
        return {"success": True, "message": "Backend already running"}

    log_entry("🚀 Starting Journal Craft Crew backend server...")
    try:
        backend_cmd = [
            "cd", "/home/alf/Documents/7.CodeProjects/Journal Craft Crew/journal-platform-backend",
            "source", ".venv/bin/activate",
            "python", "unified_backend.py"
        ]
        process = subprocess.Popen(
            ' '.join(backend_cmd),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        server_processes["backend"] = process
        log_entry("✅ Backend server started successfully")
        return {"success": True, "message": "Backend started successfully"}
    except Exception as e:
        log_entry(f"❌ Failed to start backend server: {e}")
        return {"success": False, "message": str(e)}

def start_frontend_server():
    """Start only the frontend server"""
    status = check_server_status()
    if status["frontend"]["running"]:
        log_entry("Frontend server is already running")
        return {"success": True, "message": "Frontend already running"}

    log_entry("🚀 Starting Journal Craft Crew frontend server...")
    try:
        frontend_cmd = [
            "cd", "/home/alf/Documents/7.CodeProjects/Journal Craft Crew/journal-platform-frontend",
            "npm", "run", "dev"
        ]
        process = subprocess.Popen(
            ' '.join(frontend_cmd),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        server_processes["frontend"] = process
        log_entry("✅ Frontend server started successfully")
        return {"success": True, "message": "Frontend started successfully"}
    except Exception as e:
        log_entry(f"❌ Failed to start frontend server: {e}")
        return {"success": False, "message": str(e)}

def stop_backend_server():
    """Stop only the backend server"""
    log_entry("🛑 Stopping backend server...")
    stopped = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and proc.info['name'] == 'python' and 'unified_backend.py' in ' '.join(cmdline):
                log_entry(f"Stopping backend server (PID: {proc.info['pid']})")
                proc.terminate()
                stopped = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if stopped:
        log_entry("✅ Backend server stopped successfully")
        return {"success": True, "message": "Backend stopped successfully"}
    else:
        log_entry("⚠️ Backend server was not running")
        return {"success": True, "message": "Backend was not running"}

def stop_frontend_server():
    """Stop only the frontend server"""
    log_entry("🛑 Stopping frontend server...")
    stopped = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and proc.info['name'] == 'node' and ('npm run dev' in cmdline or 'vite' in cmdline):
                log_entry(f"Stopping frontend server (PID: {proc.info['pid']})")
                proc.terminate()
                stopped = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if stopped:
        log_entry("✅ Frontend server stopped successfully")
        return {"success": True, "message": "Frontend stopped successfully"}
    else:
        log_entry("⚠️ Frontend server was not running")
        return {"success": True, "message": "Frontend was not running"}

def restart_backend_server():
    """Restart the backend server"""
    log_entry("🔄 Restarting backend server...")
    stop_backend_server()
    time.sleep(2)
    return start_backend_server()

def restart_frontend_server():
    """Restart the frontend server"""
    log_entry("🔄 Restarting frontend server...")
    stop_frontend_server()
    time.sleep(2)
    return start_frontend_server()

# Start a coding session automatically
start_coding_session()

if __name__ == '__main__':
    # Load session history on startup
    load_sessions()

    log_entry("Starting Orchestrator Dashboard on port 6771")
    log_entry("Dashboard available at: http://localhost:6771")
    log_entry("Journal Craft Crew Frontend: http://localhost:5173")
    log_entry("🔒 Backend API: https://localhost:6770 (SSL/TLS Enabled)")
    if session_history:
        log_entry(f"Loaded {len(session_history)} previous sessions")

    app.run(host='0.0.0.0', port=6771, debug=True, threaded=True)