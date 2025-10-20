#!/bin/bash
# Don't exit on error initially - we'll handle errors manually
set +e

# Install build essentials and poppler
sudo apt-get update
sudo apt-get install -y build-essential libpoppler-cpp-dev libqpdf-dev pkg-config ocrmypdf make

# Symlink gcc-12 and g++-12 to the default versions if not present
if ! command -v gcc-12 &> /dev/null; then
    sudo ln -sf $(which gcc) /usr/bin/gcc-12
fi
if ! command -v g++-12 &> /dev/null; then
    sudo ln -sf $(which g++) /usr/bin/g++-12
fi

# Install Homebrew non-interactively if not present
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for current session
    echo >> /home/vscode/.bashrc
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/vscode/.bashrc
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

    sudo apt-get install build-essential
    brew install gcc@11 pkg-config poppler ocrmypdf
fi

# Optional: Run Makefile setup if present
if [ -f Makefile ]; then
    echo "Running Makefile setup..."
    if ! make setup; then
        echo "Makefile setup failed, continuing with manual setup..."
    fi
fi

# Run Brewfile if Homebrew and Brewfile are present
if command -v brew &> /dev/null && [ -f Brewfile ]; then
    brew bundle --verbose --no-upgrade
fi

# Install Python dependencies using uv
# Note: Python 3.14 has compatibility issues with some packages (pydantic-core, pikepdf)
# Try uv sync first, but fall back to Python 3.12 if needed
echo "Attempting to install Python dependencies with uv..."
if uv sync --all-extras; then
    echo "✅ uv sync successful"
    UV_SUCCESS=true
else
    echo "❌ uv sync failed, likely due to Python 3.14 compatibility issues"
    echo "Setting up Python 3.12 environment as fallback..."
    UV_SUCCESS=false
    
    # Configure Python 3.12 environment
    if command -v python3.12 &> /dev/null; then
        echo "Found Python 3.12, creating fallback environment..."
        python3.12 -m venv .venv-fallback
        source .venv-fallback/bin/activate
        pip install monopoly-core
        echo "✅ Using Python 3.12 fallback environment at .venv-fallback"
        FALLBACK_SUCCESS=true
    else
        echo "⚠️  Warning: Python 3.12 not available, manual setup may be required"
        FALLBACK_SUCCESS=false
    fi
fi

# Set up library path for pdftotext
echo 'export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH' >> /home/vscode/.bashrc

# Verify setup
export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
echo "Verifying monopoly installation..."
if [ "$UV_SUCCESS" = true ] && uv run monopoly --version > /dev/null 2>&1; then
    echo "✅ monopoly working with uv environment"
    echo "To run monopoly: export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:\$LD_LIBRARY_PATH && uv run monopoly"
elif [ "$FALLBACK_SUCCESS" = true ] && [ -f .venv-fallback/bin/monopoly ]; then
    .venv-fallback/bin/monopoly --version > /dev/null 2>&1
    echo "✅ monopoly working with Python 3.12 fallback environment"
    echo "To run monopoly: export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu:\$LD_LIBRARY_PATH && .venv-fallback/bin/monopoly"
else
    echo "⚠️  Warning: monopoly setup verification failed, but setup completed"
    echo "Manual verification may be required"
fi

echo "✅ Devcontainer setup complete."