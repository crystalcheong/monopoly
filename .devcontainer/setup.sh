#!/bin/bash
set -e

# Install build essentials and poppler
sudo apt-get update
sudo apt-get install -y build-essential libpoppler-cpp-dev pkg-config ocrmypdf make

# Symlink g++-12 to the default g++ if not present
if ! command -v g++-12 &> /dev/null; then
    sudo ln -s $(which g++) /usr/bin/g++-12
fi

# Install Homebrew non-interactively if not present
if ! command -v brew &> /dev/null; then
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for current session
    echo >> /home/vscode/.bashrc
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/vscode/.bashrc
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

    sudo apt-get install build-essential
    brew install gcc
fi

# Optional: Run Makefile setup if present
if [ -f Makefile ]; then
    make setup || true
fi

# Run Brewfile if Homebrew and Brewfile are present
if command -v brew &> /dev/null && [ -f Brewfile ]; then
    brew bundle --verbose --no-upgrade || true
fi

# Install Python dependencies using uv
uv sync --all-extras

# Verify setup
uv run monopoly --version

echo "Devcontainer setup complete."
