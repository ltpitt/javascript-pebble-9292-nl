.PHONY: help install clean build lint test test-api generate-icons backend-install backend-dev backend-clean venv-check

# Variables
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
NODE := node
PEBBLE := pebble

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help:
	@echo ""
	@echo "$(GREEN)NextRide for Pebble - Development Commands$(NC)"
	@echo ""
	@echo "$(BLUE)Setup & Installation:$(NC)"
	@echo "  make install           - Create venv and install all dependencies"
	@echo "  make venv              - Create Python virtual environment only"
	@echo "  make backend-install   - Install backend dependencies (delegates to backend/)"
	@echo ""
	@echo "$(BLUE)Building & Validation:$(NC)"
	@echo "  make build             - Build Pebble app (requires pebble CLI)"
	@echo "  make lint              - Validate JavaScript syntax"
	@echo "  make validate          - Run all validations (lint + build check)"
	@echo ""
	@echo "$(BLUE)Testing:$(NC)"
	@echo "  make test              - Run basic JavaScript validation"
	@echo "  make test-api          - Test OV API connectivity (requires internet)"
	@echo ""
	@echo "$(BLUE)Resource Generation:$(NC)"
	@echo "  make generate-icons    - Generate app icons from Python scripts"
	@echo ""
	@echo "$(BLUE)Backend Operations:$(NC)"
	@echo "  make backend-dev       - Start backend in development mode"
	@echo "  make backend-start     - Start backend in production mode"
	@echo "  make backend-stop      - Stop backend server"
	@echo "  make backend-test      - Test backend API endpoints"
	@echo "  make backend-clean     - Clean backend artifacts"
	@echo ""
	@echo "$(BLUE)Cleanup:$(NC)"
	@echo "  make clean             - Remove build artifacts and venv"
	@echo "  make clean-build       - Remove only build artifacts"
	@echo ""
	@echo "$(YELLOW)Note: First-time setup requires 'make install' to create venv$(NC)"
	@echo ""

# Create Python virtual environment
venv:
	@echo "$(BLUE)📦 Creating Python virtual environment...$(NC)"
	python3 -m venv $(VENV)
	@echo "$(GREEN)✅ Virtual environment created: $(VENV)/$(NC)"

# Install all dependencies (Python + Node if needed)
install: venv
	@echo "$(BLUE)📥 Installing Python dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install pillow flask flask-cors flask-limiter requests
	@echo "$(GREEN)✅ Python dependencies installed!$(NC)"
	@echo ""
	@echo "$(YELLOW)⚠️  Pebble SDK must be installed separately$(NC)"
	@echo "    Visit: https://developer.rebble.io/developer.pebble.com/sdk/install/index.html"
	@echo ""
	@echo "$(GREEN)✅ Setup complete!$(NC)"

# Check if venv exists before running Python commands
venv-check:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)❌ Virtual environment not found. Run 'make install' first.$(NC)"; \
		exit 1; \
	fi

# Build Pebble app
build:
	@echo "$(BLUE)🔨 Building Pebble app...$(NC)"
	@if command -v $(PEBBLE) >/dev/null 2>&1; then \
		$(PEBBLE) build; \
		echo "$(GREEN)✅ Build complete!$(NC)"; \
	else \
		echo "$(YELLOW)❌ Pebble SDK not found. Please install from:$(NC)"; \
		echo "    https://developer.rebble.io/developer.pebble.com/sdk/install/index.html"; \
		exit 1; \
	fi

# Lint JavaScript files
lint:
	@echo "$(BLUE)🔍 Validating JavaScript syntax...$(NC)"
	@if [ -f "src/js/app.js" ]; then \
		$(NODE) -c src/js/app.js && echo "$(GREEN)✅ app.js: OK$(NC)"; \
	fi
	@if [ -f "src/js/main.js" ]; then \
		$(NODE) -c src/js/main.js && echo "$(GREEN)✅ main.js: OK$(NC)"; \
	fi
	@echo "$(GREEN)✅ JavaScript validation passed!$(NC)"

# Run all validations
validate: lint
	@echo "$(BLUE)🔍 Running build validation...$(NC)"
	@if command -v $(PEBBLE) >/dev/null 2>&1; then \
		$(PEBBLE) build > /dev/null 2>&1 && echo "$(GREEN)✅ Build validation passed!$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Skipping build validation (Pebble SDK not installed)$(NC)"; \
	fi

# Test JavaScript files (alias for lint)
test: lint
	@echo "$(GREEN)✅ All tests passed!$(NC)"

# Test OV API connectivity
test-api:
	@echo "$(BLUE)🧪 Testing OV API connectivity...$(NC)"
	@if [ -x "./test-ovapi.sh" ]; then \
		./test-ovapi.sh; \
	else \
		echo "$(YELLOW)❌ test-ovapi.sh not found or not executable$(NC)"; \
		exit 1; \
	fi

# Generate app icons
generate-icons: venv-check
	@echo "$(BLUE)🎨 Generating app icons...$(NC)"
	@cd resources/images && ../../$(PYTHON) generate_bus_icon.py
	@cd resources/images && ../../$(PYTHON) generate_transit_icons.py
	@echo "$(GREEN)✅ Icons generated!$(NC)"

# Backend operations (delegate to backend/Makefile)
backend-install:
	@echo "$(BLUE)📦 Installing backend dependencies...$(NC)"
	@cd backend && $(MAKE) install

backend-dev:
	@echo "$(BLUE)🚀 Starting backend in development mode...$(NC)"
	@cd backend && $(MAKE) dev

backend-start:
	@echo "$(BLUE)🚀 Starting backend in production mode...$(NC)"
	@cd backend && $(MAKE) start

backend-stop:
	@echo "$(BLUE)🛑 Stopping backend...$(NC)"
	@cd backend && $(MAKE) stop

backend-test:
	@echo "$(BLUE)🧪 Testing backend API...$(NC)"
	@cd backend && $(MAKE) test

backend-clean:
	@echo "$(BLUE)🧹 Cleaning backend artifacts...$(NC)"
	@cd backend && $(MAKE) clean

# Clean build artifacts only
clean-build:
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf out/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "$(GREEN)✅ Build artifacts cleaned!$(NC)"

# Clean everything (build artifacts + venv)
clean: clean-build
	@echo "$(BLUE)🧹 Removing virtual environment...$(NC)"
	rm -rf $(VENV)
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

# Development workflow shortcut
dev: validate
	@echo "$(GREEN)✅ Ready for development!$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  • Edit your code in src/js/app.js"
	@echo "  • Run 'make validate' to check your changes"
	@echo "  • Run 'make build' to build the app"
	@echo "  • Run 'pebble install --emulator basalt' to test in emulator"
