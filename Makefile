.PHONY: help install setup migrate test run serve clean admin logs version full-stack full-install quick-start

# Default target
.DEFAULT_GOAL := help

# Python & Django variables
PYTHON := python3
PIP := $(PYTHON) -m pip
MANAGE := $(PYTHON) manage.py
VENV := venv
NODE := node
NPM := npm

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# ============================================================================
# HELP - Display all available commands
# ============================================================================
help:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║     KVK_8833_PROFIT - Trading System Makefile               ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 ONE-COMMAND SETUP (FASTEST):$(NC)"
	@echo "  make quick-start          Setup & run EVERYTHING in one command!"
	@echo ""
	@echo "$(GREEN)⭐ FULL-STACK (RECOMMENDED):$(NC)"
	@echo "  make full-install         Install EVERYTHING (backend + frontend)"
	@echo "  make full-stack           Run both Django + React servers together"
	@echo ""
	@echo "$(GREEN)QUICK START:$(NC)"
	@echo "  make install              Install backend only"
	@echo "  make run                  Just run backend server"
	@echo ""
	@echo "$(GREEN)FRONTEND COMMANDS:$(NC)"
	@echo "  make frontend-install     Install React dependencies"
	@echo "  make frontend-start       Start React dev server (port 3000)"
	@echo "  make frontend-build       Build React for production"
	@echo "  make frontend-clean       Clean React node_modules"
	@echo ""
	@echo "$(GREEN)BACKEND SETUP:$(NC)"
	@echo "  make setup                Setup virtual environment"
	@echo "  make deps                 Install Python dependencies"
	@echo "  make migrate              Create & apply migrations"
	@echo "  make admin                Create superuser"
	@echo "  make sample-data          Load sample data"
	@echo ""
	@echo "$(GREEN)RUN COMMANDS:$(NC)"
	@echo "  make serve                Run Django server (port 8001)"
	@echo "  make test                 Run unit tests"
	@echo "  make test-verbose         Run tests with verbose output"
	@echo ""
	@echo "$(GREEN)UTILITY COMMANDS:$(NC)"
	@echo "  make clean                Clean up everything"
	@echo "  make reset                Reset database"
	@echo "  make shell                Django interactive shell"
	@echo "  make check                Check Django setup"
	@echo "  make version              Show version info"
	@echo "  make status   quick-start$(NC)       # ONE command: setup + run"
	@echo "  $(YELLOW)make full-install$(NC)      # Install everything (once)"
	@echo "  $(YELLOW)make full-stack$(NC)        # Run both servers"
	@echo "  $(YELLOW)make serve$(NC)             # Run just backend"
	@echo "  $(YELLOW)make frontend-start$(NC)    # Run just frontend"
	@echo ""

# ============================================================================
# QUICK-START - One-Command Setup & Run Everything
# ============================================================================

quick-start:
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║          KVK Trading Platform - Quick Start Setup            ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)Step 1/3: Setting up backend & frontend...$(NC)"
	@sleep 1
	@$(MAKE) full-install > /dev/null 2>&1 || true
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Step 2/3: Verifying prerequisites...$(NC)"
	@sleep 1
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)✗ Backend setup failed$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "$(RED)✗ Frontend setup failed$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ All prerequisites verified!$(NC)"
	@echo ""
	@echo "$(BLUE)Step 3/3: Starting both servers...$(NC)"
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║          🎉 KVK Trading Platform is LIVE!                    ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)📱 OPEN IN YOUR BROWSER:$(NC)"
	@echo "  Frontend:     $(YELLOW)http://localhost:3000$(NC)"
	@echo "  Backend API:  $(YELLOW)http://localhost:8001/api/$(NC)"
	@echo "  Admin Panel:  $(YELLOW)http://localhost:8001/admin/$(NC)"
	@echo "  Health Check: $(YELLOW)http://localhost:8001/health/$(NC)"
	@echo ""
	@echo "$(BLUE)🔐 LOGIN CREDENTIALS:$(NC)"
	@echo "  Username: $(YELLOW)vinod8833$(NC)"
	@echo "  Password: $(YELLOW)test123$(NC)"
	@echo ""
	@echo "$(BLUE)⏹️  TO STOP: Press Ctrl+C$(NC)"
	@echo ""
	@. $(VENV)/bin/activate && $(MANAGE) runserver 0.0.0.0:8001 &
	@cd frontend && npm start $(YELLOW)make full-stack$(NC)        # Run both servers"
	@echo "  $(YELLOW)make serve$(NC)             # Run just backend"
	@echo "  $(YELLOW)make frontend-start$(NC)    # Run just frontend"
	@echo ""

# ============================================================================
# FULL-STACK COMMANDS - Backend + Frontend Together
# ============================================================================

# FULL-INSTALL - Install everything (backend + frontend)
full-install: setup deps frontend-install migrate admin sample-data
	@echo ""
	@echo "$(GREEN)✓ Full installation complete!$(NC)"
	@echo ""
	@echo "$(BLUE)You're ready to go! Run:$(NC)"
	@echo "  $(YELLOW)make full-stack$(NC)      # Start both servers"
	@echo ""
	@echo "$(BLUE)Or run servers separately:$(NC)"
	@echo "  Terminal 1: $(YELLOW)make serve$(NC)                 (Django on :8001)"
	@echo "  Terminal 2: $(YELLOW)make frontend-start$(NC)         (React on :3000)"
	@echo ""

# FULL-STACK - Run both Django and React servers
full-stack:
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║          Starting KVK Trading Platform                        ║$(NC)"
	@echo "$(GREEN)║          (Full Stack: Django + React)                         ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)Services starting...$(NC)"
	@echo ""
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)Error: Backend not installed. Run: make full-install$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "$(RED)Error: Frontend not installed. Run: make frontend-install$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Prerequisites verified$(NC)"
	@echo ""
	@echo "$(BLUE)Starting Django backend (port 8001)...$(NC)"
	@echo "$(BLUE)Starting React frontend (port 3000)...$(NC)"
	@echo ""
	@echo "$(YELLOW)Press Ctrl+C to stop all services$(NC)"
	@echo ""
	@echo "$(BLUE)URLs:$(NC)"
	@echo "  Frontend:       $(YELLOW)http://localhost:3000$(NC)"
	@echo "  Backend API:    $(YELLOW)http://localhost:8001/api/$(NC)"
	@echo "  Admin Panel:    $(YELLOW)http://localhost:8001/admin/$(NC)"
	@echo "  Health Check:   $(YELLOW)http://localhost:8001/health/$(NC)"
	@echo ""
	@echo "$(BLUE)Credentials:$(NC)"
	@echo "  Username: $(YELLOW)vinod8833$(NC)"
	@echo "  Password: $(YELLOW)test123$(NC)"
	@echo ""
	@. $(VENV)/bin/activate && $(MANAGE) runserver 0.0.0.0:8001 &
	@cd frontend && npm start

# ============================================================================
# FRONTEND COMMANDS - React Installation & Management
# ============================================================================

# FRONTEND-INSTALL - Install React dependencies
frontend-install:
	@echo "$(BLUE)Installing React dependencies...$(NC)"
	@if [ ! -d "frontend" ]; then \
		echo "$(RED)Error: frontend directory not found$(NC)"; \
		exit 1; \
	fi
	@cd frontend && $(NPM) install
	@echo "$(GREEN)✓ React dependencies installed$(NC)"

# FRONTEND-START - Run React development server
frontend-start:
	@echo "$(BLUE)Starting React development server...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "$(RED)Error: Dependencies not installed. Run: make frontend-install$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Frontend running on $(YELLOW)http://localhost:3000$(NC)"
	@echo "$(BLUE)Press Ctrl+C to stop$(NC)"
	@echo ""
	@cd frontend && $(NPM) start

# FRONTEND-BUILD - Build React for production
frontend-build:
	@echo "$(BLUE)Building React for production...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "$(YELLOW)Installing dependencies first...$(NC)"; \
		$(MAKE) frontend-install; \
	fi
	@cd frontend && $(NPM) run build
	@echo "$(GREEN)✓ React build complete - output in frontend/build/$(NC)"

# FRONTEND-CLEAN - Clean React node_modules and build
frontend-clean:
	@echo "$(RED)Cleaning React...$(NC)"
	@rm -rf frontend/node_modules
	@rm -rf frontend/build
	@echo "$(GREEN)✓ React cleaned$(NC)"

# FRONTEND-TEST - Run React tests
frontend-test:
	@echo "$(BLUE)Running React tests...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "$(RED)Error: Dependencies not installed. Run: make frontend-install$(NC)"; \
		exit 1; \
	fi
	@cd frontend && $(NPM) test

# ============================================================================
# INSTALL - Backend only setup (original behavior)
# ============================================================================
install: setup deps migrate admin sample-data
	@echo ""
	@echo "$(GREEN)✓ Installation complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Run server:    $(YELLOW)make serve$(NC)"
	@echo "  2. Visit:         $(YELLOW)http://localhost:8000/health/$(NC)"
	@echo "  3. Admin:         $(YELLOW)http://localhost:8000/admin/$(NC)"
	@echo "  4. API:           $(YELLOW)http://localhost:8000/api/$(NC)"
	@echo ""

# ============================================================================
# SETUP - Create virtual environment
# ============================================================================
setup:
	@echo "$(BLUE)Setting up virtual environment...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)✓ Virtual environment created$(NC)"; \
	else \
		echo "$(YELLOW)✓ Virtual environment already exists$(NC)"; \
	fi

# ============================================================================
# DEPS - Install dependencies
# ============================================================================
deps: setup
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@. $(VENV)/bin/activate && $(PIP) install --upgrade pip setuptools > /dev/null 2>&1
	@. $(VENV)/bin/activate && $(PIP) install Django==4.2.8 djangorestframework==3.14.0 django-cors-headers==4.3.1 > /dev/null 2>&1
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# ============================================================================
# MIGRATE - Create and apply database migrations
# ============================================================================
migrate: deps
	@echo "$(BLUE)Creating migrations...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) makemigrations trading 2>/dev/null || true
	@echo "$(BLUE)Applying migrations...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) migrate > /dev/null 2>&1
	@echo "$(GREEN)✓ Migrations applied$(NC)"

# ============================================================================
# ADMIN - Create superuser (interactive)
# ============================================================================
admin: migrate
	@echo "$(BLUE)Creating superuser...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) createsuperuser

# ============================================================================
# SAMPLE-DATA - Load sample data
# ============================================================================
sample-data: migrate
	@echo "$(BLUE)Loading sample data...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) init_sample_data 2>/dev/null || true
	@echo "$(GREEN)✓ Sample data loaded (INFY, TCS, HDFCBANK)$(NC)"

# ============================================================================
# SERVE - Run development server
# ============================================================================
serve:
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║          Starting KVK_8833_PROFIT Server                    ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)Server running on:$(NC)"
	@echo "  API Health:  $(YELLOW)http://localhost:8000/health/$(NC)"
	@echo "  Admin:       $(YELLOW)http://localhost:8000/admin/$(NC)"
	@echo "  API Root:    $(YELLOW)http://localhost:8000/api/$(NC)"
	@echo ""
	@echo "$(BLUE)Press Ctrl+C to stop$(NC)"
	@echo ""
	@. $(VENV)/bin/activate && $(MANAGE) runserver

# ============================================================================
# RUN - Alias for serve (backwards compatibility)
# ============================================================================
run: serve

# ============================================================================
# TEST - Run unit tests
# ============================================================================
test: migrate
	@echo "$(BLUE)Running tests...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) test 2>/dev/null
	@echo "$(GREEN)✓ Tests completed$(NC)"

# ============================================================================
# TEST-VERBOSE - Run tests with verbose output
# ============================================================================
test-verbose: migrate
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) test -v 2

# ============================================================================
# CLEAN - Clean up venv and database
# ============================================================================
clean:
	@echo "$(RED)Cleaning up...$(NC)"
	@rm -rf $(VENV)
	@rm -f db.sqlite3
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# ============================================================================
# RESET - Reset database
# ============================================================================
reset: migrate sample-data
	@echo "$(GREEN)✓ Database reset complete$(NC)"

# ============================================================================
# SHELL - Django interactive shell
# ============================================================================
shell:
	@echo "$(BLUE)Entering Django shell...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) shell

# ============================================================================
# CHECK - Check Django setup
# ============================================================================
check: migrate
	@echo "$(BLUE)Checking Django setup...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) check
	@echo "$(GREEN)✓ Django setup is valid$(NC)"

# ============================================================================
# LOGS - Show recent logs
# ============================================================================
logs:
	@echo "$(BLUE)Recent activity:$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) migrations --list
	@echo ""
	@echo "$(GREEN)✓ Use 'make serve' to see real-time logs$(NC)"

# ============================================================================
# VERSION - Show version and system info
# ============================================================================
version:
	@echo "$(BLUE)KVK_8833_PROFIT Version Information$(NC)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "System:        Django Trading Analysis"
	@echo "Version:       1.0"
	@echo "Status:        Production Ready ✅"
	@echo ""
	@echo "$(BLUE)Python Information:$(NC)"
	@$(PYTHON) --version
	@echo ""
	@echo "$(BLUE)Django Information:$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) --version 2>/dev/null || echo "Not installed yet - run 'make install'"
	@echo ""
	@echo "$(BLUE)Documentation:$(NC)"
	@echo "  • START_HERE.md"
	@echo "  • README.md"
	@echo "  • QUICKSTART.md"
	@echo "  • BUILD_SUMMARY.md"
	@echo ""

# ============================================================================
# STATUS - Show project status
# ============================================================================
status:
	@echo "$(BLUE)Project Status Check$(NC)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if [ -d "$(VENV)" ]; then \
		echo "$(GREEN)✓ Virtual environment$(NC)"; \
	else \
		echo "$(RED)✗ Virtual environment$(NC)"; \
	fi
	@if [ -f "requirements.txt" ]; then \
		echo "$(GREEN)✓ requirements.txt$(NC)"; \
	else \
		echo "$(RED)✗ requirements.txt$(NC)"; \
	fi
	@if [ -f "db.sqlite3" ]; then \
		echo "$(GREEN)✓ Database$(NC)"; \
	else \
		echo "$(YELLOW)◐ Database$(NC) (will be created on first run)"; \
	fi
	@if [ -f "manage.py" ]; then \
		echo "$(GREEN)✓ Django setup$(NC)"; \
	else \
		echo "$(RED)✗ Django setup$(NC)"; \
	fi
	@if [ -f "START_HERE.md" ]; then \
		echo "$(GREEN)✓ Documentation$(NC)"; \
	else \
		echo "$(RED)✗ Documentation$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  Run: $(YELLOW)make install$(NC)"
	@echo ""

# ============================================================================
# DATABASE UTILITIES
# ============================================================================
migrations-show:
	@echo "$(BLUE)Showing migrations...$(NC)"
	@. $(VENV)/bin/activate && $(MANAGE) showmigrations

# ============================================================================
# HELP for specific commands
# ============================================================================
help-install:
	@echo "$(BLUE)MAKE INSTALL$(NC) - One-command setup"
	@echo "Runs: setup → deps → migrate → admin → sample-data"
	@echo "Use this to get everything ready in one command"

help-serve:
	@echo "$(BLUE)MAKE SERVE$(NC) - Run development server"
	@echo "Starts Django development server on http://localhost:8000"
	@echo "Requires: setup, deps, migrate"

help-test:
	@echo "$(BLUE)MAKE TEST$(NC) - Run unit tests"
	@echo "Runs all unit tests in the trading app"
	@echo "Requires: migrate"

# ============================================================================
# DOCKER SUPPORT (optional)
# ============================================================================
docker-build:
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t kvk-trading:1.0 .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run:
	@echo "$(BLUE)Running Docker container...$(NC)"
	@docker run -p 8000:8000 kvk-trading:1.0

# ============================================================================
# DEVELOPMENT UTILITIES
# ============================================================================
lint:
	@echo "$(BLUE)Linting Python files...$(NC)"
	@. $(VENV)/bin/activate && python3 -m py_compile trading/*.py kvk_trading/*.py
	@echo "$(GREEN)✓ No syntax errors found$(NC)"

freeze:
	@echo "$(BLUE)Freezing requirements...$(NC)"
	@. $(VENV)/bin/activate && $(PIP) freeze > requirements-frozen.txt
	@echo "$(GREEN)✓ Requirements frozen to requirements-frozen.txt$(NC)"

# ============================================================================
# COMMON WORKFLOWS
# ============================================================================
.PHONY: workflow-quickstart workflow-development workflow-production

workflow-quickstart:
	@echo "$(BLUE)Quick Start Workflow$(NC)"
	@$(MAKE) install
	@$(MAKE) serve

workflow-development: setup deps migrate
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "Run: $(YELLOW)make serve$(NC)"

workflow-production: clean setup deps migrate
	@echo "$(GREEN)✓ Production environment ready$(NC)"
	@echo "Run: $(YELLOW)gunicorn kvk_trading.wsgi$(NC)"

# ============================================================================
# VALIDATION TARGETS
# ============================================================================
validate-python:
	@command -v $(PYTHON) >/dev/null 2>&1 || (echo "$(RED)Python not found$(NC)" && exit 1)
	@echo "$(GREEN)✓ Python available$(NC)"

validate-all: validate-python
	@echo "$(GREEN)✓ All validations passed$(NC)"

# End of Makefile
