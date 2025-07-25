# Video Clipper - Development Makefile
# Commands for managing both frontend and backend services

.PHONY: all install frontend backend dev clean help setup build

# Default target
all: setup

# Help command to show available targets
help:
	@echo "Available commands:"
	@echo "  make setup     - Install all dependencies (frontend + backend)"
	@echo "  make install   - Alias for setup"
	@echo "  make dev       - Run both frontend and backend in development"
	@echo "  make frontend  - Run frontend development server"
	@echo "  make backend   - Run backend development server"
	@echo "  make build     - Build frontend for production"
	@echo "  make clean     - Clean all dependencies and build files"
	@echo "  make help      - Show this help message"

# Setup everything (install dependencies)
setup: install

install:
	@echo "🚀 Installing dependencies..."
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed!"

# Development - run both services
dev:
	@echo "🔥 Starting development servers..."
	@echo "Backend will run on: http://localhost:8000 and http://192.168.1.106:8000"
	@echo "Frontend will run on: http://localhost:3000 and http://192.168.1.106:3000"
	@echo "Press Ctrl+C to stop both servers"
	@start cmd /c "cd backend && python main.py"
	@cd frontend && npx.cmd next dev -H 0.0.0.0 -p 3000

# Frontend development server
frontend:
	@echo "🎨 Starting frontend development server..."
	@echo "Frontend will run on:"
	@echo "  Local:   http://localhost:3000"
	@echo "  LAN:     http://192.168.1.106:3000"
	cd frontend && npx.cmd next dev -H 0.0.0.0 -p 3000

# Backend development server  
backend:
	@echo "⚡ Starting backend development server with live reload..."
	@echo "Backend will run on: http://localhost:8000"
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Build frontend for production
build:
	@echo "🏗️  Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Frontend build complete!"

# Clean all dependencies and build files
clean:
	@echo "🧹 Cleaning up..."
	@if exist "backend\__pycache__" rmdir /s /q "backend\__pycache__"
	@if exist "frontend\node_modules" rmdir /s /q "frontend\node_modules"
	@if exist "frontend\.next" rmdir /s /q "frontend\.next"
	@if exist "uploads" rmdir /s /q "uploads"
	@if exist "outputs" rmdir /s /q "outputs"
	@echo "✅ Cleanup complete!"