#!/usr/bin/env python3
"""
🌱 Transcendence - One-Click Launcher

This script automatically starts both backend and frontend servers.

Usage:
1. Clone repo
2. Install: pip install -r requirements.txt
3. Run: python main.py

Then access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("🌱" + "="*60 + "🌱")
    print("🚀 TRANSCENDENCE - Green Agents of Change")
    print("🌍 Brazilian Youth Green Career Assistant")
    print("🤖 Multi-Agent AI System")
    print("="*64)
    print()

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False

def check_npm():
    """Check if npm is installed"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm found: {result.stdout.strip()}")
            return True
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        # Try alternative npm locations on Windows
        try:
            result = subprocess.run(['npm.cmd', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        
        print("⚠️  npm not found in PATH, but Node.js is installed. Continuing anyway...")
        return True  # Allow continuation if Node.js is found

def install_frontend_deps():
    """Install frontend dependencies if needed"""
    frontend_dir = Path(__file__).parent / "frontend"
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            # Try npm first, then npm.cmd
            npm_cmd = 'npm'
            try:
                subprocess.run([npm_cmd, '--version'], capture_output=True, check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                npm_cmd = 'npm.cmd'
            
            result = subprocess.run(
                [npm_cmd, 'install'],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Frontend dependencies installed")
            else:
                print(f"❌ Failed to install frontend dependencies: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing frontend dependencies: {e}")
            return False
    else:
        print("✅ Frontend dependencies already installed")
    return True

def create_env_files():
    """Create environment files if they don't exist"""
    backend_env = Path(__file__).parent / "backend" / ".env"
    frontend_env = Path(__file__).parent / "frontend" / ".env"
    
    # Backend .env
    if not backend_env.exists():
        backend_env_content = """# AWS Mistral AI Configuration
AWS_REGION=us-east-1
AWS_MISTRAL_MODEL=mistral.mistral-7b-instruct-v0:2
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_SESSION_TOKEN=optional_session_token_here

# Development Settings
MOCK_MODE=true
DEBUG=true
LOG_LEVEL=INFO
TELEMETRY_ENABLED=true

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]

# Database Configuration
DATABASE_URL=sqlite:///./transcendence.db
DATA_DIR=./data

# Security Settings
SECRET_KEY=transcendence_dev_secret_key_change_in_production
TOKEN_EXPIRE_MINUTES=60

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Caching
CACHE_TTL=3600
CACHE_MAX_SIZE=1000"""
        
        backend_env.write_text(backend_env_content)
        print("✅ Created backend/.env file")
    
    # Frontend .env
    if not frontend_env.exists():
        frontend_env_content = """VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_LANGUAGE=en
VITE_ENABLE_ANALYTICS=true
VITE_MOCK_MODE=true"""
        
        frontend_env.write_text(frontend_env_content)
        print("✅ Created frontend/.env file")

def start_backend():
    """Start the FastAPI backend server"""
    print("🐍 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Use the current Python interpreter
        python_exe = sys.executable
        backend_process = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "app_main:app", "--reload", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for backend to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return backend_process
        else:
            print("❌ Backend server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the React frontend server"""
    print("⚛️  Starting frontend server...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        # Try npm first, then npm.cmd
        npm_cmd = 'npm'
        try:
            subprocess.run([npm_cmd, '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            npm_cmd = 'npm.cmd'
        
        frontend_process = subprocess.Popen(
            [npm_cmd, 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for frontend to start
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Frontend server started on http://localhost:5173")
            return frontend_process
        else:
            print("❌ Frontend server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main launcher function"""
    print_banner()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    if not check_node() or not check_npm():
        print("\n❌ Prerequisites not met. Please install Node.js 18+ and npm")
        sys.exit(1)
    
    # Create environment files
    print("\n📁 Setting up environment files...")
    create_env_files()
    
    # Install frontend dependencies
    print("\n📦 Checking frontend dependencies...")
    if not install_frontend_deps():
        sys.exit(1)
    
    # Start servers
    print("\n🚀 Starting servers...")
    
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    frontend_process = start_frontend()
    if not frontend_process:
        if backend_process:
            backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 SUCCESS! Both servers are running!")
    print("="*50)
    print("🌐 Frontend: http://localhost:5173")
    print("🔧 Backend API: http://localhost:8000/docs")
    print("📊 Health Check: http://localhost:8000/health")
    print("="*50)
    print("\n💡 Tips:")
    print("• Create Brazilian youth personas")
    print("• Chat with the AI assistant")
    print("• Explore green job recommendations")
    print("• View analytics dashboard")
    print("\n⚠️  Press Ctrl+C to stop all servers")
    
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Shutdown complete!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly")
                break
                
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()