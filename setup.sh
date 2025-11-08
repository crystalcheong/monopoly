#!/bin/bash

# Monopoly Development Setup Script
# This script sets up the development environment for the Monopoly project

echo "🏦 Welcome to Monopoly Development Setup"
echo "========================================"

# Check if we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the monopoly project root directory"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

echo "✅ Environment activated!"
echo ""

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y build-essential libpoppler-cpp-dev libpoppler-cpp0v5 poppler-utils pkg-config ocrmypdf tesseract-ocr ghostscript

# Update the library cache
sudo ldconfig

# Verify that the poppler library is correctly installed
ldconfig -p | grep poppler

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -e .

echo "✅ Setup complete!"
echo ""

# Show available commands
echo "🛠️  Available Development Commands:"
echo "===================================="
echo ""
echo "Code Quality:"
echo "  /workspaces/monopoly/.venv/bin/ruff check .     # Run linting"
echo "  /workspaces/monopoly/.venv/bin/ruff format .    # Format code"
echo "  /workspaces/monopoly/.venv/bin/mypy src         # Type checking"
echo ""
echo "Testing:"
echo "  /workspaces/monopoly/.venv/bin/pytest          # Run all tests"
echo "  /workspaces/monopoly/.venv/bin/pytest -v       # Run tests with verbose output"
echo "  /workspaces/monopoly/.venv/bin/pytest tests/unit/  # Run only unit tests"
echo ""
echo "Running Monopoly:"
echo "  /workspaces/monopoly/.venv/bin/monopoly --help                    # Show help"
echo "  /workspaces/monopoly/.venv/bin/monopoly src/monopoly/examples/example_statement.pdf -p  # Test with example"
echo "  /workspaces/monopoly/.venv/bin/monopoly statements/uob -p -o output  # Process UOB statements with output"
echo "  /workspaces/monopoly/.venv/bin/monopoly ./statements              # Process all statements in directory"
echo ""
echo "🎯 Quick Start:"
echo "1. Try the example: /workspaces/monopoly/.venv/bin/monopoly src/monopoly/examples/example_statement.pdf -p"
echo "2. Run tests: /workspaces/monopoly/.venv/bin/pytest"
echo "3. Check code quality: /workspaces/monopoly/.venv/bin/ruff check ."
echo ""
echo "📚 Documentation: Check the README.md for more information"
echo "🐛 Issues: https://github.com/benjamin-awd/monopoly/issues"