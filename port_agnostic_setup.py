#!/usr/bin/env python3
"""
Comprehensive Port-Agnostic Setup Script for Journal Craft Crew
Automatically finds open ports and configures the entire application
"""

import os
import sys
import json
import time
import socket
import subprocess
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading
import requests
from datetime import datetime

class PortManager:
    """Manages port discovery and allocation"""

    def __init__(self):
        self.allocated_ports = {}
        self.preferred_ranges = {
            'frontend': (5100, 5999),
            'backend': (6000, 6999),
            'database': (2700, 2799),
            'redis': (6300, 6399),
            'websocket': (7000, 7099)
        }

    def find_open_port(self, service: str, preferred: Optional[int] = None) -> int:
        """Find an open port for a service"""
        if preferred and self.is_port_open(preferred):
            self.allocated_ports[service] = preferred
            return preferred

        range_start, range_end = self.preferred_ranges.get(service, (5000, 9000))

        for port in range(range_start, range_end):
            if self.is_port_open(port) and not self.is_port_in_use(port):
                self.allocated_ports[service] = port
                print(f"✅ Allocated port {port} for {service}")
                return port

        # Fallback to any available port
        for port in range(8000, 10000):
            if self.is_port_open(port) and not self.is_port_in_use(port):
                self.allocated_ports[service] = port
                print(f"✅ Allocated fallback port {port} for {service}")
                return port

        raise Exception(f"No open ports found for {service}")

    def is_port_open(self, port: int) -> bool:
        """Check if port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False

    def is_port_in_use(self, port: int) -> bool:
        """Check if port is already in use by another process"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return True
            return False
        except:
            return False

class ConfigurationUpdater:
    """Updates configuration files with dynamic ports"""

    def __init__(self, ports: Dict[str, int]):
        self.ports = ports
        self.project_root = Path(__file__).parent

    def update_frontend_config(self):
        """Update frontend Vite config"""
        vite_config = self.project_root / "journal-platform-frontend" / "vite.config.ts"

        if not vite_config.exists():
            print(f"❌ Vite config not found: {vite_config}")
            return

        content = vite_config.read_text()

        # Update frontend port
        frontend_port = self.ports['frontend']
        content = content.replace(r"port: 5173,", f"port: {frontend_port},")

        # Update backend proxy target
        backend_port = self.ports['backend']
        content = content.replace(r"target: 'https://localhost:6770'", f"target: 'https://localhost:{backend_port}'")
        content = content.replace(r"target: 'wss://localhost:6770'", f"target: 'wss://localhost:{backend_port}'")

        vite_config.write_text(content)
        print(f"✅ Updated frontend config: port={frontend_port}, backend proxy={backend_port}")

    def update_backend_config(self):
        """Update backend configuration"""
        backend_config = self.project_root / "app" / "core" / "config.py"

        if not backend_config.exists():
            print(f"❌ Backend config not found: {backend_config}")
            return

        content = backend_config.read_text()

        # Update backend port
        backend_port = self.ports['backend']
        content = content.replace(r"PORT = 6770", f"PORT = {backend_port}")

        backend_config.write_text(content)
        print(f"✅ Updated backend config: port={backend_port}")

    def create_env_file(self):
        """Create .env file with dynamic ports"""
        env_file = self.project_root / ".env.dynamic"

        env_content = f"""# Dynamic Port Configuration - Generated at {datetime.now()}
# Journal Craft Crew Port-Agnostic Setup

# Frontend Configuration
VITE_FRONTEND_PORT={self.ports['frontend']}
VITE_API_URL=https://localhost:{self.ports['backend']}

# Backend Configuration
BACKEND_PORT={self.ports['backend']}
BACKEND_HOST=0.0.0.0

# Database Configuration
DATABASE_PORT={self.ports.get('database', 27017)}

# Redis Configuration
REDIS_PORT={self.ports.get('redis', 6379)}

# WebSocket Configuration
WEBSOCKET_PORT={self.ports.get('websocket', 7000)}

# SSL Configuration
SSL_KEY_PATH=../ssl/journal_crew.key
SSL_CERT_PATH=../ssl/journal_crew.crt

# Development Mode
DEV_MODE=true
DEBUG=true
"""

        env_file.write_text(env_content)
        print(f"✅ Created dynamic .env file: {env_file}")
        return env_file

class ServiceManager:
    """Manages starting and stopping services"""

    def __init__(self, ports: Dict[str, int]):
        self.ports = ports
        self.processes = {}
        self.project_root = Path(__file__).parent

    def kill_existing_processes(self):
        """Kill existing processes on allocated ports"""
        print("🔄 Checking for existing processes...")

        for service, port in self.ports.items():
            try:
                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    try:
                        connections = proc.connections()
                        for conn in connections:
                            if conn.laddr.port == port:
                                print(f"🔪 Killing existing {service} process (PID: {proc.pid})")
                                proc.kill()
                                proc.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                print(f"⚠️  Error checking {service} processes: {e}")

    def start_backend(self):
        """Start backend service"""
        backend_port = self.ports['backend']
        backend_dir = self.project_root / "journal-platform-backend"

        if not backend_dir.exists():
            backend_dir = self.project_root  # Assume we're in backend dir

        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", str(backend_port),
            "--reload",
            "--ssl-keyfile", "../ssl/journal_crew.key",
            "--ssl-certfile", "../ssl/journal_crew.crt"
        ]

        env = os.environ.copy()
        env_file = self.project_root / ".env.dynamic"
        if env_file.exists():
            env_file_content = env_file.read_text()
            for line in env_file_content.split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env[key] = value

        print(f"🚀 Starting backend on port {backend_port}...")
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.processes['backend'] = process
        return process

    def start_frontend(self):
        """Start frontend service"""
        frontend_port = self.ports['frontend']
        frontend_dir = self.project_root / "journal-platform-frontend"

        cmd = ["npm", "run", "dev"]

        env = os.environ.copy()
        env_file = self.project_root / ".env.dynamic"
        if env_file.exists():
            env_file_content = env_file.read_text()
            for line in env_file_content.split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env[key] = value

        print(f"🚀 Starting frontend on port {frontend_port}...")
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.processes['frontend'] = process
        return process

    def wait_for_services(self):
        """Wait for services to be ready"""
        print("⏳ Waiting for services to start...")

        # Wait for backend
        backend_url = f"https://localhost:{self.ports['backend']}/health"
        for i in range(30):  # 30 seconds timeout
            try:
                response = requests.get(backend_url, verify=False, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Backend is ready at {backend_url}")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print(f"❌ Backend failed to start at {backend_url}")
            return False

        # Wait for frontend
        frontend_url = f"http://localhost:{self.ports['frontend']}"
        for i in range(30):  # 30 seconds timeout
            try:
                response = requests.get(frontend_url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Frontend is ready at {frontend_url}")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print(f"❌ Frontend failed to start at {frontend_url}")
            return False

        return True

class PortAgnosticSetup:
    """Main setup orchestrator"""

    def __init__(self):
        self.port_manager = PortManager()
        self.services = {}

    def setup(self):
        """Run the complete setup"""
        print("🚀 Starting Port-Agnostic Setup for Journal Craft Crew")
        print("=" * 60)

        try:
            # Step 1: Find open ports
            print("\n📡 Discovering open ports...")
            frontend_port = self.port_manager.find_open_port('frontend', 5173)
            backend_port = self.port_manager.find_open_port('backend', 6770)

            ports = {
                'frontend': frontend_port,
                'backend': backend_port,
                'database': self.port_manager.find_open_port('database', 27017),
                'redis': self.port_manager.find_open_port('redis', 6379),
                'websocket': self.port_manager.find_open_port('websocket', 7000)
            }

            print(f"📍 Allocated ports: {ports}")

            # Step 2: Update configurations
            print("\n⚙️  Updating configuration files...")
            config_updater = ConfigurationUpdater(ports)
            config_updater.update_frontend_config()
            config_updater.update_backend_config()
            env_file = config_updater.create_env_file()

            # Step 3: Start services
            print("\n🔄 Managing services...")
            service_manager = ServiceManager(ports)
            service_manager.kill_existing_processes()

            backend_process = service_manager.start_backend()
            frontend_process = service_manager.start_frontend()

            # Step 4: Wait for services to be ready
            if service_manager.wait_for_services():
                print("\n🎉 Setup completed successfully!")
                print("=" * 60)
                print(f"🌐 Frontend: http://localhost:{ports['frontend']}")
                print(f"🔧 Backend:  https://localhost:{ports['backend']}")
                print(f"📄 Health:   https://localhost:{ports['backend']}/health")
                print(f"⚙️  Config:   {env_file}")
                print("=" * 60)
                print("\n✨ The application is ready to use!")
                print("🛑 Press Ctrl+C to stop all services")

                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\n🛑 Shutting down services...")
                    service_manager.kill_existing_processes()
                    print("✅ All services stopped")

            else:
                print("❌ Setup failed - services did not start properly")
                service_manager.kill_existing_processes()
                return False

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main entry point"""
    setup = PortAgnosticSetup()
    success = setup.setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()