.PHONY: help install dev dev-bg start start-bg stop restart logs clean test

# Variables
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
PORT := 8000
HOST := 127.0.0.1

help:
	@echo "NextRide Backend API - Available Commands:"
	@echo ""
	@echo "  make install    - Create venv and install dependencies"
	@echo "  make dev        - Run in development mode (foreground, auto-reload)"
	@echo "  make dev-bg     - Run in development mode (background, auto-reload)"
	@echo "  make start      - Start server in production mode (foreground)"
	@echo "  make start-bg   - Start server in production mode (background)"
	@echo "  make stop       - Stop background server (requires PID file)"
	@echo "  make restart    - Restart server (stop + start)"
	@echo "  make logs       - Show server logs (if running via systemd)"
	@echo "  make test       - Run API tests"
	@echo "  make clean      - Remove venv and cached data"
	@echo ""
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run in Docker container"
	@echo "  make docker-stop    - Stop Docker container"
	@echo "  make docker-logs    - Show Docker logs"

install:
	@echo "📦 Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "📥 Installing dependencies..."
	$(PIP) install -q --upgrade pip
	$(PIP) install -q -r requirements.txt
	@echo "✅ Installation complete!"
	@echo ""
	@echo "⚠️  Note: First run will download ~1.2GB GTFS data (2-5 minutes)"

dev: $(VENV)
	@echo "🚀 Starting development server on http://$(HOST):$(PORT)"
	@echo "📚 API docs: http://$(HOST):$(PORT)/docs"
	@echo ""
	@echo "⚠️  Running in foreground. Press Ctrl+C to stop."
	@echo "    To run in background, use 'make dev-bg'"
	@echo ""
	DEBUG=true $(UVICORN) app:app --host $(HOST) --port $(PORT) --reload

dev-bg: $(VENV)
	@echo "🚀 Starting development server in background on http://$(HOST):$(PORT)"
	@# Check if server is already running
	@if [ -f .uvicorn.pid ]; then \
		echo "❌ Server already running (PID file exists). Run 'make stop' first."; \
		exit 1; \
	fi
	@# Start server in background and save PID
	@DEBUG=true nohup $(UVICORN) app:app --host $(HOST) --port $(PORT) --reload > server.log 2>&1 & echo $$! > .uvicorn.pid
	@echo "✅ Server started with PID: $$(cat .uvicorn.pid)"
	@echo "📋 View logs: tail -f server.log"
	@echo "🛑 Stop server: make stop"

start: $(VENV)
	@echo "🚀 Starting production server on http://$(HOST):$(PORT)"
	@echo ""
	@echo "⚠️  First startup will download ~1.2GB GTFS data (2-5 minutes)"
	@echo "    Please be patient..."
	@echo ""
	@echo "⚠️  Running in foreground. Press Ctrl+C to stop."
	@echo "    To run in background, use 'make start-bg'"
	@echo ""
	$(PYTHON) app.py

start-bg: $(VENV)
	@echo "🚀 Starting production server in background on http://$(HOST):$(PORT)"
	@# Check if server is already running
	@if [ -f .app.pid ]; then \
		echo "❌ Server already running (PID file exists). Run 'make stop' first."; \
		exit 1; \
	fi
	@echo ""
	@echo "⚠️  First startup will download ~1.2GB GTFS data (2-5 minutes)"
	@echo ""
	@# Start server in background and save PID
	@nohup $(PYTHON) app.py > server.log 2>&1 & echo $$! > .app.pid
	@echo "✅ Server started with PID: $$(cat .app.pid)"
	@echo "📋 View logs: tail -f server.log"
	@echo "🛑 Stop server: make stop"

stop:
	@echo "🛑 Stopping server..."
	@if [ -f .uvicorn.pid ]; then \
		PID=$$(cat .uvicorn.pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			kill $$PID && echo "✅ Server stopped (PID: $$PID)"; \
			rm -f .uvicorn.pid; \
		else \
			echo "⚠️  No process found with PID $$PID (stale PID file)"; \
			rm -f .uvicorn.pid; \
		fi; \
	elif [ -f .app.pid ]; then \
		PID=$$(cat .app.pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			kill $$PID && echo "✅ Server stopped (PID: $$PID)"; \
			rm -f .app.pid; \
		else \
			echo "⚠️  No process found with PID $$PID (stale PID file)"; \
			rm -f .app.pid; \
		fi; \
	else \
		echo "⚠️  No PID file found."; \
		echo "    • If server is running in foreground, use Ctrl+C to stop it"; \
		echo "    • If server was started outside of make, find and kill the process manually"; \
		echo "    • PID files are only created when using 'make start-bg' or 'make dev-bg'"; \
	fi

restart: stop start

logs:
	@echo "📋 Showing logs (systemd service)..."
	@journalctl -u nextride-backend -f -n 50 2>/dev/null || \
		echo "Not running as systemd service. Use 'make dev' or 'make start' directly."

test:
	@echo "🧪 Running API tests..."
	@echo ""
	@echo "Testing health endpoint..."
	@curl -s http://localhost:$(PORT)/health | python3 -m json.tool || echo "Server not running"
	@echo ""
	@echo "Testing search endpoint..."
	@curl -s "http://localhost:$(PORT)/api/stops/search?query=Haarlem&limit=5" | python3 -m json.tool || echo "Server not running"

clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf data/*.zip
	rm -f .uvicorn.pid .app.pid server.log
	@echo "✅ Cleanup complete"

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t nextride-backend .
	@echo "✅ Docker image built: nextride-backend"

docker-run:
	@echo "🐳 Starting Docker container..."
	docker run -d \
		--name nextride-backend \
		-p $(PORT):8000 \
		-v $$(pwd)/data:/app/data \
		--restart unless-stopped \
		nextride-backend
	@echo "✅ Container started: nextride-backend"
	@echo "📋 View logs: make docker-logs"

docker-stop:
	@echo "🛑 Stopping Docker container..."
	docker stop nextride-backend || true
	docker rm nextride-backend || true
	@echo "✅ Container stopped"

docker-logs:
	@echo "📋 Docker logs (Ctrl+C to exit)..."
	docker logs -f nextride-backend

# Ensure venv exists for commands that need it
$(VENV):
	@echo "❌ Virtual environment not found. Run 'make install' first."
	@exit 1
