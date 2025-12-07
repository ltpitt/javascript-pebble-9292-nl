.PHONY: help install dev start stop restart logs clean test

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
	@echo "  make dev        - Run in development mode (auto-reload)"
	@echo "  make start      - Start server in production mode"
	@echo "  make stop       - Stop running server"
	@echo "  make restart    - Restart server"
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
	DEBUG=true $(UVICORN) app:app --host $(HOST) --port $(PORT) --reload

start: $(VENV)
	@echo "🚀 Starting production server on http://$(HOST):$(PORT)"
	@echo ""
	@echo "⚠️  First startup will download ~1.2GB GTFS data (2-5 minutes)"
	@echo "    Please be patient..."
	@echo ""
	$(PYTHON) app.py

stop:
	@echo "🛑 Stopping server..."
	@pkill -f "uvicorn app:app" || echo "No server running"

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
