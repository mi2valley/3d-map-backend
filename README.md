# Qamposer Backend

A FastAPI-based quantum circuit simulation backend powered by Qiskit.

## Overview

Qamposer Backend provides a REST API for quantum circuit simulation. It receives circuit definitions from the frontend, executes quantum simulations using Qiskit, and returns measurement results and state vectors.

## Technology Stack

- **Python 3.13** - Programming language
- **FastAPI** - Modern web framework for building APIs
- **Qiskit** - IBM's quantum computing framework
- **Qiskit Aer** - High-performance quantum circuit simulator
- **Uvicorn** - ASGI server for serving the application
- **Poetry** - Dependency management and packaging
- **Pydantic** - Data validation using Python type annotations

## Prerequisites

### macOS

```bash
# Install Python 3.13 using Homebrew
brew install python@3.13

# Verify installation
python3 --version  # Should be Python 3.13.x

# Install Poetry (Python package manager)
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="$HOME/.local/bin:$PATH"

# Verify Poetry installation
poetry --version
```

### Windows

1. **Install Python 3.13:**
   - Download Python 3.13 installer from [python.org](https://www.python.org/downloads/)
   - Run the installer
   - **IMPORTANT:** Check "Add Python to PATH" during installation
   - Verify installation in Command Prompt or PowerShell:
   ```powershell
   python --version  # Should be Python 3.13.x
   ```

2. **Install Poetry:**

   **Option 1: Using PowerShell (Recommended)**
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

   **Option 2: Using pip**
   ```powershell
   pip install poetry
   ```

   Verify installation:
   ```powershell
   poetry --version
   ```

## Installation

### Step 1: Navigate to Backend Directory

```bash
cd qamposer-backend
```

### Step 2: Create Environment File

**macOS/Linux:**
```bash
cp .env.example .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

### Step 3: Install Dependencies

```bash
# Install all dependencies using Poetry
poetry install

# This will:
# - Create a virtual environment
# - Install all required packages (FastAPI, Qiskit, etc.)
# - Install development tools (pytest, ruff, mypy, etc.)
# - Set up pre-commit hooks
```

Alternatively, you can use the Makefile:

```bash
make install
```

## Running the Application

### Development Mode

**Using Poetry:**
```bash
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

**Using Makefile:**
```bash
make run
```

The API will be available at:
- **API:** `http://localhost:8080`
- **Interactive API Documentation (Swagger):** `http://localhost:8080/docs`
- **Alternative API Documentation (ReDoc):** `http://localhost:8080/redoc`

### Production Mode

For production deployment, use Gunicorn with Uvicorn workers:

```bash
poetry run gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8080
```

## Development

### Project Structure

```
qamposer-backend/
├── src/
│   └── backend/
│       ├── main.py           # FastAPI application entry point
│       ├── api/              # API endpoints
│       ├── models/           # Pydantic models
│       ├── services/         # Business logic
│       └── core/             # Core utilities
├── tests/                    # Test files
├── .env.example             # Environment variables template
├── .env                     # Environment variables (create from .env.example)
├── Makefile                 # Common commands
├── pyproject.toml           # Poetry configuration and dependencies
├── poetry.lock              # Locked dependency versions
└── README.md                # This file
```

### Available Make Commands

```bash
make install        # Install dependencies and pre-commit hooks
make run            # Start development server
make test           # Run tests with pytest
make update         # Update dependencies
make build          # Build distribution packages
make docker-build   # Build Docker image
make docker-run     # Run Docker container
```

### API Endpoints

#### POST /api/simulate
Simulate a quantum circuit and return measurement results.

**Request Body:**
```json
{
  "qubits": 2,
  "gates": [
    {
      "type": "H",
      "qubit": 0,
      "position": 0
    },
    {
      "type": "CNOT",
      "control": 0,
      "target": 1,
      "position": 1
    }
  ],
  "shots": 1024
}
```

**Response:**
```json
{
  "counts": {
    "00": 512,
    "11": 512
  },
  "statevector": [...],
  "circuit_diagram": "..."
}
```

### Code Quality Tools

The project uses several tools to maintain code quality:

```bash
# Run linting with ruff
poetry run ruff check .

# Run type checking with mypy
poetry run mypy src/

# Run type checking with pyright
poetry run pyright

# Run tests with pytest
poetry run pytest
# or
make test
```

### Pre-commit Hooks

Pre-commit hooks are automatically installed with `make install` or `poetry install`. They will:
- Format code with ruff
- Check types with mypy
- Run linting checks

To manually run pre-commit hooks:
```bash
poetry run pre-commit run --all-files
```

## Docker

### Build Docker Image

**macOS/Linux:**
```bash
make docker-build
```

**Windows:**
```powershell
docker build . -t py312
```

### Run Docker Container

**macOS/Linux:**
```bash
make docker-run
```

**Windows:**
```powershell
docker run -it -p 8080:8080 py312
```

The API will be available at `http://localhost:8080`

## Testing

Run the test suite:

```bash
# Using Poetry
poetry run pytest

# Using Makefile
make test

# Run with coverage
poetry run pytest --cov=backend --cov-report=html
```

## Environment Variables

Create a `.env` file from `.env.example`:

```env
# Example .env file
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:5173"]
```

## Troubleshooting

### Poetry Command Not Found

**macOS/Linux:**
```bash
# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.zshrc or ~/.bash_profile for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

**Windows:**
```powershell
# Poetry should be in PATH after installation
# If not, add manually:
# Go to System Properties > Environment Variables
# Add Poetry installation path to PATH
```

### Virtual Environment Issues

```bash
# Remove existing virtual environment
rm -rf .venv  # macOS/Linux
# or
rd /s /q .venv  # Windows

# Reinstall dependencies
poetry install
```

### Qiskit Installation Errors

Qiskit requires a C++ compiler. If you encounter build errors:

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

**Windows:**
```powershell
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Port Already in Use

```bash
# Find and kill process using port 8080
# macOS/Linux
lsof -ti:8080 | xargs kill -9

# Windows (PowerShell as Administrator)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

These provide interactive API documentation where you can test endpoints directly.

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write tests for new features
4. Run `make test` and ensure all tests pass
5. Run pre-commit hooks before committing

## License

See the main project LICENSE file for details.
